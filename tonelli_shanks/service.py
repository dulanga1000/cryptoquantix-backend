import hashlib
import random

# --- TONELLI-SHANKS ALGORITHM (Question 2) ---

def legendre_symbol(a, p):
    """Computes the Legendre symbol a|p using Euler's criterion."""
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls

def tonelli_shanks(n, p):
    """
    Solves the quadratic congruence x^2 = n (mod p).
    Returns (root, steps_list) so the frontend can display the proof.
    """
    n = n % p
    steps = []
    
    if n == 0:
        return 0, ["n is 0, root is 0"]
    if p == 2:
        return n, ["p is 2, root is n mod 2"]
    if legendre_symbol(n, p) != 1:
        return None, ["Legendre symbol is not 1. No square root exists."]

    # Step 1: Factor p - 1 = Q * 2^S
    Q = p - 1
    S = 0
    while Q % 2 == 0:
        Q //= 2
        S += 1
    steps.append(f"Factored p-1 as Q*2^S: Q={Q}, S={S}")

    # Step 2: Find a quadratic non-residue z
    z = 2
    while legendre_symbol(z, p) != -1:
        z += 1
    steps.append(f"Found quadratic non-residue z={z}")

    # Step 3: Initialize variables
    M = S
    c = pow(z, Q, p)
    t = pow(n, Q, p)
    R = pow(n, (Q + 1) // 2, p)
    steps.append(f"Initialized: M={M}, c={c}, t={t}, R={R}")

    # Step 4: Loop
    while t != 0 and t != 1:
        t2i = t
        i = 0
        for i in range(1, M):
            t2i = (t2i * t2i) % p
            if t2i == 1:
                break
        
        steps.append(f"Loop iteration: Found t^(2^i) = 1 at i={i}")
        
        if i == M:
            return None, steps # No solution found (shouldn't happen if prime)

        # Update variables
        b = pow(c, 1 << (M - i - 1), p)
        M = i
        c = (b * b) % p
        t = (t * c) % p
        R = (R * b) % p
        steps.append(f"Updated: M={M}, c={c}, t={t}, R={R}")

    return R, steps

# --- ELLIPTIC CURVE CRYPTOGRAPHY (ECC) ---
# Using secp256k1 parameters (y^2 = x^3 + 7)

P_CURVE = 2**256 - 2**32 - 977 # The prime modulus
N_CURVE = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 # Order
A_CURVE = 0
B_CURVE = 7
G_X = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
G_Y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G_POINT = (G_X, G_Y)

def mod_inverse(k, p):
    """Returns the modular inverse of k mod p."""
    if k == 0:
        raise ZeroDivisionError('division by zero')
    return pow(k, p - 2, p)

def ecc_add(p1, p2):
    """Point addition on the elliptic curve."""
    if p1 is None: return p2
    if p2 is None: return p1

    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2 and y1 != y2:
        return None

    if x1 == x2:
        # Point doubling
        s = ((3 * x1 * x1 + A_CURVE) * mod_inverse(2 * y1, P_CURVE)) % P_CURVE
    else:
        # Point addition
        s = ((y2 - y1) * mod_inverse(x2 - x1, P_CURVE)) % P_CURVE

    x3 = (s * s - x1 - x2) % P_CURVE
    y3 = (s * (x1 - x3) - y1) % P_CURVE
    return (x3, y3)

def ecc_multiply(k, point):
    """Scalar multiplication (k * Point) using double-and-add."""
    result = None
    addend = point

    while k:
        if k & 1:
            result = ecc_add(result, addend)
        addend = ecc_add(addend, addend)
        k >>= 1

    return result

def generate_keypair():
    """Generates a private and public key."""
    private_key = random.SystemRandom().randrange(1, N_CURVE)
    public_key = ecc_multiply(private_key, G_POINT)
    return private_key, public_key

def hash_message(message: str):
    """Hashes a message using SHA-256."""
    return int(hashlib.sha256(message.encode('utf-8')).hexdigest(), 16)

def sign_message(private_key, message):
    """Signs a message using simplified ECDSA."""
    z = hash_message(message)
    k = random.SystemRandom().randrange(1, N_CURVE)
    x1, y1 = ecc_multiply(k, G_POINT)
    r = x1 % N_CURVE
    if r == 0: return sign_message(private_key, message)
    
    s = (mod_inverse(k, N_CURVE) * (z + r * private_key)) % N_CURVE
    if s == 0: return sign_message(private_key, message)
    
    return (r, s)

def verify_signature(public_key, message, signature):
    """Verifies an ECDSA signature."""
    r, s = signature
    if not (1 <= r < N_CURVE and 1 <= s < N_CURVE):
        return False
        
    z = hash_message(message)
    w = mod_inverse(s, N_CURVE)
    
    u1 = (z * w) % N_CURVE
    u2 = (r * w) % N_CURVE
    
    point1 = ecc_multiply(u1, G_POINT)
    point2 = ecc_multiply(u2, public_key)
    x1, y1 = ecc_add(point1, point2)
    
    return (x1 % N_CURVE) == r