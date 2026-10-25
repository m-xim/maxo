import pytest
from adaptix.load_error import LoadError

from maxo.bot.defaults import BotDefaults, apply_defaults
from maxo.bot.methods import (
    AnswerOnCallback,
    EditMessage,
    GetMembers,
    GetMessages,
    GetUpdates,
    SendMessage,
)
from maxo.enums import ChatAdminPermission, TextFormat
from maxo.errors import AttributeIsEmptyError
from maxo.omit import Omittable, Omitted, is_omitted
from maxo.serialization import get_retort
from maxo.types import (
    BotAdminPermissionsChanged,
    BotStarted,
    CommentCreated,
    CommentEdited,
    CommentMessage,
    CommentRemoved,
    Message,
    MessageCreated,
    NewMessageBody,
    OpenAppButton,
    UpdateList,
    UploadMediaResult,
    User,
    VideoAttachmentDetails,
    VideoThumbnail,
)
from maxo.types.base import FacadeMaxoType
from maxo.types.binding import bind_bot
from tests.factories import make_bot


class Sub(FacadeMaxoType):
    b: int


class MyType(FacadeMaxoType):
    a: str
    sub: Sub


@pytest.mark.parametrize(
    "default",
    [TextFormat.HTML, TextFormat.MARKDOWN, None, Omitted()],
)
def test_bot_default_text_format(default: Omittable[TextFormat | None]) -> None:
    defaults = BotDefaults(text_format=default)
    retort = get_retort()

    data = retort.dump(apply_defaults(SendMessage(), defaults))
    if is_omitted(default):
        assert "format" not in data["body"]
    else:
        assert data["body"]["format"] == default

    data = retort.dump(apply_defaults(EditMessage(message_id="1"), defaults))
    if is_omitted(default):
        assert "format" not in data["body"]
    else:
        assert data["body"]["format"] == default

    # `NewMessageBody` сверху не дампится - только внутри `AnswerOnCallback`,
    # где `apply_defaults` спускается в него отдельно.
    data = retort.dump(
        apply_defaults(
            AnswerOnCallback(callback_id="c", message=NewMessageBody()),
            defaults,
        ),
    )
    if is_omitted(default):
        assert "format" not in data["body"]["message"]
    else:
        assert data["body"]["message"]["format"] == default


@pytest.mark.parametrize(
    "default",
    [True, False, Omitted()],
)
def test_bot_default_disable_link_preview(default: Omittable[bool]) -> None:
    defaults = BotDefaults(disable_link_preview=default)
    retort = get_retort()

    data = retort.dump(apply_defaults(SendMessage(), defaults))
    if is_omitted(default):
        assert "disable_link_preview" not in data["query"]
    else:
        assert data["query"]["disable_link_preview"] == default


@pytest.mark.parametrize(
    "method",
    [
        GetUpdates(marker=None),
        GetUpdates(types=None),
        GetMessages(message_ids=None),
        GetMembers(chat_id=1, user_ids=None),
    ],
)
def test_query_none_is_omitted(method: object) -> None:
    retort = get_retort()

    data = retort.dump(method)

    assert not data.get("query")


def test_bind_binds_whole_tree() -> None:
    bot = make_bot(token="")
    retort = get_retort()

    data = {"a": "a", "sub": {"b": 1}}
    my = bind_bot(retort.load(data, MyType), bot)

    assert bot is my.bot is my.sub.bot

    dump = retort.dump(my, MyType)
    assert dump == data


def test_retort_without_bot_no_load_bot() -> None:
    retort = get_retort()

    data = {"a": "a", "sub": {"b": 1}}

    my = retort.load(data, MyType)

    with pytest.raises(AttributeIsEmptyError):
        _ = my.bot

    with pytest.raises(AttributeIsEmptyError):
        _ = my.sub.bot

    dump = retort.dump(my, MyType)
    assert dump == data


def test_retort_empty_message() -> None:
    retort = get_retort()

    data = {
        "marker": 1,
        "updates": [
            {
                "update_type": "message_created",
                "timestamp": 1234567890,
                "user_locale": "ru",
            },
        ],
    }

    with pytest.raises(LoadError):
        _ = retort.load(data, UpdateList)


def test_retort_full_message_created_loads_ok() -> None:
    retort = get_retort()

    # Полный валидный message_created - убеждаемся, что регрессия не сломала happy path
    data = {
        "marker": 1,
        "updates": [
            {
                "update_type": "message_created",
                "timestamp": 1234567890,
                "user_locale": "ru",
                "message": {
                    "body": {"seq": 1, "mid": "msg-1", "text": "hello"},
                    "recipient": {"chat_id": 1, "chat_type": "dialog"},
                    "timestamp": 1234567890,
                },
            },
        ],
    }

    result = retort.load(data, UpdateList)
    assert len(result.updates) == 1


def test_retort_keeps_message_created_with_post_id_as_message() -> None:
    retort = get_retort()
    data = {
        "marker": 1,
        "updates": [
            {
                "update_type": "message_created",
                "timestamp": 1234567890,
                "message": {
                    "body": {"seq": 1, "mid": "comment", "text": "hello"},
                    "recipient": {
                        "chat_id": 1,
                        "chat_type": "channel",
                        "post_id": "post",
                    },
                    "timestamp": 1234567890,
                },
            },
            {
                "update_type": "message_created",
                "timestamp": 1234567890,
                "message": {
                    "body": {"seq": 2, "mid": "message", "text": "hello"},
                    "recipient": {
                        "chat_id": 1,
                        "chat_type": "channel",
                    },
                    "timestamp": 1234567890,
                },
            },
        ],
    }

    result = retort.load(data, UpdateList)
    comment_update, message_update = result.updates

    assert isinstance(comment_update, MessageCreated)
    assert isinstance(message_update, MessageCreated)
    assert type(comment_update.message) is Message
    assert type(message_update.message) is Message


def test_retort_loads_comment_updates_from_raw_json() -> None:
    retort = get_retort()
    comment = {
        "body": {"seq": 1, "mid": "comment", "text": "hello"},
        "recipient": {
            "chat_id": 1,
            "chat_type": "channel",
            "post_id": "post",
        },
        "timestamp": 1234567890,
    }
    data = {
        "marker": 1,
        "updates": [
            {
                "update_type": "comment_created",
                "timestamp": 1234567890,
                "message": comment,
            },
            {
                "update_type": "comment_edited",
                "timestamp": 1234567890,
                "message": comment,
            },
            {
                "update_type": "comment_removed",
                "timestamp": 1234567890,
                "chat_id": 1,
                "message_id": "comment",
                "post_id": "post",
                "user_id": 2,
            },
        ],
    }

    result = retort.load(data, UpdateList)

    assert isinstance(result.updates[0], CommentCreated)
    assert isinstance(result.updates[0].message, CommentMessage)
    assert isinstance(result.updates[1], CommentEdited)
    assert isinstance(result.updates[1].message, CommentMessage)
    assert isinstance(result.updates[2], CommentRemoved)


def test_retort_loads_bot_admin_permissions_changed() -> None:
    retort = get_retort()
    data = {
        "marker": 1,
        "updates": [
            {
                "update_type": "bot_admin_permissions_changed",
                "timestamp": 1234567890,
                "chat_id": 1,
                "user_id": 2,
                "bot_id": 3,
                "is_channel": True,
                "is_admin": True,
                "permissions": ["add_admins", "can_call"],
            },
        ],
    }

    update = retort.load(data, UpdateList).updates[0]

    assert isinstance(update, BotAdminPermissionsChanged)
    assert update.chat_id == 1
    assert update.user_id == 2
    assert update.bot_id == 3
    assert update.permissions == [
        ChatAdminPermission.ADD_ADMINS,
        ChatAdminPermission.CAN_CALL,
    ]
    assert retort.dump(update)["update_type"] == "bot_admin_permissions_changed"


def test_retort_loads_video_details_with_url_only_thumbnail() -> None:
    retort = get_retort()

    details = retort.load(
        {
            "token": "video-token",
            "width": 320,
            "height": 240,
            "duration": 7000,
            "urls": {"mp4_240": "https://example.com/video.mp4"},
            "thumbnail": {"url": "https://example.com/thumb.jpg"},
        },
        VideoAttachmentDetails,
    )

    assert details.thumbnail == VideoThumbnail(url="https://example.com/thumb.jpg")


def test_retort_loads_user_with_null_last_activity_time() -> None:
    retort = get_retort()

    user = retort.load(
        {
            "user_id": 1,
            "first_name": "Ivan",
            "is_bot": False,
            "last_activity_time": None,
        },
        User,
    )

    assert user.last_activity_time is None
    with pytest.raises(AttributeIsEmptyError):
        _ = user.unsafe_last_activity_time


def test_retort_keeps_avatar_of_user_in_update() -> None:
    retort = get_retort()

    update = retort.load(
        {
            "update_type": "bot_started",
            "timestamp": 1,
            "chat_id": 10,
            "user": {
                "user_id": 1,
                "first_name": "Ivan",
                "is_bot": False,
                "avatar_url": "https://i.oneme.ru/small",
                "full_avatar_url": "https://i.oneme.ru/full",
            },
        },
        BotStarted,
    )

    assert update.user.unsafe_avatar_url == "https://i.oneme.ru/small"
    assert update.user.unsafe_full_avatar_url == "https://i.oneme.ru/full"


def test_retort_loads_file_id_of_upload_result() -> None:
    retort = get_retort()

    result = retort.load({"fileId": 3343344796, "token": "tok"}, UploadMediaResult)

    assert result.file_id == 3343344796


def test_retort_loads_open_app_button_without_web_app() -> None:
    retort = get_retort()

    message = retort.load(
        {
            "body": {
                "seq": 1,
                "mid": "msg-1",
                "text": "app",
                "attachments": [
                    {
                        "type": "inline_keyboard",
                        "payload": {
                            "buttons": [
                                [{"type": "open_app", "text": "App", "contact_id": 5}],
                            ],
                        },
                    },
                ],
            },
            "recipient": {"chat_id": 1, "chat_type": "dialog"},
            "timestamp": 1234567890,
        },
        Message,
    )

    keyboard = message.body.keyboard
    assert keyboard is not None
    button = keyboard.buttons[0][0]
    assert isinstance(button, OpenAppButton)
    assert button.contact_id == 5
    assert is_omitted(button.web_app)
