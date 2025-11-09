from typing import Optional

from maxo.types import MaxoType


class LinkPreviewOptions(MaxoType):
    is_disabled: Optional[bool]
    url: Optional[str]
    prefer_small_media: Optional[bool]
    prefer_large_media: Optional[bool]
    show_above_text: Optional[bool]
