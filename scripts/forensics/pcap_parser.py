#!/usr/bin/env python3
"""
InCTF 2026 Finals — PCAP Analysis Helper
TEAM_UNFINDABLES (FIN-030)
"""
import subprocess, sys, os

def analyze_pcap(filepath):
    if not os.path.exists(filepath):
        print(f"[-] File not found: {filepath}")
        return

    print(f"\n{'='*60}")
    print(f"  PCAP Analysis: {filepath}")
    print(f"{'='*60}")

    def run(cmd):
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            return r.stdout
        except:
            return ""

    # Protocol hierarchy
    print("\n[*] Protocol Hierarchy:")
    print(run(f'tshark -r "{filepath}" -q -z io,phs'))

    # Conversations
    print("\n[*] Top Conversations:")
    print(run(f'tshark -r "{filepath}" -q -z conv,tcp | head -20'))

    # HTTP requests
    print("\n[*] HTTP Requests:")
    print(run(f'tshark -r "{filepath}" -Y http.request -T fields -e ip.src -e http.request.method -e http.host -e http.request.uri | head -30'))

    # DNS queries
    print("\n[*] DNS Queries:")
    print(run(f'tshark -r "{filepath}" -Y "dns.flags.response == 0" -T fields -e dns.qry.name | sort -u | head -30'))

    # Credentials (FTP, HTTP Basic, etc.)
    print("\n[*] Possible Credentials:")
    print(run(f'tshark -r "{filepath}" -Y "ftp.request.command == USER || ftp.request.command == PASS" -T fields -e ftp.request.command -e ftp.request.arg'))
    print(run(f'tshark -r "{filepath}" -Y http.authorization -T fields -e http.authorization | head -10'))

    # Interesting strings
    print("\n[*] Flag-like strings:")
    print(run(f'tshark -r "{filepath}" -T fields -e data.text 2>/dev/null | grep -ioE "(flag|inctf|ctf)\\{{[^}}]+\\}}" | sort -u'))

    # Extract files
    print("\n[*] Extracting HTTP objects...")
    extract_dir = f"{filepath}_extracted"
    os.makedirs(extract_dir, exist_ok=True)
    run(f'tshark -r "{filepath}" --export-objects http,{extract_dir} 2>/dev/null')
    files = os.listdir(extract_dir)
    if files:
        print(f"  Extracted {len(files)} files to {extract_dir}/")
        for f in files[:10]:
            print(f"    - {f}")
    else:
        print("  No HTTP objects extracted")

    # TCP streams count
    streams = run(f'tshark -r "{filepath}" -T fields -e tcp.stream | sort -un | tail -1').strip()
    if streams:
        print(f"\n[*] Total TCP streams: {streams}")
        print("  Use: tshark -r file.pcap -q -z follow,tcp,ascii,<stream_number>")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 pcap_parser.py <pcap_file>")
        sys.exit(1)
    analyze_pcap(sys.argv[1])
