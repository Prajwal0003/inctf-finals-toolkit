#!/usr/bin/env bash
# ============================================
# InCTF 2026 Finals — Quick Service Enumeration
# TEAM_UNFINDABLES (FIN-030)
#
# Usage: ./enum_services.sh <target_ip> [port_range]
# ============================================
set -euo pipefail

TARGET="${1:?Usage: $0 <target_ip> [port_range]}"
PORTS="${2:-1-65535}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}[*] Enumerating services on ${TARGET}${NC}"
echo "================================================"

# Quick port scan
echo -e "\n${YELLOW}[1/4] Quick TCP SYN scan${NC}"
nmap -sS -T4 --min-rate=1000 -p "$PORTS" "$TARGET" -oN "/tmp/nmap_quick_${TARGET}.txt" 2>/dev/null

# Get open ports
OPEN_PORTS=$(grep "^[0-9]" "/tmp/nmap_quick_${TARGET}.txt" 2>/dev/null | cut -d'/' -f1 | tr '\n' ',' | sed 's/,$//')

if [[ -z "$OPEN_PORTS" ]]; then
    echo -e "${RED}[-] No open ports found${NC}"
    exit 1
fi

echo -e "${GREEN}[+] Open ports: ${OPEN_PORTS}${NC}"

# Service version detection
echo -e "\n${YELLOW}[2/4] Service version detection${NC}"
nmap -sV -sC -p "$OPEN_PORTS" "$TARGET" -oN "/tmp/nmap_version_${TARGET}.txt" 2>/dev/null
cat "/tmp/nmap_version_${TARGET}.txt"

# UDP quick scan (top ports)
echo -e "\n${YELLOW}[3/4] Quick UDP scan (top 20)${NC}"
nmap -sU --top-ports 20 -T4 "$TARGET" -oN "/tmp/nmap_udp_${TARGET}.txt" 2>/dev/null
grep "open" "/tmp/nmap_udp_${TARGET}.txt" 2>/dev/null || echo "  No UDP ports found"

# Banner grabbing
echo -e "\n${YELLOW}[4/4] Banner grabbing${NC}"
for port in $(echo "$OPEN_PORTS" | tr ',' ' '); do
    echo -ne "  Port ${port}: "
    timeout 3 bash -c "echo '' | nc -w 2 ${TARGET} ${port}" 2>/dev/null | head -1 || echo "(no banner)"
done

echo -e "\n${GREEN}[+] Results saved to /tmp/nmap_*_${TARGET}.txt${NC}"
