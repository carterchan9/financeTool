"""
Data Loader Module for Phase 0 MVP.

This module handles:
- Fetching historical stock price data from yfinance
- Caching data locally to avoid repeated downloads
- Loading previously cached data

Functions:
    fetch_price_data: Download historical OHLCV data
    save_raw_data: Save DataFrame to CSV
    load_cached_data: Load previously cached data
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
from typing import Optional
import logging

from src.config import RAW_DATA_PATH

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_price_data(
    ticker: str,
    start: str,
    end: str,
    use_cache: bool = True
) -> Optional[pd.DataFrame]:
    """
    Fetch historical OHLCV data for a given ticker.

    This function first checks if cached data exists. If not (or if use_cache=False),
    it downloads fresh data from yfinance and caches it.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "SPY")
        start: Start date in YYYY-MM-DD format
        end: End date in YYYY-MM-DD format
        use_cache: If True, try to load from cache first

    Returns:
        DataFrame with columns: Open, High, Low, Close, Adj Close, Volume
        Indexed by date. Returns None if fetch fails.

    Example:
        >>> df = fetch_price_data("AAPL", "2020-01-01", "2023-12-31")
        >>> print(df.head())
    """
    # Try to load from cache first
    if use_cache:
        cached_df = load_cached_data(ticker)
        if cached_df is not None:
            logger.info(f"Loaded cached data for {ticker}")
            return cached_df

    # Download data from yfinance
    logger.info(f"Fetching data for {ticker} from {start} to {end}...")

    try:
        # Download data
        stock = yf.Ticker(ticker)
        df = stock.history(start=start, end=end)

        # Check if data is empty
        if df.empty:
            logger.warning(f"No data returned for {ticker}. Ticker may be invalid.")
            return None

        # Remove timezone info if present
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        logger.info(f"Successfully fetched {len(df)} rows for {ticker}")

        # Save to cache
        save_raw_data(df, ticker)

        return df

    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return None


def save_raw_data(df: pd.DataFrame, ticker: str) -> None:
    """
    Save raw price data to CSV file.

    Args:
        df: DataFrame containing price data
        ticker: Stock ticker symbol (used for filename)

    Example:
        >>> save_raw_data(df, "AAPL")
        # Saves to data/raw/AAPL_raw.csv
    """
    # Create directory if it doesn't exist
    data_dir = Path(RAW_DATA_PATH)
    data_dir.mkdir(parents=True, exist_ok=True)

    # Define file path
    file_path = data_dir / f"{ticker}_raw.csv"

    # Save to CSV
    df.to_csv(file_path)
    logger.info(f"Saved raw data to {file_path}")


def load_cached_data(ticker: str) -> Optional[pd.DataFrame]:
    """
    Load previously cached data from CSV file.

    Args:
        ticker: Stock ticker symbol

    Returns:
        DataFrame with price data if file exists, None otherwise

    Example:
        >>> df = load_cached_data("AAPL")
        >>> if df is not None:
        ...     print("Cached data loaded")
    """
    file_path = Path(RAW_DATA_PATH) / f"{ticker}_raw.csv"

    if not file_path.exists():
        logger.debug(f"No cached data found for {ticker}")
        return None

    try:
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)
        logger.info(f"Loaded {len(df)} rows from cache for {ticker}")
        return df

    except Exception as e:
        logger.error(f"Error loading cached data for {ticker}: {e}")
        return None


def get_data_info(df: pd.DataFrame) -> dict:
    """
    Get summary information about the dataset.

    Args:
        df: DataFrame with price data

    Returns:
        Dictionary with dataset statistics

    Example:
        >>> info = get_data_info(df)
        >>> print(f"Data spans {info['n_days']} days")
    """
    return {
        "n_rows": len(df),
        "start_date": df.index.min(),
        "end_date": df.index.max(),
        "n_days": (df.index.max() - df.index.min()).days,
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict()
    }


def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate that the DataFrame contains required columns and valid data.

    Args:
        df: DataFrame to validate

    Returns:
        True if valid, raises ValueError if invalid

    Raises:
        ValueError: If data is invalid
    """
    required_columns = ["Open", "High", "Low", "Close", "Volume"]

    # Check for required columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Check for empty DataFrame
    if df.empty:
        raise ValueError("DataFrame is empty")

    # Check for all NaN values
    if df["Close"].isna().all():
        raise ValueError("Close column contains only NaN values")

    # Check for negative prices
    if (df["Close"] < 0).any():
        raise ValueError("Close column contains negative values")

    return True


# Convenience function to load multiple tickers
def fetch_multiple_tickers(
    tickers: list,
    start: str,
    end: str,
    use_cache: bool = True
) -> dict:
    """
    Fetch data for multiple tickers.

    Args:
        tickers: List of ticker symbols
        start: Start date in YYYY-MM-DD format
        end: End date in YYYY-MM-DD format
        use_cache: If True, use cached data when available

    Returns:
        Dictionary mapping ticker to DataFrame

    Example:
        >>> data = fetch_multiple_tickers(["AAPL", "SPY"], "2020-01-01", "2023-12-31")
        >>> print(f"Loaded {len(data)} tickers")
    """
    data_dict = {}

    for ticker in tickers:
        logger.info(f"\nProcessing {ticker}...")
        df = fetch_price_data(ticker, start, end, use_cache)

        if df is not None:
            try:
                validate_data(df)
                data_dict[ticker] = df
                logger.info(f"✅ {ticker}: {len(df)} rows loaded")
            except ValueError as e:
                logger.warning(f"❌ {ticker}: Validation failed - {e}")
        else:
            logger.warning(f"❌ {ticker}: Failed to fetch data")

    return data_dict


if __name__ == "__main__":
    # Test the data loader
    print("Testing Data Loader Module")
    print("=" * 60)

    # Test fetching single ticker
    print("\n1. Testing single ticker fetch (AAPL)...")
    df = fetch_price_data("AAPL", "2020-01-01", "2023-12-31", use_cache=False)

    if df is not None:
        print(f"✅ Successfully fetched {len(df)} rows")
        print(f"\nFirst 5 rows:")
        print(df.head())
        print(f"\nData info:")
        info = get_data_info(df)
        for key, value in info.items():
            if key != "missing_values":
                print(f"  {key}: {value}")
    else:
        print("❌ Failed to fetch data")

    # Test loading from cache
    print("\n2. Testing cache loading...")
    df_cached = load_cached_data("AAPL")
    if df_cached is not None:
        print(f"✅ Successfully loaded {len(df_cached)} rows from cache")

    # Test multiple tickers
    print("\n3. Testing multiple tickers...")
    data = fetch_multiple_tickers(["AAPL", "SPY"], "2023-01-01", "2023-12-31")
    print(f"\n✅ Loaded {len(data)} tickers successfully")

    print("\n" + "=" * 60)
    print("Data Loader Module test complete!")
