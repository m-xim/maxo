from maxo.routing.updates import MaxUpdate
from maxo.types.base import MaxoType


class UpdateList(MaxoType):
    """Список всех обновлений в чатах, в которых ваш бот участвовал"""

    updates: list[MaxUpdate]

    marker: int | None = None
