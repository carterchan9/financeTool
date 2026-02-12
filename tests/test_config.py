"""
Test configuration module.
Ensures all config values are valid and accessible.
"""

import pytest
from datetime import datetime


def test_config_imports():
    """Test that all required config values can be imported."""
    from src.config import (
        TICKERS,
        START_DATE,
        END_DATE,
        TEST_SPLIT_DATE,
        MA_WINDOWS,
        VOLATILITY_WINDOW,
        MODEL_TYPE,
        RANDOM_SEED,
        LOGISTIC_PARAMS,
        RANDOM_FOREST_PARAMS,
    )

    assert TICKERS is not None
    assert START_DATE is not None
    assert END_DATE is not None
    assert TEST_SPLIT_DATE is not None
    assert MA_WINDOWS is not None
    assert VOLATILITY_WINDOW is not None
    assert MODEL_TYPE is not None
    assert RANDOM_SEED is not None
    assert LOGISTIC_PARAMS is not None
    assert RANDOM_FOREST_PARAMS is not None


def test_tickers_not_empty():
    """Test that TICKERS list is not empty."""
    from src.config import TICKERS

    assert len(TICKERS) > 0
    assert all(isinstance(ticker, str) for ticker in TICKERS)
    assert all(len(ticker) > 0 for ticker in TICKERS)


def test_date_format():
    """Test that dates are in correct format and parseable."""
    from src.config import START_DATE, END_DATE, TEST_SPLIT_DATE

    # Test date format
    start = datetime.strptime(START_DATE, "%Y-%m-%d")
    end = datetime.strptime(END_DATE, "%Y-%m-%d")
    test_split = datetime.strptime(TEST_SPLIT_DATE, "%Y-%m-%d")

    # Test date order
    assert start < end, "START_DATE must be before END_DATE"
    assert start < test_split < end, "TEST_SPLIT_DATE must be between START_DATE and END_DATE"


def test_ma_windows():
    """Test that moving average windows are valid."""
    from src.config import MA_WINDOWS

    assert isinstance(MA_WINDOWS, list)
    assert len(MA_WINDOWS) > 0
    assert all(isinstance(w, int) for w in MA_WINDOWS)
    assert all(w > 0 for w in MA_WINDOWS)
    # Windows should be in ascending order
    assert MA_WINDOWS == sorted(MA_WINDOWS)


def test_volatility_window():
    """Test that volatility window is valid."""
    from src.config import VOLATILITY_WINDOW

    assert isinstance(VOLATILITY_WINDOW, int)
    assert VOLATILITY_WINDOW > 0


def test_model_type():
    """Test that model type is valid."""
    from src.config import MODEL_TYPE

    assert MODEL_TYPE in ["logistic", "random_forest"]


def test_random_seed():
    """Test that random seed is set."""
    from src.config import RANDOM_SEED

    assert isinstance(RANDOM_SEED, int)
    assert RANDOM_SEED >= 0


def test_model_params():
    """Test that model parameters contain required keys."""
    from src.config import LOGISTIC_PARAMS, RANDOM_FOREST_PARAMS, RANDOM_SEED

    # Logistic Regression params
    assert "random_state" in LOGISTIC_PARAMS
    assert LOGISTIC_PARAMS["random_state"] == RANDOM_SEED
    assert "max_iter" in LOGISTIC_PARAMS

    # Random Forest params
    assert "random_state" in RANDOM_FOREST_PARAMS
    assert RANDOM_FOREST_PARAMS["random_state"] == RANDOM_SEED
    assert "n_estimators" in RANDOM_FOREST_PARAMS


def test_paths_defined():
    """Test that all required paths are defined."""
    from src.config import (
        RAW_DATA_PATH,
        PROCESSED_DATA_PATH,
        MODEL_PATH,
        FIGURES_PATH,
    )

    assert RAW_DATA_PATH is not None
    assert PROCESSED_DATA_PATH is not None
    assert MODEL_PATH is not None
    assert FIGURES_PATH is not None


def test_validate_config():
    """Test configuration validation function."""
    from src.config import validate_config

    # Should not raise an exception with valid config
    assert validate_config() == True


def test_get_model_params():
    """Test get_model_params function."""
    from src.config import get_model_params, LOGISTIC_PARAMS, RANDOM_FOREST_PARAMS

    # Test getting logistic params
    params = get_model_params("logistic")
    assert params == LOGISTIC_PARAMS

    # Test getting random forest params
    params = get_model_params("random_forest")
    assert params == RANDOM_FOREST_PARAMS

    # Test default (uses MODEL_TYPE)
    params = get_model_params()
    assert params is not None

    # Test invalid model type
    with pytest.raises(ValueError):
        get_model_params("invalid_model")


def test_feature_names():
    """Test that feature names are defined."""
    from src.config import FEATURE_NAMES, TARGET_NAME

    assert isinstance(FEATURE_NAMES, list)
    assert len(FEATURE_NAMES) > 0
    assert all(isinstance(name, str) for name in FEATURE_NAMES)
    assert TARGET_NAME is not None
    assert isinstance(TARGET_NAME, str)


def test_print_config():
    """Test that print_config runs without error."""
    from src.config import print_config

    # Should not raise an exception
    print_config()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
