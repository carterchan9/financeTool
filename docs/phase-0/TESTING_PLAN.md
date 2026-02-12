# Phase 0 Testing Plan

Comprehensive testing strategy for Phase 0 MVP.

---

## Testing Philosophy

- **Test critical paths**: Data loading, feature engineering, model training
- **Keep it simple**: Focus on functionality, not edge cases
- **Fast feedback**: Tests should run in <10 seconds
- **Practical**: Test what matters for the pipeline

---

## Test Structure

```
tests/
├── __init__.py
├── test_config.py
├── test_data_loader.py
├── test_features.py
├── test_model.py
├── test_evaluation.py
└── test_integration.py
```

---

## Unit Tests

### 1. Test Configuration (`test_config.py`)

```python
"""Test configuration values are valid."""

def test_config_imports():
    from src.config import TICKERS, START_DATE, END_DATE
    assert TICKERS is not None
    assert len(TICKERS) > 0

def test_date_format():
    from src.config import START_DATE, END_DATE
    from datetime import datetime
    # Ensure dates are parseable
    datetime.strptime(START_DATE, "%Y-%m-%d")
    datetime.strptime(END_DATE, "%Y-%m-%d")

def test_model_params():
    from src.config import LOGISTIC_PARAMS, RANDOM_FOREST_PARAMS
    assert "random_state" in LOGISTIC_PARAMS
    assert "random_state" in RANDOM_FOREST_PARAMS
```

---

### 2. Test Data Loader (`test_data_loader.py`)

```python
"""Test data loading functionality."""
import pytest
import pandas as pd
from src.data_loader import fetch_price_data, save_raw_data, load_cached_data

def test_fetch_price_data():
    """Test fetching data from yfinance."""
    df = fetch_price_data("AAPL", "2023-01-01", "2023-01-31")

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns
    assert "Open" in df.columns
    assert len(df) > 0

def test_fetch_invalid_ticker():
    """Test handling of invalid ticker."""
    # Should handle gracefully, not crash
    df = fetch_price_data("INVALID_TICKER_XYZ", "2023-01-01", "2023-01-31")
    # Implementation should return empty DataFrame or raise ValueError
    assert df is None or df.empty

def test_save_and_load_data():
    """Test saving and loading cached data."""
    # Fetch data
    df = fetch_price_data("AAPL", "2023-01-01", "2023-01-31")

    # Save data
    save_raw_data(df, "AAPL_test")

    # Load data
    df_loaded = load_cached_data("AAPL_test")

    assert df_loaded is not None
    assert len(df_loaded) == len(df)
```

---

### 3. Test Feature Engineering (`test_features.py`)

```python
"""Test feature engineering functions."""
import pandas as pd
import numpy as np
from src.features import (
    compute_returns,
    compute_moving_averages,
    compute_volatility,
    generate_target,
    compute_features
)

@pytest.fixture
def sample_price_data():
    """Create sample price data for testing."""
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    prices = np.random.randn(100).cumsum() + 100
    return pd.DataFrame({
        "Close": prices,
        "Open": prices * 0.99,
        "High": prices * 1.01,
        "Low": prices * 0.98,
        "Volume": np.random.randint(1e6, 1e7, 100)
    }, index=dates)

def test_compute_returns(sample_price_data):
    """Test daily returns calculation."""
    df = compute_returns(sample_price_data)

    assert "returns" in df.columns
    assert not df["returns"].isna().all()
    # Returns should be roughly between -10% and +10% daily
    assert df["returns"].abs().max() < 0.5

def test_compute_moving_averages(sample_price_data):
    """Test moving average calculation."""
    df = compute_moving_averages(sample_price_data, windows=[5, 20])

    assert "ma_5" in df.columns
    assert "ma_20" in df.columns
    # MAs should be close to price
    assert (df["ma_5"] - df["Close"]).abs().mean() < df["Close"].mean() * 0.1

def test_compute_volatility(sample_price_data):
    """Test volatility calculation."""
    df = compute_returns(sample_price_data)
    df = compute_volatility(df, window=20)

    assert "volatility" in df.columns
    assert df["volatility"].min() >= 0  # Volatility should be non-negative

def test_generate_target(sample_price_data):
    """Test target generation."""
    df = compute_returns(sample_price_data)
    df = generate_target(df)

    assert "target" in df.columns
    assert set(df["target"].dropna().unique()).issubset({0, 1})

def test_compute_features(sample_price_data):
    """Test full feature pipeline."""
    df = compute_features(sample_price_data)

    # Check all expected columns exist
    expected_cols = ["returns", "ma_5", "ma_20", "volatility", "target"]
    for col in expected_cols:
        assert col in df.columns

    # Should have dropped NaN rows
    assert not df.isna().any().any()
```

---

### 4. Test Model Training (`test_model.py`)

```python
"""Test model training and prediction."""
import numpy as np
from sklearn.datasets import make_classification
from src.model import train_model, predict, save_model, load_model

@pytest.fixture
def sample_classification_data():
    """Create sample classification data."""
    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    return X, y

def test_train_logistic_regression(sample_classification_data):
    """Test logistic regression training."""
    X, y = sample_classification_data
    model = train_model(X, y, model_type="logistic")

    assert model is not None
    assert hasattr(model, "predict")

def test_train_random_forest(sample_classification_data):
    """Test random forest training."""
    X, y = sample_classification_data
    model = train_model(X, y, model_type="random_forest")

    assert model is not None
    assert hasattr(model, "predict")
    assert hasattr(model, "feature_importances_")

def test_predict(sample_classification_data):
    """Test prediction."""
    X, y = sample_classification_data
    model = train_model(X, y, model_type="logistic")
    predictions = predict(model, X)

    assert len(predictions) == len(y)
    assert set(predictions).issubset({0, 1})

def test_save_and_load_model(sample_classification_data):
    """Test model persistence."""
    X, y = sample_classification_data
    model = train_model(X, y, model_type="logistic")

    # Save model
    save_model(model, "TEST", "logistic")

    # Load model
    loaded_model = load_model("TEST", "logistic")

    assert loaded_model is not None
    # Predictions should match
    pred1 = predict(model, X[:10])
    pred2 = predict(loaded_model, X[:10])
    assert np.array_equal(pred1, pred2)
```

---

### 5. Test Evaluation (`test_evaluation.py`)

```python
"""Test evaluation metrics."""
import numpy as np
from src.evaluation import evaluate_classification

def test_evaluate_classification():
    """Test evaluation metrics calculation."""
    y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
    y_pred = np.array([0, 1, 0, 0, 1, 1, 1, 0])

    metrics = evaluate_classification(y_true, y_pred)

    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "confusion_matrix" in metrics

    # Metrics should be between 0 and 1
    assert 0 <= metrics["accuracy"] <= 1
    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert 0 <= metrics["f1"] <= 1

def test_perfect_predictions():
    """Test metrics with perfect predictions."""
    y_true = np.array([0, 1, 1, 0, 1, 0])
    y_pred = np.array([0, 1, 1, 0, 1, 0])

    metrics = evaluate_classification(y_true, y_pred)

    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0
```

---

## Integration Tests

### Test End-to-End Pipeline (`test_integration.py`)

```python
"""Integration tests for full pipeline."""
import pytest
from src.data_loader import fetch_price_data
from src.features import compute_features
from src.model import train_model, predict
from src.evaluation import evaluate_classification
from sklearn.model_selection import train_test_split

def test_full_pipeline():
    """Test complete pipeline from data to predictions."""
    # 1. Fetch data
    df = fetch_price_data("AAPL", "2020-01-01", "2023-12-31")
    assert not df.empty

    # 2. Engineer features
    df_features = compute_features(df)
    assert "target" in df_features.columns

    # 3. Prepare train/test split
    X = df_features.drop("target", axis=1)
    y = df_features["target"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # 4. Train model
    model = train_model(X_train, y_train, model_type="logistic")
    assert model is not None

    # 5. Predict
    predictions = predict(model, X_test)
    assert len(predictions) == len(y_test)

    # 6. Evaluate
    metrics = evaluate_classification(y_test, predictions)
    assert "accuracy" in metrics
    # Accuracy should be reasonable (better than random)
    assert metrics["accuracy"] > 0.4

@pytest.mark.slow
def test_multiple_tickers():
    """Test pipeline works for multiple tickers."""
    tickers = ["AAPL", "SPY"]

    for ticker in tickers:
        df = fetch_price_data(ticker, "2022-01-01", "2023-12-31")
        assert not df.empty

        df_features = compute_features(df)
        assert "target" in df_features.columns
```

---

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_data_loader.py -v
```

### Run with Coverage
```bash
pytest --cov=src tests/
```

### Run Only Fast Tests (Skip Slow)
```bash
pytest tests/ -v -m "not slow"
```

---

## Test Coverage Goals

- **Data Loader**: 80%+ coverage
- **Features**: 90%+ coverage
- **Model**: 70%+ coverage
- **Evaluation**: 90%+ coverage
- **Overall**: 75%+ coverage

---

## Continuous Testing

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
echo "Running tests..."
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

### GitHub Actions (Future)

Create `.github/workflows/test.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

---

## Manual Testing Checklist

Before Phase 0 completion:

- [ ] Run `python main.py` successfully
- [ ] Verify output files created:
  - [ ] `data/raw/*.csv`
  - [ ] `data/processed/*.csv`
  - [ ] `models/*.pkl`
  - [ ] `docs/figures/*.png`
- [ ] Check console output shows metrics
- [ ] Verify plots are generated and meaningful
- [ ] Test with different tickers
- [ ] Test with different date ranges

---

**Last Updated**: 2026-02-12
