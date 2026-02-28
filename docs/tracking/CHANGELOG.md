# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Random Forest + XGBoost model comparison
- test_features.py and test_backtester.py
- Multi-model per-ticker performance breakdown

---

## [0.2.0] - 2026-02-28

### Added
- `src/backtester.py` — Long-only backtesting engine
  - `run_backtest()`: simulates strategy vs buy-and-hold
  - `compute_backtest_metrics()`: total return, Sharpe ratio, max drawdown, win rate
  - `print_backtest_report()`: formatted per-ticker report
  - `plot_equity_curves()`: equity curve chart saved to docs/figures/
- 5 new technical indicator features in `src/features.py`:
  - `compute_rsi()` — RSI(14)
  - `compute_macd()` — MACD line + signal line (12,26,9)
  - `compute_bollinger_bands()` — price position within bands
  - `compute_volume_features()` — volume ratio vs 20-day average
- Rebuilt `scripts/generate_html_dashboard.py` for Phase 1 (12 tickers, 6 charts each, 20 KB)

### Changed
- `src/config.py`: expanded TICKERS from 2 → 12, added RSI/MACD/BB/Volume params, updated FEATURE_NAMES (5 → 10)
- `main.py`: updated to Phase 1, added backtest step (step 7/8), updated summary report
- `src/features.py`: updated `compute_features()` to call all 4 new indicator functions

### Results
- 12/12 tickers processed successfully
- 72 charts generated
- Strategy outperforms buy-and-hold on: META (+105% vs +75%), TSLA (+23% vs +4%), GOOGL (+35% vs +32%), TLT (-11% vs -33%)

---

## [0.1.0] - 2026-02-12

### Added
- Initial project structure
- Documentation files:
  - PROJECT_ROADMAP.md - 12-18 month development roadmap
  - PROJECT_STATUS.md - Current status tracking
  - CHAT_CONTEXT.md - Development decisions log
  - FEATURES.md - Feature tracking
  - SETUP_GUIDE.md - Installation instructions
  - RUN_GUIDE.md - Usage guide
  - README.md - Project overview
  - CHANGELOG.md - This file
- Project directories:
  - data/ (raw, processed, external)
  - notebooks/
  - src/ (data, features, models, backtesting, api, utils)
  - tests/
  - configs/
  - dashboards/
  - docs/
  - models/
  - logs/
- Configuration files:
  - requirements.txt - Python dependencies
  - .gitignore - Git ignore rules
- Phase 0 marked as "In Progress"

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

---

## Template for Future Entries

## [X.Y.Z] - YYYY-MM-DD

### Added
- New features or files

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in upcoming releases

### Removed
- Features or files that were removed

### Fixed
- Bug fixes

### Security
- Security improvements or vulnerability fixes

---

## Version History

- 0.1.0 (2026-02-12) - Initial project setup

---

**Note**: For detailed phase-by-phase changes, see [PROJECT_STATUS.md](PROJECT_STATUS.md) and [FEATURES.md](FEATURES.md).
