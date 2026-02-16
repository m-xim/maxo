from maxo.errors import AttributeIsEmptyError
from maxo.omit import Omittable, Omitted, is_defined
from maxo.types import PhotoToken
from maxo.types.base import MaxoType


class PhotoAttachmentRequestPayload(MaxoType):
    """
    Запрос на прикрепление изображения (все поля являются взаимоисключающими)

    Args:
        photos: Токены, полученные после загрузки изображений
        token: Токен существующего вложения
        url: Любой внешний URL изображения, которое вы хотите прикрепить
    """

    photos: Omittable[list[PhotoToken] | None] = Omitted()  # TODO: Проверить кто это
    token: Omittable[str | None] = Omitted()
    url: Omittable[str | None] = Omitted()

    @property
    def unsafe_photos(self) -> list[PhotoToken]:
        if is_defined(self.photos):
            return self.photos

        raise AttributeIsEmptyError(
            obj=self,
            attr="photos",
        )

    @property
    def unsafe_token(self) -> str:
        if is_defined(self.token):
            return self.token

        raise AttributeIsEmptyError(
            obj=self,
            attr="token",
        )

    @property
    def unsafe_url(self) -> str:
        if is_defined(self.url):
            return self.url

        raise AttributeIsEmptyError(
            obj=self,
            attr="url",
        )
