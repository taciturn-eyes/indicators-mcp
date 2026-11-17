import pandas as pd

from .config import MACD_FAST_PERIOD, MACD_SLOW_PERIOD, MACD_SIGNAL_PERIOD


def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    fast_ema = df["close"].ewm(span=MACD_FAST_PERIOD, adjust=False).mean()
    slow_ema = df["close"].ewm(span=MACD_SLOW_PERIOD, adjust=False).mean()
    df["DIF"] = fast_ema - slow_ema
    df["DEA"] = df["DIF"].ewm(span=MACD_SIGNAL_PERIOD, adjust=False).mean()
    df["MACD_Hist"] = (df["DIF"] - df["DEA"]) * 2
    return df
