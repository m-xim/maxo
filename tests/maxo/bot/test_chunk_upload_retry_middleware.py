"""Retries of a resumable-upload chunk; ported from upstream `test_upload.py`."""

from collections.abc import Sequence
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from maxo.backoff import BackoffConfig
from maxo.bot.middlewares import ChunkUploadRetryMiddleware
from maxo.bot.upload import UploadConfig
from maxo.errors import MaxBotApiError, MaxBotNetworkError, MaxBotTimeoutError

_BACKOFF = UploadConfig().chunk_backoff


def _response(status_code: int) -> MagicMock:
    return MagicMock(status_code=status_code)


async def _handle(
    outcomes: Sequence[object],
    retries: int,
    backoff: BackoffConfig = _BACKOFF,
) -> tuple[object, AsyncMock, AsyncMock]:
    middleware = ChunkUploadRetryMiddleware(max_retries=retries, backoff_config=backoff)
    next_handler = AsyncMock(side_effect=outcomes)
    with patch("asyncio.sleep", new_callable=AsyncMock) as sleep:
        result = await middleware.handle(MagicMock(), next_handler)
    return result, next_handler, sleep


async def test_server_error_is_retried_then_succeeds() -> None:
    ok = _response(200)

    result, next_handler, _ = await _handle([_response(500), ok], retries=3)

    assert result is ok
    assert next_handler.await_count == 2


async def test_server_error_is_returned_after_retries() -> None:
    # The caller turns the last 5xx into `MaxBotApiError`
    last = _response(500)

    result, next_handler, _ = await _handle([_response(500), last], retries=1)

    assert result is last
    assert next_handler.await_count == 2


async def test_client_error_is_not_retried() -> None:
    bad = _response(400)

    result, next_handler, _ = await _handle([bad], retries=3)

    assert result is bad
    assert next_handler.await_count == 1


async def test_timeout_is_retried_then_succeeds() -> None:
    ok = _response(200)

    result, next_handler, _ = await _handle(
        [MaxBotTimeoutError("timed out"), ok],
        retries=3,
    )

    assert result is ok
    assert next_handler.await_count == 2


async def test_network_error_is_reraised_after_retries() -> None:
    errors = [MaxBotNetworkError("boom") for _ in range(3)]

    with pytest.raises(MaxBotNetworkError, match="boom"):
        await _handle(errors, retries=2)


async def test_api_error_is_not_retried() -> None:
    middleware = ChunkUploadRetryMiddleware(max_retries=3, backoff_config=_BACKOFF)
    error = MaxBotApiError(code="", error="x", message="x")
    next_handler = AsyncMock(side_effect=error)

    with pytest.raises(MaxBotApiError):
        await middleware.handle(MagicMock(), next_handler)

    assert next_handler.await_count == 1


async def test_first_retry_waits_backoff_min_delay() -> None:
    _, _, sleep = await _handle([_response(500), _response(200)], retries=3)

    # The first pause is exactly `min_delay`, not doubled
    assert sleep.await_args_list[0].args[0] == _BACKOFF.min_delay
