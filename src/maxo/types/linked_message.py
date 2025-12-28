from maxo.enums.message_link_type import MessageLinkType
from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType
from maxo.types.message_body import MessageBody
from maxo.types.user import User


class LinkedMessage(MaxoType):
    """
    Пересланное или ответное сообщение.

    Args:
        type: Тип связанного сообщения.
        sender: Пользователь, отправивший сообщение.
        chat_id: Чат, в котором сообщение было изначально опубликовано. Только для пересланных сообщений
        message: Схема, представляющая тело сообщения

    """

    message: MessageBody
    type: MessageLinkType

    chat_id: Omittable[int] = Omitted()
    sender: Omittable[User] = Omitted()
