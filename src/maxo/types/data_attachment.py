from maxo.types.attachment import Attachment


class DataAttachment(Attachment):
    """Attachment contains payload sent through `SendMessageButton`"""

    data: str
