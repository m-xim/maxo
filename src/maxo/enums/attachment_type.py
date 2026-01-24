from enum import StrEnum


class AttachmentType(StrEnum):
    """Общая схема, представляющая вложение сообщения"""

    AUDIO = "audio"
    CONTACT = "contact"
    DATA = "data"
    FILE = "file"
    IMAGE = "image"
    INLINE_KEYBOARD = "inline_keyboard"
    REPLY_KEYBOARD = "reply_keyboard"
    LOCATION = "location"
    SHARE = "share"
    STICKER = "sticker"
    VIDEO = "video"
