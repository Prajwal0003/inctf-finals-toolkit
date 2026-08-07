# 🐧 CTF LINUX & KALI SURVIVAL GUIDE
### InCTF 2026 Finals — On-Site Environment & VM Setup (Rule 14 Offline Compliant)

---

## 1. Transferring Files Between Host & Kali VM (Offline)

### Method 1: Local HTTP Server (Host-Only Network)
If the host and Kali VM are on the same virtual network adapter (NAT / Host-Only / Bridged):
1. **On the sender machine (e.g. Host with challenge files):**
   ```bash
   python3 -m http.server 8000
   ```
2. **On the receiver machine (Inside Kali VM):**
   ```bash
   # Check host IP (usually 10.0.2.2 or 192.168.56.1)
   wget http://10.0.2.2:8000/challenge.zip
   # or
   curl http://10.0.2.2:8000/challenge.zip -o challenge.zip
   ```

### Method 2: The Base64 Copy-Paste Trick (Works 100% via Terminal / Clipboard)
If network sharing or drag-and-drop between Host and VM is completely blocked:
1. **On Host (Encode file to Base64 text):**
   ```bash
   base64 -w 0 challenge_binary > b64.txt
   # Copy the contents of b64.txt
   ```
2. **Inside Kali VM (Decode back to binary):**
   ```bash
   echo "PASTE_BASE64_STRING_HERE" | base64 -d > challenge_binary
   chmod +x challenge_binary
   ```

### Method 3: VirtualBox Shared Folders
1. In VirtualBox Menu: **Devices -> Shared Folders -> Shared Folder Settings...**
2. Add a folder from your host (e.g. `C:\Users\prajw\Downloads` or your Pendrive), check **Auto-mount**.
3. Inside Kali Linux terminal:
   ```bash
   sudo mkdir -p /mnt/shared
   sudo mount -t vboxsf [FolderName] /mnt/shared
   cd /mnt/shared
   ```

---

## 2. Linux Terminal Survival & Refresher

### Navigation & Search:
```bash
pwd                           # Print current working directory
ls -la                        # List all files including hidden with sizes/permissions
find . -name "*.py"           # Find all Python files recursively
find . -type f -exec grep -Hn "inctf{" {} + # Search for flag in EVERY file in current folder
grep -rni "flag" .            # Recursive case-insensitive line-number search
chmod +x script.sh            # Make file executable
chmod 777 folder/             # Full read/write/execute permissions
```

### File Inspection:
```bash
head -n 20 file.txt           # View first 20 lines
tail -n 20 file.txt           # View last 20 lines
tail -f access.log            # Follow log file in real time
wc -l wordlist.txt            # Count lines in file
sort list.txt | uniq -c       # Count unique occurrences
xxd file | head -n 10         # Hex dump view
xxd -r hex.txt > binary       # Reverse hex dump back to binary
```

### Process Management:
```bash
ps aux | grep python         # Find running python processes
kill -9 <PID>                 # Force kill process by PID
killall -9 gdb                # Kill all stuck GDB instances
netstat -tulpn                # See which local ports are open/listening
ss -tulpn                     # Modern socket statistics
```

---

## 3. Python Quick One-Liners (Instant Solvers)

```python
# 1. Base64 Decode:
python3 -c "import base64; print(base64.b64decode('aW5jdGZ7dGVzdH0=').decode())"

# 2. Hex to ASCII:
python3 -c "print(bytes.fromhex('696e6374667b746573747d').decode())"

# 3. URL Decode:
python3 -c "import urllib.parse; print(urllib.parse.unquote('%69%6e%63%74%66'))"

# 4. ROT13:
python3 -c "import codecs; print(codecs.decode('vapgs{grfg}', 'rot_13'))"

# 5. Quick Socket Connection (Netcat in Python):
python3 -c "
import socket
s = socket.socket()
s.connect(('127.0.0.1', 9001))
print(s.recv(1024).decode())
s.sendall(b'admin\n')
print(s.recv(1024).decode())
"
```

---

## 4. Working Without Root / Sudo on Host

If the host machine has no `sudo`:
1. **Install Python Packages locally without sudo:**
   ```bash
   pip install --user pwntools pycryptodome z3-solver requests
   ```
2. **Use `/tmp` for writable storage:**
   `/tmp` and `/var/tmp` are always 100% writable by any non-root user. Compile your scripts and store artifacts in `/tmp`.
3. **Execute everything inside your Kali Linux VM:**
   Inside Kali in VirtualBox, you are `root` (or `sudo su` with password `kali` or `toor`). Use Kali for all heavy lifting!
