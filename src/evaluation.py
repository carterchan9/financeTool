"""
Evaluation Module for Phase 0 MVP.

This module provides comprehensive evaluation metrics for classification models.

Functions:
    evaluate_classification: Calculate all classification metrics
    print_evaluation_report: Pretty-print evaluation results
    calculate_accuracy: Calculate accuracy score
    calculate_precision_recall: Calculate precision and recall
    calculate_f1: Calculate F1 score
    get_confusion_matrix: Get confusion matrix
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score
)
from typing import Dict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def evaluate_classification(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray = None
) -> Dict:
    """
    Calculate comprehensive classification metrics.

    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_proba: Prediction probabilities (optional, for AUC-ROC)

    Returns:
        Dictionary containing:
            - accuracy: Overall accuracy
            - precision: Precision score
            - recall: Recall score
            - f1: F1 score
            - confusion_matrix: 2x2 confusion matrix
            - auc_roc: AUC-ROC score (if y_proba provided)

    Example:
        >>> metrics = evaluate_classification(y_test, predictions)
        >>> print(f"Accuracy: {metrics['accuracy']:.3f}")
    """
    logger.info("Calculating evaluation metrics...")

    # Convert to numpy arrays if needed
    if isinstance(y_true, pd.Series):
        y_true = y_true.values
    if isinstance(y_pred, pd.Series):
        y_pred = y_pred.values

    metrics = {}

    # Basic metrics
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    metrics['precision'] = precision_score(y_true, y_pred, zero_division=0)
    metrics['recall'] = recall_score(y_true, y_pred, zero_division=0)
    metrics['f1'] = f1_score(y_true, y_pred, zero_division=0)

    # Confusion matrix
    metrics['confusion_matrix'] = confusion_matrix(y_true, y_pred)

    # AUC-ROC if probabilities provided
    if y_proba is not None:
        try:
            # If y_proba has 2 columns, use the positive class probability
            if len(y_proba.shape) > 1 and y_proba.shape[1] == 2:
                y_proba = y_proba[:, 1]
            metrics['auc_roc'] = roc_auc_score(y_true, y_proba)
        except Exception as e:
            logger.warning(f"Could not calculate AUC-ROC: {e}")
            metrics['auc_roc'] = None

    # Additional metrics
    tn, fp, fn, tp = metrics['confusion_matrix'].ravel()

    metrics['true_positives'] = int(tp)
    metrics['true_negatives'] = int(tn)
    metrics['false_positives'] = int(fp)
    metrics['false_negatives'] = int(fn)

    # Specificity (True Negative Rate)
    metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0

    # Number of samples
    metrics['n_samples'] = len(y_true)
    metrics['n_positive'] = int(y_true.sum())
    metrics['n_negative'] = int(len(y_true) - y_true.sum())

    logger.info("✅ Evaluation complete")

    return metrics


def print_evaluation_report(
    metrics: Dict,
    title: str = "Model Evaluation Report"
) -> None:
    """
    Pretty-print evaluation metrics.

    Args:
        metrics: Dictionary of metrics from evaluate_classification
        title: Report title

    Example:
        >>> metrics = evaluate_classification(y_test, predictions)
        >>> print_evaluation_report(metrics, "Test Set Results")
    """
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    # Basic metrics
    print("\nClassification Metrics:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1']:.4f}")

    if 'specificity' in metrics:
        print(f"  Specificity: {metrics['specificity']:.4f}")

    if 'auc_roc' in metrics and metrics['auc_roc'] is not None:
        print(f"  AUC-ROC:   {metrics['auc_roc']:.4f}")

    # Sample counts
    print("\nSample Distribution:")
    print(f"  Total Samples: {metrics['n_samples']}")
    print(f"  Positive (1):  {metrics['n_positive']} ({metrics['n_positive']/metrics['n_samples']*100:.1f}%)")
    print(f"  Negative (0):  {metrics['n_negative']} ({metrics['n_negative']/metrics['n_samples']*100:.1f}%)")

    # Confusion matrix
    print("\nConfusion Matrix:")
    cm = metrics['confusion_matrix']
    print(f"                 Predicted")
    print(f"                 0        1")
    print(f"  Actual 0    {cm[0,0]:5d}   {cm[0,1]:5d}")
    print(f"  Actual 1    {cm[1,0]:5d}   {cm[1,1]:5d}")

    print("\nConfusion Matrix Breakdown:")
    print(f"  True Negatives:  {metrics['true_negatives']}")
    print(f"  False Positives: {metrics['false_positives']}")
    print(f"  False Negatives: {metrics['false_negatives']}")
    print(f"  True Positives:  {metrics['true_positives']}")

    print("=" * 60 + "\n")


def calculate_classification_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_names: list = None
) -> str:
    """
    Generate sklearn classification report.

    Args:
        y_true: True labels
        y_pred: Predicted labels
        target_names: Names for classes (default: ["Down", "Up"])

    Returns:
        Classification report string

    Example:
        >>> report = calculate_classification_report(y_test, predictions)
        >>> print(report)
    """
    if target_names is None:
        target_names = ["Down (0)", "Up (1)"]

    report = classification_report(y_true, y_pred, target_names=target_names)
    return report


def compare_models(
    results: Dict[str, Dict]
) -> pd.DataFrame:
    """
    Compare multiple model results side by side.

    Args:
        results: Dictionary mapping model name to metrics dictionary

    Returns:
        DataFrame with models as rows and metrics as columns

    Example:
        >>> results = {
        ...     "Logistic Regression": metrics_lr,
        ...     "Random Forest": metrics_rf
        ... }
        >>> comparison = compare_models(results)
        >>> print(comparison)
    """
    comparison_data = []

    for model_name, metrics in results.items():
        row = {
            'Model': model_name,
            'Accuracy': metrics['accuracy'],
            'Precision': metrics['precision'],
            'Recall': metrics['recall'],
            'F1': metrics['f1'],
        }

        if 'auc_roc' in metrics and metrics['auc_roc'] is not None:
            row['AUC-ROC'] = metrics['auc_roc']

        comparison_data.append(row)

    df = pd.DataFrame(comparison_data)
    return df


def calculate_baseline_accuracy(y_true: np.ndarray) -> float:
    """
    Calculate baseline accuracy (always predict majority class).

    Args:
        y_true: True labels

    Returns:
        Baseline accuracy score

    Example:
        >>> baseline = calculate_baseline_accuracy(y_test)
        >>> print(f"Our model must beat: {baseline:.3f}")
    """
    # Count occurrences
    unique, counts = np.unique(y_true, return_counts=True)
    majority_count = counts.max()
    total = len(y_true)

    baseline = majority_count / total

    logger.info(f"Baseline accuracy (majority class): {baseline:.4f}")

    return baseline


def is_better_than_baseline(
    metrics: Dict,
    y_true: np.ndarray,
    threshold: float = 0.05
) -> bool:
    """
    Check if model performs significantly better than baseline.

    Args:
        metrics: Model metrics dictionary
        y_true: True labels
        threshold: Minimum improvement required (default: 5%)

    Returns:
        True if model beats baseline by threshold

    Example:
        >>> if is_better_than_baseline(metrics, y_test):
        ...     print("Model is useful!")
    """
    baseline = calculate_baseline_accuracy(y_true)
    model_acc = metrics['accuracy']

    improvement = model_acc - baseline
    beats_baseline = improvement > threshold

    print(f"\nBaseline vs Model:")
    print(f"  Baseline accuracy: {baseline:.4f}")
    print(f"  Model accuracy:    {model_acc:.4f}")
    print(f"  Improvement:       {improvement:+.4f} ({improvement*100:+.2f}%)")
    print(f"  Beats baseline:    {'✅ Yes' if beats_baseline else '❌ No'}")

    return beats_baseline


if __name__ == "__main__":
    # Test evaluation module
    print("Testing Evaluation Module")
    print("=" * 60)

    # Create sample predictions
    np.random.seed(42)
    n_samples = 100

    # True labels (slightly imbalanced)
    y_true = np.random.binomial(1, 0.55, n_samples)

    # Predictions with ~70% accuracy
    y_pred = y_true.copy()
    # Flip 30% of predictions
    flip_indices = np.random.choice(n_samples, size=int(n_samples * 0.3), replace=False)
    y_pred[flip_indices] = 1 - y_pred[flip_indices]

    # Prediction probabilities
    y_proba = np.random.rand(n_samples, 2)
    y_proba = y_proba / y_proba.sum(axis=1, keepdims=True)  # Normalize

    print("\n1. Testing basic evaluation...")
    metrics = evaluate_classification(y_true, y_pred, y_proba)
    print("✅ Metrics calculated")

    print("\n2. Testing evaluation report...")
    print_evaluation_report(metrics, "Test Evaluation")

    print("\n3. Testing classification report...")
    report = calculate_classification_report(y_true, y_pred)
    print(report)

    print("\n4. Testing baseline comparison...")
    baseline = calculate_baseline_accuracy(y_true)
    is_better = is_better_than_baseline(metrics, y_true)

    print("\n5. Testing model comparison...")
    # Simulate two models
    metrics2 = metrics.copy()
    metrics2['accuracy'] = 0.65
    metrics2['f1'] = 0.62

    results = {
        "Model A": metrics,
        "Model B": metrics2
    }

    comparison = compare_models(results)
    print("\nModel Comparison:")
    print(comparison.to_string(index=False))

    print("\n" + "=" * 60)
    print("Evaluation Module test complete!")
