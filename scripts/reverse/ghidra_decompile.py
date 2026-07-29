#!/usr/bin/env python3
"""
InCTF 2026 Finals — Ghidra Headless Auto-Decompiler
TEAM_UNFINDABLES (FIN-030)

Ghidra's GUI can take a long time to open and navigate during a fast-paced CTF.
This script uses Ghidra's "Headless" mode to automatically analyze a binary 
and dump all of its C pseudo-code directly into a single text file instantly!

Usage: python3 ghidra_decompile.py <binary>
Output: <binary>.c (containing all decompiled C code)
"""
import os, sys, subprocess, tempfile, shutil

G, Y, C, R, B, N = '\033[92m', '\033[93m', '\033[96m', '\033[91m', '\033[1m', '\033[0m'

# Common paths for Ghidra in Arch Linux
GHIDRA_PATHS = [
    "/opt/ghidra/support/analyzeHeadless",
    "/usr/share/ghidra/support/analyzeHeadless"
]

def find_ghidra():
    # Check common paths
    for path in GHIDRA_PATHS:
        if os.path.exists(path):
            return path
            
    # Check system PATH
    path = shutil.which("analyzeHeadless")
    if path:
        return path
        
    return None

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 ghidra_decompile.py <binary_file>")
        sys.exit(1)
        
    binary = os.path.abspath(sys.argv[1])
    
    if not os.path.exists(binary):
        print(f"{R}[-] File not found: {binary}{N}")
        sys.exit(1)

    print(f"\n{B}{C}{'='*60}{N}")
    print(f"  {B}Ghidra Headless Auto-Decompiler{N}")
    print(f"{B}{C}{'='*60}{N}\n")

    ghidra_headless = find_ghidra()
    if not ghidra_headless:
        print(f"{R}[-] Could not find 'analyzeHeadless' executable.{N}")
        print(f"    Make sure Ghidra is installed via the pacman-packages.txt")
        sys.exit(1)

    out_c_file = binary + ".c"
    
    print(f"[*] Found Ghidra at: {ghidra_headless}")
    print(f"[*] Generating Jython Decompilation Script...")
    
    # This is a Jython script that Ghidra will run internally
    script_content = """
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
import os

print("\\n[*] Starting internal decompilation engine...")
monitor = ConsoleTaskMonitor()
ifc = DecompInterface()
ifc.openProgram(currentProgram)

out_file = getScriptArgs()[0]
print("[*] Dumping to: " + out_file)

with open(out_file, 'w') as f:
    fm = currentProgram.getFunctionManager()
    funcs = fm.getFunctions(True)
    count = 0
    for func in funcs:
        # Skip external/thunk functions to keep output clean
        if func.isExternal() or func.isThunk():
            continue
            
        res = ifc.decompileFunction(func, 0, monitor)
        if res and res.getDecompiledFunction():
            f.write("// ===============================================================\\n")
            f.write("// Function: " + func.getName() + "\\n")
            f.write("// Address:  " + str(func.getEntryPoint()) + "\\n")
            f.write("// ===============================================================\\n")
            f.write(res.getDecompiledFunction().getC() + "\\n\\n\\n")
            count += 1
            
print("[+] Successfully dumped " + str(count) + " functions.")
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "AutoDump.py")
        with open(script_path, "w") as f:
            f.write(script_content)
            
        print(f"[*] Running Ghidra Headless Analyzer (This will take 1-2 minutes)...")
        print(f"[*] Please wait...\n")
        
        # Command line arguments for Ghidra Headless Analyzer
        cmd = [
            ghidra_headless,
            tmpdir,               # Project location
            "TempProj",           # Project name
            "-import", binary,    # File to import
            "-scriptPath", tmpdir,# Where to find our script
            "-postScript", "AutoDump.py", out_c_file, # Run script and pass out_file as arg
            "-deleteProject"      # Do not save the temporary project
        ]
        
        try:
            # We hide stdout to prevent Ghidra's massive log spam, but capture stderr if it crashes
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0 and os.path.exists(out_c_file):
                print(f"{G}{B}[+] Success! All C pseudo-code saved to:{N} {C}{out_c_file}{N}")
                print(f"    You can now open it in vim or use 'grep' to search for logic!")
            else:
                print(f"{R}[-] Ghidra failed or did not generate the output.{N}")
                print(f"Error output:\n{result.stderr}")
        except Exception as e:
            print(f"{R}[-] Error executing Ghidra: {e}{N}")

if __name__ == "__main__":
    main()
