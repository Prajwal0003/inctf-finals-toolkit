#!/usr/bin/env python3
"""
InCTF 2026 Finals — Generic Solve Template
TEAM_UNFINDABLES (FIN-030)

Quick-start template for any challenge.
Copy this and start solving.
"""
import sys, os

# ============================================
# Challenge Info
# ============================================
CHALLENGE_NAME = "unknown"
CATEGORY = "misc"  # pwn, crypto, web, rev, forensics, misc
FLAG_FORMAT = "inctf{.*}"

# ============================================
# Solve
# ============================================
def solve():
    """Main solve logic goes here."""
    print(f"[*] Solving: {CHALLENGE_NAME} ({CATEGORY})")
    
    # --- Your code here ---
    
    flag = ""
    
    # --- End ---
    
    if flag:
        print(f"\n[+] FLAG: {flag}")
    else:
        print("[-] Flag not found yet")
    
    return flag

if __name__ == "__main__":
    solve()
