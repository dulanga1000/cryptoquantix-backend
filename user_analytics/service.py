import yfinance as yf
from datetime import datetime

def get_current_price(symbol):
    """Helper to get fresh price for P&L calculations."""
    if symbol == 'USD': return 1.0  
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        return float(data['Close'].iloc[-1]) if not data.empty else 0.0
    except:
        return 0.0

def calculate_portfolio_performance(trades):
    """Aggregates ledger trades and calculates true value and P&L."""
    portfolio_map = {}
    
    buy_count = 0
    sell_count = 0
    swap_count = 0
    
    raw_history = []

    for trade in trades:
        sym = trade.symbol
        action = getattr(trade, 'action', 'SYSTEM') 
        
        if action == 'BUY' and trade.quantity > 0 and sym != 'USD':
            buy_count += 1
        elif action == 'SELL' and trade.quantity < 0 and sym != 'USD':
            sell_count += 1
        elif action == 'SWAP' and trade.quantity > 0:
            swap_count += 1

        if sym != 'USD' or action == 'SYSTEM': 
            raw_history.append({
                "id": trade.id,
                "symbol": sym,
                "action": action,
                "quantity": round(float(trade.quantity), 6),
                "price": round(float(trade.buy_price), 2),
                "total_value": round(float(abs(trade.quantity) * trade.buy_price), 2),
                "timestamp": trade.timestamp.strftime("%b %d, %Y - %H:%M") if trade.timestamp else "N/A"
            })

        if sym not in portfolio_map:
            portfolio_map[sym] = {"quantity": 0.0, "invested": 0.0}
        
        if trade.quantity > 0: 
            portfolio_map[sym]["quantity"] += trade.quantity
            portfolio_map[sym]["invested"] += (trade.buy_price * trade.quantity)
        else: 
            if portfolio_map[sym]["quantity"] > 0:
                avg_price = portfolio_map[sym]["invested"] / portfolio_map[sym]["quantity"]
                portfolio_map[sym]["quantity"] += trade.quantity 
                portfolio_map[sym]["invested"] += (trade.quantity * avg_price)

    raw_history.sort(key=lambda x: x["id"], reverse=True)

    summary = []
    total_invested = 0.0
    crypto_value = 0.0
    usd_balance = 0.0

    for symbol, data in portfolio_map.items():
        if data["quantity"] <= 0.0001:  
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

    return {
        "assets": summary,
        "usd_balance": round(float(usd_balance), 2),
        "total_invested": round(float(total_invested), 2),
        "crypto_value": round(float(crypto_value), 2),
        "overall_p_l": round(float(crypto_value - total_invested), 2),
        "buy_count": buy_count,
        "sell_count": sell_count,
        "swap_count": swap_count,
        "history": raw_history 
    }