from pathlib import Path

import pytest

from nanobot.agent.memory_learning import MemoryLearningManager


def _make_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True)
    return workspace


def test_record_memory_skips_duplicate_entries(tmp_path) -> None:
    manager = MemoryLearningManager(_make_workspace(tmp_path))

    assert manager._record_memory("User likes concise replies.", "user_profile") is True
    assert manager._record_memory("  User likes concise replies.  ", "user_profile") is False

    content = manager.memory_file.read_text(encoding="utf-8")
    assert content.count("User likes concise replies.") == 1


def test_record_user_profile_skips_duplicate_entries(tmp_path) -> None:
    manager = MemoryLearningManager(_make_workspace(tmp_path))

    assert manager._record_user_profile("User prefers concise replies.", "user_profile") is True
    assert manager._record_user_profile("  User prefers concise replies.  ", "user_profile") is False

    content = manager.profile_file.read_text(encoding="utf-8")
    assert content.count("User prefers concise replies.") == 1


def test_record_self_cognition_accepts_stable_identity_and_skips_duplicates(tmp_path) -> None:
    manager = MemoryLearningManager(_make_workspace(tmp_path))

    content = "我的职责边界是先核实事实，再给出可执行建议。"
    assert manager._record_self_cognition(content, "self_cognition") is True
    assert manager._record_self_cognition(content, "self_cognition") is False

    saved = manager.self_file.read_text(encoding="utf-8")
    assert saved.count(content) == 1


def test_low_value_entries_are_rejected(tmp_path) -> None:
    manager = MemoryLearningManager(_make_workspace(tmp_path))

    assert manager._record_user_profile("记住这个", "user_profile") is False
    assert manager._record_learning("下次注意", "learning") is False
    assert manager._record_self_cognition("这个很重要", "self_cognition") is False

    assert not manager.profile_file.exists()
    assert not manager.learnings_file.exists()
    assert not manager.self_file.exists()


def test_is_trigger_message_supports_english_keywords(tmp_path) -> None:
    manager = MemoryLearningManager(_make_workspace(tmp_path))

    assert manager.is_trigger_message("Please remember this for later.") is True
    assert manager.is_trigger_message("Can you record this experience?") is True
    assert manager.is_trigger_message("Hello there.") is False


def test_record_shared_user_profile_writes_into_bot_section(tmp_path) -> None:
    workspace = _make_workspace(tmp_path)
    shared_memory = tmp_path / "shared" / "memory"
    shared_memory.mkdir(parents=True)
    (shared_memory / "USER_PROFILE.md").write_text(
        """# 用户画像

## 基本信息
<!-- 由 bot1_core 维护 -->
- **姓名**：

## 健康档案
<!-- 由 bot2_health 维护 -->
- **身高体重**：

## 财务状况
<!-- 由 bot3_finance 维护 -->
- **收入水平**：

## 心理状态
<!-- 由 bot4_emotion 维护 -->
- **性格特点**：

## 自媒体运营
<!-- 由 bot5_media 维护 -->
- **平台账号**：

## 更新日志
""",
        encoding="utf-8",
    )
    manager = MemoryLearningManager(
        workspace,
        shared_memory_path=shared_memory,
        bot_id="bot1_core",
    )

    assert manager._record_shared_user_profile("用户偏好简洁回复。", "user_profile") is True
    assert manager._record_shared_user_profile("用户偏好简洁回复。", "user_profile") is False

    content = (shared_memory / "USER_PROFILE.md").read_text(encoding="utf-8")
    assert "## 基本信息" in content
    assert "用户偏好简洁回复。" in content
    assert content.count("用户偏好简洁回复。") == 1


@pytest.mark.asyncio
async def test_record_on_trigger_marks_duplicates_as_skipped(tmp_path) -> None:
    manager = MemoryLearningManager(_make_workspace(tmp_path))

    async def fake_ai(_: str) -> str:
        return (
            "memory: User likes concise replies.\n"
            "learning: Use ab open before ab snapshot."
        )

    first = await manager.record_on_trigger("\u8bb0\u4e0b\u6765\uff1a...", "", fake_ai)
    second = await manager.record_on_trigger("\u8bb0\u4e0b\u6765\uff1a...", "", fake_ai)

    assert first["recorded"] == {
        "memory": "User likes concise replies.",
        "learning": "Use ab open before ab snapshot.",
    }
    assert second["recorded"] == {}
    assert second["skipped"] == {
        "memory": "duplicate",
        "learning": "duplicate",
    }

    profile = manager.profile_file.read_text(encoding="utf-8")
    assert "User likes concise replies." in profile


@pytest.mark.asyncio
async def test_record_on_trigger_skips_low_value_entries(tmp_path) -> None:
    manager = MemoryLearningManager(_make_workspace(tmp_path))

    async def fake_ai(_: str) -> str:
        return (
            "self: 这个很重要\n"
            "memory: 记住这个\n"
            "learning: 下次注意"
        )

    result = await manager.record_on_trigger("记下来", "", fake_ai)

    assert result["recorded"] == {}
    assert result["skipped"] == {
        "self": "low_value",
        "memory": "low_value",
        "learning": "low_value",
    }
    assert "跳过低价值自我认知" in result["summary"]
