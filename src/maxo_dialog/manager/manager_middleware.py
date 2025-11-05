from collections.abc import Awaitable, Callable
from typing import Any, Union

from maxo.routing.interfaces import BaseMiddleware, Router
from maxo.routing.updates.base import MaxUpdate
from maxo.types import MaxoType
from maxo_dialog.api.entities import ChatEvent, DialogUpdateEvent
from maxo_dialog.api.internal import STORAGE_KEY, DialogManagerFactory
from maxo_dialog.api.protocols import (
    BgManagerFactory,
    DialogManager,
    DialogRegistryProtocol,
)

MANAGER_KEY = "dialog_manager"
BG_FACTORY_KEY = "dialog_bg_factory"


class ManagerMiddleware(BaseMiddleware):
    def __init__(
        self,
        dialog_manager_factory: DialogManagerFactory,
        registry: DialogRegistryProtocol,
        router: Router,
    ) -> None:
        super().__init__()
        self.dialog_manager_factory = dialog_manager_factory
        self.registry = registry
        self.router = router

    def _is_event_supported(
        self,
        event: MaxoType,
        data: dict[str, Any],
    ) -> bool:
        return STORAGE_KEY in data

    async def __call__(
        self,
        handler: Callable[
            [Union[MaxUpdate, DialogUpdateEvent], dict[str, Any]],
            Awaitable[Any],
        ],
        event: ChatEvent,
        data: dict[str, Any],
    ) -> Any:
        if self._is_event_supported(event, data):
            data[MANAGER_KEY] = self.dialog_manager_factory(
                event=event,
                data=data,
                registry=self.registry,
                router=self.router,
            )

        try:
            return await handler(event, data)
        finally:
            manager: DialogManager | None = data.pop(MANAGER_KEY, None)
            if manager:
                await manager.close_manager()


class BgFactoryMiddleware(BaseMiddleware):
    def __init__(
        self,
        bg_manager_factory: BgManagerFactory,
    ) -> None:
        super().__init__()
        self.bg_manager_factory = bg_manager_factory

    async def __call__(
        self,
        handler: Callable[
            [Union[MaxoType, DialogUpdateEvent], dict[str, Any]],
            Awaitable[MaxoType],
        ],
        event: MaxoType,
        data: dict[str, Any],
    ) -> Any:
        data[BG_FACTORY_KEY] = self.bg_manager_factory
        return await handler(event, data)
