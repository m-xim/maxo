from unittest.mock import AsyncMock

import pytest

from maxo import Bot
from maxo.utils.upload_media import BufferedInputFile


async def test_aenter_closes_client_when_me_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncMock()
    bot = Bot("token", client=client)
    bot._owns_client = True

    async def boom() -> None:
        raise RuntimeError("bad token")

    monkeypatch.setattr(bot, "me", boom)
    with pytest.raises(RuntimeError):
        await bot.__aenter__()

    client.close.assert_awaited_once()


async def test_empty_file_rejected_before_get_upload_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bot = Bot("token")

    async def fail(**_: object) -> None:
        raise AssertionError("get_upload_url must not be called")

    monkeypatch.setattr(bot, "get_upload_url", fail)
    with pytest.raises(ValueError, match="пустой"):
        await bot.upload(BufferedInputFile.image(b"", "empty.png"))
    await bot.close()
