import pytest

from maxo.errors import (
    MaxBotApiError,
    MaxBotBadGatewayError,
    MaxBotBadRequestError,
    MaxBotClientError,
    MaxBotForbiddenError,
    MaxBotMethodNotAllowedError,
    MaxBotNotFoundError,
    MaxBotServerError,
    MaxBotServiceUnavailableError,
    MaxBotTooManyRequestsError,
    MaxBotUnauthorizedError,
    MaxBotUnknownServerError,
    MaxBotUnsupportedMediaTypeError,
)
from maxo.errors.api import raise_api_error


@pytest.mark.parametrize(
    ("status_code", "error_class"),
    [
        (400, MaxBotBadRequestError),
        (401, MaxBotUnauthorizedError),
        (403, MaxBotForbiddenError),
        (404, MaxBotNotFoundError),
        (405, MaxBotMethodNotAllowedError),
        (415, MaxBotUnsupportedMediaTypeError),
        (429, MaxBotTooManyRequestsError),
        (500, MaxBotUnknownServerError),
        (502, MaxBotBadGatewayError),
        (503, MaxBotServiceUnavailableError),
        (418, MaxBotClientError),
        (501, MaxBotServerError),
        (302, MaxBotApiError),
    ],
)
def test_raise_api_error_falls_back_to_status_group(
    status_code: int,
    error_class: type[MaxBotApiError],
) -> None:
    with pytest.raises(error_class):
        raise_api_error(status_code, {})


def test_api_error_str_uses_fields_and_raw_data() -> None:
    error = MaxBotApiError("code", "error", "message")
    raw_error = MaxBotApiError("", "", "", {"raw": "data"})

    assert str(error) == (
        "MaxBotApiError(code='code', error='error', message='message')"
    )
    assert str(raw_error) == "MaxBotApiError(raw_data={'raw': 'data'})"


@pytest.mark.parametrize(
    ("data", "message"),
    [(b"<html>Bad Gateway</html>", "<html>Bad Gateway</html>"), (None, "")],
)
def test_raise_api_error_without_json_body_keeps_status_and_text(
    data: object,
    message: str,
) -> None:
    with pytest.raises(MaxBotBadGatewayError) as exc_info:
        raise_api_error(502, data)

    assert exc_info.value.error == "HTTP 502"
    assert exc_info.value.message == message
