from maxo.bot.methods.base import MaxoMethod
from maxo.types.bot_info import BotInfo


class GetMyInfo(MaxoMethod[BotInfo]):
    """Получение информации о боте."""

    __url__ = "me"
    __http_method__ = "get"
