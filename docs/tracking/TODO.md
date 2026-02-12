# TODO & Task Tracking

Quick reference for immediate next steps and ongoing tasks.

---

## Immediate Next Steps (Phase 0)

### Setup Tasks
- [ ] Create Python virtual environment
- [ ] Install dependencies from requirements.txt
- [ ] Initialize git repository
- [ ] Test basic imports (pandas, sklearn, yfinance)

### Implementation Tasks
- [ ] Create data collection script (`src/data/collect_data.py`)
- [ ] Select target stocks (recommendation: AAPL, MSFT, SPY)
- [ ] Implement feature engineering (`src/features/engineer_features.py`)
- [ ] Create training script for Logistic Regression
- [ ] Create training script for Random Forest
- [ ] Build visualization notebook
- [ ] Compare model performances

### Documentation Tasks
- [ ] Update PROJECT_STATUS.md with progress
- [ ] Update FEATURES.md as features are completed
- [ ] Log decisions in CHAT_CONTEXT.md
- [ ] Update CHANGELOG.md

---

## Phase 0 Detailed Checklist

### 1. Environment Setup
- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] Git repository initialized
- [ ] .env file created from .env.example
- [ ] Basic import test passed

### 2. Data Collection
- [ ] `src/data/collect_data.py` created
- [ ] Function to fetch data from yfinance
- [ ] Data validation implemented
- [ ] Error handling for failed downloads
- [ ] Data saved to `data/raw/`
- [ ] Test with 3 stocks successfully

### 3. Feature Engineering
- [ ] `src/features/engineer_features.py` created
- [ ] Daily returns calculation
- [ ] Moving averages (5-day, 20-day)
- [ ] Volatility (rolling std)
- [ ] Target variable (next-day direction)
- [ ] Handle missing values
- [ ] Save processed data to `data/processed/`

### 4. Model Training
- [ ] `src/models/train_logistic.py` created
- [ ] `src/models/train_random_forest.py` created
- [ ] Train/test split implemented
- [ ] Models trained successfully
- [ ] Models saved to `models/`
- [ ] Evaluation metrics calculated

### 5. Visualization
- [ ] `notebooks/01_data_exploration.ipynb` created
- [ ] Price history plots
- [ ] Feature distributions
- [ ] Correlation matrix
- [ ] Predictions vs actuals
- [ ] Model comparison charts

### 6. Testing
- [ ] `tests/test_data_collection.py` created
- [ ] `tests/test_feature_engineering.py` created
- [ ] `tests/test_models.py` created
- [ ] All tests passing

---

## Future Phase Tasks

### Phase 1 (Weeks 4-8)
- [ ] Expand to 10+ stocks
- [ ] Implement RSI indicator
- [ ] Implement MACD indicator
- [ ] Implement Bollinger Bands
- [ ] Create backtesting engine
- [ ] Calculate Sharpe ratio
- [ ] Generate performance reports

### Phase 2 (Weeks 9-16)
- [ ] Implement LSTM model
- [ ] Implement GRU model
- [ ] Set up MLflow for experiment tracking
- [ ] Hyperparameter tuning with Optuna
- [ ] Model comparison framework

### Phase 3 (Weeks 17-24)
- [ ] News data collection
- [ ] Sentiment analysis implementation
- [ ] FinBERT integration
- [ ] Multimodal model

### Phase 4 (Weeks 25-32)
- [ ] Portfolio optimization
- [ ] Risk metrics (VaR, volatility)
- [ ] RL agent (optional)

### Phase 5 (Weeks 33-40)
- [ ] FastAPI implementation
- [ ] Streamlit dashboard
- [ ] Docker containerization
- [ ] Cloud deployment

---

## Known Issues & Blockers

### Current Blockers
- None currently

### Known Issues
- None currently

### Tech Debt
- None currently

---

## Ideas & Improvements

### Feature Ideas
- Add volume-based indicators
- Include sector/industry data
- Add macroeconomic indicators
- Implement attention mechanisms

### Infrastructure Ideas
- Set up automated testing with GitHub Actions
- Add data quality monitoring
- Implement feature store
- Add model registry

### Learning Goals
- Deep dive into LSTM internals
- Master Optuna for hyperparameter tuning
- Learn MLflow best practices
- Understand portfolio theory deeply

---

## Questions to Research

- [ ] What are the best hyperparameters for Random Forest in financial data?
- [ ] How to handle imbalanced classes in stock prediction?
- [ ] Best practices for time series cross-validation?
- [ ] How to incorporate transaction costs realistically?

---

## Completed Tasks

### 2026-02-12
- [x] Created project structure
- [x] Created all documentation files
- [x] Set up .gitignore
- [x] Created requirements.txt
- [x] Created config.yaml
- [x] Created .env.example

---

**Last Updated**: 2026-02-12

**Note**: Keep this file updated as you progress. Move completed tasks to the "Completed Tasks" section with dates.
