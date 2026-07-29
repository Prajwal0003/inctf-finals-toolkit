#!/usr/bin/env python3
"""
InCTF 2026 Finals — Hash Cracking Utilities
TEAM_UNFINDABLES (FIN-030)
"""
import hashlib, itertools, string, sys, os

HASH_FUNCS = {
    'md5': hashlib.md5, 'sha1': hashlib.sha1,
    'sha256': hashlib.sha256, 'sha512': hashlib.sha512,
}

def identify_hash(h):
    lengths = {32: 'md5', 40: 'sha1', 64: 'sha256', 128: 'sha512'}
    return lengths.get(len(h), 'unknown')

def crack_wordlist(target, hash_type='md5', wordlist=None):
    if wordlist is None:
        wordlist = os.path.expanduser('~/wordlists/rockyou.txt')
    hfunc = HASH_FUNCS.get(hash_type, hashlib.md5)
    with open(wordlist, 'r', errors='ignore') as f:
        for i, word in enumerate(f):
            word = word.strip()
            if hfunc(word.encode()).hexdigest() == target:
                print(f"[+] CRACKED: {target} = {word}")
                return word
            if i % 1000000 == 0 and i > 0:
                print(f"[*] Tried {i} words...")
    print("[-] Not found in wordlist")
    return None

def crack_bruteforce(target, hash_type='md5', charset=string.ascii_lowercase, max_len=6):
    hfunc = HASH_FUNCS.get(hash_type, hashlib.md5)
    for length in range(1, max_len + 1):
        print(f"[*] Trying length {length}...")
        for combo in itertools.product(charset, repeat=length):
            word = ''.join(combo)
            if hfunc(word.encode()).hexdigest() == target:
                print(f"[+] CRACKED: {target} = {word}")
                return word
    return None

def hash_string(s, hash_type='md5'):
    return HASH_FUNCS.get(hash_type, hashlib.md5)(s.encode()).hexdigest()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 hash_crack.py <hash> [wordlist]")
        sys.exit(1)
    target = sys.argv[1]
    ht = identify_hash(target)
    print(f"[*] Hash type: {ht}")
    wl = sys.argv[2] if len(sys.argv) > 2 else None
    crack_wordlist(target, ht, wl)
