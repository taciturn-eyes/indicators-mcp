import unittest
from unittest.mock import patch

from indicators_mcp.config import DEFAULT_SCAN_SYMBOLS, SYMBOL_CODE_MAP
from indicators_mcp.radar import scan_binance_futures


class RadarTests(unittest.TestCase):
    def test_default_scan_keeps_one_symbol_failure_local(self):
        def build_row(symbol, interval):
            if symbol == "SOXLUSDT" and interval == "1d":
                raise RuntimeError("mock API failure")
            return [symbol, interval, "100", "趋势", "无背离", "无异常", "多≤95 / 空≥105"]

        with patch("indicators_mcp.radar.build_radar_row", side_effect=build_row):
            report = scan_binance_futures()

        for alias in DEFAULT_SCAN_SYMBOLS:
            self.assertIn(SYMBOL_CODE_MAP[alias], report)
        self.assertIn("| SOXLUSDT | 1d |", report)
        self.assertIn("| SOXLUSDT | 4h |", report)
        self.assertIn("扫描失败：mock API failure", report)
        self.assertEqual(report.count("\n|"), 14)
        self.assertIn("周期: 1d/4h", report)
        self.assertNotIn("最近15根K线", report)

    def test_symbols_are_normalized_deduplicated_and_keep_requested_interval(self):
        with patch(
            "indicators_mcp.radar.build_radar_row",
            side_effect=lambda symbol, interval: [symbol, interval, "", "", "", "", ""],
        ) as build_row:
            report = scan_binance_futures("btc, BTCUSDT, ETH", ["15M", "1h"])

        calls = [call.args for call in build_row.call_args_list]
        self.assertCountEqual(calls, [
            ("BTCUSDT", "15m"), ("BTCUSDT", "1h"),
            ("ETHUSDT", "15m"), ("ETHUSDT", "1h"),
        ])
        self.assertIn("周期: 15m/1h", report)

    def test_empty_symbols_and_invalid_intervals_are_rejected(self):
        with self.assertRaises(ValueError):
            scan_binance_futures(" , ")
        with self.assertRaises(ValueError):
            scan_binance_futures("BTC", [""])

    def test_empty_interval_list_uses_default_periods(self):
        with patch(
            "indicators_mcp.radar.build_radar_row",
            side_effect=lambda symbol, interval: [symbol, interval, "", "", "", "", ""],
        ) as build_row:
            report = scan_binance_futures("BTC", [])

        self.assertCountEqual(
            [call.args for call in build_row.call_args_list],
            [("BTCUSDT", "1d"), ("BTCUSDT", "4h")],
        )
        self.assertIn("周期: 1d/4h", report)


if __name__ == "__main__":
    unittest.main()
