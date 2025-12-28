from typing import Any

from maxo.types.base import MaxoType


class PhotoTokens(MaxoType):
    """Это информация, которую вы получите, как только изображение будет загружено"""

    photos: dict[str, Any]
