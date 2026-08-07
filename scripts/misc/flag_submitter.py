#!/usr/bin/env python3
"""
InCTF 2026 Finals — Flag Submitter
TEAM_UNFINDABLES (FIN-030)

Auto-submit flags and track solved challenges.
Configure the submission endpoint based on the CTF platform.
"""
import requests, json, os, time, re, sys

# ============================================
# Configuration (fill in at the venue)
# ============================================
CTF_URL = ""           # e.g., "http://ctf.inctf.in"
SUBMIT_ENDPOINT = ""   # e.g., "/api/v1/challenges/attempt"
TEAM_TOKEN = ""        # Auth token
FLAG_FORMAT = re.compile(r'inctf\{[^\}]+\}|InCTF\{[^\}]+\}')

SOLVED_FILE = os.path.expanduser("~/ctf/solved_flags.json")

def load_solved():
    if os.path.exists(SOLVED_FILE):
        with open(SOLVED_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_solved(solved):
    os.makedirs(os.path.dirname(SOLVED_FILE), exist_ok=True)
    with open(SOLVED_FILE, 'w') as f:
        json.dump(solved, f, indent=2)

def submit_flag(flag, challenge_name="unknown"):
    """Submit a flag to the CTF platform."""
    solved = load_solved()
    
    if flag in solved.values():
        print(f"[!] Already submitted: {flag}")
        return False

    print(f"[*] Submitting flag for '{challenge_name}': {flag}")
    
    if not CTF_URL or not SUBMIT_ENDPOINT:
        print("[!] CTF platform not configured — saving flag locally")
        solved[challenge_name] = flag
        save_solved(solved)
        print(f"[+] Saved to {SOLVED_FILE}")
        return True

    try:
        headers = {"Authorization": f"Token {TEAM_TOKEN}", "Content-Type": "application/json"}
        data = {"challenge_id": challenge_name, "submission": flag}
        r = requests.post(f"{CTF_URL}{SUBMIT_ENDPOINT}", json=data, headers=headers, timeout=10)
        
        if r.status_code == 200:
            result = r.json()
            if result.get("status") == "correct" or result.get("success"):
                print(f"[+] CORRECT! {challenge_name} solved!")
                solved[challenge_name] = flag
                save_solved(solved)
                return True
            else:
                print(f"[-] INCORRECT: {result}")
                return False
        else:
            print(f"[-] HTTP {r.status_code}: {r.text}")
            return False
    except Exception as e:
        print(f"[-] Error: {e}")
        solved[challenge_name] = flag
        save_solved(solved)
        return False

def scan_for_flags(directory="."):
    """Scan directory for strings matching flag format."""
    flags = set()
    for root, dirs, files in os.walk(directory):
        for f in files:
            try:
                filepath = os.path.join(root, f)
                with open(filepath, 'r', errors='ignore') as fh:
                    content = fh.read()
                    matches = FLAG_FORMAT.findall(content)
                    for m in matches:
                        flags.add(m)
                        print(f"[+] Found flag in {filepath}: {m}")
            except:
                pass
    return flags

if __name__ == "__main__":
    if len(sys.argv) > 1:
        flag = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        submit_flag(flag, name)
    else:
        print("Flag Submitter — TEAM_UNFINDABLES")
        print("Usage: python3 flag_submitter.py <flag> [challenge_name]")
        print("       python3 flag_submitter.py --scan [directory]")
