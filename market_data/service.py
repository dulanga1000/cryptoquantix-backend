import yfinance as yf
import requests

# 📈 Stock price
def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")

        # check empty / invalid
        if data is None or data.empty:
            return None

        price = data['Close'].iloc[-1]

        # safe convert
        if price is None:
            return None

        return float(price)

    except Exception as e:
        print("Stock Price Error:", e)
        return None


# 📊 Candle data (OHLC)
def get_candles(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="5d")

        if data is None or data.empty:
            return []

        candles = []

        for index, row in data.iterrows():
            try:
                candles.append({
                    "date": str(index),
                    "open": float(row.get("Open", 0)),
                    "high": float(row.get("High", 0)),
                    "low": float(row.get("Low", 0)),
                    "close": float(row.get("Close", 0)),
                    "volume": int(row.get("Volume", 0))
                })
            except:
                continue  # skip broken row

        return candles

    except Exception as e:
        print("Candles Error:", e)
        return []


# 🔍 Search (simple version)
def search_symbol(query):
    try:
        sample = ["AAPL", "TSLA", "GOOGL", "MSFT"]
        return [s for s in sample if query.upper() in s]
    except Exception as e:
        print("Search Error:", e)
        return []


# 🚀 Trending (mock)
def get_trending():
    return ["AAPL", "TSLA", "BTC", "ETH"]


# 💰 Crypto price
def get_crypto_price(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        res = requests.get(url, timeout=5)

        if res.status_code != 200:
            return None

        data = res.json()

        if symbol not in data:
            return None

        return data[symbol]["usd"]

    except Exception as e:
        print("Crypto Error:", e)
        return None