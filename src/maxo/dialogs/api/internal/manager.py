from abc import abstractmethod
from typing import Protocol

from maxo import Ctx
from maxo.routing.interfaces import BaseRouter
from maxo.dialogs.api.entities import ChatEvent
from maxo.dialogs.api.protocols import (
    DialogManager,
    DialogRegistryProtocol,
)


class DialogManagerFactory(Protocol):
    @abstractmethod
    def __call__(
        self,
        event: ChatEvent,
        ctx: Ctx,
        registry: DialogRegistryProtocol,
        router: BaseRouter,
    ) -> DialogManager:
        raise NotImplementedError
