from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, ClassVar, Self, dataclass_transform

from maxo.enums.update_type import UpdateType
from maxo.errors import AttributeIsEmptyError

if TYPE_CHECKING:
    from maxo.bot.bot import Bot


@dataclass_transform(
    frozen_default=False,
    kw_only_default=True,
)
class _MaxoTypeMetaClass(type):
    def __new__(
        cls,
        name: str,
        bases: tuple[Any, ...],
        namespace: dict[str, Any],
        slots: bool = True,
        **kwargs: Any,
    ) -> Any:
        class_ = super().__new__(cls, name, bases, namespace, **kwargs)
        # `dataclass(slots=True)` re-creates the class through this metaclass
        # with `__slots__` set: don't wrap it twice.
        if "__slots__" in namespace:
            return class_

        return dataclass(
            slots=slots,
            frozen=False,
            kw_only=True,
        )(class_)


class MaxoType(metaclass=_MaxoTypeMetaClass):
    """
    Base of all maxo dataclasses. Holds no bot.

    Subclasses become `@dataclass(slots=True, kw_only=True)` automatically;
    `class X(MaxoType, slots=False)` disables slots.
    """


class FacadeMaxoType(MaxoType):
    """
    Type that holds the bot: updates and messages.

    `_bot` is a field, so `dataclasses.replace` and `copy` keep it
    """

    _bot: "Bot | None" = field(default=None, repr=False, compare=False)

    @property
    def bot(self) -> "Bot":
        if self._bot is not None:
            return self._bot

        raise AttributeIsEmptyError(
            obj=self,
            attr="bot",
        )

    def as_(self, bot: "Bot | None") -> Self:
        """Bind the bot to self and every nested `FacadeMaxoType`."""
        from maxo.types.binding import bind_bot  # noqa: PLC0415

        return bind_bot(self, bot)


class BaseUpdate(MaxoType):
    """Routing event: MAX update, signal or error."""


class MaxUpdate(BaseUpdate, FacadeMaxoType):
    """
    Базовый класс для всех апдейтов из Макса.

    У всех апдейтов есть тип (`type`, `update_type`) и время (`timestamp`).
    Методы для работы с апдейтом (например, отправить сообщение или ответить
    на колбэк) подмешаны в сам апдейт через `*MethodsFacade`.
    """

    type: ClassVar[UpdateType]
    timestamp: datetime

    @property
    def update_type(self) -> UpdateType:
        return self.type
