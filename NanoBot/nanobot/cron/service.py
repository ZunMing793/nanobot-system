"""Cron service for scheduling agent tasks."""

import asyncio
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Coroutine

from loguru import logger

from nanobot.cron.types import CronJob, CronJobState, CronPayload, CronSchedule, CronStore, TaskPack


def _now_ms() -> int:
    return int(time.time() * 1000)


def _compute_next_run(schedule: CronSchedule, now_ms: int) -> int | None:
    """Compute next run time in ms."""
    if schedule.kind == "at":
        return schedule.at_ms if schedule.at_ms and schedule.at_ms > now_ms else None

    if schedule.kind == "every":
        if not schedule.every_ms or schedule.every_ms <= 0:
            return None
        # Next interval from now
        return now_ms + schedule.every_ms

    if schedule.kind == "cron" and schedule.expr:
        try:
            from zoneinfo import ZoneInfo

            from croniter import croniter
            # Use caller-provided reference time for deterministic scheduling
            base_time = now_ms / 1000
            tz = ZoneInfo(schedule.tz) if schedule.tz else datetime.now().astimezone().tzinfo
            base_dt = datetime.fromtimestamp(base_time, tz=tz)
            cron = croniter(schedule.expr, base_dt)
            next_dt = cron.get_next(datetime)
            return int(next_dt.timestamp() * 1000)
        except Exception:
            return None

    return None


def _validate_schedule_for_add(schedule: CronSchedule) -> None:
    """Validate schedule fields that would otherwise create non-runnable jobs."""
    if schedule.tz and schedule.kind != "cron":
        raise ValueError("tz can only be used with cron schedules")

    if schedule.kind == "cron" and schedule.tz:
        try:
            from zoneinfo import ZoneInfo

            ZoneInfo(schedule.tz)
        except Exception:
            raise ValueError(f"unknown timezone '{schedule.tz}'") from None


class CronService:
    """Service for managing and executing scheduled jobs."""

    def __init__(
        self,
        store_path: Path,
        on_job: Callable[[CronJob], Coroutine[Any, Any, str | None]] | None = None
    ):
        self.store_path = store_path
        self.on_job = on_job
        self._store: CronStore | None = None
        self._last_mtime: float = 0.0
        self._timer_task: asyncio.Task | None = None
        self._running = False

    def _load_store(self) -> CronStore:
        """Load jobs from disk. Reloads automatically if file was modified externally."""
        if self._store and self.store_path.exists():
            mtime = self.store_path.stat().st_mtime
            if mtime != self._last_mtime:
                logger.info("Cron: jobs.json modified externally, reloading")
                self._store = None
        if self._store:
            return self._store

        if self.store_path.exists():
            try:
                data = json.loads(self.store_path.read_text(encoding="utf-8"))
                version = data.get("version", 1)
                jobs = []
                for j in data.get("jobs", []):
                    jobs.append(CronJob(
                        id=j["id"],
                        name=j["name"],
                        enabled=j.get("enabled", True),
                        schedule=CronSchedule(
                            kind=j["schedule"]["kind"],
                            at_ms=j["schedule"].get("atMs"),
                            every_ms=j["schedule"].get("everyMs"),
                            expr=j["schedule"].get("expr"),
                            tz=j["schedule"].get("tz"),
                        ),
                        payload=CronPayload(
                            kind=j["payload"].get("kind", "agent_turn"),
                            message=j["payload"].get("message", ""),
                            deliver=j["payload"].get("deliver", False),
                            channel=j["payload"].get("channel"),
                            to=j["payload"].get("to"),
                        ),
                        state=CronJobState(
                            next_run_at_ms=j.get("state", {}).get("nextRunAtMs"),
                            last_run_at_ms=j.get("state", {}).get("lastRunAtMs"),
                            last_status=j.get("state", {}).get("lastStatus"),
                            last_error=j.get("state", {}).get("lastError"),
                        ),
                        created_at_ms=j.get("createdAtMs", 0),
                        updated_at_ms=j.get("updatedAtMs", 0),
                        delete_after_run=j.get("deleteAfterRun", False),
                    ))

                # Load packs (v2 feature)
                packs = []
                for p in data.get("packs", []):
                    packs.append(TaskPack(
                        id=p["id"],
                        name=p["name"],
                        display=p["display"],
                        description=p.get("description", ""),
                        job_ids=p.get("jobIds", []),
                        created_at_ms=p.get("createdAtMs", 0),
                        updated_at_ms=p.get("updatedAtMs", 0),
                    ))

                active_pack_id = data.get("activePackId")

                self._store = CronStore(
                    version=2,
                    jobs=jobs,
                    packs=packs,
                    active_pack_id=active_pack_id,
                )

                # Migrate v1 to v2: create default packs if missing
                if version < 2 and not packs:
                    self._create_default_packs()
                    self._save_store()

            except Exception as e:
                logger.warning("Failed to load cron store: {}", e)
                self._store = CronStore()
                self._create_default_packs()
        else:
            self._store = CronStore()
            self._create_default_packs()

        return self._store

    def _create_default_packs(self) -> None:
        """Create the two default packs if they don't exist."""
        if not self._store:
            return

        now = _now_ms()
        default_packs = [
            TaskPack(
                id="pack_lab",
                name="lab_competition",
                display="实验室备赛学习",
                description="实验室备赛期间的学习任务",
                created_at_ms=now,
                updated_at_ms=now,
            ),
            TaskPack(
                id="pack_holiday",
                name="holiday_home",
                display="假期在家娱乐",
                description="假期在家的娱乐提醒",
                created_at_ms=now,
                updated_at_ms=now,
            ),
        ]

        existing_ids = {p.id for p in self._store.packs}
        for pack in default_packs:
            if pack.id not in existing_ids:
                self._store.packs.append(pack)
                logger.info("Cron: created default pack '{}'", pack.name)

    def _save_store(self) -> None:
        """Save jobs to disk."""
        if not self._store:
            return

        self.store_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": self._store.version,
            "jobs": [
                {
                    "id": j.id,
                    "name": j.name,
                    "enabled": j.enabled,
                    "schedule": {
                        "kind": j.schedule.kind,
                        "atMs": j.schedule.at_ms,
                        "everyMs": j.schedule.every_ms,
                        "expr": j.schedule.expr,
                        "tz": j.schedule.tz,
                    },
                    "payload": {
                        "kind": j.payload.kind,
                        "message": j.payload.message,
                        "deliver": j.payload.deliver,
                        "channel": j.payload.channel,
                        "to": j.payload.to,
                    },
                    "state": {
                        "nextRunAtMs": j.state.next_run_at_ms,
                        "lastRunAtMs": j.state.last_run_at_ms,
                        "lastStatus": j.state.last_status,
                        "lastError": j.state.last_error,
                    },
                    "createdAtMs": j.created_at_ms,
                    "updatedAtMs": j.updated_at_ms,
                    "deleteAfterRun": j.delete_after_run,
                }
                for j in self._store.jobs
            ],
            "packs": [
                {
                    "id": p.id,
                    "name": p.name,
                    "display": p.display,
                    "description": p.description,
                    "jobIds": p.job_ids,
                    "createdAtMs": p.created_at_ms,
                    "updatedAtMs": p.updated_at_ms,
                }
                for p in self._store.packs
            ],
            "activePackId": self._store.active_pack_id,
        }

        self.store_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        self._last_mtime = self.store_path.stat().st_mtime
    
    async def start(self) -> None:
        """Start the cron service."""
        self._running = True
        self._load_store()
        self._recompute_next_runs()
        self._save_store()
        self._arm_timer()
        logger.info("Cron service started with {} jobs", len(self._store.jobs if self._store else []))

    def stop(self) -> None:
        """Stop the cron service."""
        self._running = False
        if self._timer_task:
            self._timer_task.cancel()
            self._timer_task = None

    def _recompute_next_runs(self) -> None:
        """Recompute next run times for all enabled jobs."""
        if not self._store:
            return
        now = _now_ms()
        for job in self._store.jobs:
            if job.enabled:
                job.state.next_run_at_ms = _compute_next_run(job.schedule, now)

    def _get_next_wake_ms(self) -> int | None:
        """Get the earliest next run time across all jobs."""
        if not self._store:
            return None
        times = [j.state.next_run_at_ms for j in self._store.jobs
                 if j.enabled and j.state.next_run_at_ms]
        return min(times) if times else None

    def _arm_timer(self) -> None:
        """Schedule the next timer tick."""
        if self._timer_task:
            self._timer_task.cancel()

        next_wake = self._get_next_wake_ms()
        if not next_wake or not self._running:
            return

        delay_ms = max(0, next_wake - _now_ms())
        delay_s = delay_ms / 1000

        async def tick():
            await asyncio.sleep(delay_s)
            if self._running:
                await self._on_timer()

        self._timer_task = asyncio.create_task(tick())

    async def _on_timer(self) -> None:
        """Handle timer tick - run due jobs."""
        self._load_store()
        if not self._store:
            return

        now = _now_ms()
        due_jobs = [
            j for j in self._store.jobs
            if j.enabled and j.state.next_run_at_ms and now >= j.state.next_run_at_ms
        ]

        for job in due_jobs:
            await self._execute_job(job)

        self._save_store()
        self._arm_timer()

    async def _execute_job(self, job: CronJob) -> None:
        """Execute a single job."""
        start_ms = _now_ms()
        logger.info("Cron: executing job '{}' ({})", job.name, job.id)

        try:
            response = None
            if self.on_job:
                response = await self.on_job(job)

            job.state.last_status = "ok"
            job.state.last_error = None
            logger.info("Cron: job '{}' completed", job.name)

        except Exception as e:
            job.state.last_status = "error"
            job.state.last_error = str(e)
            logger.error("Cron: job '{}' failed: {}", job.name, e)

        job.state.last_run_at_ms = start_ms
        job.updated_at_ms = _now_ms()

        # Handle one-shot jobs
        if job.schedule.kind == "at":
            if job.delete_after_run:
                self._store.jobs = [j for j in self._store.jobs if j.id != job.id]
            else:
                job.enabled = False
                job.state.next_run_at_ms = None
        else:
            # Compute next run
            job.state.next_run_at_ms = _compute_next_run(job.schedule, _now_ms())

    # ========== Public API ==========

    def list_jobs(self, include_disabled: bool = False) -> list[CronJob]:
        """List all jobs."""
        store = self._load_store()
        jobs = store.jobs if include_disabled else [j for j in store.jobs if j.enabled]
        return sorted(jobs, key=lambda j: j.state.next_run_at_ms or float('inf'))

    def add_job(
        self,
        name: str,
        schedule: CronSchedule,
        message: str,
        deliver: bool = False,
        channel: str | None = None,
        to: str | None = None,
        delete_after_run: bool = False,
    ) -> CronJob:
        """Add a new job."""
        store = self._load_store()
        _validate_schedule_for_add(schedule)
        now = _now_ms()

        job = CronJob(
            id=str(uuid.uuid4())[:8],
            name=name,
            enabled=True,
            schedule=schedule,
            payload=CronPayload(
                kind="agent_turn",
                message=message,
                deliver=deliver,
                channel=channel,
                to=to,
            ),
            state=CronJobState(next_run_at_ms=_compute_next_run(schedule, now)),
            created_at_ms=now,
            updated_at_ms=now,
            delete_after_run=delete_after_run,
        )

        store.jobs.append(job)
        self._save_store()
        self._arm_timer()

        logger.info("Cron: added job '{}' ({})", name, job.id)
        return job

    def remove_job(self, job_id: str) -> bool:
        """Remove a job by ID."""
        store = self._load_store()
        before = len(store.jobs)
        store.jobs = [j for j in store.jobs if j.id != job_id]
        removed = len(store.jobs) < before

        if removed:
            self._save_store()
            self._arm_timer()
            logger.info("Cron: removed job {}", job_id)

        return removed

    def enable_job(self, job_id: str, enabled: bool = True) -> CronJob | None:
        """Enable or disable a job."""
        store = self._load_store()
        for job in store.jobs:
            if job.id == job_id:
                job.enabled = enabled
                job.updated_at_ms = _now_ms()
                if enabled:
                    job.state.next_run_at_ms = _compute_next_run(job.schedule, _now_ms())
                else:
                    job.state.next_run_at_ms = None
                self._save_store()
                self._arm_timer()
                return job
        return None

    async def run_job(self, job_id: str, force: bool = False) -> bool:
        """Manually run a job."""
        store = self._load_store()
        for job in store.jobs:
            if job.id == job_id:
                if not force and not job.enabled:
                    return False
                await self._execute_job(job)
                self._save_store()
                self._arm_timer()
                return True
        return False

    def status(self) -> dict:
        """Get service status."""
        store = self._load_store()
        return {
            "enabled": self._running,
            "jobs": len(store.jobs),
            "next_wake_at_ms": self._get_next_wake_ms(),
        }

    # ========== Pack Management API ==========

    def list_packs(self) -> list[TaskPack]:
        """List all task packs."""
        store = self._load_store()
        return store.packs

    def get_active_pack(self) -> TaskPack | None:
        """Get the currently active pack."""
        store = self._load_store()
        if not store.active_pack_id:
            return None
        for pack in store.packs:
            if pack.id == store.active_pack_id:
                return pack
        return None

    def create_pack(self, name: str, display: str, description: str = "") -> TaskPack:
        """Create a new empty task pack."""
        store = self._load_store()
        now = _now_ms()

        # Check if name already exists
        for p in store.packs:
            if p.name == name:
                raise ValueError(f"Pack with name '{name}' already exists")

        pack = TaskPack(
            id=f"pack_{uuid.uuid4().hex[:6]}",
            name=name,
            display=display,
            description=description,
            created_at_ms=now,
            updated_at_ms=now,
        )

        store.packs.append(pack)
        self._save_store()

        logger.info("Cron: created pack '{}' ({})", name, pack.id)
        return pack

    def delete_pack(self, pack_id: str) -> bool:
        """Delete a pack. Only empty packs can be deleted."""
        store = self._load_store()

        for pack in store.packs:
            if pack.id == pack_id:
                if pack.job_ids:
                    raise ValueError(f"Cannot delete pack '{pack.name}': still has {len(pack.job_ids)} jobs")
                if store.active_pack_id == pack_id:
                    store.active_pack_id = None
                store.packs.remove(pack)
                self._save_store()
                logger.info("Cron: deleted pack {}", pack_id)
                return True

        return False

    def switch_pack(self, pack_id: str | None) -> tuple[bool, int]:
        """
        Switch to the specified pack.

        - pack_id=None: disable all jobs
        - pack_id=valid: disable all jobs, then enable jobs in this pack

        Returns (success, enabled_job_count).
        """
        store = self._load_store()
        now = _now_ms()

        # Validate pack exists if specified
        target_pack = None
        if pack_id:
            for pack in store.packs:
                if pack.id == pack_id:
                    target_pack = pack
                    break
            if not target_pack:
                return False, 0

        # 1. Disable all jobs
        for job in store.jobs:
            job.enabled = False
            job.state.next_run_at_ms = None

        enabled_count = 0

        # 2. If a pack is specified, enable its jobs
        if target_pack:
            for job_id in target_pack.job_ids:
                for job in store.jobs:
                    if job.id == job_id:
                        job.enabled = True
                        job.state.next_run_at_ms = _compute_next_run(job.schedule, now)
                        enabled_count += 1
                        break
            store.active_pack_id = pack_id
            logger.info("Cron: switched to pack '{}', enabled {} jobs", target_pack.name, enabled_count)
        else:
            store.active_pack_id = None
            logger.info("Cron: disabled all jobs (no active pack)")

        self._save_store()
        self._arm_timer()
        return True, enabled_count

    def add_job_to_pack(self, job_id: str, pack_id: str) -> bool:
        """Add a job to a pack."""
        store = self._load_store()

        # Find job
        job_exists = any(j.id == job_id for j in store.jobs)
        if not job_exists:
            return False

        # Find pack and add job
        for pack in store.packs:
            if pack.id == pack_id:
                if job_id not in pack.job_ids:
                    pack.job_ids.append(job_id)
                    pack.updated_at_ms = _now_ms()
                    self._save_store()
                    logger.info("Cron: added job {} to pack {}", job_id, pack.name)
                return True

        return False

    def remove_job_from_pack(self, job_id: str, pack_id: str) -> bool:
        """Remove a job from a pack."""
        store = self._load_store()

        for pack in store.packs:
            if pack.id == pack_id:
                if job_id in pack.job_ids:
                    pack.job_ids.remove(job_id)
                    pack.updated_at_ms = _now_ms()
                    self._save_store()
                    logger.info("Cron: removed job {} from pack {}", job_id, pack.name)
                return True

        return False

    def get_pack_by_name(self, name: str) -> TaskPack | None:
        """Get a pack by its internal name."""
        store = self._load_store()
        for pack in store.packs:
            if pack.name == name:
                return pack
        return None
