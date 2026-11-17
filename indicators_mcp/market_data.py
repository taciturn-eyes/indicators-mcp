import pandas as pd
import requests

from .config import BINANCE_KLINE_URL, KLINE_COLUMNS, REQUEST_TIMEOUT_SECONDS, SYMBOL_CODE_MAP


def normalize_symbol(symbol: str) -> str:
    code = symbol.strip().upper()
    if not code:
        raise ValueError("交易代码不能为空")
    return SYMBOL_CODE_MAP.get(code, code if code.endswith("USDT") else f"{code}USDT")


def fetch_klines(symbol: str, interval: str, limit: int = 250) -> pd.DataFrame:
    params = {"symbol": normalize_symbol(symbol), "interval": interval, "limit": limit}
    response = requests.get(BINANCE_KLINE_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list) or not data:
        raise ValueError("Binance 未返回有效的合约K线数据")

    df = pd.DataFrame(data, columns=KLINE_COLUMNS)
    for column in ("open", "high", "low", "close", "volume"):
        df[column] = df[column].astype(float)
    df["time"] = pd.to_datetime(df["open_time"], unit="ms").dt.strftime("%m-%d %H:%M")
    return df
