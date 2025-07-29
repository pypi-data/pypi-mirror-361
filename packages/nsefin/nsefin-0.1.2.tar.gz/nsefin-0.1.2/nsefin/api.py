"""
NSE HISTORICAL DATA DOWNLOAD UTILITY

Description: This utility is Python Library to get publicly available historic candlestick data
of stocks, index, its derivatives from the new NSE india website

Timeframes supported are : 1m, 3m, 5m, 10m, 15m, 30m, 1h, 1d, 1w, 1M.

Disclaimer : This utility is meant for educational purposes only. Downloading data from NSE
website requires explicit approval from the exchange. Hence, the usage of this utility is for
limited purposes only under proper/explicit approvals.

Requirements : Following packages are to be installed (using pip) prior to using this utility
- pandas
- requests
- python 3.8 and above

Available Functions:
==================

Core Data Functions:
- download_symbol_master() : Download NSE and NFO master data
- search(symbol, exchange, match=False) : Search for symbols in NSE/NFO exchanges
- get_history(symbol, exchange, start, end, interval) : Get historical price data
- get_price_info(symbol) : Get current price information for a symbol
- get_equity_info(symbol) : Get complete equity information for a symbol

Market Data Functions:
- get_pre_market_info(category) : Get pre-market information
- get_index_details(category, list_only=False) : Get index details for category
- get_gainers_losers() : Get top gainers and losers data
- get_advance_decline() : Get advance/decline data for indices

Holiday Functions:
- get_clearing_holidays(list_only=False) : Get NSE clearing holidays
- is_clearing_holiday(date_str=None) : Check if date is clearing holiday

Derivatives Functions:
- get_futures_data(symbol, indices=False) : Get futures data for symbol
- get_option_chain(symbol, indices=False) : Get option chain data
- get_live_option_chain(symbol, expiry_date, oi_mode, indices=False) : Get live option chain

Historical Data Functions:
- get_52_week_high_low(stock=None) : Get 52-week high/low data
- get_equity_bhav_copy(trade_date) : Get equity bhav copy for date
- get_fno_bhav_copy(trade_date) : Get F&O bhav copy for date
- get_bhav_copy_with_delivery(trade_date) : Get bhav copy with delivery data
- get_indices_bhav_copy(trade_date) : Get indices bhav copy for date

Corporate Actions Functions:
- get_corporate_actions(from_date, to_date, filter=None) : Get corporate actions
- get_corporate_announcements(from_date, to_date) : Get corporate announcements
- get_insider_trading(from_date, to_date) : Get insider trading data
- get_upcoming_results() : Get upcoming results calendar

Market Analysis Functions:
- get_most_active_by_volume() : Get most active stocks by volume
- get_most_active_by_value() : Get most active stocks by value
- get_most_active_index_calls() : Get most active index calls
- get_most_active_index_puts() : Get most active index puts
- get_most_active_stock_calls() : Get most active stock calls
- get_most_active_stock_puts() : Get most active stock puts
- get_most_active_contracts_by_oi() : Get most active contracts by open interest
- get_most_active_contracts_by_volume() : Get most active contracts by volume
- get_most_active_futures_by_volume() : Get most active futures by volume
- get_most_active_options_by_volume() : Get most active options by volume

Index Analysis Functions:
- get_index_pe_ratio() : Get P/E ratios for indices
- get_index_pb_ratio() : Get P/B ratios for indices
- get_index_dividend_yield() : Get dividend yield for indices
- get_index_historical_data(index, from_date, to_date) : Get historical index data

List Functions:
- get_equity_list(list_only=False) : Get all equity symbols
- get_fno_list(list_only=False) : Get all F&O symbols
- get_etf_list() : Get all ETF symbols

Utility Functions:
- get_market_depth(symbol) : Get market depth for symbol
- get_fii_dii_activity() : Get FII/DII trading activity
"""

import pandas as pd
import time
import json
import requests
from datetime import datetime, timedelta
import re
from io import StringIO, BytesIO
import zipfile
import gzip



class NSE:
    """
    A comprehensive class for NSE data access including historical data, market info, and utilities.

    This class provides methods to:
    - Download NSE and NFO symbol master data
    - Search for symbols in NSE/NFO exchanges
    - Get historical price data for stocks, indices, futures, and options
    - Access live market data, option chains, corporate actions, and more
    - Retrieve various market analysis data and reports

    Attributes:
        session (requests.Session): HTTP session for making requests
        nse_url (str): URL for NSE master data
        nfo_url (str): URL for NFO master data
        historical_url (str): URL for historical data
        nse_data (pandas.DataFrame): Cached NSE symbol data
        nfo_data (pandas.DataFrame): Cached NFO symbol data
        headers (dict): HTTP headers for requests
        cookies (dict): Session cookies
    """

    equity_market_list = ['NIFTY 50', 'NIFTY NEXT 50', 'NIFTY MIDCAP 50', 'NIFTY MIDCAP 100',
                          'NIFTY MIDCAP 150', 'NIFTY SMALLCAP 50', 'NIFTY SMALLCAP 100', 'NIFTY SMALLCAP 250',
                          'NIFTY MIDSMALLCAP 400', 'NIFTY 100', 'NIFTY 200', 'NIFTY AUTO',
                          'NIFTY BANK', 'NIFTY ENERGY', 'NIFTY FINANCIAL SERVICES', 'NIFTY FINANCIAL SERVICES 25/50',
                          'NIFTY FMCG',
                          'NIFTY IT', 'NIFTY MEDIA', 'NIFTY METAL', 'NIFTY PHARMA', 'NIFTY PSU BANK', 'NIFTY REALTY',
                          'NIFTY PRIVATE BANK', 'Securities in F&O', 'Permitted to Trade',
                          'NIFTY DIVIDEND OPPORTUNITIES 50',
                          'NIFTY50 VALUE 20', 'NIFTY100 QUALITY 30', 'NIFTY50 EQUAL WEIGHT', 'NIFTY100 EQUAL WEIGHT',
                          'NIFTY100 LOW VOLATILITY 30', 'NIFTY ALPHA 50', 'NIFTY200 QUALITY 30',
                          'NIFTY ALPHA LOW-VOLATILITY 30',
                          'NIFTY200 MOMENTUM 30', 'NIFTY COMMODITIES', 'NIFTY INDIA CONSUMPTION', 'NIFTY CPSE',
                          'NIFTY INFRASTRUCTURE',
                          'NIFTY MNC', 'NIFTY GROWTH SECTORS 15', 'NIFTY PSE', 'NIFTY SERVICES SECTOR',
                          'NIFTY100 LIQUID 15',
                          'NIFTY MIDCAP LIQUID 15']

    pre_market_list = ['NIFTY 50', 'Nifty Bank', 'Emerge', 'Securities in F&O', 'Others', 'All']

    def __init__(self):
        """Initialize the NSE instance with default configuration."""
        self.session = requests.Session()

        self.headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            'Content-Type': 'application/json',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate'
        }

        self.session.headers.update(self.headers)
        self.nse_url = "https://charting.nseindia.com/Charts/GetEQMasters"
        self.nfo_url = "https://charting.nseindia.com/Charts/GetFOMasters"
        self.historical_url = "https://charting.nseindia.com//Charts/symbolhistoricaldata/"
        self.nse_data = None
        self.nfo_data = None

        # Initialize session with NSE website
        self.session.get("http://nseindia.com", headers=self.headers)
        self.cookies = self.session.cookies.get_dict()

    def _get_symbol_master_data(self, url):
        """
        Download symbol master data from the given URL.

        Args:
            url (str): The URL to download data from

        Returns:
            pandas.DataFrame: DataFrame containing symbol master data
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.text.splitlines()
            columns = ['ScripCode', 'Symbol', 'Name', 'Type']
            return pd.DataFrame([line.split('|') for line in data], columns=columns)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download data from {url}: {e}")
            return pd.DataFrame()

    def download_symbol_master(self):
        """
        Download NSE and NFO master data for search symbol.

        This method downloads the complete symbol master data for both NSE and NFO
        exchanges and caches them for future use.

        Examples:
            >>> nse = NSE()
            >>> nse.download_symbol_master()
        """
        print("Downloading NSE master data...")
        self.nse_data = self._get_symbol_master_data(self.nse_url)
        print("Downloading NFO master data...")
        self.nfo_data = self._get_symbol_master_data(self.nfo_url)
        print("Master data download completed.")

    def search_symbols(self, symbol, exchange, match=False):
        """
        Search for stock/index symbols in the specified exchange.

        Args:
            symbol (str): The symbol or part of the symbol to search for.
            exchange (str): The exchange to search in ('NSE' or 'NFO').
            match (bool): If True, performs an exact match. If False, searches for symbols containing the input.

        Returns:
            pandas.DataFrame: A DataFrame containing all matching symbols.

        Examples:
            >>> nse = NSE()
            >>> nse.download_symbol_master()
            >>> result = nse.search_symbols('RELIANCE', 'NSE', match=True)
            >>> print(result)
        """
        if self.nse_data is None or self.nfo_data is None:
            self.download_symbol_master()

        exchange = exchange.upper()
        if exchange == 'NSE':
            df = self.nse_data
        elif exchange == 'NFO':
            df = self.nfo_data
        else:
            print(f"Invalid exchange '{exchange}'. Please choose 'NSE' or 'NFO'.")
            return pd.DataFrame()

        if df is None or df.empty:
            print(f"No data available for {exchange}.")
            return pd.DataFrame()

        if match:
            result = df[df['Symbol'].str.upper() == symbol.upper()]
        else:
            result = df[df['Symbol'].str.contains(symbol, case=False, na=False)]

        if result.empty:
            print(f"No matching result found for symbol '{symbol}' in {exchange}.")
            return pd.DataFrame()

        return result.reset_index(drop=True)

    def _search_symbol(self, symbol, exchange):
        """
        Search for a symbol in the specified exchange and return the first match.

        Args:
            symbol (str): Symbol to search for
            exchange (str): Exchange to search in ('NSE' or 'NFO')

        Returns:
            pandas.Series or None: First matching symbol data or None if not found
        """
        df = self.nse_data if exchange.upper() == 'NSE' else self.nfo_data
        if df is None or df.empty:
            print(f"Data for {exchange} not available. Please run download_symbol_master() first.")
            return None
        result = df[df['Symbol'].str.contains(symbol, case=False, na=False)]
        if result.empty:
            print(f"No matching result found for symbol '{symbol}' in {exchange}.")
            return None
        return result.iloc[0]


    def get_price_history(self, symbol="Nifty 50", exchange="NSE", start=None, end=None, interval='1d'):
        """
        Get historical price data (OHLCV) for a stock or index symbol.

        Args:
            symbol (str): Symbol name (default: "Nifty 50")
            exchange (str): Exchange name - 'NSE' or 'NFO' (default: "NSE")
            start (datetime): Start date for data (default: None)
            end (datetime): End date for data (default: None)
            interval (str): Time interval - '1m', '3m', '5m', '10m', '15m', '30m', '1h', '1d', '1w', '1M' (default: '1d')

        Returns:
            pandas.DataFrame: Historical OHLCV data with columns [Timestamp, Open, High, Low, Close, Volume]
        """
        if self.nse_data is None or self.nfo_data is None:
            self.download_symbol_master()

        def adjust_timestamp(ts):
            if interval in ['30m', '1h']:
                num = 15
            elif interval in ['10m']:
                num = 5
            else:
                num = int(re.match(r'\d+', interval).group())
            if num == 0:
                return (ts - timedelta(minutes=num)).round('min')
            else:
                return (ts - timedelta(minutes=num)).round((str(num) + 'min'))

        symbol_info = self._search_symbol(symbol, exchange)
        if symbol_info is None:
            return pd.DataFrame()

        interval_xref = {
            '1m': ('1', 'I'), '3m': ('3', 'I'), '5m': ('5', 'I'), '10m': ('5', 'I'),
            '15m': ('15', 'I'), '30m': ('15', 'I'), '1h': ('15', 'I'),
            '1d': ('1', 'D'), '1w': ('1', 'W'), '1M': ('1', 'M')
        }

        time_interval, chart_period = interval_xref.get(interval, ('1', 'D'))

        payload = {
            "exch": "N" if exchange.upper() == "NSE" else "D",
            "instrType": "C" if exchange.upper() == "NSE" else "D",
            "ScripCode": int(symbol_info['ScripCode']),
            "ulScripCode": int(symbol_info['ScripCode']),
            "fromDate": int(start.timestamp()) if start else 0,
            "toDate": int(end.timestamp()) if end else int(time.time()),
            "timeInterval": time_interval,
            "chartPeriod": chart_period,
            "chartStart": 0
        }

        try:
            # Set Cookies
            self.session.get("https://www.nseindia.com", timeout=5)
            response = self.session.post(self.historical_url, data=json.dumps(payload), timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                print("No data received from the Source - NSE.")
                return pd.DataFrame()

            df = pd.DataFrame(data)
            df.columns = ['Status', 'TS', 'Open', 'High', 'Low', 'Close', 'Volume']
            df['TS'] = pd.to_datetime(df['TS'], unit='s', utc=True)
            df['TS'] = df['TS'].dt.tz_localize(None)
            df = df[['TS', 'Open', 'High', 'Low', 'Close', 'Volume']]

            # Apply cutoff time only for intraday intervals
            intraday_intervals = ['1m', '3m', '5m', '15m']
            intraday_consolidate_intervals = ['10m','30m', '1h']
            if interval in intraday_intervals:
                cutoff_time = pd.Timestamp('15:30:00').time()
                df = df[df['TS'].dt.time <= cutoff_time]
                df['Timestamp'] = df['TS'].apply(adjust_timestamp)
                df.drop(columns=['TS'], inplace=True)
                df.set_index('Timestamp', inplace=True, drop=True)
                return df
            if interval in intraday_consolidate_intervals:
                cutoff_time = pd.Timestamp('15:30:00').time()
                df = df[df['TS'].dt.time <= cutoff_time]
                df['Timestamp'] = df['TS'].apply(adjust_timestamp)
                df.drop(columns=['TS'], inplace=True)
                df.set_index('Timestamp', inplace=True, drop=True)
                agg_parm = ''
                if interval == '30m':
                    agg_parm = '30min'
                elif interval == '10m':
                    agg_parm = '10min'
                else:
                    agg_parm = '60min'
                # Get the first timestamp to use as custom origin
                first_ts = df.index.min()
                offset_td = pd.to_timedelta(first_ts.time().strftime('%H:%M:%S'))
                df_aggregated = df.resample(agg_parm, origin='start_day', offset=offset_td).agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                })
                df_aggregated.dropna(inplace=True)
                return df_aggregated

            df.rename(columns={'TS': 'Timestamp'}, inplace=True)
            df.set_index('Timestamp', inplace=True, drop=True)
            return df

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching historical data: {e}")
            return pd.DataFrame()

    def get_pre_market_info(self, category='All'):
        """Get pre-market information for specified category."""
        try:
            pre_market_xref = {"NIFTY 50": "NIFTY", "Nifty Bank": "BANKNIFTY", "Emerge": "SME", "Securities in F&O": "FO",
                               "Others": "OTHERS", "All": "ALL"}

            ref_url = 'https://www.nseindia.com/market-data/pre-open-market-cm-and-emerge-market'
            ref = requests.get(ref_url, headers=self.headers, timeout=10)
            url = f"https://www.nseindia.com/api/market-data-pre-open?key={pre_market_xref[category]}"
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()

            if not response.text.strip():
                print(f"Warning: Empty response from NSE pre-market API for category {category}")
                return pd.DataFrame()

            data = response.json()
            if 'data' not in data:
                print(f"Warning: No pre-market data available for category {category}")
                return pd.DataFrame()

            processed_data = []
            for i in data['data']:
                processed_data.append(i["metadata"])
            df = pd.DataFrame(processed_data)
            df = df.set_index("symbol", drop=True)
            return df
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Warning: Failed to fetch pre-market info for category {category}: {e}")
            return pd.DataFrame()

    def get_index_details(self, category, list_only=False):
        """Get index details for specified category."""
        try:
            category = category.upper().replace('&', '%26').replace(' ', '%20')

            ref_url = f"https://www.nseindia.com/market-data/live-equity-market?symbol={category}"
            ref = requests.get(ref_url, headers=self.headers, timeout=10)
            url = f"https://www.nseindia.com/api/equity-stockIndices?index={category}"
            response = requests.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()

            if not response.text.strip():
                print(f"Warning: Empty response from NSE index details API for category {category}")
                return [] if list_only else pd.DataFrame()

            data = response.json()
            if 'data' not in data:
                print(f"Warning: No index data available for category {category}")
                return [] if list_only else pd.DataFrame()

            df = pd.DataFrame(data['data'])
            df = df.drop(["meta"], axis=1)
            df = df.set_index("symbol", drop=True)
            if list_only:
                symbol_list = sorted(df.index[1:].tolist())
                return symbol_list
            else:
                return df
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Warning: Failed to fetch index details for category {category}: {e}")
            return [] if list_only else pd.DataFrame()


    def get_equity_info(self, symbol):
        """Extracts the full details of a symbol as seen on NSE website."""
        try:
            symbol = symbol.replace(' ', '%20').replace('&', '%26')
            ref_url = 'https://www.nseindia.com/get-quotes/equity?symbol=' + symbol
            ref = requests.get(ref_url, headers=self.headers, timeout=10)

            url = 'https://www.nseindia.com/api/quote-equity?symbol=' + symbol
            response = requests.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()

            if not response.text.strip():
                print(f"Warning: Empty response from NSE equity info API for symbol {symbol}")
                return None

            data = response.json()

            url = 'https://www.nseindia.com/api/quote-equity?symbol=' + symbol + "&section=trade_info"
            trade_response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            trade_response.raise_for_status()

            if not trade_response.text.strip():
                print(f"Warning: Empty response from NSE trade info API for symbol {symbol}")
                trade_data = {}
            else:
                trade_data = trade_response.json()

            data['tradeData'] = trade_data
            return data
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Warning: Failed to fetch equity info for symbol {symbol}: {e}")
            return None

    def get_price_info(self, symbol):
        """Gets all key price related information for a given stock."""
        try:
            symbol = symbol.replace(' ', '%20').replace('&', '%26')
            ref_url = 'https://www.nseindia.com/get-quotes/equity?symbol=' + symbol
            ref = self.session.get(ref_url, headers=self.headers, timeout=10)
            url = 'https://www.nseindia.com/api/quote-equity?symbol=' + symbol

            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()

            if not response.text.strip():
                print(f"Warning: Empty response from NSE price info API for symbol {symbol}")
                return None

            # Clean the response text to handle extra data
            response_text = response.text.strip()

            # Try to find the JSON part if there's extra data
            try:
                # First try normal JSON parsing
                data = response.json()
            except ValueError:
                # If that fails, try to extract JSON from the response
                try:
                    # Look for JSON object start
                    start = response_text.find('{')
                    if start != -1:
                        # Find the matching closing brace
                        brace_count = 0
                        end = start
                        for i, char in enumerate(response_text[start:], start):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end = i + 1
                                    break

                        json_part = response_text[start:end]
                        data = json.loads(json_part)
                    else:
                        print(f"Warning: No valid JSON found in response for symbol {symbol}")
                        return None
                except (ValueError, json.JSONDecodeError) as json_error:
                    print(f"Warning: Failed to parse JSON for symbol {symbol}: {json_error}")
                    return None

            if not data or 'error' in data:
                print(f"Warning: No price data available for symbol {symbol}")
                return None

            if 'priceInfo' not in data:
                print(f"Warning: Price info not available for symbol {symbol}")
                return None

            return {
                "Symbol": symbol,
                "LastTradedPrice": data['priceInfo']['lastPrice'],
                "PreviousClose": data['priceInfo']['previousClose'],
                "Change": data['priceInfo']['change'],
                "PercentChange": data['priceInfo']['pChange'],
                "Open": data['priceInfo']['open'],
                "Close": data['priceInfo']['close'],
                "High": data['priceInfo']['intraDayHighLow']['max'],
                "Low": data['priceInfo']['intraDayHighLow']['min'],
                "VWAP": data['priceInfo']['vwap'],
                "UpperCircuit": data['priceInfo']['upperCP'],
                "LowerCircuit": data['priceInfo']['lowerCP'],
            }
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Warning: Failed to fetch price info for symbol {symbol}: {e}")
            return None

    def get_futures_data(self, symbol, indices=False):
        """Returns the list of futures instruments for a given stock and its details."""
        try:
            symbol = symbol.replace(' ', '%20').replace('&', '%26')
            ref_url = 'https://www.nseindia.com/get-quotes/derivatives?symbol=' + symbol
            ref = requests.get(ref_url, headers=self.headers, timeout=10)
            url = 'https://www.nseindia.com/api/quote-derivative?symbol=' + symbol
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()

            if not response.text.strip():
                print(f"Warning: Empty response from NSE futures data API for symbol {symbol}")
                return pd.DataFrame()

            data = response.json()
            if 'stocks' not in data:
                print(f"Warning: No futures data available for symbol {symbol}")
                return pd.DataFrame()

            lst = []
            for i in data["stocks"]:
                if i["metadata"]["instrumentType"] == ("Index Futures" if indices else "Stock Futures"):
                    lst.append(i["metadata"])
            df = pd.DataFrame(lst)
            if not df.empty:
                df = df.set_index("identifier", drop=True)
            return df
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Warning: Failed to fetch futures data for symbol {symbol}: {e}")
            return pd.DataFrame()

    def get_option_chain(self, symbol, indices=False):
        """Returns the full option chain table as seen on NSE website for the given stock/index."""
        try:
            symbol = symbol.replace(' ', '%20').replace('&', '%26')
            if not indices:
                ref_url = 'https://www.nseindia.com/get-quotes/derivatives?symbol=' + symbol
                ref = requests.get(ref_url, headers=self.headers, timeout=10)
                url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + symbol
            else:
                ref_url = 'https://www.nseindia.com/get-quotes/derivatives?symbol=' + symbol
                ref = requests.get(ref_url, headers=self.headers, timeout=10)
                url = 'https://www.nseindia.com/api/option-chain-indices?symbol=' + symbol

            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict(), timeout=10)
            response.raise_for_status()

            if not response.text.strip():
                print(f"Warning: Empty response from NSE option chain API for symbol {symbol}")
                return pd.DataFrame()

            response_data = response.json()
            if 'records' not in response_data:
                print(f"Warning: No option chain data available for symbol {symbol}")
                return pd.DataFrame()

            data = response_data["records"]

            my_df = []
            for i in data["data"]:
                for k, v in i.items():
                    if k == "CE" or k == "PE":
                        info = v
                        info["instrumentType"] = k
                        info["timestamp"] = data["timestamp"]
                        my_df.append(info)

            df = pd.DataFrame(my_df)
            if not df.empty:
                df = df.set_index("identifier", drop=True)
            return df
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            print(f"Warning: Failed to fetch option chain for symbol {symbol}: {e}")
            return pd.DataFrame()

    def get_live_option_chain(self, symbol: str, expiry_date: str = None, oi_mode: str = "full", indices=False):
        """Get live NSE option chain."""
        try:
            symbol = symbol.replace(' ', '%20').replace('&', '%26')
            ref_url = 'https://www.nseindia.com/option-chain'
            ref = requests.get(ref_url, headers=self.headers)
            if not indices:
                url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + symbol
            else:
                url = 'https://www.nseindia.com/api/option-chain-indices?symbol=' + symbol

            payload = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict()).json()

            if expiry_date:
                exp_date = pd.to_datetime(expiry_date, format='%d-%m-%Y')
                expiry_date = exp_date.strftime('%d-%b-%Y')

            if oi_mode == 'compact':
                col_names = ['Fetch_Time', 'Symbol', 'Expiry_Date', 'CALLS_OI', 'CALLS_Chng_in_OI', 'CALLS_Volume',
                             'CALLS_IV', 'CALLS_LTP', 'CALLS_Net_Chng', 'Strike_Price', 'PUTS_OI', 'PUTS_Chng_in_OI', 
                             'PUTS_Volume', 'PUTS_IV', 'PUTS_LTP', 'PUTS_Net_Chng']
            else:
                col_names = ['Fetch_Time', 'Symbol', 'Expiry_Date', 'CALLS_OI', 'CALLS_Chng_in_OI', 'CALLS_Volume',
                             'CALLS_IV', 'CALLS_LTP', 'CALLS_Net_Chng', 'CALLS_Bid_Qty', 'CALLS_Bid_Price', 'CALLS_Ask_Price',
                             'CALLS_Ask_Qty', 'Strike_Price', 'PUTS_Bid_Qty', 'PUTS_Bid_Price', 'PUTS_Ask_Price',
                             'PUTS_Ask_Qty', 'PUTS_Net_Chng', 'PUTS_LTP', 'PUTS_IV', 'PUTS_Volume', 'PUTS_Chng_in_OI', 'PUTS_OI']

            oi_data = pd.DataFrame(columns=col_names)
            oi_row = {col: 0 for col in col_names}

            for m in range(len(payload['records']['data'])):
                if not expiry_date or (payload['records']['data'][m]['expiryDate'] == expiry_date):
                    try:
                        oi_row['Expiry_Date'] = payload['records']['data'][m]['expiryDate']
                        oi_row['Strike_Price'] = payload['records']['data'][m]['strikePrice']

                        # Handle CALLS data
                        if 'CE' in payload['records']['data'][m]:
                            ce_data = payload['records']['data'][m]['CE']
                            oi_row['CALLS_OI'] = ce_data.get('openInterest', 0)
                            oi_row['CALLS_Chng_in_OI'] = ce_data.get('changeinOpenInterest', 0)
                            oi_row['CALLS_Volume'] = ce_data.get('totalTradedVolume', 0)
                            oi_row['CALLS_IV'] = ce_data.get('impliedVolatility', 0)
                            oi_row['CALLS_LTP'] = ce_data.get('lastPrice', 0)
                            oi_row['CALLS_Net_Chng'] = ce_data.get('change', 0)

                            if oi_mode == 'full':
                                oi_row['CALLS_Bid_Qty'] = ce_data.get('bidQty', 0)
                                oi_row['CALLS_Bid_Price'] = ce_data.get('bidprice', 0)
                                oi_row['CALLS_Ask_Price'] = ce_data.get('askPrice', 0)
                                oi_row['CALLS_Ask_Qty'] = ce_data.get('askQty', 0)

                        # Handle PUTS data
                        if 'PE' in payload['records']['data'][m]:
                            pe_data = payload['records']['data'][m]['PE']
                            oi_row['PUTS_OI'] = pe_data.get('openInterest', 0)
                            oi_row['PUTS_Chng_in_OI'] = pe_data.get('changeinOpenInterest', 0)
                            oi_row['PUTS_Volume'] = pe_data.get('totalTradedVolume', 0)
                            oi_row['PUTS_IV'] = pe_data.get('impliedVolatility', 0)
                            oi_row['PUTS_LTP'] = pe_data.get('lastPrice', 0)
                            oi_row['PUTS_Net_Chng'] = pe_data.get('change', 0)

                            if oi_mode == 'full':
                                oi_row['PUTS_Bid_Qty'] = pe_data.get('bidQty', 0)
                                oi_row['PUTS_Bid_Price'] = pe_data.get('bidprice', 0)
                                oi_row['PUTS_Ask_Price'] = pe_data.get('askPrice', 0)
                                oi_row['PUTS_Ask_Qty'] = pe_data.get('askQty', 0)

                        if oi_data.empty:
                            oi_data = pd.DataFrame([oi_row]).copy()
                        else:
                            oi_data = pd.concat([oi_data, pd.DataFrame([oi_row])], ignore_index=True)

                    except KeyError:
                        pass

            oi_data['Symbol'] = symbol
            oi_data['Fetch_Time'] = payload['records']['timestamp']
            return oi_data
        except Exception as e:
            print(f"Error fetching live option chain: {e}")
            return pd.DataFrame()

    def get_52_week_high_low(self, stock=None):
        """Get 52 Week High and Low data."""
        try:
            url = 'https://nsearchives.nseindia.com/content/CM_52_wk_High_low_25012024.csv'
            response = requests.get(url, headers=self.headers)
            data = StringIO(response.text.replace(
                '"Disclaimer - The Data provided in the adjusted 52 week high and adjusted 52 week low columns  are adjusted for corporate actions (bonus, splits & rights).For actual (unadjusted) 52 week high & low prices, kindly refer bhavcopy."\n"Effective for 25-Jan-2024"\n',
                ''))
            df = pd.read_csv(data)

            if stock is not None:
                row = df[df['SYMBOL'] == stock]
                if row.empty:
                    return None
                return {
                    "Symbol": stock,
                    "52 Week High": row["Adjusted 52_Week_High"].values[0],
                    "52 Week High Date": row["52_Week_High_Date"].values[0],
                    "52 Week Low": row["Adjusted 52_Week_Low"].values[0],
                    "52 Week Low Date": row["52_Week_Low_DT"].values[0]
                }
            return df
        except Exception as e:
            print(f"Error fetching 52-week data: {e}")
            return None

    def get_corporate_actions(self, from_date_str: str = None, to_date_str: str = None, filter: str = None):
        """Fetch Corporate Action data from NSE."""
        if from_date_str is None:
            from_date = datetime.now() - timedelta(days=30)
            from_date_str = from_date.strftime("%d-%m-%Y")
            to_date_str = datetime.now().strftime("%d-%m-%Y")
        if to_date_str is None:
            to_date_str = datetime.now().strftime("%d-%m-%Y")

        try:
            ref_url = 'https://www.nseindia.com/companies-listing/corporate-filings-actions'
            ref = requests.get(ref_url, headers=self.headers)
            url = f"https://www.nseindia.com/api/corporates-corporateActions?index=equities&from_date={from_date_str}&to_date={to_date_str}"
            data_obj = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            corp_action = pd.DataFrame(data_obj.json())
            if filter is not None:
                corp_action = corp_action[corp_action['subject'].str.contains(filter, case=False, na=False)]
            return corp_action
        except Exception as e:
            print(f"Error fetching Corporate Action Data: {e}")
            return None

    def get_corporate_announcements(self, from_date_str: str = None, to_date_str: str = None):
        """Fetch Corporate Announcements data from NSE."""
        if from_date_str is None:
            from_date = datetime.now() - timedelta(days=30)
            from_date_str = from_date.strftime("%d-%m-%Y")
            to_date_str = datetime.now().strftime("%d-%m-%Y")
        if to_date_str is None:
            to_date_str = datetime.now().strftime("%d-%m-%Y")

        try:
            ref_url = ('https://www.nseindia.com/companies-listing/corporate-filings-announcements')
            ref = requests.get(ref_url, headers=self.headers)
            url = f'https://www.nseindia.com/api/corporate-announcements?index=equities&from_date={from_date_str}&to_date={to_date_str}'
            data_obj = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            corp_announcement = pd.DataFrame(data_obj.json())
            return corp_announcement
        except Exception as e:
            print(f"Error fetching Corporate Announcements Data: {e}")
            return None

    def get_gainers_losers(self):
        """Get gainers and losers data."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/top-gainers-losers'
            ref = requests.get(ref_url, headers=self.headers)

            url = 'https://www.nseindia.com/api/live-analysis-variations?index=gainers'
            data_obj = requests.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data_dict = data_obj.json()

            # Extract gainers
            gain_dict = {
                'Nifty Gainer': pd.DataFrame(data_dict['NIFTY']['data'])['symbol'].to_list(),
                'Bank Nifty Gainer': pd.DataFrame(data_dict['BANKNIFTY']['data'])['symbol'].to_list(),
                'Nifty Next 50 Gainer': pd.DataFrame(data_dict['NIFTYNEXT50']['data'])['symbol'].to_list(),
                'All Securities Gainer': pd.DataFrame(data_dict['allSec']['data'])['symbol'].to_list(),
                'FNO Gainer': pd.DataFrame(data_dict['FOSec']['data'])['symbol'].to_list()
            }

            url = 'https://www.nseindia.com/api/live-analysis-variations?index=loosers'
            data_obj = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data_dict = data_obj.json()

            # Extract losers
            loss_dict = {
                'Nifty Loser': pd.DataFrame(data_dict['NIFTY']['data'])['symbol'].to_list(),
                'Bank Nifty Loser': pd.DataFrame(data_dict['BANKNIFTY']['data'])['symbol'].to_list(),
                'Nifty Next 50 Loser': pd.DataFrame(data_dict['NIFTYNEXT50']['data'])['symbol'].to_list(),
                'All Securities Loser': pd.DataFrame(data_dict['allSec']['data'])['symbol'].to_list(),
                'FNO Loser': pd.DataFrame(data_dict['FOSec']['data'])['symbol'].to_list()
            }

            return gain_dict, loss_dict
        except Exception as e:
            print(f"Error fetching gainers/losers data: {e}")
            return {}, {}

    def get_equity_list(self, list_only=False):
        """Get list of all equity available to trade in NSE."""
        try:
            url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
            nse_resp = self.session.get(url, headers=self.headers, cookies=self.cookies)
            if nse_resp.status_code != 200:
                raise FileNotFoundError(f"No equity list data available")

            data_df = pd.read_csv(BytesIO(nse_resp.content))
            data_df = data_df[['SYMBOL', 'NAME OF COMPANY', ' SERIES', ' DATE OF LISTING', ' FACE VALUE']]

            if list_only:
                symbol_list = data_df['SYMBOL'].tolist()
                return symbol_list
            return data_df
        except Exception as e:
            print(f"Error fetching equity list: {e}")
            return [] if list_only else pd.DataFrame()

    def get_fno_list(self, list_only=False):
        """Get a dataframe of all listed derivative list with the recent lot size to trade."""
        try:
            ref_url = 'https://www.nseindia.com/products-services/equity-derivatives-list-underlyings-information'
            ref = requests.get(ref_url, headers=self.headers)
            url = "https://www.nseindia.com/api/underlying-information"
            response = requests.get(url, headers=self.headers, cookies=ref.cookies.get_dict())

            if response.status_code != 200:
                raise Exception("Resource not available for FNO equity list")

            data_dict = response.json()
            data_df = pd.DataFrame(data_dict['data']['UnderlyingList'])

            if list_only:
                symbol_list = data_df['symbol'].tolist()
                return symbol_list
            return data_df
        except Exception as e:
            print(f"Error fetching FNO list: {e}")
            return [] if list_only else pd.DataFrame()

    def get_equity_bhav_copy(self, trade_date: str):
        """Extract Equity Bhav Copy per the traded date provided."""
        try:
            trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
            url = 'https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_'
            payload = f"{str(trade_date.strftime('%Y%m%d'))}_F_0000.csv.zip"
            request_bhav = requests.get(url + payload, headers=self.headers)

            if request_bhav.status_code == 200:
                zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
                for file_name in zip_bhav.filelist:
                    if file_name:
                        return pd.read_csv(zip_bhav.open(file_name))
            else:
                raise FileNotFoundError(f'Data not found for date: {trade_date}')
        except Exception as e:
            print(f"Error fetching equity bhav copy: {e}")
            return pd.DataFrame()

    def get_fno_bhav_copy(self, trade_date: str):
        """Get the NSE FNO bhav copy data as per the traded date."""
        try:
            trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
            url = 'https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_'
            payload = f"{str(trade_date.strftime('%Y%m%d'))}_F_0000.csv.zip"
            request_bhav = requests.get(url + payload, headers=self.headers)

            if request_bhav.status_code == 200:
                zip_bhav = zipfile.ZipFile(BytesIO(request_bhav.content), 'r')
                for file_name in zip_bhav.filelist:
                    if file_name:
                        return pd.read_csv(zip_bhav.open(file_name))
            else:
                raise FileNotFoundError(f'Data not found for date: {trade_date}')
        except Exception as e:
            print(f"Error fetching FNO bhav copy: {e}")
            return pd.DataFrame()

    def get_bhav_copy_with_delivery(self, trade_date: str):
        """Get the NSE bhav copy with delivery data as per the traded date."""
        try:
            trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
            use_date = trade_date.strftime("%d%m%Y")
            url = f'https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{use_date}.csv'
            request_bhav = requests.get(url, headers=self.headers)

            if request_bhav.status_code == 200:
                bhav_df = pd.read_csv(BytesIO(request_bhav.content))
                bhav_df.columns = [name.replace(' ', '') for name in bhav_df.columns]
                bhav_df['SERIES'] = bhav_df['SERIES'].str.replace(' ', '')
                bhav_df['DATE1'] = bhav_df['DATE1'].str.replace(' ', '')
                return bhav_df
            else:
                raise FileNotFoundError(f'Data not found for date: {trade_date}')
        except Exception as e:
            print(f"Error fetching bhav copy with delivery: {e}")
            return pd.DataFrame()

    def get_indices_bhav_copy(self, trade_date: str):
        """Get NSE indices bhav copy as per the traded date provided."""
        try:
            trade_date = datetime.strptime(trade_date, "%d-%m-%Y")
            url = f"https://nsearchives.nseindia.com/content/indices/ind_close_all_{str(trade_date.strftime('%d%m%Y').upper())}.csv"
            nse_resp = requests.get(url, headers=self.headers)

            if nse_resp.status_code != 200:
                raise FileNotFoundError(f"No data available for: {trade_date}")

            return pd.read_csv(BytesIO(nse_resp.content))
        except Exception as e:
            print(f"Error fetching indices bhav copy: {e}")
            return pd.DataFrame()

    def get_insider_trading(self, from_date: str = None, to_date: str = None):
        """Get insider trading data from NSE."""
        try:
            if from_date is None:
                from_date = datetime.now() - timedelta(days=30)
                from_date_str = from_date.strftime("%d-%m-%Y")
                to_date_str = datetime.now().strftime("%d-%m-%Y")
            else:
                from_date_str = from_date
            if to_date is None:
                to_date_str = datetime.now().strftime("%d-%m-%Y")
            else:
                to_date_str = to_date

            ref_url = 'https://www.nseindia.com/companies-listing/corporate-filings-insider-trading'
            ref = requests.get(ref_url, headers=self.headers)
            url = f'https://www.nseindia.com/api/corporates-pit?index=equities&from_date={from_date_str}&to_date={to_date_str}'
            response = requests.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['data'])
        except Exception as e:
            print(f"Error fetching insider trading data: {e}")
            return pd.DataFrame()

    def get_upcoming_results(self):
        """Get upcoming results calendar from NSE."""
        try:
            ref_url = 'https://www.nseindia.com/companies-listing/corporate-filings-event-calendar'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/event-calendar?'
            response = requests.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            df = pd.DataFrame(data)
            events = df[df['purpose'].str.contains('Results', case=False, na=False)]
            return events
        except Exception as e:
            print(f"Error fetching upcoming results: {e}")
            return pd.DataFrame()

    def get_most_active_by_volume(self):
        """Get most active equity stocks by volume."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/most-active-equities'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/live-analysis-most-active-securities?index=volume'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['data'])
        except Exception as e:
            print(f"Error fetching most active by volume: {e}")
            return pd.DataFrame()

    def get_most_active_by_value(self):
        """Get most active equity stocks by value."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/most-active-equities'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/live-analysis-most-active-securities?index=value'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['data'])
        except Exception as e:
            print(f"Error fetching most active by value: {e}")
            return pd.DataFrame()

    def get_most_active_index_calls(self):
        """Get most active index calls."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=calls-index-vol'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['OPTIDX']['data'])
        except Exception as e:
            print(f"Error fetching most active index calls: {e}")
            return pd.DataFrame()

    def get_most_active_index_puts(self):
        """Get most active index puts."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=puts-index-vol'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['OPTIDX']['data'])
        except Exception as e:
            print(f"Error fetching most active index puts: {e}")
            return pd.DataFrame()

    def get_most_active_stock_calls(self):
        """Get most active stock calls."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=calls-stocks-vol'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['OPTSTK']['data'])
        except Exception as e:
            print(f"Error fetching most active stock calls: {e}")
            return pd.DataFrame()

    def get_most_active_stock_puts(self):
        """Get most active stock puts."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=puts-stocks-vol'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['OPTSTK']['data'])
        except Exception as e:
            print(f"Error fetching most active stock puts: {e}")
            return pd.DataFrame()

    def get_most_active_contracts_by_oi(self):
        """Get most active contracts by open interest."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=oi'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['volume']['data'])
        except Exception as e:
            print(f"Error fetching most active contracts by OI: {e}")
            return pd.DataFrame()

    def get_most_active_contracts_by_volume(self):
        """Get most active contracts by volume."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=contracts'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['volume']['data'])
        except Exception as e:
            print(f"Error fetching most active contracts by volume: {e}")
            return pd.DataFrame()

    def get_most_active_futures_by_volume(self):
        """Get most active futures contracts by volume."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=futures'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['volume']['data'])
        except Exception as e:
            print(f"Error fetching most active futures by volume: {e}")
            return pd.DataFrame()

    def get_most_active_options_by_volume(self):
        """Get most active options contracts by volume."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/most-active-contracts'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/snapshot-derivatives-equity?index=options&limit=20'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['volume']['data'])
        except Exception as e:
            print(f"Error fetching most active options by volume: {e}")
            return pd.DataFrame()

    def get_index_pe_ratio(self):
        """Get P/E ratios for indices."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/index-performances'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/allIndices'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            df = pd.json_normalize(data['data'])

            if not df.empty:
                df = df[['indexSymbol', 'key', 'pe']]
                df = df[df['pe'].str.strip() != '']
                df = df[df['pe'].str.strip() != 'None']
                df.columns = ['Index', 'Type', 'Profit_Earning_Ratio']
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching index P/E ratio: {e}")
            return pd.DataFrame()

    def get_index_pb_ratio(self):
        """Get P/B ratios for indices."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/index-performances'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/allIndices'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            df = pd.json_normalize(data['data'])

            if not df.empty:
                df = df[['indexSymbol', 'key', 'pb']]
                df = df[df['pb'].str.strip() != '']
                df = df[df['pb'].str.strip() != 'None']
                df.columns = ['Index', 'Type', 'Price_Book_Ratio']
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching index P/B ratio: {e}")
            return pd.DataFrame()

    def get_index_dividend_yield(self):
        """Get dividend yield for indices."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/index-performances'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/allIndices'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            df = pd.json_normalize(data['data'])

            if not df.empty:
                df = df[['indexSymbol', 'key', 'dy']]
                df = df[df['dy'].str.strip() != '']
                df = df[df['dy'].str.strip() != 'None']
                df.columns = ['Index', 'Type', 'Dividend_Yield']
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching index dividend yield: {e}")
            return pd.DataFrame()

    def get_advance_decline(self):
        """Get advance/decline data for indices."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/live-market-indices'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/allIndices'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            df = pd.json_normalize(data['data'])

            if not df.empty:
                df = df[['indexSymbol', 'advances', 'declines', 'unchanged']]
                df.dropna(inplace=True)
                df.columns = ['Index', 'Advances', 'Declines', 'Unchanged']
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching advance/decline data: {e}")
            return pd.DataFrame()

    def get_index_historical_data(self, index: str, from_date: str, to_date: str):
        """Get historical index data set for the specific time period."""
        try:
            # Check for valid dates and period inputs
            if not from_date or not to_date:
                raise ValueError('Please provide valid date parameters')

            from_dt = datetime.strptime(from_date, "%d-%m-%Y")
            to_dt = datetime.strptime(to_date, "%d-%m-%Y")
            time_delta = (to_dt - from_dt).days
            if time_delta < 1:
                raise ValueError('to_date should be greater than from_date')

            index_data_columns = ['TIMESTAMP', 'INDEX_NAME', 'OPEN_INDEX_VAL', 'HIGH_INDEX_VAL', 
                                 'CLOSE_INDEX_VAL', 'LOW_INDEX_VAL', 'TRADED_QTY', 'TURN_OVER']

            nse_df = pd.DataFrame(columns=index_data_columns)
            from_date_obj = datetime.strptime(from_date, "%d-%m-%Y")
            to_date_obj = datetime.strptime(to_date, "%d-%m-%Y")
            load_days = (to_date_obj - from_date_obj).days

            while load_days > 0:
                if load_days > 365:
                    end_date = (from_date_obj + timedelta(364)).strftime("%d-%m-%Y")
                    start_date = from_date_obj.strftime("%d-%m-%Y")
                else:
                    end_date = to_date_obj.strftime("%d-%m-%Y")
                    start_date = from_date_obj.strftime("%d-%m-%Y")

                data_df = self._get_index_data(index=index, from_date=start_date, to_date=end_date)
                from_date_obj = from_date_obj + timedelta(365)
                load_days = (to_date_obj - from_date_obj).days

                if nse_df.empty:
                    nse_df = data_df
                else:
                    nse_df = pd.concat([nse_df, data_df], ignore_index=True)
            return nse_df
        except Exception as e:
            print(f"Error fetching index historical data: {e}")
            return pd.DataFrame()

    def _get_index_data(self, index: str, from_date: str, to_date: str):
        """Helper method to get index data for specific date range."""
        try:
            index_data_columns = ['TIMESTAMP', 'INDEX_NAME', 'OPEN_INDEX_VAL', 'HIGH_INDEX_VAL', 
                                 'CLOSE_INDEX_VAL', 'LOW_INDEX_VAL', 'TRADED_QTY', 'TURN_OVER']

            index = index.replace(' ', '%20').upper()
            ref_url = 'https://www.nseindia.com/reports-indices-historical-index-data'
            ref = requests.get(ref_url, headers=self.headers)

            url = f"https://www.nseindia.com/api/historical/indicesHistory?indexType={index}&from={from_date}&to{to_date}"
            data_json = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict()).json()

            data_close_df = pd.DataFrame(data_json['data']['indexCloseOnlineRecords']).drop(
                columns=['_id', "EOD_TIMESTAMP"])
            data_turnover_df = pd.DataFrame(data_json['data']['indexTurnoverRecords']).drop(
                columns=['_id', 'HIT_INDEX_NAME_UPPER'])
            data_df = pd.merge(data_close_df, data_turnover_df, on='TIMESTAMP', how='inner')

            data_df.drop(columns='TIMESTAMP', inplace=True)

            unwanted_str_list = ['FH_', 'EOD_', 'HIT_']
            new_col = data_df.columns
            for unwanted in unwanted_str_list:
                new_col = [name.replace(f'{unwanted}', '') for name in new_col]

            data_df.columns = new_col
            return data_df[index_data_columns]
        except Exception as e:
            print(f"Error in _get_index_data: {e}")
            return pd.DataFrame()

    def get_etf_list(self):
        """Get all ETF symbols."""
        try:
            ref_url = 'https://www.nseindia.com/market-data/exchange-traded-funds-etf'
            ref = requests.get(ref_url, headers=self.headers)
            url = 'https://www.nseindia.com/api/etf'
            response = self.session.get(url, headers=self.headers, cookies=ref.cookies.get_dict())
            data = response.json()
            return pd.DataFrame(data['data'])
        except Exception as e:
            print(f"Error fetching ETF list: {e}")
            return pd.DataFrame()

    def get_market_depth(self, symbol):
        """Function to retrieve market depth for a given symbol."""
        try:
            data = self.get_equity_info(symbol)
            if data and 'tradeData' in data:
                return {
                    'ask': data['tradeData']['marketDeptOrderBook']['ask'],
                    'bid': data['tradeData']['marketDeptOrderBook']['bid']
                }
            return {}
        except Exception as e:
            print(f"Error fetching market depth: {e}")
            return {}

    def get_fii_dii_activity(self):
        """FII and DII trading activity of the day."""
        try:
            url = "https://www.nseindia.com/api/fiidiiTradeReact"
            data_json = requests.get(url, headers=self.headers)
            return pd.DataFrame(data_json.json())
        except Exception as e:
            print(f"Error fetching FII/DII activity: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    # Initialize NSE instance
    nse = NSE()

    # Select Timeframe for historic data download
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)

    # Symbol Search - NSE
    print("********************  Symbol Search Utility  **********************")
    symbols = nse.search('NIFTY BANK', exchange='NSE', match=False)
    print(symbols)

    # Symbol Search - NFO
    symbols = nse.search('BANKNIFTY25APR', exchange='NFO', match=False)
    print("********************  Symbol Search Utility  **********************")
    print(symbols)

    # Download Index EOD Data
    data = nse.get_history(
        symbol='NIFTY',
        exchange='NSE',
        start=start_date,
        end=end_date,
        interval='1d'
    )
    print("********************  Index EOD Data  **********************")
    print("Symbol : NIFTY 50")
    print(data.head(2))

    # Download Index Intraday Data
    data = nse.get_history(
        symbol='NIFTY BANK',
        exchange='NSE',
        start=start_date,
        end=end_date,
        interval='1m'
    )
    print("********************  Index Intraday Data  **********************")
    print("Symbol : BANKNIFTY - 1 Minute data")
    print(data.head(2))

    # Download Stock (Underlying) Data
    data = nse.get_history(
        symbol='TCS',
        exchange='NSE',
        start=start_date,
        end=end_date,
        interval='10m'
    )
    print("********************  Stock Intraday Data  **********************")
    print("Symbol : TCS - 10 Minute data")
    print(data.head(2))