import logging
import random
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

import redis.asyncio as aioredis

from lein_vector import MemoryManagerQdrant, QdrantAdapter, RedisShortTermMemory
from lein_vector.schemas.chunk import Chunk, ChunkPayload
from lein_vector.sentence_transformer import EmbeddingProviderGemini

log = logging.getLogger(__name__)

class Memory:
    def __init__(self, short_term, memory_manager, embedder, redis_conn, merge_n: int,
                 gift_base: float, gift_growth: float, score_threshold: float):
        """
        :param short_term: Кратковременное хранилище сообщений пользователя (RedisShortTermMemory).
        :param memory_manager: Менеджер долговременной памяти (MemoryManagerQdrant).
        :param embedder: Провайдер эмбеддингов (EmbeddingProviderGemini).
        :param merge_n: Количество чанков для слияния при мердже.
        """
        self.short = short_term
        self.long = memory_manager
        self.embed = embedder
        self._msg_no: dict[int, int] = {}
        self.r = redis_conn
        self.merge_n = merge_n

        self._gift_base = gift_base
        self._gift_growth = gift_growth
        self._gift_fail: dict[tuple[int, str], int] = {}

        self.score_threshold = score_threshold

    @classmethod
    async def from_qdrant(
        cls,
        host: str,
        port: int,
        collection: str,
        redis_url: str,
        vector_size: int = 768,
        api_key: str | None = None,
        short_maxlen: int = 40,
        gift_base: float = 0.04,
        gift_growth: float = 1.2,
        score_threshold: float = 0.72,
        merge_n: int = 5,
    ) -> "Memory":
        """
        Создаёт MemoryFacade со всеми зависимостями
        :param host: Адрес Qdrant.
        :param port: Порт Qdrant.
        :param collection: Название коллекции Qdrant.
        :param redis_url: Ссылка на подключение к Redis
        :param vector_size: Размерность векторного пространства.
        :param api_key: Ключ для эмбеддера (если требуется).
        :param short_maxlen: Максимальная длина окна кратковременной памяти.
        :param gift_base: Базовый шанс "намека на подарок"
        :param gift_growth: Экспоненциальный множитель шанса
        :param score_threshold: Базовый фильтр косинусной близости эмбеддинга
        :param merge_n: Кол-во Чанков памяти, необходимых для суммаризации
        :returns: Экземпляр Memory с инициализированными зависимостями.
        """
        _redis = aioredis.from_url(redis_url, decode_responses=True)
        short_mem = RedisShortTermMemory(_redis, maxlen=short_maxlen)
        embedder = EmbeddingProviderGemini(api_key=api_key)
        adapter = QdrantAdapter(host, port, collection, vector_size)
        await adapter.init_collection()
        long_mem = MemoryManagerQdrant(adapter, embedder)
        return cls(
            short_mem,
            long_mem,
            embedder,
            redis_conn=_redis,
            merge_n=merge_n,
            gift_base=gift_base,
            gift_growth=gift_growth,
            score_threshold=score_threshold
        )

    @staticmethod
    def _to_openai(msgs: list[dict]) -> list[dict]:
        """
        :param msgs: Список сообщений внутреннего формата.
        :returns: Список сообщений в формате OpenAI (role, content).
        """
        role_map = {"gf": "assistant"}  # «gf» → OpenAI «assistant»
        return [
            {"role": role_map.get(m["role"], m["role"]), "content": m["text"]}
            for m in msgs
        ]

    async def step_gf(
        self,
        user_id: int,
        gf_msg: str,
        bot: str,
        *,
        block_size: int = 4,
        save_pair: bool = True,
    ):
        """
        Добавляет в чанк памяти ответ ассистента.
        :param user_id: Идентификатор пользователя
        :param gf_msg: Сообщение от gf (assistant)
        :param bot: Идентификатор бота
        :param block_size: Размер блока для сохранения в долговременной памяти
        :param save_pair: Флаг, сохранять ли пару сообщений при достижении block_size
        """
        key = (user_id, bot)
        curr_no = await self.r.incr(f"msg_no:{bot}:{user_id}")
        ts = datetime.now(UTC).timestamp()
        await self.short.add(
            bot=bot,
            user_id=user_id,
            role="gf",
            text=str(gf_msg),
            extra={"msg_no": curr_no, "ts": ts},
        )

        if save_pair and curr_no % block_size == 0:
            last_block = await self.short.window(user_id, bot, block_size)

            block_text = "\n".join(f'{m["role"]}: {m["text"]}' for m in last_block)

            vector = await self.embed.get_embedding(block_text)

            new_chunk = Chunk(
                chunk_id=uuid4(),
                bot=bot,
                user_id=user_id,
                chunk_type="type0",
                created_at=datetime.now(UTC),
                last_hit=datetime.now(UTC),
                hit_count=0,
                text=block_text,
                persistent=False,
                extra={"msg_no": curr_no},
            )
            await self.long.upsert_chunk_with_vector(new_chunk, vector)

        log.info(curr_no % (block_size * self.merge_n))
        if curr_no % (block_size * self.merge_n) == 0:
            try:
                log.debug(f'Summary requested {bot}:{user_id}')
                merged_text, used_ids = await self.long.merge_old_chunks(
                    user_id=user_id, bot=bot, chunk_type="type0", n=self.merge_n
                )
                return merged_text, used_ids
            except:
                log.error("Summary failed\n", exc_info=True)
                return None, None
        else:
            return None, None

    async def get_long_memories(
            self, user_id: int, bot: str, search_terms: list[str], topk: int = 3
    ) -> list:
        """
        Возвращает ТОЛЬКО длительную память по списку тем.
        :param bot: Кодовое имя бота
        :param user_id: Идентификатор пользователя
        :param search_terms: Список поисковых запросов (строк)
        :param topk: Количество возвращаемых чанков на запрос
        :returns: Список релевантных чанков
        """
        # wtf: Добавить фильтр только саммари
        search_terms_embedded = [await self.embed.get_embedding(term) for term in search_terms]

        result = await self.long.retrieve_by_embeddings(
            user_id=user_id,
            bot=bot,
            embeddings=search_terms_embedded,
            score_threshold=0.72,
            topk=topk,
            filter_={"chunk_type": "type1"},
        )

        log.info(f"get_long_memories: user_id={user_id}, bot={bot}, search_terms={search_terms}, result={result}")

        return result

    async def get_short_memories(
        self, user_id: int, bot: str, n_memories: int = 20
    ) -> list:
        """
        Возвращает ТОЛЬКО кратковременную память по списку тем
        :param bot: Кодовое имя бота
        :param user_id: Идентификатор пользователя
        :param n_memories: Количество последних сообщений кратковременной памяти
        :returns: Список сообщений
        """
        data = await self.short.window(user_id, bot, n_memories)
        return self._to_openai(data)

    async def add_short_msg(
        self,
        user_id: int,
        bot: str,
        text: str,
        *,
        role: str = "user",
    ) -> bool:
        """
        Записывает сообщение и возвращает флаг `is_gift_hint`.
        Шанс = min(1, p0 * growth**fails).
        """
        await self.short.add(bot=bot, user_id=user_id, role=role, text=text)

        if role != "user":
            return False

        key = (user_id, bot)
        fails = self._gift_fail.get(key, 0)
        await self.r.incr(f"msg_no:{bot}:{user_id}")

        p0, g = self._gift_base, self._gift_growth
        p = min(1.0, p0 * (g**fails))

        if random.random() < p:
            self._gift_fail[key] = 0
            log.warning(f"GIFT {user_id} -> {bot}")
            return True
        else:
            self._gift_fail[key] = fails + 1
            return False

    async def add_summary_chunk(
        self,
        user_id: int,
        bot: str,
        text: str,
        old_chunks: list[UUID],
        *,
        chunk_type: str = "type1",
    ) -> None:
        """
        Ручное добавление summary-чанка:
        1) upsert нового чанка-саммари;
        2) удаление использованных чанков.
        :param user_id:     id пользователя
        :param bot:         кодовое имя бота
        :param text:        текст саммари
        :param old_chunks:  список UUID чанков, вошедших в саммари
        :param chunk_type:  тип нового чанка (по умолчанию 'type1')
        """
        # Эмбеддинг для саммари
        embedding = await self.embed.get_embedding(text)

        # Создаём новый Chunk
        summary_chunk = Chunk(
            chunk_id=uuid4(),
            bot=bot,
            user_id=user_id,
            chunk_type=chunk_type,
            created_at=datetime.now(UTC),
            last_hit=datetime.now(UTC),
            hit_count=0,
            text=text,
            persistent=False,
            summary_of=old_chunks,
        )

        # Записываем в Qdrant
        await self.long.upsert_chunk_with_vector(
            user_id=user_id,
            chunk=summary_chunk,
            embedding=embedding,
        )

        # Удаляем исходные чанки
        if old_chunks:
            await self.long.delete_chunks(user_id, old_chunks)

    async def drop_last_short(
        self, user_id: int, bot: str, n: int = 2
    ) -> list[dict]:
        """
        Удалить N последних сообщений из short-term и вернуть их содержимое.
        Пригодится, если нужно «отмотать» историю.
        """
        removed = await self.short.pop_last(user_id=user_id, bot=bot, n=n)
        # счётчик сообщений, чтобы merge-триггер продолжал работать
        if removed:
            await self.r.decrby(f"msg_no:{bot}:{user_id}", len(removed))
        return removed

    async def delete_memory(self, user_id: int, bot: str) -> None:
        """
        Полная очистка памяти данного (user_id, bot):
          • short-term  (Redis)
          • long-term   (Qdrant)
          • внутренние счётчики фасада (_msg_no, _gift_fail)
        """
        await self.short.clear(user_id=user_id, bot=bot)

        await self.long.delete_all(user_id, bot)

        self._msg_no.pop((user_id, bot), None)
        self._gift_fail.pop((user_id, bot), None)


    @staticmethod
    def _chunk_texts(chunks: Sequence[Chunk | ChunkPayload]) -> list[str]:
        """
        :param chunks: Последовательность Chunk или ChunkPayload.
        :returns: Список текстов из чанков.
        """
        return [c.text for c in chunks]
