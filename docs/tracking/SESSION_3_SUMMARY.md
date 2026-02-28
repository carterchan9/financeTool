# Session 3 Summary — Phase 1 Core Implementation

**Date**: 2026-02-28
**Duration**: ~1 session
**Phase**: Phase 1 — Multi-Asset & Backtesting

---

## What Was Built

### 1. Technical Indicators (src/features.py)
Added 4 new functions expanding features from 5 → 10:

| Feature | Function | What it captures |
|---------|----------|-----------------|
| `rsi_14` | `compute_rsi()` | Momentum — overbought/oversold |
| `macd` | `compute_macd()` | Trend direction & strength |
| `macd_signal` | `compute_macd()` | Smoothed MACD for crossover signals |
| `bb_position` | `compute_bollinger_bands()` | Price position in volatility range (0–1) |
| `volume_ratio` | `compute_volume_features()` | Volume conviction vs average |

### 2. Backtesting Engine (src/backtester.py) — new module
- **Strategy**: Long-only — invest when model predicts "up", hold cash otherwise
- **Benchmark**: Buy-and-hold (always invested)
- **Metrics**: total return, Sharpe ratio, max drawdown, win rate, invested days
- **Output**: Per-ticker report + equity curve PNG

### 3. Expanded Asset Universe (src/config.py)
From 2 → 12 tickers: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, SPY, QQQ, GLD, TLT, BTC-USD

### 4. HTML Dashboard (scripts/generate_html_dashboard.py)
Rebuilt from scratch: 12-ticker tab navigation, 6 charts per ticker, 20 KB (was 1.5 MB).

---

## Pipeline Run Results (2026-02-28)

All 12 tickers succeeded. Key takeaways:

**Accuracy** (49–54% range — expected near random for daily direction prediction):
- Best: GOOGL 53.6%, GLD 52.1%
- Note: F1 score matters more than accuracy due to class imbalance handling

**Strategy vs Buy-and-Hold**:
- ✅ META: +106% vs +75% (strategy wins by avoiding drawdowns)
- ✅ TSLA: +23% vs +4% (volatile stock — being out of market helps)
- ✅ GOOGL: +35% vs +32%
- ✅ TLT: -11% vs -33% (bonds bear market — strategy avoided most losses)
- 📉 NVDA: +132% vs +357% (massive AI rally — strategy too cautious)
- 📉 BTC-USD: only invested 4% of days — missed the crypto bull run

**Key insight**: The long-only strategy consistently reduces max drawdown (sometimes by 50%+) on every asset. It struggles when an asset has a sustained unidirectional trend — the model sits in cash during the rally.

---

## What's Next (Phase 1 Remaining)

1. **Multi-model comparison** — Run Random Forest and XGBoost alongside Logistic Regression
   - RF should benefit from the non-linear relationships in RSI/MACD/BB
   - XGBoost is the standard for tabular financial data

2. **Test suite expansion** — `test_features.py`, `test_backtester.py`

3. **Feature importance analysis** — Which indicators matter most per asset?

---

## Key Files Changed

| File | Change |
|------|--------|
| `src/config.py` | 12 tickers, 10 features, new indicator params |
| `src/features.py` | +4 indicator functions, updated `compute_features()` |
| `src/backtester.py` | New module — full backtesting engine |
| `main.py` | Phase 1 pipeline with backtest step |
| `scripts/generate_html_dashboard.py` | Rebuilt for Phase 1 |
| `docs/figures/` | 72 charts (was 17) |
| `dashboards/results_dashboard.html` | Regenerated — 20 KB |
