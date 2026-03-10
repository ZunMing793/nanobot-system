# Find Skills 详细指南

本文档包含发现和安装 agent skills 的完整操作流程。

---

## 1. 两平台搜索策略

### Platform 1: skills.sh (官方)

```bash
npx skills find [query]
```
- 官方技能注册表
- 精选高质量技能
- 适用于：开发工具、官方集成

### Platform 2: ClawHub (社区)

```bash
npx clawhub@latest search [query]
npx clawhub@latest explore  # 浏览最新技能
```
- 更广泛的社区技能
- 更多通用工具
- 适用于：生产力、自动化、专业任务

**在线浏览：**
- https://skills.sh/
- https://clawhub.ai/

---

## 2. 帮助用户发现技能

### 场景 A：用户知道自己需要什么

**Step 1: 搜索技能**
```bash
# 在两个平台上搜索以获得最佳结果
npx skills find [query]
npx clawhub@latest search [query]
```

**Step 2: 展示选项**
向用户展示：
1. 技能名称和描述
2. 安装命令
3. 了解更多的链接

**Step 3: 获得批准后安装**

### 场景 B：用户不知道搜索什么

**Step 1: 查阅技能目录**

阅读技能目录参考文件以找到相关类别：
```
C:/Users/79345/.claude/skills/find-skills/references/skills-catalog.md
```

**Step 2: 提出澄清问题**
- "您想完成什么类型的任务？"
- "您是在处理文档、数据、网页搜索还是自动化？"

**Step 3: 根据类别推荐**

| 用户需求 | 推荐技能 |
|----------|----------|
| 处理文档 | `pdf`, `docx`, `xlsx`, `pptx` |
| 网页搜索 | `tavily-search`, `exa-web-search-free` |
| 金融数据 | `tushare-finance`, `stock-market-pro` |
| 浏览器自动化 | `agent-browser` |
| 视频编辑 | `ffmpeg-video-editor` |
| 邮件处理 | `email-management-expert` |

---

## 3. 常用技能类别

| 类别 | 搜索关键词 |
|------|-----------|
| Web 开发 | react, nextjs, typescript, css, tailwind |
| 测试 | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| 文档 | docs, readme, changelog, api-docs |
| 代码质量 | review, lint, refactor, best-practices |
| 设计 | ui, ux, design-system, accessibility |
| 生产力 | workflow, automation, git |
| 数据 | finance, stock, analysis, excel |

---

## 4. NanoBot 系统安装方法

**重要：NanoBot 使用共享技能目录！**

### 方法 1: ClawHub（推荐 - 支持 --workdir）

```bash
npx clawhub@latest install <slug> --workdir /home/NanoBot/shared
```

### 方法 2: skills.sh（需先 cd 到目录）

```bash
# skills CLI 不支持 --workdir，必须先 cd
cd /home/NanoBot/shared/skills
npx skills add <owner/repo@skill> -y
cd -  # 返回之前的目录
```

### 方法 3: 手动下载（网络失败时）

当 `git clone` 超时时，使用 GitHub API + wget 手动下载文件。

**Step 1: 列出技能目录内容**
```bash
# 检查技能中有哪些文件
curl -s "https://api.github.com/repos/<owner>/<repo>/contents/skills/<skill-name>" | jq -r ".[].name"
```

**Step 2: 创建技能目录结构**
```bash
mkdir -p C:/Users/79345/.claude/skills/<skill-name>/{scripts,references}
```

**Step 3: 下载文件**
```bash
# 下载 SKILL.md（必需）
wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/SKILL.md" \
  -O C:/Users/79345/.claude/skills/<skill-name>/SKILL.md

# 下载脚本（如有）
wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/scripts/script.py" \
  -O C:/Users/79345/.claude/skills/<skill-name>/scripts/script.py

# 下载参考文件（如有）
wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/references/ref.md" \
  -O C:/Users/79345/.claude/skills/<skill-name>/references/ref.md
```

**Step 4: 批量下载目录中的所有文件**
```bash
# 下载 scripts 目录中的所有文件
for f in $(curl -s "https://api.github.com/repos/<owner>/<repo>/contents/skills/<skill-name>/scripts" | jq -r ".[].name"); do
  wget "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<skill-name>/scripts/$f" \
    -O "C:/Users/79345/.claude/skills/<skill-name>/scripts/$f"
done
```

**常见错误类型和解决方案：**

| 错误 | 含义 | 解决方案 |
|------|------|----------|
| `Connection timed out` | 网络超时 | 使用 GitHub API + wget |
| `TLS connection was non-properly terminated` | TLS 中断 | 使用 GitHub API + wget |
| `Failed to connect to xxx port 443` | 端口被阻止 | 使用 GitHub API + wget |

**为什么 GitHub API 在 git clone 失败时仍能工作：**
- API 使用 HTTPS over 443 端口（与 git 相同）
- API 更稳定，不需要 git 协议
- 单文件下载比完整克隆更小

---

## 5. 常见错误避免

| 错误 | 原因 | 正确方式 |
|------|------|----------|
| `npx skills add xxx -g -y` | 全局安装，非共享 | `cd /home/NanoBot/shared/skills && npx skills add xxx -y` |
| `npx skills add xxx --workdir ...` | skills CLI 不支持 --workdir | 使用 ClawHub 或先 cd |
| `npx clawhub install xxx -g` | 错误参数 | `npx clawhub install xxx --workdir /home/NanoBot/shared` |

---

## 6. 安装后检查清单

安装新技能后，检查：

1. **allowed-tools** - 如果技能有脚本，确保 SKILL.md 有：
   ```yaml
   allowed-tools:
     - Bash(python:*)  # 用于 Python 脚本
     - Read
   ```

2. **API 配置** - 如果技能需要外部 API，创建 config.json：
   ```bash
   echo '{"api_key": "your_key"}' > C:/Users/79345/.claude/skills/<skill-name>/config.json
   ```

3. **重启 bots** 以加载新技能

---

## 7. 未找到技能时

1. 承认没有找到现有技能
2. 提供用通用能力帮助
3. 建议创建自定义技能：

```bash
npx skills init my-custom-skill
```

---

## 8. 参考文件

- **技能目录**: `references/skills-catalog.md` - 按类别组织的完整技能目录
