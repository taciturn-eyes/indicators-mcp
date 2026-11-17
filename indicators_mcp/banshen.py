from typing import List

import numpy as np
import pandas as pd


def detect_banshen_macd_divergence(df: pd.DataFrame) -> List[str]:
    """Detect repeated MACD histogram divergence within same-side waves."""
    signals = []
    hist = df["MACD_Hist"].values
    highs = df["high"].values
    lows = df["low"].values
    times = df["time"].values
    count = len(df)
    if count == 0:
        return ["当前没有可用K线，无法检测背离。"]

    positive_waves = []
    index = 0
    while index < count:
        if hist[index] > 0:
            start = index
            while index < count and hist[index] > 0:
                index += 1
            end = index - 1
            if end - start >= 2:
                peak_index = start + np.argmax(hist[start:end + 1])
                price_high_index = start + np.argmax(highs[start:end + 1])
                positive_waves.append({
                    "idx": peak_index,
                    "end_idx": end,
                    "price_time": times[price_high_index],
                    "hist_val": hist[peak_index],
                    "price_high": highs[price_high_index],
                })
        else:
            index += 1

    negative_waves = []
    index = 0
    while index < count:
        if hist[index] < 0:
            start = index
            while index < count and hist[index] < 0:
                index += 1
            end = index - 1
            if end - start >= 2:
                trough_index = start + np.argmin(hist[start:end + 1])
                price_low_index = start + np.argmin(lows[start:end + 1])
                negative_waves.append({
                    "idx": trough_index,
                    "end_idx": end,
                    "price_time": times[price_low_index],
                    "hist_val": hist[trough_index],
                    "price_low": lows[price_low_index],
                })
        else:
            index += 1

    if len(positive_waves) >= 2 and hist[-1] > 0:
        latest = positive_waves[-1]
        previous = positive_waves[-2]
        if count - 1 - latest["end_idx"] <= 2 and latest["idx"] - previous["idx"] <= 45:
            if latest["price_high"] > previous["price_high"] and latest["hist_val"] < previous["hist_val"] * 0.8:
                divergence_count = 2
                if len(positive_waves) >= 3:
                    previous_two = positive_waves[-3]
                    if (
                        previous["idx"] - previous_two["idx"] <= 45
                        and previous["price_high"] > previous_two["price_high"]
                        and previous["hist_val"] < previous_two["hist_val"] * 0.85
                    ):
                        divergence_count = 3

                trigger = "⏳等待柱体缩短(实转虚)"
                if count >= 3 and hist[-1] < hist[-2] and hist[-2] >= latest["hist_val"] * 0.95:
                    trigger = "🔥【已触发】MACD柱体实转虚，右侧空单扳机出现！"
                elif hist[-1] < latest["hist_val"]:
                    trigger = "✅柱体正在收缩衰减中"

                signals.append(
                    f"⚠️ 检测到【{divergence_count}次连续顶背离】| "
                    f"前高:{previous['price_high']}({previous['price_time']}) -> "
                    f"新高:{latest['price_high']}({latest['price_time']}) | "
                    f"MACD柱峰由 {round(previous['hist_val'], 4)} 萎缩至 {round(latest['hist_val'], 4)} | "
                    f"状态: {trigger}"
                )

    if len(negative_waves) >= 2 and hist[-1] < 0:
        latest = negative_waves[-1]
        previous = negative_waves[-2]
        if count - 1 - latest["end_idx"] <= 2 and latest["idx"] - previous["idx"] <= 45:
            if latest["price_low"] < previous["price_low"] and abs(latest["hist_val"]) < abs(previous["hist_val"]) * 0.8:
                divergence_count = 2
                if len(negative_waves) >= 3:
                    previous_two = negative_waves[-3]
                    if (
                        previous["idx"] - previous_two["idx"] <= 45
                        and previous["price_low"] < previous_two["price_low"]
                        and abs(previous["hist_val"]) < abs(previous_two["hist_val"]) * 0.85
                    ):
                        divergence_count = 3

                trigger = "⏳等待柱体缩短(实转虚)"
                if count >= 3 and hist[-1] > hist[-2] and hist[-2] <= latest["hist_val"] * 0.95:
                    trigger = "🔥【已触发】MACD柱体实转虚，右侧多单扳机出现！"
                elif hist[-1] > latest["hist_val"]:
                    trigger = "✅柱体正在收缩衰减中"

                signals.append(
                    f"⚠️ 检测到【{divergence_count}次连续底背离】| "
                    f"前低:{previous['price_low']}({previous['price_time']}) -> "
                    f"新低:{latest['price_low']}({latest['price_time']}) | "
                    f"MACD柱谷由 {round(previous['hist_val'], 4)} 萎缩至 {round(latest['hist_val'], 4)} | "
                    f"状态: {trigger}"
                )

    if not signals:
        signals.append("当前最新波段未检测到显著的连续背离结构。")
    return signals


def summarize_macd_divergence(df: pd.DataFrame) -> str:
    signals = detect_banshen_macd_divergence(df)
    if all("未检测到显著" in signal for signal in signals):
        return "无显著背离"

    summaries = []
    for signal in signals:
        if "顶背离" in signal:
            side = "顶背离/做空"
        elif "底背离" in signal:
            side = "底背离/做多"
        else:
            summaries.append(signal)
            continue

        if "已触发" in signal:
            status = "已触发"
        elif "正在收缩衰减中" in signal:
            status = "柱体收缩"
        else:
            status = "等待实转虚"
        summaries.append(f"{side}：{status}")
    return "；".join(summaries)
