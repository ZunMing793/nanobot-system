"""Command handler for bot commands."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from loguru import logger

if TYPE_CHECKING:
    from nanobot.session.manager import SessionManager


class CommandHandler:
    """Handler for bot commands starting with '/'."""

    BOTS = ["bot1_core", "bot2_health", "bot3_finance", "bot4_emotion", "bot5_media"]

    def __init__(
        self,
        bot_id: str,
        workspace: Path,
        bot_root: Path | None = None,
        models_config_path: Path | None = None,
        shared_learnings_path: Path | None = None,
        shared_memory_path: Path | None = None,
        call_ai_func: Callable[[str], Any] | None = None,
        session_manager: SessionManager | None = None,
        history_window: int = 100,
    ):
        self.bot_id = bot_id
        self.workspace = workspace
        self.bot_root = bot_root or workspace.parent
        self.models_config_path = models_config_path
        self.shared_learnings_path = shared_learnings_path
        self.shared_memory_path = shared_memory_path
        self.call_ai = call_ai_func
        self.session_manager = session_manager
        self.history_window = history_window
        self.current_model_file = workspace / ".current_model"
        self.pid_dir = Path(os.environ.get("TEMP", "/tmp")) / "nanobot"

    @staticmethod
    def _service_name(bot_id: str) -> str:
        return f"nanobot@{bot_id}.service"

    def _has_systemctl(self) -> bool:
        return shutil.which("systemctl") is not None

    def _get_systemd_properties(self, bot_id: str, *properties: str) -> dict[str, str] | None:
        if not self._has_systemctl():
            return None

        command = ["systemctl", "show", self._service_name(bot_id)]
        for prop in properties:
            command.extend(["-p", prop])

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except OSError:
            return None

        if result.returncode != 0:
            return None

        parsed: dict[str, str] = {}
        for line in result.stdout.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            parsed[key] = value.strip()
        return parsed

    def _run_systemctl_action(self, action: str, bot_id: str) -> bool:
        if not self._has_systemctl():
            return False
        try:
            result = subprocess.run(
                ["systemctl", action, self._service_name(bot_id)],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            return False
        return result.returncode == 0

    def is_command(self, message: str) -> bool:
        return message.strip().startswith("/")

    def parse_command(self, message: str) -> tuple[str, list[str]]:
        parts = message.strip().split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        return command, args

    async def handle(self, message: str, session_key: str | None = None) -> str | None:
        if not self.is_command(message):
            return None

        command, args = self.parse_command(message)
        handlers = {
            "/clear": self._cmd_clear,
            "/new": self._cmd_new,
            "/compact": self._cmd_compact,
            "/model": self._cmd_model,
            "/memory": self._cmd_memory,
            "/learn": self._cmd_learn,
            "/bots": self._cmd_bots,
            "/restart": self._cmd_restart,
            "/stop": self._cmd_stop,
            "/start": self._cmd_start,
            "/logs": self._cmd_logs,
            "/status": lambda a: self._cmd_status(a, session_key=session_key),
            "/help": self._cmd_help,
        }

        handler = handlers.get(command)
        if not handler:
            return f"❌ 未知命令：{command}\n输入 /help 查看可用命令"

        try:
            return await handler(args)
        except Exception as e:
            logger.error("Command error: {} - {}", command, e)
            return f"❌ 命令执行失败：{e}"

    def _get_current_model(self) -> str:
        if self.current_model_file.exists():
            return self.current_model_file.read_text(encoding="utf-8").strip()
        return "glm-5"

    def _set_current_model(self, model: str) -> None:
        self.current_model_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_model_file.write_text(model, encoding="utf-8")

    def _get_models_config(self) -> dict[str, Any]:
        if self.models_config_path and self.models_config_path.exists():
            return json.loads(self.models_config_path.read_text(encoding="utf-8"))
        return {"providers": {}, "models": {}, "default_model": ""}

    async def _cmd_clear(self, args: list[str]) -> str:
        return "✅ 已清除上下文"

    async def _cmd_new(self, args: list[str]) -> str:
        if not self.call_ai:
            return "❌ 此命令需要 AI 支持"

        prompt = """请思考当前会话中是否有值得记录的内容：

1. 用户画像信息（姓名、偏好、习惯等）→ 更新到 PROFILE.md
2. 动态记忆（持续有效的重要背景、任务上下文）→ 更新到 MEMORY.md
3. 有价值的经验（解决问题的方法、最佳实践）→ 更新到 LEARNINGS.md
4. 共享价值的信息（其他 bot 也需要知道的）→ 更新到 shared/learnings/SHARED.md 或 shared/memory/USER_PROFILE.md

如果有，请记录。然后回复“已记录 X 条信息”或“无需记录”。
简洁回复即可，不要展开。"""

        result = await self.call_ai(prompt)
        return f"✅ {result}\n\n已新建会话"

    async def _cmd_compact(self, args: list[str]) -> str:
        if not self.call_ai:
            return "❌ 此命令需要 AI 支持"

        prompt = "请总结当前对话的关键信息，我将用这个摘要替换完整历史。简洁回复摘要内容。"
        result = await self.call_ai(prompt)
        return f"✅ 已压缩上下文\n\n摘要：{result[:200]}..."

    async def _cmd_model(self, args: list[str]) -> str:
        config = self._get_models_config()
        current = self._get_current_model()

        if len(args) >= 2:
            provider_name = args[0].lower()
            model_name = args[1]

            provider = config.get("providers", {}).get(provider_name)
            if not provider:
                available = ", ".join(config.get("providers", {}).keys())
                return f"❌ 未找到提供商：{provider_name}\n可用：{available}"

            model_cfg = None
            for key, model in config.get("models", {}).items():
                normalized = model_name.replace("-", "_").replace(".", "_")
                if model.get("model") == model_name or key == normalized:
                    model_cfg = model
                    break

            if not model_cfg:
                return f"❌ 未找到模型：{model_name}"

            self._set_current_model(model_name)
            provider_label = provider.get("name", provider_name)
            model_label = model_cfg.get("name", model_name)
            return f"✅ 已切换到 {provider_label} {model_label}\n[MODEL_SWITCH]{provider_name}|{model_name}"

        lines = ["可用模型：", ""]
        for key, model in config.get("models", {}).items():
            provider_name = model.get("provider", "")
            provider = config.get("providers", {}).get(provider_name, {})
            model_id = model.get("model", key)
            marker = " ← 当前" if model_id == current else ""
            lines.append(f"/model {provider.get('name', provider_name)} {model_id}{marker}")
        return "\n".join(lines)

    async def _cmd_memory(self, args: list[str]) -> str:
        if not self.call_ai:
            return "❌ 此命令需要 AI 支持"

        profile_file = self.workspace / "user" / "PROFILE.md"
        memory_file = self.workspace / "memory" / "MEMORY.md"

        content = "请总结以下记忆内容：\n\n"
        if profile_file.exists():
            content += f"【私有用户画像】\n{profile_file.read_text(encoding='utf-8')}\n\n"
        if memory_file.exists():
            content += f"【私有记忆】\n{memory_file.read_text(encoding='utf-8')}\n\n"
        if self.shared_memory_path:
            shared_memory_file = self.shared_memory_path / "USER_PROFILE.md"
            if shared_memory_file.exists():
                content += f"【共享记忆】\n{shared_memory_file.read_text(encoding='utf-8')}\n\n"

        result = await self.call_ai(content)
        return f"📝 记忆摘要：\n\n{result}"

    async def _cmd_learn(self, args: list[str]) -> str:
        if not self.call_ai:
            return "❌ 此命令需要 AI 支持"

        content = "请总结以下学习经验：\n\n"
        learnings_file = self.workspace / ".learnings" / "LEARNINGS.md"
        if learnings_file.exists():
            content += f"【私有经验】\n{learnings_file.read_text(encoding='utf-8')}\n\n"
        if self.shared_learnings_path:
            shared_file = self.shared_learnings_path / "SHARED.md"
            if shared_file.exists():
                content += f"【共享经验】\n{shared_file.read_text(encoding='utf-8')}\n\n"

        result = await self.call_ai(content)
        return f"📚 经验摘要：\n\n{result}"

    async def _cmd_bots(self, args: list[str]) -> str:
        lines = ["Bot 状态列表：", ""]
        lines.append("┌─────────────┬─────────┬──────────────┬─────────────┐")
        lines.append("│ Bot ID      │ 状态    │ 启动时间     │ 模型        │")
        lines.append("├─────────────┼─────────┼──────────────┼─────────────┤")

        for bot_id in self.BOTS:
            status = "运行中" if self._is_bot_running(bot_id) else "已停止"
            start_time = self._get_bot_start_time(bot_id)
            model = self._get_bot_model(bot_id)
            lines.append(f"│ {bot_id:<11} │ {status:<7} │ {start_time:<12} │ {model:<11} │")

        lines.append("└─────────────┴─────────┴──────────────┴─────────────┘")

        if self.call_ai:
            prompt = f"检查以下 bot 状态，是否有异常（如重复进程）：\n\n{chr(10).join(lines)}"
            analysis = await self.call_ai(prompt)
            return f"{chr(10).join(lines)}\n\n🔍 分析：{analysis}"
        return "\n".join(lines)

    def _is_bot_running(self, bot_id: str) -> bool:
        systemd = self._get_systemd_properties(bot_id, "ActiveState")
        if systemd and systemd.get("ActiveState") == "active":
            return True

        if bot_id == self.bot_id:
            return True

        pid_file = self.pid_dir / f"{bot_id}.pid"
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text(encoding="utf-8").strip())
                os.kill(pid, 0)
                return True
            except (ValueError, OSError, ProcessLookupError):
                return False
        return False

    def _get_bot_start_time(self, bot_id: str) -> str:
        systemd = self._get_systemd_properties(bot_id, "ActiveEnterTimestamp")
        timestamp = (systemd or {}).get("ActiveEnterTimestamp", "")
        if timestamp and timestamp != "n/a":
            try:
                core = " ".join(timestamp.split()[:3])
                return datetime.strptime(core, "%a %Y-%m-%d %H:%M:%S").strftime("%m-%d %H:%M")
            except ValueError:
                return timestamp

        pid_file = self.pid_dir / f"{bot_id}.pid"
        if pid_file.exists():
            try:
                return datetime.fromtimestamp(pid_file.stat().st_mtime).strftime("%m-%d %H:%M")
            except Exception:
                pass
        return "-"

    def _get_bot_model(self, bot_id: str) -> str:
        bot_dir = self.bot_root.parent / bot_id
        model_file = bot_dir / "workspace" / ".current_model"
        if model_file.exists():
            return model_file.read_text(encoding="utf-8").strip()[:24]
        return "glm-5"

    def _estimate_tokens_from_value(self, value: Any) -> int:
        if value is None:
            return 0
        if isinstance(value, str):
            cjk = len(re.findall(r"[\u3400-\u9FFF]", value))
            other = len(value) - cjk
            return cjk + max(1, other // 4) if value else 0
        if isinstance(value, dict):
            return sum(self._estimate_tokens_from_value(v) for v in value.values())
        if isinstance(value, list | tuple | set):
            return sum(self._estimate_tokens_from_value(v) for v in value)
        return self._estimate_tokens_from_value(str(value))

    def _get_session_context_stats(self, session_key: str | None) -> dict[str, int] | None:
        if not session_key or not self.session_manager:
            return None

        session = self.session_manager.get_or_create(session_key)
        history = session.get_history(max_messages=self.history_window)
        estimated_tokens = 0
        for item in history:
            estimated_tokens += 6
            estimated_tokens += self._estimate_tokens_from_value(item.get("role"))
            estimated_tokens += self._estimate_tokens_from_value(item.get("content"))
            estimated_tokens += self._estimate_tokens_from_value(item.get("tool_calls"))
            estimated_tokens += self._estimate_tokens_from_value(item.get("tool_call_id"))
            estimated_tokens += self._estimate_tokens_from_value(item.get("name"))

        return {
            "messages": len(history),
            "estimated_tokens": estimated_tokens,
        }

    @staticmethod
    def _format_context_limit(limit: int | str) -> str:
        if not isinstance(limit, int):
            return str(limit)
        if limit >= 1000:
            return f"{limit // 1000}K"
        return str(limit)

    async def _cmd_restart(self, args: list[str]) -> str:
        if not args:
            return "❌ 请指定 bot_id 或 all"

        if args[0].lower() == "all":
            results = [f"  {bot_id}: {self._restart_bot(bot_id)}" for bot_id in self.BOTS]
            return "✅ 已重启所有 bot：\n" + "\n".join(results)

        return f"✅ {args[0]} {self._restart_bot(args[0])}"

    def _restart_bot(self, bot_id: str) -> str:
        if bot_id not in self.BOTS:
            return "❌ 未知的 bot_id"

        try:
            if self._run_systemctl_action("restart", bot_id):
                return "已重启"
            self._stop_bot_process(bot_id)
            self._start_bot_process(bot_id)
            return "已重启"
        except Exception as e:
            return f"重启失败：{e}"

    async def _cmd_stop(self, args: list[str]) -> str:
        if not args:
            return "❌ 请指定 bot_id"
        if args[0] not in self.BOTS:
            return f"❌ 未知的 bot_id：{args[0]}"
        try:
            self._stop_bot_process(args[0])
            return f"✅ {args[0]} 已停止"
        except Exception as e:
            return f"❌ 停止失败：{e}"

    async def _cmd_start(self, args: list[str]) -> str:
        if not args:
            return "❌ 请指定 bot_id"
        if args[0] not in self.BOTS:
            return f"❌ 未知的 bot_id：{args[0]}"
        try:
            self._start_bot_process(args[0])
            return f"✅ {args[0]} 已启动"
        except Exception as e:
            return f"❌ 启动失败：{e}"

    def _stop_bot_process(self, bot_id: str) -> None:
        if self._run_systemctl_action("stop", bot_id):
            return

        pid_file = self.pid_dir / f"{bot_id}.pid"
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text(encoding="utf-8").strip())
                os.kill(pid, 9)
            except (ValueError, ProcessLookupError, OSError):
                pass
            pid_file.unlink(missing_ok=True)

    def _start_bot_process(self, bot_id: str) -> None:
        if self._run_systemctl_action("start", bot_id):
            return

        bot_dir = self.bot_root.parent / bot_id
        log_file = bot_dir / "logs" / "bot.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        import sys

        process = subprocess.Popen(
            [sys.executable, "-m", "nanobot", "gateway", "--config", "config.json"],
            cwd=str(bot_dir),
            stdout=open(log_file, "w", encoding="utf-8"),
            stderr=open(log_file.parent / "error.log", "w", encoding="utf-8"),
        )

        self.pid_dir.mkdir(parents=True, exist_ok=True)
        (self.pid_dir / f"{bot_id}.pid").write_text(str(process.pid), encoding="utf-8")

    async def _cmd_logs(self, args: list[str]) -> str:
        if not args:
            return "❌ 请指定 bot_id"

        bot_id = args[0]
        lines = int(args[1]) if len(args) > 1 else 50
        if bot_id not in self.BOTS:
            return f"❌ 未知的 bot_id：{bot_id}"

        log_file = self.bot_root.parent / bot_id / "logs" / "bot.log"
        if not log_file.exists():
            return f"❌ 日志文件不存在：{bot_id}"

        content = log_file.read_text(encoding="utf-8", errors="ignore")
        log_lines = content.strip().split("\n")[-lines:]
        return f"📜 {bot_id} 最近 {len(log_lines)} 行日志：\n\n" + "\n".join(log_lines)

    async def _cmd_status(self, args: list[str], session_key: str | None = None) -> str:
        current_model = self._get_current_model()
        config = self._get_models_config()

        model_info = None
        for model in config.get("models", {}).values():
            if model.get("model") == current_model or current_model == model.get("name"):
                model_info = model
                break

        context_limit = model_info.get("context", "N/A") if model_info else "N/A"
        session_stats = self._get_session_context_stats(session_key)

        if isinstance(context_limit, int) and session_stats:
            used_tokens = session_stats["estimated_tokens"]
            usage_pct_value = (used_tokens / context_limit * 100) if context_limit else 0
            usage_pct = round(usage_pct_value)
            if used_tokens > 0 and usage_pct == 0:
                usage_pct = 1
            context_line = f"上下文: {usage_pct}%({self._format_context_limit(context_limit)})"
            message_line = f"会话消息数: {session_stats['messages']}"
        else:
            context_line = f"上下文: 未知({self._format_context_limit(context_limit)})"
            message_line = "会话消息数: 未知"

        lines = [
            f"Bot ID: {self.bot_id}",
            f"状态: {'运行中' if self._is_bot_running(self.bot_id) else '已停止'}",
            f"模型: {model_info.get('name', current_model) if model_info else current_model}",
            context_line,
            message_line,
            f"工作区: {self.workspace}",
        ]
        return "📊 当前状态：\n\n" + "\n".join(lines)

    async def _cmd_help(self, args: list[str]) -> str:
        lines = [
            "📖 可用命令：",
            "",
            "【会话管理】",
            "  /clear          清除上下文",
            "  /new            新建会话（先判断是否值得记录）",
            "  /compact        压缩上下文",
            "",
            "【模型管理】",
            "  /model                    查看模型列表",
            "  /model <提供商> <模型名>  切换模型",
            "",
            "【记忆/经验】",
            "  /memory         查看记忆摘要",
            "  /learn          查看经验摘要",
            "",
            "【Bot 管理】",
            "  /bots                    查看所有 bot 状态",
            "  /restart <bot_id/all>    重启 bot",
            "  /stop <bot_id>           停止 bot",
            "  /start <bot_id>          启动 bot",
            "  /logs <bot_id> [行数]    查看日志",
            "",
            "【其他】",
            "  /status         查看当前状态",
            "  /help           显示帮助",
        ]
        return "\n".join(lines)
