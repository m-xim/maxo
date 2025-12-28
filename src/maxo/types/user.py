from datetime import datetime

from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType


class User(MaxoType):
    """
    Объект, описывающий пользователя. Имеет несколько вариаций (наследований):

    - [`User`](/docs-api/objects/User)
    - [`UserWithPhoto`](/docs-api/objects/UserWithPhoto)
    - [`BotInfo`](/docs-api/objects/BotInfo)
    - [`ChatMember`](/docs-api/objects/ChatMember)
    """

    first_name: str
    is_bot: bool
    last_activity_time: datetime
    user_id: int

    last_name: str | None = None
    username: str | None = None

    name: Omittable[str | None] = Omitted()

    @property
    def id(self) -> int:
        return self.user_id

    @property
    def fullname(self) -> str | None:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        return None
