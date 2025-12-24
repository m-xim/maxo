from typing import Generic, TypeVar

from maxo.routing.signals import Update
from maxo.routing.updates.base import BaseUpdate

_UpdateT = TypeVar("_UpdateT", bound=BaseUpdate)
_ExceptionT = TypeVar("_ExceptionT", bound=Exception)


class ErrorEvent(BaseUpdate, Generic[_ExceptionT, _UpdateT]):
    exception: _ExceptionT
    update: Update[_UpdateT]

    @property
    def error(self) -> _ExceptionT:
        return self.exception

    @property
    def event(self) -> _UpdateT:
        return self.update.update
