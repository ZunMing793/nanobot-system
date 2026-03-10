from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import selfcheck_multibot
import smoke_test_bot


@dataclass
class CheckMessage:
    level: str
    text: str


@dataclass
class DoctorReport:
    ok: bool = True
    messages: list[CheckMessage] = field(default_factory=list)

    def fail(self, text: str) -> None:
        self.ok = False
        self.messages.append(CheckMessage("FAIL", text))

    def warn(self, text: str) -> None:
        self.messages.append(CheckMessage("WARN", text))

    def info(self, text: str) -> None:
        self.messages.append(CheckMessage("INFO", text))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _workspace_dir(bot_id: str) -> Path:
    return _repo_root() / bot_id / "workspace"


def _check_json_file(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True, "ok"
    except Exception as exc:
        return False, f"invalid json: {exc}"


def _heartbeat_state(path: Path) -> str:
    if not path.exists():
        return "missing"
    text = path.read_text(encoding="utf-8").strip()
    markers = (
        "# Heartbeat Tasks",
        "## Active Tasks",
        "## Completed",
        "<!-- Add your periodic tasks below this line -->",
        "<!-- Move completed tasks here or delete them -->",
    )
    compact = text
    for marker in markers:
        compact = compact.replace(marker, "")
    return "configured" if compact.strip() else "empty"


def _local_ab_state() -> str:
    ab_path = _repo_root() / "shared" / "bin" / "ab"
    if not ab_path.exists():
        return "missing"
    return "present"


def _run_ssh(remote_host: str, ssh_key: str, remote_cmd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "ssh",
            "-i",
            ssh_key,
            remote_host,
            remote_cmd,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def _remote_checks(remote_host: str, ssh_key: str) -> list[CheckMessage]:
    messages: list[CheckMessage] = []
    command = (
        "set -e; "
        "echo 'SERVICES'; systemctl is-active "
        "nanobot@bot1_core nanobot@bot2_health nanobot@bot3_finance "
        "nanobot@bot4_emotion nanobot@bot5_media; "
        "echo 'SWAP'; swapon --show --noheadings || true; "
        "echo 'AB'; bash -lc 'export PATH=\"/home/NanoBot/shared/bin:$PATH\"; "
        "command -v ab >/dev/null && echo ab:ok || echo ab:missing; "
        "command -v agent-browser >/dev/null && echo agent-browser:ok || echo agent-browser:missing'; "
        "echo 'DOCTOR'; test -f /home/NanoBot/scripts/doctor.py && echo doctor:ok || echo doctor:missing; "
        "echo 'SMOKE'; test -f /home/NanoBot/scripts/smoke_test_bot.py && echo smoke:ok || echo smoke:missing"
    )
    result = _run_ssh(remote_host, ssh_key, command)
    if result.returncode != 0:
        messages.append(CheckMessage("FAIL", f"remote check failed: {result.stderr.strip() or result.stdout.strip()}"))
        return messages

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    service_lines: list[str] = []
    section = ""
    for line in lines:
        if line in {"SERVICES", "SWAP", "AB", "DOCTOR", "SMOKE"}:
            section = line
            continue
        if section == "SERVICES":
            service_lines.append(line)
        elif section == "SWAP":
            if not line:
                continue
            messages.append(CheckMessage("INFO", f"remote swap: {line}"))
        elif section == "AB":
            level = "INFO" if line.endswith(":ok") else "WARN"
            messages.append(CheckMessage(level, f"remote {line}"))
        elif section == "DOCTOR":
            level = "INFO" if line.endswith(":ok") else "WARN"
            messages.append(CheckMessage(level, f"remote {line}"))
        elif section == "SMOKE":
            level = "INFO" if line.endswith(":ok") else "WARN"
            messages.append(CheckMessage(level, f"remote {line}"))

    if service_lines:
        if all(line == "active" for line in service_lines):
            messages.append(CheckMessage("INFO", "remote services: all active"))
        else:
            messages.append(CheckMessage("FAIL", f"remote services: {' '.join(service_lines)}"))
    return messages


async def run_doctor(*, model_ping: bool = False, remote_host: str | None = None, ssh_key: str | None = None) -> DoctorReport:
    report = DoctorReport()
    repo = _repo_root()

    shared_missing = selfcheck_multibot._check_shared_layout(repo)
    if shared_missing:
        report.fail(f"shared layout missing: {', '.join(shared_missing)}")
    else:
        report.info("shared layout: ok")

    ab_state = _local_ab_state()
    if ab_state == "present":
        report.info("local agent-browser wrapper: present")
    else:
        report.warn("local agent-browser wrapper: missing")

    smoke_targets = selfcheck_multibot.BOTS
    for bot_id in smoke_targets:
        check = selfcheck_multibot._check_bot(bot_id, repo)
        if check.ok:
            report.info(f"{bot_id} config/layout: ok")
        else:
            report.fail(check.render())

        workspace = _workspace_dir(bot_id)
        heartbeat_path = workspace / "HEARTBEAT.md"
        report.info(f"{bot_id} heartbeat: {_heartbeat_state(heartbeat_path)}")

        cron_path = workspace / "cron" / "jobs.json"
        cron_ok, cron_state = _check_json_file(cron_path)
        if cron_path.exists():
            if cron_ok:
                report.info(f"{bot_id} cron store: ok")
            else:
                report.fail(f"{bot_id} cron store: {cron_state}")
        else:
            report.info(f"{bot_id} cron store: absent")

        smoke = await smoke_test_bot.run_smoke_test(
            bot_id,
            ping_model=model_ping and bot_id == "bot1_core",
        )
        if smoke.ok:
            report.info(
                f"{bot_id} smoke: ok (skills={smoke.facts.get('skills_available', '-')}, "
                f"tools={len(smoke.facts.get('tools', []))})"
            )
        else:
            report.fail(f"{bot_id} smoke: failed")
        for warning in smoke.warnings:
            report.warn(f"{bot_id} {warning.code.lower()}: {warning.message}")

    if remote_host and ssh_key:
        report.messages.extend(_remote_checks(remote_host, ssh_key))
        if any(message.level == "FAIL" for message in report.messages):
            report.ok = False

    return report


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified NanoBot doctor entrypoint.")
    parser.add_argument("--model-ping", action="store_true", help="Run a real model ping for bot1_core.")
    parser.add_argument("--remote-host", help="Optional SSH target, e.g. ubuntu@1.2.3.4")
    parser.add_argument("--ssh-key", help="Optional SSH private key path for remote checks")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = asyncio.run(
        run_doctor(
            model_ping=args.model_ping,
            remote_host=args.remote_host,
            ssh_key=args.ssh_key,
        )
    )
    print("NanoBot Doctor")
    for item in report.messages:
        print(f"[{item.level}] {item.text}")
    print(f"SUMMARY={'PASS' if report.ok else 'FAIL'}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
