#!/usr/bin/env python3
"""
InCTF 2026 Finals — Reverse Engineering Dynamic Cracker
TEAM_UNFINDABLES (FIN-030)

This tool helps solve "Crackme" style reverse engineering challenges 
WITHOUT needing to read Assembly code. It uses `ltrace` to run the 
program dynamically and spy on standard C library functions (like strcmp).

If the program compares your input against the real flag, this script 
will catch it in the act!

Usage: python3 rev_cracker.py ./challenge
"""
import subprocess, sys, os, re
import tempfile

G, Y, C, R, B, N = '\033[92m', '\033[93m', '\033[96m', '\033[91m', '\033[1m', '\033[0m'

def run_ltrace(binary, input_data):
    """Run binary with ltrace and feed it input_data."""
    print(f"[*] Running dynamic trace with input: '{input_data}'...")
    
    # Run ltrace -s 256 (string size) -f (follow forks) -i (instruction pointer)
    cmd = f'ltrace -s 256 -f "{binary}"'
    
    try:
        # Run with input piped to stdin
        process = subprocess.Popen(
            cmd, shell=True, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=input_data + "\n", timeout=5)
        return stderr # ltrace outputs to stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return "[!] Timeout: Program did not exit. It might be waiting for more input."
    except Exception as e:
        return str(e)

def analyze_trace(trace_output):
    """Analyze ltrace output for interesting comparisons."""
    comparisons = []
    
    # Look for strcmp, strncmp, memcmp, strcasecmp
    pattern = re.compile(r'(strn?cmp|memcmp|strcasecmp)\s*\(\s*"([^"]+)"\s*,\s*"([^"]+)"')
    
    for line in trace_output.split('\n'):
        match = pattern.search(line)
        if match:
            func = match.group(1)
            arg1 = match.group(2)
            arg2 = match.group(3)
            comparisons.append((func, arg1, arg2))
            
    return comparisons

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 rev_cracker.py <binary>")
        sys.exit(1)
        
    binary = sys.argv[1]
    if not os.path.exists(binary):
        print(f"{R}[-] File not found: {binary}{N}")
        sys.exit(1)
        
    # Make executable just in case
    os.system(f'chmod +x "{binary}"')

    print(f"\n{B}{C}{'='*60}{N}")
    print(f"  {B}Reverse Engineering Dynamic Cracker{N}")
    print(f"{B}{C}{'='*60}{N}\n")

    # We will try a few different dummy inputs. 
    # Often, the program expects the flag format.
    dummy_inputs = [
        "inctf{test_flag_12345}",
        "password123",
        "A" * 32
    ]
    
    flag_found = False

    for dummy in dummy_inputs:
        trace = run_ltrace(binary, dummy)
        comparisons = analyze_trace(trace)
        
        if comparisons:
            print(f"\n{Y}[+] Captured Library Comparisons!{N}")
            for func, arg1, arg2 in comparisons:
                print(f"  {C}{func}{N}( {B}\"{arg1}\"{N} , {B}\"{arg2}\"{N} )")
                
                # If one of the arguments looks like a flag, highlight it!
                if "inctf{" in arg1.lower() and arg1 != dummy:
                    print(f"\n{G}{B}[*] SUCCESS! THE FLAG MIGHT BE: {arg1}{N}")
                    flag_found = True
                elif "inctf{" in arg2.lower() and arg2 != dummy:
                    print(f"\n{G}{B}[*] SUCCESS! THE FLAG MIGHT BE: {arg2}{N}")
                    flag_found = True
                    
        # Check if the flag was just passed to puts/printf
        flag_match = re.search(r'inctf\{[^}]+\}', trace, re.IGNORECASE)
        if flag_match and flag_match.group(0) != dummy:
             print(f"\n{G}{B}[*] SUCCESS! SPOTTED FLAG IN MEMORY: {flag_match.group(0)}{N}")
             flag_found = True
             
    if not flag_found:
        print(f"\n{R}[-] No obvious flag comparisons found dynamically.{N}")
        print(f"    The program might be doing character-by-character checks (e.g. XOR).")
        print(f"    Try using the 'angr_template.py' for symbolic execution instead!")

if __name__ == "__main__":
    main()
