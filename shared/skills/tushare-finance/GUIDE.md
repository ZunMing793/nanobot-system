# Tushare 金融数据详细指南

本文档包含 Tushare 金融数据获取的完整使用说明。

---

## 1. Token 配置

### 1.1 询问用户

使用前确认：是否已配置 Tushare Token？

### 1.2 配置方式

编辑配置文件：`C:/Users/79345/.claude/skills/tushare-finance/config.json`

```json
{
  "api_key": "你的Tushare Token"
}
```

### 1.3 获取 Token

1. 访问 https://tushare.pro 免费注册
2. 登录后在「个人中心」获取 Token
3. 填入 config.json 的 api_key 字段

---

## 2. 验证依赖

检查 Python 环境：
```bash
python -c "import tushare, pandas; print('OK')"
```

如报错，安装依赖：
```bash
pip install tushare pandas
```

---

## 3. 常用接口速查

| 数据类型 | 接口方法 | 说明 |
|---------|---------|------|
| 股票列表 | `pro.stock_basic()` | 获取所有股票列表 |
| 日线行情 | `pro.daily()` | 获取日线行情数据 |
| 财务指标 | `pro.fina_indicator()` | 财务指标（ROE等） |
| 利润表 | `pro.income()` | 利润表数据 |
| 指数行情 | `pro.index_daily()` | 指数日线数据 |
| 基金净值 | `pro.fund_nav()` | 基金净值数据 |
| GDP数据 | `pro.gdp()` | 国内生产总值 |
| CPI数据 | `pro.cpi()` | 居民消费价格指数 |

**完整接口列表**：查看 `reference/README.md`

---

## 4. 数据获取流程

### 4.1 步骤

1. **查找接口**：根据需求在 `reference/README.md` 找到对应接口
2. **阅读文档**：查看 `reference/接口文档/[接口名].md` 了解参数
3. **编写代码**：
4. **返回结果**：DataFrame 格式

### 4.2 代码示例

```python
import tushare as ts

# 初始化（使用配置文件中的 Token）
pro = ts.pro_api()

# 调用接口
df = pro.daily(ts_code='000001.SZ', start_date='20241201', end_date='20241231')
```

---

## 5. 参数格式说明

| 参数类型 | 格式 | 示例 |
|----------|------|------|
| 日期 | YYYYMMDD | 20241231 |
| 股票代码 | ts_code 格式 | 000001.SZ, 600000.SH |
| 返回格式 | pandas DataFrame | - |

---

## 6. 接口文档参考

接口文档按类别组织（共 220+ 个接口）：

| 类别 | 接口数量 |
|------|----------|
| 股票数据 | 39 个 |
| 指数数据 | 18 个 |
| 基金数据 | 11 个 |
| 期货期权 | 16 个 |
| 宏观经济 | 10 个 |
| 港股美股 | 23 个 |
| 债券数据 | 16 个 |

**接口索引**：`reference/README.md`

---

## 7. 参考资源

- **Tushare 官方文档**：https://tushare.pro/document/2
- **API 测试工具**：https://tushare.pro/document/1
- **快速参考**：`QUICK_REFERENCE.md`
