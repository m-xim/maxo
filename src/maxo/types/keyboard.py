from maxo.types import InlineButtons
from maxo.types.base import MaxoType


class Keyboard(MaxoType):
    """Клавиатура - это двумерный массив кнопок"""

    buttons: list[list[InlineButtons]]
