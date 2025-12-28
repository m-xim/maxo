from maxo.types import ReplyButtons
from maxo.types.attachment import Attachment


class ReplyKeyboardAttachment(Attachment):
    """Custom reply keyboard in message"""

    buttons: list[list[ReplyButtons]]
