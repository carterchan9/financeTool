# Run Guide

This guide explains how to run different components of the Finance ML project.

---

## Quick Start

### Activate Virtual Environment
```bash
cd /Users/carterchan/Documents/self-projects/financeTool
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

---

## Phase 0: MVP Setup

### 1. Data Collection

**Collect historical stock data:**
```bash
python src/data/collect_data.py --symbols AAPL MSFT SPY --start 2020-01-01 --end 2024-12-31
```

**Parameters:**
- `--symbols`: List of stock tickers (space-separated)
- `--start`: Start date (YYYY-MM-DD)
- `--end`: End date (YYYY-MM-DD)
- `--output`: Output directory (default: data/raw/)

**Output:**
- Raw price data saved to `data/raw/SYMBOL_raw.csv`

### 2. Feature Engineering

**Generate features from raw data:**
```bash
python src/features/engineer_features.py --input data/raw/ --output data/processed/
```

**Features generated:**
- Daily returns
- Moving averages (5-day, 20-day)
- Volatility (rolling std)
- Target variable (next-day up/down)

**Output:**
- Processed data saved to `data/processed/SYMBOL_features.csv`

### 3. Train Models

**Train baseline models:**
```bash
# Logistic Regression
python src/models/train_logistic.py --data data/processed/AAPL_features.csv

# Random Forest
python src/models/train_random_forest.py --data data/processed/AAPL_features.csv
```

**Output:**
- Model saved to `models/`
- Training metrics printed to console
- Plots saved to `docs/figures/`

### 4. Run Jupyter Notebooks

**Launch Jupyter Lab:**
```bash
jupyter lab
```

**Available notebooks:**
- `notebooks/01_data_exploration.ipynb` - Explore raw data
- `notebooks/02_feature_engineering.ipynb` - Feature analysis
- `notebooks/03_model_training.ipynb` - Train and compare models
- `notebooks/04_visualization.ipynb` - Create visualizations

---

## Phase 1: Multi-Asset & Backtesting

### Collect Multi-Asset Data
```bash
python src/data/collect_multi_asset.py --symbols AAPL MSFT GOOGL AMZN SPY QQQ --start 2020-01-01
```

### Run Backtesting
```bash
python src/backtesting/run_backtest.py --strategy threshold --model models/random_forest.pkl --data data/processed/
```

**Parameters:**
- `--strategy`: Strategy type (threshold, mean_reversion, momentum)
- `--model`: Path to trained model
- `--initial_capital`: Starting capital (default: 10000)
- `--commission`: Commission per trade (default: 0.001)

**Output:**
- Backtest results saved to `data/backtests/`
- Performance report generated

### Generate Backtest Report
```bash
python src/backtesting/generate_report.py --results data/backtests/latest.json
```

---

## Phase 2: Advanced ML Models

### Train LSTM Model
```bash
python src/models/train_lstm.py \
    --data data/processed/AAPL_features.csv \
    --sequence_length 60 \
    --epochs 100 \
    --batch_size 32
```

### Hyperparameter Tuning
```bash
python src/models/tune_hyperparameters.py \
    --model lstm \
    --data data/processed/ \
    --trials 50
```

**Output:**
- Best hyperparameters saved to `configs/best_params.json`
- Optuna study database saved to `models/optuna.db`

---

## Phase 3: Alternative Data & NLP

### Collect News Data
```bash
python src/data/collect_news.py --symbols AAPL MSFT --days 30
```

### Sentiment Analysis
```bash
python src/features/sentiment_analysis.py \
    --input data/external/news.csv \
    --output data/processed/sentiment.csv \
    --model finbert
```

**Models available:**
- `vader` - VADER sentiment
- `textblob` - TextBlob sentiment
- `finbert` - FinBERT transformer

---

## Phase 4: Portfolio Optimization

### Run Portfolio Optimization
```bash
python src/portfolio/optimize.py \
    --symbols AAPL MSFT GOOGL AMZN \
    --method mean_variance \
    --target_return 0.15
```

**Methods:**
- `mean_variance` - Modern Portfolio Theory
- `risk_parity` - Risk parity allocation
- `max_sharpe` - Maximum Sharpe ratio
- `rl` - Reinforcement Learning agent

### Calculate Risk Metrics
```bash
python src/portfolio/risk_metrics.py --portfolio data/portfolios/latest.json
```

---

## Phase 5: Cloud & Deployment

### Run API Server
```bash
python src/api/main.py --host 0.0.0.0 --port 8000
```

**API Endpoints:**
- `GET /health` - Health check
- `POST /predict` - Get predictions
- `GET /stocks/{symbol}` - Get stock data
- `POST /backtest` - Run backtest

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Run Dashboard
```bash
streamlit run dashboards/app.py
```

**Dashboard features:**
- Real-time predictions
- Portfolio performance
- Risk metrics
- Interactive charts

### Docker Deployment

**Build image:**
```bash
docker build -t finance-ml:latest .
```

**Run container:**
```bash
docker run -p 8000:8000 finance-ml:latest
```

---

## Testing

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Suite
```bash
pytest tests/test_data_collection.py -v
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html
```

---

## Utilities

### Update All Data
```bash
python src/utils/update_all_data.py
```

### Clean Data Directory
```bash
python src/utils/clean_data.py --older_than 30
```

### Export Models
```bash
python src/utils/export_model.py --model models/lstm.h5 --format onnx
```

---

## Logging

Logs are stored in `logs/` directory:
- `logs/app.log` - Application logs
- `logs/training.log` - Model training logs
- `logs/api.log` - API request logs

**View logs:**
```bash
tail -f logs/app.log
```

---

## Common Commands Cheat Sheet

```bash
# Activate environment
source venv/bin/activate

# Collect data
python src/data/collect_data.py --symbols AAPL MSFT SPY

# Train model
python src/models/train_random_forest.py --data data/processed/AAPL_features.csv

# Run backtest
python src/backtesting/run_backtest.py --strategy threshold

# Start API
python src/api/main.py

# Run dashboard
streamlit run dashboards/app.py

# Run tests
pytest tests/

# View logs
tail -f logs/app.log
```

---

## Troubleshooting

### Data Download Issues
```bash
# Clear cache
rm -rf ~/.cache/yfinance/

# Re-download with verbose mode
python src/data/collect_data.py --symbols AAPL --verbose
```

### Model Training Issues
```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Train on CPU only
python src/models/train_lstm.py --device cpu
```

### API Issues
```bash
# Check port availability
lsof -i :8000

# Run on different port
python src/api/main.py --port 8080
```

---

## Performance Optimization

### Enable GPU Acceleration
```bash
# Check CUDA installation
nvidia-smi

# Install GPU version of PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Parallel Processing
```bash
# Use multiple workers for data processing
python src/data/collect_data.py --workers 4

# Parallel backtesting
python src/backtesting/run_backtest.py --parallel --n_jobs 4
```

---

## Next Steps

1. Complete Phase 0 implementation
2. Review results and iterate
3. Move to Phase 1 when ready
4. Keep [PROJECT_STATUS.md](PROJECT_STATUS.md) updated

---

**Last Updated**: 2026-02-12
