from collections.abc import Mapping
from typing import Any, final

from maxo.routing.ctx import Ctx
from maxo.routing.interfaces.middleware import BaseMiddleware, NextMiddleware
from maxo.routing.signals.update import Update
from maxo.routing.updates.base import BaseUpdate
from maxo.routing.updates.message_callback import MessageCallback
from maxo.routing.updates.message_created import MessageCreated
from maxo.tools.facades.updates.base import BaseUpdateFacade
from maxo.tools.facades.updates.message_callback import MessageCallbackFacade
from maxo.tools.facades.updates.message_created import MessageCreatedFacade

_FACEDS_MAP: Mapping[type[Any], type[BaseUpdateFacade[Any]]] = {
    MessageCreated: MessageCreatedFacade,
    MessageCallback: MessageCallbackFacade,
}


class FacadeMiddleware(BaseMiddleware[Update[Any]]):
    @final
    async def __call__(
        self,
        update: Update[Any],
        ctx: Ctx[Update[Any]],
        next: NextMiddleware[Update[Any]],
    ) -> Any:
        facade = self._facade_cls_factory(type(update.update))
        ctx.facade = facade(ctx.bot, update.update)

        return await next(ctx)

    def _facade_cls_factory(
        self,
        update_tp: type[BaseUpdate],
    ) -> type[BaseUpdateFacade[Any]]:
        return _FACEDS_MAP[update_tp]
