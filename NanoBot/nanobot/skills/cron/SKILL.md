---
name: cron
description: Schedule reminders and recurring tasks with task pack support.
---

# Cron

Use the `cron` tool to schedule reminders or recurring tasks, and manage task packs.

## Three Modes

1. **Reminder** - message is sent directly to user
2. **Task** - message is a task description, agent executes and sends result
3. **One-time** - runs once at a specific time, then auto-deletes

## Task Packs (任务包)

Task packs allow grouping jobs and switching between different scenarios. Each bot instance has its own packs - they are NOT shared.

### Default Packs

Two default packs are auto-created:
- `lab_competition` - 实验室备赛学习
- `holiday_home` - 假期在家娱乐

### Pack Operations

List all packs:
```
cron(action="pack_list")
```

Switch to a pack (disables all jobs, enables jobs in selected pack):
```
cron(action="pack_switch", pack_name="lab_competition")
```

Disable all jobs (no active pack):
```
cron(action="pack_switch")
```

Add job to a pack when creating:
```
cron(action="add", message="开始学习", cron_expr="0 9 * * *", pack_name="lab_competition")
```

Create a new pack:
```
cron(action="pack_create", pack_name="work_mode", pack_display="工作模式", pack_description="工作时间提醒")
```

Delete an empty pack:
```
cron(action="pack_delete", pack_name="work_mode")
```

## Examples

Fixed reminder:
```
cron(action="add", message="Time to take a break!", every_seconds=1200)
```

Dynamic task (agent executes each time):
```
cron(action="add", message="Check HKUDS/nanobot GitHub stars and report", every_seconds=600)
```

One-time scheduled task (compute ISO datetime from current time):
```
cron(action="add", message="Remind me about the meeting", at="<ISO datetime>")
```

Timezone-aware cron:
```
cron(action="add", message="Morning standup", cron_expr="0 9 * * 1-5", tz="America/Vancouver")
```

Add job to a pack:
```
cron(action="add", message="休息一下", every_seconds=3600, pack_name="lab_competition")
```

List/remove:
```
cron(action="list")
cron(action="remove", job_id="abc123")
```

## Pack Workflow Example

```
# 1. View available packs
cron(action="pack_list")
# Output:
# 任务包列表:
# - [ ] lab_competition (实验室备赛学习) - 0 个任务
# - [ ] holiday_home (假期在家娱乐) - 0 个任务

# 2. Add tasks to a pack
cron(action="add", message="开始学习", cron_expr="0 9 * * *", pack_name="lab_competition")
cron(action="add", message="休息一下", every_seconds=3600, pack_name="lab_competition")

# 3. Switch to the pack
cron(action="pack_switch", pack_name="lab_competition")
# Output: 已切换到「实验室备赛学习」，启用 2 个任务

# 4. Check status
cron(action="pack_list")
# Output:
# 任务包列表:
# - [●] lab_competition (实验室备赛学习) - 2 个任务 [当前激活]
# - [ ] holiday_home (假期在家娱乐) - 0 个任务
```

## Time Expressions

| User says | Parameters |
|-----------|------------|
| every 20 minutes | every_seconds: 1200 |
| every hour | every_seconds: 3600 |
| every day at 8am | cron_expr: "0 8 * * *" |
| weekdays at 5pm | cron_expr: "0 17 * * 1-5" |
| 9am Vancouver time daily | cron_expr: "0 9 * * *", tz: "America/Vancouver" |
| at a specific time | at: ISO datetime string (compute from current time) |

## Timezone

Use `tz` with `cron_expr` to schedule in a specific IANA timezone. Without `tz`, the server's local timezone is used.
