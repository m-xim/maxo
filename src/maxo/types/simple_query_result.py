from maxo.errors import AttributeIsEmptyError
from maxo.omit import Omittable, Omitted, is_defined
from maxo.types.base import MaxoType


class SimpleQueryResult(MaxoType):
    """
    Простой ответ на запрос

    Args:
        message: Объяснительное сообщение, если результат не был успешным
        success: `true`, если запрос был успешным, `false` в противном случае
    """

    success: bool

    message: Omittable[str] = Omitted()

    @property
    def unsafe_message(self) -> str:
        if is_defined(self.message):
            return self.message

        raise AttributeIsEmptyError(
            obj=self,
            attr="message",
        )
