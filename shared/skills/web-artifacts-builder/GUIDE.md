# Web Artifacts Builder 详细指南

本文档包含构建复杂前端HTML组件的完整操作流程。

---

## 1. 技术栈

- **React 18** + TypeScript
- **Vite** (开发服务器)
- **Parcel** (打包)
- **Tailwind CSS** 3.4.1
- **shadcn/ui** (40+组件预装)
- **Radix UI** 依赖

---

## 2. 开发流程

### Step 1: 初始化项目

```bash
bash scripts/init-artifact.sh <project-name>
cd <project-name>
```

初始化后的项目包含：
- ✅ React + TypeScript (via Vite)
- ✅ Tailwind CSS + shadcn/ui 主题系统
- ✅ 路径别名 (`@/`) 已配置
- ✅ 40+ shadcn/ui 组件预装
- ✅ Parcel 打包配置

### Step 2: 开发组件

编辑生成的文件，使用 shadcn/ui 组件构建界面。

**常用 shadcn/ui 组件**：
- Button, Card, Dialog, Dropdown
- Form, Input, Select, Table
- Tabs, Toast, Tooltip

**参考文档**: https://ui.shadcn.com/docs/components

### Step 3: 打包为单文件HTML

```bash
bash scripts/bundle-artifact.sh
```

生成 `bundle.html` - 包含所有 JS、CSS 的自包含文件。

### Step 4: 分享给用户

将打包好的 HTML 文件分享给用户查看。

---

## 3. 设计原则

**避免"AI风格"**：
- ❌ 过度居中布局
- ❌ 紫色渐变
- ❌ 统一圆角
- ❌ Inter字体

**推荐做法**：
- ✅ 有意的不对称布局
- ✅ 个性化的配色方案
- ✅ 多样化的圆角和间距
- ✅ 有特色的字体选择

---

## 4. 测试（可选）

打包后可使用 Playwright/Puppeteer 测试，但建议先展示给用户，有问题再测试。

---

## 5. 常见问题

### Q: 什么时候使用这个skill？
A: 当需要复杂的前端组件（状态管理、路由、shadcn/ui）时使用。简单单文件HTML不需要。

### Q: Node版本要求？
A: Node 18+，脚本会自动检测并锁定Vite版本。
