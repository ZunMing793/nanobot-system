import asyncio
from pathlib import Path

from nanobot.bus.events import OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.channels.qq import QQChannel
from nanobot.config.schema import QQConfig


class _FakeAuthor:
    def __init__(self, user_openid: str):
        self.user_openid = user_openid


class _FakeAttachment:
    def __init__(
        self,
        *,
        attachment_id: str = "att1",
        filename: str = "image.png",
        content_type: str = "image/png",
        url: str = "https://example.com/image.png",
        size: int = 10,
    ):
        self.id = attachment_id
        self.filename = filename
        self.content_type = content_type
        self.url = url
        self.size = size


class _FakeInbound:
    def __init__(self, *, message_id: str = "msg1", content: str = "", attachments=None):
        self.id = message_id
        self.content = content
        self.attachments = attachments or []
        self.author = _FakeAuthor("user-openid")


class _FakeAPI:
    def __init__(self):
        self.sent_messages: list[dict] = []
        self.sent_files: list[dict] = []

    async def post_c2c_message(self, **kwargs):
        self.sent_messages.append(kwargs)
        return kwargs

    async def post_c2c_file(self, **kwargs):
        self.sent_files.append(kwargs)
        return {"file_uuid": "uuid", "file_info": "info", "ttl": 0}


class _FakeClient:
    def __init__(self):
        self.api = _FakeAPI()


def _make_channel() -> QQChannel:
    config = QQConfig(enabled=True, app_id="app", secret="secret", allow_from=["*"])
    return QQChannel(config=config, bus=MessageBus())


def test_on_message_accepts_attachment_only(monkeypatch) -> None:
    channel = _make_channel()
    captured: dict = {}

    async def fake_download(_attachment):
        return "/tmp/image.png", "[image: /tmp/image.png]", {"type": "image", "path": "/tmp/image.png"}

    async def fake_handle_message(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(channel, "_download_attachment", fake_download)
    monkeypatch.setattr(channel, "_handle_message", fake_handle_message)

    asyncio.run(channel._on_message(_FakeInbound(attachments=[_FakeAttachment()])))

    assert captured["chat_id"] == "user-openid"
    assert captured["media"] == ["/tmp/image.png"]
    assert "[image: /tmp/image.png]" in captured["content"]
    assert captured["metadata"]["attachments"][0]["type"] == "image"


def test_send_remote_image_as_c2c_media() -> None:
    channel = _make_channel()
    channel._client = _FakeClient()

    asyncio.run(
        channel.send(
            OutboundMessage(
                channel="qq",
                chat_id="user-openid",
                content="",
                media=["https://example.com/pic.png"],
            )
        )
    )

    assert channel._client.api.sent_files[0]["file_type"] == 1
    assert channel._client.api.sent_messages[0]["msg_type"] == 7
    assert channel._client.api.sent_messages[0]["media"]["file_uuid"] == "uuid"


def test_resolve_public_media_url_stages_local_file(tmp_path: Path) -> None:
    channel = _make_channel()
    channel.config.public_media_base_url = "https://files.example.com/qq"
    channel._outbound_media_dir = tmp_path / "outbound"
    local_file = tmp_path / "chart.png"
    local_file.write_bytes(b"image")

    public_url = channel._resolve_public_media_url(str(local_file))

    assert public_url is not None
    assert public_url.startswith("https://files.example.com/qq/")
    staged_files = list(channel._outbound_media_dir.iterdir())
    assert len(staged_files) == 1
    assert staged_files[0].read_bytes() == b"image"


def test_send_local_file_without_public_url_falls_back_to_text(tmp_path: Path) -> None:
    channel = _make_channel()
    channel._client = _FakeClient()
    local_file = tmp_path / "report.pdf"
    local_file.write_bytes(b"pdf")

    asyncio.run(
        channel.send(
            OutboundMessage(
                channel="qq",
                chat_id="user-openid",
                content="请查看附件",
                media=[str(local_file)],
            )
        )
    )

    assert channel._client.api.sent_files == []
    assert channel._client.api.sent_messages[-1]["msg_type"] == 0
    assert "请查看附件" in channel._client.api.sent_messages[-1]["content"]
    assert "QQ C2C 富媒体需要公网可访问 URL" in channel._client.api.sent_messages[-1]["content"]
