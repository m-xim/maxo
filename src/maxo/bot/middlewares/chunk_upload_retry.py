from typing import Any

from unihttp.exceptions import NonRetryableError
from unihttp.http import HTTPRequest, HTTPResponse
from unihttp.middlewares import AsyncHandler, AsyncMiddleware

from maxo.backoff import Backoff, BackoffConfig
from maxo.errors.api import MaxBotServerError
from maxo.errors.network import MaxBotNetworkError


class ChunkUploadRetryMiddleware(AsyncMiddleware):
    """
    Ретраит чанк resumable upload при сетевых сбоях и 5xx.

    Работает снаружи `NetworkErrorMiddleware` и видит ошибки maxo.
    4xx и `NonRetryableError` не ретраятся.
    """

    __slots__ = ("_backoff_config", "_max_retries")

    def __init__(self, max_retries: int, backoff_config: BackoffConfig) -> None:
        self._max_retries = max_retries
        self._backoff_config = backoff_config

    async def handle(
        self,
        request: HTTPRequest,
        next_handler: AsyncHandler,
    ) -> HTTPResponse[Any]:
        backoff = Backoff(self._backoff_config)
        while True:
            try:
                return await next_handler(request)
            except (MaxBotNetworkError, MaxBotServerError) as error:
                # A bad URL or a redirect loop won't heal on retry
                if (
                    isinstance(error.__cause__, NonRetryableError)
                    or backoff.counter >= self._max_retries
                ):
                    raise

            backoff.next()
            await backoff.sleep()
