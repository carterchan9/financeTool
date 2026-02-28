"""
Backtesting Engine for Phase 1.

Simulates trading based on model predictions and measures real-world
profitability — bridging ML accuracy with actual trading returns.

Strategy: Long-only
    - Predict 1 (up)  → invest 100% in the asset next day
    - Predict 0 (down) → hold cash (0% invested) next day

Benchmark: Buy-and-hold (always fully invested)

Key metrics:
    total_return:   Cumulative % gain over the test period
    sharpe_ratio:   Risk-adjusted return (annualised)
    max_drawdown:   Largest peak-to-trough loss
    win_rate:       % of invested days that ended positive

Functions:
    run_backtest: Simulate strategy and return equity curves
    compute_backtest_metrics: Calculate performance statistics
    print_backtest_report: Print formatted results
"""

import numpy as np
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def run_backtest(
    predictions: np.ndarray,
    df_raw_test: pd.DataFrame,
) -> dict:
    """
    Simulate a long-only strategy using model predictions.

    On each day in the test period, if the model predicted "up" (1) for
    that day, we are invested and capture that day's return. If the model
    predicted "down" (0), we hold cash and earn 0%.

    Args:
        predictions: Array of 0/1 predictions aligned with df_raw_test index
        df_raw_test: Raw price DataFrame for the test period (needs 'Close')

    Returns:
        Dictionary with:
            strategy_returns:  Daily returns of the strategy
            bah_returns:       Daily returns of buy-and-hold
            strategy_equity:   Cumulative equity curve of strategy (starts at 1.0)
            bah_equity:        Cumulative equity curve of buy-and-hold
            dates:             DatetimeIndex aligned to the returns
    """
    df = df_raw_test.copy()

    # Daily returns of the underlying asset
    daily_returns = df['Close'].pct_change().fillna(0)

    # Align predictions to the same index
    pred_series = pd.Series(predictions, index=df.index, dtype=float)

    # Strategy: invested on days where prediction = 1, cash otherwise
    # We use the prediction from day t to decide whether to hold on day t
    # (model predicts next-day direction, so prediction[t] applies to day t+1)
    # Shift predictions forward by 1 so we "act" on tomorrow using today's signal
    strategy_returns = daily_returns * pred_series.shift(1).fillna(0)

    # Buy-and-hold: always invested
    bah_returns = daily_returns

    # Equity curves (compound growth from 1.0)
    strategy_equity = (1 + strategy_returns).cumprod()
    bah_equity = (1 + bah_returns).cumprod()

    return {
        'strategy_returns': strategy_returns,
        'bah_returns': bah_returns,
        'strategy_equity': strategy_equity,
        'bah_equity': bah_equity,
        'dates': df.index,
    }


def compute_backtest_metrics(backtest_result: dict) -> dict:
    """
    Compute performance statistics from a backtest result.

    Args:
        backtest_result: Dictionary returned by run_backtest()

    Returns:
        Dictionary with performance metrics:
            strategy_total_return: Strategy total % return
            bah_total_return:      Buy-and-hold total % return
            strategy_sharpe:       Annualised Sharpe ratio (risk-free = 0)
            bah_sharpe:            Buy-and-hold Sharpe ratio
            strategy_max_drawdown: Worst peak-to-trough drawdown
            bah_max_drawdown:      Buy-and-hold worst drawdown
            win_rate:              % of invested days that were profitable
            n_invested_days:       Number of days the strategy was invested
            n_total_days:          Total number of trading days in test period
    """
    sr = backtest_result['strategy_returns']
    br = backtest_result['bah_returns']
    se = backtest_result['strategy_equity']
    be = backtest_result['bah_equity']

    def total_return(equity: pd.Series) -> float:
        return float(equity.iloc[-1] - 1) * 100  # as percentage

    def sharpe(returns: pd.Series) -> float:
        if returns.std() == 0:
            return 0.0
        return float(returns.mean() / returns.std() * np.sqrt(252))

    def max_drawdown(equity: pd.Series) -> float:
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        return float(drawdown.min() * 100)  # as percentage (negative)

    # Win rate: among days where we were invested, how often did we profit?
    invested_days = sr[sr != 0]
    win_rate = float((invested_days > 0).mean() * 100) if len(invested_days) > 0 else 0.0

    return {
        'strategy_total_return': total_return(se),
        'bah_total_return': total_return(be),
        'strategy_sharpe': sharpe(sr),
        'bah_sharpe': sharpe(br),
        'strategy_max_drawdown': max_drawdown(se),
        'bah_max_drawdown': max_drawdown(be),
        'win_rate': win_rate,
        'n_invested_days': int((sr != 0).sum()),
        'n_total_days': int(len(sr)),
    }


def print_backtest_report(metrics: dict, ticker: str) -> None:
    """
    Print a formatted backtest performance report.

    Args:
        metrics: Dictionary returned by compute_backtest_metrics()
        ticker: Asset name for the report header
    """
    print(f"\n{'─'*50}")
    print(f"  Backtest Report: {ticker}")
    print(f"{'─'*50}")

    invested_pct = metrics['n_invested_days'] / metrics['n_total_days'] * 100
    print(f"  Days:             {metrics['n_total_days']} total, "
          f"{metrics['n_invested_days']} invested ({invested_pct:.0f}%)")

    print(f"\n  {'Metric':<22} {'Strategy':>10} {'Buy & Hold':>10}")
    print(f"  {'─'*44}")

    def fmt_pct(v):
        sign = '+' if v >= 0 else ''
        return f"{sign}{v:.1f}%"

    def fmt_ratio(v):
        sign = '+' if v >= 0 else ''
        return f"{sign}{v:.2f}"

    print(f"  {'Total Return':<22} "
          f"{fmt_pct(metrics['strategy_total_return']):>10} "
          f"{fmt_pct(metrics['bah_total_return']):>10}")
    print(f"  {'Sharpe Ratio':<22} "
          f"{fmt_ratio(metrics['strategy_sharpe']):>10} "
          f"{fmt_ratio(metrics['bah_sharpe']):>10}")
    print(f"  {'Max Drawdown':<22} "
          f"{fmt_pct(metrics['strategy_max_drawdown']):>10} "
          f"{fmt_pct(metrics['bah_max_drawdown']):>10}")
    print(f"  {'Win Rate (invested)':<22} {metrics['win_rate']:>9.1f}%")

    # Summary verdict
    outperforms = metrics['strategy_total_return'] > metrics['bah_total_return']
    label = "OUTPERFORMS buy & hold" if outperforms else "underperforms buy & hold"
    icon = "✅" if outperforms else "📉"
    print(f"\n  {icon}  Strategy {label}")
    print(f"{'─'*50}")


def plot_equity_curves(
    backtest_result: dict,
    ticker: str,
    save: bool = True,
) -> None:
    """
    Plot strategy equity curve vs buy-and-hold.

    Args:
        backtest_result: Dictionary returned by run_backtest()
        ticker: Asset ticker for title and filename
        save: Whether to save the figure to docs/figures/
    """
    import matplotlib.pyplot as plt
    from src.config import FIGURES_PATH, FIGURE_DPI, PLOT_STYLE

    try:
        plt.style.use(PLOT_STYLE)
    except OSError:
        plt.style.use('seaborn-v0_8')

    fig, ax = plt.subplots(figsize=(12, 5))

    se = backtest_result['strategy_equity']
    be = backtest_result['bah_equity']

    ax.plot(se.index, se.values * 100 - 100, label='ML Strategy (Long-Only)', linewidth=1.5)
    ax.plot(be.index, be.values * 100 - 100, label='Buy & Hold', linewidth=1.5, alpha=0.7)
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.4)
    ax.fill_between(se.index, se.values * 100 - 100, 0, alpha=0.08)

    ax.set_title(f'{ticker} — Strategy vs Buy & Hold', fontsize=14)
    ax.set_ylabel('Cumulative Return (%)')
    ax.set_xlabel('Date')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save:
        path = Path(FIGURES_PATH) / f"{ticker}_backtest.png"
        plt.savefig(path, dpi=FIGURE_DPI, bbox_inches='tight')
        logger.info(f"Saved equity curve to {path}")

    plt.close()
