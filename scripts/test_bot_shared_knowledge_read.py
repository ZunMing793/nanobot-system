from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_import_path() -> None:
    repo = _repo_root()
    nanobot_src = repo / "NanoBot"
    if str(nanobot_src) not in sys.path:
        sys.path.insert(0, str(nanobot_src))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a real bot prompt against shared knowledge files.")
    parser.add_argument("--bot-root", type=Path, required=True, help="Bot root directory containing config.json")
    parser.add_argument(
        "--prompt",
        type=str,
        default=(
            "请不要凭印象回答。共享知识库里有一本《刘澜·学习力30讲》,"
            "请你先自行查看共享知识库目录和对应提取文本,再回答:"
            "1)这份资料的正式标题是什么;"
            "2)前3个你能确认的核心主题;"
            "3)给出2个来自原文的短摘录(每个不超过20个字);"
            "4)最后明确说明你读取了哪些具体文件路径。"
        ),
        help="Prompt to send to the bot. Include explicit file paths when needed.",
    )
    parser.add_argument("--session", type=str, default="cli:shared-knowledge-test", help="Session key")
    return parser


async def _run(bot_root: Path, prompt: str, session_key: str) -> int:
    from nanobot.agent.loop import AgentLoop
    from nanobot.bus.queue import MessageBus
    from nanobot.cli.commands import _load_models_config, _make_provider
    from nanobot.config.loader import load_config
    from nanobot.cron.service import CronService
    from nanobot.utils.helpers import sync_workspace_templates

    os.chdir(bot_root)
    config = load_config(bot_root / "config.json")
    sync_workspace_templates(config.workspace_path)

    bus = MessageBus()
    models_config = _load_models_config(config)
    provider = _make_provider(config, models_config)
    cron = CronService(config.workspace_path / "cron" / "jobs.json")

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=config.workspace_path,
        model=config.agents.defaults.model,
        temperature=config.agents.defaults.temperature,
        max_tokens=config.agents.defaults.max_tokens,
        max_iterations=config.agents.defaults.max_tool_iterations,
        memory_window=config.agents.defaults.memory_window,
        reasoning_effort=config.agents.defaults.reasoning_effort,
        brave_api_key=config.tools.web.search.api_key or None,
        web_proxy=config.tools.web.proxy or None,
        exec_config=config.tools.exec,
        cron_service=cron,
        restrict_to_workspace=config.tools.restrict_to_workspace,
        mcp_servers=config.tools.mcp_servers,
        channels_config=config.channels,
        shared_skills_path=config.shared_skills_path,
        shared_learnings_path=config.shared_learnings_path,
        shared_memory_path=config.shared_memory_path,
        models_config_path=config.shared_skills_path.parent / "config" / "models.json"
        if config.shared_skills_path
        else None,
        bot_id=config.bot_id,
        bot_root=config.workspace_path.parent,
        builtin_skills_path=_repo_root() / "NanoBot" / "nanobot" / "skills",
    )

    async def on_progress(content: str, *, tool_hint: bool = False) -> None:
        tag = "TOOL" if tool_hint else "THINK"
        print(f"[{tag}] {content}")

    try:
        response = await agent.process_direct(prompt, session_key=session_key, on_progress=on_progress)
        print("\n===FINAL===\n")
        print(response)
        return 0
    finally:
        await agent.close_mcp()


def main() -> int:
    _ensure_import_path()
    args = _build_parser().parse_args()
    return asyncio.run(_run(args.bot_root.resolve(), args.prompt, args.session))


if __name__ == "__main__":
    raise SystemExit(main())
