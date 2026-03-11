# Learning Guide - Understanding the Finance ML Project

**Purpose**: This guide helps you understand how the entire project works, from architecture to implementation details.

**Target Audience**: Developers learning ML, finance, or wanting to understand the codebase.

---

## 📚 Table of Contents

1. [Project Architecture](#project-architecture)
2. [Data Flow](#data-flow)
3. [Module Deep Dives](#module-deep-dives)
4. [Key Concepts](#key-concepts)
5. [Code Examples](#code-examples)
6. [Common Patterns](#common-patterns)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ Project Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Configuration Layer                   │
│                      (config.py)                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│                     Data Pipeline                        │
├─────────────────────────────────────────────────────────┤
│  1. Data Loader → 2. Feature Eng → 3. Train/Test Split  │
│  (data_loader.py)   (features.py)                        │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│                     ML Pipeline                          │
├─────────────────────────────────────────────────────────┤
│  4. Model Training → 5. Predictions → 6. Evaluation     │
│     (model.py)                      (evaluation.py)      │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Visualization Layer                    │
│                  (visualization.py)                      │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure Explained

```
financeTool/
├── src/                    # Source code modules
│   ├── config.py          # Configuration management
│   ├── data_loader.py     # Data fetching & caching
│   ├── test_utils.py      # Testing utilities
│   ├── features.py        # Feature engineering
│   ├── model.py           # ML model training
│   ├── evaluation.py      # Performance metrics
│   └── visualization.py   # Plotting functions
│
├── main.py                 # Production pipeline orchestrator
├── main_demo.py            # Demo pipeline with synthetic data
│
├── tests/                  # Test suite
│   └── test_config.py     # Config tests (13 passing)
│
├── data/                   # Data storage
│   ├── raw/               # Original downloaded data
│   ├── processed/         # Feature-engineered data
│   └── external/          # Third-party data (future)
│
├── models/                 # Saved trained models
├── docs/                   # All documentation
└── logs/                   # Application logs
```

---

## 🔄 Data Flow

### Complete Pipeline Flow

```
1. CONFIGURATION
   └─> config.py loads all settings

2. DATA LOADING
   └─> data_loader.py fetches stock prices from yfinance
   └─> Saves to data/raw/TICKER_raw.csv

3. FEATURE ENGINEERING
   └─> features.py reads raw data
   └─> Calculates: returns, MAs, volatility, price-to-MA
   └─> Creates target variable (next-day direction)
   └─> Drops NaN rows
   └─> Saves to data/processed/TICKER_processed.csv

4. TRAIN/TEST SPLIT
   └─> Time-based split at TEST_SPLIT_DATE (2022-01-01)
   └─> Train: before split date
   └─> Test: after split date

5. MODEL TRAINING
   └─> model.py trains Logistic Regression or Random Forest
   └─> Uses balanced class weights
   └─> Saves to models/TICKER_MODEL.pkl

6. PREDICTION
   └─> model.predict() generates 0/1 predictions
   └─> model.predict_proba() gives probabilities

7. EVALUATION
   └─> evaluation.py calculates metrics
   └─> Accuracy, precision, recall, F1, AUC-ROC
   └─> Confusion matrix
   └─> Compares to baseline (majority class)

8. VISUALIZATION
   └─> visualization.py creates plots
   └─> Saves to docs/figures/
   └─> 8 different plot types
```

---

## 📖 Module Deep Dives

### 1. config.py - Configuration Management

**Purpose**: Centralize all configuration parameters in one place.

**Key Components:**
```python
# Tickers to analyze
TICKERS = ["AAPL", "SPY"]

# Date ranges
START_DATE = "2015-01-01"
END_DATE = "2024-12-31"
TEST_SPLIT_DATE = "2022-01-01"

# Feature parameters
MA_WINDOWS = [5, 20]          # Moving average windows
VOLATILITY_WINDOW = 20        # Volatility calculation window

# Model configuration
MODEL_TYPE = "logistic"       # or "random_forest"
RANDOM_SEED = 42              # For reproducibility
```

**Why it matters:**
- No magic numbers scattered in code
- Easy to experiment (change one value)
- Validation ensures correctness
- Helper functions provide clean access

**Usage Example:**
```python
from src.config import TICKERS, MODEL_TYPE, get_model_params

# Access configuration
for ticker in TICKERS:
    process_ticker(ticker)

# Get model hyperparameters
params = get_model_params(MODEL_TYPE)
```

---

### 2. data_loader.py - Data Fetching

**Purpose**: Download and cache historical stock data.

**Key Functions:**

**`fetch_price_data(ticker, start, end)`**
- Downloads OHLCV data from yfinance
- Checks cache first (avoids re-downloading)
- Saves to data/raw/
- Returns pandas DataFrame

```python
# Example usage
df = fetch_price_data("AAPL", "2020-01-01", "2023-12-31")
# Returns DataFrame with: Open, High, Low, Close, Volume, Date (index)
```

**How caching works:**
1. Check if `data/raw/TICKER_raw.csv` exists
2. If yes: load and return
3. If no: download, save, return

**Why caching matters:**
- Faster subsequent runs
- Reduces API calls
- Works offline after first download
- Good for development/testing

---

### 3. features.py - Feature Engineering

**Purpose**: Transform raw prices into ML-ready features.

**Features Created:**

1. **Daily Returns**
   ```python
   returns = (Close_today - Close_yesterday) / Close_yesterday
   ```
   - Measures daily percentage change
   - Stationary (good for ML)
   - Range: typically -10% to +10%

2. **Moving Averages (5-day, 20-day)**
   ```python
   ma_5 = Close.rolling(window=5).mean()
   ma_20 = Close.rolling(window=20).mean()
   ```
   - Smooth out price noise
   - ma_5: short-term trend
   - ma_20: long-term trend
   - Creates NaN for first N rows

3. **Volatility (20-day rolling std)**
   ```python
   volatility = returns.rolling(window=20).std()
   ```
   - Measures price variability
   - Higher = more risky
   - Used for risk assessment

4. **Price Relative to MA**
   ```python
   price_to_ma = (Close - ma_20) / ma_20
   ```
   - Positive: price above MA (bullish)
   - Negative: price below MA (bearish)
   - Normalized by MA value

5. **Target Variable**
   ```python
   target = 1 if next_day_return > 0 else 0
   ```
   - Binary: 1 = up, 0 = down
   - Shifted by 1 day (predicting future)
   - Used as ML label

**Data Cleaning:**
- Rolling calculations create NaN values
- Drop all rows with NaN
- Typically lose first ~20 rows
- Ensures clean data for ML

---

### 4. model.py - Machine Learning

**Purpose**: Train ML models to predict stock direction.

**Models Implemented:**

**Logistic Regression**
- Linear model
- Simple, fast, interpretable
- Good baseline
- Parameters:
  - `max_iter=1000` - training iterations
  - `class_weight='balanced'` - handles imbalance

**Random Forest**
- Ensemble of decision trees
- Can capture non-linear patterns
- Provides feature importance
- Parameters:
  - `n_estimators=100` - number of trees
  - `max_depth=10` - tree depth
  - `class_weight='balanced'` - handles imbalance

**Training Process:**
```python
# 1. Prepare data
X_train = train_data.drop('target', axis=1)
y_train = train_data['target']

# 2. Train model
model = train_model(X_train, y_train, model_type="logistic")

# 3. Save model
save_model(model, "AAPL", "logistic")

# 4. Make predictions
predictions = predict(model, X_test)
probabilities = predict_proba(model, X_test)
```

**Why Balanced Class Weights:**
- Stock data often imbalanced (more up days or down days)
- Without balancing: model predicts majority class
- With balancing: model learns both classes equally

---

### 5. evaluation.py - Performance Metrics

**Purpose**: Measure how well the model performs.

**Metrics Explained:**

**Accuracy**
```python
accuracy = (correct_predictions / total_predictions)
```
- Overall correctness
- Problem: misleading if imbalanced
- Example: 55% = better than random (50%)

**Precision**
```python
precision = true_positives / (true_positives + false_positives)
```
- When model predicts "up", how often is it right?
- High precision = few false alarms

**Recall**
```python
recall = true_positives / (true_positives + false_negatives)
```
- Of all "up" days, how many did we catch?
- High recall = few missed opportunities

**F1 Score**
```python
f1 = 2 * (precision * recall) / (precision + recall)
```
- Harmonic mean of precision and recall
- Balances both metrics
- Good single-number summary

**Confusion Matrix**
```
               Predicted
               0     1
Actual 0    TN    FP
Actual 1    FN    TP
```
- TN: Correctly predicted down
- FP: Predicted up, actually down
- FN: Predicted down, actually up
- TP: Correctly predicted up

**Baseline Comparison:**
- Baseline = always predict majority class
- Our model must beat baseline to be useful
- Example: If 55% days are up, baseline = 55%

---

### 6. visualization.py - Data Visualization

**Purpose**: Create publication-quality visualizations.

**Visualizations Created:**

1. **Price History** - Line chart of closing prices
2. **Features Plot** - Subplots of all engineered features
3. **Predictions Overlay** - Price with buy/sell markers
4. **Confusion Matrix** - Heatmap of predictions
5. **Feature Importance** - Bar chart (Random Forest only)
6. **Accuracy Timeline** - Correct vs incorrect over time
7. **Model Comparison** - Bar chart comparing models

**Design Choices:**
- Matplotlib for all plots (standard, reliable)
- Seaborn for statistical plots
- Consistent color scheme
- Professional styling
- Automatic saving to docs/figures/

---

## 🧠 Key Concepts

### 1. Time Series Specifics

**Why No Random Splitting:**
```python
# ❌ WRONG for time series
X_train, X_test = train_test_split(X, y, test_size=0.2)

# ✅ CORRECT for time series
train = data[data.index < '2022-01-01']
test = data[data.index >= '2022-01-01']
```

**Reason**: Must preserve temporal order to avoid look-ahead bias.

### 2. Feature Engineering Importance

Raw prices are NOT good features:
- Non-stationary (trend + seasonality)
- Scale varies widely
- Hard for ML to learn

Returns ARE good features:
- Stationary (no trend)
- Comparable across stocks
- Scale-invariant

### 3. Class Imbalance

Stock data often imbalanced:
- Bull markets: 55-60% up days
- Bear markets: 40-45% up days

Solution: Use `class_weight='balanced'`
- Automatically adjusts for imbalance
- Prevents model from just predicting majority

### 4. Model Persistence

**Why Save Models:**
- Avoid retraining
- Deploy in production
- Reproducible results
- Share with others

**How We Save:**
```python
import joblib
joblib.dump(model, 'models/AAPL_logistic.pkl')
model = joblib.load('models/AAPL_logistic.pkl')
```

---

## 💻 Code Examples

### Example 1: Complete Pipeline for One Stock

```python
# 1. Load configuration
from src.config import START_DATE, END_DATE, TEST_SPLIT_DATE

# 2. Fetch data
from src.data_loader import fetch_price_data
df_raw = fetch_price_data("AAPL", START_DATE, END_DATE)

# 3. Engineer features
from src.features import compute_features
df_features = compute_features(df_raw)

# 4. Split train/test
train = df_features[df_features.index < TEST_SPLIT_DATE]
test = df_features[df_features.index >= TEST_SPLIT_DATE]

X_train = train.drop('target', axis=1)
y_train = train['target']
X_test = test.drop('target', axis=1)
y_test = test['target']

# 5. Train model
from src.model import train_model, predict
model = train_model(X_train, y_train, model_type="logistic")

# 6. Make predictions
predictions = predict(model, X_test)

# 7. Evaluate
from src.evaluation import evaluate_classification, print_evaluation_report
metrics = evaluate_classification(y_test, predictions)
print_evaluation_report(metrics)

# 8. Visualize
from src.visualization import plot_price_with_predictions
plot_price_with_predictions(df_raw.loc[test.index], predictions, "AAPL")
```

### Example 2: Comparing Multiple Models

```python
from src.model import train_model
from src.evaluation import evaluate_classification, compare_models

# Train multiple models
models = {}
results = {}

for model_type in ["logistic", "random_forest"]:
    models[model_type] = train_model(X_train, y_train, model_type=model_type)
    preds = predict(models[model_type], X_test)
    results[model_type] = evaluate_classification(y_test, preds)

# Compare
comparison = compare_models(results)
print(comparison)
```

### Example 3: Custom Feature Engineering

```python
from src.features import compute_returns, compute_moving_averages
import pandas as pd

# Start with raw data
df = fetch_price_data("AAPL", "2020-01-01", "2023-12-31")

# Add custom features
df = compute_returns(df)
df = compute_moving_averages(df, windows=[10, 50, 200])  # Custom windows

# Add your own features
df['price_momentum'] = df['Close'].pct_change(periods=5)
df['volume_trend'] = df['Volume'].rolling(10).mean()

# Clean and prepare
df = df.dropna()
```

---

## 🔍 Common Patterns

### Pattern 1: Function Signature Convention

```python
def function_name(
    required_param: type,
    optional_param: type = None
) -> return_type:
    """
    Brief description.

    Args:
        required_param: Description
        optional_param: Description (default: None)

    Returns:
        Description of return value

    Example:
        >>> result = function_name("value")
    """
    # Implementation
    pass
```

### Pattern 2: Error Handling

```python
try:
    # Attempt operation
    df = fetch_price_data(ticker, start, end)

    if df is None or df.empty:
        logger.warning(f"No data for {ticker}")
        return None

except Exception as e:
    logger.error(f"Error processing {ticker}: {e}")
    return None
```

### Pattern 3: Configuration Access

```python
# Import from config
from src.config import MA_WINDOWS, MODEL_TYPE, get_model_params

# Use configuration
for window in MA_WINDOWS:
    df[f'ma_{window}'] = df['Close'].rolling(window).mean()

params = get_model_params(MODEL_TYPE)
model = LogisticRegression(**params)
```

---

## 🐛 Troubleshooting

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Set PYTHONPATH
export PYTHONPATH=/path/to/financeTool

# Or run from project root
cd /path/to/financeTool
python main.py
```

### Issue: yfinance Download Fails

**Problem**: `No data returned for AAPL`

**Solutions**:
1. Check internet connection
2. Try different date range
3. Use demo with synthetic data: `python main_demo.py`
4. Check yfinance is updated: `pip install --upgrade yfinance`

### Issue: NaN Values in Features

**Problem**: Features contain NaN

**Cause**: Rolling calculations create NaN for first N rows

**Solution**: Already handled in `compute_features()` - drops NaN rows

### Issue: Low Model Accuracy

**Problem**: Model accuracy around 50%

**Expected**: Phase 0 uses simple features and models
- 50-55% is baseline (random guessing)
- 55-60% is good for Phase 0
- Phase 2 will add deep learning for better performance

---

## 📚 Further Learning

### Financial ML Concepts
- Read: "Advances in Financial Machine Learning" by Marcos López de Prado
- Topic: Time series cross-validation
- Topic: Feature importance in financial data

### Technical Skills
- Pandas time series: https://pandas.pydata.org/docs/user_guide/timeseries.html
- Scikit-learn: https://scikit-learn.org/stable/
- Matplotlib: https://matplotlib.org/stable/gallery/index.html

### Next Steps
- Explore Phase 1 features (RSI, MACD, Bollinger Bands)
- Learn about backtesting strategies
- Study portfolio optimization theory

---

**Last Updated**: 2026-02-12
