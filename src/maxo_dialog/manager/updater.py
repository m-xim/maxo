import asyncio
from contextvars import copy_context

from maxo import Bot, Dispatcher
from maxo_dialog.api.entities import DialogUpdate, DialogUpdateEvent


class Updater:
    def __init__(self, dp: Dispatcher):
        if not isinstance(dp, Dispatcher):
            raise TypeError("Root router must be Dispatcher.")
        self.dp = dp

    async def notify(self, bot: Bot, update: DialogUpdate) -> None:
        def callback():
            asyncio.create_task(  # noqa: RUF006
                self._process_update(bot, update),
            )

        asyncio.get_running_loop().call_soon(callback, context=copy_context())

    async def _process_update(self, bot: Bot, update: DialogUpdate) -> None:
        event = update.event
        await self.dp.feed_update(
            DialogUpdate(
                aiogd_update=DialogUpdateEvent(
                    update_type="update",
                    event=update,
                    bot=bot,
                    event_from_user=event.from_user,
                    event_chat=event.chat,
                    event_thread_id=event.thread_id,
                    **self.dp.workflow_data,
                )
            )
        )
