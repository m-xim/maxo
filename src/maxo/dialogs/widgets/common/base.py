from typing import Any, Optional

from maxo.dialogs import DialogManager
from maxo.dialogs.api.internal import Widget


class BaseWidget(Widget):
    def managed(self, manager: DialogManager) -> Any:
        return self

    def find(self, widget_id: str) -> Optional["Widget"]:
        return None
