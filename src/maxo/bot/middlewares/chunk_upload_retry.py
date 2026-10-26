from typing import Any

from unihttp.exceptions import NonRetryableError
from unihttp.http import HTTPRequest, HTTPResponse
from unihttp.middlewares import AsyncHandler, AsyncMiddleware

from maxo.backoff import Backoff, BackoffConfig
from maxo.errors.api import MaxBotServerError
from maxo.errors.network import MaxBotNetworkError


class ChunkUploadRetryMiddleware(AsyncMiddleware):
    """
    Ретраит отправку чанка resumable upload: сетевые сбои и 5xx.

    Передаётся в `Bot.call_method(middleware=...)` и работает снаружи
    `NetworkErrorMiddleware`, поэтому видит уже переведённые ошибки maxo:
    `MaxBotNetworkError`/`MaxBotTimeoutError` и `MaxBotServerError` от
    `ChunkUpload.on_error`. 4xx и сетевые ошибки из `NonRetryableError`
    (битый URL, петля редиректов) не ретраятся.
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
