import requests
import random
import binascii

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
    return pow(k, p - 2, p)

def ec_add(P, Q, p):
    if P == (0, 0): return Q
    if Q == (0, 0): return P
    if P == Q:
        if P[1] == 0: return (0, 0)
        l = (3 * P[0]**2 + A) * mod_inverse(2 * P[1], p) % p
    else:
        if P[0] == Q[0]: return (0, 0)
        l = (Q[1] - P[1]) * mod_inverse(Q[0] - P[0], p) % p
    
    x_r = (l**2 - P[0] - Q[0]) % p
    y_r = (l * (P[0] - x_r) - P[1]) % p
    return (x_r, y_r)

def scalar_mult(k, P, p):
    R = (0, 0)
    Q = P
    steps = []
    
    while k > 0:
        if k & 1:
            R = ec_add(R, Q, p)
            steps.append(R[0])
        Q = ec_add(Q, Q, p)
        steps.append(Q[0])
        k >>= 1
    return R, steps

def point_to_hex(pub_point):
    if pub_point == (0, 0):
        return "00"
    # შევქმნათ შეკუმშული (Compressed) ან გაშლილი (Uncompressed) საჯარო გასაღები
    # ქვემოთ მოცემულია გაშლილი ვერსია (04 + X + Y)
    x_hex = hex(pub_point[0])[2:].zfill(64)
    y_hex = hex(pub_point[1])[2:].zfill(64)
    return f"04{x_hex}{y_hex}"

# საჯარო გასაღებების წაკითხვა ფაილიდან
try:
    with open("pubs.txt", "r") as f:
        pub_keys = {line.strip() for line in f}
except FileNotFoundError:
    pub_keys = []
    print("ყურადღება: pubs.txt ფაილი ვერ მოიძებნა.")

for input_pub_keys in pub_keys:
    if len(input_pub_keys) < 130:
        continue
        
    p_g_x = int(input_pub_keys[2:66], 16)
    p_g_y = int(input_pub_keys[66:], 16)

    private = (p_g_x + p_g_y) % (N - 1)

    # საჯარო წერტილის გენერაცია კერძო გასაღებიდან
    pub, steps = scalar_mult(private, G, P)

    # ეტაპების (steps) შემოწმება
    for step in steps:
        predict_key = ((step + (Gx + Gy)) * Gx) % N
        
        # ვამოწმებთ არის თუ არა ნაწინასწარმეტყველები გასაღები სწორი
        public, second_steps = scalar_mult(predict_key, G, P)
        public_hex = point_to_hex(public)
        
        if public_hex == input_pub_keys:
            print(f"იპოვეს დამთხვევა! კერძო გასაღებია: {hex(predict_key)}")
            break
