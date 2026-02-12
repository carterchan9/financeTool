"""
Feature Engineering Module for Phase 0 MVP.

This module transforms raw price data into ML-ready features including:
- Daily returns
- Moving averages
- Volatility
- Price relative to moving average
- Binary target variable (next-day direction)

Functions:
    compute_returns: Calculate daily returns
    compute_moving_averages: Calculate MAs for multiple windows
    compute_volatility: Calculate rolling volatility
    compute_price_relative_to_ma: Price position relative to MA
    generate_target: Create binary target variable
    compute_features: Main orchestrator function
"""

import pandas as pd
import numpy as np
from typing import List
import logging

from src.config import MA_WINDOWS, VOLATILITY_WINDOW, FEATURE_NAMES, TARGET_NAME

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily returns from closing prices.

    Formula: return_t = (Close_t - Close_{t-1}) / Close_{t-1}

    Args:
        df: DataFrame with 'Close' column

    Returns:
        DataFrame with additional 'returns' column

    Example:
        >>> df = compute_returns(df)
        >>> print(df['returns'].head())
    """
    df = df.copy()
    df['returns'] = df['Close'].pct_change()
    logger.debug(f"Computed returns: {df['returns'].describe()}")
    return df


def compute_moving_averages(
    df: pd.DataFrame,
    windows: List[int] = None
) -> pd.DataFrame:
    """
    Calculate moving averages for specified windows.

    Args:
        df: DataFrame with 'Close' column
        windows: List of window sizes (e.g., [5, 20]). If None, uses config.MA_WINDOWS

    Returns:
        DataFrame with additional 'ma_{window}' columns

    Example:
        >>> df = compute_moving_averages(df, windows=[5, 20])
        >>> print(df[['Close', 'ma_5', 'ma_20']].head(25))
    """
    if windows is None:
        windows = MA_WINDOWS

    df = df.copy()

    for window in windows:
        col_name = f'ma_{window}'
        df[col_name] = df['Close'].rolling(window=window).mean()
        logger.debug(f"Computed {window}-day MA: {col_name}")

    return df


def compute_volatility(
    df: pd.DataFrame,
    window: int = None
) -> pd.DataFrame:
    """
    Calculate rolling volatility (standard deviation of returns).

    Args:
        df: DataFrame with 'returns' column
        window: Rolling window size. If None, uses config.VOLATILITY_WINDOW

    Returns:
        DataFrame with additional 'volatility' column

    Example:
        >>> df = compute_returns(df)
        >>> df = compute_volatility(df, window=20)
        >>> print(df['volatility'].head(25))
    """
    if window is None:
        window = VOLATILITY_WINDOW

    df = df.copy()

    if 'returns' not in df.columns:
        df = compute_returns(df)

    df['volatility'] = df['returns'].rolling(window=window).std()
    logger.debug(f"Computed {window}-day volatility")

    return df


def compute_price_relative_to_ma(
    df: pd.DataFrame,
    ma_column: str = 'ma_20'
) -> pd.DataFrame:
    """
    Calculate price position relative to moving average.

    Formula: (Close - MA) / MA

    This indicates whether price is above (positive) or below (negative)
    the moving average, normalized by the MA value.

    Args:
        df: DataFrame with 'Close' and moving average column
        ma_column: Name of MA column to use (default: 'ma_20')

    Returns:
        DataFrame with additional 'price_to_ma' column

    Example:
        >>> df = compute_price_relative_to_ma(df)
        >>> print(df['price_to_ma'].describe())
    """
    df = df.copy()

    if ma_column not in df.columns:
        # Extract window from column name (e.g., 'ma_20' -> 20)
        window = int(ma_column.split('_')[1])
        df = compute_moving_averages(df, windows=[window])

    df['price_to_ma'] = (df['Close'] - df[ma_column]) / df[ma_column]
    logger.debug("Computed price relative to MA")

    return df


def generate_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate binary target variable for next-day direction prediction.

    Target = 1 if next day's return is positive, 0 otherwise.

    Args:
        df: DataFrame with 'returns' column

    Returns:
        DataFrame with additional 'target' column

    Example:
        >>> df = generate_target(df)
        >>> print(df['target'].value_counts())
    """
    df = df.copy()

    if 'returns' not in df.columns:
        df = compute_returns(df)

    # Shift returns by -1 to get next day's return
    next_day_return = df['returns'].shift(-1)

    # Create binary target: 1 if next day goes up, 0 otherwise
    df[TARGET_NAME] = (next_day_return > 0).astype(int)

    logger.debug(f"Generated target variable: {df[TARGET_NAME].value_counts().to_dict()}")

    return df


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main feature engineering pipeline.

    Orchestrates all feature computations and cleans the resulting DataFrame.

    Steps:
        1. Compute daily returns
        2. Compute moving averages
        3. Compute volatility
        4. Compute price relative to MA
        5. Generate target variable
        6. Drop rows with NaN values
        7. Select only feature columns and target

    Args:
        df: Raw DataFrame with OHLCV data

    Returns:
        Clean DataFrame with engineered features and target

    Example:
        >>> df_features = compute_features(df_raw)
        >>> print(df_features.head())
        >>> print(f"Features: {df_features.columns.tolist()}")
    """
    logger.info("Starting feature engineering...")

    # Make a copy to avoid modifying original
    df = df.copy()

    # Compute all features
    df = compute_returns(df)
    df = compute_moving_averages(df, windows=MA_WINDOWS)
    df = compute_volatility(df, window=VOLATILITY_WINDOW)
    df = compute_price_relative_to_ma(df)
    df = generate_target(df)

    # Log NaN counts before dropping
    nan_counts = df[FEATURE_NAMES + [TARGET_NAME]].isna().sum()
    logger.info(f"NaN counts before dropping:\n{nan_counts}")

    # Drop rows with NaN values (caused by rolling calculations)
    initial_rows = len(df)
    df = df.dropna(subset=FEATURE_NAMES + [TARGET_NAME])
    final_rows = len(df)

    logger.info(f"Dropped {initial_rows - final_rows} rows with NaN values")
    logger.info(f"Final dataset: {final_rows} rows")

    # Select only the feature columns and target
    feature_cols = FEATURE_NAMES + [TARGET_NAME]
    df_features = df[feature_cols].copy()

    # Validate the result
    validate_features(df_features)

    logger.info("Feature engineering complete!")

    return df_features


def validate_features(df: pd.DataFrame) -> bool:
    """
    Validate that the feature DataFrame is properly formed.

    Checks:
        - No NaN values
        - No infinite values
        - Target is binary (0 or 1)
        - Sufficient data points

    Args:
        df: DataFrame with engineered features

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    # Check for NaN values
    if df.isna().any().any():
        nan_cols = df.columns[df.isna().any()].tolist()
        raise ValueError(f"Features contain NaN values in columns: {nan_cols}")

    # Check for infinite values
    if np.isinf(df.select_dtypes(include=[np.number])).any().any():
        inf_cols = df.columns[np.isinf(df.select_dtypes(include=[np.number])).any()].tolist()
        raise ValueError(f"Features contain infinite values in columns: {inf_cols}")

    # Check target is binary
    if TARGET_NAME in df.columns:
        unique_values = df[TARGET_NAME].unique()
        if not set(unique_values).issubset({0, 1}):
            raise ValueError(f"Target must be binary (0 or 1), found: {unique_values}")

    # Check sufficient data
    if len(df) < 50:
        raise ValueError(f"Insufficient data points: {len(df)} (minimum 50 required)")

    logger.debug("Feature validation passed")
    return True


def get_feature_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get statistical summary of features.

    Args:
        df: DataFrame with features

    Returns:
        DataFrame with descriptive statistics

    Example:
        >>> summary = get_feature_summary(df_features)
        >>> print(summary)
    """
    return df.describe()


if __name__ == "__main__":
    # Test feature engineering with sample data
    print("Testing Feature Engineering Module")
    print("=" * 60)

    from src.test_utils import generate_sample_price_data

    # Generate sample data
    print("\n1. Generating sample price data...")
    df_raw = generate_sample_price_data(n_days=500)
    print(f"✅ Generated {len(df_raw)} days of price data")

    # Test individual feature functions
    print("\n2. Testing individual feature functions...")

    # Returns
    df = compute_returns(df_raw)
    print(f"✅ Returns computed. Mean: {df['returns'].mean():.4f}")

    # Moving averages
    df = compute_moving_averages(df, windows=[5, 20])
    print(f"✅ Moving averages computed")

    # Volatility
    df = compute_volatility(df)
    print(f"✅ Volatility computed. Mean: {df['volatility'].mean():.4f}")

    # Price relative to MA
    df = compute_price_relative_to_ma(df)
    print(f"✅ Price-to-MA computed")

    # Target
    df = generate_target(df)
    print(f"✅ Target generated. Distribution: {df[TARGET_NAME].value_counts().to_dict()}")

    # Test full pipeline
    print("\n3. Testing full feature pipeline...")
    df_features = compute_features(df_raw)
    print(f"✅ Feature engineering complete")
    print(f"\nFeatures shape: {df_features.shape}")
    print(f"Feature columns: {df_features.columns.tolist()}")

    # Show summary
    print("\n4. Feature summary:")
    print(df_features.head(10))

    print("\n5. Descriptive statistics:")
    print(df_features.describe())

    print("\n" + "=" * 60)
    print("Feature Engineering Module test complete!")
