from maxo.omit import Omittable, Omitted
from maxo.types.base import MaxoType


class PinMessageBody(MaxoType):
    message_id: str

    notify: Omittable[bool | None] = Omitted()
