#!/usr/bin/env python3
"""
InCTF 2026 Finals — Multi-Encoding Decoder
TEAM_UNFINDABLES (FIN-030)

Auto-detect and decode encoded strings through multiple layers.
Usage: python3 decoder.py "SGVsbG8gV29ybGQ="
"""
import base64, binascii, codecs, re, sys, urllib.parse

G, Y, C, R, B, N = '\033[92m', '\033[93m', '\033[96m', '\033[91m', '\033[1m', '\033[0m'

def try_decode(data, depth=0, max_depth=10):
    if depth > max_depth or not data:
        return
    prefix = "  " * depth
    if isinstance(data, bytes):
        try: data = data.decode('utf-8', errors='replace')
        except: return

    data = data.strip()
    if not data: return

    # Check for flag
    flag = re.search(r'(inctf\{[^}]+\}|flag\{[^}]+\}|CTF\{[^}]+\})', data, re.I)
    if flag:
        print(f"{prefix}{G}{B}[***] FLAG FOUND: {flag.group()}{N}")

    # Base64
    if re.match(r'^[A-Za-z0-9+/]+=*$', data) and len(data) >= 4 and len(data) % 4 <= 2:
        try:
            decoded = base64.b64decode(data).decode('utf-8', errors='replace')
            if all(32 <= ord(c) < 127 or c in '\n\r\t' for c in decoded):
                print(f"{prefix}{Y}[Base64]{N} → {decoded[:200]}")
                try_decode(decoded, depth + 1)
        except: pass

    # Base32
    if re.match(r'^[A-Z2-7]+=*$', data) and len(data) >= 8:
        try:
            decoded = base64.b32decode(data).decode('utf-8', errors='replace')
            if all(32 <= ord(c) < 127 or c in '\n\r\t' for c in decoded):
                print(f"{prefix}{Y}[Base32]{N} → {decoded[:200]}")
                try_decode(decoded, depth + 1)
        except: pass

    # Hex
    if re.match(r'^[0-9a-fA-F]+$', data) and len(data) >= 4 and len(data) % 2 == 0:
        try:
            decoded = bytes.fromhex(data).decode('utf-8', errors='replace')
            if all(32 <= ord(c) < 127 or c in '\n\r\t' for c in decoded):
                print(f"{prefix}{Y}[Hex]{N} → {decoded[:200]}")
                try_decode(decoded, depth + 1)
        except: pass

    # URL encoding
    if '%' in data:
        try:
            decoded = urllib.parse.unquote(data)
            if decoded != data:
                print(f"{prefix}{Y}[URL]{N} → {decoded[:200]}")
                try_decode(decoded, depth + 1)
        except: pass

    # ROT13
    decoded = codecs.decode(data, 'rot_13')
    if decoded != data and re.search(r'(flag|inctf|ctf)', decoded, re.I):
        print(f"{prefix}{Y}[ROT13]{N} → {decoded[:200]}")

    # Binary
    if re.match(r'^[01\s]+$', data):
        try:
            bits = data.replace(' ', '')
            chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits)-7, 8)]
            decoded = ''.join(chars)
            if all(32 <= ord(c) < 127 for c in decoded):
                print(f"{prefix}{Y}[Binary]{N} → {decoded[:200]}")
                try_decode(decoded, depth + 1)
        except: pass

    # Decimal (space-separated ASCII)
    if re.match(r'^[\d\s]+$', data) and ' ' in data:
        try:
            nums = [int(x) for x in data.split()]
            if all(32 <= n < 127 for n in nums):
                decoded = ''.join(chr(n) for n in nums)
                print(f"{prefix}{Y}[Decimal ASCII]{N} → {decoded[:200]}")
                try_decode(decoded, depth + 1)
        except: pass

    # All ROT shifts
    if depth == 0 and len(data) < 200:
        for shift in range(1, 26):
            shifted = ''.join(
                chr((ord(c) - ord('a' if c.islower() else 'A') + shift) % 26 + ord('a' if c.islower() else 'A'))
                if c.isalpha() else c for c in data
            )
            if re.search(r'(flag|inctf|ctf|the|and)', shifted, re.I):
                print(f"{prefix}{Y}[ROT{shift}]{N} → {shifted[:200]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 decoder.py \"<encoded_string>\"")
        sys.exit(1)
    data = " ".join(sys.argv[1:])
    print(f"\n{B}{C}Multi-Layer Decoder{N}")
    print(f"Input: {data[:100]}{'...' if len(data)>100 else ''}\n")
    try_decode(data)
    print()
