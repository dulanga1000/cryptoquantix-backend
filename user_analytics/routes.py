from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import analytics_bp
from extensions import db
from database.models import Watchlist, Trade
from .service import calculate_portfolio_performance, get_current_price

# --- WATCHLIST ROUTES ---
@analytics_bp.route('/watchlist', methods=['GET'])
@jwt_required()
def get_watchlist():
    user_id = int(get_jwt_identity()) 
    items = Watchlist.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": i.id, "symbol": i.symbol} for i in items]), 200

@analytics_bp.route('/watchlist', methods=['POST'])
@jwt_required()
def add_to_watchlist():
    user_id = int(get_jwt_identity()) 
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    
    if not symbol: return jsonify({"msg": "Symbol is required"}), 400
    if Watchlist.query.filter_by(user_id=user_id, symbol=symbol).first():
        return jsonify({"msg": "Symbol already in watchlist"}), 400
    
    new_item = Watchlist(user_id=user_id, symbol=symbol)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"msg": "Added to watchlist"}), 201

# --- PORTFOLIO ROUTES ---
@analytics_bp.route('/portfolio', methods=['GET'])
@jwt_required()
def get_portfolio():
    user_id = int(get_jwt_identity()) 
    trades = Trade.query.filter_by(user_id=user_id).all()
    performance = calculate_portfolio_performance(trades)
    return jsonify(performance), 200

@analytics_bp.route('/portfolio/trade', methods=['POST'])
@jwt_required()
def add_trade():
    user_id = int(get_jwt_identity()) 
    data = request.get_json()

    required = ["symbol", "quantity", "buy_price", "side"]
    if not all(k in data for k in required):
        return jsonify({"msg": f"Missing fields. Required: {required}"}), 422

    try:
        raw_symbol = str(data.get('symbol', '')).strip().upper()
        qty = float(data.get('quantity'))
        price = float(data.get('buy_price'))
        side = str(data.get('side', 'BUY')).upper()
        cost = float(qty * price)

        usd_trades = Trade.query.filter_by(user_id=user_id, symbol='USD').all()
        usd_balance = float(sum(t.quantity for t in usd_trades))
        
        crypto_trades = Trade.query.filter_by(user_id=user_id, symbol=raw_symbol).all()
        crypto_balance = float(sum(t.quantity for t in crypto_trades))

        if side == 'BUY':
            if usd_balance < cost:
                return jsonify({"msg": f"Insufficient USD. Trade costs ${cost:,.2f}, your balance is ${usd_balance:,.2f}"}), 400
            
            new_crypto_trade = Trade(user_id=user_id, symbol=raw_symbol, quantity=qty, buy_price=price, action=side)
            usd_trade = Trade(user_id=user_id, symbol='USD', quantity=-cost, buy_price=1.0, action=side)
            
        elif side == 'SELL':
            if crypto_balance < qty:
                return jsonify({"msg": f"Insufficient {raw_symbol}. Trying to sell {qty}, but you only own {crypto_balance}"}), 400
            
            new_crypto_trade = Trade(user_id=user_id, symbol=raw_symbol, quantity=-qty, buy_price=price, action=side)
            usd_trade = Trade(user_id=user_id, symbol='USD', quantity=cost, buy_price=1.0, action=side)
        else:
            return jsonify({"msg": "Invalid trade side."}), 400

        db.session.add(new_crypto_trade)
        db.session.add(usd_trade)
        db.session.commit()
        
        return jsonify({"msg": f"{side} order executed ✅", "symbol": raw_symbol}), 201

    except Exception as e:
        return jsonify({"msg": f"Internal server error: {str(e)}"}), 500

# --- CRYPTO SWAP ROUTE ---
@analytics_bp.route('/portfolio/swap', methods=['POST'])
@jwt_required()
def swap_crypto():
    user_id = int(get_jwt_identity()) 
    data = request.get_json()

    required = ["from_symbol", "to_symbol", "quantity"]
    if not all(k in data for k in required):
        return jsonify({"msg": f"Missing fields. Required: {required}"}), 422

    try:
        from_symbol = str(data.get('from_symbol', '')).strip().upper()
        to_symbol = str(data.get('to_symbol', '')).strip().upper()
        qty = float(data.get('quantity'))

        if qty <= 0:
            return jsonify({"msg": "Quantity must be greater than zero."}), 400
        if from_symbol == to_symbol:
            return jsonify({"msg": "Cannot swap the same asset."}), 400

        from_trades = Trade.query.filter_by(user_id=user_id, symbol=from_symbol).all()
        from_balance = float(sum(t.quantity for t in from_trades))

        if from_balance < qty:
            return jsonify({"msg": f"Insufficient {from_symbol} balance for this swap."}), 400

        from_price = float(get_current_price(from_symbol))
        to_price = float(get_current_price(to_symbol))

        if from_price <= 0 or to_price <= 0:
            return jsonify({"msg": "Error fetching live market exchange rates."}), 500

        usd_value = float(qty * from_price)
        receive_qty = float(usd_value / to_price)

        deduct_trade = Trade(user_id=user_id, symbol=from_symbol, quantity=float(-qty), buy_price=from_price, action='SWAP')
        add_trade = Trade(user_id=user_id, symbol=to_symbol, quantity=receive_qty, buy_price=to_price, action='SWAP')

        db.session.add(deduct_trade)
        db.session.add(add_trade)
        db.session.commit()

        return jsonify({
            "msg": f"Successfully swapped for {receive_qty:.6f} {to_symbol} ✅", 
            "received": receive_qty
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"msg": f"Database execution error: {str(e)}"}), 500