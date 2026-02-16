from maxo.enums.update_type import UpdateType
from maxo.routing.updates.base import MaxUpdate


class MessageRemoved(MaxUpdate):
    """
    Вы получите этот `update`, как только сообщение будет удалено

    Args:
        chat_id: ID чата, где сообщение было удалено
        message_id: ID удаленного сообщения
        type:
        user_id: Пользователь, удаливший сообщение
    """

    type = UpdateType.MESSAGE_REMOVED

    chat_id: int
    message_id: str
    user_id: int
