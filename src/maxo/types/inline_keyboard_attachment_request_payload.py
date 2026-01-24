from maxo.types.base import MaxoType
from maxo.types.button import Button


class InlineKeyboardAttachmentRequestPayload(MaxoType):
    buttons: list[list[Button]]
