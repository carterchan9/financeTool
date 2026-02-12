# Phase 0 Implementation Guide

Step-by-step guide for implementing Phase 0 MVP.

---

## Implementation Order

### Week 1: Foundation
1. [Environment Setup](#1-environment-setup)
2. [Configuration](#2-configuration)
3. [Data Loader](#3-data-loader)
4. [Testing Data Pipeline](#4-testing-data-pipeline)

### Week 2: Features & Models
5. [Feature Engineering](#5-feature-engineering)
6. [Model Training](#6-model-training)
7. [Evaluation](#7-evaluation)

### Week 3: Visualization & Integration
8. [Visualization](#8-visualization)
9. [Main Pipeline](#9-main-pipeline)
10. [Documentation & Cleanup](#10-documentation--cleanup)

---

## 1. Environment Setup

### Create Virtual Environment
```bash
cd /Users/carterchan/Documents/self-projects/financeTool
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Verify Installation
```bash
python -c "import pandas, numpy, sklearn, yfinance; print('✅ All dependencies installed')"
```

---

## 2. Configuration

**File**: `src/config.py`

### Implementation Steps

1. Create the file with basic structure
2. Add data configuration
3. Add feature parameters
4. Add model configuration
5. Add path configuration

### Testing
```bash
python -c "from src.config import TICKERS, START_DATE; print(f'Tickers: {TICKERS}')"
```

### Cursor Prompt
```
Create src/config.py with:
- TICKERS list (AAPL, SPY)
- Date ranges (START_DATE, END_DATE, TEST_SPLIT_DATE)
- Feature parameters (MA_WINDOWS, VOLATILITY_WINDOW)
- Model configuration (MODEL_TYPE, RANDOM_SEED)
- Path constants (RAW_DATA_PATH, PROCESSED_DATA_PATH, MODEL_PATH)
- Model hyperparameters (LOGISTIC_PARAMS, RANDOM_FOREST_PARAMS)

Follow the specification in docs/phase-0/COMPONENT_SPECS.md section 1.
```

---

## 3. Data Loader

**File**: `src/data_loader.py`

### Implementation Steps

1. Import dependencies (pandas, yfinance, pathlib, etc.)
2. Implement `fetch_price_data()`
3. Implement `save_raw_data()`
4. Implement `load_cached_data()`
5. Add error handling and logging

### Testing
```python
from src.data_loader import fetch_price_data
df = fetch_price_data("AAPL", "2020-01-01", "2023-12-31")
print(df.head())
print(df.shape)
```

### Cursor Prompt
```
Create src/data_loader.py with three functions:

1. fetch_price_data(ticker: str, start: str, end: str) -> pd.DataFrame
   - Use yfinance to download historical data
   - Return DataFrame with OHLCV columns indexed by date
   - Handle errors gracefully

2. save_raw_data(df: pd.DataFrame, ticker: str) -> None
   - Save to data/raw/{ticker}.csv
   - Create directory if needed

3. load_cached_data(ticker: str) -> pd.DataFrame
   - Load from data/raw/{ticker}.csv if exists
   - Return None if not found

Include docstrings and error handling. Follow specs in docs/phase-0/COMPONENT_SPECS.md section 2.
```

---

## 4. Testing Data Pipeline

### Create Test Script
**File**: `tests/test_data_loader.py`

```python
import pytest
from src.data_loader import fetch_price_data

def test_fetch_price_data():
    df = fetch_price_data("AAPL", "2020-01-01", "2020-01-31")
    assert not df.empty
    assert "Close" in df.columns
    assert len(df) > 0
```

### Run Tests
```bash
pytest tests/test_data_loader.py -v
```

---

## 5. Feature Engineering

**File**: `src/features.py`

### Implementation Steps

1. Implement `compute_returns()`
2. Implement `compute_moving_averages()`
3. Implement `compute_volatility()`
4. Implement `compute_price_relative_to_ma()`
5. Implement `generate_target()`
6. Implement `compute_features()` (orchestrator)

### Testing
```python
from src.data_loader import fetch_price_data
from src.features import compute_features

df = fetch_price_data("AAPL", "2020-01-01", "2023-12-31")
df_features = compute_features(df)
print(df_features.columns)
print(df_features.head())
```

### Cursor Prompt
```
Create src/features.py with these functions:

1. compute_returns(df) - calculate daily returns
2. compute_moving_averages(df, windows) - MA for multiple windows
3. compute_volatility(df, window) - rolling std
4. compute_price_relative_to_ma(df) - (Close - MA_20) / MA_20
5. generate_target(df) - binary next-day direction
6. compute_features(df) - orchestrate all feature functions

Use config.MA_WINDOWS and config.VOLATILITY_WINDOW.
Handle NaN values by dropping rows with NaNs.
Follow specs in docs/phase-0/COMPONENT_SPECS.md section 3.
```

---

## 6. Model Training

**File**: `src/model.py`

### Implementation Steps

1. Import scikit-learn models
2. Implement `train_logistic_regression()`
3. Implement `train_random_forest()`
4. Implement `train_model()` dispatcher
5. Implement `save_model()` and `load_model()`
6. Implement `predict()`

### Testing
```python
from src.model import train_model, predict
from sklearn.model_selection import train_test_split

# Assume X, y are prepared
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = train_model(X_train, y_train, model_type="logistic")
predictions = predict(model, X_test)
print(predictions[:10])
```

### Cursor Prompt
```
Create src/model.py with:

1. train_logistic_regression(X_train, y_train, params) - use sklearn LogisticRegression
2. train_random_forest(X_train, y_train, params) - use sklearn RandomForestClassifier
3. train_model(X_train, y_train, model_type) - dispatcher function
4. save_model(model, ticker, model_type) - use joblib to save to models/
5. load_model(ticker, model_type) - load from models/
6. predict(model, X_test) - return predictions

Use config.LOGISTIC_PARAMS and config.RANDOM_FOREST_PARAMS.
Follow specs in docs/phase-0/COMPONENT_SPECS.md section 4.
```

---

## 7. Evaluation

**File**: `src/evaluation.py`

### Implementation Steps

1. Import sklearn metrics
2. Implement `evaluate_classification()`
3. Implement `print_evaluation_report()`

### Testing
```python
from src.evaluation import evaluate_classification, print_evaluation_report
import numpy as np

y_true = np.array([0, 1, 1, 0, 1])
y_pred = np.array([0, 1, 0, 0, 1])
metrics = evaluate_classification(y_true, y_pred)
print_evaluation_report(metrics)
```

### Cursor Prompt
```
Create src/evaluation.py with:

1. evaluate_classification(y_true, y_pred) -> dict
   - Calculate accuracy, precision, recall, f1, confusion_matrix
   - Use sklearn.metrics functions
   - Return as dictionary

2. print_evaluation_report(metrics) -> None
   - Pretty-print all metrics
   - Format confusion matrix nicely

Follow specs in docs/phase-0/COMPONENT_SPECS.md section 5.
```

---

## 8. Visualization

**File**: `src/visualization.py`

### Implementation Steps

1. Import matplotlib/plotly
2. Implement `plot_price_history()`
3. Implement `plot_features()`
4. Implement `plot_price_with_predictions()`
5. Implement `plot_confusion_matrix()`
6. Implement `plot_feature_importance()` (optional)

### Cursor Prompt
```
Create src/visualization.py with:

1. plot_price_history(df, ticker) - line chart of closing prices
2. plot_features(df) - subplot grid of all features
3. plot_price_with_predictions(df, predictions, ticker) - price with buy/sell markers
4. plot_confusion_matrix(y_true, y_pred) - heatmap of confusion matrix
5. plot_feature_importance(model, feature_names) - bar chart (if model has feature_importances_)

Use matplotlib or plotly. Save figures to docs/figures/.
Follow specs in docs/phase-0/COMPONENT_SPECS.md section 6.
```

---

## 9. Main Pipeline

**File**: `main.py`

### Implementation Steps

1. Import all modules
2. Create main() function
3. Implement data loading loop
4. Implement feature engineering
5. Implement train/test split (time-based)
6. Implement model training
7. Implement evaluation
8. Implement visualization
9. Add command-line argument parsing (optional)

### Structure
```python
def main():
    # Load config
    # For each ticker:
    #   1. Load data
    #   2. Engineer features
    #   3. Split train/test by date
    #   4. Train model
    #   5. Predict
    #   6. Evaluate
    #   7. Visualize
    # Print summary

if __name__ == "__main__":
    main()
```

### Cursor Prompt
```
Create main.py that orchestrates the entire pipeline:

1. Import config and all modules
2. Create main() function that:
   - Loops through config.TICKERS
   - Fetches/loads data using data_loader
   - Engineers features using features.py
   - Splits data by config.TEST_SPLIT_DATE
   - Trains model using model.py
   - Evaluates using evaluation.py
   - Visualizes using visualization.py
   - Saves model
3. Add proper logging/print statements
4. Add error handling for each ticker

Follow the data flow in docs/phase-0/PHASE_0_SDD.md section 6.
```

---

## 10. Documentation & Cleanup

### Tasks

1. **Create README for Phase 0**
   ```bash
   # Document how to run main.py
   # Include sample output
   # Add troubleshooting section
   ```

2. **Create Jupyter Notebooks**
   - `notebooks/01_exploration.ipynb` - Data exploration
   - `notebooks/02_feature_engineering.ipynb` - Feature analysis
   - `notebooks/03_modeling.ipynb` - Model training and evaluation

3. **Update Project Status**
   - Mark Phase 0 tasks as complete in `docs/tracking/TODO.md`
   - Update `docs/tracking/PROJECT_STATUS.md`
   - Update `docs/tracking/FEATURES.md`
   - Add entry to `docs/tracking/CHANGELOG.md`

4. **Code Quality**
   ```bash
   # Format code
   black src/ main.py

   # Run linter
   flake8 src/ main.py

   # Run tests
   pytest tests/ -v
   ```

5. **Git Commit**
   ```bash
   git add .
   git commit -m "feat(phase-0): complete MVP implementation

   - Data loader with yfinance integration
   - Feature engineering (returns, MAs, volatility)
   - Logistic Regression and Random Forest models
   - Evaluation metrics and confusion matrix
   - Visualization of predictions
   - End-to-end pipeline in main.py

   Closes #1"

   git push origin main
   ```

---

## Validation Checklist

Before marking Phase 0 complete:

- [ ] `python main.py` runs without errors
- [ ] At least 1 asset produces predictions
- [ ] Accuracy metric is displayed
- [ ] Confusion matrix is generated
- [ ] Price chart with predictions exists
- [ ] Model is saved to `models/` directory
- [ ] All tests pass: `pytest tests/`
- [ ] Code is formatted: `black src/ main.py`
- [ ] Documentation is updated
- [ ] Git commit pushed to GitHub

---

## Common Issues & Solutions

### Issue: yfinance download fails
**Solution**: Check internet connection, try different date range

### Issue: NaN values in features
**Solution**: Increase START_DATE to account for rolling windows

### Issue: Model accuracy is ~50%
**Solution**: This is expected for Phase 0. Focus is on pipeline, not performance.

### Issue: Plots don't show
**Solution**: Add `plt.show()` or save to file instead

---

**Next**: Once Phase 0 is complete, move to Phase 1 SDD for backtesting implementation.

**Last Updated**: 2026-02-12
