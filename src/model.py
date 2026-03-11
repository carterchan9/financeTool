"""
Model Training Module for Phase 1.

This module handles:
- Training ML models (Logistic Regression, Random Forest, XGBoost)
- Saving and loading trained models
- Making predictions

Functions:
    train_logistic_regression: Train logistic regression classifier
    train_random_forest: Train random forest classifier
    train_xgboost: Train XGBoost classifier
    train_model: Main training dispatcher
    save_model: Persist model to disk
    load_model: Load saved model
    predict: Generate predictions
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from pathlib import Path
import joblib
from typing import Optional, Tuple
import logging

from src.config import (
    LOGISTIC_PARAMS,
    RANDOM_FOREST_PARAMS,
    XGBOOST_PARAMS,
    MODEL_PATH,
    RANDOM_SEED
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_logistic_regression(
    X_train: np.ndarray,
    y_train: np.ndarray,
    params: dict = None
) -> LogisticRegression:
    """
    Train Logistic Regression classifier.

    Args:
        X_train: Training features
        y_train: Training labels
        params: Model hyperparameters. If None, uses config.LOGISTIC_PARAMS

    Returns:
        Trained LogisticRegression model

    Example:
        >>> model = train_logistic_regression(X_train, y_train)
        >>> print(f"Model coefficients: {model.coef_}")
    """
    if params is None:
        params = LOGISTIC_PARAMS.copy()

    logger.info("Training Logistic Regression model...")
    logger.info(f"Parameters: {params}")

    model = LogisticRegression(**params)
    model.fit(X_train, y_train)

    logger.info("✅ Logistic Regression training complete")

    return model


def train_random_forest(
    X_train: np.ndarray,
    y_train: np.ndarray,
    params: dict = None
) -> RandomForestClassifier:
    """
    Train Random Forest classifier.

    Args:
        X_train: Training features
        y_train: Training labels
        params: Model hyperparameters. If None, uses config.RANDOM_FOREST_PARAMS

    Returns:
        Trained RandomForestClassifier model

    Example:
        >>> model = train_random_forest(X_train, y_train)
        >>> print(f"Feature importances: {model.feature_importances_}")
    """
    if params is None:
        params = RANDOM_FOREST_PARAMS.copy()

    logger.info("Training Random Forest model...")
    logger.info(f"Parameters: {params}")

    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    logger.info("✅ Random Forest training complete")

    return model


def train_xgboost(
    X_train: np.ndarray,
    y_train: np.ndarray,
    params: dict = None
) -> XGBClassifier:
    """
    Train XGBoost classifier.

    XGBoost builds trees sequentially, each correcting the errors of the
    previous. It typically outperforms Random Forest on tabular data because
    it focuses learning on hard examples.

    Args:
        X_train: Training features
        y_train: Training labels
        params: Model hyperparameters. If None, uses config.XGBOOST_PARAMS

    Returns:
        Trained XGBClassifier model
    """
    if params is None:
        params = XGBOOST_PARAMS.copy()

    logger.info("Training XGBoost model...")
    logger.info(f"Parameters: {params}")

    model = XGBClassifier(**params)
    model.fit(X_train, y_train)

    logger.info("✅ XGBoost training complete")

    return model


def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    model_type: str = "logistic",
    params: dict = None
):
    """
    Main training function that dispatches to specific model trainers.

    Args:
        X_train: Training features (numpy array or DataFrame)
        y_train: Training labels (numpy array or Series)
        model_type: "logistic" or "random_forest"
        params: Optional custom hyperparameters

    Returns:
        Trained model object

    Raises:
        ValueError: If model_type is invalid

    Example:
        >>> model = train_model(X_train, y_train, model_type="logistic")
        >>> predictions = predict(model, X_test)
    """
    # Convert to numpy arrays if needed
    if isinstance(X_train, pd.DataFrame):
        X_train = X_train.values
    if isinstance(y_train, pd.Series):
        y_train = y_train.values

    logger.info(f"Training {model_type} model...")
    logger.info(f"Training set size: {len(X_train)} samples, {X_train.shape[1]} features")
    logger.info(f"Class distribution: {np.bincount(y_train.astype(int))}")

    if model_type == "logistic":
        model = train_logistic_regression(X_train, y_train, params)
    elif model_type == "random_forest":
        model = train_random_forest(X_train, y_train, params)
    elif model_type == "xgboost":
        model = train_xgboost(X_train, y_train, params)
    else:
        raise ValueError(f"Unknown model type: {model_type}. Must be 'logistic', 'random_forest', or 'xgboost'")

    return model


def save_model(
    model,
    ticker: str,
    model_type: str
) -> Path:
    """
    Save trained model to disk using joblib.

    Args:
        model: Trained model object
        ticker: Stock ticker symbol
        model_type: Model type for filename

    Returns:
        Path to saved model file

    Example:
        >>> save_model(model, "AAPL", "logistic")
        # Saves to models/AAPL_logistic.pkl
    """
    # Create directory if it doesn't exist
    model_dir = Path(MODEL_PATH)
    model_dir.mkdir(parents=True, exist_ok=True)

    # Define file path
    filename = f"{ticker}_{model_type}.pkl"
    file_path = model_dir / filename

    # Save model
    joblib.dump(model, file_path)
    logger.info(f"Model saved to {file_path}")

    return file_path


def load_model(
    ticker: str,
    model_type: str
) -> Optional[object]:
    """
    Load previously trained model from disk.

    Args:
        ticker: Stock ticker symbol
        model_type: Model type

    Returns:
        Loaded model object, or None if file doesn't exist

    Example:
        >>> model = load_model("AAPL", "logistic")
        >>> if model is not None:
        ...     predictions = predict(model, X_test)
    """
    filename = f"{ticker}_{model_type}.pkl"
    file_path = Path(MODEL_PATH) / filename

    if not file_path.exists():
        logger.warning(f"Model file not found: {file_path}")
        return None

    try:
        model = joblib.load(file_path)
        logger.info(f"Model loaded from {file_path}")
        return model

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None


def predict(model, X_test) -> np.ndarray:
    """
    Generate predictions from trained model.

    Args:
        model: Trained model object
        X_test: Test features (numpy array or DataFrame)

    Returns:
        Array of predictions (0 or 1)

    Example:
        >>> predictions = predict(model, X_test)
        >>> print(f"Predicted {predictions.sum()} positive cases")
    """
    # Convert to numpy array if needed
    if isinstance(X_test, pd.DataFrame):
        X_test = X_test.values

    predictions = model.predict(X_test)

    logger.debug(f"Generated {len(predictions)} predictions")
    logger.debug(f"Prediction distribution: {np.bincount(predictions.astype(int))}")

    return predictions


def predict_proba(model, X_test) -> np.ndarray:
    """
    Generate prediction probabilities from trained model.

    Args:
        model: Trained model object
        X_test: Test features (numpy array or DataFrame)

    Returns:
        Array of shape (n_samples, 2) with class probabilities

    Example:
        >>> probas = predict_proba(model, X_test)
        >>> print(f"Probability of up: {probas[:, 1]}")
    """
    # Convert to numpy array if needed
    if isinstance(X_test, pd.DataFrame):
        X_test = X_test.values

    probabilities = model.predict_proba(X_test)

    logger.debug(f"Generated {len(probabilities)} probability predictions")

    return probabilities


def get_feature_importance(
    model,
    feature_names: list
) -> pd.DataFrame:
    """
    Get feature importance from tree-based models.

    Args:
        model: Trained model with feature_importances_ attribute
        feature_names: List of feature names

    Returns:
        DataFrame with features and their importance scores

    Example:
        >>> importance = get_feature_importance(model, feature_names)
        >>> print(importance.sort_values('importance', ascending=False))
    """
    if not hasattr(model, 'feature_importances_'):
        logger.warning("Model does not have feature_importances_ attribute")
        return None

    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    })

    importance_df = importance_df.sort_values('importance', ascending=False)

    return importance_df


def get_model_params(model) -> dict:
    """
    Get parameters from trained model.

    Args:
        model: Trained model object

    Returns:
        Dictionary of model parameters

    Example:
        >>> params = get_model_params(model)
        >>> print(params)
    """
    return model.get_params()


if __name__ == "__main__":
    # Test model training with sample data
    print("Testing Model Training Module")
    print("=" * 60)

    from src.test_utils import generate_sample_price_data
    from src.features import compute_features
    from sklearn.model_selection import train_test_split

    # Generate and process sample data
    print("\n1. Generating and processing sample data...")
    df_raw = generate_sample_price_data(n_days=500)
    df_features = compute_features(df_raw)

    # Prepare train/test split
    X = df_features.drop('target', axis=1)
    y = df_features['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False, random_state=RANDOM_SEED
    )

    print(f"✅ Data prepared")
    print(f"   Train: {len(X_train)} samples")
    print(f"   Test: {len(X_test)} samples")
    print(f"   Features: {X_train.shape[1]}")

    # Test Logistic Regression
    print("\n2. Testing Logistic Regression...")
    model_lr = train_model(X_train, y_train, model_type="logistic")
    predictions_lr = predict(model_lr, X_test)
    print(f"✅ Logistic Regression trained and tested")
    print(f"   Predictions: {predictions_lr[:10]}")

    # Test Random Forest
    print("\n3. Testing Random Forest...")
    model_rf = train_model(X_train, y_train, model_type="random_forest")
    predictions_rf = predict(model_rf, X_test)
    print(f"✅ Random Forest trained and tested")
    print(f"   Predictions: {predictions_rf[:10]}")

    # Test feature importance
    print("\n4. Testing feature importance...")
    importance = get_feature_importance(model_rf, X.columns.tolist())
    print("Feature importance:")
    print(importance)

    # Test model saving and loading
    print("\n5. Testing model persistence...")
    save_model(model_lr, "TEST", "logistic")
    save_model(model_rf, "TEST", "random_forest")

    loaded_lr = load_model("TEST", "logistic")
    loaded_rf = load_model("TEST", "random_forest")

    if loaded_lr is not None and loaded_rf is not None:
        print("✅ Models saved and loaded successfully")

        # Verify loaded models work
        pred_loaded = predict(loaded_lr, X_test[:5])
        print(f"   Loaded model predictions: {pred_loaded}")

    # Test probability predictions
    print("\n6. Testing probability predictions...")
    probas = predict_proba(model_lr, X_test[:5])
    print("Prediction probabilities (first 5 samples):")
    print(probas)

    print("\n" + "=" * 60)
    print("Model Training Module test complete!")
