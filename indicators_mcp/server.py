from typing import List

from mcp.server.fastmcp import FastMCP

from .analysis import analyze_single_timeframe
from .config import DEFAULT_SCAN_INTERVALS, DEFAULT_SCAN_SYMBOLS
from .radar import scan_binance_futures as scan_radar


mcp = FastMCP("Binance-BanShen-Wyckoff-Analyzer")


@mcp.tool()
def scan_binance_futures(
    symbols: str = ",".join(DEFAULT_SCAN_SYMBOLS),
    intervals: List[str] = list(DEFAULT_SCAN_INTERVALS),
) -> str:
    """并发扫描多个币安永续合约，输出精简雷达摘要。

    symbols 接受逗号或空格分隔的简称/合约代码，例如 "BTC, ETH, XAU, CL, TQQQ, SOXL"。
    intervals 为周期列表，例如 ["1d", "4h"]；默认扫描日线和4小时线。
    """
    return scan_radar(symbols, intervals)


@mcp.tool()
def analyze_binance_futures(
    symbol: str = "BTCUSDT", intervals: List[str] = ["1d", "4h", "1h", "5m"]
) -> str:
    """深度分析单个合约，可传简称或标准合约代码，并按指定周期输出K线细节。"""
    if not intervals:
        intervals = ["1d", "4h", "1h", "5m"]

    results = []
    for interval in intervals:
        try:
            results.append(analyze_single_timeframe(symbol, interval.strip(), 250))
        except Exception as error:
            results.append(f"[{interval}] 获取失败: {error}")
    return "\n\n".join(results)
