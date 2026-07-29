#!/usr/bin/env python3
"""
InCTF 2026 Finals — Offline Writeup Search
TEAM_UNFINDABLES (FIN-030)

COMPETITION-TIME: Searches pre-downloaded writeups LOCALLY.
No internet, no AI — just fast text search.
Rule 14: public writeups are allowed.

Usage:
    python3 writeup_search.py "buffer overflow canary"
    python3 writeup_search.py -c crypto "rsa small e"
    python3 writeup_search.py -i "given n e c, n is 512 bits"
"""
import json, os, re, sys, argparse

WRITEUP_DIR = os.path.expanduser("~/ctf-writeups")
INDEX_FILE = os.path.join(WRITEUP_DIR, "index.json")
G, Y, C, R, B, N = '\033[92m', '\033[93m', '\033[96m', '\033[91m', '\033[1m', '\033[0m'

CHALLENGE_PATTERNS = {
    "pwn": {
        "buffer overflow": ["buffer", "overflow", "bof", "stack smash"],
        "format string": ["format", "printf", "%p", "%n"],
        "heap": ["heap", "malloc", "free", "tcache", "fastbin", "uaf"],
        "rop": ["rop", "gadget", "return oriented", "ret2libc"],
    },
    "crypto": {
        "rsa": ["rsa", "modulus", "exponent", "factoring"],
        "aes": ["aes", "cbc", "ecb", "padding oracle"],
        "xor": ["xor", "key reuse", "repeating key"],
        "ecc": ["elliptic", "ecdsa", "curve"],
        "lattice": ["lattice", "lll", "coppersmith"],
    },
    "web": {
        "sqli": ["sql", "injection", "union select"],
        "xss": ["xss", "cross-site", "reflected"],
        "ssti": ["ssti", "template", "jinja"],
        "ssrf": ["ssrf", "server-side request"],
        "deserial": ["deserializ", "pickle", "unserialize"],
    },
    "forensics": {
        "stego": ["steg", "hidden", "lsb"],
        "pcap": ["pcap", "wireshark", "packet"],
        "memory": ["volatility", "memory dump", "memdump"],
    },
    "reverse": {
        "static": ["reverse", "ghidra", "decompil"],
        "dynamic": ["debug", "gdb", "strace"],
        "angr/z3": ["angr", "symbolic", "z3", "constraint"],
    },
}

def load_index():
    if not os.path.exists(INDEX_FILE):
        print(f"{R}[-] Run download_writeups.py first!{N}")
        sys.exit(1)
    with open(INDEX_FILE) as f:
        return json.load(f)

def search_index(index, query, category=None, max_r=10):
    terms = query.lower().split()
    results = []
    for e in index:
        if category and e["category"] != category:
            continue
        score = 0
        for t in terms:
            if t in e["title"].lower(): score += 10
            if any(t in k for k in e.get("keywords", [])): score += 7
            if t in e["preview"].lower(): score += 3
        if score > 0:
            results.append((score, e))
    results.sort(key=lambda x: -x[0])
    return results[:max_r]

def search_fulltext(query, max_r=10):
    terms = query.lower().split()
    results = []
    for root, _, files in os.walk(WRITEUP_DIR):
        for fn in files:
            if not fn.endswith((".md", ".txt", ".py")): continue
            fp = os.path.join(root, fn)
            try:
                content = open(fp, "r", errors="replace").read()
                cl = content.lower()
                score = sum(cl.count(t) for t in terms)
                if score > 0:
                    ctx = ""
                    for t in terms:
                        i = cl.find(t)
                        if i >= 0:
                            ctx = "..." + content[max(0,i-80):i+len(t)+80].replace("\n"," ") + "..."
                            break
                    results.append((score, fp, ctx))
            except: continue
    results.sort(key=lambda x: -x[0])
    return results[:max_r]

def identify_type(desc):
    dl = desc.lower()
    matches = []
    for cat, techs in CHALLENGE_PATTERNS.items():
        for tech, kws in techs.items():
            s = sum(1 for k in kws if k in dl)
            if s > 0: matches.append((s, cat, tech))
    matches.sort(key=lambda x: -x[0])
    if matches:
        print(f"\n{B}{C}Challenge Type Identification{N}\n{'='*50}")
        for s, cat, tech in matches[:5]:
            print(f"  {Y}[{cat}]{N} → {B}{tech}{N} (confidence: {'█'*s}{'░'*(5-s)})")
        print(f"\n  {G}Most likely: {B}{matches[0][1]}/{matches[0][2]}{N}")
    return matches[0] if matches else (0, None, None)

def main():
    p = argparse.ArgumentParser(description="Offline Writeup Search")
    p.add_argument("query", nargs="*")
    p.add_argument("-c", "--category", choices=["pwn","crypto","web","reverse","forensics","misc"])
    p.add_argument("-i", "--identify", action="store_true", help="Identify challenge type")
    p.add_argument("-f", "--fulltext", action="store_true", help="Full-text search")
    args = p.parse_args()
    if not args.query:
        p.print_help()
        return
    q = " ".join(args.query)
    if args.identify:
        identify_type(q)
    idx = load_index()
    ir = search_index(idx, q, args.category)
    fr = search_fulltext(q) if args.fulltext or not ir else []
    print(f"\n{B}{C}{'='*60}{N}\n  Results for: {Y}{q}{N}\n{B}{C}{'='*60}{N}")
    for i,(s,e) in enumerate(ir,1):
        print(f"\n  {B}{i}. {e['title']}{N} [{e['category']}] (score:{s})")
        if e.get("keywords"): print(f"     Tags: {', '.join(e['keywords'][:6])}")
        print(f"     {C}→ {e['path']}{N}")
    for i,(s,fp,ctx) in enumerate(fr,1):
        print(f"\n  {B}{i}. {os.path.basename(fp)}{N} (hits:{s})")
        if ctx: print(f"     {ctx[:150]}")
        print(f"     {C}→ {fp}{N}")
    print(f"\n{G}[+] {len(ir)+len(fr)} results{N}\n")

if __name__ == "__main__":
    main()
