#!/usr/bin/env python3
"""
InCTF 2026 Finals — Challenge Type Identifier & Strategy Advisor
TEAM_UNFINDABLES (FIN-030)

Describe a challenge and get technique suggestions + tool recommendations.
No AI involved — just pattern matching against known CTF patterns.

Usage: python3 challenge_advisor.py "binary with canary, leaks libc address"
"""
import sys, re

G, Y, C, R, B, M, N = '\033[92m', '\033[93m', '\033[96m', '\033[91m', '\033[1m', '\033[95m', '\033[0m'

STRATEGIES = {
    # PWN
    ("pwn", "buffer overflow + no protections"): {
        "detect": ["buffer", "overflow", "no canary", "no pie", "nx disabled"],
        "strategy": [
            "1. Find offset with cyclic pattern",
            "2. Inject shellcode on stack (NX disabled)",
            "3. Jump to shellcode via overwritten return address",
        ],
        "tools": ["pwntools", "gdb + pwndbg", "shellcode_gen.py"],
        "template": "exploit_template.py",
    },
    ("pwn", "buffer overflow + NX"): {
        "detect": ["overflow", "nx", "no canary"],
        "strategy": [
            "1. Find offset with cyclic pattern",
            "2. Leak libc via puts@plt(puts@got) + ret to main",
            "3. Calculate libc base, call system('/bin/sh')",
        ],
        "tools": ["pwntools", "rop_finder.py", "one_gadget"],
        "template": "exploit_template.py",
    },
    ("pwn", "buffer overflow + canary"): {
        "detect": ["overflow", "canary", "stack"],
        "strategy": [
            "1. Leak canary via format string or brute force",
            "2. Overflow buffer, preserve canary in payload",
            "3. ROP chain or ret2libc after canary",
        ],
        "tools": ["pwntools", "gdb", "rop_finder.py"],
        "template": "exploit_template.py",
    },
    ("pwn", "format string"): {
        "detect": ["format", "printf", "%p", "%n", "%x", "fmt"],
        "strategy": [
            "1. Leak stack values with %p (find offset)",
            "2. Leak canary/PIE base/libc if needed",
            "3. Arbitrary write via %n to GOT or return address",
            "pwntools: fmtstr_payload(offset, {target: value})",
        ],
        "tools": ["pwntools (fmtstr_payload)", "gdb"],
        "template": "exploit_template.py",
    },
    ("pwn", "heap exploitation"): {
        "detect": ["heap", "malloc", "free", "tcache", "chunk", "uaf", "double free", "fastbin"],
        "strategy": [
            "1. Identify heap primitive (UAF, double free, overflow)",
            "2. tcache poisoning: overwrite fd -> allocate anywhere",
            "3. Overwrite __free_hook or __malloc_hook with system",
            "4. Or: House of Force / House of Orange for older glibc",
        ],
        "tools": ["pwntools", "gdb + pwndbg (heap commands)", "one_gadget"],
        "template": "exploit_template.py",
    },
    # CRYPTO
    ("crypto", "RSA - basic"): {
        "detect": ["rsa", "n", "e", "c", "decrypt"],
        "strategy": [
            "1. Try factoring n (factordb, yafu, Fermat)",
            "2. Check for small e (cube root attack)",
            "3. Check for common modulus / shared factors",
            "4. Run rsa_toolkit.py auto_solve(n, e, c)",
        ],
        "tools": ["rsa_toolkit.py", "SageMath", "gmpy2"],
        "template": "rsa_toolkit.py -> auto_solve()",
    },
    ("crypto", "RSA - special"): {
        "detect": ["wiener", "small d", "large e", "coppersmith", "partial"],
        "strategy": [
            "Large e → Wiener's attack (d < N^0.25)",
            "Partial key → Coppersmith small roots",
            "Multiple messages → Hastad broadcast",
            "Same n, diff e → Common modulus attack",
        ],
        "tools": ["rsa_toolkit.py", "SageMath"],
        "template": "rsa_toolkit.py",
    },
    ("crypto", "AES / block cipher"): {
        "detect": ["aes", "block", "cbc", "ecb", "encrypt", "oracle", "padding"],
        "strategy": [
            "ECB: detect identical blocks, cut-paste attack",
            "CBC: bit-flipping (XOR prev block), padding oracle",
            "CTR: nonce reuse -> XOR known plaintext",
            "Padding oracle → aes_oracle.py",
        ],
        "tools": ["aes_oracle.py", "pycryptodome"],
        "template": "aes_oracle.py",
    },
    # WEB
    ("web", "SQL injection"): {
        "detect": ["sql", "login", "database", "query", "username", "password", "auth"],
        "strategy": [
            "1. Test: ' OR 1=1-- -",
            "2. Detect columns: ORDER BY N / UNION SELECT NULL,...",
            "3. Extract: UNION SELECT table_name FROM information_schema.tables",
            "4. Use sqlmap for automation",
        ],
        "tools": ["sqli_helper.py", "sqlmap", "Burp Suite"],
        "template": "sqli_helper.py",
    },
    ("web", "SSTI"): {
        "detect": ["template", "ssti", "render", "jinja", "flask", "twig"],
        "strategy": [
            "1. Detect: {{7*7}} -> 49?",
            "2. Identify engine (Jinja2, Twig, etc.)",
            "3. RCE payload from ssti_payloads.txt",
            "Jinja2: {{config.__class__.__init__.__globals__['os'].popen('id').read()}}",
        ],
        "tools": ["ssti_payloads.txt", "curl/httpie"],
        "template": "ssti_payloads.txt",
    },
    ("web", "JWT"): {
        "detect": ["jwt", "token", "bearer", "authorization", "json web"],
        "strategy": [
            "1. Decode: jwt_toolkit.py <token>",
            "2. Try alg:none attack",
            "3. Crack weak HMAC secret",
            "4. Check for key confusion (RS256->HS256)",
        ],
        "tools": ["jwt_toolkit.py"],
        "template": "jwt_toolkit.py",
    },
    # FORENSICS
    ("forensics", "steganography"): {
        "detect": ["image", "png", "jpg", "hidden", "steg", "pixel", "lsb"],
        "strategy": [
            "1. file + exiftool (metadata)",
            "2. binwalk (embedded files)",
            "3. strings (flag in plaintext?)",
            "4. zsteg / stegsolve (LSB for PNG)",
            "5. steghide extract (JPEG, try empty password first)",
        ],
        "tools": ["stego_solver.py", "binwalk", "zsteg", "steghide", "exiftool"],
        "template": "stego_solver.py <file>",
    },
    ("forensics", "pcap / network"): {
        "detect": ["pcap", "capture", "network", "packet", "wireshark", "traffic"],
        "strategy": [
            "1. Protocol hierarchy: tshark -z io,phs",
            "2. Follow TCP streams for passwords/flags",
            "3. Extract HTTP objects",
            "4. Check DNS queries for exfiltration",
        ],
        "tools": ["pcap_parser.py", "tshark", "Wireshark"],
        "template": "pcap_parser.py <file>",
    },
    ("forensics", "memory dump"): {
        "detect": ["memory", "dump", "ram", "volatility", "vmem", "raw"],
        "strategy": [
            "1. vol windows.info (identify OS)",
            "2. vol windows.pslist (processes)",
            "3. vol windows.cmdline (commands run)",
            "4. vol windows.filescan -> dumpfiles",
            "5. vol windows.hashdump (password hashes)",
        ],
        "tools": ["volatility3"],
        "template": "vol -f dump.raw windows.info",
    },
    # REV
    ("reverse", "binary reversing"): {
        "detect": ["reverse", "binary", "crackme", "keygen", "serial", "password check"],
        "strategy": [
            "1. file + checksec → identify binary",
            "2. strings → quick wins",
            "3. Ghidra decompile → understand logic",
            "4. GDB dynamic: break at comparison, read registers",
            "5. angr symbolic execution for constraint solving",
        ],
        "tools": ["ghidra", "gdb + pwndbg", "angr", "r2"],
        "template": "N/A — use Ghidra + GDB",
    },
}

def advise(description):
    dl = description.lower()
    matches = []
    for (cat, name), info in STRATEGIES.items():
        score = sum(1 for kw in info["detect"] if kw in dl)
        if score > 0:
            matches.append((score, cat, name, info))
    matches.sort(key=lambda x: -x[0])

    print(f"\n{B}{C}{'='*60}{N}")
    print(f"  {B}Challenge Strategy Advisor{N}")
    print(f"  Description: {Y}{description}{N}")
    print(f"{B}{C}{'='*60}{N}")

    if not matches:
        print(f"\n{R}  No matching patterns found. Try more specific keywords.{N}")
        return

    for i, (score, cat, name, info) in enumerate(matches[:3]):
        print(f"\n{B}{G}{'-'*50}{N}")
        print(f"  {B}Match #{i+1}: {Y}[{cat}]{N} {B}{name}{N} (score: {score})")
        print(f"{B}{G}{'-'*50}{N}")
        print(f"\n  {B}Strategy:{N}")
        for step in info["strategy"]:
            print(f"    {C}->{N} {step}")
        print(f"\n  {B}Tools:{N}")
        for tool in info["tools"]:
            print(f"    {M}-{N} {tool}")
        print(f"\n  {B}Quick start:{N} {G}{info['template']}{N}")

    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 challenge_advisor.py \"<challenge description>\"")
        print(f"\nExamples:")
        print(f"  challenge_advisor.py \"binary with format string vulnerability\"")
        print(f"  challenge_advisor.py \"RSA with very large e and small d\"")
        print(f"  challenge_advisor.py \"flask app with user input in template\"")
        print(f"  challenge_advisor.py \"pcap file with HTTP traffic\"")
        sys.exit(0)
    advise(" ".join(sys.argv[1:]))
