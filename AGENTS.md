# Repository Guidelines

## 协作约定
- 本仓库默认使用中文进行说明、评审、文档与协作沟通;仅在接口字段、第三方协议或用户明确要求时使用英文。
- 修改前先确认影响范围,优先做小而聚焦的变更,避免顺手修复无关问题。

## 项目结构与模块组织
- `NanoBot/nanobot/` 是主 Python 包,按功能划分为 `agent/`、`channels/`、`providers/`、`cli/`、`skills/`、`utils/` 等目录。
- `NanoBot/tests/` 存放 Python 自动化测试;新增功能应尽量补充对应测试。
- `NanoBot/bridge/` 是 TypeScript WhatsApp 网桥,源码在 `src/`,编译输出到 `dist/`。
- `scripts/` 提供仓库级脚本,如 `bot_manager.ps1`、`bot_manager.sh`、`selfcheck_multibot.py`。
- `bot1_core/` 到 `bot5_media/` 为各 Bot 的运行工作区,包含 `config.json`、`logs/`、`memory/`、`workspace/`,不应承载共享业务代码。
- `shared/` 存放复用技能和参考资料。

## 构建、测试与开发命令
- `cd NanoBot && pip install -e .[dev]`:安装主包及开发依赖。
- `cd NanoBot && pytest`:运行测试套件。
- `cd NanoBot && ruff check .`:执行代码风格与导入检查。
- `cd NanoBot && python -m nanobot onboard`:初始化本地工作区。
- `cd NanoBot && python -m nanobot gateway`:启动主网关。
- `cd NanoBot/bridge && npm install && npm run build`:安装并编译桥接模块。
- `python scripts/selfcheck_multibot.py`:检查多 Bot 配置是否可用。

## 代码风格与测试要求
- Python 目标版本为 3.11+,使用 4 空格缩进,遵循 Ruff 100 字符行宽限制。
- 命名采用:函数/模块 `snake_case`、类 `PascalCase`、常量 `UPPER_CASE`。
- TypeScript 源码仅维护在 `NanoBot/bridge/src/`,`dist/` 视为生成产物。
- 测试使用 `pytest`,文件命名为 `test_*.py`;桥接改动至少运行一次 `npm run build`。

## 提交、安全与 PR 要求
- 提交信息建议使用简短祈使句,如 `fix: validate provider config`,一次提交只解决一个主题。
- PR 需说明改动目的、验证步骤、关联问题;涉及 CLI、日志或渠道行为变更时附示例输出更佳。
- 严禁提交 `config.json`、`logs/`、`memory/`、`workspace/` 中的密钥、令牌或个人数据;修改认证、Provider 或渠道集成前先查看 `NanoBot/SECURITY.md`。
