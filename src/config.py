"""
Configuration file for Phase 0 MVP.
All parameters for data, features, and models centralized here.

This file contains all configurable parameters for the Finance ML pipeline.
Modify these values to experiment with different settings without changing code.
"""

# ============================================================================
# Data Configuration
# ============================================================================

# Ticker symbols to analyze
# Start with 2-3 liquid stocks for Phase 0
TICKERS = ["AAPL", "SPY"]

# Date range for historical data
START_DATE = "2015-01-01"  # Beginning of training data
END_DATE = "2024-12-31"    # End of all data

# Train/Test split date (time-based split)
# All data before this date = training, after = testing
TEST_SPLIT_DATE = "2022-01-01"

# ============================================================================
# Feature Engineering Configuration
# ============================================================================

# Moving average windows (in days)
# [5, 20] = 1 week and 1 month moving averages
MA_WINDOWS = [5, 20]

# Volatility calculation window (in days)
# 20 = approximately 1 month of trading days
VOLATILITY_WINDOW = 20

# Minimum number of data points required after feature engineering
# This accounts for NaN rows created by rolling calculations
MIN_DATA_POINTS = 100

# ============================================================================
# Model Configuration
# ============================================================================

# Model type to use: "logistic" or "random_forest"
MODEL_TYPE = "logistic"

# Random seed for reproducibility
# Set to fixed value to ensure consistent results across runs
RANDOM_SEED = 42

# Test set size (only used if not doing time-based split)
TEST_SIZE = 0.2

# ============================================================================
# Directory Paths
# ============================================================================

# Data directories
RAW_DATA_PATH = "data/raw"
PROCESSED_DATA_PATH = "data/processed"
EXTERNAL_DATA_PATH = "data/external"

# Model storage directory
MODEL_PATH = "models"

# Visualization output directory
FIGURES_PATH = "docs/figures"

# Logs directory
LOGS_PATH = "logs"

# ============================================================================
# Model Hyperparameters
# ============================================================================

# Logistic Regression parameters
LOGISTIC_PARAMS = {
    "max_iter": 1000,           # Maximum iterations for convergence
    "solver": "lbfgs",          # Optimization algorithm
    "random_state": RANDOM_SEED,
    "class_weight": "balanced",  # Handle class imbalance
    "C": 1.0                    # Regularization strength (inverse)
}

# Random Forest parameters
RANDOM_FOREST_PARAMS = {
    "n_estimators": 100,        # Number of trees
    "max_depth": 10,            # Maximum tree depth
    "min_samples_split": 5,     # Minimum samples to split node
    "min_samples_leaf": 2,      # Minimum samples in leaf node
    "random_state": RANDOM_SEED,
    "n_jobs": -1,               # Use all CPU cores
    "class_weight": "balanced"  # Handle class imbalance
}

# ============================================================================
# Visualization Configuration
# ============================================================================

# Plot style
PLOT_STYLE = "seaborn-v0_8"

# Figure size (width, height) in inches
FIGURE_SIZE = (12, 6)

# DPI for saved figures
FIGURE_DPI = 100

# Save format for figures
FIGURE_FORMAT = "png"

# ============================================================================
# Logging Configuration
# ============================================================================

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Date format for logs
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# Feature Names (for reference and plotting)
# ============================================================================

# These will be the column names in the processed data
FEATURE_NAMES = [
    "returns",           # Daily returns
    "ma_5",             # 5-day moving average
    "ma_20",            # 20-day moving average
    "volatility",       # Rolling volatility
    "price_to_ma",      # Price relative to MA_20
]

# Target variable name
TARGET_NAME = "target"

# ============================================================================
# Validation Functions
# ============================================================================

def validate_config():
    """
    Validate configuration parameters.
    Raises ValueError if any parameters are invalid.
    """
    from datetime import datetime

    # Validate dates
    try:
        start = datetime.strptime(START_DATE, "%Y-%m-%d")
        end = datetime.strptime(END_DATE, "%Y-%m-%d")
        test_split = datetime.strptime(TEST_SPLIT_DATE, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}")

    # Validate date order
    if start >= end:
        raise ValueError("START_DATE must be before END_DATE")
    if test_split <= start or test_split >= end:
        raise ValueError("TEST_SPLIT_DATE must be between START_DATE and END_DATE")

    # Validate tickers
    if not TICKERS or len(TICKERS) == 0:
        raise ValueError("TICKERS list cannot be empty")

    # Validate windows
    if not all(w > 0 for w in MA_WINDOWS):
        raise ValueError("All MA_WINDOWS values must be positive")
    if VOLATILITY_WINDOW <= 0:
        raise ValueError("VOLATILITY_WINDOW must be positive")

    # Validate model type
    if MODEL_TYPE not in ["logistic", "random_forest"]:
        raise ValueError("MODEL_TYPE must be 'logistic' or 'random_forest'")

    return True


def get_model_params(model_type: str = None):
    """
    Get hyperparameters for specified model type.

    Args:
        model_type: Model type ("logistic" or "random_forest").
                   If None, uses MODEL_TYPE from config.

    Returns:
        Dictionary of model hyperparameters.

    Raises:
        ValueError: If model_type is invalid.
    """
    if model_type is None:
        model_type = MODEL_TYPE

    if model_type == "logistic":
        return LOGISTIC_PARAMS.copy()
    elif model_type == "random_forest":
        return RANDOM_FOREST_PARAMS.copy()
    else:
        raise ValueError(f"Unknown model type: {model_type}")


# ============================================================================
# Configuration Summary
# ============================================================================

def print_config():
    """Print current configuration for verification."""
    print("=" * 60)
    print("Phase 0 Configuration")
    print("=" * 60)
    print(f"Tickers: {TICKERS}")
    print(f"Date Range: {START_DATE} to {END_DATE}")
    print(f"Test Split: {TEST_SPLIT_DATE}")
    print(f"Model Type: {MODEL_TYPE}")
    print(f"Moving Average Windows: {MA_WINDOWS}")
    print(f"Volatility Window: {VOLATILITY_WINDOW}")
    print(f"Random Seed: {RANDOM_SEED}")
    print("=" * 60)


# Validate configuration on import
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"Warning: Configuration validation failed: {e}")


# Run validation and print config when executed directly
if __name__ == "__main__":
    print("Validating configuration...")
    try:
        validate_config()
        print("✅ Configuration is valid")
        print()
        print_config()
    except ValueError as e:
        print(f"❌ Configuration validation failed: {e}")
        exit(1)
