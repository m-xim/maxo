from datetime import datetime
from typing import Any

from maxo.enums.chat_status import ChatStatus
from maxo.enums.chat_type import ChatType
from maxo.errors import AttributeIsEmptyError
from maxo.omit import Omittable, Omitted, is_defined
from maxo.types.base import MaxoType
from maxo.types.image import Image
from maxo.types.message import Message
from maxo.types.user_with_photo import UserWithPhoto


class Chat(MaxoType):
    """
    Args:
        chat_id: ID чата
        chat_message_id: ID сообщения, содержащего кнопку, через которую был инициирован чат
        description: Описание чата
        dialog_with_user: Данные о пользователе в диалоге (только для чатов типа `"dialog"`)
        icon: Иконка чата
        is_public: Доступен ли чат публично (для диалогов всегда `false`)
        last_event_time: Время последнего события в чате
        link: Ссылка на чат
        owner_id: ID владельца чата
        participants: Участники чата с временем последней активности. Может быть `null`, если запрашивается список чатов
        participants_count: Количество участников чата. Для диалогов всегда `2`
        pinned_message: Закреплённое сообщение в чате (возвращается только при запросе конкретного чата)
        status: Статус чата:
            - `"active"` — Бот является активным участником чата.
            - `"removed"` — Бот был удалён из чата.
            - `"left"` — Бот покинул чат.
            - `"closed"` — Чат был закрыт.
        title: Отображаемое название чата. Может быть `null` для диалогов
        type: Тип чата:
             - `"chat"` — Групповой чат.
    """

    chat_id: int
    is_public: bool
    last_event_time: datetime
    participants_count: int
    status: ChatStatus
    type: ChatType

    description: str | None = None
    icon: Image | None = None
    title: str | None = None

    chat_message_id: Omittable[str | None] = Omitted()
    dialog_with_user: Omittable[UserWithPhoto | None] = Omitted()
    link: Omittable[str | None] = Omitted()
    owner_id: Omittable[int | None] = Omitted()
    participants: Omittable[dict[str, Any] | None] = Omitted()
    pinned_message: Omittable[Message | None] = Omitted()

    @property
    def id(self) -> int:
        return self.chat_id

    @property
    def unsafe_chat_message_id(self) -> str:
        if is_defined(self.chat_message_id):
            return self.chat_message_id

        raise AttributeIsEmptyError(
            obj=self,
            attr="chat_message_id",
        )

    @property
    def unsafe_description(self) -> str:
        if is_defined(self.description):
            return self.description

        raise AttributeIsEmptyError(
            obj=self,
            attr="description",
        )

    @property
    def unsafe_dialog_with_user(self) -> UserWithPhoto:
        if is_defined(self.dialog_with_user):
            return self.dialog_with_user

        raise AttributeIsEmptyError(
            obj=self,
            attr="dialog_with_user",
        )

    @property
    def unsafe_icon(self) -> Image:
        if is_defined(self.icon):
            return self.icon

        raise AttributeIsEmptyError(
            obj=self,
            attr="icon",
        )

    @property
    def unsafe_link(self) -> str:
        if is_defined(self.link):
            return self.link

        raise AttributeIsEmptyError(
            obj=self,
            attr="link",
        )

    @property
    def unsafe_owner_id(self) -> int:
        if is_defined(self.owner_id):
            return self.owner_id

        raise AttributeIsEmptyError(
            obj=self,
            attr="owner_id",
        )

    @property
    def unsafe_participants(self) -> dict[str, Any]:
        if is_defined(self.participants):
            return self.participants

        raise AttributeIsEmptyError(
            obj=self,
            attr="participants",
        )

    @property
    def unsafe_pinned_message(self) -> Message:
        if is_defined(self.pinned_message):
            return self.pinned_message

        raise AttributeIsEmptyError(
            obj=self,
            attr="pinned_message",
        )

    @property
    def unsafe_title(self) -> str:
        if is_defined(self.title):
            return self.title

        raise AttributeIsEmptyError(
            obj=self,
            attr="title",
        )
