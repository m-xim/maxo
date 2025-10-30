from asyncio import Lock
from collections import defaultdict
from collections.abc import AsyncIterator, Hashable
from contextlib import asynccontextmanager

from maxo.fsm.event_isolations.base import BaseEventIsolation
from maxo.fsm.key_builder import (
    DefaultKeyBuilder,
    KeyBuilder,
    StorageKey,
    StorageKeyType,
)


class SimpleEventIsolation(BaseEventIsolation):
    __slots__ = ("_key_builder", "_locks")

    def __init__(
        self,
        key_builder: KeyBuilder | None = None,
    ) -> None:
        if key_builder is None:
            key_builder = DefaultKeyBuilder()
        self._key_builder = key_builder

        self._locks: defaultdict[Hashable, Lock] = defaultdict(Lock)

    @asynccontextmanager
    async def lock(self, key: StorageKey) -> AsyncIterator[None]:
        built_key = self._key_builder.build(key, StorageKeyType.LOCK)

        lock = self._locks[built_key]
        async with lock:
            yield

    async def close(self) -> None:
        self._locks.clear()
