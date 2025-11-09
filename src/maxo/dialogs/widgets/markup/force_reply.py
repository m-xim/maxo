from typing import Optional

from maxo.dialogs import DialogManager
from maxo.dialogs.api.internal.widgets import (
    MarkupFactory,
    MarkupVariant,
    RawKeyboard,
)
from maxo.dialogs.widgets.text import Text


class ForceReplyFactory(MarkupFactory):
    def __init__(
        self,
        input_field_placeholder: Optional[Text] = None,
        selective: Optional[bool] = None,
    ):
        self.input_field_placeholder = input_field_placeholder
        self.selective = selective

    async def render_markup(
        self,
        data: dict,
        manager: DialogManager,
        keyboard: RawKeyboard,
    ) -> MarkupVariant:
        if self.input_field_placeholder:
            placeholder = await self.input_field_placeholder.render_text(
                data,
                manager,
            )
        else:
            placeholder = None
        # TODO validate keyboard
        return ForceReply(
            input_field_placeholder=placeholder,
            selective=self.selective,
        )
