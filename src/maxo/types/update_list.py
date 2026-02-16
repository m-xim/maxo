from maxo.errors import AttributeIsEmptyError
from maxo.omit import is_defined
from maxo.routing.updates import Updates
from maxo.types.base import MaxoType


class UpdateList(MaxoType):
    """
    Список всех обновлений в чатах, в которых ваш бот участвовал

    Args:
        marker: Указатель на следующую страницу данных
        updates: Страница обновлений
    """

    updates: list[Updates]

    marker: int | None = None

    @property
    def unsafe_marker(self) -> int:
        if is_defined(self.marker):
            return self.marker

        raise AttributeIsEmptyError(
            obj=self,
            attr="marker",
        )
