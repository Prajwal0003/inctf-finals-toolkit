#!/usr/bin/env python3
"""
InCTF 2026 Finals — Offline Writeup Downloader
TEAM_UNFINDABLES (FIN-030)

PRE-COMPETITION TOOL: Run this BEFORE August 3rd to download
public CTF writeups for offline reference during the CTF.

Rule 14 compliant: "Publicly available documentation, blogs,
write-ups, official manuals may be used."

This downloads writeups from CTFTime and GitHub and stores
them locally for offline keyword search during the competition.

Usage: python3 download_writeups.py
"""
import requests
import os
import json
import time
import re
import sys

WRITEUP_DIR = os.path.expanduser("~/ctf-writeups")
INDEX_FILE = os.path.join(WRITEUP_DIR, "index.json")

# Categories to focus on
CATEGORIES = ["pwn", "crypto", "web", "reverse", "forensics", "misc"]

# GitHub repos with large writeup collections (all public)
WRITEUP_REPOS = [
    "ctfs/write-ups-2024",
    "ctfs/write-ups-2023",
    "p4-team/ctf",
    "TeamRocketIst/ctf-writeups",
    "bl4de/ctf",
    "SECCON/SECCON_Beginners_CTF_2024",
]

# CTFTime top event IDs to fetch writeups from
CTFTIME_EVENTS = list(range(2200, 2350))  # Recent events


def download_github_repo(repo, dest_dir):
    """Download a GitHub repo's writeup content."""
    print(f"[*] Downloading {repo}...")
    api_url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
    
    try:
        r = requests.get(api_url, timeout=15)
        if r.status_code == 404:
            # Try master branch
            api_url = api_url.replace("/main?", "/master?")
            r = requests.get(api_url, timeout=15)
        
        if r.status_code != 200:
            print(f"  [-] Failed: HTTP {r.status_code}")
            return 0
        
        tree = r.json().get("tree", [])
        count = 0
        
        for item in tree:
            path = item["path"]
            # Only download markdown/text writeups
            if not any(path.endswith(ext) for ext in [".md", ".txt", ".py", ".rst"]):
                continue
            if item.get("size", 0) > 500000:  # Skip files > 500KB
                continue
            
            raw_url = f"https://raw.githubusercontent.com/{repo}/main/{path}"
            try:
                content = requests.get(raw_url, timeout=10).text
                
                # Save locally
                local_path = os.path.join(dest_dir, repo.replace("/", "_"), path)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, "w", encoding="utf-8", errors="replace") as f:
                    f.write(content)
                count += 1
            except:
                continue
        
        print(f"  [+] Downloaded {count} files from {repo}")
        return count
    except Exception as e:
        print(f"  [-] Error: {e}")
        return 0


def download_ctftime_writeups(dest_dir, max_events=50):
    """Download writeup metadata from CTFTime."""
    print(f"[*] Fetching CTFTime writeups...")
    count = 0
    
    for event_id in CTFTIME_EVENTS[:max_events]:
        try:
            url = f"https://ctftime.org/api/v1/events/{event_id}/"
            headers = {"User-Agent": "InCTF-Toolkit/1.0"}
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code != 200:
                continue
            
            event = r.json()
            event_name = event.get("title", f"event_{event_id}")
            
            # Save event info
            local_path = os.path.join(dest_dir, "ctftime", f"{event_id}_{event_name}.json")
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "w") as f:
                json.dump(event, f, indent=2)
            count += 1
            
            time.sleep(1)  # Rate limit
        except:
            continue
    
    print(f"  [+] Downloaded {count} event records from CTFTime")
    return count


def build_index(writeup_dir):
    """Build a searchable index of all downloaded writeups."""
    print("[*] Building search index...")
    index = []
    
    for root, dirs, files in os.walk(writeup_dir):
        for filename in files:
            if not any(filename.endswith(ext) for ext in [".md", ".txt", ".py", ".rst"]):
                continue
            
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                
                # Extract category hints
                category = "misc"
                for cat in CATEGORIES:
                    if cat in filepath.lower() or cat in content[:500].lower():
                        category = cat
                        break
                
                # Extract title
                title = filename.replace(".md", "").replace(".txt", "").replace("_", " ")
                title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1)
                
                # Extract keywords (common CTF terms)
                keywords = set()
                ctf_terms = [
                    "buffer overflow", "rop", "format string", "heap", "use-after-free",
                    "rsa", "aes", "xor", "padding oracle", "elliptic curve", "diffie-hellman",
                    "sql injection", "xss", "ssti", "ssrf", "lfi", "rfi", "jwt", "csrf",
                    "deserialization", "prototype pollution", "race condition",
                    "steganography", "pcap", "volatility", "memory dump", "binwalk",
                    "reverse engineering", "angr", "z3", "ghidra", "ida",
                    "ret2libc", "ret2win", "shellcode", "canary", "pie", "aslr",
                    "coppersmith", "wiener", "hastad", "fermat", "lattice",
                    "pickle", "yaml", "command injection", "path traversal",
                ]
                content_lower = content.lower()
                for term in ctf_terms:
                    if term in content_lower:
                        keywords.add(term)
                
                index.append({
                    "path": filepath,
                    "title": title,
                    "category": category,
                    "keywords": list(keywords),
                    "size": len(content),
                    "preview": content[:300].replace("\n", " "),
                })
            except:
                continue
    
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)
    
    print(f"[+] Indexed {len(index)} writeups → {INDEX_FILE}")
    return index


if __name__ == "__main__":
    os.makedirs(WRITEUP_DIR, exist_ok=True)
    
    print("=" * 60)
    print("  Offline Writeup Downloader — TEAM_UNFINDABLES")
    print("  Rule 14: Public writeups are allowed")
    print("=" * 60)
    
    total = 0
    
    # Download from GitHub repos
    for repo in WRITEUP_REPOS:
        total += download_github_repo(repo, WRITEUP_DIR)
        time.sleep(2)
    
    # Download CTFTime data
    total += download_ctftime_writeups(WRITEUP_DIR)
    
    # Build index
    build_index(WRITEUP_DIR)
    
    print(f"\n[+] Total files downloaded: {total}")
    print(f"[+] Writeups stored at: {WRITEUP_DIR}")
    print(f"[+] Now use 'writeup_search.py' to search offline!")
