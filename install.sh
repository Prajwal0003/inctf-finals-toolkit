#!/usr/bin/env bash
# ============================================
# InCTF 2026 Finals — Master Installer
# TEAM_UNFINDABLES (FIN-030)
# Target: Arch Linux 2026.02.01
# ============================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/install.log"

log() { echo -e "${GREEN}[+]${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"; }
err() { echo -e "${RED}[-]${NC} $1" | tee -a "$LOG_FILE"; }
section() { echo -e "\n${CYAN}=== $1 ===${NC}" | tee -a "$LOG_FILE"; }

# Check root
if [[ $EUID -ne 0 ]]; then
    err "This script must be run as root (sudo ./install.sh)"
    exit 1
fi

REAL_USER="${SUDO_USER:-$(whoami)}"
REAL_HOME=$(eval echo "~${REAL_USER}")

echo "" > "$LOG_FILE"
log "InCTF 2026 Finals Toolkit Installer"
log "Team: TEAM_UNFINDABLES | ID: FIN-030"
log "Installing for user: ${REAL_USER}"
log "Date: $(date)"

# ============================================
section "1/7 — Updating System"
# ============================================
pacman -Syu --noconfirm 2>&1 | tee -a "$LOG_FILE"

# ============================================
section "2/7 — Installing Pacman Packages"
# ============================================
PACMAN_PKGS="${SCRIPT_DIR}/packages/pacman-packages.txt"
if [[ -f "$PACMAN_PKGS" ]]; then
    # Filter out comments and empty lines
    PKGS=$(grep -v '^#' "$PACMAN_PKGS" | grep -v '^$' | tr '\n' ' ')
    log "Installing: ${PKGS}"
    pacman -S --noconfirm --needed $PKGS 2>&1 | tee -a "$LOG_FILE" || warn "Some pacman packages may have failed"
else
    err "pacman-packages.txt not found!"
fi

# ============================================
section "3/7 — Installing AUR Helper (yay)"
# ============================================
if ! command -v yay &>/dev/null; then
    log "Installing yay AUR helper..."
    cd /tmp
    sudo -u "$REAL_USER" git clone https://aur.archlinux.org/yay.git 2>&1 | tee -a "$LOG_FILE"
    cd yay
    sudo -u "$REAL_USER" makepkg -si --noconfirm 2>&1 | tee -a "$LOG_FILE"
    cd "$SCRIPT_DIR"
    rm -rf /tmp/yay
else
    log "yay already installed, skipping"
fi

# ============================================
section "4/7 — Installing AUR Packages"
# ============================================
AUR_PKGS="${SCRIPT_DIR}/packages/aur-packages.txt"
if [[ -f "$AUR_PKGS" ]]; then
    while IFS= read -r pkg; do
        # Skip comments and empty lines
        [[ "$pkg" =~ ^#.*$ || -z "$pkg" ]] && continue
        log "Installing AUR package: ${pkg}"
        sudo -u "$REAL_USER" yay -S --noconfirm --needed "$pkg" 2>&1 | tee -a "$LOG_FILE" || warn "AUR package '${pkg}' failed"
    done < "$AUR_PKGS"
else
    err "aur-packages.txt not found!"
fi

# ============================================
section "5/7 — Installing Python Packages"
# ============================================
PY_REQS="${SCRIPT_DIR}/python-requirements.txt"
if [[ -f "$PY_REQS" ]]; then
    log "Installing Python packages..."
    sudo -u "$REAL_USER" pip install --user --break-system-packages -r "$PY_REQS" 2>&1 | tee -a "$LOG_FILE" || warn "Some pip packages may have failed"
else
    err "python-requirements.txt not found!"
fi

# ============================================
section "6/7 — Deploying Configs"
# ============================================
CONFIGS_DIR="${SCRIPT_DIR}/configs"

# tmux
if [[ -f "${CONFIGS_DIR}/.tmux.conf" ]]; then
    log "Deploying tmux config..."
    cp "${CONFIGS_DIR}/.tmux.conf" "${REAL_HOME}/.tmux.conf"
    chown "$REAL_USER:$REAL_USER" "${REAL_HOME}/.tmux.conf"
fi

# GDB
if [[ -f "${CONFIGS_DIR}/.gdbinit" ]]; then
    log "Deploying GDB config..."
    cp "${CONFIGS_DIR}/.gdbinit" "${REAL_HOME}/.gdbinit"
    chown "$REAL_USER:$REAL_USER" "${REAL_HOME}/.gdbinit"
fi

# Vim
if [[ -f "${CONFIGS_DIR}/.vimrc" ]]; then
    log "Deploying Vim config..."
    cp "${CONFIGS_DIR}/.vimrc" "${REAL_HOME}/.vimrc"
    chown "$REAL_USER:$REAL_USER" "${REAL_HOME}/.vimrc"
fi

# Zsh
if [[ -f "${CONFIGS_DIR}/.zshrc" ]]; then
    log "Deploying Zsh config..."
    # Backup existing
    [[ -f "${REAL_HOME}/.zshrc" ]] && cp "${REAL_HOME}/.zshrc" "${REAL_HOME}/.zshrc.bak"
    cp "${CONFIGS_DIR}/.zshrc" "${REAL_HOME}/.zshrc"
    chown "$REAL_USER:$REAL_USER" "${REAL_HOME}/.zshrc"
fi

# ============================================
section "7/7 — Deploying Scripts"
# ============================================
SCRIPTS_DIR="${SCRIPT_DIR}/scripts"
DEPLOY_DIR="${REAL_HOME}/ctf-scripts"

log "Deploying CTF scripts to ${DEPLOY_DIR}..."
mkdir -p "$DEPLOY_DIR"
cp -r "${SCRIPTS_DIR}/"* "$DEPLOY_DIR/" 2>/dev/null || warn "No scripts to deploy"
chown -R "$REAL_USER:$REAL_USER" "$DEPLOY_DIR"
chmod -R +x "$DEPLOY_DIR"

# Download Offline CyberChef
CYBERCHEF_URL="https://github.com/gchq/CyberChef/releases/download/v10.18.9/CyberChef_v10.18.9.zip"
if [[ ! -f "${DEPLOY_DIR}/CyberChef.html" ]]; then
    log "Downloading Offline CyberChef..."
    sudo -u "$REAL_USER" wget -q -O "${DEPLOY_DIR}/CyberChef.zip" "$CYBERCHEF_URL" || warn "CyberChef download failed"
    if [[ -f "${DEPLOY_DIR}/CyberChef.zip" ]]; then
        sudo -u "$REAL_USER" unzip -q "${DEPLOY_DIR}/CyberChef.zip" -d "${DEPLOY_DIR}/" || warn "CyberChef unzip failed"
        mv "${DEPLOY_DIR}/"CyberChef_*.html "${DEPLOY_DIR}/CyberChef.html" 2>/dev/null || true
        rm "${DEPLOY_DIR}/CyberChef.zip" 2>/dev/null || true
    fi
fi

# Add scripts to PATH
PROFILE_LINE='export PATH="$HOME/ctf-scripts:$HOME/ctf-scripts/pwn:$HOME/ctf-scripts/crypto:$HOME/ctf-scripts/web:$HOME/ctf-scripts/forensics:$HOME/ctf-scripts/misc:$HOME/ctf-scripts/recon:$PATH"'
if ! grep -q "ctf-scripts" "${REAL_HOME}/.bashrc" 2>/dev/null; then
    echo "$PROFILE_LINE" >> "${REAL_HOME}/.bashrc"
fi
if ! grep -q "ctf-scripts" "${REAL_HOME}/.zshrc" 2>/dev/null; then
    echo "$PROFILE_LINE" >> "${REAL_HOME}/.zshrc"
fi

# ============================================
section "Wordlists"
# ============================================
WORDLISTS_DIR="${REAL_HOME}/wordlists"
mkdir -p "$WORDLISTS_DIR"

# Download SecLists (if internet is available during setup)
if [[ ! -d "${WORDLISTS_DIR}/SecLists" ]]; then
    log "Downloading SecLists..."
    sudo -u "$REAL_USER" git clone --depth 1 https://github.com/danielmiessler/SecLists.git "${WORDLISTS_DIR}/SecLists" 2>&1 | tee -a "$LOG_FILE" || warn "SecLists download failed"
fi

# Download rockyou.txt
if [[ ! -f "${WORDLISTS_DIR}/rockyou.txt" ]]; then
    log "Downloading rockyou.txt..."
    sudo -u "$REAL_USER" wget -q -O "${WORDLISTS_DIR}/rockyou.txt.gz" "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt" 2>&1 | tee -a "$LOG_FILE" || warn "rockyou.txt download failed"
fi

chown -R "$REAL_USER:$REAL_USER" "$WORDLISTS_DIR"

# ============================================
section "Docker Setup"
# ============================================
log "Enabling Docker service..."
systemctl enable docker 2>/dev/null || true
systemctl start docker 2>/dev/null || true
usermod -aG docker "$REAL_USER" 2>/dev/null || true

# Pull AperiSolve image (as requested by teammate)
log "Pulling AperiSolve Docker image..."
docker pull zeecka/aperisolve 2>&1 | tee -a "$LOG_FILE" || warn "AperiSolve pull failed"

# ============================================
section "Installation Complete!"
# ============================================
echo ""
log "✅ All tools installed successfully!"
log "📁 CTF scripts deployed to: ${DEPLOY_DIR}"
log "📁 Wordlists at: ${WORDLISTS_DIR}"
log "📋 Full log: ${LOG_FILE}"
echo ""
warn "Please log out and back in for group changes (docker) to take effect."
warn "Run 'source ~/.zshrc' or 'source ~/.bashrc' to load new aliases."
echo ""
