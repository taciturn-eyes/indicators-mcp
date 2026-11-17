import numpy as np
import pandas as pd


def tag_wyckoff_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Tag candles with volume/spread anomalies using Wyckoff effort versus result."""
    df["vol_ma20"] = df["volume"].rolling(20).mean()
    df["body"] = np.abs(df["close"] - df["open"])
    df["body_ma20"] = df["body"].rolling(20).mean()
    df["spread"] = df["high"] - df["low"]
    df["Vol_Ratio"] = (df["volume"] / (df["vol_ma20"] + 1e-9)).round(2)

    tags = []
    for _, row in df.iterrows():
        if pd.isna(row["vol_ma20"]) or row["vol_ma20"] == 0 or row["spread"] == 0:
            tags.append("-")
            continue

        vol_ratio = row["Vol_Ratio"]
        body_ratio = row["body"] / (row["body_ma20"] + 1e-9)
        upper_wick = row["high"] - max(row["open"], row["close"])
        lower_wick = min(row["open"], row["close"]) - row["low"]
        upper_wick_ratio = upper_wick / row["spread"]
        lower_wick_ratio = lower_wick / row["spread"]
        is_bull = row["close"] >= row["open"]
        tag_list = []

        if vol_ratio >= 1.8 and (body_ratio <= 0.65 or upper_wick_ratio >= 0.5):
            if upper_wick_ratio >= 0.5:
                tag_list.append("放量长上影滞涨(供应涌现)")
            elif is_bull:
                tag_list.append("放量窄幅滞涨(努力无结果)")

        if vol_ratio >= 1.8 and (lower_wick_ratio >= 0.5 or (not is_bull and body_ratio <= 0.65)):
            if lower_wick_ratio >= 0.5:
                tag_list.append("放量长下影承接(Spring/吸筹)")
            else:
                tag_list.append("放量窄幅止跌(买盘阻击)")

        if vol_ratio >= 1.6 and body_ratio >= 1.5 and upper_wick_ratio < 0.3 and lower_wick_ratio < 0.3:
            tag_list.append("放量宽体突破(SOS)" if is_bull else "放量长阴砸盘(SOW)")

        if vol_ratio <= 0.65 and body_ratio <= 0.75:
            tag_list.append("缩量回踩/整理(抛压枯竭LPS)")

        tags.append(" | ".join(tag_list) if tag_list else "正常")

    df["Wyckoff_Tag"] = tags
    return df
