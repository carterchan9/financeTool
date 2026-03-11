# Phase 2: Advanced ML Models — Full Outline

**Status**: Planned
**Depends on**: Phase 1 complete ✅
**Key Libraries**: PyTorch, Optuna, MLflow

---

## Goals

- Add sequence-aware deep learning models (LSTM, GRU) that see the last N days instead of a single-day snapshot
- Tune hyperparameters systematically with Optuna instead of guessing
- Track all experiments (params, metrics, artifacts) with MLflow so results are reproducible and comparable

---

## New Files

### `src/lstm_model.py`

The core PyTorch module.

#### `SequenceDataset` (PyTorch Dataset)
- Takes `X` (n_days × n_features) and `y` (n_days,)
- Sliding window: for index `i`, return `X[i:i+seq_len]` as input, `y[i+seq_len]` as label
- This is what gives LSTM/GRU temporal context — each prediction sees the past 20 days

#### `LSTMModel` (nn.Module)
- Architecture: `LSTM → Dropout → Linear(1) → Sigmoid`
- Configurable: `hidden_size`, `num_layers`, `dropout`
- Input shape: `(batch, seq_len, n_features)` → output: `(batch,)` probabilities

#### `GRUModel` (nn.Module)
- Same architecture as LSTM but using GRU cells
- Fewer parameters than LSTM, often comparable performance, trains faster

#### `prepare_sequences()`
- Scales features with `StandardScaler` (fit on train only — no leakage)
- Returns `train_loader`, `test_loader`, `scaler`

#### `train_sequence_model()`
- Adam optimizer + BCELoss
- Early stopping (patience=10 epochs without improvement)
- Returns list of per-epoch losses

#### `predict_sequence()`
- Returns binary predictions and raw probabilities
- **Important**: predictions align with `y_test[seq_len:]` not `y_test[:]` — needs care in main pipeline

#### `get_device()`
- Returns `"mps"` on Apple Silicon, `"cuda"` if available, else `"cpu"`

---

### `src/tuner.py`

Optuna-based hyperparameter search.

#### `objective_lstm(trial, X_train, y_train)`
- Suggests:
  - `hidden_size` ∈ {32, 64, 128}
  - `num_layers` ∈ {1, 2}
  - `dropout` ∈ [0.1, 0.4]
  - `lr` ∈ [1e-4, 1e-2]
  - `seq_len` ∈ {10, 20, 30}
- Trains on 80% of train set, validates on remaining 20% (time-ordered)
- Returns validation F1 score (maximize)

#### `tune_model(model_type, X_train, y_train, n_trials=30)`
- Runs Optuna study, returns best params
- Suppresses Optuna's verbose output during search

#### `get_default_params(model_type)`
- Returns sensible defaults (used when skipping tuning for speed)

---

## Updated Files

### `main.py`
- Add `import mlflow` at top
- In `process_ticker()`, after sklearn models:
  - Train LSTM and GRU using `prepare_sequences()` + `train_sequence_model()`
  - Align sequence predictions with the correct test window (`y_test[seq_len:]`)
  - Evaluate and add to `all_model_results` alongside LR/RF/XGB
  - Pick best across all 5 models by F1
- Wrap entire ticker run in `mlflow.start_run(run_name=ticker)`
  - Log params: `seq_len`, `n_epochs`, `hidden_size`, `lr`, ticker
  - Log metrics: accuracy, F1, AUC per model type
  - Log best model artifact with `mlflow.pytorch.log_model()`
- Summary table now shows LR / RF / XGB / LSTM / GRU columns

### `src/config.py`
Add Phase 2 constants:

```python
# Sequence model config
SEQ_LEN = 20           # Look-back window (days)
N_EPOCHS = 50          # Max training epochs
BATCH_SIZE = 32        # Training batch size
LSTM_HIDDEN = 64       # Hidden layer size
LSTM_LAYERS = 2        # Number of stacked layers
LSTM_DROPOUT = 0.2     # Dropout probability
LEARNING_RATE = 1e-3   # Adam learning rate

# Optuna
N_TUNING_TRIALS = 30   # Number of hyperparameter search trials

# MLflow
MLFLOW_EXPERIMENT = "finance-ml-phase2"
```

### `requirements.txt`
Add: `torch`, `optuna`, `mlflow`

---

## Pipeline Flow (updated `process_ticker`)

```
[1] Fetch data
[2] Engineer features         (same as Phase 1)
[3] Train/test split
[4] Train sklearn models      LR, RF, XGBoost   ← same as Phase 1
[5] Train sequence models     LSTM, GRU          ← NEW
    - Scale features
    - Build sliding-window sequences
    - Train with early stopping
    - Align predictions to test index
[6] Compare all 5 models      pick best by F1    ← extended
[7] Backtest best model
[8] Visualizations
[9] Log everything to MLflow                     ← NEW
```

---

## Expected Outcomes

- LSTM/GRU may outperform sklearn on trending assets (TSLA, BTC) where momentum matters
- On mean-reverting assets (TLT, GLD) sklearn likely still wins
- MLflow UI (`mlflow ui`) lets you compare all runs in a browser
- Optuna tuning script can be run separately to find best hyperparams before the main run

---

## What's NOT in Phase 2

- No walk-forward / time-series cross-validation (Phase 3+)
- No news/sentiment data (Phase 3)
- No portfolio-level optimization (Phase 4)
- No cloud deployment (Phase 5)
