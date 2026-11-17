from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from typing import List

from .analysis import build_radar_row
from .config import DEFAULT_SCAN_INTERVALS, DEFAULT_SCAN_SYMBOLS
from .market_data import normalize_symbol


RADAR_HEADERS = ("合约", "周期", "现价", "均线排列", "MACD连续背离", "最近5根威科夫异常", "ATR止损(多/空)")


def parse_symbols(symbols: str) -> List[str]:
    parts = re.split(r"[,\s]+", symbols.replace("，", ",").strip())
    normalized = [normalize_symbol(part) for part in parts if part]
    return list(dict.fromkeys(normalized))


def parse_intervals(intervals: List[str] | str | None) -> List[str]:
    if intervals is None or intervals == []:
        values = list(DEFAULT_SCAN_INTERVALS)
    elif isinstance(intervals, str):
        values = [intervals]
    else:
        values = intervals

    parsed = []
    for value in values:
        parsed.extend(re.split(r"[,/\s]+", value.replace("，", ",").strip()))
    normalized = list(dict.fromkeys(interval.strip().lower() for interval in parsed if interval.strip()))
    if not normalized:
        raise ValueError("请至少提供一个有效的时间周期")
    return normalized


def scan_binance_futures(
    symbols: str = ",".join(DEFAULT_SCAN_SYMBOLS),
    intervals: List[str] | str = list(DEFAULT_SCAN_INTERVALS),
) -> str:
    contracts = parse_symbols(symbols)
    if not contracts:
        raise ValueError("请至少提供一个交易代码")
    periods = parse_intervals(intervals)
    tasks = [(symbol, interval) for symbol in contracts for interval in periods]

    rows_by_symbol = {}
    with ThreadPoolExecutor(max_workers=min(12, len(tasks))) as executor:
        futures = {
            executor.submit(build_radar_row, symbol, interval): (symbol, interval)
            for symbol, interval in tasks
        }
        for future in as_completed(futures):
            symbol, interval = futures[future]
            try:
                rows_by_symbol[(symbol, interval)] = future.result()
            except Exception as error:
                message = str(error).replace("|", "/").replace("\n", " ")
                rows_by_symbol[(symbol, interval)] = [
                    symbol, interval, "-", "-", "-", f"扫描失败：{message}", "-",
                ]

    lines = [
        f"币安合约雷达 | 周期: {'/'.join(periods)} | 并发扫描: {len(contracts)} 品种 × {len(periods)} 周期",
        "| " + " | ".join(RADAR_HEADERS) + " |",
        "| " + " | ".join(["---"] * len(RADAR_HEADERS)) + " |",
    ]
    for symbol in contracts:
        for interval in periods:
            cells = [
                cell.replace("|", "/").replace("\n", " ")
                for cell in rows_by_symbol[(symbol, interval)]
            ]
            lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)
