"""
Visualization Module for Phase 0 MVP.

This module creates informative visualizations of data, features, and model results.

Functions:
    plot_price_history: Plot stock price over time
    plot_features: Plot all engineered features
    plot_price_with_predictions: Price chart with prediction markers
    plot_confusion_matrix: Heatmap of confusion matrix
    plot_feature_importance: Bar chart of feature importance
    plot_predictions_timeline: Timeline showing prediction correctness
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import logging

from src.config import (
    FIGURES_PATH,
    FIGURE_SIZE,
    FIGURE_DPI,
    FIGURE_FORMAT,
    PLOT_STYLE
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set plot style
try:
    plt.style.use(PLOT_STYLE)
except:
    plt.style.use('default')
    logger.warning(f"Could not load style '{PLOT_STYLE}', using default")


def _setup_figure_path():
    """Create figures directory if it doesn't exist."""
    figures_dir = Path(FIGURES_PATH)
    figures_dir.mkdir(parents=True, exist_ok=True)
    return figures_dir


def plot_price_history(
    df: pd.DataFrame,
    ticker: str,
    save: bool = True
) -> plt.Figure:
    """
    Plot closing price history.

    Args:
        df: DataFrame with 'Close' column and date index
        ticker: Stock ticker for title
        save: Whether to save figure to disk

    Returns:
        matplotlib Figure object

    Example:
        >>> fig = plot_price_history(df, "AAPL")
        >>> plt.show()
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    ax.plot(df.index, df['Close'], linewidth=2, color='#2E86DE')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.set_title(f'{ticker} - Price History', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save:
        figures_dir = _setup_figure_path()
        filepath = figures_dir / f'{ticker}_price_history.{FIGURE_FORMAT}'
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        logger.info(f"Saved figure: {filepath}")

    return fig


def plot_features(
    df: pd.DataFrame,
    ticker: str = "Stock",
    save: bool = True
) -> plt.Figure:
    """
    Plot all engineered features in subplots.

    Args:
        df: DataFrame with feature columns
        ticker: Stock ticker for title
        save: Whether to save figure to disk

    Returns:
        matplotlib Figure object

    Example:
        >>> fig = plot_features(df_features, "AAPL")
        >>> plt.show()
    """
    # Determine features to plot (exclude target)
    feature_cols = [col for col in df.columns if col != 'target']

    n_features = len(feature_cols)
    n_cols = 2
    n_rows = (n_features + 1) // 2

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 3*n_rows))
    axes = axes.flatten() if n_features > 1 else [axes]

    for idx, col in enumerate(feature_cols):
        ax = axes[idx]
        ax.plot(df.index, df[col], linewidth=1, alpha=0.7)
        ax.set_title(col.replace('_', ' ').title(), fontsize=11)
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)

    # Remove extra subplots
    for idx in range(n_features, len(axes)):
        fig.delaxes(axes[idx])

    plt.suptitle(f'{ticker} - Engineered Features', fontsize=14, fontweight='bold')
    plt.tight_layout()

    if save:
        figures_dir = _setup_figure_path()
        filepath = figures_dir / f'{ticker}_features.{FIGURE_FORMAT}'
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        logger.info(f"Saved figure: {filepath}")

    return fig


def plot_price_with_predictions(
    df: pd.DataFrame,
    predictions: np.ndarray,
    ticker: str,
    actual_col: str = 'target',
    save: bool = True
) -> plt.Figure:
    """
    Plot price with buy/sell prediction markers.

    Green markers: Predicted up (1)
    Red markers: Predicted down (0)

    Args:
        df: DataFrame with 'Close' column and date index
        predictions: Array of predictions (0 or 1)
        ticker: Stock ticker for title
        actual_col: Column name for actual outcomes (optional)
        save: Whether to save figure to disk

    Returns:
        matplotlib Figure object

    Example:
        >>> fig = plot_price_with_predictions(df_test, predictions, "AAPL")
        >>> plt.show()
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # Plot price line
    ax.plot(df.index, df['Close'], linewidth=2, color='#2E86DE', label='Close Price', alpha=0.7)

    # Plot predictions
    pred_up = predictions == 1
    pred_down = predictions == 0

    ax.scatter(df.index[pred_up], df['Close'][pred_up],
              marker='^', color='green', s=100, alpha=0.6,
              label='Predicted Up', zorder=5)

    ax.scatter(df.index[pred_down], df['Close'][pred_down],
              marker='v', color='red', s=100, alpha=0.6,
              label='Predicted Down', zorder=5)

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.set_title(f'{ticker} - Price with Predictions', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save:
        figures_dir = _setup_figure_path()
        filepath = figures_dir / f'{ticker}_predictions.{FIGURE_FORMAT}'
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        logger.info(f"Saved figure: {filepath}")

    return fig


def plot_confusion_matrix(
    cm: np.ndarray,
    title: str = "Confusion Matrix",
    save: bool = True,
    filename: str = "confusion_matrix"
) -> plt.Figure:
    """
    Plot confusion matrix as heatmap.

    Args:
        cm: Confusion matrix array
        title: Plot title
        save: Whether to save figure to disk
        filename: Filename (without extension)

    Returns:
        matplotlib Figure object

    Example:
        >>> from sklearn.metrics import confusion_matrix
        >>> cm = confusion_matrix(y_true, y_pred)
        >>> fig = plot_confusion_matrix(cm)
        >>> plt.show()
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Down (0)', 'Up (1)'],
                yticklabels=['Down (0)', 'Up (1)'],
                cbar_kws={'label': 'Count'},
                ax=ax)

    ax.set_xlabel('Predicted Label', fontsize=12)
    ax.set_ylabel('True Label', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')

    plt.tight_layout()

    if save:
        figures_dir = _setup_figure_path()
        filepath = figures_dir / f'{filename}.{FIGURE_FORMAT}'
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        logger.info(f"Saved figure: {filepath}")

    return fig


def plot_feature_importance(
    importance_df: pd.DataFrame,
    title: str = "Feature Importance",
    save: bool = True,
    filename: str = "feature_importance"
) -> plt.Figure:
    """
    Plot feature importance as horizontal bar chart.

    Args:
        importance_df: DataFrame with 'feature' and 'importance' columns
        title: Plot title
        save: Whether to save figure to disk
        filename: Filename (without extension)

    Returns:
        matplotlib Figure object

    Example:
        >>> from src.model import get_feature_importance
        >>> importance = get_feature_importance(model, feature_names)
        >>> fig = plot_feature_importance(importance)
        >>> plt.show()
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Sort by importance
    importance_df = importance_df.sort_values('importance', ascending=True)

    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(importance_df)))

    ax.barh(importance_df['feature'], importance_df['importance'], color=colors)
    ax.set_xlabel('Importance', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()

    if save:
        figures_dir = _setup_figure_path()
        filepath = figures_dir / f'{filename}.{FIGURE_FORMAT}'
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        logger.info(f"Saved figure: {filepath}")

    return fig


def plot_predictions_timeline(
    df: pd.DataFrame,
    predictions: np.ndarray,
    y_true: np.ndarray,
    ticker: str,
    save: bool = True
) -> plt.Figure:
    """
    Plot timeline showing correct vs incorrect predictions.

    Args:
        df: DataFrame with date index
        predictions: Predicted labels
        y_true: True labels
        ticker: Stock ticker for title
        save: Whether to save figure to disk

    Returns:
        matplotlib Figure object

    Example:
        >>> fig = plot_predictions_timeline(df_test, predictions, y_test, "AAPL")
        >>> plt.show()
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # Calculate correctness
    correct = predictions == y_true
    incorrect = ~correct

    # Plot as scatter
    y_values = np.ones(len(predictions))

    ax.scatter(df.index[correct], y_values[correct],
              marker='o', color='green', s=50, alpha=0.6,
              label=f'Correct ({correct.sum()})')

    ax.scatter(df.index[incorrect], y_values[incorrect],
              marker='x', color='red', s=100, alpha=0.8,
              label=f'Incorrect ({incorrect.sum()})')

    # Calculate accuracy
    accuracy = correct.sum() / len(predictions)

    ax.set_xlabel('Date', fontsize=12)
    ax.set_yticks([])
    ax.set_title(f'{ticker} - Prediction Accuracy Timeline (Acc: {accuracy:.2%})',
                fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()

    if save:
        figures_dir = _setup_figure_path()
        filepath = figures_dir / f'{ticker}_accuracy_timeline.{FIGURE_FORMAT}'
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        logger.info(f"Saved figure: {filepath}")

    return fig


def plot_model_comparison(
    comparison_df: pd.DataFrame,
    save: bool = True
) -> plt.Figure:
    """
    Plot bar chart comparing multiple models.

    Args:
        comparison_df: DataFrame from evaluation.compare_models()
        save: Whether to save figure to disk

    Returns:
        matplotlib Figure object

    Example:
        >>> comparison = compare_models(results)
        >>> fig = plot_model_comparison(comparison)
        >>> plt.show()
    """
    metrics = [col for col in comparison_df.columns if col != 'Model']
    n_metrics = len(metrics)

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(comparison_df))
    width = 0.8 / n_metrics

    for idx, metric in enumerate(metrics):
        offset = (idx - n_metrics/2 + 0.5) * width
        ax.bar(x + offset, comparison_df[metric],
               width, label=metric, alpha=0.8)

    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Model Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(comparison_df['Model'], rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1)

    plt.tight_layout()

    if save:
        figures_dir = _setup_figure_path()
        filepath = figures_dir / f'model_comparison.{FIGURE_FORMAT}'
        plt.savefig(filepath, dpi=FIGURE_DPI, bbox_inches='tight')
        logger.info(f"Saved figure: {filepath}")

    return fig


if __name__ == "__main__":
    # Test visualization module
    print("Testing Visualization Module")
    print("=" * 60)

    from src.test_utils import generate_sample_price_data
    from src.features import compute_features

    # Generate sample data
    print("\n1. Generating sample data...")
    df_raw = generate_sample_price_data(n_days=252)
    df_features = compute_features(df_raw)
    print("✅ Data generated")

    # Test price history plot
    print("\n2. Testing price history plot...")
    fig1 = plot_price_history(df_raw, "TEST", save=True)
    plt.close(fig1)
    print("✅ Price history plot created")

    # Test features plot
    print("\n3. Testing features plot...")
    fig2 = plot_features(df_features, "TEST", save=True)
    plt.close(fig2)
    print("✅ Features plot created")

    # Test predictions plot
    print("\n4. Testing predictions plot...")
    # Generate fake predictions (use raw data for price plot)
    np.random.seed(42)
    predictions = np.random.randint(0, 2, len(df_raw[-len(df_features):]))
    df_raw_subset = df_raw[-len(df_features):]
    fig3 = plot_price_with_predictions(df_raw_subset, predictions, "TEST", save=True)
    plt.close(fig3)
    print("✅ Predictions plot created")

    # Test confusion matrix plot
    print("\n5. Testing confusion matrix plot...")
    cm = np.array([[30, 20], [15, 35]])
    fig4 = plot_confusion_matrix(cm, save=True)
    plt.close(fig4)
    print("✅ Confusion matrix plot created")

    # Test feature importance plot
    print("\n6. Testing feature importance plot...")
    importance_df = pd.DataFrame({
        'feature': ['returns', 'ma_5', 'ma_20', 'volatility', 'price_to_ma'],
        'importance': [0.25, 0.20, 0.18, 0.22, 0.15]
    })
    fig5 = plot_feature_importance(importance_df, save=True)
    plt.close(fig5)
    print("✅ Feature importance plot created")

    # Test predictions timeline
    print("\n7. Testing predictions timeline plot...")
    y_true = df_features['target'].values
    fig6 = plot_predictions_timeline(df_features, predictions, y_true, "TEST", save=True)
    plt.close(fig6)
    print("✅ Predictions timeline plot created")

    # Test model comparison plot
    print("\n8. Testing model comparison plot...")
    comparison_df = pd.DataFrame({
        'Model': ['Logistic Regression', 'Random Forest'],
        'Accuracy': [0.68, 0.72],
        'Precision': [0.65, 0.70],
        'Recall': [0.62, 0.68]
    })
    fig7 = plot_model_comparison(comparison_df, save=True)
    plt.close(fig7)
    print("✅ Model comparison plot created")

    print(f"\n✅ All figures saved to {FIGURES_PATH}/")
    print("\n" + "=" * 60)
    print("Visualization Module test complete!")
