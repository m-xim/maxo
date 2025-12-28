from maxo.omit import Omittable, Omitted
from maxo.types.user import User


class UserWithPhoto(User):
    """Объект пользователя с фотографией"""

    avatar_url: Omittable[str] = Omitted()
    description: Omittable[str | None] = Omitted()
    full_avatar_url: Omittable[str] = Omitted()
