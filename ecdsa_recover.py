import ecdsa
from ecdsa.numbertheory import inverse_mod
import requests

# SECP256K1 parameters
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (Gx, Gy)

# Elliptic curve point addition and doubling
def mod_inverse(k, p):
    return inverse_mod(k, p)

def ec_add(P, Q, p):
    if P == (0, 0): return Q
    if Q == (0, 0): return P
    if P == Q:
        l = (3 * P[0]**2 + A) * mod_inverse(2 * P[1], p) % p
    else:
        l = (Q[1] - P[1]) * mod_inverse(Q[0] - P[0], p) % p
    x_r = (l**2 - P[0] - Q[0]) % p
    y_r = (l * (P[0] - x_r) - P[1]) % p
    return (x_r, y_r)

def scalar_mult(k, P, p):
    R = (0, 0)
    Q = P
    while k:
        if k & 1:
            R = ec_add(R, Q, p)
        Q = ec_add(Q, Q, p)
        k >>= 1
    return R

def diagonal_transform(pub_key):
    """Experimental transformation to find private key from public key."""
    x, y = pub_key
    return ((x - y) ** 3) % N if x > y else ((y - x) ** 3) % N


# Input: Uncompressed public key (hex format)
input_public_key = "04ee0e2a4438785f693b6d3ece91ab915f9e329c7bfa65fe68d21e8ab3ef4107d3c0d42c218d9a4f80561eb6f83a5f6644d4b47ace4adb5a123bdd287e5cfb358d"

# Extract x-coordinate
x_coord = int(input_public_key[2:66], 16)

# Initialize private key with x-coordinate
private = x_coord

for i in range(1000000000):  # Limit iterations
    public = scalar_mult(private, G, P)
    recovered_k = diagonal_transform(public)
    print(f"Iteration {i}: Private = {private}, Recovered = {recovered_k}")
    
    # Check if recovered public key matches input public key
    if scalar_mult(recovered_k, G, P) == (int(input_public_key[2:66], 16), int(input_public_key[66:], 16)):
        message = f"Success: Recovered Private Key = {recovered_k}"
        print(message)
    
        break
    
    private = recovered_k
