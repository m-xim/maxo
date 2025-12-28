from maxo.enums.chat_admin_permission import ChatAdminPermission
from maxo.types.base import MaxoType


class ChatAdmin(MaxoType):
    """
    Администратора чата.

    Args:
        user_id: Идентификатор администратора с правами доступа.
        permissions: Перечень прав пользователя.
        alias:
            Заголовок, который будет показан на клиенте
            Если пользователь администратор или владелец
            и ему не установлено это название, то поле не передается,
            клиенты на своей стороне подменят на "владелец" или "админ".

    """

    alias: str
    permissions: list[ChatAdminPermission]
    user_id: int
