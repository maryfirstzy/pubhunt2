import ecdsa
from ecdsa.numbertheory import inverse_mod
import requests
import random

# SECP256K1 პარამეტრები
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (Gx, Gy)

# ელიფსური მრუდის ოპერაციები
def mod_inverse(k, p):
    return inverse_mod(k, p)

def ec_add(P, Q, p):
    if P == (0, 0): return Q
    if Q == (0, 0): return P
    if P == Q:
        if P[1] == 0: return (0, 0)
        l = (3 * P[0]**2 + A) * mod_inverse(2 * P[1], p) % p
    else:
        if P[0] == Q[0]: return (0, 0)  # წერტილების განუსაზღვრელი ჯამი
        l = (Q[1] - P[1]) * mod_inverse(Q[0] - P[0], p) % p
    x_r = (l**2 - P[0] - Q[0]) % p
    y_r = (l * (P[0] - x_r) - P[1]) % p
    return (x_r, y_r)

def scalar_mult(k, P, p):
    R = (0, 0)
    Q = P
    un_modified_k = k
    steps = []
    while k > 0:
        if k & 1:
            R = ec_add(R, Q, p)
            steps.append(R[0] + un_modified_k)
        Q = ec_add(Q, Q, p)
        steps.append(Q[0] + un_modified_k)
        k >>= 1
    return R, steps

# საჯარო გასაღებების წაკითხვა ფაილიდან
# დატოვებულია კომენტარად სანამ ფაილს შექმნით
"""
with open("pubs.txt", "r") as f:
    pub_keys = {line.strip() for line in f}
"""

# სიმულაციისთვის უბრალოდ ვქმნით 1 გასაღებს
pub_keys = ["e0a8b039282faf6fe0fd769cfbc4b6b4cf8758ba68220eac420e32b91ddfa673"]

for input_pub_keys in pub_keys:
    # `hex_string` და X კოორდინატის დამუშავება
    hex_string_x = "0xe0a8b039282faf6fe0fd769cfbc4b6b4cf8758ba68220eac420e32b91ddfa673"
    p_g_x = int(hex_string_x[2:66], 16)
    
    # p_g_y ცვლადი არ გქონდათ, ვიყენებთ Gy-ს (შეგიძლიათ შეცვალოთ საჭიროებისამებრ)
    p_g_y = Gy 

    private = (p_g_x + p_g_y) % (N - 1)

    # საჯარო გასაღებისა და ნაბიჯების გენერირება X-დან
    pub, steps = scalar_mult(private, G, P)

    # გამოვთვალოთ პროგნოზირებული გასაღები თითოეული ნაბიჯისთვის
    for step in steps:
        predict_key = ((step + (Gx + Gy)) * Gx) % N
        # დაბეჭდვის ლოგიკა (კომენტარი მოიხსენით დასაბეჭდად)
        # print(predict_key)
