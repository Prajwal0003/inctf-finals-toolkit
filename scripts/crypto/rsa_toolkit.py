#!/usr/bin/env python3
"""
InCTF 2026 Finals — RSA Attack Toolkit
TEAM_UNFINDABLES (FIN-030)

Multi-attack RSA solver for CTF challenges.
Usage: python3 rsa_toolkit.py
"""
from Crypto.PublicKey import RSA
from Crypto.Util.number import *
import gmpy2
import sys
import itertools

# ============================================
# Core RSA Functions
# ============================================

def factordb_local(n):
    """Try basic factorization methods."""
    factors = []

    # Trial division (small primes)
    for p in range(2, 100000):
        while n % p == 0:
            factors.append(p)
            n //= p
    if n > 1:
        factors.append(n)
    return factors


def fermat_factor(n, max_iter=1000000):
    """Fermat factorization — works when p and q are close."""
    a = gmpy2.isqrt(n) + 1
    b2 = a * a - n
    for _ in range(max_iter):
        if gmpy2.is_square(b2):
            b = gmpy2.isqrt(b2)
            p = int(a + b)
            q = int(a - b)
            if p * q == n:
                return (p, q)
        a += 1
        b2 = a * a - n
    return None


def wiener_attack(e, n):
    """Wiener's attack — works when d is small (d < N^0.25)."""
    def continued_fraction(num, den):
        cf = []
        while den:
            q, r = divmod(num, den)
            cf.append(q)
            num, den = den, r
        return cf

    def convergents(cf):
        convs = []
        for i in range(len(cf)):
            if i == 0:
                h, k = cf[0], 1
            elif i == 1:
                h = cf[1] * cf[0] + 1
                k = cf[1]
            else:
                h = cf[i] * convs[-1][0] + convs[-2][0]
                k = cf[i] * convs[-1][1] + convs[-2][1]
            convs.append((h, k))
        return convs

    cf = continued_fraction(e, n)
    convs = convergents(cf)

    for k, d in convs:
        if k == 0:
            continue
        phi_candidate = (e * d - 1) // k
        # Check if phi_candidate is valid
        b = n - phi_candidate + 1
        discriminant = b * b - 4 * n
        if discriminant >= 0:
            sqrt_disc = gmpy2.isqrt(discriminant)
            if sqrt_disc * sqrt_disc == discriminant:
                p = (b + sqrt_disc) // 2
                q = (b - sqrt_disc) // 2
                if p * q == n:
                    return int(d)
    return None


def hastad_broadcast(ciphertexts, moduli, e=3):
    """Hastad's broadcast attack — same message, different moduli, small e."""
    from functools import reduce

    def chinese_remainder_theorem(remainders, moduli):
        N = reduce(lambda a, b: a * b, moduli)
        result = 0
        for r, m in zip(remainders, moduli):
            Ni = N // m
            Mi = int(gmpy2.invert(Ni, m))
            result += r * Ni * Mi
        return result % N

    if len(ciphertexts) < e:
        print(f"Need at least {e} ciphertexts for e={e}")
        return None

    x = chinese_remainder_theorem(ciphertexts[:e], moduli[:e])
    m, exact = gmpy2.iroot(x, e)
    if exact:
        return int(m)
    return None


def common_modulus_attack(c1, c2, e1, e2, n):
    """Common modulus attack — same n, same plaintext, different e."""
    g, s1, s2 = gmpy2.gcdext(e1, e2)
    if g != 1:
        print("e1 and e2 are not coprime!")
        return None

    s1, s2 = int(s1), int(s2)

    if s1 < 0:
        c1 = int(gmpy2.invert(c1, n))
        s1 = -s1
    if s2 < 0:
        c2 = int(gmpy2.invert(c2, n))
        s2 = -s2

    m = (pow(c1, s1, n) * pow(c2, s2, n)) % n
    return m


def small_e_attack(c, e, n):
    """Small e attack — when m^e < n (no modular reduction)."""
    m, exact = gmpy2.iroot(c, e)
    if exact:
        return int(m)

    # Try with multiples of n
    for k in range(1, 1000):
        m, exact = gmpy2.iroot(c + k * n, e)
        if exact:
            return int(m)
    return None


def decrypt_rsa(c, d, n):
    """Standard RSA decryption."""
    m = pow(c, d, n)
    return long_to_bytes(m)


def solve_from_factors(c, e, n, p, q):
    """Decrypt given p, q factors."""
    phi = (p - 1) * (q - 1)
    d = int(gmpy2.invert(e, phi))
    m = pow(c, d, n)
    return long_to_bytes(m)


# ============================================
# Auto-Solver
# ============================================

def auto_solve(n, e, c):
    """Try all known attacks automatically."""
    print(f"\n{'='*60}")
    print(f"  RSA Auto-Solver")
    print(f"  n = {n} ({n.bit_length()} bits)")
    print(f"  e = {e}")
    print(f"  c = {c}")
    print(f"{'='*60}\n")

    # 1. Small e
    print("[*] Trying small e attack...")
    m = small_e_attack(c, e, n)
    if m:
        plaintext = long_to_bytes(m)
        print(f"[+] SUCCESS! Plaintext: {plaintext}")
        return plaintext

    # 2. Wiener
    if e > n // 3:
        print("[*] Trying Wiener's attack (large e)...")
        d = wiener_attack(e, n)
        if d:
            plaintext = decrypt_rsa(c, d, n)
            print(f"[+] SUCCESS! d = {d}")
            print(f"[+] Plaintext: {plaintext}")
            return plaintext

    # 3. Fermat
    print("[*] Trying Fermat factorization...")
    result = fermat_factor(n, max_iter=100000)
    if result:
        p, q = result
        print(f"[+] Factors found! p = {p}, q = {q}")
        plaintext = solve_from_factors(c, e, n, p, q)
        print(f"[+] Plaintext: {plaintext}")
        return plaintext

    # 4. Small factors
    print("[*] Trying trial division...")
    factors = factordb_local(n)
    if len(factors) >= 2 and all(f < n for f in factors):
        print(f"[+] Factors: {factors}")
        # Multi-prime RSA
        from functools import reduce
        phi = reduce(lambda a, b: a * b, [f - 1 for f in factors])
        d = int(gmpy2.invert(e, phi))
        plaintext = decrypt_rsa(c, d, n)
        print(f"[+] Plaintext: {plaintext}")
        return plaintext

    print("[-] All automatic attacks failed.")
    print("[*] Try: factordb.com, SageMath, or challenge-specific attacks")
    return None


if __name__ == "__main__":
    print("RSA Attack Toolkit — TEAM_UNFINDABLES")
    print("Import and use: from rsa_toolkit import *")
    print("\nAvailable attacks:")
    print("  auto_solve(n, e, c)          — Try all attacks")
    print("  fermat_factor(n)             — Close primes")
    print("  wiener_attack(e, n)          — Small d")
    print("  hastad_broadcast(cs, ns, e)  — Broadcast attack")
    print("  common_modulus_attack(...)   — Same n, diff e")
    print("  small_e_attack(c, e, n)      — m^e < n")
    print("  solve_from_factors(c,e,n,p,q) — Direct decrypt")

    # Example usage (uncomment and fill in values):
    # n = 0x...
    # e = 65537
    # c = 0x...
    # auto_solve(n, e, c)
