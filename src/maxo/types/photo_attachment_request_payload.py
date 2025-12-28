from typing import Any

from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType


class PhotoAttachmentRequestPayload(MaxoType):
    """Запрос на прикрепление изображения (все поля являются взаимоисключающими)"""

    photos: Omittable[dict[str, Any] | None] = Omitted()
    token: Omittable[str | None] = Omitted()
    url: Omittable[str | None] = Omitted()
