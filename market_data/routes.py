from flask import jsonify, request
from . import market_bp
from .service import get_live_price, get_historical_candles

@market_bp.route('/price/<symbol>', methods=['GET'])
def fetch_price(symbol):
    # Now receives a full dictionary with price, change, volume, etc.
    market_data = get_live_price(symbol)
    
    if market_data is None:
        return jsonify({"error": f"Could not find market data for {symbol}"}), 404
    
    market_data["symbol"] = symbol
    return jsonify(market_data), 200

@market_bp.route('/candles/<symbol>', methods=['GET'])
def fetch_candles(symbol):
    period = request.args.get('period', '1mo')
    interval = request.args.get('interval', '1d')
    
    candles = get_historical_candles(symbol, period, interval)
    if not candles:
        return jsonify({"error": "No data found"}), 404
        
    return jsonify({
        "symbol": symbol,
        "candles": candles
    }), 200