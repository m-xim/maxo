from maxo.enums.text_format import TextFormat
from maxo.omit import Omittable, Omitted
from maxo.types import AttachmentsRequests
from maxo.types.base import MaxoType
from maxo.types.new_message_link import NewMessageLink


class NewMessageBody(MaxoType):
    """
    Новое тело сообщения.

    Args:
        text: Новый текст сообщения. До 4000 символов.
        attachments: Вложения сообщения. Если пусто, все вложения будут удалены.
        link: Ссылка на сообщение.
        notify: Если false, участники чата не будут уведомлены (по умолчанию true).
        format:
            Если установлен, текст сообщения будет форматрован данным способом.
            Для подробной информации загляните в раздел Форматирование

    """

    attachments: list[AttachmentsRequests] | None = None
    link: NewMessageLink | None = None
    text: str | None = None

    format: Omittable[TextFormat | None] = Omitted()
    notify: Omittable[bool] = Omitted()
