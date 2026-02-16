from datetime import datetime

from maxo.errors import AttributeIsEmptyError
from maxo.omit import Omittable, Omitted, is_defined
from maxo.types.base import MaxoType
from maxo.types.user import User


class Callback(MaxoType):
    """
    Объект, отправленный боту, когда пользователь нажимает кнопку

    Args:
        callback_id: Текущий ID клавиатуры
        payload: Токен кнопки
        timestamp: Unix-время, когда пользователь нажал кнопку
        user: Пользователь, нажавший на кнопку
    """

    callback_id: str
    timestamp: datetime
    user: User

    payload: Omittable[str] = Omitted()

    @property
    def id(self) -> str:
        return self.callback_id

    @property
    def unsafe_payload(self) -> str:
        if is_defined(self.payload):
            return self.payload

        raise AttributeIsEmptyError(
            obj=self,
            attr="payload",
        )
