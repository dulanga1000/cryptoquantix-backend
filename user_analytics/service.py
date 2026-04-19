import yfinance as yf

def get_current_price(symbol):
    """Helper to get fresh price for P&L calculations."""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        return data['Close'].iloc[-1] if not data.empty else 0
    except:
        return 0

def calculate_portfolio_performance(trades):
    """Calculates total value and P&L for a list of trade objects."""
    summary = []
    total_invested = 0
    total_current_value = 0

    for trade in trades:
        current_p = get_current_price(trade.symbol)
        invested = trade.buy_price * trade.quantity
        current_val = current_p * trade.quantity
        p_l = current_val - invested
        
        total_invested += invested
        total_current_value += current_val

        summary.append({
            "id": trade.id,
            "symbol": trade.symbol,
            "quantity": trade.quantity,
            "buy_price": trade.buy_price,
            "current_price": round(current_p, 2),
            "p_l": round(p_l, 2),
            "p_l_percent": round((p_l / invested) * 100, 2) if invested > 0 else 0
        })

    return {
        "assets": summary,
        "total_invested": round(total_invested, 2),
        "total_value": round(total_current_value, 2),
        "overall_p_l": round(total_current_value - total_invested, 2)
    }