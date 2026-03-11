"""
Main Pipeline for Phase 1.

This script orchestrates the complete ML pipeline:
1. Load configuration
2. Fetch stock data
3. Engineer features  (returns, MAs, volatility, RSI, MACD, Bollinger Bands, volume)
4. Train all 3 models (Logistic Regression, Random Forest, XGBoost)
5. Compare models — pick best by F1 score
6. Backtest best model strategy vs buy-and-hold
7. Create visualizations

Usage:
    python main.py

Author: Carter Chan
Phase: 1 - Multi-Asset & Technical Indicators
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
    ALL_MODEL_TYPES,
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
from src.backtester import run_backtest, compute_backtest_metrics, print_backtest_report, plot_equity_curves

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

        # Step 4: Train all models and compare
        logger.info(f"\n[4/7] Training {len(ALL_MODEL_TYPES)} models: {ALL_MODEL_TYPES}...")
        all_model_results = {}

        for model_type in ALL_MODEL_TYPES:
            logger.info(f"  Training {model_type}...")
            m = train_model(X_train, y_train, model_type=model_type)
            save_model(m, ticker, model_type)
            preds = predict(m, X_test)
            probas = predict_proba(m, X_test)
            met = evaluate_classification(y_test, preds, probas)
            all_model_results[model_type] = {
                'model': m,
                'predictions': preds,
                'probabilities': probas,
                'metrics': met,
            }

        # Print per-model summary
        print(f"\n  {'Model':<16} {'Accuracy':>10} {'F1':>8} {'AUC':>8}")
        print(f"  {'─'*44}")
        for mt, r in all_model_results.items():
            m = r['metrics']
            print(f"  {mt:<16} {m['accuracy']:>10.4f} {m['f1']:>8.4f} {m['auc_roc']:>8.4f}")

        # Pick best model by F1 score
        best_model_type = max(all_model_results, key=lambda mt: all_model_results[mt]['metrics']['f1'])
        best = all_model_results[best_model_type]
        predictions = best['predictions']
        probabilities = best['probabilities']
        metrics = best['metrics']
        model = best['model']
        logger.info(f"✅ Best model: {best_model_type} (F1={metrics['f1']:.4f})")

        # Step 5: Evaluate best model fully
        logger.info(f"\n[5/7] Evaluating best model ({best_model_type})...")
        print_evaluation_report(metrics, f"{ticker} - {best_model_type} (best)")
        baseline = calculate_baseline_accuracy(y_test)
        beats_baseline = is_better_than_baseline(metrics, y_test)

        # Step 6: Backtest best model
        logger.info(f"\n[6/7] Backtesting {best_model_type} strategy...")
        df_raw_test = df_raw.loc[test_data.index]
        backtest_result = run_backtest(predictions, df_raw_test)
        backtest_metrics = compute_backtest_metrics(backtest_result)
        print_backtest_report(backtest_metrics, ticker)
        plot_equity_curves(backtest_result, ticker, save=True)
        logger.info(f"✅ Backtest complete")

        # Step 7: Visualizations
        logger.info(f"\n[7/7] Creating visualizations...")

        plot_price_history(df_raw, ticker, save=True)
        plot_features(df_features, ticker, save=True)
        plot_price_with_predictions(df_raw_test, predictions, ticker, save=True)
        plot_confusion_matrix(
            metrics['confusion_matrix'],
            title=f"{ticker} - Confusion Matrix ({best_model_type})",
            filename=f"{ticker}_confusion_matrix",
            save=True
        )
        plot_predictions_timeline(test_data, predictions, y_test, ticker, save=True)

        # Feature importance for tree-based models
        importance = get_feature_importance(model, X_train.columns.tolist())
        if importance is not None:
            plot_feature_importance(
                importance,
                title=f"{ticker} - Feature Importance ({best_model_type})",
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
            'best_model_type': best_model_type,
            'all_model_results': {mt: r['metrics'] for mt, r in all_model_results.items()},
            'backtest': backtest_metrics,
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
    print("FINANCE ML LAB - PHASE 1")
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

    # Model comparison across tickers (best model per ticker)
    if len(successful_tickers) > 1:
        print("\n" + "="*70)
        print("BEST MODEL PER TICKER")
        print("="*70)

        comparison_data = {}
        for ticker in successful_tickers:
            comparison_data[ticker] = all_results[ticker]['metrics']

        comparison_df = compare_models(comparison_data)
        print("\n" + comparison_df.to_string(index=False))
        plot_model_comparison(comparison_df, save=True)

        # Show which model type won each ticker
        print("\n" + "="*70)
        print("MODEL TYPE WINNERS")
        print("="*70)
        print(f"\n  {'Ticker':<10} {'Best Model':<18} {'F1':>8}  vs  LR F1 / RF F1 / XGB F1")
        print(f"  {'─'*65}")
        for ticker in successful_tickers:
            r = all_results[ticker]
            best = r['best_model_type']
            amr = r['all_model_results']
            lr_f1  = amr.get('logistic', {}).get('f1', 0)
            rf_f1  = amr.get('random_forest', {}).get('f1', 0)
            xgb_f1 = amr.get('xgboost', {}).get('f1', 0)
            print(f"  {ticker:<10} {best:<18} {r['metrics']['f1']:>8.4f}     "
                  f"{lr_f1:.4f} / {rf_f1:.4f} / {xgb_f1:.4f}")

    # Performance summary for successful tickers
    if successful_tickers:
        print("\n" + "="*70)
        print("PERFORMANCE SUMMARY")
        print("="*70)

        for ticker in successful_tickers:
            metrics = all_results[ticker]['metrics']
            baseline = all_results[ticker]['baseline']
            beats = all_results[ticker]['beats_baseline']
            bt = all_results[ticker]['backtest']
            best = all_results[ticker]['best_model_type']

            print(f"\n{ticker} [{best}]:")
            print(f"  Accuracy:        {metrics['accuracy']:.4f} (Baseline: {baseline:.4f})")
            print(f"  F1 Score:        {metrics['f1']:.4f}")
            print(f"  ML Status:       {'✅ Beats baseline' if beats else '❌ Below baseline'}")
            strat_ret = bt['strategy_total_return']
            bah_ret = bt['bah_total_return']
            outperforms = strat_ret > bah_ret
            print(f"  Strategy Return: {strat_ret:+.1f}% vs Buy&Hold {bah_ret:+.1f}%  "
                  f"{'✅' if outperforms else '📉'}")
            print(f"  Sharpe Ratio:    {bt['strategy_sharpe']:.2f}")

    # Final message
    print("\n" + "="*70)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\n✅ Phase 1 pipeline complete!")
    print(f"\nResults saved to:")
    print(f"  - Models: models/")
    print(f"  - Processed data: {PROCESSED_DATA_PATH}/")
    print(f"  - Figures: docs/figures/")
    print(f"  - Logs: logs/main.log")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
