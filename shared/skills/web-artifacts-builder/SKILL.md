---
name: web-artifacts-builder
description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
always: true
license: Complete terms in LICENSE.txt
---

# Web Artifacts Builder

使用 React + Tailwind CSS + shadcn/ui 构建复杂前端组件。

## 触发场景

- 需要复杂的前端组件（状态管理、路由）
- 需要使用 shadcn/ui 组件库
- 单文件HTML无法满足的需求

---

## ⚠️ 执行前必读

**决定使用此 skill 后，必须先读取**：
`C:/Users/79345/.claude/skills/web-artifacts-builder/GUIDE.md`

**禁止事项**：
- ❌ 不准偷懒不读取 skill 的其他详细文件
- ❌ 不准直接用 SKILL.md 中的精简格式给用户输出

**输出要求**：
- 输出开头必须列出：「已读取：SKILL.md、GUIDE.md」

---

## 技术栈

- React 18 + TypeScript + Vite
- Tailwind CSS 3.4.1
- shadcn/ui (40+组件)
- Parcel (打包)

---

## 快速流程

1. **初始化**: `bash scripts/init-artifact.sh <name>`
2. **开发**: 编辑生成的代码
3. **打包**: `bash scripts/bundle-artifact.sh`
4. **分享**: 展示 bundle.html 给用户

---

## 详细指南

完整开发流程和设计原则请阅读：GUIDE.md
