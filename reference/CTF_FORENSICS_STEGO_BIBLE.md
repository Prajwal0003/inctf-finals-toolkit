# 🔍 CTF FORENSICS & STEGANOGRAPHY MASTER BIBLE
### InCTF 2026 Finals — Zero to Hero Reference (Rule 14 Offline Compliant)

---

## 1. Initial File Triage & Magic Byte Inspection

```bash
file evidence.*              # Determine true file type regardless of extension
xxd evidence | head -n 5     # View hex header (magic bytes)
strings -n 8 evidence | grep -iE 'inctf|flag|pass|key|http' # Quick string hunt
```

### Common Magic Bytes (Hex Headers):
| File Type | Magic Bytes (Hex) | Trailer / End Bytes |
|---|---|---|
| **PNG** | `89 50 4E 47 0D 0A 1A 0A` | `49 45 4E 44 AE 42 60 82` (`IEND`) |
| **JPEG / JPG** | `FF D8 FF` | `FF D9` |
| **GIF** | `47 49 46 38 37 61` or `47 49 46 38 39 61` | `00 3B` |
| **ZIP / DOCX / APK** | `50 4B 03 04` | `50 4B 05 06` |
| **PDF** | `25 50 44 46` (`%PDF`) | `25 25 45 4F 46` (`%%EOF`) |
| **PCAP / PCAPNG** | `D4 C3 B2 A1` / `0A 0D 0D 0A` | - |
| **ELF Binary** | `7F 45 4C 46` (`\x7fELF`) | - |

---

## 2. Hidden File & Archive Extraction

```bash
# 1. Binwalk (Automated carve & extract):
binwalk evidence.png                       # Scan for embedded files
binwalk -e -M --run-as=root evidence.png   # Recursively extract everything

# 2. Foremost (File carving based on headers):
foremost -i evidence.dd -o output_dir/

# 3. Bulk Extractor (Extract URLs, emails, IP addresses):
bulk_extractor -o bulk_out/ evidence.raw
```

---

## 3. Image Steganography (PNG, JPG, BMP)

### Metadata & Headers:
```bash
exiftool image.jpg                         # Check comments, GPS coordinates, Artist tags
pngcheck -v image.png                      # Check for corrupted CRC or altered dimensions (IHDR)
```

### LSB (Least Significant Bit) & Stego Tools:
```bash
# 1. PNG & BMP (zsteg - The King of PNG stego):
zsteg -a image.png                         # Runs all LSB combinations, checks for zip/text

# 2. JPEG / JPG (steghide & stegseek):
steghide extract -sf image.jpg             # Prompts for passphrase (press Enter for blank)
stegseek image.jpg /usr/share/wordlists/rockyou.txt # Fast brute force cracking in <1 second!

# 3. Outguess:
outguess -r -k "password" image.jpg flag.txt
```

---

## 4. Audio Steganography (.wav, .mp3)

1. **Spectrogram Analysis (Visual hidden text in audio):**
   - Open file in **Audacity** or **Sonic Visualiser**.
   - In Audacity: Click track name dropdown -> Select **Spectrogram** view.
   - Zoom in/out to reveal hidden text drawn in frequencies.

2. **DTMF / Dial Tones (Phone Number Audio):**
   - Use online/offline DTMF decoder or check frequency peaks (e.g. 697-941 Hz + 1209-1477 Hz).

3. **Morse Code Audio:**
   - Listen for short (dit) and long (dah) beeps, or view waveform peaks.

---

## 5. Network Forensics (PCAP / PCAPNG)

### Wireshark GUI Steps:
1. **Statistics -> Protocol Hierarchy:** See top protocols (HTTP, DNS, ICMP, FTP).
2. **Statistics -> Conversations:** Identify suspect IP addresses & data volume.
3. **File -> Export Objects -> HTTP / SMB / TFTP / IMF:** Instantly dump transferred files!
4. **Follow Stream:** Right-click packet -> `Follow` -> `TCP Stream` or `HTTP Stream`.

### TShark Command Line Tricks:
```bash
# Extract all HTTP URLs:
tshark -r capture.pcap -Y "http.request" -T fields -e http.host -e http.request.uri

# Extract DNS Queries (Look for DNS Tunneling / Base64 subdomains):
tshark -r capture.pcap -Y "dns.flags.response == 0" -T fields -e dns.qry.name | sort -u

# Extract ICMP Data (Ping Tunneling):
tshark -r capture.pcap -Y "icmp" -T fields -e data | xxd -r -p

# Export all HTTP files to folder:
tshark -r capture.pcap --export-objects http,./extracted_files/
```

---

## 6. Memory Forensics (Volatility 3)

```bash
# 1. Identify Windows OS info:
vol -f memory.raw windows.info

# 2. List running processes:
vol -f memory.raw windows.pslist
vol -f memory.raw windows.pstree
vol -f memory.raw windows.cmdline.CmdLine    # View command line arguments!

# 3. Extract Passwords & Hashes:
vol -f memory.raw windows.hashdump
vol -f memory.raw windows.lsadump

# 4. Search and Dump Files:
vol -f memory.raw windows.filescan | grep -iE "flag|secret|desktop|download"
# Dump file by its memory virtual address:
vol -f memory.raw windows.dumpfiles --virtaddr 0xdeadbeef

# 5. Linux Memory Dump:
vol -f memory.raw linux.bash.Bash           # View bash history from RAM!
```

---

## 7. Cracking Encrypted Archives (ZIP, 7z, RAR)

```bash
# 1. Extract hash from archive:
zip2john secret.zip > zip.hash
rar2john secret.rar > rar.hash
7z2john secret.7z > 7z.hash

# 2. Crack with John:
john zip.hash --wordlist=/usr/share/wordlists/rockyou.txt

# 3. Crack with Hashcat:
# Mode 13600 (WinZip) or 11600 (7-Zip)
hashcat -m 13600 zip.hash /usr/share/wordlists/rockyou.txt
```
