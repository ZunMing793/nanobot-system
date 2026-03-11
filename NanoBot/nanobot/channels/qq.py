"""QQ channel implementation using botpy SDK."""

from __future__ import annotations

import asyncio
import mimetypes
import shutil
import uuid
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import httpx
from loguru import logger

from nanobot.bus.events import OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.channels.base import BaseChannel
from nanobot.config.schema import QQConfig
from nanobot.providers.transcription import GroqTranscriptionProvider

try:
    import botpy
    from botpy.message import C2CMessage

    QQ_AVAILABLE = True
except ImportError:
    QQ_AVAILABLE = False
    botpy = None
    C2CMessage = None

if TYPE_CHECKING:
    from botpy.message import C2CMessage


_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
_AUDIO_EXTS = {".silk", ".amr", ".ogg", ".opus", ".mp3", ".wav", ".m4a", ".aac"}
_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
_MEDIA_TTL = timedelta(hours=24)


def _make_bot_class(channel: "QQChannel") -> "type[botpy.Client]":
    """Create a botpy Client subclass bound to the given channel."""
    intents = botpy.Intents(public_messages=True, direct_message=True)
    if hasattr(intents, "_intents"):
        intents._intents |= 1 << 25
    elif hasattr(intents, "value"):
        intents.value |= 1 << 25
    else:
        try:
            intents.intents = (intents.intents or 0) | (1 << 25)
        except Exception:
            pass

    class _Bot(botpy.Client):
        def __init__(self):
            super().__init__(intents=intents, ext_handlers=False)

        async def on_ready(self):
            logger.info("QQ bot ready: {}", self.robot.name)

        async def on_c2c_message_create(self, message: "C2CMessage"):
            logger.info("QQ C2C message received: {}", message.content[:50] if message.content else "empty")
            await channel._on_message(message)

        async def on_direct_message_create(self, message):
            logger.info("QQ direct message received: {}", message.content[:50] if message.content else "empty")
            await channel._on_message(message)

    return _Bot


class QQChannel(BaseChannel):
    """QQ channel using botpy SDK with WebSocket connection."""

    name = "qq"

    def __init__(self, config: QQConfig, bus: MessageBus):
        super().__init__(config, bus)
        self.config: QQConfig = config
        self._client: "botpy.Client | None" = None
        self._processed_ids: deque = deque(maxlen=1000)
        self._msg_seq: int = 1
        self._http: httpx.AsyncClient | None = None
        self._media_dir = Path.home() / ".nanobot" / "media" / "qq"
        self._outbound_media_dir = Path.home() / ".nanobot" / "media" / "qq-outbound"

    async def start(self) -> None:
        """Start the QQ bot."""
        if not QQ_AVAILABLE:
            logger.error("QQ SDK not installed. Run: pip install qq-botpy")
            return

        if not self.config.app_id or not self.config.secret:
            logger.error("QQ app_id and secret not configured")
            return

        self._running = True
        self._http = httpx.AsyncClient(timeout=60.0, follow_redirects=True)
        BotClass = _make_bot_class(self)
        self._client = BotClass()

        logger.info("QQ bot started (C2C private message)")
        await self._run_bot()

    async def _run_bot(self) -> None:
        """Run the bot connection with auto-reconnect."""
        while self._running:
            try:
                await self._client.start(appid=self.config.app_id, secret=self.config.secret)
            except Exception as e:
                logger.warning("QQ bot error: {}", e)
            if self._running:
                logger.info("Reconnecting QQ bot in 5 seconds...")
                await asyncio.sleep(5)

    async def stop(self) -> None:
        """Stop the QQ bot."""
        self._running = False
        if self._client:
            try:
                await self._client.close()
            except Exception:
                pass
        if self._http:
            try:
                await self._http.aclose()
            except Exception:
                pass
            self._http = None
        logger.info("QQ bot stopped")

    @staticmethod
    def _is_http_url(value: str) -> bool:
        return value.startswith("http://") or value.startswith("https://")

    @staticmethod
    def _normalize_url(url: str | None) -> str | None:
        raw = (url or "").strip()
        if not raw:
            return None
        if raw.startswith("//"):
            return f"https:{raw}"
        if raw.startswith("http://") or raw.startswith("https://"):
            return raw
        return f"https://{raw.lstrip('/')}"

    @staticmethod
    def _safe_filename(name: str | None, fallback: str) -> str:
        candidate = (name or "").strip()
        if not candidate:
            candidate = fallback
        cleaned = candidate.replace("\\", "_").replace("/", "_")
        return cleaned or fallback

    @staticmethod
    def _guess_media_kind(filename: str | None = None, content_type: str | None = None) -> str:
        mime = (content_type or "").lower()
        ext = Path(filename or "").suffix.lower()
        if mime.startswith("image/") or ext in _IMAGE_EXTS:
            return "image"
        if mime.startswith("audio/") or ext in _AUDIO_EXTS:
            return "audio"
        if mime.startswith("video/") or ext in _VIDEO_EXTS:
            return "video"
        return "file"

    @staticmethod
    def _qq_file_type(kind: str) -> int:
        return {"image": 1, "video": 2, "audio": 3}.get(kind, 4)

    @staticmethod
    def _cleanup_directory(directory: Path, max_age: timedelta = _MEDIA_TTL) -> None:
        """Delete staged media files older than max_age."""
        if not directory.exists():
            return
        cutoff = datetime.now().timestamp() - max_age.total_seconds()
        for item in directory.iterdir():
            try:
                if item.is_file() and item.stat().st_mtime < cutoff:
                    item.unlink(missing_ok=True)
            except OSError:
                continue

    async def _download_attachment(self, attachment: Any) -> tuple[str | None, str | None, dict[str, Any] | None]:
        """Download one inbound QQ attachment and build a content marker."""
        if not self._http:
            return None, None, None

        url = self._normalize_url(getattr(attachment, "url", None))
        filename = self._safe_filename(
            getattr(attachment, "filename", None),
            f"attachment_{getattr(attachment, 'id', uuid.uuid4().hex)}",
        )
        content_type = getattr(attachment, "content_type", None)
        kind = self._guess_media_kind(filename, content_type)
        if not url:
            return None, f"[{kind}: missing url for {filename}]", None

        self._media_dir.mkdir(parents=True, exist_ok=True)
        self._cleanup_directory(self._media_dir)
        file_id = getattr(attachment, "id", None) or uuid.uuid4().hex
        target = self._media_dir / f"{str(file_id)[:16]}_{filename}"

        try:
            response = await self._http.get(url)
            response.raise_for_status()
            target.write_bytes(response.content)
        except Exception as e:
            logger.warning("Failed to download QQ attachment {}: {}", filename, e)
            return None, f"[{kind}: {filename} - download failed]", None

        marker = f"[{kind if kind != 'file' else 'file'}: {target}]"
        if kind == "audio" and self.config.groq_api_key:
            transcription = await GroqTranscriptionProvider(self.config.groq_api_key).transcribe(target)
            if transcription:
                marker = f"{marker}\n[transcription: {transcription}]"

        metadata = {
            "type": kind,
            "filename": filename,
            "path": str(target),
            "url": url,
            "content_type": content_type,
            "size": getattr(attachment, "size", None),
        }
        return str(target), marker, metadata

    def _resolve_public_media_url(self, media_ref: str) -> str | None:
        """Resolve a media reference to a publicly reachable URL for QQ C2C sending."""
        raw = (media_ref or "").strip()
        if not raw:
            return None
        if self._is_http_url(raw):
            return raw

        local_path = Path(raw)
        if not local_path.is_file():
            return None

        base = (self.config.public_media_base_url or "").strip().rstrip("/")
        if not base:
            return None

        self._outbound_media_dir.mkdir(parents=True, exist_ok=True)
        self._cleanup_directory(self._outbound_media_dir)
        staged = self._outbound_media_dir / f"{uuid.uuid4().hex}{local_path.suffix.lower()}"
        shutil.copy2(local_path, staged)
        return f"{base}/{staged.name}"

    async def _send_media_ref(self, chat_id: str, media_ref: str, reply_to: str | None = None) -> tuple[bool, str | None]:
        """Send one media reference through QQ C2C if possible."""
        if not self._client:
            return False, "QQ client not initialized"

        raw = (media_ref or "").strip()
        if not raw:
            return False, None

        parsed = urlparse(raw)
        filename = Path(parsed.path or raw).name or "attachment"
        kind = self._guess_media_kind(filename, mimetypes.guess_type(filename)[0])
        public_url = self._resolve_public_media_url(raw)
        if not public_url:
            note = (
                f"[QQ 暂未发送附件：{filename}；当前 QQ C2C 富媒体需要公网可访问 URL，"
                "请为 qq.public_media_base_url 配置一个可公网访问的静态地址]"
            )
            return False, note

        try:
            media = await self._client.api.post_c2c_file(
                openid=chat_id,
                file_type=self._qq_file_type(kind),
                url=public_url,
                srv_send_msg=False,
            )
            self._msg_seq += 1
            await self._client.api.post_c2c_message(
                openid=chat_id,
                msg_type=7,
                media=media,
                msg_id=reply_to,
                msg_seq=self._msg_seq,
            )
            return True, None
        except Exception as e:
            logger.error("Error sending QQ media {}: {}", filename, e)
            return False, f"[QQ 附件发送失败：{filename}]"

    async def send(self, msg: OutboundMessage) -> None:
        """Send a message through QQ."""
        if not self._client:
            logger.warning("QQ client not initialized")
            return

        try:
            reply_to = msg.metadata.get("message_id")
            fallback_notes: list[str] = []

            for media_ref in msg.media or []:
                _, note = await self._send_media_ref(msg.chat_id, media_ref, reply_to=reply_to)
                if note:
                    fallback_notes.append(note)

            content_parts = [msg.content.strip()] if msg.content and msg.content.strip() else []
            content_parts.extend(note for note in fallback_notes if note)
            final_text = "\n".join(content_parts).strip()
            if not final_text:
                return

            self._msg_seq += 1
            await self._client.api.post_c2c_message(
                openid=msg.chat_id,
                msg_type=0,
                content=final_text,
                msg_id=reply_to,
                msg_seq=self._msg_seq,
            )
        except Exception as e:
            logger.error("Error sending QQ message: {}", e)

    async def _on_message(self, data: "C2CMessage") -> None:
        """Handle incoming message from QQ."""
        try:
            if data.id in self._processed_ids:
                return
            self._processed_ids.append(data.id)

            author = data.author
            user_id = str(getattr(author, "id", None) or getattr(author, "user_openid", "unknown"))
            content = (data.content or "").strip()
            attachments = list(getattr(data, "attachments", []) or [])

            media_paths: list[str] = []
            content_parts: list[str] = [content] if content else []
            attachment_meta: list[dict[str, Any]] = []

            for attachment in attachments:
                file_path, marker, meta = await self._download_attachment(attachment)
                if file_path:
                    media_paths.append(file_path)
                if marker:
                    content_parts.append(marker)
                if meta:
                    attachment_meta.append(meta)

            if not content_parts and not media_paths:
                return

            await self._handle_message(
                sender_id=user_id,
                chat_id=user_id,
                content="\n".join(part for part in content_parts if part).strip() or "[empty message]",
                media=media_paths,
                metadata={"message_id": data.id, "attachments": attachment_meta},
            )
        except Exception:
            logger.exception("Error handling QQ message")
