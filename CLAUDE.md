# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NanoBot_System 是一个多实例 AI 助手系统,基于 [nanobot](https://github.com/HKUDS/nanobot) 框架构建。系统同时运行多个专业化 Bot 实例,共享技能、知识和学习成果。

## Development Commands

```bash
# 安装开发依赖
cd NanoBot && pip install -e .[dev]

# 运行测试
cd NanoBot && pytest

# 运行单个测试
cd NanoBot && pytest tests/test_loop_save_turn.py -v

# 代码风格检查
cd NanoBot && ruff check .

# 初始化工作区
cd NanoBot && python -m nanobot onboard

# 启动网关服务
cd NanoBot && python -m nanobot gateway

# 编译 WhatsApp 桥接模块
cd NanoBot/bridge && npm install && npm run build

# 检查多 Bot 配置
python scripts/selfcheck_multibot.py
```

## Architecture

### Core Agent (`NanoBot/nanobot/agent/`)

- **loop.py**: 核心处理引擎,负责消息接收、上下文构建、LLM 调用、工具执行
- **context.py**: 提示词构建器,处理历史消息、内存、技能加载
- **memory.py**: 持久化内存存储
- **memory_learning.py**: 记忆学习与整合
- **skills.py**: 技能加载器
- **subagent.py**: 后台任务执行管理
- **tools/**: 内置工具(filesystem, shell, web, cron, spawn, mcp, message)

### Providers (`NanoBot/nanobot/providers/`)

- **registry.py**: LLM 提供者注册表,定义所有支持的 Provider 及其元数据
- **litellm_provider.py**: LiteLLM 包装器,处理大多数 Provider
- **base.py**: 提供者基类

添加新 Provider 的步骤:
1. 在 `registry.py` 的 `PROVIDERS` 中添加 `ProviderSpec`
2. 在 `config/schema.py` 的 `ProvidersConfig` 中添加字段

### Channels (`NanoBot/nanobot/channels/`)

支持的聊天平台:Telegram, Discord, WhatsApp, Feishu, DingTalk, Slack, Email, QQ, Matrix, Mochat

- **base.py**: 通道基类
- **manager.py**: 通道管理器

### Message Bus (`NanoBot/nanobot/bus/`)

- **events.py**: 定义 `InboundMessage` 和 `OutboundMessage` 数据类
- **queue.py**: 消息队列实现

### Configuration (`NanoBot/nanobot/config/`)

- **schema.py**: Pydantic 配置模型,支持 camelCase 和 snake_case

## Multi-Bot Deployment

```
NanoBot_System/
├── NanoBot/           # 主 Python 包
├── bot1_core/         # 核心 Bot 实例
├── bot2_health/       # 健康助手
├── bot3_finance/      # 金融助手
├── bot4_emotion/      # 情感助手
├── bot5_media/        # 媒体助手
├── shared/            # 共享资源
│   ├── config/        # 共享配置(如 models.json)
│   ├── skills/        # 共享技能
│   ├── knowledge/     # 共享知识库
│   ├── learnings/     # 共享学习成果
│   └── memory/        # 共享记忆
└── scripts/           # 运维脚本
```

每个 Bot 实例包含:
- `config.json`: 该实例的配置
- `logs/`: 运行日志
- `workspace/`: 工作空间(MEMORY.md, HEARTBEAT.md, 会话文件)

## Skills System

技能存放在 `NanoBot/nanobot/skills/` 和 `shared/skills/` 中。每个技能是一个目录,包含 `SKILL.md` 文件:

```markdown
---
name: skill-name
description: 技能描述
---

# 技能指令

[给 Agent 的详细指令]
```

内置技能:github, weather, summarize, tmux, clawhub, skill-creator, cron

## Key Patterns

### Provider Detection

Provider 注册表根据以下优先级检测:
1. 显式 `provider` 配置
2. API Key 前缀(如 `sk-or-` → OpenRouter)
3. API Base URL 关键字
4. 模型名称关键字

### Tool Execution

所有工具继承自 `agent/tools/base.py` 的基类,通过 `ToolRegistry` 注册。Agent 循环在 LLM 返回工具调用时执行相应工具。

### Session Management

会话由 `session/manager.py` 管理,使用 `{channel}:{chat_id}` 作为唯一标识。

## Testing

测试文件位于 `NanoBot/tests/`,使用 pytest。关键测试文件:

- `test_loop_save_turn.py`: Agent 循环保存测试
- `test_context_*.py`: 上下文构建测试
- `test_*_provider.py`: 各 Provider 测试
- `test_*_channel.py`: 各通道测试

## Security Notes

- 配置文件权限应设为 0600
- `allowFrom` 列表控制通道访问权限
- Shell 工具有危险命令过滤
- 文件操作有路径遍历保护
- 生产环境应启用 `restrictToWorkspace`
