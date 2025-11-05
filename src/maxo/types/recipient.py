from maxo.enums.chat_type import ChatType
from maxo.types.base import MaxoType


class Recipient(MaxoType):
    """
    Получатель сообщения.

    Args:
        chat_type: Тип чата.
        user_id: ID пользователя, если сообщение было отправлено пользователю.
        chat_id: ID чата.

    """

    chat_type: ChatType
    user_id: int | None = None
    chat_id: int | None = None

    @property
    def id(self) -> int:
        if self.chat_type == ChatType.DIALOG:
            return self.user_id
        if self.chat_type == ChatType.CHAT:
            return self.chat_id
        raise RuntimeError("Неизвестный тип чата")
