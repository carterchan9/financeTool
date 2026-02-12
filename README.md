# Finance ML Project

A comprehensive machine learning platform for financial market prediction, portfolio optimization, and risk analysis.

## 🎯 Project Vision

This project aims to build a production-ready finance ML platform that demonstrates:
- **Machine Learning**: From classical models to deep learning
- **Financial Engineering**: Technical analysis, portfolio theory, risk management
- **Data Engineering**: ETL pipelines, feature engineering, data quality
- **MLOps**: Model deployment, monitoring, CI/CD
- **Cloud Infrastructure**: Scalable, production-ready deployment

## 🚀 Current Status

**Phase**: Phase 0 - MVP Setup
**Progress**: 0%
**Last Updated**: 2026-02-12

See [docs/tracking/PROJECT_STATUS.md](docs/tracking/PROJECT_STATUS.md) for detailed progress tracking.

## 📋 Quick Links

- **[Project Roadmap](docs/PROJECT_ROADMAP.md)** - 12-18 month development plan
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Quick reference guide
- **[Setup Guide](docs/guides/SETUP_GUIDE.md)** - Installation and configuration
- **[Run Guide](docs/guides/RUN_GUIDE.md)** - How to run different components
- **[Project Status](docs/tracking/PROJECT_STATUS.md)** - Current progress and metrics
- **[Features](docs/tracking/FEATURES.md)** - Implemented and planned features
- **[TODO](docs/tracking/TODO.md)** - Task checklist
- **[All Documentation](docs/)** - Complete docs directory

## 🏗️ Project Structure

```
financeTool/
├── data/                 # Data storage
│   ├── raw/             # Original data
│   ├── processed/       # Processed features
│   └── external/        # Third-party data
├── notebooks/           # Jupyter notebooks
├── src/                 # Source code
│   ├── data/           # Data collection
│   ├── features/       # Feature engineering
│   ├── models/         # ML models
│   ├── backtesting/    # Backtesting engine
│   ├── api/            # API endpoints
│   └── utils/          # Utilities
├── tests/              # Test suite
├── configs/            # Configuration files
├── dashboards/         # Web dashboards
├── docs/               # Documentation
├── models/             # Saved models
└── logs/               # Application logs
```

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.9+** - Primary language
- **pandas & numpy** - Data manipulation
- **scikit-learn** - Classical ML
- **PyTorch/TensorFlow** - Deep learning
- **yfinance** - Market data

### Advanced Tools (Later Phases)
- **Transformers** - NLP and sentiment analysis
- **FastAPI** - REST API
- **Streamlit** - Interactive dashboards
- **MLflow** - Experiment tracking
- **Docker** - Containerization
- **AWS/GCP** - Cloud deployment

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Virtual environment (venv or conda)

### Quick Start

```bash
# Clone or navigate to project
cd /Users/carterchan/Documents/self-projects/financeTool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pandas; import numpy; import sklearn; print('Setup successful!')"
```

See [docs/guides/SETUP_GUIDE.md](docs/guides/SETUP_GUIDE.md) for detailed installation instructions.

## 🎓 Learning Path

This project is designed as a learning journey through:

1. **Phase 0** (Weeks 1-3): Basic ML and data handling
2. **Phase 1** (Weeks 4-8): Financial engineering and backtesting
3. **Phase 2** (Weeks 9-16): Deep learning for time series
4. **Phase 3** (Weeks 17-24): NLP and alternative data
5. **Phase 4** (Weeks 25-32): Portfolio optimization and risk
6. **Phase 5** (Weeks 33-40): Cloud deployment and MLOps
7. **Phase 6+** (Months 12+): Continuous expansion

## 🎯 Current Phase: Phase 0 - MVP

### Goals
- Collect historical stock data for 1-3 assets
- Compute basic features (returns, moving averages, volatility)
- Train simple models (Logistic Regression, Random Forest)
- Visualize predictions vs actuals

### Next Steps
1. Install dependencies
2. Select target stocks (e.g., AAPL, MSFT, SPY)
3. Create data collection script
4. Implement feature engineering
5. Train baseline models

See [docs/PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md) for complete phase details.

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_data_collection.py -v
```

## 📊 Key Features (Planned)

### Phase 0-1
- ✅ Historical data collection
- ✅ Basic feature engineering
- ✅ Classical ML models
- ✅ Simple backtesting

### Phase 2-3
- 🚧 LSTM/GRU models
- 🚧 Sentiment analysis
- 🚧 Multimodal predictions

### Phase 4-5
- ⏸️ Portfolio optimization
- ⏸️ Risk management
- ⏸️ REST API
- ⏸️ Cloud deployment

See [docs/tracking/FEATURES.md](docs/tracking/FEATURES.md) for complete feature tracking.

## 📈 Usage Examples

### Collect Stock Data
```bash
python src/data/collect_data.py --symbols AAPL MSFT SPY --start 2020-01-01
```

### Train Model
```bash
python src/models/train_random_forest.py --data data/processed/AAPL_features.csv
```

### Run Backtest
```bash
python src/backtesting/run_backtest.py --strategy threshold --model models/rf_model.pkl
```

See [RUN_GUIDE.md](RUN_GUIDE.md) for detailed usage instructions.

## 📝 Documentation

- **[Setup Guide](SETUP_GUIDE.md)** - Installation and environment setup
- **[Run Guide](RUN_GUIDE.md)** - How to run all components
- **[Project Roadmap](PROJECT_ROADMAP.md)** - Long-term development plan
- **[Features](FEATURES.md)** - Feature tracking and status
- **[Chat Context](CHAT_CONTEXT.md)** - Development decisions log
- **[Project Status](PROJECT_STATUS.md)** - Current progress metrics

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are welcome!

### Development Workflow
1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit for review

## 📄 License

This project is for educational purposes.

## 🎯 Goals & Success Metrics

### Technical Goals
- Build end-to-end ML pipeline
- Implement multiple model architectures
- Deploy production-ready API
- Achieve >55% directional accuracy

### Learning Goals
- Master time series ML
- Understand financial engineering
- Gain MLOps experience
- Build cloud-native applications

### Career Goals
- Portfolio showcase piece
- Demonstrate full-stack ML skills
- Show continuous learning
- Prove production readiness

## 📞 Contact & Support

- Check [CHAT_CONTEXT.md](CHAT_CONTEXT.md) for past discussions
- Review [SETUP_GUIDE.md](SETUP_GUIDE.md) for troubleshooting
- See [RUN_GUIDE.md](RUN_GUIDE.md) for usage help

## 🔮 Future Expansion Ideas

- Cryptocurrency prediction
- Real-time streaming data
- Reinforcement learning traders
- Explainable AI
- Multi-timeframe analysis
- Macroeconomic indicators
- Automated reporting
- Mobile app interface

---

**Start your journey**: Follow the [Setup Guide](SETUP_GUIDE.md) and begin Phase 0!

**Last Updated**: 2026-02-12
