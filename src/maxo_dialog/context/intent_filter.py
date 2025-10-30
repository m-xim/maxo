from typing import Optional

from maxo.filters import BaseFilter
from maxo.fsm import StatesGroup
from maxo.types import TelegramObject
from maxo_dialog.api.entities import Context
from maxo_dialog.api.internal import CONTEXT_KEY


class IntentFilter(BaseFilter):
    def __init__(self, aiogd_intent_state_group: Optional[type[StatesGroup]]):
        self.aiogd_intent_state_group = aiogd_intent_state_group

    async def __call__(self, obj: TelegramObject, **kwargs) -> bool:
        del obj  # unused
        if self.aiogd_intent_state_group is None:
            return True

        context: Context = kwargs.get(CONTEXT_KEY)
        if not context:
            return False
        return context.state.group == self.aiogd_intent_state_group
