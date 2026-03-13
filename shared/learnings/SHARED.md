# 共享学习记录

> 本文件存储所有 Bot 共享的学习经验，任何 Bot 都可以读取和写入。

---

## 格式说明

```markdown
## [SHARED-YYYYMMDD-001] 简短标题

**适用**：所有 bot | **标签**：#通用

### 问题
通用问题描述

### 解决
通用解决方案

### 来源
bot-X 于 YYYY-MM-DD 发现

---
```

---

## 共享经验

## [SHARED-20260313-001] 时间敏感性检查

**适用**：所有 bot | **标签**：#定时任务 #时间 #提醒

### 问题
在处理定时任务、日程提醒等时间相关功能时，没有先确认当前时间，导致错误判断下一个任务触发时间。

### 解决
执行任何时间相关的计算或回答前，**必须先获取并确认当前时间**：
```python
from datetime import datetime
import zoneinfo

beijing = zoneinfo.ZoneInfo('Asia/Shanghai')
now = datetime.now(beijing)
print(f'当前时间: {now.strftime("%Y-%m-%d %H:%M:%S")}')
```

关键原则：
1. 永远不要假设或猜测当前时间
2. 涉及"下一个任务"、"还有多久"等表述时，必须基于实际时间计算
3. 注意时区问题，统一使用北京时间（Asia/Shanghai）

### 来源
Claude Code 于 2026-03-13 发现

---
