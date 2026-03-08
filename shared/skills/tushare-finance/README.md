# Tushare Finance Skill

[![Version](https://img.shields.io/badge/version-2.0.6-blue.svg)](https://github.com/StanleyChanH/Tushare-Finance-Skill-for-Claude-Code)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-Available-purple.svg)](https://clawhub.com)

è·åä¸­å½éèå¸åºæ°æ®ç?OpenClaw Skillï¼æ¯æ?**220+ ä¸?Tushare Pro æ¥å£**ã?
## â?ç¹æ?
- ð **å¼ç®±å³ç?* - ä¸é®å®è£ï¼æ éå¤æéç½®
- ð **å¨é¢è¦ç** - Aè¡ãæ¸¯è¡ãç¾è¡ãåºéãæè´§ãåºå¸
- ð§ **å¤ç§æ¹å¼** - Python APIãå½ä»¤è¡å·¥å·ãæ¹éå¯¼å?- ð **å®æ¶æ°æ®** - æ¯æè¡ç¥¨è¡æãè´¢å¡æ¥è¡¨ãå®è§ç»æµ?- ð **OpenClaw éæ** - æ ç¼éæå°èªå¨åå·¥ä½æµ?- ð **å®æ´ææ¡£** - 220+ æ¥å£å®æ´ç´¢å¼åä½¿ç¨ç¤ºä¾?
## ð¥ å®è£

### æ¹æ³ 1ï¼éè¿ ClawHubï¼æ¨èï¼

```bash
clawhub install tushare-finance
```

### æ¹æ³ 2ï¼æå¨å®è£?
```bash
git clone https://github.com/StanleyChanH/Tushare-Finance-Skill-for-Claude-Code.git
cd Tushare-Finance-Skill-for-Claude-Code
pip install -r requirements.txt
```

## ð éç½®

### è·å Tushare Token

1. è®¿é® [Tushare Pro](https://tushare.pro) æ³¨åè´¦å·
2. å¨ä¸ªäººä¸­å¿è·å?Token
3. éç½®ç¯å¢åéï¼?
```bash
export TUSHARE_TOKEN="your_token_here"

# ææ·»å å° ~/.bashrc
echo 'export TUSHARE_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

## ð å¿«éå¼å§?
### Python API

```python
from scripts.api_client import TushareAPI

# åå§åå®¢æ·ç«¯
api = TushareAPI()

# æ¥è¯¢è¡ç¥¨æ¥çº¿è¡æ
df = api.get_stock_daily("000001.SZ", "2024-01-01", "2024-12-31")
print(df.head())

# æ¥è¯¢å¬å¸åºæ¬ä¿¡æ¯
info = api.get_stock_info("000001.SZ")
print(info)

# æ¹éæ¥è¯¢å¤åªè¡ç¥¨
stocks = ["000001.SZ", "000002.SZ", "600000.SH"]
data = api.batch_query(stocks, "2024-01-01", "2024-12-31")
```

### å½ä»¤è¡å·¥å?
```bash
# æ¥è¯¢ååªè¡ç¥¨
python scripts/quick_query.py --stock 000001.SZ --start 2024-01-01 --end 2024-12-31

# æ¹éæ¥è¯¢
python scripts/quick_query.py --file stocks.txt --start 2024-01-01 --output result.csv

# å¯¼åº Excel
python scripts/batch_export.py --stock 000001.SZ --start 2024-01-01 --end 2024-12-31 --format excel
```

## ð æ¯æçæ°æ®ç±»å?
### è¡ç¥¨æ°æ®ï¼?9 ä¸ªæ¥å£ï¼

| æ¥å£ | è¯´æ | ç¤ºä¾ |
|------|------|------|
| `daily` | æ¥çº¿è¡æ | `api.get_stock_daily()` |
| `stock_basic` | è¡ç¥¨åè¡¨ | `api.get_stock_list()` |
| `fina_indicator` | è´¢å¡ææ  | `api.get_financial_indicator()` |
| `income` | å©æ¶¦è¡?| `api.get_income_statement()` |
| `balancesheet` | èµäº§è´åºè¡¨ | `api.get_balance_sheet()` |

### ææ°æ°æ®ï¼?8 ä¸ªæ¥å£ï¼

| æ¥å£ | è¯´æ | ç¤ºä¾ |
|------|------|------|
| `index_daily` | ææ°æ¥çº¿ | `api.get_index_daily()` |
| `index_weight` | ææ°æå | `api.get_index_weight()` |
| `index_basic` | ææ°åè¡¨ | `api.get_index_list()` |

### åºéæ°æ®ï¼?1 ä¸ªæ¥å£ï¼

| æ¥å£ | è¯´æ | ç¤ºä¾ |
|------|------|------|
| `fund_nav` | åºéåå?| `api.get_fund_nav()` |
| `fund_basic` | åºéåè¡¨ | `api.get_fund_list()` |

### æè´§æ°æ®ï¼?6 ä¸ªæ¥å£ï¼

| æ¥å£ | è¯´æ | ç¤ºä¾ |
|------|------|------|
| `futures_daily` | æè´§æ¥çº¿ | `api.get_futures_daily()` |

### å®è§æ°æ®ï¼?0 ä¸ªæ¥å£ï¼

| æ¥å£ | è¯´æ | ç¤ºä¾ |
|------|------|------|
| `gdp` | GDPæ°æ® | `api.get_gdp()` |
| `cpi` | CPIæ°æ® | `api.get_cpi()` |
| `pmi` | PMIæ°æ® | `api.get_pmi()` |

### æ¸¯è¡ç¾è¡ï¼?3 ä¸ªæ¥å£ï¼

| æ¥å£ | è¯´æ | ç¤ºä¾ |
|------|------|------|
| `hk_daily` | æ¸¯è¡æ¥çº¿ | `api.get_hk_daily()` |
| `us_daily` | ç¾è¡æ¥çº¿ | `api.get_us_daily()` |

**å®æ´æ¥å£åè¡¨**ï¼æ¥ç?[æ¥å£ææ¡£ç´¢å¼](reference/README.md)

## ð API ææ¡£

### TushareAPI ç±?
#### `__init__(token=None)`

åå§å?API å®¢æ·ç«?
**åæ°**ï¼?- `token` (str, optional): Tushare Tokenï¼é»è®¤ä»ç¯å¢åéè¯»å

#### `get_stock_daily(ts_code, start_date, end_date)`

æ¥è¯¢è¡ç¥¨æ¥çº¿è¡æ

**åæ°**ï¼?- `ts_code` (str): è¡ç¥¨ä»£ç ï¼å¦ "000001.SZ"ï¼?- `start_date` (str): å¼å§æ¥æï¼å¦?"2024-01-01"ï¼?- `end_date` (str): ç»ææ¥æï¼å¦ "2024-12-31"ï¼?
**è¿å**ï¼?- `pd.DataFrame`: æ¥çº¿æ°æ®

**ç¤ºä¾**ï¼?```python
df = api.get_stock_daily("000001.SZ", "2024-01-01", "2024-12-31")
```

#### `batch_query(ts_codes, start_date, end_date)`

æ¹éæ¥è¯¢å¤åªè¡ç¥¨

**åæ°**ï¼?- `ts_codes` (list): è¡ç¥¨ä»£ç åè¡¨
- `start_date` (str): å¼å§æ¥æ?- `end_date` (str): ç»ææ¥æ

**è¿å**ï¼?- `dict`: {è¡ç¥¨ä»£ç : DataFrame}

**ç¤ºä¾**ï¼?```python
stocks = ["000001.SZ", "000002.SZ", "600000.SH"]
data = api.batch_query(stocks, "2024-01-01", "2024-12-31")
```

**æ´å¤ API è¯·åè?*ï¼[docs/api_reference.md](docs/api_reference.md)

## ð§ ä½¿ç¨ç¤ºä¾

### ç¤ºä¾ 1ï¼è¡ç¥¨æ°æ®åæ?
```python
from scripts.api_client import TushareAPI

api = TushareAPI()

# æ¥è¯¢è¡ç¥¨æ°æ®
df = api.get_stock_daily("000001.SZ", "2024-01-01", "2024-12-31")

# è®¡ç®æ¶çç?df['return'] = df['close'].pct_change()
df['cum_return'] = (1 + df['return']).cumprod()

print(df[['trade_date', 'close', 'return', 'cum_return']].tail())
```

### ç¤ºä¾ 2ï¼æ¹éå¯¼å?
```python
from scripts.api_client import TushareAPI

api = TushareAPI()

# æ¹éæ¥è¯¢æ²ªæ·±300æå
stocks = api.get_index_weight("000300.SH", "2024-12-31")
stock_codes = stocks['con_code'].tolist()

# æ¹éè·åæ°æ®
for code in stock_codes[:10]:  # å?0å?    df = api.get_stock_daily(code, "2024-01-01", "2024-12-31")
    df.to_csv(f"./data/{code}.csv", index=False)
```

### ç¤ºä¾ 3ï¼è´¢å¡åæ?
```python
# æ¥è¯¢è´¢å¡ææ 
fina = api.get_financial_indicator("000001.SZ", "2024-01-01", "2024-12-31")

# ç­éå³é®ææ ?key_metrics = ['roe', 'roa', 'debt_to_assets', 'current_ratio']
print(fina[['ts_code', 'end_date'] + key_metrics].head())
```

**æ´å¤ç¤ºä¾**ï¼[docs/examples.md](docs/examples.md)

## âï¸ éç½®éé¡¹

### ç¯å¢åé

```bash
# Tushare Tokenï¼å¿éï¼?export TUSHARE_TOKEN="your_token_here"

# æ°æ®ç¼å­ï¼å¯éï¼
export TUSHARE_CACHE_DIR="~/.tushare_cache"

# æ¥å¿çº§å«ï¼å¯éï¼
export TUSHARE_LOG_LEVEL="INFO"
```

### éç½®æä»¶

ç¼è¾ `config/config.yaml`ï¼?
```yaml
api:
  # Tokenï¼ä¼åçº§ä½äºç¯å¢åéï¼?  token: "your_token_here"

  # è¯·æ±è¶æ¶ï¼ç§ï¼?  timeout: 30

  # éè¯æ¬¡æ°
  retry: 3

cache:
  # æ¯å¦å¯ç¨ç¼å­
  enabled: true

  # ç¼å­ç®å½
  dir: ~/.tushare_cache

  # ç¼å­æææï¼ç§ï¼
  ttl: 3600

logging:
  # æ¥å¿çº§å«
  level: INFO

  # æ¥å¿æä»¶
  file: logs/tushare.log
```

## ð§ª æµè¯

```bash
# è¿è¡æææµè¯?python -m pytest tests/

# è¿è¡ç¹å®æµè¯
python -m pytest tests/test_api.py

# æ¥çæµè¯è¦çç?python -m pytest --cov=scripts tests/
```

## ð¤ è´¡ç®

æ¬¢è¿è´¡ç®ä»£ç ãæ¥åé®é¢ææåºå»ºè®®ï¼?
### å¼åç¯å¢?
```bash
git clone https://github.com/StanleyChanH/Tushare-Finance-Skill-for-Claude-Code.git
cd Tushare-Finance-Skill-for-Claude-Code
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m pytest tests/
```

## ð è®¸å¯è¯?
Apache License 2.0

## ð è´è°¢

- [Tushare Pro](https://tushare.pro) - æä¾é«è´¨ééèæ°æ?API
- [OpenClaw](https://github.com/openclaw/openclaw) - OpenClaw æ¡æ¶

## ð ç¸å³èµæº

- **GitHub**ï¼https://github.com/StanleyChanH/Tushare-Finance-Skill-for-Claude-Code
- **ClawHub**ï¼https://clawhub.com/skill/tushare-finance
- **Tushare ææ¡£**ï¼https://tushare.pro/document/2
- **OpenClaw ææ¡£**ï¼https://docs.openclaw.ai

## ð æ´æ°æ¥å¿

### v2.0.0 (2026-02-14)
- â?æ·»å å®æ´ç?Python API å®¢æ·ç«?- â?æ·»å å½ä»¤è¡å·¥å?- â?æ·»å æ¹éå¯¼åºåè½
- ð å®å API ææ¡£åä½¿ç¨ç¤ºä¾?- ð§ª æ·»å èªå¨åæµè¯?- ð éç½® GitHub Actions èªå¨åå¸

### v1.0.0 (2026-01-10)
- ð åå§çæ¬åå¸
- ð æ¯æ 220+ Tushare Pro æ¥å£
