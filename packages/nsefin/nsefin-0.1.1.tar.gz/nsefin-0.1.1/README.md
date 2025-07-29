# nsefin - NSE Historical Data Download Utility

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python library to download publicly available historical candlestick data of stocks, indices, and derivatives from the NSE (National Stock Exchange) India website.

## Features

- Download historical price data for NSE stocks, indices, futures, and options
- Support for multiple timeframes: 1m, 3m, 5m, 10m, 15m, 30m, 1h, 1d, 1w, 1M
- Search functionality for symbols across NSE and NFO exchanges
- Clean, easy-to-use pandas DataFrame output
- Comprehensive symbol master data download

## Installation

```bash
pip install nsefin
```

## Quick Start

```python
from nsefin import search, get_history, download_symbol_master
from datetime import datetime, timedelta
import pandas as pd

# Download symbol master data (required for first use)
download_symbol_master()

# Set date range for historical data
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

# Get historical data for a stock
data = get_history(
    symbol='RELIANCE',
    exchange='NSE',
    start=start_date,
    end=end_date,
    interval='1d'
)

print(data.head())
```

## Usage Examples

### 1. Search for Symbols

```python
# Search for symbols containing 'BANK'
bank_symbols = search('BANK', exchange='NSE', match=False)
print(bank_symbols)

# Exact match for a symbol
reliance = search('RELIANCE', exchange='NSE', match=True)
print(reliance)
```

### 2. Download Stock Data

```python
# Daily data for the last 30 days
stock_data = get_history(
    symbol='TCS',
    exchange='NSE',
    start=start_date,
    end=end_date,
    interval='1d'
)

# Intraday 5-minute data
intraday_data = get_history(
    symbol='INFY',
    exchange='NSE',
    start=start_date,
    end=end_date,
    interval='5m'
)
```

### 3. Download Index Data

```python
# Nifty 50 daily data
nifty_data = get_history(
    symbol='NIFTY',
    exchange='NSE',
    start=start_date,
    end=end_date,
    interval='1d'
)

# Bank Nifty hourly data
banknifty_data = get_history(
    symbol='NIFTY BANK',
    exchange='NSE',
    start=start_date,
    end=end_date,
    interval='1h'
)
```

### 4. Download Futures and Options Data

```python
# Futures data
futures_data = get_history(
    symbol='RELIANCE25APRFUT',
    exchange='NFO',
    start=start_date,
    end=end_date,
    interval='1h'
)

# Options data
options_data = get_history(
    symbol='NIFTY25APR18000CE',
    exchange='NFO',
    start=start_date,
    end=end_date,
    interval='5m'
)