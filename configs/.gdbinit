# ============================================
# InCTF 2026 Finals — GDB init
# TEAM_UNFINDABLES
# ============================================

# Load pwndbg (if installed)
# pwndbg is typically auto-loaded via its install script

# Disable pagination
set pagination off

# Disable confirmation prompts
set confirm off

# Follow child on fork (useful for pwn challenges)
set follow-fork-mode child

# Detect forked processes
set detach-on-fork off

# Intel syntax for assembly
set disassembly-flavor intel

# Print arrays nicely
set print array on
set print pretty on

# Enable history
set history save on
set history size 10000
set history filename ~/.gdb_history

# Useful aliases
define hook-stop
    # Show context on every stop
    info registers
end

# Quick commands
define xr
    x/20gx $rsp
end
document xr
    Show 20 qwords from RSP (stack dump)
end

define xi
    x/20i $rip
end
document xi
    Show 20 instructions from RIP
end

define xs
    x/s $1
end

# Heap commands
define hchunks
    heap chunks
end

define hbins
    heap bins
end

# Allow loading .gdbinit from current directory
set auto-load safe-path /
