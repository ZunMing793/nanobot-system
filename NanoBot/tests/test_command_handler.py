import asyncio
from pathlib import Path

from nanobot.agent.command_handler import CommandHandler
from nanobot.session.manager import SessionManager


def _make_handler(tmp_path: Path, bot_id: str = "bot1_core") -> CommandHandler:
    workspace = tmp_path / bot_id / "workspace"
    workspace.mkdir(parents=True)

    models_config = tmp_path / "shared" / "config" / "models.json"
    models_config.parent.mkdir(parents=True)
    models_config.write_text(
        """
        {
          "models": {
            "glm-5": {
              "name": "GLM-5",
              "model": "glm-5",
              "context": 200000
            }
          }
        }
        """,
        encoding="utf-8",
    )

    session_manager = SessionManager(workspace)
    return CommandHandler(
        bot_id=bot_id,
        workspace=workspace,
        bot_root=workspace.parent,
        models_config_path=models_config,
        shared_learnings_path=None,
        shared_memory_path=None,
        session_manager=session_manager,
        history_window=100,
    )


def test_is_bot_running_prefers_systemd_state(tmp_path, monkeypatch) -> None:
    handler = _make_handler(tmp_path)
    monkeypatch.setattr(
        handler,
        "_get_systemd_properties",
        lambda bot_id, *props: {"ActiveState": "active"} if bot_id == "bot2_health" else None,
    )

    assert handler._is_bot_running("bot2_health") is True


def test_is_bot_running_marks_current_bot_as_running(tmp_path, monkeypatch) -> None:
    handler = _make_handler(tmp_path)
    monkeypatch.setattr(handler, "_get_systemd_properties", lambda *args: None)

    assert handler._is_bot_running("bot1_core") is True


def test_get_bot_start_time_uses_systemd_timestamp(tmp_path, monkeypatch) -> None:
    handler = _make_handler(tmp_path)
    monkeypatch.setattr(
        handler,
        "_get_systemd_properties",
        lambda *args: {"ActiveEnterTimestamp": "Tue 2026-03-10 20:09:17 CST"},
    )

    assert handler._get_bot_start_time("bot1_core") == "03-10 20:09"


def test_restart_bot_uses_systemctl_when_available(tmp_path, monkeypatch) -> None:
    handler = _make_handler(tmp_path)
    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(
        handler,
        "_run_systemctl_action",
        lambda action, bot_id: calls.append((action, bot_id)) is None or action == "restart",
    )

    assert handler._restart_bot("bot1_core") == "已重启"
    assert calls == [("restart", "bot1_core")]


def test_status_formats_context_as_percent_and_short_limit(tmp_path) -> None:
    handler = _make_handler(tmp_path)
    session = handler.session_manager.get_or_create("qq:user1")
    session.add_message("user", "你好，我想继续聊健康和睡眠。")
    session.add_message("assistant", "可以，我们继续。")
    handler.session_manager.save(session)

    result = asyncio.run(handler.handle("/status", session_key="qq:user1"))

    assert result is not None
    assert "上下文:" in result
    assert "(200K)" in result
    assert "%" in result
    assert "会话消息数:" in result
