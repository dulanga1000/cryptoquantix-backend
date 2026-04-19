from flask import Blueprint, jsonify, request
from .service import *

market_bp = Blueprint('market', __name__)


# 📈 Stock price
@market_bp.route('/price/<symbol>', methods=['GET'])
def price(symbol):
    result = get_stock_price(symbol)

    if result is None:
        return jsonify({"error": "Invalid symbol"}), 404

    return jsonify({
        "symbol": symbol.upper(),
        "price": result
    })


# 📊 Candles
@market_bp.route('/candles/<symbol>', methods=['GET'])
def candles(symbol):
    data = get_candles(symbol)

    return jsonify({
        "symbol": symbol.upper(),
        "candles": data
    })


# 🔍 Search
@market_bp.route('/search', methods=['GET'])
def search():
    q = request.args.get("q", "")
    results = search_symbol(q)

    return jsonify({
        "query": q,
        "results": results
    })


# 🚀 Trending
@market_bp.route('/trending', methods=['GET'])
def trending():
    return jsonify({
        "trending": get_trending()
    })


# 💰 Crypto
@market_bp.route('/crypto/<symbol>', methods=['GET'])
def crypto(symbol):
    price = get_crypto_price(symbol)

    if price is None:
        return jsonify({"error": "Invalid crypto"}), 404

    return jsonify({
        "symbol": symbol,
        "price_usd": price
    })