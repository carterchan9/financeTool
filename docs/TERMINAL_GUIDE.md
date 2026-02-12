# Terminal Guide - Commands & Workflows

**Purpose**: Complete reference for all terminal commands, workflows, and operations.

**Quick Start**: Jump to [Common Workflows](#common-workflows) for everyday tasks.

---

## 📋 Table of Contents

1. [Setup Commands](#setup-commands)
2. [Running the Pipeline](#running-the-pipeline)
3. [Testing](#testing)
4. [Data Management](#data-management)
5. [Model Operations](#model-operations)
6. [Git Workflows](#git-workflows)
7. [Code Quality](#code-quality)
8. [Common Workflows](#common-workflows)
9. [Troubleshooting Commands](#troubleshooting-commands)

---

## 🚀 Setup Commands

### Initial Project Setup

```bash
# Navigate to project directory
cd /Users/carterchan/Documents/self-projects/financeTool

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pandas, numpy, sklearn, yfinance; print('✅ All packages installed')"
```

### Environment Management

```bash
# Activate environment (do this every session)
source venv/bin/activate

# Deactivate environment
deactivate

# Check installed packages
pip list

# Check specific package version
pip show pandas

# Update a package
pip install --upgrade yfinance

# Freeze current environment
pip freeze > requirements_freeze.txt
```

---

## 🏃 Running the Pipeline

### Production Pipeline (main.py)

```bash
# Run complete pipeline with real data
python main.py

# With Python path (if import errors)
PYTHONPATH=. python main.py

# Run in background and save output
nohup python main.py > output.log 2>&1 &

# Monitor running process
tail -f output.log
```

### Demo Pipeline (main_demo.py)

```bash
# Run with synthetic data (offline mode)
python main_demo.py

# With Python path
PYTHONPATH=. python main_demo.py

# Redirect output to file
python main_demo.py > demo_results.txt 2>&1
```

### Running Individual Modules

```bash
# Test config module
python src/config.py

# Test data loader
PYTHONPATH=. python src/data_loader.py

# Test feature engineering
PYTHONPATH=. python src/features.py

# Test model training
PYTHONPATH=. python src/model.py

# Test evaluation
PYTHONPATH=. python src/evaluation.py

# Test visualization
PYTHONPATH=. python src/visualization.py
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py

# Run specific test function
pytest tests/test_config.py::test_config_imports

# Run with coverage report
pytest --cov=src tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html              # macOS
xdg-open htmlcov/index.html          # Linux

# Run tests with print statements
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -x

# Run tests matching pattern
pytest tests/ -k "config"

# Show slowest tests
pytest tests/ --durations=10
```

### Adding New Tests

```bash
# Create new test file
touch tests/test_features.py

# Run only new tests
pytest tests/test_features.py -v
```

---

## 💾 Data Management

### Viewing Data

```bash
# List downloaded data
ls -lh data/raw/

# View first 10 rows of CSV
head -10 data/raw/AAPL_raw.csv

# Count rows in CSV
wc -l data/raw/AAPL_raw.csv

# View processed data
head -10 data/processed/AAPL_processed.csv

# Check data size
du -sh data/
```

### Cleaning Data

```bash
# Remove raw data (will re-download)
rm data/raw/*.csv

# Remove processed data
rm data/processed/*.csv

# Remove all data
rm -rf data/raw/* data/processed/*

# Remove old data (older than 30 days)
find data/raw -name "*.csv" -mtime +30 -delete
```

### Exploring Data with Python

```bash
# Quick data exploration
python << EOF
import pandas as pd
df = pd.read_csv('data/raw/AAPL_raw.csv', index_col=0, parse_dates=True)
print(df.head())
print(df.describe())
print(f"Shape: {df.shape}")
print(f"Date range: {df.index.min()} to {df.index.max()}")
EOF
```

---

## 🤖 Model Operations

### Viewing Models

```bash
# List saved models
ls -lh models/

# Check model file size
du -sh models/*.pkl

# View model info with Python
python << EOF
import joblib
model = joblib.load('models/AAPL_logistic.pkl')
print(f"Model type: {type(model)}")
print(f"Model params: {model.get_params()}")
EOF
```

### Managing Models

```bash
# Remove all models (will retrain)
rm models/*.pkl

# Remove specific model
rm models/AAPL_logistic.pkl

# Backup models
cp -r models/ models_backup/

# Compare model sizes
ls -lSh models/
```

---

## 📊 Visualization Management

```bash
# List generated figures
ls -lh docs/figures/

# View figure count
ls docs/figures/*.png | wc -l

# Check total size
du -sh docs/figures/

# Open a figure (macOS)
open docs/figures/AAPL_price_history.png

# Open figure (Linux)
xdg-open docs/figures/AAPL_price_history.png

# Remove all figures
rm docs/figures/*.png

# Remove specific figures
rm docs/figures/TEST_*.png
```

---

## 📦 Git Workflows

### Basic Git Operations

```bash
# Check status
git status

# View changes
git diff

# View changes in specific file
git diff src/config.py

# Stage all changes
git add .

# Stage specific file
git add src/features.py

# Commit with message
git commit -m "feat(phase-0): add feature engineering"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

### Viewing History

```bash
# View commit history
git log

# View compact log
git log --oneline

# View last 5 commits
git log --oneline -5

# View commits for specific file
git log --oneline src/config.py

# View changes in last commit
git show

# View specific commit
git show <commit-hash>
```

### Branch Operations

```bash
# Create new branch
git checkout -b feature/phase-1

# Switch branches
git checkout main

# List branches
git branch

# Delete branch
git branch -d feature/old-feature

# Push branch to remote
git push origin feature/phase-1
```

### Undoing Changes

```bash
# Discard changes in file
git checkout -- src/config.py

# Unstage file
git reset HEAD src/config.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# View file from previous commit
git show HEAD:src/config.py
```

---

## ✨ Code Quality

### Formatting

```bash
# Install black formatter
pip install black

# Format all Python files
black src/ tests/ main.py main_demo.py

# Check what would change (dry run)
black --check src/

# Format specific file
black src/features.py
```

### Linting

```bash
# Install flake8
pip install flake8

# Lint all files
flake8 src/ tests/

# Lint with specific rules
flake8 src/ --max-line-length=88

# Lint and show statistics
flake8 src/ --statistics

# Ignore specific errors
flake8 src/ --ignore=E501,W503
```

### Type Checking

```bash
# Install mypy
pip install mypy

# Check types
mypy src/

# Check specific file
mypy src/features.py

# Strict mode
mypy --strict src/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

---

## 🔄 Common Workflows

### Daily Development Workflow

```bash
# 1. Start of day
cd /path/to/financeTool
source venv/bin/activate
git pull origin main

# 2. Make changes
# Edit files...

# 3. Test changes
pytest tests/ -v
python main_demo.py

# 4. Format code
black src/ tests/

# 5. Commit
git add .
git commit -m "feat: description of changes"
git push origin main
```

### Adding a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/new-indicator

# 2. Implement feature
# Edit src/features.py...

# 3. Test feature
PYTHONPATH=. python src/features.py

# 4. Add tests
# Edit tests/test_features.py...
pytest tests/test_features.py -v

# 5. Run all tests
pytest tests/ -v

# 6. Commit and push
git add .
git commit -m "feat(features): add RSI indicator"
git push origin feature/new-indicator
```

### Running Complete Analysis

```bash
# 1. Clean previous results
rm -rf data/processed/* models/* docs/figures/*

# 2. Run pipeline
python main.py 2>&1 | tee pipeline_output.log

# 3. Check results
ls -lh models/
ls -lh docs/figures/
cat logs/main.log

# 4. View a figure
open docs/figures/AAPL_predictions.png
```

### Debugging a Module

```bash
# 1. Run module with debug output
python -v src/features.py

# 2. Use pdb debugger
python -m pdb src/features.py

# 3. Check logs
cat logs/main.log | grep ERROR

# 4. Test specific function
python << EOF
from src.features import compute_returns
import pandas as pd

df = pd.read_csv('data/raw/AAPL_raw.csv', index_col=0, parse_dates=True)
df_with_returns = compute_returns(df)
print(df_with_returns.head())
EOF
```

### Performance Profiling

```bash
# Time the pipeline
time python main_demo.py

# Profile with cProfile
python -m cProfile -s cumtime main_demo.py

# Save profile output
python -m cProfile -o profile.stats main_demo.py

# Analyze profile
python -m pstats profile.stats
# Then in pstats: sort cumtime, stats 10
```

---

## 🐛 Troubleshooting Commands

### Check Python Environment

```bash
# Check Python version
python --version

# Check which Python
which python

# Check installed packages
pip list

# Check for package conflicts
pip check

# Verify virtual environment is active
echo $VIRTUAL_ENV
```

### Diagnose Import Errors

```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Try importing problematic module
python -c "from src.config import TICKERS; print(TICKERS)"

# Check if module exists
ls -la src/config.py

# Run with verbose imports
python -v -c "from src.config import TICKERS"
```

### Fix Common Issues

```bash
# Fix PYTHONPATH issues
export PYTHONPATH=/path/to/financeTool:$PYTHONPATH

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Reset git repo
git reset --hard HEAD
git clean -fd
```

### Check Disk Space

```bash
# Check available space
df -h

# Check project size
du -sh /path/to/financeTool

# Find large files
find . -type f -size +10M -ls

# Check data directory size
du -sh data/
```

### Monitor Resources

```bash
# Monitor CPU/memory during run
top

# Watch specific process
watch -n 1 'ps aux | grep python'

# Check memory usage
ps aux | grep python | awk '{print $4, $11}'
```

---

## 📝 Quick Reference

### Most Used Commands

```bash
# Activate environment
source venv/bin/activate

# Run pipeline
python main.py

# Run demo
python main_demo.py

# Run tests
pytest tests/ -v

# Format code
black src/

# Git status
git status

# Git commit and push
git add . && git commit -m "message" && git push

# Check logs
cat logs/main.log

# List models
ls -lh models/

# Open figure
open docs/figures/AAPL_predictions.png
```

### One-Liners

```bash
# Count lines of code
find src -name "*.py" | xargs wc -l

# Find TODO comments
grep -r "TODO" src/

# Check test coverage percentage
pytest --cov=src tests/ | grep "TOTAL"

# Clean all generated files
rm -rf data/processed/* models/* docs/figures/*.png __pycache__

# Create backup
tar -czf financeTool_backup_$(date +%Y%m%d).tar.gz .
```

---

## 🔗 Environment Variables

### Setting PYTHONPATH

```bash
# Temporary (current session only)
export PYTHONPATH=/path/to/financeTool

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export PYTHONPATH=/path/to/financeTool:$PYTHONPATH' >> ~/.bashrc
source ~/.bashrc

# For this project only (add to venv/bin/activate)
echo 'export PYTHONPATH=/path/to/financeTool' >> venv/bin/activate
```

### Other Useful Variables

```bash
# Disable warnings
export PYTHONWARNINGS="ignore"

# Enable debug mode
export DEBUG=1

# Set log level
export LOG_LEVEL=DEBUG
```

---

## 📚 Additional Resources

### Command Line Tools

```bash
# Install useful tools
pip install ipython        # Better Python REPL
pip install jupyterlab     # Notebook interface
pip install black flake8   # Code quality

# Use IPython for interactive work
ipython

# Launch Jupyter Lab
jupyter lab
```

### Keyboard Shortcuts (Terminal)

- `Ctrl+C` - Stop running process
- `Ctrl+Z` - Suspend process
- `Ctrl+D` - Exit Python/shell
- `Ctrl+L` - Clear screen
- `Ctrl+R` - Search command history
- `↑/↓` - Navigate command history
- `Tab` - Autocomplete

---

**Last Updated**: 2026-02-12

**Pro Tip**: Bookmark this guide and refer to it often! Add your own commonly-used commands below.

---

## Your Custom Commands

```bash
# Add your frequently used commands here:

```
