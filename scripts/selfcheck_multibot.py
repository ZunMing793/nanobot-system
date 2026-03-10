from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

BOTS = ["bot1_core", "bot2_health", "bot3_finance", "bot4_emotion", "bot5_media"]
WORKSPACE_REQUIRED_FILES = [
    "self/SELF.md",
    "user/PROFILE.md",
    "memory/MEMORY.md",
    ".learnings/LEARNINGS.md",
    "knowledge/README.md",
    "knowledge/index/manifest.json",
]
SHARED_REQUIRED_FILES = [
    "memory/USER_PROFILE.md",
    "learnings/SHARED.md",
    "knowledge/README.md",
    "knowledge/index/manifest.json",
    "knowledge/index/CATALOG.md",
]


@dataclass
class BotCheckResult:
    bot_id: str
    ok: bool
    model: str = "-"
    provider: str = "-"
    channels: str = "-"
    workspace: str = "-"
    missing: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def render(self) -> str:
        missing = ",".join(self.missing) if self.missing else "-"
        errors = " | ".join(self.errors) if self.errors else "-"
        status = "OK" if self.ok else "FAIL"
        return (
            f"{self.bot_id}:{status} "
            f"model={self.model} provider={self.provider} channels={self.channels} "
            f"workspace={self.workspace} missing={missing} errors={errors}"
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_import_path() -> None:
    repo = _repo_root()
    nanobot_src = repo / "NanoBot"
    if str(nanobot_src) not in sys.path:
        sys.path.insert(0, str(nanobot_src))


def _missing_items(base: Path, relative_paths: list[str]) -> list[str]:
    return [rel for rel in relative_paths if not (base / rel).exists()]


def _resolve_workspace_dir(bot_dir: Path, cfg) -> Path:
    workspace_value = getattr(getattr(cfg, "agents", None), "defaults", None)
    workspace_path = getattr(workspace_value, "workspace", "./workspace")
    return (bot_dir / workspace_path).resolve()


def _check_shared_layout(repo: Path) -> list[str]:
    shared_root = repo / "shared"
    missing = _missing_items(shared_root, SHARED_REQUIRED_FILES)
    if not (shared_root / "skills").exists():
        missing.append("skills/")
    return missing


def _check_bot(bot_id: str, repo: Path) -> BotCheckResult:
    _ensure_import_path()

    from nanobot.bus.queue import MessageBus
    from nanobot.channels.manager import ChannelManager
    from nanobot.cli.commands import _load_models_config, _make_provider
    from nanobot.config.loader import load_config

    bot_dir = repo / bot_id
    cfg_path = bot_dir / "config.json"
    if not cfg_path.exists():
        return BotCheckResult(bot_id=bot_id, ok=False, errors=("missing config.json",))

    try:
        prev_cwd = os.getcwd()
        os.chdir(str(bot_dir))
        try:
            cfg = load_config(Path("config.json"))
            models_cfg = _load_models_config(cfg)
            provider = _make_provider(cfg, models_cfg)
            bus = MessageBus()
            channels = ChannelManager(cfg, bus)
            enabled = ",".join(channels.enabled_channels) if channels.enabled_channels else "-"

            workspace_dir = _resolve_workspace_dir(bot_dir, cfg)
            missing = _missing_items(workspace_dir, WORKSPACE_REQUIRED_FILES)
            if not (workspace_dir / "skills").exists():
                missing.append("skills/")

            selected_model = cfg.agents.defaults.model
            provider_name = type(provider).__name__
            workspace_state = "OK" if not missing else "MISSING"
            errors: list[str] = []

            model_info = None
            if isinstance(models_cfg, dict):
                model_info = models_cfg.get("models", {}).get(selected_model)
            if model_info is None:
                errors.append(f"unknown model '{selected_model}'")
            elif "provider" not in model_info:
                errors.append(f"model '{selected_model}' missing provider mapping")

            return BotCheckResult(
                bot_id=bot_id,
                ok=not missing and not errors,
                model=selected_model,
                provider=provider_name,
                channels=enabled,
                workspace=workspace_state,
                missing=tuple(missing),
                errors=tuple(errors),
            )
        finally:
            os.chdir(prev_cwd)
    except Exception as exc:
        return BotCheckResult(bot_id=bot_id, ok=False, errors=(f"{type(exc).__name__}: {exc}",))


def main() -> int:
    repo = _repo_root()
    shared_missing = _check_shared_layout(repo)
    if shared_missing:
        print("shared:FAIL missing=" + ",".join(shared_missing))
    else:
        print("shared:OK")

    failed: list[str] = []
    for bot_id in BOTS:
        result = _check_bot(bot_id, repo)
        print(result.render())
        if not result.ok:
            failed.append(result.bot_id)

    if shared_missing or failed:
        failed_parts: list[str] = []
        if shared_missing:
            failed_parts.append("shared")
        failed_parts.extend(failed)
        print("FAILED=" + ";".join(failed_parts))
        return 1
    print("ALL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

