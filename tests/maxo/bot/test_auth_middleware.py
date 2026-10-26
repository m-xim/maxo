from unittest.mock import AsyncMock

import pytest
from unihttp.http import HTTPRequest

from maxo.bot.middlewares import AuthMiddleware
from maxo.bot.middlewares.auth import USER_AGENT
from tests.constants import TOKEN


def _request(url: str) -> HTTPRequest:
    return HTTPRequest(
        url=url,
        method="GET",
        header={},
        path={},
        query={},
        body={},
        file={},
        form=None,
    )


async def _handle(url: str) -> HTTPRequest:
    request = _request(url)
    await AuthMiddleware(TOKEN).handle(request, AsyncMock())
    return request


@pytest.mark.parametrize("url", ["messages", "/me", "chats/1/members"])
async def test_token_goes_to_api_paths(url: str) -> None:
    request = await _handle(url)

    assert request.header["Authorization"] == TOKEN
    assert request.header["User-Agent"] == USER_AGENT


@pytest.mark.parametrize(
    "url",
    [
        "https://fu.oneme.ru/api/upload.do?sig=1",
        "http://evil.test/file.bin",
        "//evil.test/file.bin",  # urljoin resolves it to another host too
    ],
)
async def test_token_never_goes_to_other_hosts(url: str) -> None:
    """An absolute URL bypasses `base_url` to another host: no token goes there,
    even if the request went through the API client by mistake."""
    request = await _handle(url)

    assert "Authorization" not in request.header
    assert request.header["User-Agent"] == USER_AGENT


async def test_explicit_header_is_kept() -> None:
    request = _request("messages")
    request.header["Authorization"] = "other"

    await AuthMiddleware(TOKEN).handle(request, AsyncMock())

    assert request.header["Authorization"] == "other"
