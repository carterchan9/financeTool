"""
Main Pipeline for Phase 2.

This script orchestrates the complete ML pipeline:
1. Load configuration
2. Fetch stock data
3. Engineer features  (returns, MAs, volatility, RSI, MACD, Bollinger Bands, volume)
4. Train sklearn models (Logistic Regression, Random Forest, XGBoost)
5. Train sequence models (LSTM, GRU)
6. Compare all 5 models — pick best by F1 score
7. Backtest best model strategy vs buy-and-hold
8. Create visualizations
9. Log everything to MLflow

Usage:
    python main.py

Author: Carter Chan
Phase: 2 - Advanced ML Models
"""

import sys
import os

# Disable MLflow background threads BEFORE importing mlflow.
# MLflow 3.x starts telemetry + system-metrics threads that segfault on
# Apple Silicon (MPS) due to a known psutil/importlib interaction.
os.environ["MLFLOW_DISABLE_TELEMETRY"] = "true"
os.environ["MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING"] = "false"
os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///mlflow.db"

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

# mlflow is imported lazily inside _mlflow_* helpers below.
# Importing it at module level starts background threads that segfault on
# Apple Silicon when racing with importlib during startup.
_mlflow = None

def _get_mlflow():
    global _mlflow
    if _mlflow is None:
        import mlflow as _ml
        import mlflow.pytorch
        import mlflow.sklearn
        _mlflow = _ml
    return _mlflow

# Import configuration
from src.config import (
    TICKERS,
    START_DATE,
    END_DATE,
    TEST_SPLIT_DATE,
    ALL_MODEL_TYPES,
    PROCESSED_DATA_PATH,
    SEQ_LEN,
    N_EPOCHS,
    BATCH_SIZE,
    LSTM_HIDDEN,
    LSTM_LAYERS,
    LSTM_DROPOUT,
    LEARNING_RATE,
    EARLY_STOPPING_PATIENCE,
    MLFLOW_EXPERIMENT,
    print_config,
    validate_config,
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
    compare_models,
)
from src.visualization import (
    plot_price_history,
    plot_features,
    plot_price_with_predictions,
    plot_confusion_matrix,
    plot_feature_importance,
    plot_predictions_timeline,
    plot_model_comparison,
)
from src.backtester import run_backtest, compute_backtest_metrics, print_backtest_report, plot_equity_curves
from src.lstm_model import (
    LSTMModel,
    GRUModel,
    prepare_sequences,
    train_sequence_model,
    predict_sequence,
    get_device,
    get_sequence_probas_2d,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# MLflow helpers — all calls wrapped so a tracking failure never kills the run
# ============================================================================

def _mlflow_log_param(key, value):
    try:
        _get_mlflow().log_param(key, value)
    except Exception:
        pass


def _mlflow_log_metric(key, value):
    try:
        _get_mlflow().log_metric(key, float(value))
    except Exception:
        pass


def _mlflow_log_model(model, model_type, ticker):
    try:
        import mlflow.pytorch, mlflow.sklearn
        if model_type in ("lstm", "gru"):
            model.cpu()
            mlflow.pytorch.log_model(model, name=f"model_{ticker}")
        else:
            mlflow.sklearn.log_model(model, name=f"model_{ticker}")
    except Exception:
        pass


# ============================================================================
# Helpers
# ============================================================================

def create_directories():
    """Create necessary directories if they don't exist."""
    from src.config import RAW_DATA_PATH, MODEL_PATH, FIGURES_PATH, LOGS_PATH

    for path in [RAW_DATA_PATH, PROCESSED_DATA_PATH, MODEL_PATH, FIGURES_PATH, LOGS_PATH]:
        Path(path).mkdir(parents=True, exist_ok=True)


def train_sequence_models(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    device: str,
) -> dict:
    """
    Train LSTM and GRU sequence models and return their results.

    Predictions align with y_test[SEQ_LEN:] because each prediction requires
    SEQ_LEN days of history. The 'seq_offset' key tells the caller how to
    slice y_test and the test index for evaluation and backtesting.

    Args:
        X_train, y_train: Training arrays (numpy)
        X_test, y_test:   Test arrays (numpy)
        device:           Compute device string

    Returns:
        Dict: model_type -> {model, predictions, probabilities, metrics, seq_offset}
    """
    seq_results = {}
    n_features = X_train.shape[1]
    y_test_seq = y_test[SEQ_LEN:]

    for seq_type in ["lstm", "gru"]:
        logger.info(f"  Training {seq_type.upper()}...")

        train_loader, test_loader, _ = prepare_sequences(
            X_train, y_train, X_test, y_test,
            seq_len=SEQ_LEN,
            batch_size=BATCH_SIZE,
        )

        model = (
            LSTMModel(n_features, LSTM_HIDDEN, LSTM_LAYERS, LSTM_DROPOUT)
            if seq_type == "lstm"
            else GRUModel(n_features, LSTM_HIDDEN, LSTM_LAYERS, LSTM_DROPOUT)
        )

        train_sequence_model(
            model, train_loader,
            n_epochs=N_EPOCHS,
            lr=LEARNING_RATE,
            patience=EARLY_STOPPING_PATIENCE,
            device=device,
        )

        preds, probs_1d = predict_sequence(model, test_loader, device=device)
        probs_2d = get_sequence_probas_2d(probs_1d)
        metrics = evaluate_classification(y_test_seq, preds, probs_2d)

        seq_results[seq_type] = {
            'model': model,
            'predictions': preds,
            'probabilities': probs_2d,
            'metrics': metrics,
            'seq_offset': SEQ_LEN,
        }

        logger.info(f"  ✅ {seq_type.upper()} — F1: {metrics['f1']:.4f}, Acc: {metrics['accuracy']:.4f}")

    return seq_results


# ============================================================================
# Per-ticker pipeline
# ============================================================================

def process_ticker(ticker: str, device: str) -> dict:
    """
    Process a single ticker through the entire pipeline.

    Args:
        ticker: Stock ticker symbol
        device: Compute device for sequence models

    Returns:
        Dictionary with all results and metrics
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"Processing {ticker}")
    logger.info(f"{'='*70}")

    results = {'ticker': ticker, 'success': False, 'error': None}

    try:
        run = _get_mlflow().start_run(run_name=ticker)
    except Exception:
        run = None

    try:
        _mlflow_log_param("ticker", ticker)
        _mlflow_log_param("seq_len", SEQ_LEN)
        _mlflow_log_param("n_epochs", N_EPOCHS)
        _mlflow_log_param("lstm_hidden", LSTM_HIDDEN)
        _mlflow_log_param("lstm_layers", LSTM_LAYERS)
        _mlflow_log_param("learning_rate", LEARNING_RATE)
        _mlflow_log_param("device", device)

        # Step 1: Fetch data
        logger.info(f"\n[1/8] Fetching data for {ticker}...")
        df_raw = fetch_price_data(ticker, START_DATE, END_DATE)

        if df_raw is None or df_raw.empty:
            results['error'] = "Data fetch failed"
            return results

        data_info = get_data_info(df_raw)
        logger.info(f"✅ Loaded {data_info['n_rows']} days of data")

        # Step 2: Engineer features
        logger.info(f"\n[2/8] Engineering features...")
        df_features = compute_features(df_raw)
        validate_features(df_features)
        logger.info(f"✅ {df_features.shape[1]} features, {df_features.shape[0]} samples")

        processed_file = Path(PROCESSED_DATA_PATH) / f"{ticker}_processed.csv"
        df_features.to_csv(processed_file)

        # Step 3: Train/test split (time-based)
        logger.info(f"\n[3/8] Splitting train/test data...")
        train_data = df_features[df_features.index < TEST_SPLIT_DATE]
        test_data = df_features[df_features.index >= TEST_SPLIT_DATE]

        X_train = train_data.drop('target', axis=1)
        y_train = train_data['target']
        X_test = test_data.drop('target', axis=1)
        y_test = test_data['target']

        logger.info(f"✅ Train: {len(X_train)} samples | Test: {len(X_test)} samples")
        _mlflow_log_param("n_train", len(X_train))
        _mlflow_log_param("n_test", len(X_test))

        if len(X_train) < 50 or len(X_test) < SEQ_LEN + 20:
            results['error'] = "Insufficient data"
            return results

        # Step 4: Train sklearn models (LR, RF, XGBoost)
        logger.info(f"\n[4/8] Training sklearn models: {ALL_MODEL_TYPES}...")
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
                'seq_offset': 0,
            }

        # Step 5: Train sequence models (LSTM, GRU)
        logger.info(f"\n[5/8] Training sequence models (LSTM, GRU) on {device.upper()}...")
        seq_results = train_sequence_models(
            X_train.values, y_train.values,
            X_test.values, y_test.values,
            device=device,
        )
        all_model_results.update(seq_results)

        # Print full 5-model comparison table
        print(f"\n  {'Model':<16} {'Accuracy':>10} {'F1':>8} {'AUC':>8}")
        print(f"  {'─'*44}")
        for mt, r in all_model_results.items():
            m = r['metrics']
            print(f"  {mt:<16} {m['accuracy']:>10.4f} {m['f1']:>8.4f} {m['auc_roc']:>8.4f}")

        # Log all model metrics to MLflow
        for mt, r in all_model_results.items():
            m = r['metrics']
            _mlflow_log_metric(f"{mt}_accuracy", m['accuracy'])
            _mlflow_log_metric(f"{mt}_f1", m['f1'])
            _mlflow_log_metric(f"{mt}_auc", m['auc_roc'])

        # Step 6: Pick best model by F1
        best_model_type = max(all_model_results, key=lambda mt: all_model_results[mt]['metrics']['f1'])
        best = all_model_results[best_model_type]
        seq_offset = best['seq_offset']
        predictions = best['predictions']
        probabilities = best['probabilities']
        metrics = best['metrics']
        model = best['model']

        logger.info(f"✅ Best model: {best_model_type} (F1={metrics['f1']:.4f})")
        _mlflow_log_param("best_model", best_model_type)
        _mlflow_log_metric("best_f1", metrics['f1'])
        _mlflow_log_metric("best_accuracy", metrics['accuracy'])
        _mlflow_log_metric("best_auc", metrics['auc_roc'])

        # Evaluate best model
        logger.info(f"\n[6/8] Evaluating best model ({best_model_type})...")
        print_evaluation_report(metrics, f"{ticker} - {best_model_type} (best)")
        baseline = calculate_baseline_accuracy(y_test)
        beats_baseline = is_better_than_baseline(metrics, y_test)

        # Step 7: Backtest best model
        # Sequence models predict on y_test[seq_offset:] — align raw prices
        logger.info(f"\n[7/8] Backtesting {best_model_type} strategy...")
        test_index = test_data.index[seq_offset:]
        df_raw_test = df_raw.loc[test_index]
        backtest_result = run_backtest(predictions, df_raw_test)
        backtest_metrics = compute_backtest_metrics(backtest_result)
        print_backtest_report(backtest_metrics, ticker)
        plot_equity_curves(backtest_result, ticker, save=True)

        _mlflow_log_metric("strategy_return", backtest_metrics['strategy_total_return'])
        _mlflow_log_metric("bah_return", backtest_metrics['bah_total_return'])
        _mlflow_log_metric("sharpe", backtest_metrics['strategy_sharpe'])
        _mlflow_log_metric("max_drawdown", backtest_metrics['strategy_max_drawdown'])

        # Step 8: Visualizations
        logger.info(f"\n[8/8] Creating visualizations...")

        plot_price_history(df_raw, ticker, save=True)
        plot_features(df_features, ticker, save=True)
        plot_price_with_predictions(df_raw_test, predictions, ticker, save=True)
        plot_confusion_matrix(
            metrics['confusion_matrix'],
            title=f"{ticker} - Confusion Matrix ({best_model_type})",
            filename=f"{ticker}_confusion_matrix",
            save=True,
        )
        plot_predictions_timeline(
            test_data.iloc[seq_offset:], predictions, y_test.iloc[seq_offset:], ticker, save=True
        )

        importance = get_feature_importance(model, X_train.columns.tolist())
        if importance is not None:
            plot_feature_importance(
                importance,
                title=f"{ticker} - Feature Importance ({best_model_type})",
                filename=f"{ticker}_feature_importance",
                save=True,
            )

        _mlflow_log_model(model, best_model_type, ticker)
        logger.info(f"✅ All visualizations created")

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
        logger.info(f"✅ {ticker} complete!")
        logger.info(f"{'='*70}")

    except Exception as e:
        logger.error(f"Error processing {ticker}: {e}", exc_info=True)
        results['error'] = str(e)

    finally:
        if run is not None:
            try:
                _get_mlflow().end_run()
            except Exception:
                pass

    return results


# ============================================================================
# Main
# ============================================================================

def main():
    """Main pipeline execution."""
    print("\n" + "="*70)
    print("FINANCE ML LAB - PHASE 2")
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

    print_config()

    # Setup
    create_directories()
    device = get_device()
    logger.info(f"✅ Compute device: {device.upper()}")

    # Setup MLflow (lazy import — avoids background thread race on startup)
    try:
        _get_mlflow().set_experiment(MLFLOW_EXPERIMENT)
        logger.info(f"✅ MLflow experiment: {MLFLOW_EXPERIMENT}")
        logger.info(f"   View results: mlflow ui  (then open http://localhost:5000)")
    except Exception as e:
        logger.warning(f"MLflow setup failed (continuing without tracking): {e}")

    # Process each ticker
    all_results = {}
    for ticker in TICKERS:
        results = process_ticker(ticker, device)
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
        for ticker in failed_tickers:
            print(f"     - {ticker}: {all_results[ticker]['error']}")

    # Model type comparison across tickers
    if len(successful_tickers) > 1:
        print("\n" + "="*70)
        print("MODEL TYPE WINNERS")
        print("="*70)
        print(f"\n  {'Ticker':<10} {'Best Model':<16} {'F1':>8}  |  LR / RF / XGB / LSTM / GRU")
        print(f"  {'─'*70}")
        for ticker in successful_tickers:
            r = all_results[ticker]
            best = r['best_model_type']
            amr = r['all_model_results']
            lr_f1   = amr.get('logistic', {}).get('f1', 0)
            rf_f1   = amr.get('random_forest', {}).get('f1', 0)
            xgb_f1  = amr.get('xgboost', {}).get('f1', 0)
            lstm_f1 = amr.get('lstm', {}).get('f1', 0)
            gru_f1  = amr.get('gru', {}).get('f1', 0)
            print(f"  {ticker:<10} {best:<16} {r['metrics']['f1']:>8.4f}  |  "
                  f"{lr_f1:.4f} / {rf_f1:.4f} / {xgb_f1:.4f} / {lstm_f1:.4f} / {gru_f1:.4f}")

    # Performance summary
    if successful_tickers:
        print("\n" + "="*70)
        print("PERFORMANCE SUMMARY")
        print("="*70)

        comparison_data = {t: all_results[t]['metrics'] for t in successful_tickers}
        comparison_df = compare_models(comparison_data)
        plot_model_comparison(comparison_df, save=True)

        for ticker in successful_tickers:
            metrics = all_results[ticker]['metrics']
            baseline = all_results[ticker]['baseline']
            beats = all_results[ticker]['beats_baseline']
            bt = all_results[ticker]['backtest']
            best = all_results[ticker]['best_model_type']

            strat_ret = bt['strategy_total_return']
            bah_ret = bt['bah_total_return']
            outperforms = strat_ret > bah_ret

            print(f"\n{ticker} [{best}]:")
            print(f"  Accuracy:        {metrics['accuracy']:.4f} (Baseline: {baseline:.4f})")
            print(f"  F1 Score:        {metrics['f1']:.4f}")
            print(f"  ML Status:       {'✅ Beats baseline' if beats else '❌ Below baseline'}")
            print(f"  Strategy Return: {strat_ret:+.1f}% vs Buy&Hold {bah_ret:+.1f}%  "
                  f"{'✅' if outperforms else '📉'}")
            print(f"  Sharpe Ratio:    {bt['strategy_sharpe']:.2f}")

    print("\n" + "="*70)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\n✅ Phase 2 pipeline complete!")
    print(f"\nResults saved to:")
    print(f"  - Models:          models/")
    print(f"  - Processed data:  {PROCESSED_DATA_PATH}/")
    print(f"  - Figures:         docs/figures/")
    print(f"  - Logs:            logs/main.log")
    print(f"  - MLflow:          mlflow.db  (run: mlflow ui)")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
