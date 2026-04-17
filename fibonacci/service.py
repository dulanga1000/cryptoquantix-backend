
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
        "dp_time": dp_time,
        "matrix_time": matrix_time
    }


if __name__ == "__main__":
    print(fibonacci_dp(10))  # expected: 55
    print("Fibonacci(10) =", fibonacci_matrix(10))        # Expected: 55
    print("Fibonacci(50) =", fibonacci_matrix(50))       # Expected: 12586269025
    print("Fibonacci(100) =", fibonacci_matrix(100))     # Expected: 354224848179261915075
    print(compare_methods(1000))
