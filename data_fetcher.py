import yfinance as yf

def get_full_ticker(ticker, market):
    """
    Appends the appropriate suffix to the ticker symbol based on the market.

    :param ticker: Stock ticker symbol (e.g., 'TCS').
    :param market: Market identifier ('NSE' or 'BSE').
    :return: Full ticker symbol including suffix.
    """
    if market == 'NSE':
        return f"{ticker}.NS"
    elif market == 'BSE':
        return f"{ticker}.BO"
    else:
        raise ValueError("Market must be either 'NSE' or 'BSE'.")

def fetch_data(ticker, market, start, end):
    """
    Fetches historical data for the given ticker from the specified market.

    :param ticker: Stock ticker symbol (e.g., 'TCS').
    :param market: Market identifier ('NSE' or 'BSE').
    :param start: Start date for fetching data (string format 'YYYY-MM-DD').
    :param end: End date for fetching data (string format 'YYYY-MM-DD').
    :return: Pandas DataFrame with the historical data.
    """
    full_ticker = get_full_ticker(ticker, market)
    print(full_ticker)
    data = yf.download(full_ticker, start=start, end=end)
    return data

