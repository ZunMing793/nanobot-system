# China Stock Analysis 详细指南

本文档包含 A 股价值投资分析的完整操作流程。

---

## 1. 数据源协作

本 skill 与 **tushare-finance** 协同工作：

| Skill | 定位 | 数据源 | 说明 |
|-------|------|--------|------|
| **tushare-finance** | 数据获取 | Tushare Pro API | 220+ 接口，需注册获取 token |
| **china-stock-analysis** | 数据分析 | akshare / tushare | 本 skill，自动选择数据源 |

**自动选择逻辑**：
1. 检测 tushare-finance 是否已配置 token
2. 如已配置 → 优先使用 tushare（日线行情更稳定）
3. 如未配置 → 使用 akshare（免费）

```
用户请求分析股票
        ↓
china-stock-analysis
        ↓
检测 tushare-finance/config.json
        ↓
    存在 → 使用 tushare 获取数据
    不存在 → 使用 akshare 获取数据
        ↓
进行分析、估值、生成报告
```

---

## 2. 环境准备

### Python 环境要求

```bash
# 必需依赖
pip install akshare pandas numpy

# 可选依赖（如需使用 tushare 数据源）
pip install tushare
```

### 数据源配置

**方式1：使用 akshare（默认，免费）**
- 无需配置，直接可用

**方式2：使用 tushare（可选，日线行情稳定）**
1. 访问 https://tushare.pro 免费注册获取 token
2. 配置到 tushare-finance skill：
   ```bash
   # 编辑配置文件
   C:/Users/79345/.claude/skills/tushare-finance/config.json

   # 内容格式
   {"api_key": "你的token"}
   ```

### 检查数据源状态

```bash
python scripts/data_fetcher.py --status
```

输出示例：
```
数据源状态:
----------------------------------------
  akshare（免费）: ✅ 可用
  tushare（需要 token）: ✅ 已配置

当前使用: tushare（需要 token）
----------------------------------------
```

### 依赖检查

```bash
# 检查 akshare
python -c "import akshare; print('akshare OK')"

# 检查 tushare（可选）
python -c "import tushare; print('tushare OK')"
```

---

## 3. 核心模块

### 1. Stock Screener (股票筛选器)
筛选符合条件的股票

### 2. Financial Analyzer (财务分析器)
个股深度财务分析

### 3. Industry Comparator (行业对比)
同行业横向对比分析

### 4. Valuation Calculator (估值计算器)
内在价值测算与安全边际计算

---

## 4. Workflow 1: 股票筛选

### Step 1: 收集筛选条件

向用户询问筛选条件。提供以下选项供用户选择或自定义：

**估值指标：**
- PE (市盈率): 例如 PE < 15
- PB (市净率): 例如 PB < 2
- PS (市销率): 例如 PS < 3

**盈利能力：**
- ROE (净资产收益率): 例如 ROE > 15%
- ROA (总资产收益率): 例如 ROA > 8%
- 毛利率: 例如 > 30%
- 净利率: 例如 > 10%

**成长性：**
- 营收增长率: 例如 > 10%
- 净利润增长率: 例如 > 15%
- 连续增长年数: 例如 >= 3年

**股息：**
- 股息率: 例如 > 3%
- 连续分红年数: 例如 >= 5年

**财务安全：**
- 资产负债率: 例如 < 60%
- 流动比率: 例如 > 1.5
- 速动比率: 例如 > 1

**筛选范围：**
- 全A股
- 沪深300成分股
- 中证500成分股
- 创业板/科创板
- 用户自定义列表

### Step 2: 执行筛选

```bash
python scripts/stock_screener.py \
    --scope "hs300" \
    --pe-max 15 \
    --roe-min 15 \
    --debt-ratio-max 60 \
    --dividend-min 2 \
    --output screening_result.json
```

**参数说明：**
- `--scope`: 筛选范围 (all/hs300/zz500/cyb/kcb/custom:600519,000858,...)
- `--pe-max/--pe-min`: PE范围
- `--pb-max/--pb-min`: PB范围
- `--roe-min`: 最低ROE
- `--growth-min`: 最低增长率
- `--debt-ratio-max`: 最大资产负债率
- `--dividend-min`: 最低股息率
- `--output`: 输出文件路径

### Step 3: 展示结果

读取 `screening_result.json` 并以表格形式呈现：

| 代码 | 名称 | PE | PB | ROE | 股息率 | 评分 |
|------|------|----|----|-----|--------|------|
| 600519 | 贵州茅台 | 25.3 | 8.5 | 30.2% | 2.1% | 85 |

---

## 5. Workflow 2: 个股分析

### Step 1: 收集股票信息

询问用户：
1. 股票代码或名称
2. 分析深度级别：
   - **摘要级**：关键指标 + 投资结论（1页）
   - **标准级**：财务分析 + 估值 + 行业对比 + 风险提示
   - **深度级**：完整调研报告，包含历史数据追踪

### Step 2: 获取股票数据

```bash
python scripts/data_fetcher.py \
    --code "600519" \
    --data-type all \
    --years 5 \
    --output stock_data.json
```

**参数说明：**
- `--code`: 股票代码
- `--data-type`: 数据类型 (basic/financial/valuation/holder/all)
- `--years`: 获取多少年的历史数据
- `--output`: 输出文件

### Step 3: 运行财务分析

```bash
python scripts/financial_analyzer.py \
    --input stock_data.json \
    --level standard \
    --output analysis_result.json
```

### Step 4: 计算估值

```bash
python scripts/valuation_calculator.py \
    --input stock_data.json \
    --methods dcf,ddm,relative \
    --discount-rate 10 \
    --growth-rate 8 \
    --output valuation_result.json
```

**参数说明：**
- `--input`: 股票数据文件
- `--methods`: 估值方法 (dcf/ddm/relative/all)
- `--discount-rate`: 折现率(%)
- `--growth-rate`: 永续增长率(%)
- `--margin-of-safety`: 安全边际(%)
- `--output`: 输出文件

### Step 5: 生成报告

读取分析结果，参考 `templates/analysis_report.md` 模板生成中文分析报告。

报告结构（标准级）：
1. **公司概况**：基本信息、主营业务
2. **财务健康**：资产负债表分析
3. **盈利能力**：杜邦分析、利润率趋势
4. **成长性分析**：营收/利润增长趋势
5. **估值分析**：DCF/DDM/相对估值
6. **风险提示**：财务异常检测、股东减持
7. **投资结论**：综合评分、操作建议

---

## 6. Workflow 3: 行业对比

### Step 1: 收集对比目标

询问用户：
1. 目标股票代码（可多个）
2. 或者：行业分类 + 对比数量

### Step 2: 获取行业数据

```bash
python scripts/data_fetcher.py \
    --codes "600519,000858,002304" \
    --data-type comparison \
    --output industry_data.json
```

或按行业获取：
```bash
python scripts/data_fetcher.py \
    --industry "白酒" \
    --top 10 \
    --output industry_data.json
```

### Step 3: 生成对比

```bash
python scripts/financial_analyzer.py \
    --input industry_data.json \
    --mode comparison \
    --output comparison_result.json
```

### Step 4: 展示对比表

| 指标 | 贵州茅台 | 五粮液 | 洋河股份 | 行业均值 |
|------|----------|--------|----------|----------|
| PE | 25.3 | 18.2 | 15.6 | 22.4 |
| ROE | 30.2% | 22.5% | 20.1% | 18.5% |
| 毛利率 | 91.5% | 75.2% | 72.3% | 65.4% |
| 评分 | 85 | 78 | 75 | - |

---

## 7. Workflow 4: 估值计算

### Step 1: 收集估值参数

询问用户估值参数（或使用默认值）：

**DCF模型参数：**
- 折现率 (WACC): 默认10%
- 预测期: 默认5年
- 永续增长率: 默认3%

**DDM模型参数：**
- 要求回报率: 默认10%
- 股息增长率: 使用历史数据推算

**相对估值参数：**
- 对比基准: 行业均值 / 历史均值

### Step 2: 运行估值

```bash
python scripts/valuation_calculator.py \
    --code "600519" \
    --methods all \
    --discount-rate 10 \
    --terminal-growth 3 \
    --forecast-years 5 \
    --margin-of-safety 30 \
    --output valuation.json
```

### Step 3: 展示估值结果

| 估值方法 | 内在价值 | 当前价格 | 安全边际价格 | 结论 |
|----------|----------|----------|--------------|------|
| DCF | ¥2,150 | ¥1,680 | ¥1,505 | 低估 |
| DDM | ¥1,980 | ¥1,680 | ¥1,386 | 低估 |
| 相对估值 | ¥1,850 | ¥1,680 | ¥1,295 | 合理 |

---

## 8. 财务异常检测

在分析过程中自动检测以下异常信号：

### 检测项目

1. **应收账款异常**
   - 应收账款增速 > 营收增速 × 1.5
   - 应收账款周转天数大幅增加

2. **现金流背离**
   - 净利润持续增长但经营现金流下降
   - 现金收入比 < 80%

3. **存货异常**
   - 存货增速 > 营收增速 × 2
   - 存货周转天数大幅增加

4. **毛利率异常**
   - 毛利率波动 > 行业均值波动 × 2
   - 毛利率与同行严重偏离

5. **关联交易**
   - 关联交易占比过高（> 30%）

6. **股东减持**
   - 大股东近期减持公告
   - 高管集中减持

### 风险等级

- 🟢 **低风险**：无明显异常
- 🟡 **中风险**：1-2项轻微异常
- 🔴 **高风险**：多项异常或严重异常

---

## 9. A 股特色分析

### 政策敏感度

根据行业分类提供政策相关提示：
- 房地产：房住不炒政策
- 新能源：补贴政策变化
- 医药：集采政策影响
- 互联网：反垄断、数据安全

### 股东结构分析

1. 控股股东类型（国企/民企/外资）
2. 股权集中度
3. 近期增减持情况
4. 质押比例

---

## 10. 输出格式

### JSON 输出格式

所有脚本输出 JSON 格式，便于后续处理：

```json
{
  "code": "600519",
  "name": "贵州茅台",
  "analysis_date": "2025-01-25",
  "level": "standard",
  "summary": {
    "score": 85,
    "conclusion": "低估",
    "recommendation": "建议关注"
  },
  "financials": { ... },
  "valuation": { ... },
  "risks": [ ... ]
}
```

### Markdown 报告

生成结构化的中文 Markdown 报告，参考 `templates/analysis_report.md`。

---

## 11. 错误处理

### 网络错误
如果 akshare 数据获取失败，提示用户：
1. 检查网络连接
2. 稍后重试（可能是接口限流）
3. 尝试更换数据源

### 股票代码无效
提示用户检查股票代码是否正确，提供可能的匹配建议。

### 数据不完整
对于新上市股票或财务数据不完整的情况，说明数据限制并基于可用数据进行分析。

---

## 12. 数据源对比

| 功能 | akshare | tushare（免费账户） |
|------|---------|---------------------|
| 成本 | 完全免费 | 免费注册 |
| 稳定性 | ⚠️ 网络不稳定 | ✅ 稳定 |
| 日线行情 | ✅ | ✅ |
| 财务数据 | ✅ 全面 | ❌ 需积分 |
| 财务指标 | ✅ | ❌ 需积分 |
| 股东数据 | ✅ | ❌ 需积分 |

**互补策略**：
- 日线行情 → tushare（稳定）
- 财务数据 → akshare（功能全）
- akshare 失败时提示用户稍后重试

---

## 13. 注意事项

- 所有分析基于公开财务数据，不涉及任何内幕信息
- 估值模型的参数假设对结果影响较大，需向用户说明
- A股市场受政策影响较大，定量分析需结合定性判断
- 所有分析仅供参考，不构成投资建议
