# Project Structure Overview

Clean, organized directory structure for the Finance ML project.

---

## 📁 Root Directory

```
financeTool/
├── README.md              # Main project overview
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── .env.example          # Environment variables template
├── PROJECT_STRUCTURE.md  # This file
│
├── docs/                 # 📚 All documentation (see below)
├── configs/              # ⚙️ Configuration files
├── src/                  # 🐍 Source code
├── tests/                # 🧪 Test suite
├── notebooks/            # 📓 Jupyter notebooks
├── data/                 # 💾 Data storage
├── models/               # 🤖 Saved models
├── logs/                 # 📋 Application logs
└── dashboards/           # 📊 Dashboard apps (Phase 5)
```

---

## 📚 Documentation Structure (`docs/`)

```
docs/
├── README.md                    # Documentation index
├── PROJECT_ROADMAP.md          # 12-18 month development plan
├── PROJECT_SUMMARY.md          # Quick reference guide
│
├── guides/                     # 📖 How-to guides
│   ├── SETUP_GUIDE.md         # Installation & setup
│   └── RUN_GUIDE.md           # Usage & commands
│
├── tracking/                   # 📊 Progress tracking
│   ├── PROJECT_STATUS.md      # Current progress & metrics
│   ├── FEATURES.md            # Feature tracking by phase
│   ├── TODO.md                # Task checklist
│   ├── CHAT_CONTEXT.md        # Development decisions log
│   └── CHANGELOG.md           # Version history
│
└── development/                # 👨‍💻 Development guidelines
    └── CONTRIBUTING.md        # Code style & workflow
```

---

## 🐍 Source Code Structure (`src/`)

```
src/
├── __init__.py
├── data/                   # Data collection & processing
│   └── __init__.py
├── features/               # Feature engineering
│   └── __init__.py
├── models/                 # ML model definitions
│   └── __init__.py
├── backtesting/            # Backtesting framework
│   └── __init__.py
├── api/                    # API endpoints (Phase 5)
│   └── __init__.py
└── utils/                  # Utility functions
    └── __init__.py
```

---

## 💾 Data Structure (`data/`)

```
data/
├── raw/                    # Original downloaded data
│   └── .gitkeep
├── processed/              # Cleaned & featured data
│   └── .gitkeep
└── external/               # Third-party data sources
    └── .gitkeep
```

---

## ⚙️ Configuration Structure (`configs/`)

```
configs/
├── config.yaml            # Main configuration
└── .gitkeep
```

---

## 🧪 Test Structure (`tests/`)

```
tests/
├── __init__.py
├── test_data_collection.py      (Phase 0)
├── test_feature_engineering.py  (Phase 0)
├── test_models.py                (Phase 0)
├── test_backtesting.py          (Phase 1)
└── ...                          (Future phases)
```

---

## 📓 Notebooks Structure (`notebooks/`)

```
notebooks/
├── 01_data_exploration.ipynb      (Phase 0)
├── 02_feature_engineering.ipynb   (Phase 0)
├── 03_model_training.ipynb        (Phase 0)
├── 04_visualization.ipynb         (Phase 0)
└── ...                            (Future phases)
```

---

## 🤖 Models Structure (`models/`)

```
models/
├── .gitkeep
├── logistic_regression.pkl        (Phase 0)
├── random_forest.pkl              (Phase 0)
├── lstm_model.h5                  (Phase 2)
└── ...                            (Future phases)
```

---

## Quick Navigation

| Need to... | Go to... |
|------------|----------|
| Get started | [docs/guides/SETUP_GUIDE.md](docs/guides/SETUP_GUIDE.md) |
| Run commands | [docs/guides/RUN_GUIDE.md](docs/guides/RUN_GUIDE.md) |
| Check progress | [docs/tracking/PROJECT_STATUS.md](docs/tracking/PROJECT_STATUS.md) |
| See what's next | [docs/tracking/TODO.md](docs/tracking/TODO.md) |
| Understand the plan | [docs/PROJECT_ROADMAP.md](docs/PROJECT_ROADMAP.md) |
| Quick reference | [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) |
| Browse all docs | [docs/README.md](docs/README.md) |

---

## File Organization Principles

### Root Directory
- **Minimal clutter**: Only essential files (README, requirements, configs)
- **Clear purpose**: Each file has obvious purpose
- **Standard structure**: Follows Python project conventions

### Documentation (`docs/`)
- **Categorized**: Guides, tracking, development
- **Easy to find**: Clear naming and structure
- **Well-linked**: Cross-references between docs

### Source Code (`src/`)
- **Modular**: Separated by functionality
- **Importable**: Proper `__init__.py` structure
- **Scalable**: Easy to add new modules

### Data (`data/`)
- **Separated**: Raw, processed, external
- **Ignored**: Data files not in git (see `.gitignore`)
- **Tracked structure**: `.gitkeep` maintains folders

---

**Last Updated**: 2026-02-12
