# 🔐 CTF CRYPTOGRAPHY MASTER BIBLE
### InCTF 2026 Finals — Zero to Hero Reference (Rule 14 Offline Compliant)

---

## 1. RSA Attacks & Mathematical Recipes

RSA Basics: $n = p \times q$, $\phi(n) = (p-1)(q-1)$, $e \cdot d \equiv 1 \pmod{\phi(n)}$, $c = m^e \pmod n$, $m = c^d \pmod n$.

### 1. Small Public Exponent ($e = 3$ and $m^e < n$):
If the message $m$ is small and not padded, $m = \sqrt[e]{c}$ (integer root).
```python
import gmpy2
from Crypto.Util.number import long_to_bytes
m, exact = gmpy2.iroot(c, e)
if exact:
    print(long_to_bytes(m))
```

### 2. Fermat's Factorization ($p$ and $q$ are very close):
When $p \approx q$, $n = a^2 - b^2 = (a-b)(a+b)$.
```python
import gmpy2
from Crypto.Util.number import long_to_bytes

def fermat(n):
    a = gmpy2.isqrt(n)
    if a * a < n:
        a += 1
    while True:
        b2 = a * a - n
        if gmpy2.is_square(b2):
            b = gmpy2.isqrt(b2)
            return int(a - b), int(a + b)
        a += 1

p, q = fermat(n)
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
print(long_to_bytes(pow(c, d, n)))
```

### 3. Wiener's Attack (Small Private Exponent $d < \frac{1}{3} n^{1/4}$):
When $d$ is very small, use continued fractions of $\frac{e}{n}$ to recover $d$.
Use `from scripts.crypto.rsa_toolkit import rsa_wiener` or `owiener.attack(e, n)`.

### 4. Common Modulus Attack (Same $m$ encrypted with $e_1, e_2$ and $\gcd(e_1, e_2) = 1$ on same $n$):
```python
from Crypto.Util.number import long_to_bytes
def egcd(a, b):
    if a == 0: return (b, 0, 1)
    g, y, x = egcd(b % a, a)
    return (g, x - (b // a) * y, y)

def common_modulus(c1, c2, e1, e2, n):
    g, s1, s2 = egcd(e1, e2)
    if s1 < 0:
        c1 = pow(c1, -1, n)
        s1 = -s1
    if s2 < 0:
        c2 = pow(c2, -1, n)
        s2 = -s2
    m = (pow(c1, s1, n) * pow(c2, s2, n)) % n
    return long_to_bytes(m)
```

---

## 2. AES (Advanced Encryption Standard) Attacks

### 1. ECB Byte-at-a-Time (Electronic Codebook):
In ECB, identical 16-byte plaintext blocks produce identical ciphertext blocks.
- **Attack:** Send 15 `'A'`s. The oracle encrypts `'A'*15 + flag[0]`.
- Brute-force all 256 characters for the 16th byte until the block matches!

### 2. CBC Bit-Flipping Attack:
In CBC mode, $P_2 = D(C_2) \oplus C_1$. Modifying byte $i$ in $C_1$ flips the exact same bit in $P_2$!
```python
# To change "user=guest" to "user=admin":
# ciphertext is modified before sending to server
cipher_byte_array[target_index] ^= ord('g') ^ ord('a')
```

### 3. CBC Padding Oracle:
If server returns "Padding Error" vs "Invalid Signature/OK", you can decrypt any ciphertext byte-by-byte without the key!
Use: `python3 ~/ctf-scripts/crypto/aes_oracle.py`

---

## 3. XOR & Stream Ciphers

### 1. Single-Byte XOR:
```python
cipher = bytes.fromhex("...")
for k in range(256):
    pt = bytes([b ^ k for b in cipher])
    if b"inctf{" in pt.lower() or b"flag{" in pt.lower():
        print(f"Key: {k} -> {pt}")
```

### 2. Multi-Byte Repeating XOR (Crib Dragging):
If you know the flag starts with `inctf{`:
```python
cipher = bytes.fromhex("...")
known = b"inctf{"
key_leak = bytes([c ^ k for c, k in zip(cipher, known)])
print("Leaked key prefix:", key_leak)
```

---

## 4. Hash Cracking Cheatsheet (Hashcat & John)

| Hash Type | Example Length | Hashcat Mode (`-m`) | John Format |
|---|---|---|---|
| **MD5** | 32 hex chars | `-m 0` | `--format=raw-md5` |
| **SHA-1** | 40 hex chars | `-m 100` | `--format=raw-sha1` |
| **SHA-256** | 64 hex chars | `-m 1400` | `--format=raw-sha256` |
| **SHA-512** | 128 hex chars | `-m 1700` | `--format=raw-sha512` |
| **NTLM (Windows)**| 32 hex chars | `-m 1000` | `--format=nt` |
| **JWT HMAC-SHA256**| `eyJ...` | `-m 16500` | `--format=HMAC-SHA256` |

```bash
# Hashcat with rockyou:
hashcat -m 0 -a 0 target_hash.txt /usr/share/wordlists/rockyou.txt

# John with wordlist & rules:
john target_hash.txt --wordlist=/usr/share/wordlists/rockyou.txt --rules
```
