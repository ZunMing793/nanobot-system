"""Cron types."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class CronSchedule:
    """Schedule definition for a cron job."""
    kind: Literal["at", "every", "cron"]
    # For "at": timestamp in ms
    at_ms: int | None = None
    # For "every": interval in ms
    every_ms: int | None = None
    # For "cron": cron expression (e.g. "0 9 * * *")
    expr: str | None = None
    # Timezone for cron expressions
    tz: str | None = None


@dataclass
class CronPayload:
    """What to do when the job runs."""
    kind: Literal["system_event", "agent_turn"] = "agent_turn"
    message: str = ""
    # Deliver response to channel
    deliver: bool = False
    channel: str | None = None  # e.g. "whatsapp"
    to: str | None = None  # e.g. phone number


@dataclass
class CronJobState:
    """Runtime state of a job."""
    next_run_at_ms: int | None = None
    last_run_at_ms: int | None = None
    last_status: Literal["ok", "error", "skipped"] | None = None
    last_error: str | None = None


@dataclass
class CronJob:
    """A scheduled job."""
    id: str
    name: str
    enabled: bool = True
    schedule: CronSchedule = field(default_factory=lambda: CronSchedule(kind="every"))
    payload: CronPayload = field(default_factory=CronPayload)
    state: CronJobState = field(default_factory=CronJobState)
    created_at_ms: int = 0
    updated_at_ms: int = 0
    delete_after_run: bool = False


@dataclass
class TaskPack:
    """A pack of cron jobs for easy switching between scenarios."""
    id: str
    name: str                              # Internal name (e.g. "work_mode")
    display: str                           # Display name (e.g. "工作模式")
    description: str = ""                  # Description
    job_ids: list[str] = field(default_factory=list)  # Job IDs in this pack
    created_at_ms: int = 0
    updated_at_ms: int = 0


@dataclass
class CronStore:
    """Persistent store for cron jobs."""
    version: int = 2                       # Upgraded to v2 for packs support
    jobs: list[CronJob] = field(default_factory=list)
    packs: list[TaskPack] = field(default_factory=list)
    active_pack_id: str | None = None      # Currently active pack ID
