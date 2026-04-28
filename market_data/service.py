import yfinance as yf

def get_live_price(symbol: str):
    """Fetches the current market price and 24h details for a given symbol."""
    try:
        ticker = yf.Ticker(symbol)
        #  Fetch 2 days to calculate 24h change
        data = ticker.history(period="2d")
        if data.empty:
            return None

        current_price = round(data['Close'].iloc[-1], 2)
        high_price = round(data['High'].iloc[-1], 2)
        low_price = round(data['Low'].iloc[-1], 2)
        volume = int(data['Volume'].iloc[-1])

        change = 0
        change_percent = 0
        if len(data) >= 2:
            prev_close = data['Close'].iloc[-2]
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100

        return {
            "price": current_price,
            "high_24h": high_price,
            "low_24h": low_price,
            "volume": volume,
            "change": round(change, 2),
            "change_percent": round(change_percent, 2)
        }
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
    common = {
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
        "SOL": "SOL-USD",
        "AAPL": "AAPL",
        "TSLA": "TSLA"
    }
    return common.get(query.upper(), query.upper())