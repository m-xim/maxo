import asyncio
import io
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Sequence
from contextlib import aclosing, asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, TypeAlias
from urllib.parse import quote

from anyio import open_file
from unihttp.clients.base import BaseAsyncClient
from unihttp.http import UploadFile
from unihttp.http.response import HTTPResponse
from unihttp.http.stream import AsyncChunkStream
from unihttp.method import BaseMethod, ResponseType, StreamMethod
from unihttp.middlewares import AsyncMiddleware

from maxo.bot.client import default_media_client
from maxo.bot.methods.download import Download
from maxo.bot.methods.upload.chunk_upload import ChunkUpload, UploadResponseBody
from maxo.bot.methods.upload.upload_media import UploadMedia
from maxo.bot.middlewares import ChunkUploadRetryMiddleware, NetworkErrorMiddleware
from maxo.bot.middlewares.network_error import translate_network_errors
from maxo.enums import UploadType
from maxo.errors.api import RetvalReturnedError
from maxo.omit import is_defined
from maxo.serialization import get_retort
from maxo.types import AttachmentPayload
from maxo.types.attachments import AttachmentsRequests, MediaAttachmentsRequests
from maxo.types.audio_attachment_request import AudioAttachmentRequest
from maxo.types.buttons import InlineButtons
from maxo.types.file_attachment_request import FileAttachmentRequest
from maxo.types.inline_keyboard_attachment_request import (
    InlineKeyboardAttachmentRequest,
)
from maxo.types.inline_keyboard_attachment_request_payload import (
    InlineKeyboardAttachmentRequestPayload,
)
from maxo.types.media_input import MediaInput
from maxo.types.photo_attachment_request import PhotoAttachmentRequest
from maxo.types.upload_media_result import UploadMediaResult
from maxo.types.video_attachment_request import VideoAttachmentRequest
from maxo.utils.upload_media import FSInputFile, InputFile

if TYPE_CHECKING:
    from maxo.bot.bot import Bot

DEFAULT_DOWNLOAD_CHUNK_SIZE = 65536

MediaAttachmentFactory: TypeAlias = Callable[[str], MediaAttachmentsRequests]

MEDIA_ATTACHMENT_FACTORIES: dict[UploadType, MediaAttachmentFactory] = {
    UploadType.FILE: FileAttachmentRequest.factory,
    UploadType.AUDIO: AudioAttachmentRequest.factory,
    UploadType.VIDEO: VideoAttachmentRequest.factory,
    UploadType.IMAGE: lambda token: PhotoAttachmentRequest.factory(token=token),
}


class Media:
    """
    Client for MAX media hosts, available as `bot.media`.

    Own HTTP client and middleware, no token. A passed `client` is not closed.
    """

    def __init__(self, bot: "Bot", client: BaseAsyncClient | None = None) -> None:
        self._bot = bot
        self._client = client
        self._owns_client = client is None
        self.middleware: list[AsyncMiddleware] = [NetworkErrorMiddleware()]

    @property
    def client(self) -> BaseAsyncClient:
        if self._client is None:
            self._client = default_media_client()
        return self._client

    async def close(self) -> None:
        if self._owns_client and self._client is not None:
            client, self._client = self._client, None
            await client.close()

    async def call_method(
        self,
        method: BaseMethod[ResponseType],
        *,
        middleware: Sequence[AsyncMiddleware] | None = None,
    ) -> ResponseType:
        # Middleware вызова идут первыми: так они получают ошибки maxo,
        # а не сырые исключения unihttp.
        return await self.client.call_method(
            method,
            middleware=[*(middleware or ()), *self.middleware],
        )

    async def call_method_stream(
        self,
        method: StreamMethod,
        *,
        middleware: Sequence[AsyncMiddleware] | None = None,
    ) -> HTTPResponse[AsyncChunkStream]:
        return await self.client.call_method_stream(
            method,
            middleware=[*(middleware or ()), *self.middleware],
        )

    async def build_attachments(
        self,
        base: Sequence[AttachmentsRequests],
        keyboard: Sequence[Sequence[InlineButtons]] | None = None,
        files: Sequence[MediaInput] | None = None,
    ) -> Sequence[AttachmentsRequests]:
        """
        Собирает вложения сообщения: `base`, клавиатуру и медиа.

        Файлы из `files` загружаются, готовые вложения передаются как есть,
        порядок сохраняется.
        """
        attachments = list(base)

        if keyboard is not None:
            attachments.append(
                InlineKeyboardAttachmentRequest(
                    payload=InlineKeyboardAttachmentRequestPayload(
                        buttons=[list(row) for row in keyboard],
                    ),
                ),
            )

        if files:
            attachments.extend(await self._build_media(files))

        return attachments

    async def _build_media(
        self,
        files: Sequence[MediaInput],
    ) -> list[MediaAttachmentsRequests]:
        """Загружает файлы, готовые вложения оставляет на местах."""
        to_upload = [file for file in files if isinstance(file, InputFile)]

        # Размер каждого файла считаем один раз и прокидываем дальше
        sizes = await asyncio.gather(*(file.size() for file in to_upload))
        uploaded = iter(
            await asyncio.gather(
                *(
                    self.upload(f, size)
                    for f, size in zip(to_upload, sizes, strict=True)
                ),
            ),
        )

        # Let the server process files before sending
        config = self._bot.upload_config
        delay = max(
            (
                config.estimated_processing_delay(f.type, size)
                for f, size in zip(to_upload, sizes, strict=True)
            ),
            default=0.0,
        )
        if delay > 0:
            await asyncio.sleep(delay)

        return [next(uploaded) if isinstance(f, InputFile) else f for f in files]

    async def upload(
        self,
        file: InputFile,
        size: int | None = None,
    ) -> MediaAttachmentsRequests:
        """Загружает файл и возвращает вложение с его токеном."""
        if size is None:
            size = await file.size()
        if size <= 0:
            msg = "Нельзя загрузить пустой файл"
            raise ValueError(msg)

        endpoint = await self._bot.get_upload_url(type=file.type)

        upload_result = await self._upload_file(file, endpoint.url, size)

        token: str
        if is_defined(endpoint.token):
            token = endpoint.token
        elif upload_result is not None:
            token = upload_result.last_token
        else:
            raise RuntimeError("Could not get upload token")

        return MEDIA_ATTACHMENT_FACTORIES[file.type](token)

    async def _upload_file(
        self,
        file: InputFile,
        url: str,
        size: int,
    ) -> UploadMediaResult | None:
        if self._bot.upload_config.should_use_resumable(file.type, size):
            return await self._upload_resumable(url, file, size)

        if isinstance(file, FSInputFile):
            # Streamed, not read into memory
            content = await asyncio.to_thread(Path(file.path).open, "rb")
            with content:
                return await self._upload_single(url, file.file_name, content)
        return await self._upload_single(url, file.file_name, await file.read())

    async def _upload_single(
        self,
        url: str,
        file_name: str,
        content: bytes | BinaryIO,
    ) -> UploadMediaResult | None:
        try:
            return await self.call_method(
                UploadMedia(
                    upload_url=url,
                    file=UploadFile(file=content, filename=file_name),
                ),
            )
        except RetvalReturnedError:
            return None

    async def _upload_resumable(
        self,
        upload_url: str,
        file: InputFile,
        size: int | None = None,
    ) -> UploadMediaResult | None:
        """Загружает видео или аудио по `upload_url` частями."""
        config = self._bot.upload_config

        if size is None:
            size = await file.size()

        encoded_name = quote(file.file_name, safe="")
        disposition = f'attachment; filename="{encoded_name}"'

        offset = 0
        final_body: UploadResponseBody = b""
        retry = ChunkUploadRetryMiddleware(
            max_retries=config.chunk_retries,
            backoff_config=config.chunk_backoff,
        )
        # aclosing: при ошибке `async for` не закрывает генератор, а у
        # `FSInputFile.stream` внутри него остаётся открытый файл.
        async with aclosing(file.stream(config.chunk_size)) as chunks:
            async for chunk in chunks:
                end = offset + len(chunk) - 1
                final_body = await self.call_method(
                    ChunkUpload(
                        upload_url=upload_url,
                        content_range=f"bytes {offset}-{end}/{size}",
                        content_disposition=disposition,
                        chunk=chunk,
                    ),
                    middleware=[retry],
                )
                offset += len(chunk)

        if offset != size:
            # Файл изменился между замером размера и чтением
            msg = f"Размер файла изменился во время загрузки: {size} -> {offset} байт"
            raise ValueError(msg)

        if not isinstance(final_body, dict):
            return None
        return get_retort().load(final_body, UploadMediaResult)

    @asynccontextmanager
    async def download_stream(
        self,
        url: str | AttachmentPayload,
        chunk_size: int = DEFAULT_DOWNLOAD_CHUNK_SIZE,
    ) -> AsyncIterator[AsyncIterator[bytes]]:
        """
        Отдаёт вложение чанками.

        Соединение освобождается на выходе из `async with`, в том числе
        при прерванном цикле.
        """
        if isinstance(url, AttachmentPayload):
            url = url.url

        response = await self.call_method_stream(
            Download(url=url, __chunk_size__=chunk_size),
        )
        async with (
            response.data as stream,
            aclosing(_translate_chunks(stream)) as chunks,
        ):
            yield chunks

    async def download(
        self,
        url: str | AttachmentPayload,
        chunk_size: int = DEFAULT_DOWNLOAD_CHUNK_SIZE,
    ) -> bytes:
        """
        Скачивает вложение целиком в память.

        Для больших файлов: `download_to()` или `download_stream()`.
        """
        buffer = io.BytesIO()
        async with self.download_stream(url, chunk_size=chunk_size) as chunks:
            async for chunk in chunks:
                buffer.write(chunk)
        return buffer.getvalue()

    async def download_to(
        self,
        url: str | AttachmentPayload,
        path: Path | str,
        chunk_size: int = DEFAULT_DOWNLOAD_CHUNK_SIZE,
    ) -> None:
        """Скачивает вложение в файл. Каталог должен существовать."""
        async with (
            self.download_stream(url, chunk_size=chunk_size) as chunks,
            await open_file(path, "wb") as file,
        ):
            async for chunk in chunks:
                await file.write(chunk)


async def _translate_chunks(stream: AsyncIterator[bytes]) -> AsyncGenerator[bytes]:
    # Only reading: errors from the caller's `async with` body stay as is
    with translate_network_errors():
        async for chunk in stream:
            yield chunk
