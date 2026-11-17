# Binance Futures Indicators MCP

本项目通过 MCP 提供币安永续合约的多品种雷达与单品种深度分析。

## 运行

```powershell
uv sync
uv run main.py
```

在 Cherry Studio 中将命令配置为项目虚拟环境的 Python，并将 `main.py` 作为参数。服务使用 stdio；修改工具后在 Cherry Studio 刷新或重连 MCP 服务。

## MCP 工具

- `scan_binance_futures`：默认并发扫描 BTC、ETH、XAU、CL、TQQQ、SOXL 的 1h 雷达摘要。可传入逗号分隔的简称/合约代码及单一周期。
- `analyze_binance_futures`：对单个品种按一个或多个周期生成 K 线与指标明细。

## 模块

- `indicators_mcp/market_data.py`：合约代码规范化与 K 线 API。
- `indicators_mcp/trend.py`、`volatility.py`、`macd.py`：EMA、ATR 与 MACD 计算。
- `indicators_mcp/banshen.py`、`wyckoff.py`：半神连续背离与威科夫量价标记。
- `indicators_mcp/analysis.py`、`radar.py`：指标组合、深度报告与并发雷达。
- `indicators_mcp/server.py`：MCP 工具注册；`main.py` 是启动入口。

## 测试

```powershell
uv run python -m unittest discover -s tests -v
```
