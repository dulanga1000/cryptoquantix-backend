watchlist = []
transactions = []

def add_to_watchlist(symbol):
    if symbol not in watchlist:
        watchlist.append(symbol)

    return {
        "message": "Added to watchlist",
        "watchlist": watchlist
    }

def get_watchlist():
    return {
        "watchlist": watchlist
    }

def remove_from_watchlist(symbol):
    if symbol in watchlist:
        watchlist.remove(symbol)
        return {
            "message": "Removed from watchlist",
            "watchlist": watchlist
        }
    else:
        return {
            "error": "Symbol not found"
        }

def add_trade(data):
    symbol = data.get("symbol")
    price = data.get("price")
    quantity = data.get("quantity")
    trade_type = data.get("type")

    if not symbol or price is None or quantity is None or not trade_type:
        return {"error": "Invalid trade data"}

    trade = {
        "symbol": symbol,
        "price": price,
        "quantity": quantity,
        "type": trade_type
    }

    transactions.append(trade)

    return {
        "message": "Trade added",
        "trade": trade
    }

def get_summary():
    total_trades = len(transactions)

    total_investment = 0
    current_value = 0

    for trade in transactions:
        price = trade.get("price", 0)
        quantity = trade.get("quantity", 0)

        total_investment += price * quantity

        current_price = price * 1.1
        current_value += current_price * quantity

    profit_loss = current_value - total_investment

    percent_return = 0
    if total_investment > 0:
        percent_return = (profit_loss / total_investment) * 100

    return {
        "total_trades": total_trades,
        "transactions": transactions,
        "total_investment": round(total_investment, 2),
        "current_value": round(current_value, 2),
        "profit_loss": round(profit_loss, 2),
        "percent_return": round(percent_return, 2)
    }