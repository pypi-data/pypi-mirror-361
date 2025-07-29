# EMR-Py

## Documentation
[Read the docs](https://ezemriv.github.io/EMR-Py/)

---

## Current Implementation Status
- ✅ Logging utilities
- ✅ ML encoders
- ✅ Telegram trading bot
- ✅ Performance decorators
- 🚧 Time series visualization
- 📋 Planned: GCP utilities, trading indicators, backtesting tools

---

## Library Structure (Tentative)

```
src/emrpy/
├── __init__.py
├── py.typed
├── decorators.py           # General utilities (timer, memory profiling)
├── logging/               # Logging configuration utilities
│   ├── __init__.py
│   └── logger_config.py
├── data/               # data utilities
│   ├── __init__.py
│   └── data_loaders.py
├── ml/                    # Machine Learning utilities
│   ├── __init__.py
│   └── encoders.py        # Categorical encoding functions
├── visualization/         # Plotting and visualization functions
│   ├── __init__.py
│   └── timeseries.py     # Time series plotting utilities
├── timeseries/           # Time series analysis tools
│   ├── __init__.py
│   ├── features.py       # Feature engineering
│   └── analysis.py       # Time series analysis functions
├── trading/              # Trading-specific utilities
│   ├── __init__.py
│   ├── indicators.py     # Technical indicators
│   ├── backtesting.py    # Backtesting utilities
│   └── telegrambot.py    # Trading notifications via Telegram
├── gcp/                  # Google Cloud Platform utilities
│   ├── __init__.py
│   ├── bigquery.py       # BigQuery helpers
│   └── storage.py        # Cloud Storage helpers
└── finance/              # Financial data utilities
    ├── __init__.py
    └── data_processing.py # Financial data preprocessing
```
