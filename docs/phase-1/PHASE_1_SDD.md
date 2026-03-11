# Phase 1 Software Design Document

**Phase**: 1 — Multi-Asset & Backtesting
**Status**: ✅ Complete
**Date**: 2026-03-11

---

## 1. Scope

### In Scope
- Expand asset universe from 2 → 12 tickers
- Add 5 technical indicators: RSI, MACD, MACD signal, Bollinger Band position, volume ratio
- Build backtesting engine (long-only strategy vs buy-and-hold)
- Add Random Forest and XGBoost to the model pipeline
- Auto-select best model per ticker by F1 score
- Generate equity curve charts and an HTML dashboard

### Out of Scope
- Live/paper trading
- Deep learning models (Phase 2)
- Sentiment/news data (Phase 3)
- Portfolio-level optimization (Phase 4)
- Cloud deployment (Phase 5)

---

## 2. Architecture

### Module Changes

| Module | Change | Description |
|--------|--------|-------------|
| `src/config.py` | Updated | 12 tickers, 10 features, new indicator params, XGBoost params, `ALL_MODEL_TYPES` |
| `src/features.py` | Updated | +4 functions: `compute_rsi`, `compute_macd`, `compute_bollinger_bands`, `compute_volume_features` |
| `src/model.py` | Updated | Added `train_xgboost`, updated `train_model` dispatcher to support `"xgboost"` |
| `src/backtester.py` | **New** | Full backtesting engine |
| `main.py` | Rewritten | Phase 1 pipeline: trains all 3 models, picks best, backtests, generates all charts |

### Data Flow

```
yfinance → data_loader → raw DataFrame (OHLCV)
         → features    → 10 features + target (2495 rows per ticker)
         → time split  → train (pre-2022) / test (2022–2024)
         → model ×3    → LR predictions, RF predictions, XGB predictions
         → evaluation  → compare by F1 → pick best model
         → backtester  → equity curve vs buy-and-hold
         → visualization → 6 charts per ticker + dashboard
```

---

## 3. New Features (Technical Indicators)

| Feature | Formula | Signal |
|---------|---------|--------|
| `rsi_14` | EWM gain/loss ratio over 14 days, scaled 0–100 | >70 overbought, <30 oversold |
| `macd` | EMA(12) − EMA(26) | Positive = bullish momentum |
| `macd_signal` | EMA(9) of MACD | Crossover = trend change |
| `bb_position` | (Close − Lower band) / (Upper − Lower) | 0=oversold, 1=overbought |
| `volume_ratio` | Volume / 20-day avg volume | >1.5 = strong conviction |

---

## 4. Backtesting Engine (`src/backtester.py`)

### Strategy
- **Long-only**: invest when model predicts "up" (1), hold cash when "down" (0)
- **Benchmark**: buy-and-hold (always invested)
- **No shorting**, no leverage, no transaction costs

### Metrics
| Metric | Description |
|--------|-------------|
| Total return | Compounded portfolio growth over test period |
| Sharpe ratio | Return / volatility (annualized, risk-free rate = 0) |
| Max drawdown | Largest peak-to-trough decline |
| Win rate | % of invested days with positive return |
| Days invested | How often the strategy is in the market |

---

## 5. Model Pipeline

All three models are trained on every ticker. Best model is selected by F1 score.

| Model | Library | Key params |
|-------|---------|-----------|
| Logistic Regression | scikit-learn | C=1.0, class_weight=balanced, max_iter=1000 |
| Random Forest | scikit-learn | n_estimators=100, max_depth=10, class_weight=balanced |
| XGBoost | xgboost | n_estimators=200, max_depth=4, learning_rate=0.05, subsample=0.8 |

---

## 6. Acceptance Criteria

- [x] 12/12 assets processed successfully
- [x] All 5 technical indicators computed without data leakage
- [x] Backtesting engine produces total return, Sharpe, and max drawdown
- [x] 3-model comparison runs per ticker and picks best by F1
- [x] 72 figures generated and saved to `docs/figures/`
- [x] HTML dashboard navigable across all 12 tickers
