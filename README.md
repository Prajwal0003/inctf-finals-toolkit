# 🏴 InCTF 2026 Finals — Custom Tools/Scripts Request

**Team:** TEAM_UNFINDABLES  
**Team ID:** FIN-030  
**Platform:** Arch Linux 2026.02.01 (3 machines)

---

## Overview

This repository contains all custom tools, scripts, configurations, and dependencies requested for pre-installation on our competition machines. Everything here runs **entirely offline** — no internet required during the CTF.

## Quick Install

```bash
git clone https://github.com/<your-username>/inctf-finals-toolkit.git
cd inctf-finals-toolkit
chmod +x install.sh
sudo ./install.sh
```

## Repository Structure

```
inctf-finals-toolkit/
├── install.sh                  # Master installer (run as root)
├── README.md                   # This file
├── packages/
│   ├── pacman-packages.txt     # Official Arch repo packages
│   └── aur-packages.txt       # AUR packages
├── configs/
│   ├── .tmux.conf              # tmux configuration
│   ├── .gdbinit                # GDB init with pwndbg
│   ├── .vimrc                  # Vim configuration for CTF
│   └── .zshrc                  # Zsh config with CTF aliases
├── scripts/
│   ├── pwn/
│   │   ├── exploit_template.py # Pwntools exploit template
│   │   ├── rop_finder.py       # Quick ROP chain builder
│   │   └── shellcode_gen.py    # Common shellcodes
│   ├── crypto/
│   │   ├── rsa_toolkit.py      # RSA attack suite
│   │   ├── aes_oracle.py       # AES padding oracle
│   │   └── hash_crack.py       # Hash utilities
│   ├── web/
│   │   ├── sqli_helper.py      # SQL injection helper
│   │   ├── jwt_toolkit.py      # JWT forge/decode
│   │   └── ssti_payloads.txt   # SSTI payload collection
│   ├── forensics/
│   │   ├── stego_solver.py     # Multi-format stego solver
│   │   └── pcap_parser.py      # PCAP analysis helper
│   ├── misc/
│   │   ├── flag_submitter.py   # Auto flag submission
│   │   └── solve_stub.py       # Generic solve template
│   └── recon/
│       └── enum_services.sh    # Quick service enumeration
├── wordlists/
│   └── download_wordlists.sh   # Pre-downloads common wordlists
└── python-requirements.txt     # Python packages (pip)
```

## What's Included

### 🔧 Binary Exploitation / Pwn
- pwntools, pwndbg, ROPgadget, one_gadget, seccomp-tools
- GDB with pwndbg configured, radare2
- Custom exploit templates and shellcode generators

### 🔐 Cryptography
- SageMath, pycryptodome, gmpy2, z3-solver, sympy
- RSA multi-attack toolkit (Wiener, Boneh-Durfee, Fermat, Hastad)
- AES oracle attacks, hash utilities

### 🌐 Web
- sqlmap, ffuf, httpie, curl, gobuster
- JWT toolkit, SSTI payloads, SQLi helpers
- Burp Suite Community (if available via AUR)

### 🔍 Reverse Engineering
- Ghidra, radare2, binwalk, ltrace, strace
- Binary Ninja (if licensed), objdump, nm

### 🕵️ Forensics
- Volatility3, foremost, exiftool, steghide, zsteg
- binwalk, scalpel, bulk_extractor
- PCAP analysis tools (tshark, Wireshark)

### ⚙️ Environment
- tmux (preconfigured split layouts)
- vim with CTF-optimized config
- zsh with aliases and quick-access commands
- Docker (for running challenge containers)

## Constraints (per organizer rules)
- ✅ All tools run offline
- ✅ All tools are open-source / free
- ✅ Userland only — no kernel modules or drivers
- ✅ Repository is public

## Team
- Aradhay Vinod Kopulwar
- Prajwal Sankpal
- Chaitanya Shelar
