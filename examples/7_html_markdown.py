import logging
import os

from maxo import Bot, Dispatcher
from maxo.enums import TextFormat
from maxo.routing.updates.message_created import MessageCreated
from maxo.utils.facades.updates.message_created import MessageCreatedFacade
from maxo.utils.long_polling import LongPolling

bot = Bot(os.environ["TOKEN"])
dispatcher = Dispatcher()


@dispatcher.message_created()
async def text_decoration_handler(
    update: MessageCreated,
    facade: MessageCreatedFacade,
) -> None:
    html = update.message.body.html_text
    md = update.message.body.md_text
    await facade.reply_text(text=html)
    await facade.reply_text(text=html, format=TextFormat.HTML)
    await facade.reply_text(text=md)
    await facade.reply_text(text=md, format=TextFormat.MARKDOWN)


logging.basicConfig(level=logging.DEBUG)
LongPolling(dispatcher).run(bot)
