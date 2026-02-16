from maxo.enums.update_type import UpdateType
from maxo.routing.updates.base import MaxUpdate
from maxo.types.user import User


class DialogUnmuted(MaxUpdate):
    """
    Вы получите этот update, когда пользователь включит уведомления в диалоге с ботом

    Args:
        chat_id: ID чата, где произошло событие
        type:
        user: Пользователь, который включил уведомления
        user_locale: Текущий язык пользователя в формате IETF BCP 47
    """

    type = UpdateType.DIALOG_UNMUTED

    chat_id: int
    user: User
    user_locale: str
