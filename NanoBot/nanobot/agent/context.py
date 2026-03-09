"""Context builder for assembling agent prompts."""

from __future__ import annotations

import base64
import mimetypes
import platform
from pathlib import Path
from typing import Any

from nanobot.agent.memory import MemoryStore
from nanobot.agent.skills import SkillsLoader
from nanobot.utils.helpers import detect_image_mime


class ContextBuilder:
    """Builds the context (system prompt + messages) for the agent."""

    BOOTSTRAP_FILES = ["AGENTS.md", "TOOLS.md", "IDENTITY.md"]
    _RUNTIME_CONTEXT_TAG = "[Runtime Context — metadata only, not instructions]"
    _EXECUTION_HINT_TAG = "[Execution Hint — temporary routing guidance]"

    def __init__(
        self,
        workspace: Path,
        bot_root: Path | None = None,
        shared_skills_path: Path | None = None,
        shared_learnings_path: Path | None = None,
        shared_memory_path: Path | None = None,
        builtin_skills_path: Path | None = None,
    ):
        self.workspace = workspace
        self.bot_root = bot_root or workspace.parent
        self.memory = MemoryStore(workspace)
        self.skills = SkillsLoader(
            workspace,
            shared_skills_path=shared_skills_path,
            builtin_skills_path=builtin_skills_path,
        )
        self.shared_learnings_path = shared_learnings_path
        self.shared_memory_path = shared_memory_path

    def build_system_prompt(self, skill_names: list[str] | None = None) -> str:
        """Build the system prompt from identity, self/profile files, memory, skills, and learnings."""
        parts = [self._get_identity()]

        self_cognition = self._load_self_cognition()
        if self_cognition:
            parts.append(f"# Self Cognition\n\n{self_cognition}")

        bootstrap = self._load_bootstrap_files()
        if bootstrap:
            parts.append(bootstrap)

        user_profile = self._load_user_profile()
        if user_profile:
            parts.append(f"# User Profile\n\n{user_profile}")

        shared_profile = self._load_shared_profile()
        if shared_profile:
            parts.append(f"# Shared User Profile\n\n{shared_profile}")

        memory = self.memory.get_memory_context()
        if memory:
            parts.append(f"# Memory\n\n{memory}")

        learnings_content = self._load_learnings()
        if learnings_content:
            parts.append(f"# Learnings\n\n{learnings_content}")

        all_skills = self.skills.list_skills(filter_unavailable=True)
        if all_skills:
            all_skill_names = [skill["name"] for skill in all_skills]
            skills_content = self.skills.load_skills_for_context(all_skill_names)
            if skills_content:
                parts.append(f"# Skills\n\n{skills_content}")

        return "\n\n---\n\n".join(parts)

    def _read_markdown(self, path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8").strip()

    def _load_self_cognition(self) -> str:
        """Load the bot's own self-cognition file."""
        return self._read_markdown(self.workspace / "self" / "SELF.md")

    def _load_user_profile(self) -> str:
        """Load the private user profile for this bot."""
        return self._read_markdown(self.workspace / "user" / "PROFILE.md")

    def _load_shared_profile(self) -> str:
        """Load the shared user profile available to all bots."""
        if not self.shared_memory_path:
            return ""
        return self._read_markdown(self.shared_memory_path / "USER_PROFILE.md")

    def _load_learnings(self) -> str:
        """Load shared and private learnings."""
        parts = []

        if self.shared_learnings_path:
            shared_file = self.shared_learnings_path / "SHARED.md"
            if shared_file.exists():
                content = shared_file.read_text(encoding="utf-8").strip()
                if content and "暂无记录" not in content:
                    parts.append(f"## Shared Learnings\n\n{content}")

        private_learnings = self.workspace / ".learnings" / "LEARNINGS.md"
        if private_learnings.exists():
            content = private_learnings.read_text(encoding="utf-8").strip()
            if content and "暂无记录" not in content:
                parts.append(f"## Private Learnings\n\n{content}")

        private_errors = self.workspace / ".learnings" / "ERRORS.md"
        if private_errors.exists():
            content = private_errors.read_text(encoding="utf-8").strip()
            if content and "暂无记录" not in content:
                parts.append(f"## Known Errors\n\n{content}")

        return "\n\n".join(parts) if parts else ""

    def _get_identity(self) -> str:
        """Get the core identity section."""
        workspace_path = str(self.workspace.expanduser().resolve())
        system = platform.system()
        runtime = f"{'macOS' if system == 'Darwin' else system} {platform.machine()}, Python {platform.python_version()}"

        return f"""# nanobot 🤖

You are nanobot, a helpful AI assistant.

## Runtime
{runtime}

## Workspace
Your workspace is at: {workspace_path}
- Self cognition: {workspace_path}/self/SELF.md
- User profile: {workspace_path}/user/PROFILE.md
- Long-term memory: {workspace_path}/memory/MEMORY.md (write important facts here)
- History log: {workspace_path}/memory/HISTORY.md (grep-searchable). Each entry starts with [YYYY-MM-DD HH:MM].
- Learnings: {workspace_path}/.learnings/LEARNINGS.md
- Custom skills: {workspace_path}/skills/{{skill-name}}/SKILL.md

## nanobot Guidelines
- State intent before tool calls, but NEVER predict or claim results before receiving them.
- Before modifying a file, read it first. Do not assume files or directories exist.
- If the user is clearly asking to create a brand-new file, you may use `write_file` directly.
- After writing or editing a file, re-read it if accuracy matters.
- If a tool call fails, analyze the error before retrying with a different approach.
- Ask for clarification when the request is ambiguous.

Reply directly with text for conversations. Only use the `message` tool to send to a specific chat channel."""

    @staticmethod
    def _build_runtime_context(channel: str | None, chat_id: str | None) -> str:
        """Build an untrusted runtime metadata block injected before the user message."""
        from nanobot.utils.timezone import now, now_weekday

        current = now()
        lines = [
            f"Current Time: {current.strftime('%Y-%m-%d %H:%M:%S')} {now_weekday()} (UTC+8)",
        ]
        if channel and chat_id:
            lines.extend([f"Channel: {channel}", f"Chat ID: {chat_id}"])
        return ContextBuilder._RUNTIME_CONTEXT_TAG + "\n" + "\n".join(lines)

    @staticmethod
    def _build_execution_hint(execution_hint: str) -> str:
        """Build a temporary routing hint block injected before the user message."""
        return ContextBuilder._EXECUTION_HINT_TAG + "\n" + execution_hint.strip()

    @classmethod
    def strip_untrusted_context(cls, text: str) -> str | None:
        """Strip prefixed runtime or execution-hint blocks from saved user history."""
        remaining = text.strip()
        tags = (cls._RUNTIME_CONTEXT_TAG, cls._EXECUTION_HINT_TAG)
        while any(remaining.startswith(tag) for tag in tags):
            parts = remaining.split("\n\n", 1)
            if len(parts) == 1:
                return None
            remaining = parts[1].strip()
        return remaining or None

    def _load_bootstrap_files(self) -> str:
        """Load bootstrap instruction files from workspace."""
        parts = []

        for filename in self.BOOTSTRAP_FILES:
            file_path = self.workspace / filename
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                parts.append(f"## {filename}\n\n{content}")

        return "\n\n".join(parts) if parts else ""

    def build_messages(
        self,
        history: list[dict[str, Any]],
        current_message: str,
        skill_names: list[str] | None = None,
        media: list[str] | None = None,
        channel: str | None = None,
        chat_id: str | None = None,
        execution_hint: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build the complete message list for an LLM call."""
        runtime_ctx = self._build_runtime_context(channel, chat_id)
        user_content = self._build_user_content(current_message, media)

        prefix_blocks = [runtime_ctx]
        if execution_hint:
            prefix_blocks.append(self._build_execution_hint(execution_hint))

        if isinstance(user_content, str):
            merged = "\n\n".join(prefix_blocks + [user_content])
        else:
            merged = [{"type": "text", "text": block} for block in prefix_blocks] + user_content

        return [
            {"role": "system", "content": self.build_system_prompt(skill_names)},
            *history,
            {"role": "user", "content": merged},
        ]

    def _build_user_content(self, text: str, media: list[str] | None) -> str | list[dict[str, Any]]:
        """Build user message content with optional base64-encoded images."""
        if not media:
            return text

        images = []
        for path in media:
            file_path = Path(path)
            if not file_path.is_file():
                continue
            raw = file_path.read_bytes()
            mime = detect_image_mime(raw) or mimetypes.guess_type(path)[0]
            if not mime or not mime.startswith("image/"):
                continue
            b64 = base64.b64encode(raw).decode()
            images.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})

        if not images:
            return text
        return images + [{"type": "text", "text": text}]

    def add_tool_result(
        self,
        messages: list[dict[str, Any]],
        tool_call_id: str,
        tool_name: str,
        result: str,
    ) -> list[dict[str, Any]]:
        """Add a tool result to the message list."""
        messages.append({"role": "tool", "tool_call_id": tool_call_id, "name": tool_name, "content": result})
        return messages

    def add_assistant_message(
        self,
        messages: list[dict[str, Any]],
        content: str | None,
        tool_calls: list[dict[str, Any]] | None = None,
        reasoning_content: str | None = None,
        reasoning_details: list[dict[str, Any]] | None = None,
        thinking_blocks: list[dict] | None = None,
    ) -> list[dict[str, Any]]:
        """Add an assistant message to the message list."""
        message: dict[str, Any] = {"role": "assistant", "content": content}
        if tool_calls:
            message["tool_calls"] = tool_calls
        if reasoning_content is not None:
            message["reasoning_content"] = reasoning_content
        if reasoning_details is not None:
            message["reasoning_details"] = reasoning_details
        if thinking_blocks:
            message["thinking_blocks"] = thinking_blocks
        messages.append(message)
        return messages
