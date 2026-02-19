from maxo.types import MaxoType


# TODO: Убрать лишнее, заменить None на Omitted при необходимости
class LinkPreviewOptions(MaxoType):
    is_disabled: bool | None
    url: str | None
    prefer_small_media: bool | None
    prefer_large_media: bool | None
    show_above_text: bool | None
