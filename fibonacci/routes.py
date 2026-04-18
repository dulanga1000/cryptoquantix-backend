
from flask import jsonify, request

from . import fibonacci_bp 
from .service import compare_methods, generate_signals 


#  Algorithm Performance Test (Compare DP vs Matrix)

@fibonacci_bp.route('/compare', methods=['POST'])
def test_algorithm_performance():
 
    try:
        request_data = request.get_json()
        n_value = request_data.get('n', 100) 

        performance_results = compare_methods(n_value)

        formatted_response = {
            "n": performance_results["n"],
            "dp_time_seconds": performance_results["dp_time"],
            "matrix_time_seconds": performance_results["matrix_time"],
        
            "dp_result_value": str(performance_results["dp_result"]), 
            "matrix_result_value": str(performance_results["matrix_result"])
        }

        return jsonify(formatted_response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

#  Define the exact path (URL) the Waiter is listening to
@fibonacci_bp.route('/calculate', methods=['POST'])
def calculate_trading_levels():
 
    
    try:
    
        request_data = request.get_json()

        
        high_price = request_data.get('high')
        low_price = request_data.get('low')
        current_price = request_data.get('current')
        
        
        n_precision = request_data.get('n', 50) 
        sensitivity = request_data.get('sensitivity', 1.0)

    
        bot_response = generate_signals(
            high_price=high_price,
            low_price=low_price,
            current_price=current_price,
            n=n_precision,
            sensitivity_percent=sensitivity
        )

        return jsonify(bot_response), 200

    except Exception as e:
        
        return jsonify({"error": str(e)}), 400