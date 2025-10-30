from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from maxo.fsm.event_isolations.base import BaseEventIsolation
from maxo.fsm.key_builder import StorageKey


class DisabledEventIsolation(BaseEventIsolation):
    @asynccontextmanager
    async def lock(self, key: StorageKey) -> AsyncIterator[None]:
        yield

    async def close(self) -> None:
        pass
