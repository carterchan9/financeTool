# Phase 0 Component Specifications

Detailed specifications for each component in Phase 0 MVP.

---

## 1. Configuration (`src/config.py`)

### Purpose
Centralize all configuration parameters for easy modification and experimentation.

### Implementation

```python
"""
Configuration file for Phase 0 MVP.
All parameters for data, features, and models.
"""

# Data Configuration
TICKERS = ["AAPL", "SPY"]
START_DATE = "2015-01-01"
END_DATE = "2024-12-31"

# Train/Test Split
TEST_SPLIT_DATE = "2022-01-01"

# Feature Engineering
MA_WINDOWS = [5, 20]
VOLATILITY_WINDOW = 20

# Model Configuration
MODEL_TYPE = "logistic"  # Options: "logistic", "random_forest"
RANDOM_SEED = 42

# Paths
RAW_DATA_PATH = "data/raw"
PROCESSED_DATA_PATH = "data/processed"
MODEL_PATH = "models"

# Model Hyperparameters
LOGISTIC_PARAMS = {
    "max_iter": 1000,
    "random_state": RANDOM_SEED
}

RANDOM_FOREST_PARAMS = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": RANDOM_SEED
}
```

---

## 2. Data Loader (`src/data_loader.py`)

### Purpose
Handle all data fetching, caching, and loading operations.

### Functions

#### `fetch_price_data(ticker: str, start: str, end: str) -> pd.DataFrame`

**Description**: Fetch historical OHLCV data from yfinance.

**Parameters**:
- `ticker`: Stock ticker symbol (e.g., "AAPL")
- `start`: Start date in YYYY-MM-DD format
- `end`: End date in YYYY-MM-DD format

**Returns**: DataFrame with columns: `['Open', 'High', 'Low', 'Close', 'Volume']`

**Example**:
```python
df = fetch_price_data("AAPL", "2020-01-01", "2023-12-31")
```

#### `save_raw_data(df: pd.DataFrame, ticker: str) -> None`

**Description**: Save raw data to CSV file.

**Parameters**:
- `df`: DataFrame to save
- `ticker`: Stock ticker for filename

#### `load_cached_data(ticker: str) -> pd.DataFrame`

**Description**: Load previously cached data if available.

**Parameters**:
- `ticker`: Stock ticker symbol

**Returns**: DataFrame or None if not found

---

## 3. Feature Engineering (`src/features.py`)

### Purpose
Transform raw price data into ML-ready features.

### Functions

#### `compute_returns(df: pd.DataFrame) -> pd.DataFrame`

**Description**: Calculate daily returns.

**Formula**: `return_t = (Close_t - Close_{t-1}) / Close_{t-1}`

**Returns**: DataFrame with new column `'returns'`

#### `compute_moving_averages(df: pd.DataFrame, windows: List[int]) -> pd.DataFrame`

**Description**: Calculate moving averages for specified windows.

**Parameters**:
- `df`: Input DataFrame
- `windows`: List of window sizes (e.g., [5, 20])

**Returns**: DataFrame with columns `'ma_5'`, `'ma_20'`, etc.

#### `compute_volatility(df: pd.DataFrame, window: int) -> pd.DataFrame`

**Description**: Calculate rolling volatility (standard deviation).

**Parameters**:
- `df`: Input DataFrame
- `window`: Rolling window size

**Returns**: DataFrame with column `'volatility'`

#### `compute_price_relative_to_ma(df: pd.DataFrame) -> pd.DataFrame`

**Description**: Calculate price position relative to moving average.

**Formula**: `(Close - MA_20) / MA_20`

**Returns**: DataFrame with column `'price_to_ma'`

#### `generate_target(df: pd.DataFrame) -> pd.DataFrame`

**Description**: Generate binary target variable for next-day direction.

**Formula**:
```python
target = 1 if next_day_return > 0 else 0
```

**Returns**: DataFrame with column `'target'`

#### `compute_features(df: pd.DataFrame) -> pd.DataFrame`

**Description**: Main function that orchestrates all feature engineering.

**Returns**: DataFrame with all features and target

---

## 4. Model Training (`src/model.py`)

### Purpose
Train, save, and load ML models.

### Functions

#### `train_logistic_regression(X_train, y_train, params: dict)`

**Description**: Train logistic regression model.

**Parameters**:
- `X_train`: Training features
- `y_train`: Training labels
- `params`: Model hyperparameters

**Returns**: Trained model object

#### `train_random_forest(X_train, y_train, params: dict)`

**Description**: Train random forest classifier.

**Parameters**:
- `X_train`: Training features
- `y_train`: Training labels
- `params`: Model hyperparameters

**Returns**: Trained model object

#### `train_model(X_train, y_train, model_type: str = "logistic")`

**Description**: Main training function that dispatches to specific model trainers.

**Parameters**:
- `X_train`: Training features
- `y_train`: Training labels
- `model_type`: "logistic" or "random_forest"

**Returns**: Trained model

#### `save_model(model, ticker: str, model_type: str) -> None`

**Description**: Save trained model to disk.

**Parameters**:
- `model`: Trained model object
- `ticker`: Stock ticker for filename
- `model_type`: Model type for filename

#### `load_model(ticker: str, model_type: str)`

**Description**: Load previously trained model.

**Returns**: Model object or None if not found

#### `predict(model, X_test) -> np.ndarray`

**Description**: Generate predictions from trained model.

**Returns**: Array of predictions (0 or 1)

---

## 5. Evaluation (`src/evaluation.py`)

### Purpose
Evaluate model performance with comprehensive metrics.

### Functions

#### `evaluate_classification(y_true, y_pred) -> dict`

**Description**: Calculate classification metrics.

**Returns**: Dictionary with:
- `accuracy`: Overall accuracy
- `precision`: Precision score
- `recall`: Recall score
- `f1`: F1 score
- `confusion_matrix`: Confusion matrix

**Example**:
```python
metrics = evaluate_classification(y_test, predictions)
print(f"Accuracy: {metrics['accuracy']:.3f}")
```

#### `print_evaluation_report(metrics: dict) -> None`

**Description**: Pretty-print evaluation metrics.

**Parameters**:
- `metrics`: Dictionary from `evaluate_classification`

---

## 6. Visualization (`src/visualization.py`)

### Purpose
Create informative visualizations of data and results.

### Functions

#### `plot_price_history(df: pd.DataFrame, ticker: str) -> None`

**Description**: Plot closing price over time.

**Parameters**:
- `df`: DataFrame with price data
- `ticker`: Stock ticker for title

#### `plot_features(df: pd.DataFrame) -> None`

**Description**: Plot all engineered features.

**Parameters**:
- `df`: DataFrame with features

#### `plot_price_with_predictions(df: pd.DataFrame, predictions: np.ndarray, ticker: str) -> None`

**Description**: Plot price with buy/sell markers based on predictions.

**Parameters**:
- `df`: DataFrame with price data
- `predictions`: Array of predictions
- `ticker`: Stock ticker

#### `plot_confusion_matrix(y_true, y_pred) -> None`

**Description**: Visualize confusion matrix as heatmap.

**Parameters**:
- `y_true`: True labels
- `y_pred`: Predicted labels

#### `plot_feature_importance(model, feature_names: List[str]) -> None`

**Description**: Plot feature importance (for tree-based models).

**Parameters**:
- `model`: Trained model with `feature_importances_` attribute
- `feature_names`: List of feature names

---

## 7. Main Pipeline (`main.py`)

### Purpose
Orchestrate the entire ML pipeline from data to results.

### Workflow

```python
1. Load configuration
2. For each ticker:
   a. Fetch/load data
   b. Engineer features
   c. Split train/test
   d. Train model
   e. Generate predictions
   f. Evaluate performance
   g. Create visualizations
3. Save results and models
```

### Expected Output

```
Loading data for AAPL...
Engineering features...
Training logistic regression model...
Evaluating model...

Results for AAPL:
==================
Accuracy: 0.532
Precision: 0.545
Recall: 0.621
F1 Score: 0.580

Saving model...
Creating visualizations...

Done!
```

---

## Data Schemas

### Raw Data Schema
```
Date (index) | Open | High | Low | Close | Volume
-------------|------|------|-----|-------|-------
2020-01-01   | 75.1 | 76.2 | 74.9| 76.0  | 1.2M
```

### Processed Data Schema
```
Date | Close | returns | ma_5 | ma_20 | volatility | price_to_ma | target
-----|-------|---------|------|-------|------------|-------------|-------
2020-01-01 | 76.0 | 0.012 | 75.5 | 74.8 | 0.018 | 0.016 | 1
```

---

## Error Handling

### Expected Errors
- **Network Issues**: yfinance download failure
- **Missing Data**: Ticker not found or delisted
- **Insufficient Data**: Not enough history for features
- **NaN Values**: Rolling calculations creating NaNs

### Handling Strategy
- Retry logic for network failures
- Graceful skip for missing tickers
- Minimum data requirement checks
- Forward-fill or drop NaN rows

---

**Last Updated**: 2026-02-12
