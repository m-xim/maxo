from maxo.enums.button_type import ButtonType
from maxo.enums.intent import Intent
from maxo.omit import Omittable, Omitted
from maxo.types.button import Button


class CallbackButton(Button):
    """
    Инлайн кнопка с токеном.

    После нажатия на такую кнопку клиент отправляет на сервер полезную нагрузку, которая содержит.

    Args:
        text: Видимый текст кнопки. От 1 до 128 символов.
        payload: Токен кнопки. До 1024 символов.
        intent: Намерение кнопки. Влияет на отображение клиентом.

    """

    type: ButtonType = ButtonType.CALLBACK

    payload: str

    intent: Omittable[Intent] = Omitted()
