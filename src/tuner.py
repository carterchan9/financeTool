"""
Hyperparameter Tuning Module for Phase 2.

Uses Optuna to search for the best LSTM/GRU hyperparameters via time-based
cross-validation on the training set. Run this standalone before the main
pipeline to find optimal params, then plug them into config.py.

Usage:
    python src/tuner.py --ticker AAPL --model lstm --trials 30

Functions:
    tune_model:  Run Optuna study and return best hyperparameters
    objective:   Optuna objective function (internal)
"""

import numpy as np
import optuna
import logging
import argparse
from sklearn.metrics import f1_score
from sklearn.preprocessing import StandardScaler

import torch

from src.lstm_model import LSTMModel, GRUModel, SequenceDataset, train_sequence_model
from torch.utils.data import DataLoader

# Silence optuna's per-trial output (keep only final summary)
optuna.logging.set_verbosity(optuna.logging.WARNING)

logger = logging.getLogger(__name__)


def objective(
    trial: optuna.Trial,
    model_type: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> float:
    """
    Optuna objective function.

    Splits X_train 80/20 (time-ordered), trains a sequence model on the
    first 80%, and returns F1 score on the held-out 20%.

    Hyperparameters searched:
        hidden_size:  {32, 64, 128}
        num_layers:   {1, 2}
        dropout:      [0.1, 0.4]
        lr:           [1e-4, 1e-2] (log scale)
        seq_len:      {10, 20, 30}
        batch_size:   {16, 32, 64}

    Args:
        trial:      Optuna trial object
        model_type: "lstm" or "gru"
        X_train:    Training features (unscaled), shape (n, n_features)
        y_train:    Training labels, shape (n,)

    Returns:
        F1 score on validation set (Optuna maximizes this)
    """
    hidden_size = trial.suggest_categorical("hidden_size", [32, 64, 128])
    num_layers = trial.suggest_categorical("num_layers", [1, 2])
    dropout = trial.suggest_float("dropout", 0.1, 0.4)
    lr = trial.suggest_float("lr", 1e-4, 1e-2, log=True)
    seq_len = trial.suggest_categorical("seq_len", [10, 20, 30])
    batch_size = trial.suggest_categorical("batch_size", [16, 32, 64])

    # Time-ordered 80/20 split of training data
    split = int(len(X_train) * 0.8)
    X_tr, y_tr = X_train[:split], y_train[:split]
    X_val, y_val = X_train[split:], y_train[split:]

    # Need enough data for at least one sequence
    if len(X_tr) <= seq_len or len(X_val) <= seq_len:
        return 0.0

    # Scale features
    scaler = StandardScaler()
    X_tr_scaled = scaler.fit_transform(X_tr)
    X_val_scaled = scaler.transform(X_val)

    # Build datasets
    train_ds = SequenceDataset(X_tr_scaled, y_tr, seq_len)
    val_ds = SequenceDataset(X_val_scaled, y_val, seq_len)

    if len(train_ds) == 0 or len(val_ds) == 0:
        return 0.0

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=False)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    # Build model
    n_features = X_train.shape[1]
    device = "cpu"  # tuning runs on CPU for stability

    if model_type == "lstm":
        model = LSTMModel(n_features, hidden_size, num_layers, dropout)
    else:
        model = GRUModel(n_features, hidden_size, num_layers, dropout)

    # Train with reduced epochs for speed during search
    train_sequence_model(
        model, train_loader,
        n_epochs=30,
        lr=lr,
        patience=5,
        device=device,
    )

    # Evaluate on validation set
    model.eval()
    all_probs = []
    with torch.no_grad():
        for X_batch, _ in val_loader:
            probs = model(X_batch)
            all_probs.append(probs.numpy())

    if not all_probs:
        return 0.0

    probabilities = np.concatenate(all_probs)
    predictions = (probabilities >= 0.5).astype(int)

    y_val_aligned = y_val[seq_len:]
    if len(predictions) != len(y_val_aligned):
        return 0.0

    return f1_score(y_val_aligned, predictions, zero_division=0)


def tune_model(
    model_type: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    n_trials: int = 30,
) -> dict:
    """
    Run Optuna hyperparameter search and return the best params.

    Args:
        model_type: "lstm" or "gru"
        X_train:    Training features (unscaled numpy array)
        y_train:    Training labels (numpy array)
        n_trials:   Number of trials to run

    Returns:
        Dictionary of best hyperparameters, e.g.:
        {
            "hidden_size": 64,
            "num_layers": 2,
            "dropout": 0.2,
            "lr": 0.001,
            "seq_len": 20,
            "batch_size": 32,
        }

    Example:
        >>> best_params = tune_model("lstm", X_train, y_train, n_trials=30)
        >>> print(best_params)
    """
    logger.info(f"Starting Optuna search: {model_type.upper()}, {n_trials} trials...")

    study = optuna.create_study(direction="maximize")
    study.optimize(
        lambda trial: objective(trial, model_type, X_train, y_train),
        n_trials=n_trials,
        show_progress_bar=False,
    )

    best_params = study.best_params
    best_value = study.best_value

    logger.info(f"Best {model_type.upper()} F1: {best_value:.4f}")
    logger.info(f"Best params: {best_params}")

    return best_params


def get_default_params(model_type: str) -> dict:
    """
    Return sensible default hyperparameters (used when skipping tuning).

    Args:
        model_type: "lstm" or "gru"

    Returns:
        Dictionary of default hyperparameters
    """
    return {
        "hidden_size": 64,
        "num_layers": 2,
        "dropout": 0.2,
        "lr": 1e-3,
        "seq_len": 20,
        "batch_size": 32,
    }


# ============================================================================
# Standalone runner
# ============================================================================

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(description="Tune LSTM/GRU hyperparameters with Optuna")
    parser.add_argument("--ticker", default="AAPL", help="Ticker to tune on")
    parser.add_argument("--model", default="lstm", choices=["lstm", "gru"])
    parser.add_argument("--trials", type=int, default=30)
    args = parser.parse_args()

    from src.data_loader import fetch_price_data
    from src.features import compute_features
    from src.config import START_DATE, TEST_SPLIT_DATE

    print(f"\nTuning {args.model.upper()} on {args.ticker} ({args.trials} trials)...")

    df_raw = fetch_price_data(args.ticker, START_DATE, TEST_SPLIT_DATE)
    df_features = compute_features(df_raw)

    train_data = df_features[df_features.index < TEST_SPLIT_DATE]
    X_train = train_data.drop("target", axis=1).values
    y_train = train_data["target"].values

    best_params = tune_model(args.model, X_train, y_train, n_trials=args.trials)

    print(f"\nBest params for {args.model.upper()} on {args.ticker}:")
    for k, v in best_params.items():
        print(f"  {k}: {v}")
    print(f"\nAdd these to src/config.py to use them in the main pipeline.")
