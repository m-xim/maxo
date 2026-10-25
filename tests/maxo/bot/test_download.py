from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, patch

from maxo.bot.bot import Bot
from maxo.bot.middlewares import AuthMiddleware
from maxo.types import AttachmentPayload


@asynccontextmanager
async def _stream(
    chunks: tuple[bytes, ...],
    closed: list[bool],
) -> AsyncIterator[AsyncIterator[bytes]]:
    async def iterator() -> AsyncIterator[bytes]:
        for chunk in chunks:
            yield chunk

    try:
        yield iterator()
    finally:
        closed.append(True)


def _patch_stream(
    bot: Bot,
    *chunks: bytes,
    closed: list[bool] | None = None,
) -> Any:
    """Подменяет клиент бота; в `closed` попадает факт закрытия потока."""
    response = SimpleNamespace(
        data=_stream(chunks, closed if closed is not None else []),
    )
    call = AsyncMock(return_value=response)
    return patch.object(bot, "_client", SimpleNamespace(call_method_stream=call))


async def test_download_returns_whole_payload(bot: Bot) -> None:
    with _patch_stream(bot, b"pay", b"load"):
        result = await bot.download("https://example.test/file.bin")

    assert result == b"payload"


async def test_download_to_path_writes_file(bot: Bot, tmp_path: Path) -> None:
    path = tmp_path / "payload.bin"

    with _patch_stream(bot, b"pay", b"load"):
        await bot.download_to("https://example.test/file.bin", path)

    assert path.read_bytes() == b"payload"


async def test_download_stream_yields_chunks_as_they_come(bot: Bot) -> None:
    """Стрим не склеивает чанки: на этом держится и прогресс, и запись
    в чужой буфер без буферизации файла целиком в память."""
    with _patch_stream(bot, b"pay", b"load"):
        async with bot.download_stream("https://e.test/f.bin") as stream:
            chunks = [chunk async for chunk in stream]

    assert chunks == [b"pay", b"load"]


async def test_download_unwraps_attachment_payload(bot: Bot) -> None:
    payload = AttachmentPayload(url="https://example.test/file.bin")

    with _patch_stream(bot, b"payload") as client:
        await bot.download(payload)

    call = client.call_method_stream
    assert call.await_args.args[0].url == "https://example.test/file.bin"


async def test_download_does_not_send_token(bot: Bot) -> None:
    with _patch_stream(bot, b"payload") as client:
        await bot.download("https://example.test/file.bin")

    middleware = client.call_method_stream.await_args.kwargs["middleware"]
    assert not any(isinstance(m, AuthMiddleware) for m in middleware)
    assert len(middleware) == len(bot.middleware) - 1


async def test_download_stream_closes_response_on_break(bot: Bot) -> None:
    """Соединение освобождается на `break` без участия вызывающего - ради
    этого `download_stream` и сделан контекстным менеджером."""
    closed: list[bool] = []

    with _patch_stream(bot, b"pay", b"load", closed=closed):
        async with bot.download_stream("https://e.test/f.bin") as chunks:
            async for _ in chunks:
                break

    assert closed == [True]
