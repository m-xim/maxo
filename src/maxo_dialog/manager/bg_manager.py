from datetime import datetime
from logging import getLogger
from typing import Any, Optional, Union

from maxo import Bot
from maxo.enums import ChatStatusType
from maxo.fsm import State
from maxo.routing.interfaces import Router
from maxo.types import Chat, User
from maxo_dialog.api.entities import (
    DEFAULT_STACK_ID,
    AccessSettings,
    Data,
    DialogAction,
    DialogStartEvent,
    DialogSwitchEvent,
    DialogUpdate,
    DialogUpdateEvent,
    EventContext,
    ShowMode,
    StartMode,
)
from maxo_dialog.api.internal import (
    FakeChat,
    FakeUser,
)
from maxo_dialog.api.protocols import (
    BaseDialogManager,
    BgManagerFactory,
    UnsetId,
)
from maxo_dialog.manager.updater import Updater
from maxo_dialog.utils import is_chat_loaded, is_user_loaded

logger = getLogger(__name__)


class BgManager(BaseDialogManager):
    def __init__(
        self,
        user: User,
        chat: Chat,
        bot: Bot,
        router: Router,
        intent_id: Optional[str],
        stack_id: Optional[str],
        load: bool = False,
    ):
        self._event_context = EventContext(
            chat=chat,
            user=user,
            bot=bot,
        )
        self._router = router
        self._updater = Updater(router)
        self.intent_id = intent_id
        self.stack_id = stack_id
        self.load = load

    def _get_fake_user(self, user_id: Optional[int] = None) -> User:
        """Get User if we have info about him or FakeUser instead."""
        if user_id is None or user_id == self._event_context.user.id:
            return self._event_context.user
        return FakeUser(
            user_id=user_id,
            is_bot=False,
            first_name="",
            last_activity_time=datetime.now(),
        )

    def _get_fake_chat(self, chat_id: Optional[int] = None) -> Chat:
        """Get Chat if we have info about him or FakeChat instead."""
        if chat_id is None or chat_id == self._event_context.chat.id:
            return self._event_context.chat
        return FakeChat(
            chat_id=chat_id,
            type="",
            is_public=False,
            last_event_time=datetime.now(),
            participants_count=1,
            status=ChatStatusType.ACTIVE,
        )

    def bg(
        self,
        user_id: Optional[int] = None,
        chat_id: Optional[int] = None,
        stack_id: Optional[str] = None,
        thread_id: Union[int, None, UnsetId] = UnsetId.UNSET,
        business_connection_id: Union[str, None, UnsetId] = UnsetId.UNSET,
        load: bool = False,
    ) -> "BaseDialogManager":
        chat = self._get_fake_chat(chat_id)
        user = self._get_fake_user(user_id)

        new_event_context = EventContext(
            bot=self._event_context.bot,
            chat=chat,
            user=user,
        )
        if stack_id is None:
            if self._event_context == new_event_context:
                stack_id = self.stack_id
                intent_id = self.intent_id
            else:
                stack_id = DEFAULT_STACK_ID
                intent_id = None
        else:
            intent_id = None

        return BgManager(
            user=new_event_context.user,
            chat=new_event_context.chat,
            bot=new_event_context.bot,
            router=self._router,
            intent_id=intent_id,
            stack_id=stack_id,
            load=load,
        )

    def _base_event_params(self) -> dict[str, Any]:
        return {
            "from_user": self._event_context.user,
            "chat": self._event_context.chat,
            "intent_id": self.intent_id,
            "stack_id": self.stack_id,
        }

    async def _notify(self, event: DialogUpdateEvent) -> None:
        bot = self._event_context.bot
        event.bot = bot  # TODO: ???
        update = DialogUpdate(aiogd_update=event)
        await self._updater.notify(bot=bot, update=update)

    async def _load(self) -> None:
        if self.load:
            bot = self._event_context.bot
            if not is_chat_loaded(self._event_context.chat):
                logger.debug(
                    "load chat: %s",
                    self._event_context.chat.id,
                )
                self._event_context.chat = await bot.get_chat(
                    chat_id=self._event_context.chat.id,
                )
            if not is_user_loaded(self._event_context.user):
                logger.debug(
                    "load user %s from chat %s",
                    self._event_context.chat.id,
                    self._event_context.user.id,
                )
                chat_member = await bot.get_chat_member(
                    self._event_context.chat.id,
                    self._event_context.user.id,
                )
                self._event_context.user = chat_member

    async def done(
        self,
        result: Any = None,
        show_mode: Optional[ShowMode] = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogUpdateEvent(
                action=DialogAction.DONE,
                data=result,
                show_mode=show_mode,
                **self._base_event_params(),
            ),
        )

    async def start(
        self,
        state: State,
        data: Data = None,
        mode: StartMode = StartMode.NORMAL,
        show_mode: Optional[ShowMode] = None,
        access_settings: Optional[AccessSettings] = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogStartEvent(
                action=DialogAction.START,
                data=data,
                new_state=state,
                mode=mode,
                show_mode=show_mode,
                access_settings=access_settings,
                **self._base_event_params(),
            ),
        )

    async def switch_to(
        self,
        state: State,
        show_mode: Optional[ShowMode] = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogSwitchEvent(
                action=DialogAction.SWITCH,
                data={},
                new_state=state,
                show_mode=show_mode,
                **self._base_event_params(),
            ),
        )

    async def update(
        self,
        data: dict,
        show_mode: Optional[ShowMode] = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogUpdateEvent(
                action=DialogAction.UPDATE,
                data=data,
                show_mode=show_mode,
                **self._base_event_params(),
            ),
        )


class BgManagerFactoryImpl(BgManagerFactory):
    def __init__(self, router: Router):
        self._router = router

    def bg(
        self,
        bot: Bot,
        user_id: int,
        chat_id: int,
        stack_id: Optional[str] = None,
        thread_id: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        load: bool = False,
    ) -> "BaseDialogManager":
        chat = FakeChat(
            chat_id=chat_id,
            type="",
            is_public=False,
            last_event_time=datetime.now(),
            participants_count=1,
            status=ChatStatusType.ACTIVE,
        )
        user = FakeUser(
            user_id=user_id,
            is_bot=False,
            first_name="",
            last_activity_time=datetime.now(),
        )
        if stack_id is None:
            stack_id = DEFAULT_STACK_ID

        return BgManager(
            user=user,
            chat=chat,
            bot=bot,
            router=self._router,
            intent_id=None,
            stack_id=stack_id,
            load=load,
        )
