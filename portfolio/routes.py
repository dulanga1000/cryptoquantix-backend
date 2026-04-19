from flask import Blueprint, request, jsonify
from portfolio.service import (
    add_to_watchlist,
    get_watchlist,
    remove_from_watchlist,
    add_trade,
    get_summary
)

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/api/watchlist/add', methods=['POST'])
def add_watchlist():
    data = request.json
    symbol = data.get('symbol')

    if not symbol:
        return jsonify({"error": "Missing symbol"}), 400

    result = add_to_watchlist(symbol)
    return jsonify(result)

@portfolio_bp.route('/api/watchlist', methods=['GET'])
def watchlist():
    return jsonify(get_watchlist())

@portfolio_bp.route('/api/watchlist/remove', methods=['DELETE'])
def remove_watchlist():
    data = request.json
    symbol = data.get('symbol')

    if not symbol:
        return jsonify({"error": "Missing symbol"}), 400

    result = remove_from_watchlist(symbol)

    if "error" in result:
        return jsonify(result), 404

    return jsonify(result)

@portfolio_bp.route('/api/portfolio/trade', methods=['POST'])
def trade():
    data = request.json
    return jsonify(add_trade(data))

@portfolio_bp.route('/api/portfolio/summary', methods=['GET'])
def summary():
    return jsonify(get_summary())