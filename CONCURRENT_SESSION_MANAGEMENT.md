# Concurrent Session Management for TCP Research Consortium

## Overview

This system provides robust concurrent session management for the TCP Research Consortium, enabling multiple Claude Code sessions to operate safely across different researcher workspaces while maintaining coordination and preventing conflicts.

## System Components

### 1. Consortium-Aware Compact Command
**File:** `.claude/commands/consortium-compact`

Enhances the standard `/compact` command with consortium-specific awareness:
- **Researcher Identity Preservation**: Maintains researcher context and gate responsibilities
- **Protocol State Management**: Tracks TCP protocol changes and compatibility
- **Session Coordination**: Detects other active sessions and potential conflicts
- **External Validation Context**: Preserves audit-ready documentation standards
- **Handoff Preparation**: Creates structured handoff documentation for next sessions

**Usage:**
```bash
# Use as a slash command in Claude
/consortium-compact
```

### 2. Git-Based Session Coordination
**Files:** 
- `scripts/claude-consortium-session` (main script)
- `claude-consortium-session` (wrapper)

Provides robust VCS-based session management independent of MCP:
- **Session Detection**: Identifies active Claude sessions across all researchers
- **Conflict Prevention**: Detects protocol conflicts and cross-researcher dependencies
- **Branch Management**: Creates session branches with researcher context
- **State Sharing**: Uses git refs and notes for session coordination

**Commands:**
```bash
# Start a new session (auto-detects researcher from directory)
./claude-consortium-session start

# Start session for specific researcher
./claude-consortium-session start elena-vasquez

# Check all active sessions and conflicts
./claude-consortium-session status

# Sync with other researchers' changes
./claude-consortium-session sync

# Compact current session
./claude-consortium-session compact
```

### 3. MCP-Resilient Coordination
**File:** `.claude/commands/mcp-resilient-sync`

Handles MCP timeout scenarios gracefully:
- **Health Monitoring**: Tests MCP server availability with timeouts
- **Fallback Strategy**: Uses git-based coordination when MCP is unavailable
- **Hybrid Mode**: Seamlessly switches between MCP and git coordination
- **Session Recovery**: Provides emergency session recovery procedures

**Usage:**
```bash
# Use as a slash command in Claude
/mcp-resilient-sync
```

### 4. GitHub Actions Integration
**File:** `.github/workflows/claude-session-sync.yml`

Provides automated session monitoring and conflict detection:
- **Session Detection**: Identifies Claude session branches and references
- **Protocol Analysis**: Detects protocol changes across researchers
- **Conflict Alerts**: Creates issues for high-conflict scenarios
- **Coordination Reports**: Generates session reports on pull requests

**Triggers:**
- Push to `claude-*` branches
- Pull requests to main
- Manual workflow dispatch

## Usage Workflows

### Starting a New Session

1. **Navigate to researcher workspace:**
   ```bash
   cd consortium/elena-vasquez
   ```

2. **Check current status:**
   ```bash
   ../../claude-consortium-session status
   ```

3. **Start coordinated session:**
   ```bash
   ../../claude-consortium-session start
   ```

4. **Confirm researcher identity:**
   ```bash
   ./claude-orient-consortium
   ```

### During Active Session

1. **Sync with other researchers periodically:**
   ```bash
   /mcp-resilient-sync
   ```

2. **Check for conflicts before major changes:**
   ```bash
   ../../claude-consortium-session status
   ```

3. **Use consortium-aware compacting:**
   ```bash
   /consortium-compact
   ```

### Ending a Session

1. **Compact session with handoff preparation:**
   ```bash
   /consortium-compact
   ```

2. **Clean up session state:**
   ```bash
   ../../claude-consortium-session compact
   ```

## Key Features

### Researcher Identity Awareness
- **Auto-Detection**: Identifies researcher from working directory
- **Context Preservation**: Maintains researcher specialization and gate responsibilities
- **Permission Integration**: Works with existing researcher-specific permissions

### Gate-and-Key Framework Integration
- **Gate Status Tracking**: Monitors owned vs. other researchers' gates
- **Dependency Management**: Tracks cross-researcher gate dependencies
- **Progress Coordination**: Ensures gate completion is properly coordinated

### External Validation Support
- **Pre-Registered Analysis**: Supports statistical rigor requirements
- **Conservative Claims**: Maintains external validation standards
- **Audit Readiness**: Prepares documentation for independent review

### MCP Resilience
- **Timeout Handling**: Graceful degradation when MCP services are slow
- **Fallback Coordination**: Git-based coordination independent of MCP
- **Health Monitoring**: Automatic detection of MCP service status
- **Hybrid Operations**: Seamless switching between coordination modes

### Conflict Prevention
- **Protocol Change Detection**: Identifies changes affecting other researchers
- **Session Lock Management**: Prevents conflicting concurrent work
- **Dependency Tracking**: Manages cross-researcher work dependencies
- **Early Warning System**: Alerts before conflicts become problems

## File Structure

```
tcp-research-consortium/
├── .claude/commands/
│   ├── consortium-compact          # Enhanced compact command
│   └── mcp-resilient-sync         # MCP-resilient coordination
├── .github/workflows/
│   └── claude-session-sync.yml    # Automated monitoring
├── scripts/
│   └── claude-consortium-session  # Main session manager
├── claude-consortium-session      # Wrapper script
└── consortium/
    ├── aria-blackwood/
    │   ├── claude-orient-consortium -> ../../claude-orient-consortium
    │   └── .claude/commands/claude-orient-consortium -> ../../../.claude/commands/claude-orient-consortium
    ├── elena-vasquez/
    │   ├── claude-orient-consortium -> ../../claude-orient-consortium
    │   └── .claude/commands/claude-orient-consortium -> ../../../.claude/commands/claude-orient-consortium
    └── [other researchers...]
```

## Emergency Procedures

### MCP and Git Both Unavailable
1. Create local session checkpoint:
   ```bash
   mkdir -p .claude/emergency-sessions
   echo "$(date): Emergency session checkpoint" > .claude/emergency-sessions/session-$(date +%Y%m%d-%H%M%S).md
   ```

2. Document current state manually in session file

3. Use next session to restore coordination

### High Conflict Scenarios
1. GitHub Actions will automatically create an issue
2. All researchers should coordinate via the generated issue
3. Use `./claude-consortium-session sync` to align states
4. Document resolution with `/consortium-compact`

### Session Recovery
If a session becomes orphaned:
1. Clean up session locks: `rm -f .claude-session-*`
2. Reset session refs: `git update-ref -d refs/claude/session-$(whoami)`
3. Start fresh session: `./claude-consortium-session start`

## Integration with Existing Systems

### Works With:
- ✅ Existing `./claude-orient-consortium` command
- ✅ Researcher-specific `.claude/settings.local.json` permissions
- ✅ Gate-and-key framework and identity context files
- ✅ Current git workflow and branch management
- ✅ External validation and audit requirements

### Enhances:
- 🔄 Session coordination across multiple researchers
- 🔄 Protocol change management and conflict detection
- 🔄 MCP timeout resilience and fallback strategies
- 🔄 Automated monitoring and conflict alerts
- 🔄 Documentation and handoff preparation

This system provides the robust concurrent session management needed for the TCP Research Consortium while respecting existing researcher autonomy and specialization.