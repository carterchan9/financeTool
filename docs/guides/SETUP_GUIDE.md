# Setup Guide

Complete guide to setting up the Finance ML project on your local machine.

---

## Prerequisites

### Required Software
- **Python**: 3.9 or higher
- **pip**: Python package manager
- **git**: Version control
- **IDE**: VS Code, PyCharm, or Jupyter Lab (recommended)

### Optional Software
- **Docker**: For containerization (Phase 5+)
- **Cloud CLI**: AWS CLI, gcloud, or Azure CLI (Phase 5+)

---

## Installation Steps

### 1. Clone the Repository

```bash
cd /Users/carterchan/Documents/self-projects/financeTool
```

If using git:
```bash
git init
git add .
git commit -m "Initial project setup"
```

### 2. Create Virtual Environment

**Using venv (recommended):**
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

**Using conda:**
```bash
conda create -n finance-ml python=3.9
conda activate finance-ml
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import pandas; import numpy; import sklearn; print('Setup successful!')"
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Keys (add as needed)
ALPHA_VANTAGE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here

# Data Settings
DATA_DIR=./data
MODELS_DIR=./models

# Model Settings
RANDOM_SEED=42
TEST_SIZE=0.2
```

### Config Files

Configuration files are stored in `configs/` directory:
- `configs/data_config.yaml` - Data collection settings
- `configs/model_config.yaml` - Model hyperparameters
- `configs/backtest_config.yaml` - Backtesting parameters

---

## Project Structure Overview

```
financeTool/
├── data/                 # All data files
│   ├── raw/             # Original downloaded data
│   ├── processed/       # Cleaned and processed data
│   └── external/        # Third-party data
├── notebooks/           # Jupyter notebooks for exploration
├── src/                 # Source code
│   ├── data/           # Data collection and processing
│   ├── features/       # Feature engineering
│   ├── models/         # Model definitions
│   ├── backtesting/    # Backtesting framework
│   ├── api/            # API endpoints
│   └── utils/          # Utility functions
├── tests/              # Test files
├── configs/            # Configuration files
├── dashboards/         # Dashboard applications
├── docs/               # Documentation
├── models/             # Saved model artifacts
└── logs/               # Application logs
```

---

## IDE Setup

### VS Code

**Recommended Extensions:**
- Python (Microsoft)
- Jupyter
- Pylance
- Python Docstring Generator
- GitLens

**Settings (`.vscode/settings.json`):**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true
}
```

### PyCharm

1. Open project directory
2. Configure Python interpreter (File → Settings → Project → Python Interpreter)
3. Select the virtual environment created earlier
4. Enable pytest as test runner

### Jupyter Lab

```bash
pip install jupyterlab
jupyter lab
```

---

## Database Setup (Future Phases)

For Phase 4+ when using databases:

### SQLite (Local Development)
No setup needed - SQLite is file-based

### PostgreSQL (Production)
```bash
# Install PostgreSQL
# Create database
createdb finance_ml_db

# Update .env file
DATABASE_URL=postgresql://user:password@localhost:5432/finance_ml_db
```

---

## Troubleshooting

### Common Issues

**Issue**: `ImportError: No module named 'pandas'`
**Solution**: Make sure virtual environment is activated and dependencies are installed

**Issue**: `yfinance` download fails
**Solution**: Check internet connection, try updating yfinance: `pip install --upgrade yfinance`

**Issue**: Jupyter kernel not found
**Solution**: Install ipykernel in virtual environment:
```bash
pip install ipykernel
python -m ipykernel install --user --name=finance-ml
```

**Issue**: Permission denied errors
**Solution**: Check file permissions, ensure you're not running as root

---

## Testing the Setup

Run the test suite to verify everything is working:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_data_collection.py
```

---

## Next Steps

After setup is complete:
1. Review [RUN_GUIDE.md](RUN_GUIDE.md) for usage instructions
2. Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for current phase
3. Start with Phase 0 notebooks in `notebooks/`
4. Follow [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) for development path

---

## Getting Help

- Check [CHAT_CONTEXT.md](CHAT_CONTEXT.md) for past decisions and discussions
- Review [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) for overall project plan
- Create issues for bugs or feature requests

---

**Last Updated**: 2026-02-12
