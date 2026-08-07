#!/usr/bin/env python3
"""
InCTF Toolkit Test Suite — Run this to verify ALL your tools work!
Usage: python3 test_toolkit.py
"""
import os, sys, subprocess, base64, tempfile, json

G = '\033[92m'; R = '\033[91m'; Y = '\033[93m'; C = '\033[96m'; B = '\033[1m'; N = '\033[0m'
passed = 0; failed = 0; total = 0

def test(name, condition):
    global passed, failed, total
    total += 1
    if condition:
        passed += 1
        print(f"  {G}[PASS]{N} {name}")
    else:
        failed += 1
        print(f"  {R}[FAIL]{N} {name}")

def cmd_exists(c):
    try:
        subprocess.run(c, shell=True, capture_output=True, timeout=5)
        return True
    except: return False

def run(c):
    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=10, env=env)
        return r.stdout + r.stderr
    except: return ""

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(SCRIPT_DIR, "scripts")

print(f"\n{B}{C}{'='*60}{N}")
print(f"  {B}InCTF Toolkit Test Suite{N}")
print(f"{B}{C}{'='*60}{N}\n")

# === Test 1: Python Scripts Importable ===
print(f"{Y}[Category] Python Script Syntax Check{N}")
py_files = []
for root, _, files in os.walk(SCRIPTS):
    for f in files:
        if f.endswith('.py'):
            py_files.append(os.path.join(root, f))

for pf in py_files:
    name = os.path.relpath(pf, SCRIPT_DIR)
    result = run(f'python3 -c "import ast; ast.parse(open(r\'{pf}\', encoding=\'utf-8\', errors=\'ignore\').read())"')
    test(f"Syntax OK: {name}", "Error" not in result and "Traceback" not in result)

# === Test 2: Decoder Tool ===
print(f"\n{Y}[Category] Decoder Tool{N}")
decoder = os.path.join(SCRIPTS, "misc", "decoder.py")
if os.path.exists(decoder):
    # Base64 test
    out = run(f'python3 "{decoder}" "aW5jdGZ7dGVzdF9mbGFnfQ=="')
    test("Decoder: Base64 decode", "Base64" in out or "inctf" in out or "test_flag" in out)
    # Hex test
    out = run(f'python3 "{decoder}" "696e6374667b746573747d"')
    test("Decoder: Hex decode", "Hex" in out or "inctf" in out or "test" in out)
else:
    test("Decoder exists", False)

# === Test 3: Challenge Advisor ===
print(f"\n{Y}[Category] Challenge Advisor{N}")
advisor = os.path.join(SCRIPTS, "reference", "challenge_advisor.py")
if os.path.exists(advisor):
    out = run(f'python3 "{advisor}" --help 2>&1 || python3 "{advisor}" 2>&1')
    test("Challenge Advisor: Runs without crash", "Traceback" not in out)
else:
    test("Challenge Advisor exists", False)

# === Test 4: Reference Files Exist ===
print(f"\n{Y}[Category] Reference Files{N}")
ref_dir = os.path.join(SCRIPT_DIR, "reference")
expected_refs = [
    "CTF_CHEATSHEET.md", "CTF_PWN_BIBLE.md", "CTF_WEB_BIBLE.md",
    "CTF_FORENSICS_STEGO_BIBLE.md", "CTF_CRYPTO_BIBLE.md",
    "CTF_LINUX_SURVIVAL_GUIDE.md", "CTF_ULTIMATE_COMMANDS.html",
    "CTF_RE_Bible_ULTIMATE_EDITION.pdf", "CTF_Crypto_Stego_Cheatsheet.pdf"
]
for ref in expected_refs:
    test(f"Reference: {ref}", os.path.exists(os.path.join(ref_dir, ref)))

# === Test 5: Config Files ===
print(f"\n{Y}[Category] Config Files{N}")
configs_dir = os.path.join(SCRIPT_DIR, "configs")
for cfg in [".tmux.conf", ".gdbinit", ".vimrc", ".zshrc"]:
    test(f"Config: {cfg}", os.path.exists(os.path.join(configs_dir, cfg)))

# === Test 6: Package Lists ===
print(f"\n{Y}[Category] Package Lists{N}")
pkg_dir = os.path.join(SCRIPT_DIR, "packages")
test("pacman-packages.txt exists", os.path.exists(os.path.join(pkg_dir, "pacman-packages.txt")))
test("aur-packages.txt exists", os.path.exists(os.path.join(pkg_dir, "aur-packages.txt")))
test("python-requirements.txt exists", os.path.exists(os.path.join(SCRIPT_DIR, "python-requirements.txt")))

# === Test 7: Crypto self-test ===
print(f"\n{Y}[Category] Crypto Mini-Test{N}")
# Test XOR
try:
    cipher = bytes([ord(c) ^ 42 for c in "inctf{xor_test}"])
    recovered = bytes([b ^ 42 for b in cipher]).decode()
    test("XOR encrypt/decrypt round-trip", recovered == "inctf{xor_test}")
except:
    test("XOR encrypt/decrypt round-trip", False)

# Test Base64
try:
    encoded = base64.b64encode(b"inctf{b64_test}").decode()
    decoded = base64.b64decode(encoded).decode()
    test("Base64 encode/decode round-trip", decoded == "inctf{b64_test}")
except:
    test("Base64 encode/decode round-trip", False)

# === Summary ===
print(f"\n{B}{C}{'='*60}{N}")
print(f"  {B}Results: {G}{passed} passed{N} / {R}{failed} failed{N} / {total} total")
if failed == 0:
    print(f"  {G}{B}ALL TESTS PASSED! Your toolkit is ready!{N}")
else:
    print(f"  {Y}Fix the failed items above before competition.{N}")
print(f"{B}{C}{'='*60}{N}\n")
