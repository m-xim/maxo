from datetime import datetime

from maxo.enums.chat_admin_permission import ChatAdminPermission
from maxo.types.user_with_photo import UserWithPhoto


class ChatMember(UserWithPhoto):
    """
    Информация о членстве в чате.

    Объект, описывающий участника чата.

    Args:
        is_owner: Является ли пользователь владельцем чата.
        is_admin: Является ли пользователь администратором чата
        join_time: Дата присоединения к чату в формате Unix time
        permissions: Перечень прав пользователя.
        alias: Заголовок, который будет показан на клиенте.

    """

    alias: str
    is_admin: bool
    is_owner: bool
    join_time: datetime
    last_access_time: datetime

    permissions: list[ChatAdminPermission] | None = None
