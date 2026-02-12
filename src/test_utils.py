"""
Test Utilities for generating sample data.
Used for testing when yfinance is unavailable or for unit tests.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_price_data(
    ticker: str = "TEST",
    start_date: str = "2020-01-01",
    n_days: int = 1000,
    initial_price: float = 100.0,
    volatility: float = 0.02
) -> pd.DataFrame:
    """
    Generate realistic synthetic stock price data for testing.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        n_days: Number of trading days to generate
        initial_price: Starting price
        volatility: Daily volatility (std dev of returns)

    Returns:
        DataFrame with OHLCV data indexed by date
    """
    np.random.seed(42)  # For reproducibility

    # Generate dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    dates = pd.date_range(start=start, periods=n_days, freq='D')

    # Generate returns (random walk)
    returns = np.random.normal(0.0005, volatility, n_days)  # Slight positive drift
    prices = initial_price * (1 + returns).cumprod()

    # Generate OHLCV data
    data = {
        'Open': prices * (1 + np.random.normal(0, 0.005, n_days)),
        'High': prices * (1 + np.abs(np.random.normal(0.01, 0.005, n_days))),
        'Low': prices * (1 - np.abs(np.random.normal(0.01, 0.005, n_days))),
        'Close': prices,
        'Volume': np.random.randint(1_000_000, 10_000_000, n_days)
    }

    df = pd.DataFrame(data, index=dates)

    # Ensure High is highest and Low is lowest
    df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
    df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)

    return df


if __name__ == "__main__":
    # Test sample data generation
    df = generate_sample_price_data("TEST", n_days=252)
    print("Sample data generated:")
    print(df.head(10))
    print(f"\nShape: {df.shape}")
    print(f"Date range: {df.index.min()} to {df.index.max()}")
