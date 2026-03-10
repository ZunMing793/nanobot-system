---
name: china-stock-analysis
description: "A股价值投资分析工具，提供股票筛选、个股深度分析、行业对比和估值计算功能。基于价值投资理论，支持 akshare（免费）和 tushare（需 token）双数据源，适合低频交易的普通投资者。"
always: true
allowed-tools:
  - Bash(python:*)
  - Read
---

## ⚠️ 执行前必读

**决定使用此 skill 后，必须先读取**：
`C:/Users/79345/.claude/skills/china-stock-analysis/GUIDE.md`

**禁止事项**：
- ❌ 不准偷懒不读取 skill 的其他详细文件
- ❌ 不准直接用 SKILL.md 中的精简格式给用户输出

**输出要求**：
- 输出开头必须列出：「已读取：SKILL.md、GUIDE.md」

## 触发场景

当用户请求以下操作时使用此 skill：
- 分析某只 A 股股票（基本面、估值、财务健康）
- 筛选符合条件的股票（低估值、高 ROE、高股息等）
- 对比多只股票或同行业公司
- 计算股票内在价值或安全边际
- 检测财务异常风险（应收账款、现金流背离等）
- 查看行业政策影响或股东结构分析

## 数据源说明

本 skill 与 **tushare-finance** 协同工作，自动选择数据源：
- 优先使用 tushare（如已配置 token，日线更稳定）
- 未配置则使用 akshare（免费，功能全面）

## 详细指南索引

完整内容请阅读：GUIDE.md

- 股票筛选流程与参数说明
- 个股深度分析（摘要/标准/深度三级）
- 行业对比分析
- 估值计算（DCF/DDM/相对估值）
- 财务异常检测
- A股特色分析（政策敏感度、股东结构）
- 错误处理与最佳实践
