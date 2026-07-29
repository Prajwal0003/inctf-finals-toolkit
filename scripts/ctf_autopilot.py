#!/usr/bin/env python3
"""
InCTF 2026 Finals — CTF Autopilot (Zero False-Positive Auto-Solver)
TEAM_UNFINDABLES (FIN-030)

This tool attempts to SOLVE challenges automatically without any AI.
It uses deterministic patterns, extractions, and algorithms to find flags.
If it prints a flag, it is 100% verified (matches the flag regex).

Usage: python3 ctf_autopilot.py <file_or_directory>
"""
import os, sys, re, subprocess, tempfile, shutil
from pathlib import Path

# Try to import our own tools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from crypto.rsa_toolkit import auto_solve as rsa_auto_solve
    from misc.decoder import try_decode
except:
    pass

FLAG_REGEX = re.compile(r'(inctf\{[^{}]+\}|InCTF\{[^{}]+\}|flag\{[^{}]+\})', re.IGNORECASE)

G, Y, C, R, B, N = '\033[92m', '\033[93m', '\033[96m', '\033[91m', '\033[1m', '\033[0m'

def run(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=cwd)
        return r.stdout + r.stderr
    except:
        return ""

def check_for_flag(text, source):
    """Zero false-positive check for flags."""
    if not isinstance(text, str):
        try:
            text = text.decode('utf-8', errors='ignore')
        except:
            return False
            
    matches = FLAG_REGEX.findall(text)
    if matches:
        for match in matches:
            print(f"\n{B}{G}['*'] AUTOPILOT SUCCESS! FLAG FOUND!{N}")
            print(f"{C}Source: {source}{N}")
            print(f"{B}{Y}>>>>> {match} <<<<<{N}\n")
        return True
    return False

def auto_solve_crypto(filepath, content):
    """Automatically extract n, e, c, p, q and solve RSA."""
    print(f"[*] Autopilot: Analyzing crypto variables in {filepath}...")
    
    # Extract variable assignments
    vars_found = {}
    lines = content.split('\n')
    for line in lines:
        match = re.match(r'^\s*([a-zA-Z_]+)\s*=\s*(0x[0-9a-fA-F]+|\d+)\s*$', line)
        if match:
            var_name = match.group(1).lower()
            val_str = match.group(2)
            try:
                vars_found[var_name] = int(val_str, 16) if val_str.startswith('0x') else int(val_str)
            except:
                pass
                
    if 'n' in vars_found and 'e' in vars_found and 'c' in vars_found:
        print(f"  [+] Extracted RSA params: n, e, c")
        try:
            pt = rsa_auto_solve(vars_found['n'], vars_found['e'], vars_found['c'])
            if pt:
                if check_for_flag(pt, f"RSA Auto-Solve ({filepath})"):
                    return True
        except Exception as e:
            print(f"  [-] RSA Solver error: {e}")
            
    return False

def auto_solve_file(filepath):
    """Apply all auto-solve techniques to a single file."""
    if not os.path.isfile(filepath):
        return False
        
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read()
    except:
        return False
        
    # 1. Direct Regex (Plaintext flag)
    if check_for_flag(raw_data, f"Plaintext in {filepath}"):
        return True
        
    # 2. Check if it's a crypto text file
    if filepath.endswith('.txt') or filepath.endswith('.py') or filepath.endswith('.out'):
        try:
            text_content = raw_data.decode('utf-8')
            if auto_solve_crypto(filepath, text_content):
                return True
        except:
            pass

    # 3. Base64/Encoded extraction
    # Find all base64-like strings longer than 20 chars
    b64_strings = re.findall(rb'[A-Za-z0-9+/]{20,}={0,2}', raw_data)
    import base64
    for b in b64_strings:
        try:
            decoded = base64.b64decode(b)
            if check_for_flag(decoded, f"Base64 string in {filepath}"):
                return True
        except:
            pass

    # 4. Binwalk auto-extraction
    print(f"[*] Autopilot: Running binwalk extraction on {filepath}...")
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy(filepath, tmpdir)
        base_file = os.path.basename(filepath)
        run(f"binwalk -e -M --run-as=root {base_file}", cwd=tmpdir)
        
        # Recursively check everything binwalk extracted
        extracted_dir = os.path.join(tmpdir, f"_{base_file}.extracted")
        if os.path.exists(extracted_dir):
            for root, _, files in os.walk(extracted_dir):
                for f in files:
                    ext_path = os.path.join(root, f)
                    try:
                        with open(ext_path, 'rb') as ef:
                            if check_for_flag(ef.read(), f"Extracted file: {f}"):
                                return True
                    except:
                        pass

    # 5. PCAP Extraction
    if filepath.lower().endswith('.pcap') or filepath.lower().endswith('.pcapng'):
        print(f"[*] Autopilot: Running PCAP auto-extraction on {filepath}...")
        with tempfile.TemporaryDirectory() as tmpdir:
            run(f"tshark -r '{filepath}' --export-objects http,{tmpdir}", cwd=tmpdir)
            for f in os.listdir(tmpdir):
                ext_path = os.path.join(tmpdir, f)
                if os.path.isfile(ext_path):
                    with open(ext_path, 'rb') as ef:
                        if check_for_flag(ef.read(), f"PCAP HTTP Object: {f}"):
                            return True

    return False

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file_or_directory>")
        sys.exit(1)
        
    target = sys.argv[1]
    
    print(f"\n{B}{C}{'='*60}{N}")
    print(f"  {B}CTF Autopilot (Zero False-Positive Solver){N}")
    print(f"  Target: {target}")
    print(f"{B}{C}{'='*60}{N}\n")
    
    solved = False
    
    if os.path.isdir(target):
        for root, _, files in os.walk(target):
            for f in files:
                filepath = os.path.join(root, f)
                if auto_solve_file(filepath):
                    solved = True
    else:
        if auto_solve_file(target):
            solved = True
            
    if not solved:
        print(f"\n{R}[-] Autopilot could not find the flag automatically.{N}")
        print(f"    Try using the manual analysis tools: challenge_advisor.py, binary_analyzer.py, etc.")
    else:
        print(f"\n{G}[+] Autopilot finished successfully!{N}")

if __name__ == "__main__":
    main()
