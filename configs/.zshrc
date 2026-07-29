# ============================================
# InCTF 2026 Finals — Zsh Config
# TEAM_UNFINDABLES (FIN-030)
# ============================================

# --- Prompt ---
PROMPT='%F{cyan}[CTF]%f %F{green}%n%f:%F{blue}%~%f %F{yellow}❯%f '

# --- History ---
HISTFILE=~/.zsh_history
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE

# --- Completion ---
autoload -Uz compinit && compinit
zstyle ':completion:*' menu select

# --- Key bindings ---
bindkey -e
bindkey '^[[A' history-search-backward
bindkey '^[[B' history-search-forward

# ============================================
# CTF Aliases
# ============================================

# --- Quick Navigation ---
alias ctf='cd ~/ctf'
alias chal='cd ~/ctf/challenges'
alias scripts='cd ~/ctf-scripts'

# --- Python ---
alias py='python3'
alias ipy='ipython3'
alias pip='pip3'

# --- Binary Analysis ---
alias checksec='checksec --file'
alias strings='strings -a'
alias objdump='objdump -M intel'
alias disas='objdump -d -M intel'

# --- Networking ---
alias serve='python3 -m http.server 8080'
alias listen='nc -lvnp'

# --- Hex/Encoding ---
alias hexdump='xxd'
alias b64e='base64'
alias b64d='base64 -d'
alias unhex="python3 -c \"import sys; sys.stdout.buffer.write(bytes.fromhex(sys.argv[1]))\""

# --- File Analysis ---
alias ftype='file'
alias entropy='binwalk -E'

# --- Docker ---
alias dps='docker ps'
alias drun='docker run -it --rm'

# --- Git ---
alias gs='git status'
alias gc='git commit -m'
alias gp='git push'
alias ga='git add'

# ============================================
# CTF Functions
# ============================================

# Create a new challenge directory with template
newchal() {
    local name="${1:?Usage: newchal <name>}"
    mkdir -p ~/ctf/challenges/"$name"
    cd ~/ctf/challenges/"$name"
    cp ~/ctf-scripts/misc/solve_stub.py solve.py 2>/dev/null || \
        echo '#!/usr/bin/env python3\n# Challenge: '"$name"'\n\n' > solve.py
    chmod +x solve.py
    echo "[+] Created challenge directory: $name"
}

# Quick ROT13
rot13() { echo "$1" | tr 'A-Za-z' 'N-ZA-Mn-za-m'; }

# Quick XOR with single byte
xor() {
    python3 -c "
import sys
data = open(sys.argv[1], 'rb').read()
key = int(sys.argv[2], 0)
print(bytes([b ^ key for b in data]))
" "$1" "$2"
}

# Extract all from file (binwalk)
extract() { binwalk -e --directory=./extracted "$1"; }

# Quick netcat listener
listen_on() { nc -lvnp "${1:?Usage: listen_on <port>}"; }

# Search for flag format in files
findflag() {
    local pattern="${1:-flag\{.*\}}"
    grep -rn "$pattern" . 2>/dev/null
    grep -rn "inctf{.*}" . 2>/dev/null
    grep -rn "InCTF{.*}" . 2>/dev/null
}

# Convert between bases
tohex() { printf '%x\n' "$1"; }
todec() { printf '%d\n' "0x$1"; }
tobin() { echo "obase=2;$1" | bc; }

# Quick checksec on all ELFs in directory
checksec_all() {
    find . -type f -executable -exec sh -c 'file "{}" | grep -q ELF && checksec --file="{}"' \;
}

# ============================================
# PATH
# ============================================
export PATH="$HOME/ctf-scripts:$HOME/ctf-scripts/pwn:$HOME/ctf-scripts/crypto:$HOME/ctf-scripts/web:$HOME/ctf-scripts/forensics:$HOME/ctf-scripts/misc:$HOME/ctf-scripts/recon:$HOME/.local/bin:$PATH"

# Wordlists
export WORDLISTS="$HOME/wordlists"
export SECLISTS="$HOME/wordlists/SecLists"
export ROCKYOU="$HOME/wordlists/rockyou.txt"

# ============================================
# Startup
# ============================================
echo ""
echo "  🏴 TEAM_UNFINDABLES — InCTF 2026 Finals"
echo "  📋 FIN-030 | Arch Linux"
echo "  ⚡ Type 'newchal <name>' to start a challenge"
echo ""
