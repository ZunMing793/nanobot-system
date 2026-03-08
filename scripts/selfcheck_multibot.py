from __future__ import annotations

import sys
import os
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_import_path() -> None:
    repo = _repo_root()
    nanobot_src = repo / "NanoBot"
    if str(nanobot_src) not in sys.path:
        sys.path.insert(0, str(nanobot_src))


def main() -> int:
    _ensure_import_path()

    from nanobot.bus.queue import MessageBus
    from nanobot.channels.manager import ChannelManager
    from nanobot.cli.commands import _load_models_config, _make_provider
    from nanobot.config.loader import load_config

    repo = _repo_root()
    bots = ["bot1_core", "bot2_health", "bot3_finance", "bot4_emotion", "bot5_media"]

    failed: list[str] = []

    for bot_id in bots:
        bot_dir = repo / bot_id
        cfg_path = bot_dir / "config.json"
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
                print(f"{bot_id}:OK model={cfg.agents.defaults.model} provider={type(provider).__name__} channels={enabled}")
            finally:
                os.chdir(prev_cwd)
        except Exception as e:
            failed.append(f"{bot_id}:{type(e).__name__}:{e}")
            print(f"{bot_id}:FAIL {type(e).__name__}: {e}")

    if failed:
        print("FAILED=" + ";".join(failed))
        return 1
    print("ALL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

