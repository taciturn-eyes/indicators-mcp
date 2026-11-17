from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from typing import List

from .analysis import build_radar_row
from .config import DEFAULT_SCAN_SYMBOLS
from .market_data import normalize_symbol


RADAR_HEADERS = ("合约", "现价", "均线排列", "MACD连续背离", "最近5根威科夫异常", "ATR止损(多/空)")


def parse_symbols(symbols: str) -> List[str]:
    parts = re.split(r"[,\s]+", symbols.replace("，", ",").strip())
    normalized = [normalize_symbol(part) for part in parts if part]
    return list(dict.fromkeys(normalized))


def scan_binance_futures(
    symbols: str = ",".join(DEFAULT_SCAN_SYMBOLS), interval: str = "1h"
) -> str:
    interval = interval.strip()
    if not interval:
        raise ValueError("时间周期不能为空")

    contracts = parse_symbols(symbols)
    if not contracts:
        raise ValueError("请至少提供一个交易代码")

    rows_by_symbol = {}
    with ThreadPoolExecutor(max_workers=min(6, len(contracts))) as executor:
        futures = {
            executor.submit(build_radar_row, symbol, interval): symbol
            for symbol in contracts
        }
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                rows_by_symbol[symbol] = future.result()
            except Exception as error:
                message = str(error).replace("|", "/").replace("\n", " ")
                rows_by_symbol[symbol] = [symbol, "-", "-", "-", f"扫描失败：{message}", "-"]

    lines = [
        f"币安合约雷达 | 周期: {interval} | 并发扫描: {len(contracts)} 个品种",
        "| " + " | ".join(RADAR_HEADERS) + " |",
        "| " + " | ".join(["---"] * len(RADAR_HEADERS)) + " |",
    ]
    for symbol in contracts:
        cells = [cell.replace("|", "/").replace("\n", " ") for cell in rows_by_symbol[symbol]]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)
