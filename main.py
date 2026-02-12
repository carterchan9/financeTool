"""
Main Pipeline for Phase 0 MVP.

This script orchestrates the complete ML pipeline:
1. Load configuration
2. Fetch stock data
3. Engineer features
4. Train models
5. Generate predictions
6. Evaluate performance
7. Create visualizations

Usage:
    python main.py

Author: Carter Chan
Phase: 0 - MVP
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

# Import configuration
from src.config import (
    TICKERS,
    START_DATE,
    END_DATE,
    TEST_SPLIT_DATE,
    MODEL_TYPE,
    PROCESSED_DATA_PATH,
    print_config,
    validate_config
)

# Import modules
from src.data_loader import fetch_price_data, save_raw_data, get_data_info
from src.features import compute_features, validate_features
from src.model import train_model, save_model, predict, predict_proba, get_feature_importance
from src.evaluation import (
    evaluate_classification,
    print_evaluation_report,
    calculate_baseline_accuracy,
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_directories():
    """Create necessary directories if they don't exist."""
    from src.config import RAW_DATA_PATH, MODEL_PATH, FIGURES_PATH, LOGS_PATH

    for path in [RAW_DATA_PATH, PROCESSED_DATA_PATH, MODEL_PATH, FIGURES_PATH, LOGS_PATH]:
        Path(path).mkdir(parents=True, exist_ok=True)


def process_ticker(ticker: str) -> dict:
    """
    Process a single ticker through the entire pipeline.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with results and metrics
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"Processing {ticker}")
    logger.info(f"{'='*70}")

    results = {
        'ticker': ticker,
        'success': False,
        'error': None
    }

    try:
        # Step 1: Fetch data
        logger.info(f"\n[1/7] Fetching data for {ticker}...")
        df_raw = fetch_price_data(ticker, START_DATE, END_DATE)

        if df_raw is None or df_raw.empty:
            logger.error(f"Failed to fetch data for {ticker}")
            results['error'] = "Data fetch failed"
            return results

        data_info = get_data_info(df_raw)
        logger.info(f"✅ Loaded {data_info['n_rows']} days of data")
        logger.info(f"   Date range: {data_info['start_date']} to {data_info['end_date']}")

        # Step 2: Engineer features
        logger.info(f"\n[2/7] Engineering features...")
        df_features = compute_features(df_raw)

        validate_features(df_features)
        logger.info(f"✅ Features engineered: {df_features.shape[1]} features, {df_features.shape[0]} samples")

        # Save processed data
        processed_file = Path(PROCESSED_DATA_PATH) / f"{ticker}_processed.csv"
        df_features.to_csv(processed_file)
        logger.info(f"✅ Processed data saved to {processed_file}")

        # Step 3: Train/test split (time-based)
        logger.info(f"\n[3/7] Splitting train/test data...")
        train_data = df_features[df_features.index < TEST_SPLIT_DATE]
        test_data = df_features[df_features.index >= TEST_SPLIT_DATE]

        X_train = train_data.drop('target', axis=1)
        y_train = train_data['target']
        X_test = test_data.drop('target', axis=1)
        y_test = test_data['target']

        logger.info(f"✅ Train: {len(X_train)} samples ({X_train.index.min()} to {X_train.index.max()})")
        logger.info(f"✅ Test:  {len(X_test)} samples ({X_test.index.min()} to {X_test.index.max()})")

        # Check if we have enough data
        if len(X_train) < 50 or len(X_test) < 20:
            logger.error("Insufficient data for training/testing")
            results['error'] = "Insufficient data"
            return results

        # Step 4: Train model
        logger.info(f"\n[4/7] Training {MODEL_TYPE} model...")
        model = train_model(X_train, y_train, model_type=MODEL_TYPE)

        # Save model
        model_path = save_model(model, ticker, MODEL_TYPE)
        logger.info(f"✅ Model saved to {model_path}")

        # Step 5: Generate predictions
        logger.info(f"\n[5/7] Generating predictions...")
        predictions = predict(model, X_test)
        probabilities = predict_proba(model, X_test)

        logger.info(f"✅ Generated {len(predictions)} predictions")

        # Step 6: Evaluate model
        logger.info(f"\n[6/7] Evaluating model...")
        metrics = evaluate_classification(y_test, predictions, probabilities)

        print_evaluation_report(metrics, f"{ticker} - {MODEL_TYPE.title()} Model")

        # Check if model beats baseline
        baseline = calculate_baseline_accuracy(y_test)
        beats_baseline = is_better_than_baseline(metrics, y_test)

        # Step 7: Create visualizations
        logger.info(f"\n[7/7] Creating visualizations...")

        # Price history
        plot_price_history(df_raw, ticker, save=True)

        # Features
        plot_features(df_features, ticker, save=True)

        # Predictions on price chart
        df_raw_test = df_raw.loc[test_data.index]
        plot_price_with_predictions(df_raw_test, predictions, ticker, save=True)

        # Confusion matrix
        plot_confusion_matrix(
            metrics['confusion_matrix'],
            title=f"{ticker} - Confusion Matrix",
            filename=f"{ticker}_confusion_matrix",
            save=True
        )

        # Predictions timeline
        plot_predictions_timeline(test_data, predictions, y_test, ticker, save=True)

        # Feature importance (if available)
        if MODEL_TYPE == "random_forest":
            importance = get_feature_importance(model, X_train.columns.tolist())
            plot_feature_importance(
                importance,
                title=f"{ticker} - Feature Importance",
                filename=f"{ticker}_feature_importance",
                save=True
            )

        logger.info(f"✅ All visualizations created")

        # Store results
        results.update({
            'success': True,
            'n_train': len(X_train),
            'n_test': len(X_test),
            'metrics': metrics,
            'baseline': baseline,
            'beats_baseline': beats_baseline,
            'model_type': MODEL_TYPE
        })

        logger.info(f"\n{'='*70}")
        logger.info(f"✅ {ticker} processing complete!")
        logger.info(f"{'='*70}")

    except Exception as e:
        logger.error(f"Error processing {ticker}: {e}", exc_info=True)
        results['error'] = str(e)

    return results


def main():
    """Main pipeline execution."""
    print("\n" + "="*70)
    print("FINANCE ML LAB - PHASE 0 MVP")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Validate configuration
    logger.info("\nValidating configuration...")
    try:
        validate_config()
        logger.info("✅ Configuration valid")
    except ValueError as e:
        logger.error(f"❌ Configuration invalid: {e}")
        return

    # Print configuration
    print_config()

    # Create necessary directories
    logger.info("\nCreating directories...")
    create_directories()
    logger.info("✅ Directories ready")

    # Process each ticker
    all_results = {}

    for ticker in TICKERS:
        results = process_ticker(ticker)
        all_results[ticker] = results

    # Summary report
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)

    successful_tickers = [t for t, r in all_results.items() if r['success']]
    failed_tickers = [t for t, r in all_results.items() if not r['success']]

    print(f"\n✅ Successful: {len(successful_tickers)}/{len(TICKERS)}")
    if successful_tickers:
        print(f"   Tickers: {', '.join(successful_tickers)}")

    if failed_tickers:
        print(f"\n❌ Failed: {len(failed_tickers)}/{len(TICKERS)}")
        print(f"   Tickers: {', '.join(failed_tickers)}")
        for ticker in failed_tickers:
            print(f"     - {ticker}: {all_results[ticker]['error']}")

    # Model comparison (if multiple successful)
    if len(successful_tickers) > 1:
        print("\n" + "="*70)
        print("MODEL COMPARISON ACROSS TICKERS")
        print("="*70)

        comparison_data = {}
        for ticker in successful_tickers:
            comparison_data[ticker] = all_results[ticker]['metrics']

        comparison_df = compare_models(comparison_data)
        print("\n" + comparison_df.to_string(index=False))

        # Plot comparison
        plot_model_comparison(comparison_df, save=True)

    # Performance summary for successful tickers
    if successful_tickers:
        print("\n" + "="*70)
        print("PERFORMANCE SUMMARY")
        print("="*70)

        for ticker in successful_tickers:
            metrics = all_results[ticker]['metrics']
            baseline = all_results[ticker]['baseline']
            beats = all_results[ticker]['beats_baseline']

            print(f"\n{ticker}:")
            print(f"  Accuracy:  {metrics['accuracy']:.4f} (Baseline: {baseline:.4f})")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall:    {metrics['recall']:.4f}")
            print(f"  F1 Score:  {metrics['f1']:.4f}")
            print(f"  Status:    {'✅ Beats baseline' if beats else '❌ Below baseline'}")

    # Final message
    print("\n" + "="*70)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\n✅ Phase 0 pipeline complete!")
    print(f"\nResults saved to:")
    print(f"  - Models: models/")
    print(f"  - Processed data: {PROCESSED_DATA_PATH}/")
    print(f"  - Figures: docs/figures/")
    print(f"  - Logs: logs/main.log")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
