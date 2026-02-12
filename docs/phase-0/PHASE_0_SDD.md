# Phase 0 Software Design Document (SDD)

**Project Name**: Finance ML Lab – Phase 0 MVP
**Phase Duration**: Weeks 1–3
**Author**: Carter Chan
**Version**: 0.1
**Status**: Initial Design
**Last Updated**: 2026-02-12

---

## 1. Purpose & Scope

### 1.1 Purpose

The purpose of Phase 0 is to build a minimal, working end-to-end machine learning pipeline for financial time series prediction. This MVP will:

- Fetch historical stock/ETF data
- Engineer basic financial features
- Train a baseline ML model
- Generate next-day up/down predictions
- Visualize predictions vs actual outcomes

**This phase prioritizes correctness, clarity, and extensibility, not predictive performance.**

### 1.2 In-Scope

- ✅ Historical price data (daily OHLCV)
- ✅ 1–3 assets (stocks or ETFs)
- ✅ Supervised ML classification (binary up/down)
- ✅ Offline batch training & evaluation
- ✅ Local visualizations

### 1.3 Out-of-Scope (Explicitly)

- ❌ Live trading or execution
- ❌ Real-time data
- ❌ Deep learning models
- ❌ Portfolio optimization
- ❌ Cloud deployment
- ❌ NLP or alternative data

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌──────────────┐
│ Data Ingest  │  ← yfinance / Alpha Vantage
└──────┬───────┘
       ↓
┌──────────────┐
│ Feature Eng. │  ← returns, MAs, volatility
└──────┬───────┘
       ↓
┌──────────────┐
│ ML Model     │  ← Logistic Regression / RF
└──────┬───────┘
       ↓
┌──────────────┐
│ Evaluation   │  ← accuracy, confusion matrix
└──────┬───────┘
       ↓
┌──────────────┐
│ Visualization│  ← price + predictions
└──────────────┘
```

---

## 3. Technology Stack

### 3.1 Languages & Libraries

- **Python** 3.10+
- **pandas** - Data manipulation
- **numpy** - Numerical operations
- **scikit-learn** - ML models and evaluation
- **yfinance** - Primary data source
- **matplotlib** and/or **plotly** - Visualization
- **seaborn** - Statistical visualizations (optional)

### 3.2 Development Environment

- **IDE**: Cursor / VS Code
- **Virtual Environment**: venv or conda
- **Jupyter Notebook** for experimentation
- **Python scripts** for production-ready logic

---

## 4. Project Structure

```
financeTool/
│
├── data/
│   ├── raw/                # downloaded price data
│   └── processed/          # feature-engineered datasets
│
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_modeling.ipynb
│
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── features.py
│   ├── model.py
│   ├── evaluation.py
│   └── visualization.py
│
├── requirements.txt
├── README.md
└── main.py
```

---

## 5. Component Design

### 5.1 Data Loader (`data_loader.py`)

**Responsibilities**
- Download historical OHLCV data
- Save raw data locally
- Load cached data if already present

**Inputs**
- Ticker symbol(s)
- Start date
- End date

**Outputs**
- pandas DataFrame indexed by date

**Key Functions**
```python
def fetch_price_data(ticker: str, start: str, end: str) -> pd.DataFrame
def load_cached_data(ticker: str) -> pd.DataFrame
```

---

### 5.2 Feature Engineering (`features.py`)

**Responsibilities**
- Transform raw price data into ML-ready features
- Handle NaNs caused by rolling calculations
- Generate prediction target

**Features**
- Daily returns
- 5-day moving average
- 20-day moving average
- Rolling volatility (20-day std)
- Price relative to MA

**Target Variable**
```python
target = 1 if next_day_return > 0 else 0
```

**Key Functions**
```python
def compute_features(df: pd.DataFrame) -> pd.DataFrame
def generate_target(df: pd.DataFrame) -> pd.DataFrame
```

---

### 5.3 Model Training (`model.py`)

**Responsibilities**
- Train baseline ML models
- Save trained model artifacts
- Support future model swapping

**Models**
- Logistic Regression (baseline)
- Random Forest (optional)

**Key Functions**
```python
def train_model(X_train, y_train, model_type="logistic")
def predict(model, X_test)
```

---

### 5.4 Evaluation (`evaluation.py`)

**Responsibilities**
- Quantitatively assess model performance
- Provide interpretable metrics

**Metrics**
- Accuracy
- Precision / Recall
- Confusion Matrix

**Key Functions**
```python
def evaluate_classification(y_true, y_pred) -> dict
```

---

### 5.5 Visualization (`visualization.py`)

**Responsibilities**
- Plot price history
- Overlay predictions vs actuals
- Show correct vs incorrect predictions

**Visuals**
- Price chart with buy/sell markers
- Prediction correctness timeline

**Key Functions**
```python
def plot_price_with_predictions(df)
def plot_confusion_matrix(y_true, y_pred)
```

---

## 6. Data Flow

1. `main.py` loads config and tickers
2. Data fetched via `data_loader.py`
3. Features generated in `features.py`
4. Dataset split into train/test (time-based)
5. Model trained via `model.py`
6. Predictions evaluated via `evaluation.py`
7. Results visualized via `visualization.py`

---

## 7. Configuration (`config.py`)

```python
TICKERS = ["AAPL", "SPY"]
START_DATE = "2015-01-01"
END_DATE = "2024-12-31"
TEST_SPLIT_DATE = "2022-01-01"
MODEL_TYPE = "logistic"
```

---

## 8. Non-Functional Requirements

- **Reproducibility**: Fixed random seeds
- **Extensibility**: Modular functions, no hard-coded assets
- **Clarity**: Simple models over complex ones
- **Performance**: Must run locally in <30 seconds

---

## 9. Acceptance Criteria (Phase 0 Complete When)

- [ ] ✅ Can run `python main.py` end-to-end
- [ ] ✅ At least one asset produces predictions
- [ ] ✅ Features and target are clearly defined
- [ ] ✅ Model accuracy is computed and displayed
- [ ] ✅ At least one meaningful visualization exists
- [ ] ✅ Code structure supports future phases without refactor

---

## 10. Future Hooks (Planned Extensions)

- Backtesting engine (Phase 1)
- Multi-asset aggregation
- Advanced models (Phase 2)
- NLP & alternative data (Phase 3)
- Portfolio optimization (Phase 4)

---

## 11. Summary

Phase 0 establishes a clean, minimal financial ML pipeline that:

- Demonstrates end-to-end ML competence
- Avoids premature optimization
- Acts as a stable foundation for 12–18 months of expansion

This SDD is designed to be **Cursor-friendly**: every section can be turned into code incrementally, with AI-assisted generation staying aligned to the architecture.

---

## Related Documents

- [Phase 0 Component Specs](COMPONENT_SPECS.md)
- [Phase 0 Implementation Guide](IMPLEMENTATION_GUIDE.md)
- [Phase 0 Testing Plan](TESTING_PLAN.md)

---

**Status**: Ready for Implementation
**Next Step**: Begin component implementation starting with `config.py` and `data_loader.py`
