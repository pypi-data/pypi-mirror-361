"""
NSE Finance - A Python library for NSE India data access
"""

from .api import NSE

__version__ = "0.1.1"
__author__ = "Vinod Bhadala"
__email__ = "vinodbhadala@gmail.com"

# For backward compatibility, create module-level functions
def get_nse_instance():
    """Get a new NSE instance."""
    return NSE()

# Renamed functions with better descriptions
def search_symbols(symbol, exchange='NSE', exact_match=False):
    """
    Search for stock/index symbols in NSE/NFO exchanges.

    Args:
        symbol (str): Symbol name or pattern to search for
        exchange (str): Exchange ('NSE' or 'NFO')
        exact_match (bool): True for exact match, False for partial search

    Returns:
        pandas.DataFrame: Matching symbols data
    """
    nse = NSE()
    return nse.search_symbols(symbol, exchange, exact_match)

def get_price_history(symbol, exchange='NSE', start_date=None, end_date=None, interval='1d'):
    """
    Get historical OHLCV price data for a stock or index.

    Args:
        symbol (str): Symbol name
        exchange (str): Exchange ('NSE' or 'NFO')
        start_date (datetime): Start date
        end_date (datetime): End date
        interval (str): Time interval ('1m', '5m', '1h', '1d', etc.)

    Returns:
        pandas.DataFrame: Historical OHLCV data
    """
    nse = NSE()
    return nse.get_price_history(symbol, exchange, start_date, end_date, interval)

def get_current_price(symbol):
    """
    Get current price information for a stock symbol.

    Args:
        symbol (str): Stock symbol

    Returns:
        dict: Current price data including LTP, change, OHLC, etc.
    """
    nse = NSE()
    return nse.get_price_info(symbol)

def get_option_chain_data(symbol, is_index=False):
    """
    Get option chain data for a stock or index.

    Args:
        symbol (str): Symbol name
        is_index (bool): True if symbol is an index

    Returns:
        pandas.DataFrame: Option chain data
    """
    nse = NSE()
    return nse.get_option_chain(symbol, is_index)

def get_pre_market_data(category='All'):
    """
    Get pre-market trading data.

    Args:
        category (str): Market category

    Returns:
        pandas.DataFrame: Pre-market data
    """
    nse = NSE()
    return nse.get_pre_market_info(category)

# Backward compatibility aliases
search = search_symbols  # Keep old function name
get_history = get_price_history  # Keep old function name
get_price_info = get_current_price  # Keep old function name

# Expose main class and functions
__all__ = [
    'NSE', 
    'search_symbols', 'get_price_history', 'get_current_price',
    'get_option_chain_data', 'get_pre_market_data', 'get_nse_instance',
    # Backward compatibility
    'search', 'get_history', 'get_price_info'
]