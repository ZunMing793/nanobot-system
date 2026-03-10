from __future__ import annotations

import argparse
import asyncio
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_REQUIRED_SKILLS = ("agent-browser", "pdf", "find-skills")
DEFAULT_REQUIRED_TOOLS = (
    "read_file",
    "list_dir",
    "write_file",
    "edit_file",
    "exec",
    "web_search",
    "web_fetch",
    "message",
    "spawn",
)
TEXT_ISSUE_MARKERS = ("\ufffd", "锟", "鈥", "鉁", "鉂", "鈿", "脳", "鈫", "鈮")


@dataclass
class SmokeWarning:
    code: str
    message: str


@dataclass
class SmokeResult:
    bot_id: str
    ok: bool = True
    warnings: list[SmokeWarning] = field(default_factory=list)
    facts: dict[str, Any] = field(default_factory=dict)

    def fail(self, message: str) -> None:
        self.ok = False
        self.warnings.append(SmokeWarning("FAIL", message))

    def warn(self, code: str, message: str) -> None:
        self.warnings.append(SmokeWarning(code, message))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_import_path() -> None:
    repo = _repo_root()
    nanobot_src = repo / "NanoBot"
    if str(nanobot_src) not in sys.path:
        sys.path.insert(0, str(nanobot_src))


def _resolve_config_path(base: Path, raw_path: Path | None) -> Path | None:
    if raw_path is None:
        return None
    return raw_path.resolve() if raw_path.is_absolute() else (base / raw_path).resolve()


def _detect_text_issues(text: str) -> list[str]:
    issues: list[str] = []
    if "\ufffd" in text:
        issues.append("replacement-char")
    for marker in TEXT_ISSUE_MARKERS[1:]:
        if marker in text:
            issues.append(f"mojibake:{marker.encode('unicode_escape').decode()}")
    return issues


async def _ping_model(provider, model: str) -> tuple[bool, str]:
    response = await provider.chat(
        messages=[
            {"role": "system", "content": "Reply briefly and do not use tools."},
            {"role": "user", "content": "Reply with exactly PONG."},
        ],
        model=model,
        max_tokens=16,
        temperature=0,
    )
    content = (response.content or "").strip()
    if response.finish_reason == "error":
        return False, content or "empty error response"
    if not content:
        return False, "empty response"
    return True, content


async def run_smoke_test(
    bot_id: str,
    *,
    required_skills: tuple[str, ...] = DEFAULT_REQUIRED_SKILLS,
    required_tools: tuple[str, ...] = DEFAULT_REQUIRED_TOOLS,
    ping_model: bool = False,
) -> SmokeResult:
    _ensure_import_path()

    from nanobot.agent.context import ContextBuilder
    from nanobot.agent.loop import AgentLoop
    from nanobot.agent.skills import SkillsLoader
    from nanobot.bus.queue import MessageBus
    from nanobot.cli.commands import _load_models_config, _make_provider
    from nanobot.config.loader import load_config

    repo = _repo_root()
    bot_dir = repo / bot_id
    result = SmokeResult(bot_id=bot_id)
    if not bot_dir.exists():
        result.fail(f"bot directory not found: {bot_dir}")
        return result

    prev_cwd = os.getcwd()
    try:
        os.chdir(str(bot_dir))
        cfg = load_config(Path("config.json"))
        models_cfg = _load_models_config(cfg)
        provider = _make_provider(cfg, models_cfg)
        model_name = cfg.agents.defaults.model

        workspace = _resolve_config_path(bot_dir, cfg.workspace_path)
        shared_skills = _resolve_config_path(bot_dir, cfg.shared_skills_path)
        shared_memory = _resolve_config_path(bot_dir, cfg.shared_memory_path)
        shared_learnings = _resolve_config_path(bot_dir, cfg.shared_learnings_path)
        builtin_skills = (repo / "NanoBot" / "nanobot" / "skills").resolve()

        result.facts.update(
            {
                "model": model_name,
                "provider": type(provider).__name__,
                "workspace": str(workspace),
                "shared_skills": str(shared_skills) if shared_skills else "-",
            }
        )

        if not workspace or not workspace.exists():
            result.fail(f"workspace missing: {workspace}")
            return result

        context = ContextBuilder(
            workspace,
            bot_root=bot_dir,
            shared_skills_path=shared_skills,
            shared_learnings_path=shared_learnings,
            shared_memory_path=shared_memory,
            builtin_skills_path=builtin_skills,
        )
        prompt = context.build_system_prompt()
        if not prompt.strip():
            result.fail("system prompt is empty")
        else:
            result.facts["prompt_chars"] = len(prompt)

        loader = SkillsLoader(
            workspace=workspace,
            shared_skills_path=shared_skills,
            builtin_skills_path=builtin_skills,
        )
        all_skills = loader.list_skills(filter_unavailable=False)
        available_skills = loader.list_skills(filter_unavailable=True)
        all_skill_names = {item["name"] for item in all_skills}
        available_skill_names = {item["name"] for item in available_skills}
        result.facts["skills_total"] = len(all_skills)
        result.facts["skills_available"] = len(available_skills)
        result.facts["skills_unavailable"] = sorted(all_skill_names - available_skill_names)
        if not all_skills:
            result.fail("no skills discovered")

        for skill_name in required_skills:
            skill_path = loader.get_skill_path(skill_name)
            if not skill_path:
                result.fail(f"required skill missing: {skill_name}")
                continue

            try:
                skill_text = loader.load_skill(skill_name) or ""
            except Exception as exc:
                result.fail(f"failed to load skill '{skill_name}': {exc}")
                continue

            try:
                guide_text = loader.load_skill_guide(skill_name) or ""
            except Exception as exc:
                result.fail(f"failed to load guide '{skill_name}': {exc}")
                continue

            if not skill_text.strip():
                result.fail(f"skill empty: {skill_name}")
                continue
            if not guide_text.strip():
                result.warn("missing-guide", f"guide empty or missing: {skill_name}")

            text_issues = sorted(set(_detect_text_issues(skill_text) + _detect_text_issues(guide_text)))
            if text_issues:
                result.warn(
                    "skill-text-issue",
                    f"{skill_name} contains suspicious text issues: {', '.join(text_issues)}",
                )
            if skill_name not in available_skill_names:
                result.warn("skill-unavailable", f"{skill_name} is present but currently unavailable")

        bus = MessageBus()
        loop = AgentLoop(
            bus=bus,
            provider=provider,
            workspace=workspace,
            model=model_name,
            temperature=cfg.agents.defaults.temperature,
            max_tokens=cfg.agents.defaults.max_tokens,
            memory_window=cfg.agents.defaults.memory_window,
            reasoning_effort=cfg.agents.defaults.reasoning_effort,
            brave_api_key=cfg.tools.web.search.api_key,
            web_proxy=cfg.tools.web.proxy,
            exec_config=cfg.tools.exec,
            restrict_to_workspace=cfg.tools.restrict_to_workspace,
            mcp_servers=cfg.tools.mcp_servers,
            shared_skills_path=shared_skills,
            shared_learnings_path=shared_learnings,
            shared_memory_path=shared_memory,
            models_config_path=(shared_skills.parent / "config" / "models.json").resolve()
            if shared_skills
            else None,
            bot_id=cfg.bot_id,
            bot_root=bot_dir,
            builtin_skills_path=builtin_skills,
        )
        tool_names = set(loop.tools.tool_names)
        result.facts["tools"] = sorted(tool_names)
        missing_tools = [name for name in required_tools if name not in tool_names]
        if missing_tools:
            result.fail(f"missing required tools: {', '.join(missing_tools)}")

        if ping_model:
            ok, content = await _ping_model(provider, model_name)
            if ok:
                result.facts["model_ping"] = content
            else:
                result.fail(f"model ping failed: {content}")

        close = getattr(provider, "close", None)
        if callable(close):
            maybe_awaitable = close()
            if asyncio.iscoroutine(maybe_awaitable):
                await maybe_awaitable
    except Exception as exc:
        result.fail(f"{type(exc).__name__}: {exc}")
    finally:
        os.chdir(prev_cwd)

    return result


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test a single NanoBot workspace.")
    parser.add_argument("--bot", required=True, help="Bot folder name, e.g. bot1_core")
    parser.add_argument(
        "--model-ping",
        action="store_true",
        help="Perform a real lightweight model call with the bot's configured model.",
    )
    parser.add_argument(
        "--skills",
        default=",".join(DEFAULT_REQUIRED_SKILLS),
        help="Comma-separated required skills to check.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    required_skills = tuple(filter(None, (item.strip() for item in args.skills.split(","))))
    result = asyncio.run(
        run_smoke_test(
            args.bot,
            required_skills=required_skills or DEFAULT_REQUIRED_SKILLS,
            ping_model=args.model_ping,
        )
    )

    status = "PASS" if result.ok else "FAIL"
    print(
        f"{result.bot_id}:{status} "
        f"model={result.facts.get('model', '-')} provider={result.facts.get('provider', '-')}"
    )
    for key in ("workspace", "shared_skills", "prompt_chars", "skills_total", "skills_available", "model_ping"):
        if key in result.facts:
            print(f"  {key}: {result.facts[key]}")
    if "skills_unavailable" in result.facts and result.facts["skills_unavailable"]:
        print("  skills_unavailable:", ", ".join(result.facts["skills_unavailable"]))
    if "tools" in result.facts:
        print("  tools:", ", ".join(result.facts["tools"]))
    for warning in result.warnings:
        print(f"  [{warning.code}] {warning.message}")

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
