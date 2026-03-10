---
name: tushare-finance
description: 获取中国金融市场数据（A股、港股、美股、基金、期货、债券）。支持220+个Tushare Pro接口：股票行情、财务报表、宏观经济指标。当用户请求股价数据、财务分析、指数行情、GDP/CPI等宏观数据时使用。
always: true
allowed-tools:
  - Bash(python:*)
  - Read
---

# Tushare 金融数据

通过 Tushare Pro API 获取中国金融市场数据，支持 220+ 个数据接口。

## 触发场景

- 用户请求股价数据、股票行情
- 用户需要财务分析、财务报表
- 用户需要指数行情数据
- 用户需要 GDP/CPI 等宏观经济指标
- 用户需要基金、期货、债券数据

---

## ⚠️ 执行前必读

**决定使用此 skill 后，必须先读取**：
`C:/Users/79345/.claude/skills/tushare-finance/GUIDE.md`

**禁止事项**：
- ❌ 不准偷懒不读取 skill 的其他详细文件
- ❌ 不准直接用 SKILL.md 中的精简格式给用户输出
- ❌ 这是撒谎行为，会导致数据获取失败

**输出要求**：
- 输出开头必须列出：「已读取：SKILL.md、GUIDE.md」

---

## 详细指南

完整使用能力需要读取 `GUIDE.md`，包含：
- Token 配置方法
- 依赖验证
- 常用接口速查表
- 数据获取流程
- 参数格式说明
- 接口文档参考
