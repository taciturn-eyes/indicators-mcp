BINANCE_KLINE_URL = "https://fapi.binance.com/fapi/v1/klines"
KLINE_LIMIT = 250
REQUEST_TIMEOUT_SECONDS = 10

DEFAULT_SCAN_SYMBOLS = ("BTC", "ETH", "XAU", "CL", "TQQQ", "SOXL")
SYMBOL_CODE_MAP = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "XAU": "XAUUSDT",
    "CL": "CLUSDT",
    "TQQQ": "TQQQUSDT",
    "SOXL": "SOXLUSDT",
}

EMA_PERIODS = (20, 50, 144, 169, 200)
MACD_FAST_PERIOD = 13
MACD_SLOW_PERIOD = 34
MACD_SIGNAL_PERIOD = 9
ATR_PERIOD = 14

KLINE_COLUMNS = (
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_vol", "trades", "taker_buy_base",
    "taker_buy_quote", "ignore",
)
