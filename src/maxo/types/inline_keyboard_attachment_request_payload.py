from maxo.types import InlineButtons
from maxo.types.base import MaxoType


class InlineKeyboardAttachmentRequestPayload(MaxoType):
    buttons: list[list[InlineButtons]]
