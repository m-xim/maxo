from maxo.enums.intent import Intent
from maxo.enums.reply_button_type import ReplyButtonType
from maxo.omit import Omittable, Omitted
from maxo.types.reply_button import ReplyButton


class SendMessageButton(ReplyButton):
    """After pressing this type of button client will send a message on behalf of user with given payload"""

    type: ReplyButtonType = ReplyButtonType.MESSAGE

    intent: Omittable[Intent] = Omitted()
