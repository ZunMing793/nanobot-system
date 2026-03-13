"""Cron tool for scheduling reminders and tasks."""

from contextvars import ContextVar
from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.cron.service import CronService
from nanobot.cron.types import CronSchedule


class CronTool(Tool):
    """Tool to schedule reminders and recurring tasks."""

    def __init__(self, cron_service: CronService):
        self._cron = cron_service
        self._channel = ""
        self._chat_id = ""
        self._in_cron_context: ContextVar[bool] = ContextVar("cron_in_context", default=False)

    def set_context(self, channel: str, chat_id: str) -> None:
        """Set the current session context for delivery."""
        self._channel = channel
        self._chat_id = chat_id

    def set_cron_context(self, active: bool):
        """Mark whether the tool is executing inside a cron job callback."""
        return self._in_cron_context.set(active)

    def reset_cron_context(self, token) -> None:
        """Restore previous cron context."""
        self._in_cron_context.reset(token)

    @property
    def name(self) -> str:
        return "cron"

    @property
    def description(self) -> str:
        return "Schedule reminders, recurring tasks, and manage task packs. Actions: add, list, remove, pack_list, pack_switch, pack_add_job, pack_remove_job, pack_create, pack_delete."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "list", "remove", "pack_list", "pack_switch", "pack_add_job", "pack_remove_job", "pack_create", "pack_delete"],
                    "description": "Action to perform",
                },
                "message": {"type": "string", "description": "Reminder message (for add)"},
                "every_seconds": {
                    "type": "integer",
                    "description": "Interval in seconds (for recurring tasks)",
                },
                "cron_expr": {
                    "type": "string",
                    "description": "Cron expression like '0 9 * * *' (for scheduled tasks)",
                },
                "tz": {
                    "type": "string",
                    "description": "IANA timezone for cron expressions (e.g. 'America/Vancouver')",
                },
                "at": {
                    "type": "string",
                    "description": "ISO datetime for one-time execution (e.g. '2026-02-12T10:30:00')",
                },
                "job_id": {"type": "string", "description": "Job ID (for remove)"},
                "pack_name": {"type": "string", "description": "Pack internal name (e.g. 'lab_competition')"},
                "pack_display": {"type": "string", "description": "Pack display name (e.g. '工作模式')"},
                "pack_description": {"type": "string", "description": "Pack description"},
            },
            "required": ["action"],
        }

    async def execute(
        self,
        action: str,
        message: str = "",
        every_seconds: int | None = None,
        cron_expr: str | None = None,
        tz: str | None = None,
        at: str | None = None,
        job_id: str | None = None,
        pack_name: str | None = None,
        pack_display: str | None = None,
        pack_description: str | None = None,
        **kwargs: Any,
    ) -> str:
        if action == "add":
            if self._in_cron_context.get():
                return "Error: cannot schedule new jobs from within a cron job execution"
            return self._add_job(message, every_seconds, cron_expr, tz, at, pack_name)
        elif action == "list":
            return self._list_jobs()
        elif action == "remove":
            return self._remove_job(job_id)
        elif action == "pack_list":
            return self._list_packs()
        elif action == "pack_switch":
            return self._switch_pack(pack_name)
        elif action == "pack_add_job":
            return self._add_job_to_pack(job_id, pack_name)
        elif action == "pack_remove_job":
            return self._remove_job_from_pack(job_id, pack_name)
        elif action == "pack_create":
            return self._create_pack(pack_name, pack_display, pack_description)
        elif action == "pack_delete":
            return self._delete_pack(pack_name)
        return f"Unknown action: {action}"

    def _add_job(
        self,
        message: str,
        every_seconds: int | None,
        cron_expr: str | None,
        tz: str | None,
        at: str | None,
        pack_name: str | None = None,
    ) -> str:
        if not message:
            return "Error: message is required for add"
        if not self._channel or not self._chat_id:
            return "Error: no session context (channel/chat_id)"
        if tz and not cron_expr:
            return "Error: tz can only be used with cron_expr"
        if tz:
            from zoneinfo import ZoneInfo

            try:
                ZoneInfo(tz)
            except (KeyError, Exception):
                return f"Error: unknown timezone '{tz}'"

        # Build schedule
        delete_after = False
        if every_seconds:
            schedule = CronSchedule(kind="every", every_ms=every_seconds * 1000)
        elif cron_expr:
            schedule = CronSchedule(kind="cron", expr=cron_expr, tz=tz)
        elif at:
            from datetime import datetime

            try:
                dt = datetime.fromisoformat(at)
            except ValueError:
                return f"Error: invalid ISO datetime format '{at}'. Expected format: YYYY-MM-DDTHH:MM:SS"
            at_ms = int(dt.timestamp() * 1000)
            schedule = CronSchedule(kind="at", at_ms=at_ms)
            delete_after = True
        else:
            return "Error: either every_seconds, cron_expr, or at is required"

        job = self._cron.add_job(
            name=message[:30],
            schedule=schedule,
            message=message,
            deliver=True,
            channel=self._channel,
            to=self._chat_id,
            delete_after_run=delete_after,
        )

        # Add to pack if specified
        if pack_name:
            pack = self._cron.get_pack_by_name(pack_name)
            if pack:
                self._cron.add_job_to_pack(job.id, pack.id)
                # If no active pack, the new job should be disabled
                active_pack = self._cron.get_active_pack()
                if not active_pack:
                    self._cron.enable_job(job.id, False)
                    return f"Created job '{job.name}' (id: {job.id}) in pack '{pack.display}' (disabled - no active pack)"
                elif active_pack.id != pack.id:
                    self._cron.enable_job(job.id, False)
                    return f"Created job '{job.name}' (id: {job.id}) in pack '{pack.display}' (disabled - different pack active)"
                return f"Created job '{job.name}' (id: {job.id}) in pack '{pack.display}'"
            else:
                return f"Created job '{job.name}' (id: {job.id}) - warning: pack '{pack_name}' not found"

        return f"Created job '{job.name}' (id: {job.id})"

    def _list_jobs(self) -> str:
        jobs = self._cron.list_jobs()
        if not jobs:
            return "No scheduled jobs."
        lines = [f"- {j.name} (id: {j.id}, {j.schedule.kind})" for j in jobs]
        return "Scheduled jobs:\n" + "\n".join(lines)

    def _remove_job(self, job_id: str | None) -> str:
        if not job_id:
            return "Error: job_id is required for remove"
        if self._cron.remove_job(job_id):
            return f"Removed job {job_id}"
        return f"Job {job_id} not found"

    # ========== Pack Management Methods ==========

    def _list_packs(self) -> str:
        """List all task packs with their status."""
        packs = self._cron.list_packs()
        active_pack = self._cron.get_active_pack()

        if not packs:
            return "No task packs."

        lines = ["任务包列表:"]
        for pack in packs:
            job_count = len(pack.job_ids)
            is_active = active_pack and active_pack.id == pack.id
            marker = "●" if is_active else " "
            status = " [当前激活]" if is_active else ""
            lines.append(f"- [{marker}] {pack.name} ({pack.display}) - {job_count} 个任务{status}")

        return "\n".join(lines)

    def _switch_pack(self, pack_name: str | None) -> str:
        """Switch to a pack by name, or disable all if no name given."""
        if pack_name is None:
            # Disable all jobs
            success, _ = self._cron.switch_pack(None)
            if success:
                return "已禁用所有任务（无激活的任务包）"
            return "切换失败"

        pack = self._cron.get_pack_by_name(pack_name)
        if not pack:
            return f"Error: 任务包 '{pack_name}' 不存在"

        success, enabled_count = self._cron.switch_pack(pack.id)
        if success:
            return f"已切换到「{pack.display}」，启用 {enabled_count} 个任务"
        return f"切换失败"

    def _add_job_to_pack(self, job_id: str | None, pack_name: str | None) -> str:
        """Add an existing job to a pack."""
        if not job_id:
            return "Error: job_id is required"
        if not pack_name:
            return "Error: pack_name is required"

        pack = self._cron.get_pack_by_name(pack_name)
        if not pack:
            return f"Error: 任务包 '{pack_name}' 不存在"

        if self._cron.add_job_to_pack(job_id, pack.id):
            return f"已将任务 {job_id} 添加到「{pack.display}」"
        return f"Error: 任务 {job_id} 不存在"

    def _remove_job_from_pack(self, job_id: str | None, pack_name: str | None) -> str:
        """Remove a job from a pack."""
        if not job_id:
            return "Error: job_id is required"
        if not pack_name:
            return "Error: pack_name is required"

        pack = self._cron.get_pack_by_name(pack_name)
        if not pack:
            return f"Error: 任务包 '{pack_name}' 不存在"

        if self._cron.remove_job_from_pack(job_id, pack.id):
            return f"已将任务 {job_id} 从「{pack.display}」移除"
        return f"Error: 任务 {job_id} 不在该任务包中"

    def _create_pack(self, pack_name: str | None, pack_display: str | None, pack_description: str | None) -> str:
        """Create a new task pack."""
        if not pack_name:
            return "Error: pack_name is required"
        if not pack_display:
            return "Error: pack_display is required"

        try:
            pack = self._cron.create_pack(pack_name, pack_display, pack_description or "")
            return f"已创建任务包「{pack.display}」({pack.name})"
        except ValueError as e:
            return f"Error: {e}"

    def _delete_pack(self, pack_name: str | None) -> str:
        """Delete an empty task pack."""
        if not pack_name:
            return "Error: pack_name is required"

        pack = self._cron.get_pack_by_name(pack_name)
        if not pack:
            return f"Error: 任务包 '{pack_name}' 不存在"

        try:
            if self._cron.delete_pack(pack.id):
                return f"已删除任务包「{pack.display}」"
            return f"Error: 删除失败"
        except ValueError as e:
            return f"Error: {e}"
