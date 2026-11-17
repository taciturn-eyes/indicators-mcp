import pandas as pd

from .config import EMA_PERIODS


def add_emas(df: pd.DataFrame) -> pd.DataFrame:
    for period in EMA_PERIODS:
        df[f"EMA{period}"] = df["close"].ewm(span=period, adjust=False).mean()
    return df


def describe_ema_trend(last: pd.Series) -> str:
    if last["EMA20"] > last["EMA50"] > last["EMA144"] > last["EMA169"] > last["EMA200"]:
        return "标准多头排列 (EMA20 > 50 > 144 > 169 > 200)"
    if last["EMA20"] < last["EMA50"] < last["EMA144"] < last["EMA169"] < last["EMA200"]:
        return "标准空头排列 (EMA20 < 50 < 144 < 169 < 200)"
    return "均线纠缠震荡"
