from enum import StrEnum


class AttachmentType(StrEnum):
    """Общая схема, представляющая вложение сообщения"""

    AUDIO = "audio"
    CONTACT = "contact"
    FILE = "file"
    IMAGE = "image"
    INLINE_KEYBOARD = "inline_keyboard"
    LOCATION = "location"
    SHARE = "share"
    STICKER = "sticker"
    VIDEO = "video"
