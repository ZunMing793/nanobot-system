#!/usr/bin/env python3
"""
A股数据获取模块
支持双数据源：akshare（免费）和 tushare（需要 token）

依赖: pip install akshare pandas
可选: pip install tushare  # 如需使用 tushare 数据源

协作关系：
- 本脚本：获取数据供 china-stock-analysis 分析使用
- tushare-finance skill：如已配置 token，可调用其数据接口
"""

import argparse
import json
import sys
import time
import os
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from functools import wraps
from pathlib import Path

# 默认数据源策略：
# - 日线行情：tushare（稳定）
# - 财务数据：akshare（功能全）
# - 基本信息：akshare（tushare 有频率限制）
DEFAULT_DATA_SOURCE = "auto"

# tushare-finance skill 的配置路径
TUSHARE_CONFIG_PATH = Path("/home/NanoBot/shared/skills/tushare-finance/config.json")

# 数据源状态
DATA_SOURCES = {
    "akshare": {"available": False, "name": "akshare（免费，功能全）"},
    "tushare": {"available": False, "name": "tushare（稳定，权限有限）"}
}

# 数据类型与数据源映射
DATA_SOURCE_PRIORITY = {
    "price": ["tushare", "akshare"],      # 日线行情：tushare 优先（稳定）
    "financial": ["akshare", "tushare"],  # 财务数据：akshare 优先（功能全）
    "basic": ["akshare", "tushare"],      # 基本信息：akshare 优先（tushare有频率限制）
    "holder": ["akshare"],                # 股东数据：只有 akshare
    "dividend": ["akshare"],              # 分红数据：只有 akshare
}

# 尝试导入 akshare
try:
    import akshare as ak
    import pandas as pd
    DATA_SOURCES["akshare"]["available"] = True
except ImportError:
    print("警告: akshare 未安装，请运行: pip install akshare pandas")

# 尝试导入 tushare
try:
    import tushare as ts
    DATA_SOURCES["tushare"]["available"] = True
except ImportError:
    pass  # tushare 是可选的


def check_tushare_config() -> bool:
    """检查 tushare-finance skill 的配置是否存在且有效"""
    if TUSHARE_CONFIG_PATH.exists():
        try:
            with open(TUSHARE_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                token = config.get('api_key', '').strip() or config.get('token', '').strip()
                return bool(token)
        except Exception:
            pass
    return False


def get_available_data_source() -> str:
    """获取默认数据源（向后兼容）"""
    if DATA_SOURCES["akshare"]["available"]:
        return "akshare"
    if DATA_SOURCES["tushare"]["available"] and check_tushare_config():
        return "tushare"
    return "none"


def get_best_data_source(data_type: str) -> str:
    """根据数据类型获取最佳数据源

    Args:
        data_type: 数据类型 (price/financial/basic/holder/dividend)

    Returns:
        最佳数据源名称
    """
    priorities = DATA_SOURCE_PRIORITY.get(data_type, ["akshare", "tushare"])

    for source in priorities:
        if source == "tushare":
            if DATA_SOURCES["tushare"]["available"] and check_tushare_config():
                return "tushare"
        elif source == "akshare":
            if DATA_SOURCES["akshare"]["available"]:
                return "akshare"

    # 降级：返回任何可用的
    if DATA_SOURCES["akshare"]["available"]:
        return "akshare"
    if DATA_SOURCES["tushare"]["available"] and check_tushare_config():
        return "tushare"
    return "none"


def init_tushare_api():
    """初始化 tushare API"""
    if not DATA_SOURCES["tushare"]["available"]:
        return None

    # 从 tushare-finance skill 的 config.json 读取
    token = None
    if TUSHARE_CONFIG_PATH.exists():
        try:
            with open(TUSHARE_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                token = config.get('api_key', '').strip() or config.get('token', '').strip()
        except Exception:
            pass

    if token:
        try:
            pro = ts.pro_api(token)
            # 使用 daily 接口测试连接（免费账户可用）
            pro.daily(ts_code='000001.SZ', start_date='20260101', end_date='20260101')
            return pro
        except Exception as e:
            print(f"tushare 初始化失败: {e}")
            return None
    return None


# tushare API 实例（延迟初始化）
_tushare_pro = None


def get_tushare_pro():
    """获取 tushare pro 实例（延迟初始化）"""
    global _tushare_pro
    if _tushare_pro is None:
        _tushare_pro = init_tushare_api()
    return _tushare_pro


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """网络请求重试装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # 递增等待
            return {"error": f"重试{max_retries}次后失败: {str(last_error)}"}
        return wrapper
    return decorator


def safe_float(value) -> Optional[float]:
    """安全转换为浮点数"""
    if value is None or value == '' or value == '--':
        return None
    try:
        if pd.isna(value):
            return None
        if isinstance(value, str):
            value = value.replace('%', '').replace(',', '').replace('亿', '')
        return float(value)
    except (ValueError, TypeError):
        return None


def get_cache_path(code: str, data_type: str) -> str:
    """获取缓存文件路径"""
    cache_dir = os.path.join(os.path.dirname(__file__), '.cache')
    os.makedirs(cache_dir, exist_ok=True)
    today = datetime.now().strftime('%Y%m%d')
    return os.path.join(cache_dir, f"{code}_{data_type}_{today}.json")


def load_cache(code: str, data_type: str) -> Optional[dict]:
    """加载缓存数据（当天有效）"""
    cache_path = get_cache_path(code, data_type)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def save_cache(code: str, data_type: str, data: dict):
    """保存缓存数据"""
    cache_path = get_cache_path(code, data_type)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, default=str)
    except IOError:
        pass


# ========== akshare 数据获取函数 ==========

@retry_on_failure(max_retries=2, delay=1.0)
def get_stock_info_akshare(code: str) -> dict:
    """使用 akshare 获取股票基本信息"""
    try:
        df = ak.stock_individual_info_em(symbol=code)
        info = {}
        for _, row in df.iterrows():
            info[row['item']] = row['value']
        return {
            "code": code,
            "name": info.get("股票简称", ""),
            "industry": info.get("行业", ""),
            "market_cap": safe_float(info.get("总市值")),
            "float_cap": safe_float(info.get("流通市值")),
            "total_shares": safe_float(info.get("总股本")),
            "float_shares": safe_float(info.get("流通股")),
            "pe_ttm": safe_float(info.get("市盈率(动态)")),
            "pb": safe_float(info.get("市净率")),
            "listing_date": info.get("上市时间", ""),
            "data_source": "akshare"
        }
    except Exception as e:
        return {"code": code, "error": str(e)}


@retry_on_failure(max_retries=2, delay=1.0)
def get_financial_data_akshare(code: str, years: int = 3) -> dict:
    """使用 akshare 获取财务数据"""
    max_records = min(years * 4, 12)
    result = {
        "balance_sheet": [],
        "income_statement": [],
        "cash_flow": []
    }

    fetch_configs = [
        ("balance_sheet", ak.stock_balance_sheet_by_report_em),
        ("income_statement", ak.stock_profit_sheet_by_report_em),
        ("cash_flow", ak.stock_cash_flow_sheet_by_report_em),
    ]

    for key, fetch_func in fetch_configs:
        try:
            df = fetch_func(symbol=code)
            if df is not None and not df.empty:
                result[key] = df.head(max_records).to_dict(orient='records')
        except Exception as e:
            result[f"{key}_error"] = str(e)

    return result


# ========== tushare 数据获取函数 ==========

def get_stock_info_tushare(code: str) -> dict:
    """使用 tushare 获取股票基本信息"""
    pro = get_tushare_pro()
    if not pro:
        return {"code": code, "error": "tushare 未配置或不可用"}

    try:
        # 转换代码格式：600519 -> 600519.SH
        ts_code = convert_to_ts_code(code)

        # 获取基本信息
        df_basic = pro.stock_basic(ts_code=ts_code, fields='ts_code,name,industry,market,list_date')
        # 获取实时行情
        df_daily = pro.daily_basic(ts_code=ts_code, fields='ts_code,pe_ttm,pb,total_mv,circ_mv')

        if df_basic is None or df_basic.empty:
            return {"code": code, "error": "未找到股票信息"}

        basic = df_basic.iloc[0].to_dict()
        daily = df_daily.iloc[0].to_dict() if df_daily is not None and not df_daily.empty else {}

        return {
            "code": code,
            "name": basic.get("name", ""),
            "industry": basic.get("industry", ""),
            "market": basic.get("market", ""),
            "market_cap": safe_float(daily.get("total_mv")),
            "float_cap": safe_float(daily.get("circ_mv")),
            "pe_ttm": safe_float(daily.get("pe_ttm")),
            "pb": safe_float(daily.get("pb")),
            "listing_date": basic.get("list_date", ""),
            "data_source": "tushare"
        }
    except Exception as e:
        return {"code": code, "error": str(e)}


def get_financial_data_tushare(code: str, years: int = 3) -> dict:
    """使用 tushare 获取财务数据"""
    pro = get_tushare_pro()
    if not pro:
        return {"error": "tushare 未配置或不可用"}

    try:
        ts_code = convert_to_ts_code(code)
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y%m%d')

        result = {
            "balance_sheet": [],
            "income_statement": [],
            "cash_flow": []
        }

        # 资产负债表
        try:
            df_bs = pro.balancesheet(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df_bs is not None and not df_bs.empty:
                result["balance_sheet"] = df_bs.head(years*4).to_dict(orient='records')
        except Exception as e:
            result["balance_sheet_error"] = str(e)

        # 利润表
        try:
            df_inc = pro.income(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df_inc is not None and not df_inc.empty:
                result["income_statement"] = df_inc.head(years*4).to_dict(orient='records')
        except Exception as e:
            result["income_statement_error"] = str(e)

        # 现金流量表
        try:
            df_cf = pro.cashflow(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df_cf is not None and not df_cf.empty:
                result["cash_flow"] = df_cf.head(years*4).to_dict(orient='records')
        except Exception as e:
            result["cash_flow_error"] = str(e)

        return result
    except Exception as e:
        return {"error": str(e)}


def get_financial_indicators_tushare(code: str, limit: int = 8) -> list:
    """使用 tushare 获取财务指标"""
    pro = get_tushare_pro()
    if not pro:
        return []

    try:
        ts_code = convert_to_ts_code(code)
        df = pro.fina_indicator(ts_code=ts_code)
        if df is not None and not df.empty:
            return df.head(limit).to_dict(orient='records')
    except Exception:
        pass
    return []


def convert_to_ts_code(code: str) -> str:
    """转换股票代码格式：600519 -> 600519.SH"""
    code = code.strip()
    if '.' in code:
        return code

    # 根据代码开头判断交易所
    if code.startswith(('6', '9', '5')):
        return f"{code}.SH"
    elif code.startswith(('0', '3', '2')):
        return f"{code}.SZ"
    elif code.startswith(('4', '8')):
        return f"{code}.BJ"
    return f"{code}.SH"


# ========== 统一接口（自动选择数据源） ==========

def get_stock_info(code: str, data_source: str = None) -> dict:
    """获取股票基本信息（自动选择数据源）"""
    if data_source is None:
        data_source = get_available_data_source()

    if data_source == "tushare":
        result = get_stock_info_tushare(code)
        if "error" not in result:
            return result
        # 失败时降级到 akshare
        if DATA_SOURCES["akshare"]["available"]:
            print(f"tushare 获取失败，降级到 akshare...")
            data_source = "akshare"
        else:
            return {"code": code, "error": f"tushare 失败且 akshare 不可用: {result.get('error', '')}"}

    if data_source == "akshare":
        if not DATA_SOURCES["akshare"]["available"]:
            return {"code": code, "error": "akshare 未安装，请运行: pip install akshare"}
        return get_stock_info_akshare(code)

    return {"code": code, "error": "没有可用的数据源"}


def get_financial_data(code: str, years: int = 3, data_source: str = None) -> dict:
    """获取财务数据（自动选择数据源）"""
    if data_source is None:
        data_source = get_available_data_source()

    if data_source == "tushare":
        result = get_financial_data_tushare(code, years)
        if "error" not in result:
            return result
        # 失败时降级到 akshare
        if DATA_SOURCES["akshare"]["available"]:
            print(f"tushare 获取失败，降级到 akshare...")
            data_source = "akshare"
        else:
            return {"error": f"tushare 失败且 akshare 不可用: {result.get('error', '')}"}

    if data_source == "akshare":
        if not DATA_SOURCES["akshare"]["available"]:
            return {"error": "akshare 未安装，请运行: pip install akshare"}
        return get_financial_data_akshare(code, years)

    return {"error": "没有可用的数据源"}


def get_financial_indicators(code: str, limit: int = 8, data_source: str = None) -> list:
    """获取财务指标（自动选择数据源）"""
    if data_source is None:
        data_source = get_available_data_source()

    if data_source == "tushare":
        result = get_financial_indicators_tushare(code, limit)
        if result:
            return result
        if DATA_SOURCES["akshare"]["available"]:
            print(f"tushare 获取失败，降级到 akshare...")
        else:
            return []

    # akshare
    if not DATA_SOURCES["akshare"]["available"]:
        return []

    apis = [ak.stock_financial_abstract, ak.stock_financial_analysis_indicator]
    for api in apis:
        try:
            df = api(symbol=code)
            if df is not None and not df.empty:
                return df.head(limit).to_dict(orient='records')
        except Exception:
            continue
    return []


def get_valuation_data(code: str) -> dict:
    """获取估值数据"""
    result = {}

    try:
        df = ak.stock_a_ttm_lyr(symbol=code)
        if df is None or df.empty:
            return result

        latest = df.iloc[-1].to_dict()
        result["latest"] = latest
        result["history_count"] = len(df)

        for col in ['pe_ttm', 'pb']:
            val = latest.get(col)
            if val and not pd.isna(val):
                result[f"{col}_percentile"] = (df[col].dropna() < val).mean() * 100

    except Exception as e:
        result["error"] = str(e)
        result["note"] = "估值历史数据获取失败，将使用基本信息中的估值"

    return result


def get_price_data_tushare(code: str, days: int = 60) -> dict:
    """使用 tushare 获取价格数据（稳定）"""
    pro = get_tushare_pro()
    if not pro:
        return {"error": "tushare 不可用"}

    try:
        ts_code = convert_to_ts_code(code)
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is not None and not df.empty:
            # 按日期排序
            df = df.sort_values('trade_date')
            latest = df.iloc[-1]
            return {
                "latest_price": safe_float(latest['close']),
                "latest_date": str(latest['trade_date']),
                "price_change_pct": None,  # tushare daily 不直接提供涨跌幅
                "volume": safe_float(latest['vol']),
                "turnover": safe_float(latest['amount']),
                "high_60d": safe_float(df['high'].max()),
                "low_60d": safe_float(df['low'].min()),
                "avg_volume_20d": safe_float(df.tail(20)['vol'].mean()),
                "price_data": df.tail(30).to_dict(orient='records'),
                "data_source": "tushare"
            }
        return {}
    except Exception as e:
        return {"error": str(e)}


@retry_on_failure(max_retries=2, delay=1.0)
def get_holder_data(code: str) -> dict:
    """获取股东信息"""
    result = {}

    try:
        df_top10 = ak.stock_gdfx_top_10_em(symbol=code)
        if df_top10 is not None and not df_top10.empty:
            result["top_10_holders"] = df_top10.head(10).to_dict(orient='records')
    except Exception as e:
        result["top_10_holders_error"] = str(e)

    try:
        df_holder_num = ak.stock_zh_a_gdhs(symbol=code)
        if df_holder_num is not None and not df_holder_num.empty:
            result["holder_count_history"] = df_holder_num.head(10).to_dict(orient='records')
    except Exception as e:
        result["holder_count_error"] = str(e)

    return result


@retry_on_failure(max_retries=2, delay=1.0)
def get_dividend_data(code: str) -> dict:
    """获取分红数据"""
    apis = [
        lambda c: ak.stock_dividend_cninfo(symbol=c),
        lambda c: ak.stock_history_dividend_detail(symbol=c, indicator="分红"),
    ]

    for api in apis:
        try:
            df = api(code)
            if df is not None and not df.empty:
                return {
                    "dividend_history": df.to_dict(orient='records'),
                    "dividend_count": len(df)
                }
        except Exception:
            continue

    return {"dividend_history": [], "dividend_count": 0}


def get_price_data(code: str, days: int = 60, data_source: str = None) -> dict:
    """获取价格数据（tushare 优先，失败降级到 akshare）"""
    if data_source is None:
        data_source = get_best_data_source("price")

    # 优先使用 tushare（稳定）
    if data_source == "tushare" or DATA_SOURCES["tushare"]["available"]:
        result = get_price_data_tushare(code, days)
        if "error" not in result and result:
            return result
        print(f"    tushare 价格数据获取失败，尝试 akshare...")

    # 降级到 akshare
    return get_price_data_akshare(code, days)


@retry_on_failure(max_retries=2, delay=1.0)
def get_price_data_akshare(code: str, days: int = 60) -> dict:
    """使用 akshare 获取价格数据"""
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

        df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                start_date=start_date, end_date=end_date, adjust="qfq")
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            return {
                "latest_price": safe_float(latest['收盘']),
                "latest_date": str(latest['日期']),
                "price_change_pct": safe_float(latest['涨跌幅']),
                "volume": safe_float(latest['成交量']),
                "turnover": safe_float(latest['成交额']),
                "high_60d": safe_float(df['最高'].max()),
                "low_60d": safe_float(df['最低'].min()),
                "avg_volume_20d": safe_float(df.tail(20)['成交量'].mean()),
                "price_data": df.tail(30).to_dict(orient='records'),
                "data_source": "akshare"
            }
        return {}
    except Exception as e:
        return {"error": str(e)}


@retry_on_failure(max_retries=2, delay=1.0)
def get_index_constituents(index_name: str) -> list:
    """获取指数成分股"""
    index_map = {
        "hs300": "000300",
        "zz500": "000905",
        "zz1000": "000852",
        "cyb": "399006",
        "kcb": "000688"
    }

    index_code = index_map.get(index_name)
    if not index_code:
        return []

    try:
        df = ak.index_stock_cons(symbol=index_code)
        if df is not None and not df.empty:
            return df['品种代码'].tolist()
        return []
    except Exception as e:
        print(f"获取指数成分股失败: {e}")
        return []


def get_all_a_stocks() -> list:
    """获取全部A股代码"""
    try:
        df = ak.stock_zh_a_spot_em()
        if df is not None and not df.empty:
            return df['代码'].tolist()
        return []
    except Exception as e:
        print(f"获取全部A股失败: {e}")
        return []


def fetch_stock_data(code: str, data_type: str = "all", years: int = 3,
                     use_cache: bool = True, data_source: str = None) -> dict:
    """获取单只股票的数据

    Args:
        code: 股票代码
        data_type: 数据类型 (all/basic/financial/valuation/holder)
        years: 获取多少年的历史数据
        use_cache: 是否使用缓存
        data_source: 数据源 (auto/akshare/tushare)，默认自动选择最佳
    """
    # 尝试加载缓存
    if use_cache:
        cached = load_cache(code, data_type)
        if cached:
            print(f"使用缓存数据: {code}")
            return cached

    result = {
        "code": code,
        "fetch_time": datetime.now().isoformat(),
        "data_type": data_type,
        "data_sources_used": []
    }

    print(f"正在获取 {code} 的数据...")

    # 基本信息：akshare 优先（tushare 有频率限制）
    if data_type in ["all", "basic"]:
        print("  - 获取基本信息...")
        source = data_source if data_source and data_source != "auto" else get_best_data_source("basic")
        result["basic_info"] = get_stock_info(code, source)
        if "data_source" in result["basic_info"]:
            result["data_sources_used"].append(f"basic:{result['basic_info']['data_source']}")

    # 财务数据：akshare 优先（功能全）
    if data_type in ["all", "financial"]:
        print("  - 获取财务数据...")
        source = data_source if data_source and data_source != "auto" else get_best_data_source("financial")
        result["financial_data"] = get_financial_data(code, years, source)
        result["data_sources_used"].append(f"financial:{source}")

        print("  - 获取财务指标...")
        result["financial_indicators"] = get_financial_indicators(code, data_source=source)

    # 估值数据：akshare
    if data_type in ["all", "valuation"]:
        print("  - 获取估值数据...")
        result["valuation"] = get_valuation_data(code)
        result["data_sources_used"].append("valuation:akshare")

    # 价格数据：tushare 优先（稳定）
    if data_type in ["all", "valuation"]:
        print("  - 获取价格数据...")
        source = data_source if data_source and data_source != "auto" else get_best_data_source("price")
        price_data = get_price_data(code, data_source=source)
        result["price"] = price_data
        actual_source = price_data.get("data_source", source)
        result["data_sources_used"].append(f"price:{actual_source}")

    # 股东数据：akshare
    if data_type in ["all", "holder"]:
        print("  - 获取股东数据...")
        result["holder"] = get_holder_data(code)
        result["data_sources_used"].append("holder:akshare")

        print("  - 获取分红数据...")
        result["dividend"] = get_dividend_data(code)
        result["data_sources_used"].append("dividend:akshare")

    # 保存缓存
    if use_cache:
        save_cache(code, data_type, result)

    print(f"数据获取完成: {code}")
    print(f"使用数据源: {', '.join(set(result['data_sources_used']))}")
    return result


def fetch_multiple_stocks(codes: list, data_type: str = "basic",
                          data_source: str = None) -> dict:
    """获取多只股票数据"""
    result = {
        "fetch_time": datetime.now().isoformat(),
        "stocks": [],
        "success_count": 0,
        "fail_count": 0
    }

    total = len(codes)
    for i, code in enumerate(codes):
        print(f"[{i+1}/{total}] 获取 {code}...")
        try:
            stock_data = fetch_stock_data(code, data_type, use_cache=True, data_source=data_source)
            if "error" not in stock_data.get("basic_info", {}):
                result["stocks"].append(stock_data)
                result["success_count"] += 1
            else:
                result["fail_count"] += 1
        except Exception as e:
            print(f"  获取失败: {e}")
            result["fail_count"] += 1

        if i < total - 1:
            time.sleep(0.5)

    return result


def print_data_source_status():
    """打印数据源状态"""
    print("\n数据源状态:")
    print("-" * 40)
    for source, info in DATA_SOURCES.items():
        status = "✅ 可用" if info["available"] else "❌ 不可用"
        if source == "tushare" and info["available"]:
            config_ok = check_tushare_config()
            status = "✅ 已配置" if config_ok else "⚠️ 未配置 token"
        print(f"  {info['name']}: {status}")

    available = get_available_data_source()
    print(f"\n当前使用: {DATA_SOURCES.get(available, {}).get('name', available)}")
    print("-" * 40)


def main():
    parser = argparse.ArgumentParser(description="A股数据获取工具（支持双数据源）")
    parser.add_argument("--code", type=str, help="股票代码 (如: 600519)")
    parser.add_argument("--codes", type=str, help="多个股票代码，逗号分隔 (如: 600519,000858)")
    parser.add_argument("--data-type", type=str, default="basic",
                       choices=["all", "basic", "financial", "valuation", "holder"],
                       help="数据类型 (默认: basic)")
    parser.add_argument("--years", type=int, default=3, help="获取多少年的历史数据 (默认: 3)")
    parser.add_argument("--scope", type=str, help="筛选范围: hs300/zz500/cyb/kcb/all")
    parser.add_argument("--no-cache", action="store_true", help="不使用缓存")
    parser.add_argument("--data-source", type=str, default="auto",
                       choices=["auto", "akshare", "tushare"],
                       help="数据源 (默认: auto 自动选择)")
    parser.add_argument("--output", type=str, help="输出文件路径 (JSON)")
    parser.add_argument("--status", action="store_true", help="显示数据源状态")

    args = parser.parse_args()

    # 显示数据源状态
    if args.status:
        print_data_source_status()
        return

    result = {}

    if args.code:
        result = fetch_stock_data(args.code, args.data_type, args.years,
                                   use_cache=not args.no_cache,
                                   data_source=args.data_source)
    elif args.codes:
        codes = [c.strip() for c in args.codes.split(",")]
        result = fetch_multiple_stocks(codes, args.data_type, data_source=args.data_source)
    elif args.scope:
        if args.scope == "all":
            codes = get_all_a_stocks()
        else:
            codes = get_index_constituents(args.scope)
        result = {"scope": args.scope, "stocks": codes, "count": len(codes)}
    else:
        print("请提供 --code, --codes, --scope 或 --status 参数")
        sys.exit(1)

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2, default=str)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\n数据已保存到: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
