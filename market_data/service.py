import yfinance as yf

def get_live_price(symbol: str):
    """Fetches the current market price for a given symbol."""
    try:
        ticker = yf.Ticker(symbol)
        # Fast way to get the most recent price
        data = ticker.history(period="1d")
        if data.empty:
            return None
        return round(data['Close'].iloc[-1], 2)
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

def get_historical_candles(symbol: str, period="1mo", interval="1d"):
    """Fetches historical OHLCV data for charting."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return []

        # Format data for the React frontend charts
        candles = []
        for index, row in df.iterrows():
            candles.append({
                "date": index.strftime('%Y-%m-%d'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        return candles
    except Exception as e:
        print(f"Error fetching candles for {symbol}: {e}")
        return []

def search_symbols(query: str):
    """
    Simple helper to handle common tickers. 
    Note: yfinance doesn't have a robust 'search' endpoint, 
    so we use a map for common crypto/stocks.
    """
    common = {
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
        "SOL": "SOL-USD",
        "AAPL": "AAPL",
        "TSLA": "TSLA"
    }
    return common.get(query.upper(), query.upper())