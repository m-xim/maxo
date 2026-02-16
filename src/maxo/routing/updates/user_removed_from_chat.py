from maxo.enums.update_type import UpdateType
from maxo.errors import AttributeIsEmptyError
from maxo.omit import Omittable, Omitted, is_defined
from maxo.routing.updates.base import MaxUpdate
from maxo.types.user import User


class UserRemovedFromChat(MaxUpdate):
    """
    Вы получите это обновление, когда пользователь будет удалён из чата, где бот является администратором

    Args:
        admin_id: Администратор, который удалил пользователя из чата. Может быть `null`, если пользователь покинул чат сам
        chat_id: ID чата, где произошло событие
        is_channel: Указывает, был ли пользователь удалён из канала или нет
        type:
        user: Пользователь, удалённый из чата
    """

    type = UpdateType.USER_REMOVED

    chat_id: int
    is_channel: bool
    user: User

    admin_id: Omittable[int] = Omitted()

    @property
    def unsafe_admin_id(self) -> int:
        if is_defined(self.admin_id):
            return self.admin_id

        raise AttributeIsEmptyError(
            obj=self,
            attr="admin_id",
        )
