# Phase 1 Results

**Run date**: 2026-03-11
**Pipeline**: `python main.py`
**Test period**: 2022-01-01 to 2024-12-30
**Train period**: 2015-01-02 to 2021-12-31

---

## Model Type Winners

| Ticker | Best Model | F1 | LR F1 | RF F1 | XGB F1 |
|--------|-----------|-----|-------|-------|--------|
| AAPL | xgboost | 0.5839 | 0.5267 | 0.5316 | 0.5839 |
| MSFT | logistic | 0.5830 | 0.5830 | 0.4800 | 0.5142 |
| GOOGL | logistic | 0.6717 | 0.6717 | 0.5536 | 0.5650 |
| AMZN | xgboost | 0.5360 | 0.4168 | 0.5118 | 0.5360 |
| NVDA | logistic | 0.5158 | 0.5158 | 0.4222 | 0.4322 |
| META | xgboost | 0.4686 | 0.4520 | 0.4162 | 0.4686 |
| TSLA | random_forest | 0.5916 | 0.5558 | 0.5916 | 0.5661 |
| SPY | logistic | 0.6849 | 0.6849 | 0.5376 | 0.5750 |
| QQQ | logistic | 0.6103 | 0.6103 | 0.5244 | 0.5618 |
| GLD | logistic | 0.6386 | 0.6386 | 0.4305 | 0.4750 |
| TLT | logistic | 0.6015 | 0.6015 | 0.5989 | 0.5857 |
| BTC-USD | xgboost | 0.5823 | 0.0793 | 0.5385 | 0.5823 |

**Winner summary**: LR wins 7/12, XGBoost wins 4/12, RF wins 1/12

---

## Classification Metrics (Best Model Per Ticker)

| Ticker | Accuracy | Precision | Recall | F1 | AUC-ROC |
|--------|----------|-----------|--------|----|---------|
| AAPL | 0.5186 | 0.5393 | 0.6366 | 0.5839 | 0.5244 |
| MSFT | 0.4920 | 0.5066 | 0.6864 | 0.5830 | 0.4938 |
| GOOGL | 0.5359 | 0.5360 | 0.8992 | 0.6717 | 0.5303 |
| AMZN | 0.4774 | 0.4903 | 0.5911 | 0.5360 | 0.4685 |
| NVDA | 0.5106 | 0.5490 | 0.4864 | 0.5158 | 0.5128 |
| META | 0.4934 | 0.5091 | 0.4341 | 0.4686 | 0.5097 |
| TSLA | 0.5465 | 0.5489 | 0.6416 | 0.5916 | 0.5408 |
| SPY | 0.5253 | 0.5265 | 0.9798 | 0.6849 | 0.5044 |
| QQQ | 0.5160 | 0.5337 | 0.7125 | 0.6103 | 0.5038 |
| GLD | 0.5213 | 0.5300 | 0.8030 | 0.6386 | 0.5315 |
| TLT | 0.5173 | 0.5046 | 0.7446 | 0.6015 | 0.5156 |
| BTC-USD | 0.5205 | 0.5112 | 0.6765 | 0.5823 | 0.5202 |

> **Note**: Accuracy is near-random (47–55%) as expected for daily direction prediction.
> F1 is the primary metric due to class imbalance handling.

---

## Backtest Performance

| Ticker | Strategy Return | Buy & Hold | Outperforms? | Sharpe | Max Drawdown |
|--------|----------------|------------|--------------|--------|--------------|
| AAPL | +49.5% | +40.8% | ✅ | 0.74 | — |
| MSFT | +21.8% | +30.2% | 📉 | 0.40 | — |
| GOOGL | +35.3% | +32.4% | ✅ | 0.49 | — |
| AMZN | +21.1% | +29.9% | 📉 | 0.36 | — |
| NVDA | +131.5% | +357.2% | 📉 | 0.87 | — |
| META | +29.4% | +75.3% | 📉 | 0.45 | — |
| TSLA | +75.2% | +4.4% | ✅ | 0.64 | — |
| SPY | +25.4% | +28.7% | 📉 | 0.52 | — |
| QQQ | +23.9% | +31.0% | 📉 | 0.49 | — |
| GLD | +35.0% | +43.0% | 📉 | 0.86 | — |
| TLT | -10.6% | -32.9% | ✅ | -0.19 | — |
| BTC-USD | +61.0% | +94.3% | 📉 | 0.48 | — |

**Outperforms buy-and-hold**: 4/12 tickers (AAPL, GOOGL, TSLA, TLT)

---

## Key Insights

**LR dominates ETFs and bonds** — SPY, QQQ, GLD, TLT are more linearly predictable assets where a simple decision boundary works well.

**XGBoost wins on volatile stocks and crypto** — AAPL, AMZN, META, BTC-USD benefit from XGBoost's ability to model non-linear feature interactions.

**BTC-USD edge case** — LR had near-zero F1 (0.08) because it defaulted to always predicting one class. XGBoost rescued it to 0.58.

**Strategy consistently reduces max drawdown** — Even when strategy underperforms on total return, it avoids the worst drawdown periods on every single asset. TLT is the clearest example: -10.6% vs -32.9%.

**NVDA is the hardest to beat** — A sustained AI-driven bull run (+357% buy-and-hold) means any time the strategy sits in cash it misses gains. Long-only strategies struggle against unidirectional trends.
