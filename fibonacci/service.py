
import time

def fibonacci_dp(n):
    if n <= 1:
        return n

    dp = [0, 1]

    for i in range(2, n + 1):
        dp.append(dp[i-1] + dp[i-2])


    return dp[n]

#matrix multiplication function for 2x2 matrices

def multiply_matrices(m1, m2):

    a = m1[0][0] * m2[0][0] + m1[0][1] * m2[1][0]
    b = m1[0][0] * m2[0][1] + m1[0][1] * m2[1][1]
    c = m1[1][0] * m2[0][0] + m1[1][1] * m2[1][0]
    d = m1[1][0] * m2[0][1] + m1[1][1] * m2[1][1]
    
    return [[a, b], [c, d]]



def power_matrix(mat, n):
    
    if n == 1:
        return mat
    half = power_matrix(mat, n // 2) 
     
    half_squared = multiply_matrices(half, half)
    
    if n % 2 != 0:
        base_matrix = [[1, 1], [1, 0]]
        return multiply_matrices(half_squared, base_matrix)
    
    return half_squared



def fibonacci_matrix(n):
    
   
    if n <= 0: return 0
    if n == 1: return 1
    
    
    base_matrix = [[1, 1], [1, 0]]
    result_matrix = power_matrix(base_matrix, n - 1)
    return result_matrix[0][0]

def compare_methods(n):
    start = time.time()
    dp_result = fibonacci_dp(n)
    dp_time = time.time() - start

    start = time.time()
    matrix_result = fibonacci_matrix(n)
    matrix_time = time.time() - start

    return {
        "n": n,
        "dp_result": dp_result,
        "dp_time": dp_time,
        "matrix_result": matrix_result,
        "matrix_time": matrix_time
    }
#  CORE LOGIC (Trading Levels & Ratios)

def get_fibonacci_trading_ratios(n):
    """Calculates Golden Ratios dynamically based on precision N"""
    f1 = fibonacci_matrix(n)
    f2 = fibonacci_matrix(n + 1)
    f3 = fibonacci_matrix(n + 2)
    f4 = fibonacci_matrix(n + 3)

    return {
        "23.6%": f1 / f4,
        "38.2%": f1 / f3,
        "50.0%": 0.5,
        "61.8%": f1 / f2
    }

def calculate_dynamic_price_levels(high_price, low_price, n):
    """Generates price levels based on data provided by the frontend"""
    if high_price <= low_price:
        return {"error": "High Price must be greater than Low Price!"}
    
    if n > 1000:
        n = 1000 # Memory limit to prevent excessive resource usage

    ratios = get_fibonacci_trading_ratios(n)
    price_diff = high_price - low_price
    
    return {
        "high_0": round(high_price, 3),
        "sell_23_6": round(high_price - (price_diff * ratios["23.6%"]), 3),
        "sell_38_2": round(high_price - (price_diff * ratios["38.2%"]), 3),
        "hold_50_0": round(high_price - (price_diff * ratios["50.0%"]), 3),
        "buy_61_8": round(high_price - (price_diff * ratios["61.8%"]), 3),
        "low_100": round(low_price, 3)
    }


# DECISION part 

def generate_signals(high_price, low_price, current_price, n=50, sensitivity_percent=1.0):
    """
    Generates automated Buy/Sell/Hold signals based on the current price.
    sensitivity_percent: Triggers signal when price is within this percentage (e.g., 1.0%)
    """
    # 1. Retrieve calculated levels
    levels = calculate_dynamic_price_levels(high_price, low_price, n)
    
    if "error" in levels:
        return levels # Return immediately if there's an error

    buy_level = levels["buy_61_8"]
    sell_level = levels["sell_23_6"]

    # 2. Calculate distances from the current price
    distance_to_buy = abs(current_price - buy_level)
    distance_to_sell = abs(current_price - sell_level)

    # 3. Create a Dynamic Threshold (Scales automatically for any coin)
    buffer_zone = current_price * (sensitivity_percent / 100)

    # 4. Decision Logic
    if distance_to_buy <= buffer_zone:
        action = "BUY"
        message = f"Price is at a strong Support zone (${buy_level}). This is an optimal BUY opportunity."

    elif distance_to_sell <= buffer_zone:
        action = "SELL"
        message = f"Price has reached a Resistance zone (${sell_level}). Good time to TAKE PROFIT (SELL)."

    else:
        action = "HOLD"
        message = "Price is in an intermediate zone. Wait for a better setup (HOLD)."

    # 5. Send final payload to the Frontend
    return {
        "current_price": current_price,
        "action": action,
        "buy_level": buy_level,
        "sell_level": sell_level,
        "distance_to_buy": round(distance_to_buy, 3),
        "distance_to_sell": round(distance_to_sell, 3),
        "buffer_zone": round(buffer_zone, 3),
        "levels": levels, # Includes all levels for chart plotting
        "message": message
    }

 # TESTING the Fibonacci functions and the CryptoQuantix Bot logic
if __name__ == "__main__":
    import json
    print(fibonacci_dp(10))  # expected: 55
    print("Fibonacci(10) =", fibonacci_matrix(10))        # Expected: 55
    print("Fibonacci(50) =", fibonacci_matrix(50))       # Expected: 12586269025
    print("Fibonacci(100) =", fibonacci_matrix(100))     # Expected: 354224848179261915075
    print(compare_methods(1000))

    print("--- Testing CryptoQuantix Bot ---")
    
    
    test_high = 800000
    test_low = 600000
    
    test_current = 650000


    result = generate_signals(
        high_price=test_high, 
        low_price=test_low, 
        current_price=test_current, 
        n=50, 
        sensitivity_percent=1.0
    )

    print(json.dumps(result, indent=4, ensure_ascii=False))