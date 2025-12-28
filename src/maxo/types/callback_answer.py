from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType
from maxo.types.new_message_body import NewMessageBody


class CallbackAnswer(MaxoType):
    """Отправьте этот объект, когда ваш бот хочет отреагировать на нажатие кнопки"""

    message: Omittable[NewMessageBody | None] = Omitted()
    notification: Omittable[str | None] = Omitted()
