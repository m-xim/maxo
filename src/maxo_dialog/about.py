import importlib.metadata

from maxo.fsm import State, StatesGroup
from maxo_dialog.dialog import Dialog
from maxo_dialog.widgets.kbd import Cancel, Keyboard, Start
from maxo_dialog.widgets.link_preview import LinkPreview
from maxo_dialog.widgets.text import Const, Jinja, Text
from maxo_dialog.window import Window


class MaxoDialogStates(StatesGroup):
    ABOUT = State()


async def metadata_getter(**_kwargs) -> dict:
    metadata = importlib.metadata.metadata("maxo-dialog")
    urls = [u.split(",", maxsplit=1) for u in metadata.get_all("Project-Url")]
    return {
        "metadata": metadata,
        "urls": urls,
    }


def about_dialog():
    return Dialog(
        Window(
            Jinja(
                "<b><u>{{metadata.Name}}</u></b> by @tishka17\n"
                "\n"
                "{{metadata.Summary}}\n"
                "\n"
                "<b>Version:</b> {{metadata.Version}}\n"
                "<b>Author:</b> {{metadata['Author-email']}}\n"
                "\n"
                "{% for name, url in urls%}"
                '<b>{{name}}:</b> <a href="{{url}}">{{url}}</a>\n'
                "{% endfor %}"
                "",
            ),
            LinkPreview(is_disabled=True),
            Cancel(Const("Ok")),
            getter=metadata_getter,
            preview_data=metadata_getter,
            state=MaxoDialogStates.ABOUT,
            parse_mode="html",
        ),
    )


DEFAULT_ABOUT_BTN_TEXT = Const("🗨️ About maxo-dialog")


def about_maxo_dialog_button(
    text: Text = DEFAULT_ABOUT_BTN_TEXT,
) -> Keyboard:
    return Start(
        text=text,
        state=MaxoDialogStates.ABOUT,
        id="__aiogd_about__",
    )
