"""Memory and learning manager for bot self-improvement."""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from loguru import logger

from nanobot.utils.shared_memory import SharedMemoryWriter
from nanobot.utils.timezone import now, now_str


class MemoryLearningManager:
    """Manager for profile, memory, and learning self-improvement."""

    TRIGGER_KEYWORDS = [
        "记录一个",
        "记下来",
        "记住这个",
        "更新记忆",
        "更新经验",
        "这是一个经验",
        "这个很重要",
        "下次注意",
        "以后要",
        "remember this",
        "remember that",
        "record this",
        "save this",
        "note this",
        "log this",
    ]
    DUPLICATE_SIMILARITY_THRESHOLD = 0.92
    MIN_CONTENT_LENGTH = {
        "self": 10,
        "profile": 8,
        "memory": 10,
        "learning": 12,
        "shared": 12,
    }
    LOW_VALUE_EXACT = {
        "none",
        "null",
        "n/a",
        "无",
        "暂无",
        "暂无记录",
        "待补充",
        "记住这个",
        "记录一下",
        "这个很重要",
        "下次注意",
        "以后要注意",
        "remember this",
        "this is important",
        "take care next time",
        "note this",
        "keep this in mind",
    }
    LOW_VALUE_PHRASES = (
        "格式说明",
        "简短标题",
        "一句话描述",
        "不要输出解释",
        "可以同时记录多个项目",
        "如果没有可记录内容",
        "暂无记录",
        "待补充",
        "示例",
        "模板",
    )
    GENERIC_META_PATTERNS = (
        r"^(请|需要|应该|可以|记得|记住).{0,12}(记录|记下来|更新)$",
        r"^(这|那)?(个|条)?(很重要|要注意|要记住)$",
        r"^(用户|ai|assistant)(消息|回复|说了).*$",
    )
    LEARNING_SIGNAL_KEYWORDS = (
        "当",
        "如果",
        "遇到",
        "出现",
        "先",
        "再",
        "通过",
        "使用",
        "调用",
        "配置",
        "安装",
        "排查",
        "修复",
        "解决",
        "避免",
        "不要",
        "改为",
        "确保",
        "when",
        "if",
        "use",
        "using",
        "before",
        "after",
        "avoid",
        "fix",
        "solve",
        "validate",
        "configure",
        "install",
        "ensure",
    )
    DURABLE_PROFILE_KEYWORDS = (
        "偏好",
        "喜欢",
        "不喜欢",
        "习惯",
        "目标",
        "计划",
        "职业",
        "身份",
        "风格",
        "长期",
        "经常",
        "通常",
        "稳定",
        "约束",
        "prefer",
        "preference",
        "habit",
        "goal",
        "usually",
        "often",
        "constraint",
    )
    VOLATILE_HINT_KEYWORDS = (
        "今天",
        "刚刚",
        "刚才",
        "这次",
        "本次",
        "当前这轮",
        "这一轮",
        "临时",
        "暂时",
        "today",
        "just now",
        "for now",
        "temporary",
        "this time",
    )

    def __init__(
        self,
        workspace: Path,
        shared_learnings_path: Path | None = None,
        shared_memory_path: Path | None = None,
        bot_id: str | None = None,
    ):
        self.workspace = workspace
        self.shared_learnings_path = shared_learnings_path
        self.shared_memory_path = shared_memory_path
        self.bot_id = bot_id or workspace.parent.name

        self.self_file = workspace / "self" / "SELF.md"
        self.profile_file = workspace / "user" / "PROFILE.md"
        self.memory_file = workspace / "memory" / "MEMORY.md"
        self.learnings_file = workspace / ".learnings" / "LEARNINGS.md"
        self.shared_learnings_file = (
            shared_learnings_path / "SHARED.md" if shared_learnings_path else None
        )
        self.shared_memory_file = (
            shared_memory_path / "USER_PROFILE.md" if shared_memory_path else None
        )
        self.shared_memory_writer = (
            SharedMemoryWriter(shared_memory_path) if shared_memory_path else None
        )

    def is_trigger_message(self, message: str) -> bool:
        """Check whether the message explicitly asks to record something."""
        normalized = self._normalize_text(message)
        return any(self._normalize_text(keyword) in normalized for keyword in self.TRIGGER_KEYWORDS)

    async def think_and_record(
        self,
        user_message: str,
        ai_response: str,
        call_ai_func: Any,
    ) -> dict[str, str]:
        """Actively summarize and record useful profile facts or learnings."""
        prompt = f"""请分析以下对话，判断是否值得沉淀到长期文档。

【用户消息】{user_message}

【AI 回复】{ai_response}

只有在内容满足“未来仍然有价值、足够具体、不是空话或一次性信息”时才记录。
以下内容宁可不记，也不要滥记：
- 当前这一次对话里的临时安排、礼貌用语、寒暄
- “这个很重要”“下次注意”这类空泛句子
- 没有主体、条件、结论的泛泛总结
- 纯粹重复已有常识或模板文字

请严格判断以下 4 类：
1. `self_cognition`：是否出现了值得长期保留的 bot 自我定位、职责边界、工作原则？
2. `user_profile`：是否出现了稳定的用户画像（姓名、偏好、习惯、长期目标、约束等）？
3. `learning`：是否出现了可复用的解决问题经验？必须具体到“什么场景下，怎么做，为什么有效/要避免什么”。
4. `shared`：是否出现了其他 bot 也应该知道的共享经验？只有跨 bot 普适时才记录。

请只返回 JSON，对没有高价值内容的字段填 null，格式如下：
{{"self_cognition": null, "user_profile": null, "learning": null, "shared": null}}
"""

        try:
            result = await call_ai_func(prompt)
            data = self._parse_json_payload(result)
            if not data:
                return {}

            recorded: dict[str, str] = {}

            self_cognition = self._clean_value(data.get("self_cognition"))
            if self_cognition and self._record_self_cognition(self_cognition, "self_cognition"):
                recorded["self_cognition"] = self_cognition

            user_profile = self._clean_value(data.get("user_profile"))
            if user_profile and self._record_user_profile(user_profile, "user_profile"):
                self._record_shared_user_profile(user_profile, "user_profile")
                recorded["user_profile"] = user_profile

            learning = self._clean_value(data.get("learning"))
            if learning and self._record_learning(learning, "learning"):
                recorded["learning"] = learning

            shared = self._clean_value(data.get("shared"))
            if shared and self._record_shared_learning(shared):
                recorded["shared"] = shared

            return recorded

        except Exception as exc:
            logger.error("Think and record failed: {}", exc)
            return {}

    async def record_on_trigger(
        self,
        user_message: str,
        ai_response: str,
        call_ai_func: Any,
    ) -> dict[str, Any]:
        """Passively record user profile or learning when explicitly requested."""
        prompt = f"""用户要求记录以下对话内容：
【用户消息】{user_message}

【AI 回复】{ai_response}

即使用户主动要求“记录”，你也必须先判断是否真的值得写入长期文档。
如果内容只是临时事项、空话、寒暄、重复、没有长期价值，请不要记录。

请判断应该记录到哪里：
1. 自我认知（bot 的职责、边界、工作原则）→ 返回 `self: 内容`
2. 用户画像（用户个人信息、偏好、习惯、长期目标）→ 返回 `memory: 内容`
3. 学习经验（解决问题的方法、最佳实践）→ 返回 `learning: 内容`
4. 共享经验（其他 bot 也应该知道的经验）→ 返回 `shared: 内容`

可以同时记录多个项目，每行一个。
如果没有高价值内容可记录，只返回 `none`。
不要输出解释。
"""

        try:
            result = await call_ai_func(prompt)
            recorded: dict[str, str] = {}
            skipped: dict[str, str] = {}
            handled_slots: set[str] = set()

            for category, content in self._parse_trigger_lines(result):
                slot = {
                    "memory": "profile",
                    "profile": "profile",
                    "self": "self",
                    "learning": "learning",
                    "shared": "shared",
                }[category]
                if slot in handled_slots:
                    continue
                handled_slots.add(slot)

                if category in {"memory", "profile"}:
                    if not self._is_valuable_content(content, kind="profile"):
                        skipped[category] = "low_value"
                        continue
                    wrote_private = self._record_user_profile(content, "user_request")
                    wrote_shared = self._record_shared_user_profile(content, "user_request")
                    if wrote_private or wrote_shared:
                        recorded[category] = content
                    else:
                        skipped[category] = "duplicate"
                    continue

                if category == "self":
                    if self._record_self_cognition(content, "user_request"):
                        recorded[category] = content
                    else:
                        skipped[category] = (
                            "duplicate"
                            if self._has_duplicate_entry(self.self_file, content, kind="self")
                            else "low_value"
                        )
                    continue

                writer = {
                    "learning": lambda value: self._record_learning(value, "user_request"),
                    "shared": self._record_shared_learning,
                }[category]
                if writer(content):
                    recorded[category] = content
                else:
                    skipped[category] = (
                        "duplicate"
                        if (
                            (category == "learning" and self._has_duplicate_entry(self.learnings_file, content, kind="learning"))
                            or (
                                category == "shared"
                                and self.shared_learnings_file
                                and self._has_duplicate_entry(
                                    self.shared_learnings_file,
                                    content,
                                    kind="learning",
                                )
                            )
                        )
                        else "low_value"
                    )

            return {
                "recorded": recorded,
                "skipped": skipped,
                "summary": self._build_trigger_summary(recorded, skipped),
            }

        except Exception as exc:
            logger.error("Record on trigger failed: {}", exc)
            return {
                "recorded": {},
                "skipped": {},
                "summary": f"❌ 记录失败：{exc}",
            }

    @staticmethod
    def _clean_value(value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        cleaned = value.strip()
        return cleaned or None

    def _record_self_cognition(self, content: str, source: str = "auto") -> bool:
        """Record stable bot self-cognition when content is valuable and new."""
        self.self_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._is_valuable_content(content, kind="self"):
            logger.info("Skip low-value self cognition: {}", content[:80])
            return False
        if self._has_duplicate_entry(self.self_file, content, kind="self"):
            logger.info("Skip duplicate self cognition: {}", content[:80])
            return False

        timestamp = now_str("%Y-%m-%d %H:%M")
        entry = f"\n### [{timestamp}] ({source})\n{content}\n"
        if not self.self_file.exists():
            self.self_file.write_text(f"# Bot Self Cognition\n\n{entry}", encoding="utf-8")
        else:
            current = self.self_file.read_text(encoding="utf-8")
            separator = "" if current.endswith("\n") else "\n"
            self.self_file.write_text(current + separator + entry, encoding="utf-8")

        logger.info("Recorded self cognition: {}", content[:80])
        return True

    def _record_user_profile(self, content: str, source: str = "auto") -> bool:
        """Record to the private user profile file when the content is new enough."""
        self.profile_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._is_valuable_content(content, kind="profile"):
            logger.info("Skip low-value user profile: {}", content[:80])
            return False
        if self._has_duplicate_entry(self.profile_file, content, kind="profile"):
            logger.info("Skip duplicate user profile: {}", content[:80])
            return False

        timestamp = now_str("%Y-%m-%d %H:%M")
        entry = f"\n### [{timestamp}] ({source})\n{content}\n"
        if not self.profile_file.exists():
            self.profile_file.write_text(f"# User Profile\n\n{entry}", encoding="utf-8")
        else:
            current = self.profile_file.read_text(encoding="utf-8")
            separator = "" if current.endswith("\n") else "\n"
            self.profile_file.write_text(current + separator + entry, encoding="utf-8")

        logger.info("Recorded private user profile: {}", content[:80])
        return True

    def _record_memory(self, content: str, source: str = "auto") -> bool:
        """Record to the private memory file when the content is new enough."""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._is_valuable_content(content, kind="memory"):
            logger.info("Skip low-value memory: {}", content[:80])
            return False
        if self._has_duplicate_entry(self.memory_file, content, kind="memory"):
            logger.info("Skip duplicate memory: {}", content[:80])
            return False

        timestamp = now_str("%Y-%m-%d %H:%M")
        entry = f"\n### [{timestamp}] ({source})\n{content}\n"
        if not self.memory_file.exists():
            self.memory_file.write_text(f"# Memory\n\n{entry}", encoding="utf-8")
        else:
            current = self.memory_file.read_text(encoding="utf-8")
            self.memory_file.write_text(current + entry, encoding="utf-8")

        logger.info("Recorded memory: {}", content[:80])
        return True

    def _record_learning(self, content: str, source: str = "auto") -> bool:
        """Record to the private learning file when the content is new enough."""
        self.learnings_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._is_valuable_content(content, kind="learning"):
            logger.info("Skip low-value learning: {}", content[:80])
            return False
        if self._has_duplicate_entry(self.learnings_file, content, kind="learning"):
            logger.info("Skip duplicate learning: {}", content[:80])
            return False

        timestamp = now_str("%Y-%m-%d")
        entry_id = now().strftime("%Y%m%d-%H%M%S")
        entry = (
            f"\n## [LRN-{entry_id}] 经验\n\n"
            f"**来源**：{source} | **日期**：{timestamp}\n\n"
            f"{content}\n\n---\n"
        )
        if not self.learnings_file.exists():
            self.learnings_file.write_text(f"# 学习记录\n\n{entry}", encoding="utf-8")
        else:
            current = self.learnings_file.read_text(encoding="utf-8")
            self.learnings_file.write_text(current + entry, encoding="utf-8")

        logger.info("Recorded learning: {}", content[:80])
        return True

    def _record_shared_learning(self, content: str) -> bool:
        """Record to the shared learning file when the content is new enough."""
        if not self.shared_learnings_file:
            return False

        self.shared_learnings_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._is_valuable_content(content, kind="shared"):
            logger.info("Skip low-value shared learning: {}", content[:80])
            return False
        if self._has_duplicate_entry(self.shared_learnings_file, content, kind="learning"):
            logger.info("Skip duplicate shared learning: {}", content[:80])
            return False

        timestamp = now_str("%Y-%m-%d")
        entry_id = now().strftime("%Y%m%d-%H%M%S")
        entry = (
            f"\n## [SHARED-{entry_id}] 共享经验\n\n"
            f"**日期**：{timestamp}\n\n"
            f"{content}\n\n---\n"
        )
        if not self.shared_learnings_file.exists():
            self.shared_learnings_file.write_text(f"# 共享学习记录\n\n{entry}", encoding="utf-8")
        else:
            current = self.shared_learnings_file.read_text(encoding="utf-8")
            self.shared_learnings_file.write_text(current + entry, encoding="utf-8")

        logger.info("Recorded shared learning: {}", content[:80])
        return True

    def _record_shared_user_profile(self, content: str, source: str = "auto") -> bool:
        """Record user profile facts to the shared profile section for this bot."""
        if not self.shared_memory_file or not self.shared_memory_writer:
            return False
        if not self.shared_memory_file.exists():
            return False
        if not self._is_valuable_content(content, kind="profile"):
            logger.info("Skip low-value shared profile: {}", content[:80])
            return False

        section_name = self.shared_memory_writer._get_section_name(self.bot_id)
        if not section_name:
            return False

        file_content = self.shared_memory_file.read_text(encoding="utf-8")
        section_content = self.shared_memory_writer._extract_section(file_content, section_name)
        if not section_content:
            return False
        if self._contains_duplicate_text(section_content, content, kind="profile"):
            logger.info("Skip duplicate shared profile: {}", content[:80])
            return False

        timestamp = now_str("%Y-%m-%d %H:%M")
        new_section = section_content.rstrip() + f"\n\n### [{timestamp}] ({source})\n- {content}\n"
        updated = self.shared_memory_writer._replace_section(file_content, section_name, new_section)
        if updated == file_content:
            return False
        self.shared_memory_file.write_text(updated, encoding="utf-8")
        logger.info("Recorded shared user profile for {}: {}", self.bot_id, content[:80])
        return True

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = re.sub(r"\s+", " ", text).strip().lower()
        normalized = normalized.replace("：", ":")
        normalized = normalized.replace("“", '"').replace("”", '"')
        normalized = normalized.replace("‘", "'").replace("’", "'")
        return normalized

    def _contains_duplicate_text(self, text: str, content: str, *, kind: str) -> bool:
        candidate = self._normalize_text(content)
        if not candidate:
            return True

        for existing in self._extract_entries_from_text(text, kind=kind):
            normalized_existing = self._normalize_text(existing)
            if not normalized_existing:
                continue
            if candidate == normalized_existing:
                return True
            if candidate in normalized_existing or normalized_existing in candidate:
                return True
            similarity = SequenceMatcher(None, candidate, normalized_existing).ratio()
            if similarity >= self.DUPLICATE_SIMILARITY_THRESHOLD:
                return True
        return False

    def _has_duplicate_entry(self, file_path: Path, content: str, *, kind: str) -> bool:
        if not file_path.exists():
            return False
        text = file_path.read_text(encoding="utf-8")
        return self._contains_duplicate_text(text, content, kind=kind)

    def _extract_entries_from_text(self, text: str, *, kind: str) -> list[str]:
        if kind in {"self", "memory", "profile"}:
            pattern = re.compile(
                r"^### \[[^\]]+\] \([^)]+\)\n(?:- )?(.+?)(?=^### \[[^\]]+\] \([^)]+\)\n|\Z)",
                re.MULTILINE | re.DOTALL,
            )
            return [match.group(1).strip() for match in pattern.finditer(text) if match.group(1).strip()]

        pattern = re.compile(
            r"^## \[[^\]]+\] [^\n]+\n\n(?:\*\*[^\n]+\n\n)?(.+?)(?=\n---\n|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        return [match.group(1).strip() for match in pattern.finditer(text) if match.group(1).strip()]

    @staticmethod
    def _parse_json_payload(raw: str) -> dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.DOTALL).strip()

        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return {}

        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {}

    def _parse_trigger_lines(self, raw: str) -> list[tuple[str, str]]:
        pairs: list[tuple[str, str]] = []
        for line in raw.strip().splitlines():
            stripped = line.strip().lstrip("-•*").strip()
            if not stripped or stripped.lower() == "none":
                continue
            match = re.match(
                r"^(memory|profile|self|learning|shared)\s*[:：]\s*(.+)$",
                stripped,
                re.IGNORECASE,
            )
            if not match:
                continue
            category = match.group(1).lower()
            content = match.group(2).strip()
            if content:
                pairs.append((category, content))
        return pairs

    def _is_valuable_content(self, content: str, *, kind: str) -> bool:
        cleaned = self._clean_value(content)
        if not cleaned:
            return False

        normalized = self._normalize_text(cleaned)
        normalized_plain = re.sub(r"[^\w\u4e00-\u9fff]+", " ", normalized).strip()
        compact = re.sub(r"[\W_]+", "", normalized)
        if len(compact) < self.MIN_CONTENT_LENGTH.get(kind, 8):
            return False
        if normalized in self.LOW_VALUE_EXACT or normalized_plain in self.LOW_VALUE_EXACT:
            return False
        if any(phrase in normalized for phrase in self.LOW_VALUE_PHRASES):
            return False
        if any(re.match(pattern, normalized) for pattern in self.GENERIC_META_PATTERNS):
            return False

        if kind in {"profile", "self"}:
            if any(keyword in normalized for keyword in self.VOLATILE_HINT_KEYWORDS) and not any(
                keyword in normalized for keyword in self.DURABLE_PROFILE_KEYWORDS
            ):
                return False

        if kind == "self":
            return any(
                keyword in normalized
                for keyword in (
                    "职责",
                    "边界",
                    "原则",
                    "定位",
                    "角色",
                    "使命",
                    "风格",
                    "协作",
                    "role",
                    "boundary",
                    "principle",
                    "mission",
                    "style",
                    "responsibility",
                )
            )

        if kind in {"learning", "shared"}:
            return any(keyword in normalized for keyword in self.LEARNING_SIGNAL_KEYWORDS)

        return True

    @staticmethod
    def _build_trigger_summary(recorded: dict[str, str], skipped: dict[str, str]) -> str:
        labels = {
            "self": "自我认知",
            "memory": "用户画像",
            "profile": "用户画像",
            "learning": "经验",
            "shared": "共享经验",
        }
        lines: list[str] = []
        for category, content in recorded.items():
            lines.append(f"✅ 已记录{labels[category]}：{content}")
        for category, reason in skipped.items():
            if reason == "low_value":
                lines.append(f"⚪ 跳过低价值{labels[category]}")
            else:
                lines.append(f"⚪ 跳过重复{labels[category]}")
        if not lines:
            return "⚪ 未识别到需要记录的新内容"
        return "\n".join(lines)
