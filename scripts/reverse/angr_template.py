#!/usr/bin/env python3
"""
InCTF 2026 Finals — Angr Auto-Solver Template
TEAM_UNFINDABLES (FIN-030)

When standard reversing (ltrace/strings) fails because the binary 
checks the flag character-by-character (e.g. math equations, XOR), 
we use Symbolic Execution (angr) to mathematically solve for the flag.

Usage: 
1. Open the binary in Ghidra/GDB.
2. Find the address that prints "Correct!" (Success Address)
3. Find the address that prints "Wrong!" (Fail Address)
4. Update the addresses in this script and run it!
"""
import angr
import claripy
import sys
import os

G, Y, C, R, B, N = '\033[92m', '\033[93m', '\033[96m', '\033[91m', '\033[1m', '\033[0m'

def solve_binary(binary_path, success_addr, fail_addr, flag_length=32):
    print(f"\n{B}{C}{'='*60}{N}")
    print(f"  {B}Symbolic Execution Auto-Solver (angr){N}")
    print(f"{B}{C}{'='*60}{N}\n")
    
    print(f"[*] Loading binary: {binary_path}")
    # Load the binary
    project = angr.Project(binary_path, auto_load_libs=False)

    print(f"[*] Setting up symbolic flag variables (Length: {flag_length})")
    # Create symbolic variables for the flag characters
    flag_chars = [claripy.BVS(f'flag_{i}', 8) for i in range(flag_length)]
    
    # Combine them into a single symbolic string
    flag = claripy.Concat(*flag_chars + [claripy.BVV(b'\n')])

    print(f"[*] Initializing state...")
    # Create an initial state where our symbolic flag is fed to stdin
    state = project.factory.full_init_state(
        args=[binary_path],
        add_options=angr.options.unicorn,
        stdin=flag,
    )

    # Add constraints: The flag usually contains printable ASCII characters
    for k in flag_chars:
        state.solver.add(k >= 0x20) # Greater than ' '
        state.solver.add(k <= 0x7e) # Less than '~'
        
    # Optional: Force it to start with "inctf{"
    # state.solver.add(flag_chars[0] == ord('i'))
    # state.solver.add(flag_chars[1] == ord('n'))
    # ...

    print(f"[*] Setting up simulation manager...")
    simgr = project.factory.simulation_manager(state)

    print(f"[*] Exploring paths... (This might take a while)")
    print(f"    Target (Success): {hex(success_addr)}")
    print(f"    Avoid  (Fail):    {hex(fail_addr)}")

    # Tell angr to find the success address, but avoid the fail address
    simgr.explore(find=success_addr, avoid=fail_addr)

    if len(simgr.found) > 0:
        print(f"\n{G}{B}[+] PATH FOUND!{N}")
        found_state = simgr.found[0]
        
        # Evaluate the symbolic flag in the found state
        flag_val = found_state.posix.dumps(sys.stdin.fileno())
        print(f"{C}Input required to reach target:{N}")
        print(f"\n{B}{Y}>>>>> {flag_val.decode('utf-8', errors='ignore')} <<<<<{N}\n")
    else:
        print(f"\n{R}[-] Could not find a path to the success address.{N}")
        print("    Try adjusting the flag_length or checking the addresses.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: python3 angr_template.py <binary>")
        print(f"\n{Y}NOTE: You must edit this file first to set the success/fail addresses!{N}")
        sys.exit(1)
        
    binary = sys.argv[1]
    
    if not os.path.exists(binary):
        print(f"File not found: {binary}")
        sys.exit(1)

    # =========================================================================
    # EDIT THESE ADDRESSES BEFORE RUNNING!
    # Find these using Ghidra, objdump, or GDB.
    # E.g., if it's a PIE binary, usually add the base address (e.g., 0x400000)
    # =========================================================================
    SUCCESS_ADDRESS = 0x00000000 # CHANGE ME: Address of "You got the flag!"
    FAIL_ADDRESS    = 0x00000000 # CHANGE ME: Address of "Wrong password!"
    FLAG_LENGTH     = 25         # CHANGE ME: Try different lengths if unsure
    # =========================================================================

    if SUCCESS_ADDRESS == 0x00000000:
        print(f"\n{R}[!] ERROR: You haven't set the SUCCESS_ADDRESS inside the script!{N}")
        print(f"Open {sys.argv[0]} and edit the addresses at the bottom.")
        sys.exit(1)

    solve_binary(binary, SUCCESS_ADDRESS, FAIL_ADDRESS, FLAG_LENGTH)
