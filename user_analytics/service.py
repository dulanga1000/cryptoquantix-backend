import yfinance as yf

def get_current_price(symbol):
    """Helper to get fresh price for P&L calculations."""
    if symbol == 'USD': return 1.0  # USD is always $1
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        return data['Close'].iloc[-1] if not data.empty else 0
    except:
        return 0

def calculate_portfolio_performance(trades):
    """Aggregates ledger trades and calculates total value and P&L."""
    
    # 🔥 1. Aggregate trades by symbol (Append-Only Ledger logic)
    portfolio_map = {}
    for trade in trades:
        if trade.symbol not in portfolio_map:
            portfolio_map[trade.symbol] = {"quantity": 0.0, "total_cost": 0.0}
        
        portfolio_map[trade.symbol]["quantity"] += trade.quantity
        
        # Only add to cost basis if it's a BUY (positive quantity)
        if trade.quantity > 0:
            portfolio_map[trade.symbol]["total_cost"] += (trade.buy_price * trade.quantity)

    summary = []
    total_invested = 0
    total_current_value = 0

    # 🔥 2. Build final UI data
    for symbol, data in portfolio_map.items():
        if data["quantity"] <= 0.0001:  # Ignore empty bags
            continue
            
        current_p = get_current_price(symbol)
        avg_buy_price = data["total_cost"] / data["quantity"] if data["quantity"] > 0 else 0
        invested = avg_buy_price * data["quantity"]
        current_val = current_p * data["quantity"]
        p_l = current_val - invested
        
        total_invested += invested
        total_current_value += current_val

        summary.append({
            "id": symbol,
            "symbol": symbol,
            "quantity": round(data["quantity"], 6),
            "buy_price": round(avg_buy_price, 2),
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