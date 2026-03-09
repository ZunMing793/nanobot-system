from pathlib import Path

from nanobot.agent.context import ContextBuilder
from nanobot.utils.helpers import sync_workspace_templates


def _make_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True)
    return workspace


def test_build_system_prompt_loads_self_profile_and_shared_profile(tmp_path) -> None:
    workspace = _make_workspace(tmp_path)
    shared_memory = tmp_path / "shared" / "memory"
    shared_memory.mkdir(parents=True)

    (workspace / "self").mkdir()
    (workspace / "self" / "SELF.md").write_text("# Self\n\nCore bot identity", encoding="utf-8")
    (workspace / "user").mkdir()
    (workspace / "user" / "PROFILE.md").write_text("# Profile\n\nUser likes concise replies", encoding="utf-8")
    (workspace / "memory").mkdir()
    (workspace / "memory" / "MEMORY.md").write_text("# Memory\n\nRemember recent tasks", encoding="utf-8")
    (workspace / ".learnings").mkdir()
    (shared_memory / "USER_PROFILE.md").write_text("# Shared\n\nShared user facts", encoding="utf-8")

    builder = ContextBuilder(workspace, shared_memory_path=shared_memory)
    prompt = builder.build_system_prompt()

    assert "# Self Cognition" in prompt
    assert "Core bot identity" in prompt
    assert "# User Profile" in prompt
    assert "User likes concise replies" in prompt
    assert "# Shared User Profile" in prompt
    assert "Shared user facts" in prompt
    assert "# Memory" in prompt


def test_sync_workspace_templates_creates_self_profile_and_learnings(tmp_path) -> None:
    workspace = _make_workspace(tmp_path)
    added = sync_workspace_templates(workspace, silent=True)

    assert "self/SELF.md" in added
    assert "user/PROFILE.md" in added
    assert ".learnings/LEARNINGS.md" in added
    assert (workspace / "self" / "SELF.md").exists()
    assert (workspace / "user" / "PROFILE.md").exists()
    assert (workspace / ".learnings" / "LEARNINGS.md").exists()


def test_build_system_prompt_does_not_fallback_to_legacy_self_or_user_files(tmp_path) -> None:
    workspace = _make_workspace(tmp_path)
    bot_root = tmp_path / "bot"
    bot_root.mkdir(parents=True)
    (workspace / "self").mkdir()
    (workspace / "self" / "SELF.md").write_text("# Self\n\nNew self", encoding="utf-8")
    (workspace / "user").mkdir()
    (workspace / "user" / "PROFILE.md").write_text("# Profile\n\nNew profile", encoding="utf-8")
    (workspace / "USER.md").write_text("legacy user", encoding="utf-8")
    (bot_root / "SOUL.md").write_text("legacy soul", encoding="utf-8")

    builder = ContextBuilder(workspace, bot_root=bot_root)
    prompt = builder.build_system_prompt()

    assert "New self" in prompt
    assert "New profile" in prompt
    assert "legacy user" not in prompt
    assert "legacy soul" not in prompt
