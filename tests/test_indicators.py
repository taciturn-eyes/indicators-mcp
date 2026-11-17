import unittest

import numpy as np
import pandas as pd

from indicators_mcp.analysis import prepare_indicators
from indicators_mcp.banshen import detect_banshen_macd_divergence, summarize_macd_divergence
from indicators_mcp.market_data import normalize_symbol
from indicators_mcp.trend import describe_ema_trend
from indicators_mcp.wyckoff import tag_wyckoff_anomalies


class IndicatorTests(unittest.TestCase):
    def test_symbol_aliases_map_to_contract_codes(self):
        expected = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "XAU": "XAUUSDT",
            "CL": "CLUSDT",
            "TQQQ": "TQQQUSDT",
            "SOXL": "SOXLUSDT",
        }
        for alias, contract in expected.items():
            with self.subTest(alias=alias):
                self.assertEqual(normalize_symbol(alias.lower()), contract)
        self.assertEqual(normalize_symbol("BTCUSDT"), "BTCUSDT")

    def test_indicator_pipeline_includes_ema169_and_core_outputs(self):
        close = np.linspace(100, 125, 250)
        candles = pd.DataFrame({
            "open": close - 0.1,
            "high": close + 0.3,
            "low": close - 0.3,
            "close": close,
            "volume": np.full(250, 100.0),
        })

        result = prepare_indicators(candles)

        for column in ("EMA20", "EMA50", "EMA144", "EMA169", "EMA200", "DIF", "DEA", "MACD_Hist", "ATR14", "Wyckoff_Tag"):
            with self.subTest(column=column):
                self.assertIn(column, result.columns)
        self.assertTrue(np.isfinite(result["ATR14"].iloc[-1]))

    def test_ema_trend_uses_vegas_periods(self):
        bullish = pd.Series({
            "EMA20": 5.0,
            "EMA50": 4.0,
            "EMA144": 3.0,
            "EMA169": 2.0,
            "EMA200": 1.0,
        })
        self.assertIn("标准多头排列", describe_ema_trend(bullish))

    def test_wyckoff_tags_large_upper_wick_on_high_volume(self):
        candles = pd.DataFrame({
            "open": [100.0] * 21,
            "high": [100.2] * 20 + [102.0],
            "low": [99.9] * 21,
            "close": [100.1] * 21,
            "volume": [100.0] * 20 + [500.0],
        })
        tagged = tag_wyckoff_anomalies(candles)
        self.assertIn("放量长上影滞涨", tagged["Wyckoff_Tag"].iloc[-1])

    def test_banshen_summary_reports_triggered_divergence_compactly(self):
        candles = pd.DataFrame({
            "MACD_Hist": [1.0, 2.0, 1.0, 0.0, 0.0, 0.5, 1.5, 0.5],
            "high": [12.0, 11.0, 10.0, 9.0, 9.0, 13.0, 12.0, 11.0],
            "low": [8.0] * 8,
            "time": [f"t{index}" for index in range(8)],
        })
        signals = detect_banshen_macd_divergence(candles)
        self.assertIn("前高:12.0(t0)", signals[0])
        self.assertIn("顶背离/做空：已触发", summarize_macd_divergence(candles))

    def test_banshen_handles_empty_frame(self):
        candles = pd.DataFrame(columns=["MACD_Hist", "high", "low", "time"])
        self.assertIn("没有可用K线", detect_banshen_macd_divergence(candles)[0])


if __name__ == "__main__":
    unittest.main()
