import asyncio
from collections.abc import AsyncIterator, Iterable, Sequence
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Self

from unihttp.bind_method import bind_method
from unihttp.clients.base import BaseAsyncClient
from unihttp.http.response import HTTPResponse
from unihttp.http.stream import AsyncChunkStream
from unihttp.method import BaseMethod, ResponseType, StreamMethod
from unihttp.middlewares import AsyncMiddleware

from maxo.bot.client import default_client
from maxo.bot.defaults import BotDefaults, apply_defaults
from maxo.bot.media import Media
from maxo.bot.methods import (  # type: ignore[deprecated]
    AddMembers,
    AnswerOnCallback,
    DeleteAdmins,
    DeleteChat,
    DeleteComment,
    DeleteMessage,
    EditBotInfo,
    EditChat,
    EditComment,
    EditMessage,
    EditMyCommands,
    GetAdmins,
    GetChat,
    GetChatByLink,
    GetChats,
    GetCommentById,
    GetComments,
    GetMembers,
    GetMembership,
    GetMessageById,
    GetMessages,
    GetMyInfo,
    GetPinnedMessage,
    GetSubscriptions,
    GetUpdates,
    GetUploadUrl,
    GetVideoAttachmentDetails,
    LeaveChat,
    PinMessage,
    RemoveMember,
    SendAction,
    SendComment,
    SendMessage,
    SetAdmins,
    Subscribe,
    UnpinMessage,
    Unsubscribe,
)
from maxo.bot.middlewares import (
    AttachmentNotReadyRetryMiddleware,
    AuthMiddleware,
    NetworkErrorMiddleware,
)
from maxo.bot.upload import UploadConfig
from maxo.bot.warming_up import warm_up
from maxo.errors import UnsubscribeError
from maxo.errors.state import StateError
from maxo.types import BotInfo, ClearSubscriptionsResult
from maxo.types.binding import bind_bot


class Bot(BaseAsyncClient):  # BaseAsyncClient for mypy
    def __init__(
        self,
        token: str,
        *,
        defaults: BotDefaults | None = None,
        upload_config: UploadConfig | None = None,
        warming_up: bool = True,
        client: BaseAsyncClient | None = None,
        media_client: BaseAsyncClient | None = None,
        middlewares: Sequence[AsyncMiddleware] = (),
    ) -> None:
        self._defaults = defaults or BotDefaults()
        self._token = token
        self._upload_config = (
            upload_config if upload_config is not None else UploadConfig()
        )

        self.middleware: list[AsyncMiddleware] = [
            *middlewares,
            AuthMiddleware(self._token),
            AttachmentNotReadyRetryMiddleware(
                max_retries=self._upload_config.not_ready_max_retries,
                backoff_config=self._upload_config.not_ready_backoff,
            ),
            NetworkErrorMiddleware(),
        ]
        self._client = client
        self._owns_client = client is None

        if warming_up:
            warm_up()

        self._info: BotInfo | None = None
        self._me_lock = asyncio.Lock()
        self._media = Media(self, client=media_client)

    @property
    def client(self) -> BaseAsyncClient:
        if self._client is None:
            self._client = default_client()
        return self._client

    @property
    def media(self) -> Media:
        """Клиент файловых хостов: загрузка, вложения, скачивание."""
        return self._media

    @property
    def info(self) -> BotInfo:
        if self._info is None:
            raise StateError("Bot info is not resolved yet")
        return self._info

    @property
    def defaults(self) -> BotDefaults:
        return self._defaults

    @property
    def upload_config(self) -> UploadConfig:
        return self._upload_config

    @property
    def token(self) -> str:
        return self._token

    @asynccontextmanager
    async def context(
        self,
        auto_close: bool = True,
        get_my_info: bool = True,
    ) -> AsyncIterator[Self]:
        try:
            if get_my_info:
                await self.get_my_info()
            yield self
        finally:
            if auto_close:
                await self.close()

    async def __aenter__(self) -> Self:
        await self.me()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def me(self) -> BotInfo:
        """Lazy `get_my_info`: hits the API only on the first call."""
        if self._info is None:
            async with self._me_lock:
                if self._info is None:
                    return await self.get_my_info()
        return self.info

    async def get_my_info(self) -> BotInfo:
        self._info = await self.call_method(GetMyInfo())
        return self._info

    async def close(self) -> None:
        if self._owns_client and self._client is not None:
            client, self._client = self._client, None
            await client.close()
        await self._media.close()

    async def call_method(  # for unihttp bind_method
        self,
        method: BaseMethod[ResponseType],
        *,
        middleware: Sequence[AsyncMiddleware] | None = None,
    ) -> ResponseType:
        method = apply_defaults(method, self._defaults)
        # Middleware вызова идут первыми: так они получают ошибки maxo,
        # а не сырые исключения unihttp.
        result = await self.client.call_method(
            method,
            middleware=[*(middleware or ()), *self.middleware],
        )
        return bind_bot(result, self)

    async def call_method_stream(  # for unihttp bind_method
        self,
        method: StreamMethod,
        *,
        middleware: Sequence[AsyncMiddleware] | None = None,
    ) -> HTTPResponse[AsyncChunkStream]:
        return await self.client.call_method_stream(
            method,
            middleware=[*(middleware or ()), *self.middleware],
        )

    # Bots
    edit_bot_info = bind_method(EditBotInfo)
    edit_my_commands = bind_method(EditMyCommands)

    # Chats
    add_members = bind_method(AddMembers)
    delete_admins = bind_method(DeleteAdmins)
    delete_admin = delete_admins
    delete_chat = bind_method(DeleteChat)
    edit_chat = bind_method(EditChat)
    get_admins = bind_method(GetAdmins)
    get_chat = bind_method(GetChat)
    get_chat_by_link = bind_method(GetChatByLink)
    get_chats = bind_method(GetChats)
    get_members = bind_method(GetMembers)
    get_membership = bind_method(GetMembership)
    get_pinned_message = bind_method(GetPinnedMessage)
    leave_chat = bind_method(LeaveChat)
    pin_message = bind_method(PinMessage)
    remove_member = bind_method(RemoveMember)
    send_action = bind_method(SendAction)
    set_admins = bind_method(SetAdmins)
    unpin_message = bind_method(UnpinMessage)

    # Comments

    delete_comment = bind_method(DeleteComment)
    edit_comment = bind_method(EditComment)
    get_comment_by_id = bind_method(GetCommentById)
    get_comments = bind_method(GetComments)
    send_comment = bind_method(SendComment)

    # Messages
    answer_on_callback = bind_method(AnswerOnCallback)
    delete_message = bind_method(DeleteMessage)
    edit_message = bind_method(EditMessage)
    get_message_by_id = bind_method(GetMessageById)
    get_messages = bind_method(GetMessages)
    get_video_attachment_details = bind_method(GetVideoAttachmentDetails)
    send_message = bind_method(SendMessage)

    # Subscriptions
    get_subscriptions = bind_method(GetSubscriptions)
    get_updates = bind_method(GetUpdates)
    subscribe = bind_method(Subscribe)
    unsubscribe = bind_method(Unsubscribe)

    async def clear_subscriptions(
        self,
        active_urls: str | Iterable[str] | None = None,
    ) -> ClearSubscriptionsResult:
        """
        Удаляет все WebHook-подписки, кроме активных.

        Args:
            active_urls: URL подписок, которые нужно сохранить: одна строка или
                итерируемый набор строк. Одновременно может работать несколько
                подписок (бот, статистика и т.п.). Сравнение точное, поэтому
                URL должны совпадать с тем, что вернул `get_subscriptions`.
                Если не передан, удаляются все подписки.

        Returns:
            Удалённые и сохранённые подписки.

        Raises:
            BaseExceptionGroup: Если хотя бы одну подписку удалить не удалось.
                Все запросы при этом доводятся до конца, а в группу попадают
                ошибки по каждой неудачной попытке: обычные - обёрнутыми в
                `UnsubscribeError` с URL, `BaseException` - как есть. Если
                `BaseException` не было, группа сужается до `ExceptionGroup`.

        """
        if active_urls is None:
            urls_to_keep: frozenset[str] = frozenset()
        elif isinstance(active_urls, str):
            urls_to_keep = frozenset((active_urls,))
        else:
            urls_to_keep = frozenset(active_urls)

        subscriptions = (await self.get_subscriptions()).subscriptions
        to_remove = [
            subscription
            for subscription in subscriptions
            if subscription.url not in urls_to_keep
        ]
        kept = [
            subscription
            for subscription in subscriptions
            if subscription.url in urls_to_keep
        ]

        results = await asyncio.gather(
            *(self.unsubscribe(url=subscription.url) for subscription in to_remove),
            return_exceptions=True,
        )

        errors: list[BaseException] = []
        for subscription, result in zip(to_remove, results, strict=True):
            if not isinstance(result, BaseException):
                continue
            if not isinstance(result, Exception):
                errors.append(result)
                continue
            error = UnsubscribeError(url=subscription.url, error=result)
            error.__cause__ = result
            errors.append(error)

        if errors:
            raise BaseExceptionGroup("Не удалось удалить WebHook-подписки", errors)

        return ClearSubscriptionsResult(removed=to_remove, kept=kept)

    # Uploads
    get_upload_url = bind_method(GetUploadUrl)
