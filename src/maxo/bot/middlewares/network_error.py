from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from unihttp.exceptions import NetworkError, RequestTimeoutError, UniHTTPError
from unihttp.http import HTTPRequest, HTTPResponse
from unihttp.middlewares import AsyncHandler, AsyncMiddleware

from maxo.errors.network import (
    MaxBotRequestError,
    MaxBotTimeoutError,
    to_network_error,
)


@contextmanager
def translate_network_errors() -> Iterator[None]:
    try:
        yield
    except RequestTimeoutError as error:
        raise MaxBotTimeoutError(str(error) or type(error).__name__) from error
    except (NetworkError, TimeoutError) as error:
        raise to_network_error(error) from error
    except UniHTTPError as error:
        # NonRetryableError and the rest: not a network failure, don't retry
        raise MaxBotRequestError(str(error) or type(error).__name__) from error


class NetworkErrorMiddleware(AsyncMiddleware):
    """Переводит транспортные ошибки unihttp в ошибки `maxo`."""

    async def handle(
        self,
        request: HTTPRequest,
        next_handler: AsyncHandler,
    ) -> HTTPResponse[Any]:
        with translate_network_errors():
            return await next_handler(request)
