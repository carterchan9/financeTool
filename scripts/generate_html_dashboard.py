#!/usr/bin/env python3
"""
Generate HTML Dashboard for FinanceTool Results
================================================
Creates an HTML dashboard displaying all Phase 1 results.

Usage:
    python scripts/generate_html_dashboard.py

Output:
    dashboards/results_dashboard.html - Open in any web browser
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

FIGURES_DIR = PROJECT_ROOT / "docs" / "figures"
DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT = PROJECT_ROOT / "dashboards" / "results_dashboard.html"

# Relative path from dashboards/ to docs/figures/
IMG_BASE = "../docs/figures"

TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META",
    "TSLA", "SPY", "QQQ", "GLD", "TLT", "BTC-USD",
]

CHART_TYPES = [
    ("price_history",    "Price History"),
    ("features",         "Technical Indicators"),
    ("predictions",      "Predictions"),
    ("backtest",         "Backtest vs Buy & Hold"),
    ("accuracy_timeline","Accuracy Over Time"),
    ("confusion_matrix", "Confusion Matrix"),
]


def load_summary_stats() -> list[dict]:
    """Load processed data stats for each ticker."""
    rows = []
    for ticker in TICKERS:
        csv = DATA_DIR / f"{ticker}_processed.csv"
        if not csv.exists():
            continue
        df = pd.read_csv(csv, index_col=0, parse_dates=True)
        if "target" not in df.columns:
            continue
        from src.config import TEST_SPLIT_DATE
        train = df[df.index < TEST_SPLIT_DATE]
        test = df[df.index >= TEST_SPLIT_DATE]
        rows.append({
            "ticker": ticker,
            "n_train": len(train),
            "n_test": len(test),
            "features": len(df.columns) - 1,
            "target_balance": f"{df['target'].mean()*100:.0f}% up",
        })
    return rows


def img_tag(ticker: str, chart: str) -> str:
    fname = f"{ticker}_{chart}.png"
    path = FIGURES_DIR / fname
    if not path.exists():
        return f'<div class="no-chart">No chart: {fname}</div>'
    return (
        f'<figure>'
        f'<img src="{IMG_BASE}/{fname}" alt="{ticker} {chart}" loading="lazy">'
        f'</figure>'
    )


def build_html(stats: list[dict]) -> str:
    stats_by_ticker = {r["ticker"]: r for r in stats}

    ticker_tabs = "\n".join(
        f'<button class="tab-btn" onclick="showTicker(\'{t}\')" id="btn-{t}">{t}</button>'
        for t in TICKERS
    )

    ticker_sections = ""
    for ticker in TICKERS:
        s = stats_by_ticker.get(ticker, {})
        charts_html = "\n".join(
            f'<div class="chart-block">'
            f'<h3>{label}</h3>'
            f'{img_tag(ticker, key)}'
            f'</div>'
            for key, label in CHART_TYPES
        )
        info = (
            f'<span>{s.get("n_train","—")} train days</span>'
            f'<span>{s.get("n_test","—")} test days</span>'
            f'<span>{s.get("features","—")} features</span>'
            f'<span>{s.get("target_balance","—")}</span>'
        ) if s else ""

        ticker_sections += f"""
        <section class="ticker-section" id="section-{ticker}" style="display:none">
            <div class="ticker-header">
                <h2>{ticker}</h2>
                <div class="ticker-stats">{info}</div>
            </div>
            <div class="charts-grid">{charts_html}</div>
        </section>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Finance ML Lab — Phase 1 Results</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #0f1117; color: #e2e8f0; min-height: 100vh; }}

  header {{ background: #1a1d2e; border-bottom: 1px solid #2d3748;
            padding: 18px 32px; display: flex; align-items: center; gap: 16px; }}
  header h1 {{ font-size: 1.4rem; font-weight: 700; color: #63b3ed; }}
  header span {{ color: #718096; font-size: 0.85rem; }}

  .tab-bar {{ background: #1a1d2e; padding: 12px 32px; display: flex;
              flex-wrap: wrap; gap: 8px; border-bottom: 1px solid #2d3748; position: sticky; top: 0; z-index: 10; }}
  .tab-btn {{ background: #2d3748; border: none; color: #a0aec0; padding: 6px 16px;
              border-radius: 6px; cursor: pointer; font-size: 0.85rem; transition: all .15s; }}
  .tab-btn:hover {{ background: #4a5568; color: #e2e8f0; }}
  .tab-btn.active {{ background: #3182ce; color: white; }}

  .ticker-header {{ padding: 24px 32px 0; display: flex; align-items: baseline; gap: 24px; flex-wrap: wrap; }}
  .ticker-header h2 {{ font-size: 1.8rem; font-weight: 700; color: #63b3ed; }}
  .ticker-stats {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .ticker-stats span {{ background: #2d3748; padding: 4px 12px; border-radius: 20px;
                        font-size: 0.8rem; color: #a0aec0; }}

  .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(540px, 1fr));
                  gap: 20px; padding: 20px 32px 40px; }}
  .chart-block h3 {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: .08em;
                     color: #718096; margin-bottom: 8px; }}
  .chart-block img {{ width: 100%; border-radius: 8px; border: 1px solid #2d3748; display: block; }}
  .no-chart {{ color: #4a5568; font-size: 0.8rem; padding: 12px; border: 1px dashed #2d3748; border-radius: 8px; }}

  .model-comparison {{ padding: 20px 32px 40px; }}
  .model-comparison h2 {{ font-size: 1.2rem; color: #63b3ed; margin-bottom: 16px; }}
  .model-comparison img {{ max-width: 860px; width: 100%; border-radius: 8px; border: 1px solid #2d3748; }}
</style>
</head>
<body>

<header>
  <h1>Finance ML Lab — Phase 1</h1>
  <span>Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} &nbsp;·&nbsp; {len(TICKERS)} assets &nbsp;·&nbsp; 10 features</span>
</header>

<div class="tab-bar">
  {ticker_tabs}
  <button class="tab-btn" onclick="showTicker('__comparison__')" id="btn-__comparison__">All Tickers</button>
</div>

{ticker_sections}

<section class="model-comparison" id="section-__comparison__" style="display:none">
  <h2>Model Comparison — All Tickers</h2>
  <img src="{IMG_BASE}/model_comparison.png" alt="Model comparison">
</section>

<script>
  function showTicker(id) {{
    document.querySelectorAll('.ticker-section, .model-comparison').forEach(s => s.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    const section = document.getElementById('section-' + id);
    if (section) section.style.display = '';
    const btn = document.getElementById('btn-' + id);
    if (btn) btn.classList.add('active');
  }}
  // Show first ticker on load
  showTicker('{TICKERS[0]}');
</script>
</body>
</html>
"""


def main():
    print("Loading data stats...")
    stats = load_summary_stats()

    print("Building dashboard...")
    html = build_html(stats)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html)
    print(f"Saved to {OUTPUT}")
    print(f"Size: {OUTPUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
