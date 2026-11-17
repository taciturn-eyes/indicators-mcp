from typing import List

import pandas as pd

from .banshen import detect_banshen_macd_divergence, summarize_macd_divergence
from .config import ATR_PERIOD, KLINE_LIMIT
from .macd import add_macd
from .market_data import fetch_klines, normalize_symbol
from .trend import add_emas, describe_ema_trend
from .volatility import calculate_atr
from .wyckoff import tag_wyckoff_anomalies


def prepare_indicators(df: pd.DataFrame) -> pd.DataFrame:
    add_emas(df)
    add_macd(df)
    df["ATR14"] = calculate_atr(df, ATR_PERIOD)
    return tag_wyckoff_anomalies(df)


def analyze_single_timeframe(symbol: str, interval: str, limit: int = KLINE_LIMIT) -> str:
    symbol = normalize_symbol(symbol)
    df = prepare_indicators(fetch_klines(symbol, interval, limit))

    divergence_report = "\n  ".join(detect_banshen_macd_divergence(df))
    recent_anomalies = [
        f"[{row['time']}] {row['Wyckoff_Tag']} (量比:{row['Vol_Ratio']}x)"
        for _, row in df.tail(5).iterrows()
        if row["Wyckoff_Tag"] not in ["正常", "-"]
    ]
    wyckoff_summary = "\n  ".join(recent_anomalies) if recent_anomalies else "最近5根K线量价基本匹配，无极端威科夫异常。"

    last = df.iloc[-1]
    ema_trend = describe_ema_trend(last)
    decimals = 2 if last["close"] > 100 else (4 if last["close"] > 1 else 6)

    columns = [
        "time", "open", "high", "low", "close", "Vol_Ratio",
        "EMA20", "EMA50", "EMA144", "EMA169", "EMA200", "DIF", "MACD_Hist", "Wyckoff_Tag",
    ]
    recent_df = df.tail(15)[columns].copy()
    price_columns = [
        "open", "high", "low", "close", "EMA20", "EMA50", "EMA144", "EMA169", "EMA200",
    ]
    for column in price_columns:
        recent_df[column] = recent_df[column].round(decimals)
    for column in ("DIF", "MACD_Hist"):
        recent_df[column] = recent_df[column].round(decimals + 2)

    atr = last["ATR14"]
    atr_value = round(atr, decimals)
    long_stop = round(last["low"] - atr, decimals)
    short_stop = round(last["high"] + atr, decimals)
    header = (
        f"================ {symbol} [{interval}] 深度结构与算法扫描 ================\n"
        f"• 最新现价: {round(last['close'], decimals)} | 均线格局: {ema_trend}\n"
        f"• ATR(14)波动率: {atr_value} (半神止损参考: 做多止损≤{long_stop} / 做空止损≥{short_stop})\n"
        f"• 【半神MACD背离扫描】:\n  {divergence_report}\n"
        f"• 【最近5根K线威科夫量价异常汇总】:\n  {wyckoff_summary}\n"
        f"• 最近15根K线与指标明细 (含逐行威科夫量价标记):\n"
    )
    return header + recent_df.to_string(index=False)


def build_radar_row(symbol: str, interval: str) -> List[str]:
    df = prepare_indicators(fetch_klines(symbol, interval, KLINE_LIMIT))
    last = df.iloc[-1]
    decimals = 2 if last["close"] > 100 else (4 if last["close"] > 1 else 6)

    anomalies = [
        f"{row['time']} {row['Wyckoff_Tag'].replace(' | ', '/')}"
        for _, row in df.tail(5).iterrows()
        if row["Wyckoff_Tag"] not in ["正常", "-"]
    ]
    wyckoff_summary = "；".join(anomalies) if anomalies else "无明显异常"
    atr = last["ATR14"]
    if pd.isna(atr):
        stop_levels = "K线不足，无法计算"
    else:
        stop_levels = f"多≤{round(last['low'] - atr, decimals)} / 空≥{round(last['high'] + atr, decimals)}"

    return [
        symbol,
        interval,
        str(round(last["close"], decimals)),
        describe_ema_trend(last),
        summarize_macd_divergence(df),
        wyckoff_summary,
        stop_levels,
    ]
