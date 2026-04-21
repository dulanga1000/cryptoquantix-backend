import yfinance as yf

def get_current_price(symbol):
    """Helper to get fresh price for P&L calculations."""
    if symbol == 'USD': return 1.0  
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        # 🔥 FIXED: Cast the pandas/numpy value to a standard Python float
        return float(data['Close'].iloc[-1]) if not data.empty else 0.0
    except:
        return 0.0

def calculate_portfolio_performance(trades):
    """Aggregates ledger trades and calculates true value and P&L."""
    portfolio_map = {}
    
    # 1. Build the Ledger Cost Basis
    for trade in trades:
        sym = trade.symbol
        if sym not in portfolio_map:
            portfolio_map[sym] = {"quantity": 0.0, "invested": 0.0}
        
        if trade.quantity > 0: # BUY
            portfolio_map[sym]["quantity"] += trade.quantity
            portfolio_map[sym]["invested"] += (trade.buy_price * trade.quantity)
        else: # SELL
            # Selling reduces the total quantity and the total invested amount proportionally
            if portfolio_map[sym]["quantity"] > 0:
                avg_price = portfolio_map[sym]["invested"] / portfolio_map[sym]["quantity"]
                portfolio_map[sym]["quantity"] += trade.quantity # trade.quantity is negative here
                portfolio_map[sym]["invested"] += (trade.quantity * avg_price)

    summary = []
    total_invested = 0.0
    crypto_value = 0.0
    usd_balance = 0.0

    # 2. Calculate Live P&L
    for symbol, data in portfolio_map.items():
        if data["quantity"] <= 0.0001:  # Ignore empty bags
            continue
            
        if symbol == 'USD':
            usd_balance = data["quantity"]
            continue
            
        current_p = get_current_price(symbol)
        qty = data["quantity"]
        invested = data["invested"]
        
        avg_buy_price = invested / qty if qty > 0 else 0
        current_val = current_p * qty
        p_l = current_val - invested
        
        total_invested += invested
        crypto_value += current_val

        summary.append({
            "id": symbol,
            "symbol": symbol,
            "quantity": round(float(qty), 6),
            "buy_price": round(float(avg_buy_price), 2),
            "current_price": round(float(current_p), 2),
            "p_l": round(float(p_l), 2),
            "p_l_percent": round(float((p_l / invested) * 100), 2) if invested > 0 else 0.0
        })

    # 3. Return clean, separated data to React
    return {
        "assets": summary,
        "usd_balance": round(float(usd_balance), 2),
        "total_invested": round(float(total_invested), 2),
        "crypto_value": round(float(crypto_value), 2),
        "overall_p_l": round(float(crypto_value - total_invested), 2)
    }