# Tushare API å¿«éåè?
æ¬ææ¡£æä¾æå¸¸ç¨ç?Tushare API æ¥å£åä»£ç ç¤ºä¾ã?
**ä½è?*: [StanleyChanH](https://github.com/StanleyChanH)

## è¡ç¥¨æ°æ®

### è·åè¡ç¥¨åè¡¨
```python
import tushare as ts
pro = ts.pro_api()

# è·åæææ­£å¸¸ä¸å¸çè¡ç¥¨
df = pro.stock_basic(list_status='L')

# ç­éç¹å®äº¤ææ
df_sz = pro.stock_basic(exchange='SZSE')  # æ·±äº¤æ
df_sh = pro.stock_basic(exchange='SSE')   # ä¸äº¤æ
```

### è·åæ¥çº¿è¡æ
```python
# ååªè¡ç¥¨
df = pro.daily(ts_code='000001.SZ', start_date='20241201', end_date='20241231')

# å¤åªè¡ç¥¨
df = pro.daily(ts_code='000001.SZ,600000.SH', start_date='20241201', end_date='20241231')

# ææ¥ææè¡ç¥?df = pro.daily(trade_date='20241231')
```

### è·åè´¢å¡æ°æ®
```python
# å©æ¶¦è¡?df = pro.income(ts_code='600000.SH', start_date='20240101', end_date='20241231')

# èµäº§è´åºè¡¨
df = pro.balancesheet(ts_code='600000.SH', start_date='20240101', end_date='20241231')

# ç°éæµéè¡?df = pro.cashflow(ts_code='600000.SH', start_date='20240101', end_date='20241231')

# è´¢å¡ææ 
df = pro.fina_indicator(ts_code='600000.SH', start_date='20240101', end_date='20241231')
```

## ææ°æ°æ®

### è·åææ°åè¡¨
```python
df = pro.index_basic(market='SSE')  # ä¸äº¤æææ°
df = pro.index_basic(market='SZSE') # æ·±äº¤æææ°
```

### è·åææ°è¡æ
```python
# ä¸è¯ææ°
df = pro.index_daily(ts_code='000001.SH', start_date='20241201', end_date='20241231')

# æ·±è¯ææ
df = pro.index_daily(ts_code='399001.SZ', start_date='20241201', end_date='20241231')
```

## åºéæ°æ®

### è·ååºéåè¡¨
```python
df = pro.fund_basic(market='E')  # åºååºé
df = pro.fund_basic(market='O')  # åºå¤åºé
```

### è·ååºéåå?```python
df = pro.fund_nav(ts_code='000001.OF', start_date='20241201', end_date='20241231')
```

## å®è§ç»æµ

### GDP æ°æ®
```python
df = pro.gdp(start_q='2020011', end_q='2024044')
```

### CPI æ°æ®
```python
df = pro.cpi(start_date='20240101', end_date='20241231')
```

### PMI æ°æ®
```python
df = pro.pmi(start_date='20240101', end_date='20241231')
```

### å©çæ°æ®
```python
# Shibor
df = pro.shibor(start_date='20241201', end_date='20241231')

# LPR
df = pro.lpr(start_date='20241201', end_date='20241231')
```

## æ¸¯è¡ç¾è¡

### æ¸¯è¡æ°æ®
```python
# æ¸¯è¡åè¡¨
df = pro.hk_basic()

# æ¸¯è¡è¡æ
df = pro.hk_daily(ts_code='00700.HK', start_date='20241201', end_date='20241231')
```

### ç¾è¡æ°æ®
```python
# ç¾è¡åè¡¨
df = pro.us_basic()

# ç¾è¡è¡æ
df = pro.us_daily(ts_code='AAPL', start_date='20241201', end_date='20241231')
```

## å¸¸è§æ¥è¯¢æ¨¡å¼

### ææ¥æèå´æ¥è¯?```python
df = pro.daily(
    ts_code='000001.SZ',
    start_date='20240101',  # YYYYMMDD
    end_date='20241231'
)
```

### æäº¤ææ¥æ¥è¯¢
```python
df = pro.daily(trade_date='20241231')
```

### è·åææ°æ°æ?```python
# åè·åæè¿çäº¤ææ?import datetime
today = datetime.datetime.now().strftime('%Y%m%d')
df = pro.daily(trade_date=today)
```

## æ°æ®å¤çæå·?
### æ°æ®æ¸æ´
```python
# å»é¤åçæ°æ®
df = df[df['vol'] > 0]

# æåº
df = df.sort_values('trade_date')

# éç½®ç´¢å¼
df = df.reset_index(drop=True)
```

### æ°æ®ä¿å­
```python
# ä¿å­å?CSV
df.to_csv('data.csv', index=False)

# ä¿å­å?Excel
df.to_excel('data.xlsx', index=False)
```

## éè¯¯å¤ç

```python
import tushare as ts

try:
    pro = ts.pro_api('your_token')
    df = pro.daily(ts_code='000001.SZ', start_date='20241201', end_date='20241231')
    print(df.head())
except ts.errors.TushareException as e:
    print(f"Tushare API éè¯¯: {e}")
except Exception as e:
    print(f"éè¯¯: {e}")
```

## æ§è½ä¼å

### æ¹éè·å
```python
# ä¸æ¬¡è·åå¤åªè¡ç¥?stock_codes = ['000001.SZ', '600000.SH', '000002.SZ']
df = pro.daily(ts_code=','.join(stock_codes), start_date='20241201', end_date='20241231')
```

### æ§å¶è¯·æ±é¢ç
```python
import time

for stock in stock_codes:
    df = pro.daily(ts_code=stock, start_date='20241201', end_date='20241231')
    time.sleep(0.3)  # é¿åè¶é
```

## å¸¸ç¨å­æ®µè¯´æ

### æ¥çº¿è¡æå­æ®µ
- `trade_date`: äº¤ææ¥æ
- `ts_code`: è¡ç¥¨ä»£ç 
- `open`: å¼çä»·
- `high`: æé«ä»·
- `low`: æä½ä»·
- `close`: æ¶çä»?- `vol`: æäº¤éï¼æï¼
- `amount`: æäº¤é¢ï¼ååï¼?
### è´¢å¡ææ å­æ®µ
- `end_date`: æ¥åæ?- `roe`: åèµäº§æ¶çç?- `net_profit_margin`: éå®åå©ç
- `gross_margin`: éå®æ¯å©ç
- `debt_to_assets`: èµäº§è´åºç

## æ´å¤æ¥å£

å®æ´æ¥å£åè¡¨åè¯¦ç»è¯´æè¯·æ¥çï¼?- [æ¥å£ææ¡£ç´¢å¼](docs/README.md)
- [Tushare å®æ¹ææ¡£](https://tushare.pro/document/2)
