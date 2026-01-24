from retejo.http.markers import Body, QueryParam

from maxo.bot.methods.base import MaxoMethod
from maxo.enums.text_format import TextFormat
from maxo.omit import Omittable, Omitted
from maxo.types.attachments import AttachmentsRequests
from maxo.types.new_message_link import NewMessageLink
from maxo.types.send_message_result import SendMessageResult


class SendMessage(MaxoMethod[SendMessageResult]):
    """Отправить сообщение."""

    __url__ = "messages"
    __http_method__ = "post"

    chat_id: QueryParam[Omittable[int]] = Omitted()
    disable_link_preview: QueryParam[Omittable[bool]] = Omitted()
    user_id: QueryParam[Omittable[int]] = Omitted()

    attachments: Body[list[AttachmentsRequests] | None] = None
    link: Body[NewMessageLink | None] = None
    text: Body[str | None] = None
    format: Body[Omittable[TextFormat | None]] = Omitted()
    notify: Body[Omittable[bool]] = Omitted()
