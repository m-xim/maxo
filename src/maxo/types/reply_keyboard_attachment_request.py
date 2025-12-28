from maxo.omit import Omittable, Omitted
from maxo.types import ReplyButtons
from maxo.types.attachment_request import AttachmentRequest


class ReplyKeyboardAttachmentRequest(AttachmentRequest):
    """Request to attach reply keyboard to message"""

    buttons: list[list[ReplyButtons]]

    direct: Omittable[bool] = Omitted()
    direct_user_id: Omittable[int | None] = Omitted()
