# Cross-Directory Command Reference

All consortium commands can be run from ANY researcher home directory!

## Available Commands from Any Researcher Directory

When working in any researcher directory (e.g., `consortium/elena-vasquez/`), you have access to:

### 🧭 Orientation & Identity
```bash
# Identify current researcher context
./claude-orient-consortium

# Get help on orientation
./claude-orient-consortium --help
```

### 🔄 Session Management
```bash
# Start a new coordinated session
./claude-consortium-session start

# Check active sessions and conflicts
./claude-consortium-session status

# Sync with other researchers
./claude-consortium-session sync

# Compact current session
./claude-consortium-session compact

# Get help on session management
./claude-consortium-session help
```

### 💬 Claude Slash Commands
Available in any Claude Code session:
```
# Consortium-aware session compacting
/consortium-compact

# MCP-resilient synchronization
/mcp-resilient-sync
```

## Examples from Different Directories

### From Aria's Security Research:
```bash
cd consortium/aria-blackwood
./claude-orient-consortium          # Shows: Dr. Aria Blackwood, Security
./claude-consortium-session status  # Shows all active sessions
```

### From Elena's Statistical Analysis:
```bash
cd consortium/elena-vasquez
./claude-orient-consortium          # Shows: Dr. Elena Vasquez, Statistics
./claude-consortium-session start   # Starts session as Elena
```

### From Marcus's Distributed Systems:
```bash
cd consortium/marcus-chen
./claude-orient-consortium          # Shows: Dr. Marcus Chen, Distributed
./claude-consortium-session sync    # Syncs with all researchers
```

## How It Works

Each researcher directory contains symlinks to the main commands:
```
consortium/researcher-name/
├── claude-orient-consortium -> ../../claude-orient-consortium
├── claude-consortium-session -> ../../claude-consortium-session
└── .claude/commands/
    └── claude-orient-consortium -> ../../../.claude/commands/claude-orient-consortium
```

These symlinks ensure:
- ✅ Commands work identically from any researcher directory
- ✅ Researcher context is automatically detected
- ✅ No need to navigate to root directory
- ✅ Consistent experience across all workspaces

## Quick Command Cheatsheet

| Command | Purpose | Works From |
|---------|---------|------------|
| `./claude-orient-consortium` | Identify researcher context | Any researcher dir |
| `./claude-consortium-session start` | Start coordinated session | Any researcher dir |
| `./claude-consortium-session status` | Check active sessions | Any researcher dir |
| `./claude-consortium-session sync` | Sync with others | Any researcher dir |
| `/consortium-compact` | Compact with awareness | Any Claude session |
| `/mcp-resilient-sync` | MCP-resilient sync | Any Claude session |

## Troubleshooting

If a command doesn't work from a researcher directory:

1. **Check symlinks exist:**
   ```bash
   ls -la | grep claude-
   ```

2. **Recreate if missing:**
   ```bash
   ln -sf ../../claude-orient-consortium .
   ln -sf ../../claude-consortium-session .
   ```

3. **Verify from root directory:**
   ```bash
   cd ../.. && ./claude-consortium-session status
   ```

All commands are designed to work seamlessly across the entire consortium!