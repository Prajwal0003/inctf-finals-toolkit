#!/usr/bin/env python3
"""
InCTF 2026 Finals — Stego Solver
TEAM_UNFINDABLES (FIN-030)

Multi-format steganography analysis tool.
Usage: python3 stego_solver.py <file>
"""
import subprocess, sys, os, struct

def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout + r.stderr
    except:
        return ""

def analyze_file(filepath):
    if not os.path.exists(filepath):
        print(f"[-] File not found: {filepath}")
        return
    
    ext = os.path.splitext(filepath)[1].lower()
    print(f"\n{'='*60}")
    print(f"  Stego Analysis: {filepath}")
    print(f"{'='*60}")

    # File type
    print(f"\n[*] File type:")
    print(run_cmd(f'file "{filepath}"'))

    # Exiftool metadata
    print(f"\n[*] EXIF metadata:")
    print(run_cmd(f'exiftool "{filepath}"'))

    # Strings
    print(f"\n[*] Interesting strings:")
    strings_out = run_cmd(f'strings "{filepath}" | grep -iE "flag|ctf|inctf|key|password|secret|base64|http"')
    if strings_out.strip():
        print(strings_out)
    else:
        print("  (nothing obvious)")

    # Binwalk
    print(f"\n[*] Binwalk analysis:")
    print(run_cmd(f'binwalk "{filepath}"'))

    # Format-specific checks
    if ext in ['.png']:
        print(f"\n[*] PNG-specific checks:")
        print(run_cmd(f'pngcheck -v "{filepath}"'))
        # Check for zsteg
        print(f"\n[*] zsteg (LSB analysis):")
        print(run_cmd(f'zsteg "{filepath}" 2>/dev/null || echo "zsteg not available"'))

    elif ext in ['.jpg', '.jpeg']:
        print(f"\n[*] JPEG-specific checks:")
        print(f"  steghide extract:")
        print(run_cmd(f'steghide extract -sf "{filepath}" -p "" -f 2>&1 || echo "No data with empty password"'))
        # Try common passwords
        for pw in ['password', 'secret', 'flag', 'ctf', 'inctf']:
            r = run_cmd(f'steghide extract -sf "{filepath}" -p "{pw}" -f 2>&1')
            if 'wrote' in r.lower():
                print(f"  [+] steghide password: {pw}")
                print(r)
                break

    elif ext in ['.wav', '.mp3', '.flac']:
        print(f"\n[*] Audio-specific checks:")
        print("  Try: Audacity (spectrogram view), Sonic Visualiser")
        print("  SSTV: qsstv, robot36")
        print("  DTMF: dtmf-decoder")

    elif ext in ['.pdf']:
        print(f"\n[*] PDF-specific checks:")
        print(run_cmd(f'pdftotext "{filepath}" - 2>/dev/null | head -50'))

    elif ext in ['.zip', '.7z', '.tar', '.gz']:
        print(f"\n[*] Archive analysis:")
        print(run_cmd(f'7z l "{filepath}" 2>/dev/null'))

    # Check for appended data
    print(f"\n[*] Tail bytes (last 200):")
    print(run_cmd(f'xxd "{filepath}" | tail -12'))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 stego_solver.py <file>")
        sys.exit(1)
    analyze_file(sys.argv[1])
