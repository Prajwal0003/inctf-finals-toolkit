#!/usr/bin/env python3
"""
InCTF 2026 Finals — Binary Auto-Analyzer
TEAM_UNFINDABLES (FIN-030)

Drop a binary, get instant analysis: protections, strings, 
interesting functions, and exploit strategy suggestions.
No AI — just checksec + pattern matching.

Usage: python3 binary_analyzer.py ./challenge
"""
import subprocess, sys, os, re

G, Y, C, R, B, M, N = '\033[92m', '\033[93m', '\033[96m', '\033[91m', '\033[1m', '\033[95m', '\033[0m'

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout + r.stderr
    except: return ""

def analyze(binary):
    if not os.path.exists(binary):
        print(f"{R}[-] File not found: {binary}{N}")
        return

    print(f"\n{B}{C}{'='*60}{N}")
    print(f"  {B}Binary Auto-Analyzer — {binary}{N}")
    print(f"{B}{C}{'='*60}{N}")

    # File type
    ftype = run(f'file "{binary}"').strip()
    print(f"\n{B}[File Type]{N}\n  {ftype}")

    arch = "amd64" if "64-bit" in ftype else "i386" if "32-bit" in ftype else "unknown"
    is_elf = "ELF" in ftype
    is_static = "statically linked" in ftype
    is_stripped = "stripped" in ftype and "not stripped" not in ftype

    # Checksec
    print(f"\n{B}[Protections]{N}")
    checksec = run(f'checksec --file="{binary}" 2>&1')
    if checksec: print(f"  {checksec.strip()}")

    nx = "NX enabled" in checksec or "NX            : enabled" in checksec
    canary = "Canary" in checksec and "No canary" not in checksec
    pie = "PIE enabled" in checksec or "PIE           : enabled" in checksec
    relro = "Full RELRO" in checksec

    # Quick protection summary
    print(f"\n{B}[Protection Summary]{N}")
    print(f"  Arch:    {Y}{arch}{N}")
    print(f"  NX:      {G+'ON' if nx else R+'OFF'}{N}")
    print(f"  Canary:  {G+'ON' if canary else R+'OFF'}{N}")
    print(f"  PIE:     {G+'ON' if pie else R+'OFF'}{N}")
    print(f"  RELRO:   {G+'Full' if relro else Y+'Partial' if 'Partial' in checksec else R+'None'}{N}")
    print(f"  Static:  {Y+'Yes' if is_static else 'No'}{N}")
    print(f"  Stripped:{Y+'Yes' if is_stripped else 'No'}{N}")

    # Interesting strings
    print(f"\n{B}[Interesting Strings]{N}")
    strings = run(f'strings -a "{binary}"')
    patterns = {
        "Flags": r'(flag\{|inctf\{|ctf\{).*',
        "Shell commands": r'(/bin/sh|/bin/bash|system|execve|popen)',
        "Format strings": r'(%[0-9]*[dxspn]|printf|scanf)',
        "File paths": r'(/etc/passwd|/flag|/home/.*flag|\.txt)',
        "Network": r'(socket|connect|bind|listen|recv|send)',
        "Crypto": r'(AES|RSA|encrypt|decrypt|key|iv|nonce)',
        "Dangerous funcs": r'\b(gets|strcpy|strcat|sprintf|scanf|read)\b',
    }
    for label, pattern in patterns.items():
        matches = set(re.findall(pattern, strings, re.I))
        if matches:
            print(f"  {Y}{label}:{N} {', '.join(list(matches)[:5])}")

    # Vulnerable functions
    dangerous = ['gets', 'strcpy', 'strcat', 'sprintf', 'scanf', 'read', 'printf']
    safe_alt = {'gets': 'fgets', 'strcpy': 'strncpy', 'strcat': 'strncat', 
                'sprintf': 'snprintf', 'scanf': 'fgets+sscanf'}
    
    found_vuln = []
    for func in dangerous:
        if re.search(rf'\b{func}\b', strings):
            found_vuln.append(func)
    
    if found_vuln:
        print(f"\n{B}[Potentially Vulnerable Functions]{N}")
        for func in found_vuln:
            alt = safe_alt.get(func, "N/A")
            if func in ['gets', 'strcpy', 'sprintf']:
                print(f"  {R}⚠ {func}(){N} — buffer overflow likely! (safe alt: {alt})")
            elif func == 'printf' and '%' not in run(f'objdump -d "{binary}" | grep -A2 printf | head -5'):
                print(f"  {Y}⚠ printf(){N} — possible format string if user-controlled")
            else:
                print(f"  {Y}• {func}(){N}")

    # Strategy suggestion
    print(f"\n{B}[Suggested Strategy]{N}")
    if 'gets' in found_vuln or 'strcpy' in found_vuln:
        print(f"  {G}→ Buffer Overflow detected{N}")
        if not nx:
            print(f"    {C}NX disabled → shellcode injection{N}")
            print(f"    Use: shellcode_gen.py {arch} execve")
        elif not canary and not pie:
            print(f"    {C}No canary + No PIE → direct ROP chain{N}")
            print(f"    Use: rop_finder.py {binary}")
        elif not canary and pie:
            print(f"    {C}PIE enabled → leak PIE base first, then ROP{N}")
        elif canary:
            print(f"    {C}Canary → leak canary (format string? info leak?), then overflow{N}")
    
    if 'printf' in found_vuln:
        print(f"  {G}→ Format String possible{N}")
        print(f"    {C}Test with: %p.%p.%p.%p.%p{N}")
        print(f"    {C}Use: pwntools fmtstr_payload(){N}")

    if any(f in found_vuln for f in ['malloc', 'free', 'calloc', 'realloc']):
        print(f"  {G}→ Heap challenge possible{N}")
        print(f"    {C}Check for UAF, double free, heap overflow{N}")

    if not found_vuln:
        print(f"  {Y}No obvious vulns from strings. Try:{N}")
        print(f"    1. Ghidra decompile for logic bugs")
        print(f"    2. GDB dynamic analysis")
        print(f"    3. angr for constraint solving")

    print(f"\n{B}[Quick Commands]{N}")
    print(f"  {C}ghidra {binary}{N}       — decompile")
    print(f"  {C}gdb {binary}{N}          — debug")
    print(f"  {C}r2 -A {binary}{N}        — radare2 analysis")
    print(f"  {C}ltrace ./{binary}{N}     — library calls")
    print(f"  {C}strace ./{binary}{N}     — system calls")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <binary>")
        sys.exit(1)
    analyze(sys.argv[1])
