"""Memory and learning manager for bot self-improvement."""

import re
from pathlib import Path
from typing import Any

from loguru import logger

from nanobot.utils.timezone import now, now_str


class MemoryLearningManager:
    """Manager for memory and learning self-improvement."""

    TRIGGER_KEYWORDS = [
        "记录一下",
        "记下来",
        "记住这个",
        "更新记忆",
        "更新经验",
        "这是一个经验",
        "这个很重要",
        "下次注意",
        "以后要",
    ]

    def __init__(
        self,
        workspace: Path,
        shared_learnings_path: Path | None = None,
        shared_memory_path: Path | None = None,
    ):
        self.workspace = workspace
        self.shared_learnings_path = shared_learnings_path
        self.shared_memory_path = shared_memory_path

        self.memory_file = workspace / "memory" / "MEMORY.md"
        self.learnings_file = workspace / ".learnings" / "LEARNINGS.md"
        self.shared_learnings_file = (
            shared_learnings_path / "SHARED.md" if shared_learnings_path else None
        )
        self.shared_memory_file = (
            shared_memory_path / "USER_PROFILE.md" if shared_memory_path else None
        )

    def is_trigger_message(self, message: str) -> bool:
        """Check if message contains trigger keywords for recording."""
        message_lower = message.lower()
        return any(kw in message_lower for kw in self.TRIGGER_KEYWORDS)

    async def think_and_record(
        self,
        user_message: str,
        ai_response: str,
        call_ai_func: Any,
    ) -> dict[str, str]:
        """
        Think about whether to record memory or learning.
        Called after each AI response (active mechanism).

        Returns dict of what was recorded.
        """
        prompt = f"""请分析以下对话，判断是否需要记录信息：

【用户消息】
{user_message}

【AI回复】
{ai_response}

请判断：
1. 是否包含用户画像信息（姓名、偏好、习惯、职业等）？如有，提取关键信息。
2. 是否有解决问题的经验价值？如有，简述问题和解决方案。
3. 是否有其他 bot 也需要知道的共享信息？

请用以下 JSON 格式回复（如果没有需要记录的内容，所有字段填 null）：
{{"user_profile": null或"关键信息", "learning": null或"经验描述", "shared": null或"共享信息"}}

只回复 JSON，不要其他内容。"""

        try:
            result = await call_ai_func(prompt)
            result = result.strip()

            json_match = re.search(r"\{[^}]+\}", result, re.DOTALL)
            if not json_match:
                return {}

            import json
            data = json.loads(json_match.group())

            recorded = {}

            if data.get("user_profile"):
                self._record_memory(data["user_profile"], "user_profile")
                recorded["user_profile"] = data["user_profile"]

            if data.get("learning"):
                self._record_learning(data["learning"], "learning")
                recorded["learning"] = data["learning"]

            if data.get("shared"):
                self._record_shared_learning(data["shared"])
                recorded["shared"] = data["shared"]

            return recorded

        except Exception as e:
            logger.error(f"Think and record failed: {e}")
            return {}

    async def record_on_trigger(
        self,
        user_message: str,
        ai_response: str,
        call_ai_func: Any,
    ) -> str:
        """
        Record memory or learning when user triggers (passive mechanism).

        Returns confirmation message.
        """
        prompt = f"""用户要求记录以下对话内容：

【用户消息】
{user_message}

【AI回复】
{ai_response}

请判断应该记录到哪里：
1. 用户画像（用户个人信息、偏好、习惯）→ 回复 "memory: 内容"
2. 学习经验（解决问题的方法、最佳实践）→ 回复 "learning: 内容"
3. 共享经验（其他 bot 也需要知道的）→ 回复 "shared: 内容"

可以同时记录多个，每行一个。例如：
memory: 用户喜欢简洁的回复
learning: 使用 read_file 工具读取技能文件
shared: API 需要添加 User-Agent 头才能访问

只回复需要记录的内容，不要其他解释。"""

        try:
            result = await call_ai_func(prompt)
            recorded = []

            for line in result.strip().split("\n"):
                line = line.strip()
                if line.startswith("memory:"):
                    content = line[7:].strip()
                    self._record_memory(content, "user_request")
                    recorded.append(f"📝 记忆：{content}")
                elif line.startswith("learning:"):
                    content = line[9:].strip()
                    self._record_learning(content, "user_request")
                    recorded.append(f"📚 经验：{content}")
                elif line.startswith("shared:"):
                    content = line[7:].strip()
                    self._record_shared_learning(content)
                    recorded.append(f"🌐 共享：{content}")

            if recorded:
                return "✅ 已记录：\n" + "\n".join(recorded)
            else:
                return "❌ 未能识别需要记录的内容"

        except Exception as e:
            logger.error(f"Record on trigger failed: {e}")
            return f"❌ 记录失败：{e}"

    def _record_memory(self, content: str, source: str = "auto") -> None:
        """Record to memory file."""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        timestamp = now_str("%Y-%m-%d %H:%M")
        entry = f"\n### [{timestamp}] ({source})\n{content}\n"

        if not self.memory_file.exists():
            self.memory_file.write_text(f"# 记忆\n\n{entry}")
        else:
            current = self.memory_file.read_text()
            self.memory_file.write_text(current + entry)

        logger.info(f"Recorded memory: {content[:50]}...")

    def _record_learning(self, content: str, source: str = "auto") -> None:
        """Record to learning file."""
        self.learnings_file.parent.mkdir(parents=True, exist_ok=True)

        timestamp = now_str("%Y-%m-%d")
        entry_id = now().strftime("%Y%m%d-%H%M%S")
        entry = f"\n## [LRN-{entry_id}] 经验\n\n**来源**：{source} | **日期**：{timestamp}\n\n{content}\n\n---\n"

        if not self.learnings_file.exists():
            self.learnings_file.write_text(f"# 学习记录\n\n{entry}")
        else:
            current = self.learnings_file.read_text()
            self.learnings_file.write_text(current + entry)

        logger.info(f"Recorded learning: {content[:50]}...")

    def _record_shared_learning(self, content: str) -> None:
        """Record to shared learning file."""
        if not self.shared_learnings_file:
            return

        self.shared_learnings_file.parent.mkdir(parents=True, exist_ok=True)

        timestamp = now_str("%Y-%m-%d")
        entry_id = now().strftime("%Y%m%d-%H%M%S")
        entry = f"\n## [SHARED-{entry_id}] 共享经验\n\n**日期**：{timestamp}\n\n{content}\n\n---\n"

        if not self.shared_learnings_file.exists():
            self.shared_learnings_file.write_text(f"# 共享学习记录\n\n{entry}")
        else:
            current = self.shared_learnings_file.read_text()
            self.shared_learnings_file.write_text(current + entry)

        logger.info(f"Recorded shared learning: {content[:50]}...")
