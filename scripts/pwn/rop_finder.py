#!/usr/bin/env python3
"""
InCTF 2026 Finals — ROP Chain Finder
TEAM_UNFINDABLES (FIN-030)

Quick ROP gadget finder and chain builder using pwntools.
Usage: python3 rop_finder.py <binary> [libc]
"""
from pwn import *
import sys

def find_gadgets(binary_path, libc_path=None):
    """Find useful ROP gadgets in binary and libc."""
    elf = ELF(binary_path)
    rop = ROP(elf)

    log.info(f"Binary: {binary_path}")
    log.info(f"Arch: {elf.arch}")
    log.info(f"RELRO: {elf.relro}")
    log.info(f"Stack Canary: {elf.canary}")
    log.info(f"NX: {elf.nx}")
    log.info(f"PIE: {elf.pie}")

    print("\n" + "="*60)
    print("USEFUL GADGETS (Binary)")
    print("="*60)

    gadget_names = ['pop rdi', 'pop rsi', 'pop rdx', 'pop rcx',
                    'pop rax', 'pop rbp', 'pop rsp',
                    'ret', 'leave', 'syscall',
                    'pop rdi ; ret', 'pop rsi ; pop r15 ; ret']

    for name in gadget_names:
        try:
            gadget = rop.find_gadget([name.split(' ; ')[0]])
            if gadget:
                log.success(f"{name}: {gadget.address:#x}")
        except:
            pass

    print("\n" + "="*60)
    print("USEFUL SYMBOLS")
    print("="*60)

    useful_syms = ['main', 'win', 'flag', 'shell', 'system',
                   'execve', 'gets', 'puts', 'printf',
                   '__libc_start_main', 'read', 'write',
                   'open', 'mprotect', 'mmap']

    for sym in useful_syms:
        if sym in elf.symbols:
            log.success(f"{sym}: {elf.symbols[sym]:#x}")
        elif sym in elf.plt:
            log.success(f"{sym}@plt: {elf.plt[sym]:#x}")
        elif sym in elf.got:
            log.info(f"{sym}@got: {elf.got[sym]:#x}")

    # Libc analysis
    if libc_path:
        libc = ELF(libc_path)
        libc_rop = ROP(libc)

        print("\n" + "="*60)
        print("LIBC GADGETS & OFFSETS")
        print("="*60)

        for sym in ['system', '/bin/sh', 'execve', 'one_gadget']:
            if sym in libc.symbols:
                log.success(f"libc {sym}: {libc.symbols[sym]:#x}")

        # Search for /bin/sh string
        binsh = next(libc.search(b'/bin/sh\x00'), None)
        if binsh:
            log.success(f"libc /bin/sh: {binsh:#x}")

    print("\n" + "="*60)
    print("ROP CHAIN SUGGESTIONS")
    print("="*60)

    if 'system' in elf.plt or (libc_path and 'system' in ELF(libc_path).symbols):
        print("\n[ret2libc] system('/bin/sh') chain:")
        print("  1. Leak libc address via puts@plt(puts@got)")
        print("  2. Calculate libc base")
        print("  3. Call system('/bin/sh')")

    if not elf.nx:
        print("\n[ret2shellcode] NX is disabled!")
        print("  1. Place shellcode on stack/heap")
        print("  2. Jump to shellcode")

    if not elf.pie:
        print("\n[No PIE] Addresses are fixed — direct ROP possible")

    if not elf.canary:
        print("\n[No Canary] Stack smashing possible without leak")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <binary> [libc]")
        sys.exit(1)

    binary = sys.argv[1]
    libc = sys.argv[2] if len(sys.argv) > 2 else None
    find_gadgets(binary, libc)
