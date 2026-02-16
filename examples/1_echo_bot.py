import logging
import os

from maxo import Bot, Dispatcher
from maxo.routing.updates.message_created import MessageCreated
from maxo.utils.facades.updates.message_created import MessageCreatedFacade
from maxo.utils.long_polling import LongPolling

bot = Bot(os.environ["TOKEN"])
dispatcher = Dispatcher()


@dispatcher.message_created()
async def echo_handler(
    update: MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    text = update.message.body.text or "Текста нет"
    await facade.answer_text(text)


logging.basicConfig(level=logging.DEBUG)
LongPolling(dispatcher).run(bot)
