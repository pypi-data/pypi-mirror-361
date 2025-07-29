
"""
nfinance - NSE Historical Data Download Utility

A Python library to get publicly available historic candlestick data
of stocks, index, and derivatives from the NSE India website.

Timeframes supported: 1m, 3m, 5m, 10m, 15m, 30m, 1h, 1d, 1w, 1M
"""

__version__ = "1.0.0"
__author__ = "Vinod Bhadala"
__email__ = "vinodbhadala@gmail.com"

from .api import NSE

# Create a module-level instance for direct access
_nse_instance = None

def _get_nse_instance():
    """Get or create the NSE instance."""
    global _nse_instance
    if _nse_instance is None:
        _nse_instance = NSE()
        # Initialize the symbol master data on first access
        print("Initializing NSE Data Client...")
        _nse_instance.download_symbol_master()
    return _nse_instance

# Module-level functions that delegate to the NSE instance
def search(symbol, exchange, match=False):
    """Search for symbols in the specified exchange."""
    return _get_nse_instance().search(symbol, exchange, match)

def get_history(symbol="Nifty 50", exchange="NSE", start=None, end=None, interval='1d'):
    """Get historical data for a symbol."""
    return _get_nse_instance().get_history(symbol, exchange, start, end, interval)

def download_symbol_master():
    """Download NSE and NFO master data."""
    return _get_nse_instance().download_symbol_master()

def search_symbol(symbol, exchange):
    """Search for a symbol in the specified exchange and return the first match."""
    return _get_nse_instance().search_symbol(symbol, exchange)

def pre_market_info(category='All'):
    """Get pre-market information for specified category."""
    return _get_nse_instance().pre_market_info(category)

def get_index_details(category, list_only=False):
    """Get index details for specified category."""
    return _get_nse_instance().get_index_details(category, list_only)

def clearing_holidays(list_only=False):
    """Returns the list of NSE clearing holidays."""
    return _get_nse_instance().clearing_holidays(list_only)

def trading_holidays(list_only=False):
    """Returns the list of NSE trading holidays."""
    return _get_nse_instance().trading_holidays(list_only)

def is_nse_trading_holiday(date_str=None):
    """Return True if the date supplied is a NSE trading holiday, else False."""
    return _get_nse_instance().is_nse_trading_holiday(date_str)

def is_nse_clearing_holiday(date_str=None):
    """Return True if the date supplied is a NSE clearing holiday, else False."""
    return _get_nse_instance().is_nse_clearing_holiday(date_str)

def equity_info(symbol):
    """Extracts the full details of a symbol as seen on NSE website."""
    return _get_nse_instance().equity_info(symbol)

def price_info(symbol):
    """Gets all key price related information for a given stock."""
    return _get_nse_instance().price_info(symbol)

def futures_data(symbol, indices=False):
    """Returns the list of futures instruments for a given stock and its details."""
    return _get_nse_instance().futures_data(symbol, indices)

def get_option_chain(symbol, indices=False):
    """Returns the full option chain table as seen on NSE website for the given stock/index."""
    return _get_nse_instance().get_option_chain(symbol, indices)

def get_52week_high_low(stock=None):
    """Get 52 Week High and Low data."""
    return _get_nse_instance().get_52week_high_low(stock)

def get_corporate_action(from_date_str=None, to_date_str=None, filter=None):
    """Fetch Corporate Action data from NSE."""
    return _get_nse_instance().get_corporate_action(from_date_str, to_date_str, filter)

def get_gainers_losers():
    """Get gainers and losers data."""
    return _get_nse_instance().get_gainers_losers()

def get_equity_full_list(list_only=False):
    """Get list of all equity available to trade in NSE."""
    return _get_nse_instance().get_equity_full_list(list_only)

def get_fno_full_list(list_only=False):
    """Get a dataframe of all listed derivative list with the recent lot size to trade."""
    return _get_nse_instance().get_fno_full_list(list_only)

# Export both the class and the module-level functions
__all__ = ['NSE', 'search', 'get_history', 'download_symbol_master', 'search_symbol', 
           'pre_market_info', 'get_index_details', 'clearing_holidays', 'trading_holidays',
           'is_nse_trading_holiday', 'is_nse_clearing_holiday', 'equity_info', 'price_info',
           'futures_data', 'get_option_chain', 'get_52week_high_low', 'get_corporate_action',
           'get_gainers_losers', 'get_equity_full_list', 'get_fno_full_list']
