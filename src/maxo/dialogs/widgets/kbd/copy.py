from typing import Any

from maxo.types import CallbackKeyboardButton
from maxo.dialogs import DialogManager
from maxo.dialogs.api.internal import RawKeyboard
from maxo.dialogs.widgets.common import WhenCondition
from maxo.dialogs.widgets.kbd import Keyboard
from maxo.dialogs.widgets.text import Text


class CopyText(Keyboard):
    def __init__(
        self,
        text: Text,
        copy_text: Text,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(when=when)
        self._text = text
        self._copy_text = copy_text

    async def _render_keyboard(
        self,
        data: dict[str, Any],
        manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                CallbackKeyboardButton(
                    text=await self._text.render_text(data, manager),
                    copy_text=CopyTextButton(
                        text=await self._copy_text.render_text(data, manager),
                    ),
                ),
            ],
        ]
