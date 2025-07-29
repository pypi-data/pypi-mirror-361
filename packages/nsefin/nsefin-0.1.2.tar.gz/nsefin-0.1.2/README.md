
# NSE Finance - Python Library for NSE India Data

A comprehensive Python library to access publicly available historical and real-time data from NSE India with a simple, intuitive API.

## Features

- **Historical Data**: Download OHLCV data for stocks, indices, futures, and options
- **Real-time Data**: Access live market data, option chains, and market depth
- **Market Analysis**: Get gainers/losers, most active stocks, and market statistics
- **Corporate Actions**: Access corporate announcements, insider trading, and upcoming results
- **Holiday Calendar**: Check trading and clearing holidays
- **Type Safety**: Built with Pydantic for robust data validation

## Installation

```bash
pip install nsefin
```

## Quick Start - Simple API

The easiest way to use nsefin is with the module-level functions:

```python
import nsefin
from datetime import datetime, timedelta

# Search for symbols (much clearer than just "search")
bank_stocks = nsefin.search_symbols('BANK', exchange='NSE', exact_match=False)
print(bank_stocks.head())

# Get historical price data
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

# Download stock price history
reliance_data = nsefin.get_price_history('RELIANCE', 'NSE', start_date, end_date, '1d')
print(reliance_data.head())

# Get current price information
current_price = nsefin.get_current_price('RELIANCE')
print(f"RELIANCE current price: ₹{current_price['LastTradedPrice']}")

# Check if today is a trading holiday
is_holiday = nsefin.check_trading_holiday()
print(f"Is today a trading holiday? {is_holiday}")

# Get option chain data
option_data = nsefin.get_option_chain_data('BANKNIFTY', is_index=True)
print(option_data.head())

# Get pre-market data
premarket = nsefin.get_pre_market_data('NIFTY 50')
print(premarket.head())
```

## Advanced Usage - Class-based API

For more control and advanced features, use the NSE class directly:

```python
from nsefin import NSE
from datetime import datetime, timedelta

# Initialize NSE instance
nse = NSE()

# All the same functions are available on the class
data = nse.get_price_history('TCS', 'NSE', start_date, end_date, '5m')
symbols = nse.search_symbols('NIFTY', 'NSE', exact_match=False)
```

## Function Reference

### Core Data Functions

- `search_symbols(symbol, exchange, exact_match)` - Search for stock/index symbols
- `get_price_history(symbol, exchange, start, end, interval)` - Get historical OHLCV data
- `get_current_price(symbol)` - Get live price information
- `check_trading_holiday(date_str)` - Check if date is trading holiday

### Market Data Functions

- `get_pre_market_data(category)` - Get pre-market information
- `get_option_chain_data(symbol, is_index)` - Get option chain data
- `get_index_details(category, symbols_only)` - Get index constituent details

### Holiday Functions

- `get_clearing_holidays(list_only)` - Get NSE clearing holidays
- `is_clearing_holiday(date_str)` - Check if date is clearing holiday

### Corporate Actions Functions

- `get_corporate_actions(from_date, to_date, filter)` - Get corporate actions
- `get_corporate_announcements(from_date, to_date)` - Get corporate announcements
- `get_insider_trading(from_date, to_date)` - Get insider trading data
- `get_upcoming_results()` - Get upcoming results calendar

## Backward Compatibility

All original function names are still supported:

```python
# These still work for backward compatibility
result = nsefin.search('BANK', 'NSE', match=False)  # old syntax
data = nsefin.get_history('RELIANCE', 'NSE', start_date, end_date, '1d')  # old syntax
price = nsefin.get_price_info('RELIANCE')  # old syntax
```

## Supported Time Intervals

- `1m`, `3m`, `5m`, `10m`, `15m`, `30m` - Intraday intervals
- `1h` - Hourly data
- `1d` - Daily data  
- `1w` - Weekly data
- `1M` - Monthly data

## Type Safety with Pydantic

The library includes Pydantic models for robust type checking:

```python
from nsefin.models import HistoricalDataRequest, SymbolSearchRequest

# Type-safe requests (optional)
search_req = SymbolSearchRequest(symbol="RELIANCE", exchange="NSE", exact_match=True)
hist_req = HistoricalDataRequest(symbol="TCS", interval="1d")
```

## Examples

### Get Historical Data

```python
import nsefin
from datetime import datetime, timedelta

# Get daily data for last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

data = nsefin.get_price_history('RELIANCE', 'NSE', start_date, end_date, '1d')
print(data.head())
```

### Search for Symbols

```python
# Search for bank stocks
bank_stocks = nsefin.search_symbols('BANK', exchange='NSE', exact_match=False)
print(f"Found {len(bank_stocks)} bank-related symbols")

# Exact match search
reliance = nsefin.search_symbols('RELIANCE', exchange='NSE', exact_match=True)
print(reliance)
```



### Get Option Chain

```python
# Get option chain for BANKNIFTY
option_chain = nsefin.get_option_chain_data('BANKNIFTY', is_index=True)
print(option_chain.head())
```

## Requirements

- Python 3.8+
- pandas
- requests
- numpy
- pydantic

## Disclaimer

This library is meant for educational purposes only. Downloading data from NSE website requires explicit approval from the exchange. Hence, the usage of this utility is for limited purposes only under proper/explicit approvals.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support, please raise an issue on GitHub.
