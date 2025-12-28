from maxo.enums.attachment_request_type import AttachmentRequestType
from maxo.types.attachment_request import AttachmentRequest
from maxo.types.contact_attachment_request_payload import (
    ContactAttachmentRequestPayload,
)


class ContactAttachmentRequest(AttachmentRequest):
    """Запрос на прикрепление карточки контакта к сообщению. MДОЛЖЕН быть единственным вложением в сообщении"""

    type: AttachmentRequestType = AttachmentRequestType.CONTACT

    payload: ContactAttachmentRequestPayload
