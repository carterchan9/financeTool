"""
Demo version of main.py using synthetic data for testing.
This demonstrates the full pipeline when real data isn't available.
"""

# Same as main.py but uses test_utils for data generation
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

from src.config import MODEL_TYPE, PROCESSED_DATA_PATH, print_config, validate_config
from src.test_utils import generate_sample_price_data
from src.features import compute_features, validate_features
from src.model import train_model, save_model, predict, predict_proba, get_feature_importance
from src.evaluation import (
    evaluate_classification,
    print_evaluation_report,
    is_better_than_baseline,
    compare_models
)
from src.visualization import (
    plot_price_history,
    plot_features,
    plot_price_with_predictions,
    plot_confusion_matrix,
    plot_feature_importance,
    plot_predictions_timeline,
    plot_model_comparison
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main_demo():
    """Demo pipeline with synthetic data."""
    print("\n" + "="*70)
    print("FINANCE ML LAB - PHASE 0 MVP DEMO")
    print("Using synthetic data for demonstration")
    print("="*70)

    # Validate configuration
    validate_config()
    print_config()

    # Create directories
    for path in [PROCESSED_DATA_PATH, "models", "docs/figures", "logs"]:
        Path(path).mkdir(parents=True, exist_ok=True)

    # Generate sample data for AAPL and SPY
    tickers = ["AAPL", "SPY"]
    all_results = {}

    for ticker in tickers:
        print(f"\n{'='*70}")
        print(f"Processing {ticker} (synthetic data)")
        print(f"{'='*70}")

        # Generate synthetic data
        df_raw = generate_sample_price_data(ticker=ticker, n_days=1000)

        # Engineer features
        df_features = compute_features(df_raw)
        validate_features(df_features)

        # Train/test split
        split_idx = int(len(df_features) * 0.8)
        train_data = df_features.iloc[:split_idx]
        test_data = df_features.iloc[split_idx:]

        X_train = train_data.drop('target', axis=1)
        y_train = train_data['target']
        X_test = test_data.drop('target', axis=1)
        y_test = test_data['target']

        print(f"\nTrain: {len(X_train)} samples")
        print(f"Test:  {len(X_test)} samples")

        # Train model
        model = train_model(X_train, y_train, model_type=MODEL_TYPE)
        save_model(model, ticker, MODEL_TYPE)

        # Predictions
        predictions = predict(model, X_test)
        probabilities = predict_proba(model, X_test)

        # Evaluate
        metrics = evaluate_classification(y_test, predictions, probabilities)
        print_evaluation_report(metrics, f"{ticker} - {MODEL_TYPE.title()}")
        is_better_than_baseline(metrics, y_test)

        # Visualizations
        plot_price_history(df_raw, ticker, save=True)
        plot_features(df_features, ticker, save=True)

        df_raw_test = df_raw.iloc[-len(test_data):]
        plot_price_with_predictions(df_raw_test, predictions, ticker, save=True)
        plot_confusion_matrix(metrics['confusion_matrix'],
                            title=f"{ticker} - Confusion Matrix",
                            filename=f"{ticker}_confusion_matrix", save=True)
        plot_predictions_timeline(test_data, predictions, y_test, ticker, save=True)

        if MODEL_TYPE == "random_forest":
            importance = get_feature_importance(model, X_train.columns.tolist())
            plot_feature_importance(importance, title=f"{ticker} - Features",
                                  filename=f"{ticker}_feature_importance", save=True)

        all_results[ticker] = metrics

    # Compare models
    print("\n" + "="*70)
    print("MODEL COMPARISON")
    print("="*70)
    comparison_df = compare_models(all_results)
    print("\n" + comparison_df.to_string(index=False))
    plot_model_comparison(comparison_df, save=True)

    print("\n" + "="*70)
    print("✅ Phase 0 Demo Complete!")
    print("="*70)


if __name__ == "__main__":
    main_demo()
