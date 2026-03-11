"""
LSTM/GRU Model Module for Phase 2.

This module implements sequence-based deep learning models using PyTorch.
The key difference from Phase 1 sklearn models: instead of using a single
day's features as input, sequence models see the last N days — capturing
temporal patterns like trends, momentum reversals, and volatility cycles.

Classes:
    SequenceDataset: Sliding-window PyTorch Dataset
    LSTMModel:       LSTM-based binary classifier
    GRUModel:        GRU-based binary classifier

Functions:
    prepare_sequences:      Scale features and build DataLoaders
    train_sequence_model:   Training loop with early stopping
    predict_sequence:       Inference — returns predictions + probabilities
    get_device:             Best available device (MPS > CUDA > CPU)
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Dataset
# ============================================================================

class SequenceDataset(Dataset):
    """
    PyTorch Dataset that creates sliding-window sequences from tabular data.

    For each index i, the sample is:
        X: features[i : i + seq_len]   shape (seq_len, n_features)
        y: target[i + seq_len]          scalar

    This gives the model temporal context — it sees the past `seq_len` days
    before making a prediction about the next day.

    Args:
        X:       Feature array, shape (n_days, n_features)
        y:       Target array, shape (n_days,)
        seq_len: Number of past days to look back (default: 20)
    """

    def __init__(self, X: np.ndarray, y: np.ndarray, seq_len: int = 20):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
        self.seq_len = seq_len

    def __len__(self):
        return len(self.X) - self.seq_len

    def __getitem__(self, idx):
        x_seq = self.X[idx : idx + self.seq_len]    # (seq_len, n_features)
        y_label = self.y[idx + self.seq_len]         # scalar
        return x_seq, y_label


# ============================================================================
# Models
# ============================================================================

class LSTMModel(nn.Module):
    """
    LSTM-based binary classifier.

    Architecture:
        LSTM (stacked) → Dropout → Linear(hidden → 1) → Sigmoid

    LSTM cells maintain a hidden state and a cell state across timesteps,
    making them well-suited for capturing long-range dependencies in sequences.

    Args:
        input_size:  Number of features per timestep (10 for Phase 1 features)
        hidden_size: LSTM hidden state dimension
        num_layers:  Number of stacked LSTM layers
        dropout:     Dropout probability (applied between LSTM layers and before FC)
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # x: (batch, seq_len, input_size)
        out, _ = self.lstm(x)        # (batch, seq_len, hidden_size)
        out = out[:, -1, :]          # last timestep: (batch, hidden_size)
        out = self.dropout(out)
        out = self.fc(out)           # (batch, 1)
        return torch.sigmoid(out).squeeze(1)   # (batch,)


class GRUModel(nn.Module):
    """
    GRU-based binary classifier.

    Architecture:
        GRU (stacked) → Dropout → Linear(hidden → 1) → Sigmoid

    GRU is a simpler alternative to LSTM with fewer parameters (no separate
    cell state). Often matches LSTM performance while training faster.

    Args:
        input_size:  Number of features per timestep
        hidden_size: GRU hidden state dimension
        num_layers:  Number of stacked GRU layers
        dropout:     Dropout probability
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.gru(x)
        out = out[:, -1, :]
        out = self.dropout(out)
        out = self.fc(out)
        return torch.sigmoid(out).squeeze(1)


# ============================================================================
# Data preparation
# ============================================================================

def prepare_sequences(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    seq_len: int = 20,
    batch_size: int = 32,
) -> Tuple[DataLoader, DataLoader, StandardScaler]:
    """
    Scale features and create PyTorch DataLoaders for sequence training.

    Scaling is fit on training data only (no data leakage into test set).

    Args:
        X_train, y_train: Training arrays (numpy)
        X_test, y_test:   Test arrays (numpy)
        seq_len:          Sliding window length
        batch_size:       Batch size for DataLoader

    Returns:
        train_loader: DataLoader for training
        test_loader:  DataLoader for evaluation (shuffle=False)
        scaler:       Fitted StandardScaler (for inverse transform if needed)

    Note:
        Predictions from the test_loader align with y_test[seq_len:], not
        y_test[:]. Account for this offset when evaluating or backtesting.
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    train_ds = SequenceDataset(X_train_scaled, y_train, seq_len)
    test_ds = SequenceDataset(X_test_scaled, y_test, seq_len)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    logger.info(f"Sequence dataset: train={len(train_ds)}, test={len(test_ds)} samples (seq_len={seq_len})")

    return train_loader, test_loader, scaler


# ============================================================================
# Training
# ============================================================================

def train_sequence_model(
    model: nn.Module,
    train_loader: DataLoader,
    n_epochs: int = 50,
    lr: float = 1e-3,
    patience: int = 10,
    device: str = "cpu",
) -> list:
    """
    Train a sequence model with Adam optimizer and early stopping.

    Early stopping halts training when loss stops improving (patience epochs
    without a decrease of > 1e-4), preventing overfitting on small datasets.

    Args:
        model:        LSTMModel or GRUModel instance
        train_loader: Training DataLoader
        n_epochs:     Maximum number of training epochs
        lr:           Adam learning rate
        patience:     Epochs without improvement before stopping
        device:       "cpu", "cuda", or "mps"

    Returns:
        losses: List of average loss per epoch
    """
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCELoss()

    best_loss = float('inf')
    patience_counter = 0
    losses = []

    model.train()
    for epoch in range(n_epochs):
        epoch_loss = 0.0

        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(train_loader)
        losses.append(avg_loss)

        # Early stopping
        if avg_loss < best_loss - 1e-4:
            best_loss = avg_loss
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"  Early stopping at epoch {epoch + 1} (loss={avg_loss:.4f})")
                break

        if (epoch + 1) % 10 == 0:
            logger.info(f"  Epoch {epoch + 1}/{n_epochs} — Loss: {avg_loss:.4f}")

    return losses


# ============================================================================
# Inference
# ============================================================================

def predict_sequence(
    model: nn.Module,
    test_loader: DataLoader,
    device: str = "cpu",
    threshold: float = 0.5,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate predictions from a trained sequence model.

    Args:
        model:       Trained LSTMModel or GRUModel
        test_loader: Test DataLoader
        device:      Device to run inference on
        threshold:   Classification threshold (default 0.5)

    Returns:
        predictions:  Binary array (0 or 1), shape (n_test - seq_len,)
        probabilities: Positive-class probabilities, shape (n_test - seq_len,)

    Note:
        Output length is n_test - seq_len. Align with y_test[seq_len:] and
        test_data.index[seq_len:] when evaluating or running backtest.
    """
    model.eval()
    all_probs = []

    with torch.no_grad():
        for X_batch, _ in test_loader:
            X_batch = X_batch.to(device)
            probs = model(X_batch)
            all_probs.append(probs.cpu().numpy())

    probabilities = np.concatenate(all_probs)
    predictions = (probabilities >= threshold).astype(int)

    return predictions, probabilities


# ============================================================================
# Utilities
# ============================================================================

def get_device() -> str:
    """
    Return the best available compute device.

    Priority: MPS (Apple Silicon) > CUDA (NVIDIA GPU) > CPU

    Returns:
        Device string: "mps", "cuda", or "cpu"
    """
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    return "cpu"


def get_sequence_probas_2d(probabilities: np.ndarray) -> np.ndarray:
    """
    Convert 1D positive-class probabilities to 2D array for evaluate_classification.

    Args:
        probabilities: 1D array of P(class=1)

    Returns:
        2D array of shape (n, 2) with [P(class=0), P(class=1)] columns
    """
    return np.column_stack([1 - probabilities, probabilities])
