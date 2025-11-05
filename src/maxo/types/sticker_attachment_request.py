from typing import Self

from maxo.types.base import MaxoType
from maxo.types.sticker_attachment_request_payload import (
    StickerAttachmentRequestPayload,
)


class StickerAttachmentRequest(MaxoType):
    """
    Запрос на прикрепление стикера.

    Args:
        payload: Данные для запроса прикрепления стикера.

    """

    payload: StickerAttachmentRequestPayload

    @classmethod
    def factory(cls, code: str) -> Self:
        """
        Фабричный метод.

        Args:
            code: Код стикера

        """
        return cls(
            payload=StickerAttachmentRequestPayload(
                code=code,
            ),
        )
