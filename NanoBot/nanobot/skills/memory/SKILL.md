---
name: memory
description: Two-layer memory system with grep-based recall.
always: true
---

# Memory

## Structure

- `self/SELF.md` — Bot 自我认知，只存 bot 自身定位和职责。
- `user/PROFILE.md` — 用户画像，存稳定事实、偏好、长期目标。
- `memory/MEMORY.md` — 动态记忆，存持续有效的重要背景、任务上下文、跨会话事实。
- `memory/HISTORY.md` — 追加式历史流水。不会直接加载进上下文，需检索使用；每条以 `[YYYY-MM-DD HH:MM]` 开头。
- `.learnings/LEARNINGS.md` — 私有经验。

## Search Past Events

```bash
grep -i "keyword" memory/HISTORY.md
```

Use the `exec` tool to run grep. Combine patterns: `grep -iE "meeting|deadline" memory/HISTORY.md`

## When to Update Each File

优先按职责写入：

- `user/PROFILE.md`：用户偏好、身份、长期目标。
- `memory/MEMORY.md`：项目背景、当前约束、重要上下文。
- `.learnings/LEARNINGS.md`：可复用的方法、踩坑结论、最佳实践。

## Auto-consolidation

Old conversations are automatically summarized and appended to `memory/HISTORY.md` when the session grows large. Long-term facts are extracted to `memory/MEMORY.md`. You don't need to manage this.
