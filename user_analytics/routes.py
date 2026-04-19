from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import analytics_bp
from extensions import db
from database.models import Watchlist, Trade
from .service import calculate_portfolio_performance

# --- WATCHLIST ROUTES ---

@analytics_bp.route('/watchlist', methods=['GET'])
@jwt_required()
def get_watchlist():
    user_id = get_jwt_identity()
    items = Watchlist.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": i.id, "symbol": i.symbol} for i in items]), 200

@analytics_bp.route('/watchlist', methods=['POST'])
@jwt_required()
def add_to_watchlist():
    user_id = get_jwt_identity()
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    
    if not symbol:
        return jsonify({"msg": "Symbol is required"}), 400
    
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
    user_id = get_jwt_identity()
    trades = Trade.query.filter_by(user_id=user_id).all()
    performance = calculate_portfolio_performance(trades)
    return jsonify(performance), 200

@analytics_bp.route('/portfolio/trade', methods=['POST'])
@jwt_required()
def add_trade():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 🔍 Debug: Print the exact data hitting the server
    print(f"--- INCOMING TRADE DATA ---")
    print(f"User ID: {user_id}")
    print(f"Data: {data}")

    if not data:
        return jsonify({"msg": "No JSON data received"}), 400

    # 1. Check for missing keys
    required = ["symbol", "quantity", "buy_price"]
    if not all(k in data for k in required):
        return jsonify({"msg": f"Missing fields. Required: {required}"}), 422

    try:
        # 2. Extract and sanitize
        raw_symbol = str(data.get('symbol', '')).strip().upper()
        raw_qty = data.get('quantity')
        raw_price = data.get('buy_price')

        # 3. Explicitly convert to float
        qty = float(raw_qty)
        price = float(raw_price)

        # 4. Save to database
        new_trade = Trade(
            user_id=user_id,
            symbol=raw_symbol,
            quantity=qty,
            buy_price=price
        )
        db.session.add(new_trade)
        db.session.commit()
        
        return jsonify({"msg": "Trade recorded ✅", "symbol": raw_symbol}), 201

    except (ValueError, TypeError) as e:
        print(f"❌ CONVERSION ERROR: {str(e)}")
        return jsonify({"msg": f"Data format error: {str(e)}"}), 422
    except Exception as e:
        print(f"❌ DATABASE ERROR: {str(e)}")
        return jsonify({"msg": "Internal server error"}), 500