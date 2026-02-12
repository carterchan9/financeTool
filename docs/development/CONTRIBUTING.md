# Contributing Guidelines

Thank you for your interest in contributing to the Finance ML project!

---

## Development Philosophy

This is primarily a **learning project** with these principles:
- **Learn by doing** - Implement, break, fix, understand
- **Iterate quickly** - MVP first, optimize later
- **Document decisions** - Track why, not just what
- **Test thoroughly** - Build confidence in changes
- **Keep it simple** - Avoid over-engineering

---

## Getting Started

### Prerequisites
1. Complete [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Verify all tests pass: `pytest tests/`
3. Review [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)
4. Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for current phase

### Development Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Install dev dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run tests to verify setup
pytest tests/ -v
```

---

## Development Workflow

### 1. Check Current Phase
- Review [PROJECT_STATUS.md](PROJECT_STATUS.md)
- Identify tasks in current phase
- Check for blockers or dependencies

### 2. Create Feature Branch
```bash
git checkout -b feature/phase-X-feature-name
```

### 3. Implement Changes
- Write code following style guidelines (see below)
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes
```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Check code quality
flake8 src/
black src/ --check
```

### 5. Update Documentation
- Update [FEATURES.md](FEATURES.md) with new features
- Update [PROJECT_STATUS.md](PROJECT_STATUS.md) with progress
- Update [CHANGELOG.md](CHANGELOG.md) with changes
- Add notes to [CHAT_CONTEXT.md](CHAT_CONTEXT.md) if relevant

### 6. Commit Changes
```bash
git add .
git commit -m "feat(phase-X): descriptive commit message"
```

### 7. Push and Review
```bash
git push origin feature/phase-X-feature-name
```

---

## Code Style Guidelines

### Python Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Maximum line length: 88 characters (Black default)
- Use type hints where appropriate

### Code Formatting
```bash
# Format code with Black
black src/

# Check with flake8
flake8 src/

# Sort imports
isort src/
```

### Naming Conventions
- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

### Example
```python
"""Module docstring describing purpose."""

from typing import List, Optional
import pandas as pd

# Constants
DEFAULT_WINDOW = 20
MAX_RETRIES = 3

class StockDataCollector:
    """Class to collect stock market data."""

    def __init__(self, symbols: List[str]) -> None:
        """Initialize collector with stock symbols."""
        self.symbols = symbols
        self._cache = {}

    def fetch_data(
        self,
        start_date: str,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch historical stock data.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with stock data

        Raises:
            ValueError: If date format is invalid
        """
        # Implementation
        pass
```

---

## Testing Guidelines

### Test Structure
- One test file per module: `test_module_name.py`
- Group related tests in classes
- Use descriptive test names

### Test Example
```python
"""Tests for data collection module."""

import pytest
import pandas as pd
from src.data.collect_data import fetch_stock_data


class TestFetchStockData:
    """Tests for fetch_stock_data function."""

    def test_fetch_valid_symbol(self):
        """Test fetching data for valid stock symbol."""
        df = fetch_stock_data("AAPL", "2020-01-01", "2020-12-31")
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "Close" in df.columns

    def test_fetch_invalid_symbol(self):
        """Test that invalid symbol raises ValueError."""
        with pytest.raises(ValueError):
            fetch_stock_data("INVALID", "2020-01-01", "2020-12-31")

    @pytest.mark.parametrize("symbol", ["AAPL", "MSFT", "GOOGL"])
    def test_fetch_multiple_symbols(self, symbol):
        """Test fetching data for multiple symbols."""
        df = fetch_stock_data(symbol, "2020-01-01", "2020-01-31")
        assert not df.empty
```

### Running Tests
```bash
# All tests
pytest tests/

# Specific file
pytest tests/test_data_collection.py

# Specific test
pytest tests/test_data_collection.py::TestFetchStockData::test_fetch_valid_symbol

# With coverage
pytest --cov=src --cov-report=html tests/

# Verbose output
pytest tests/ -v -s
```

---

## Documentation Guidelines

### Code Documentation
- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include type hints
- Document exceptions

### Project Documentation
Update relevant files:
- **FEATURES.md** - Mark features as completed/in-progress
- **PROJECT_STATUS.md** - Update phase progress
- **CHANGELOG.md** - Document all changes
- **CHAT_CONTEXT.md** - Log important decisions

---

## Git Commit Messages

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding/updating tests
- `chore` - Maintenance tasks

### Scopes
- `phase-0` through `phase-6`
- `data` - Data collection/processing
- `features` - Feature engineering
- `models` - Model implementation
- `backtest` - Backtesting
- `api` - API development
- `docs` - Documentation

### Examples
```bash
feat(phase-0): add yfinance data collection script

- Implemented fetch_stock_data function
- Added data validation
- Created tests for data collection

fix(models): correct random forest feature scaling

The feature scaling was not being applied correctly before
model training, causing degraded performance.

docs(setup): update installation instructions for M1 Macs
```

---

## Phase-Specific Guidelines

### Phase 0: MVP
- Focus on getting something working
- Don't over-engineer
- Document learnings
- Create notebooks for exploration

### Phase 1: Multi-Asset
- Maintain code modularity
- Ensure backtesting is reproducible
- Add comprehensive tests

### Phase 2: Deep Learning
- Document model architectures
- Track experiments with MLflow
- Save model checkpoints

### Phase 3: NLP
- Handle API rate limits gracefully
- Cache external data
- Document data sources

### Phase 4: Portfolio
- Validate financial calculations
- Test edge cases thoroughly
- Document assumptions

### Phase 5: Deployment
- Follow cloud best practices
- Implement proper logging
- Add monitoring and alerts

---

## Code Review Checklist

Before submitting changes:
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No sensitive data (API keys, etc.) in code
- [ ] FEATURES.md updated
- [ ] PROJECT_STATUS.md updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages are clear

---

## Getting Help

- Review [CHAT_CONTEXT.md](CHAT_CONTEXT.md) for past decisions
- Check [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) for context
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for setup issues
- See [RUN_GUIDE.md](RUN_GUIDE.md) for usage questions

---

## Questions?

This is a learning project, so questions and experimentation are encouraged!

---

**Last Updated**: 2026-02-12
