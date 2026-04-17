
from flask import jsonify, request

from . import fibonacci_bp 
from .service import generate_signals

# 2. Define the exact path (URL) the Waiter is listening to
@fibonacci_bp.route('/calculate', methods=['POST'])
def calculate_trading_levels():
    """
    API Endpoint that receives React data, passes it to the service logic,
    and returns the trading signals as a JSON response.
    """
    
    try:
        # Step A: The Waiter takes the order from the Customer (React)
        # React sends data in JSON format
        request_data = request.get_json()

        # Step B: Extract the specific ingredients (data) needed
        high_price = request_data.get('high')
        low_price = request_data.get('low')
        current_price = request_data.get('current')
        
        # We can set default values if React doesn't send them
        n_precision = request_data.get('n', 50) 
        sensitivity = request_data.get('sensitivity', 1.0)

        # Step C: Give the ingredients to the Chef (service.py)
        # We call the function we wrote earlier
        bot_response = generate_signals(
            high_price=high_price,
            low_price=low_price,
            current_price=current_price,
            n=n_precision,
            sensitivity_percent=sensitivity
        )

        # Step D: The Waiter brings the final dish (JSON) back to the Customer
        return jsonify(bot_response), 200

    except Exception as e:
        # If something goes wrong, tell the customer
        return jsonify({"error": str(e)}), 400