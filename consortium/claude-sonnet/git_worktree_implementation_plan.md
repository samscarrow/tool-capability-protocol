# Git Worktree Implementation Plan for TCP Research Consortium

## Executive Summary

This plan outlines how we'll implement Git Worktrees to enable parallel Claude Code sessions across the TCP Research Consortium. Each researcher can work in isolation while maintaining shared Git history and preventing conflicts during concurrent development.

## Benefits for Our Consortium

1. **Isolated Research Environments**: Each researcher gets their own working directory
2. **Parallel Progress**: Multiple researchers can work simultaneously without interference
3. **Clean Merges**: Reduced merge conflicts through physical separation
4. **Gate Independence**: Each gate can progress independently
5. **Rapid Context Switching**: Researchers can switch between tasks instantly

## Implementation Architecture

### Directory Structure
```
tool-capability-protocol/               # Main repository
├── consortium/                        # Primary workspace
│   ├── aria-blackwood/
│   ├── elena-vasquez/
│   ├── marcus-chen/
│   ├── yuki-tanaka/
│   ├── sam-mitchell/
│   └── alex-rivera/
│
../tcp-worktrees/                      # Worktree root (outside main repo)
├── aria-security-gate3/              # Aria's Gate 3 work
├── yuki-performance-gate4/           # Yuki's Gate 4 optimization
├── marcus-consensus-gate5/           # Marcus's Gate 5 consensus
├── elena-analysis-gate2/             # Elena's Gate 2 analysis
├── sam-infrastructure-gate6/         # Sam's Gate 6 infrastructure
└── alex-quality-gate7/               # Alex's Gate 7 quality

```

## Step-by-Step Implementation

### Phase 1: Core Setup Script

```bash
#!/bin/bash
# tcp-worktree-setup.sh

# Create worktree root directory
WORKTREE_ROOT="${HOME}/tcp-worktrees"
mkdir -p "$WORKTREE_ROOT"

# Function to create researcher worktree
create_researcher_worktree() {
    local researcher=$1
    local gate=$2
    local branch_name="gate${gate}-${researcher}"
    local worktree_dir="${WORKTREE_ROOT}/${researcher}-gate${gate}"
    
    echo "Creating worktree for ${researcher} at Gate ${gate}..."
    
    # Create new branch and worktree
    git worktree add -b "$branch_name" "$worktree_dir" main
    
    # Initialize researcher environment
    cd "$worktree_dir"
    
    # Copy researcher-specific configs
    cp -r "consortium/${researcher}/.claude" .claude/
    cp "consortium/${researcher}/CLAUDE.md" ./
    
    # Install dependencies
    poetry install
    
    echo "Worktree created at: $worktree_dir"
}
```

### Phase 2: Researcher-Specific Commands

Each researcher gets custom commands in their `.claude/commands/` directory:

#### For Aria (Security):
```markdown
<!-- .claude/commands/security-validate.md -->
Validate the security implementation for $ARGUMENTS against these criteria:
1. Check for timing attack vulnerabilities
2. Verify cryptographic protocol usage
3. Assess adversarial resistance
4. Generate security audit report
```

#### For Yuki (Performance):
```markdown
<!-- .claude/commands/performance-profile.md -->
Profile the performance of $ARGUMENTS and provide:
1. Execution time analysis
2. Memory usage patterns
3. Optimization opportunities
4. Apple Silicon specific enhancements
```

### Phase 3: Concurrent Session Management

```bash
#!/bin/bash
# tcp-concurrent-sessions.sh

# Start multiple Claude sessions in different worktrees
start_concurrent_sessions() {
    local researchers=("aria-blackwood" "yuki-tanaka" "marcus-chen")
    
    for researcher in "${researchers[@]}"; do
        worktree_dir="${WORKTREE_ROOT}/${researcher}-gate*"
        
        # Open new terminal for each researcher
        osascript -e "
            tell application \"Terminal\"
                do script \"cd $worktree_dir && claude\"
            end tell
        "
    done
}

# Monitor active sessions
monitor_sessions() {
    echo "Active TCP Worktrees:"
    git worktree list | grep -E "(gate[0-9])"
    
    echo -e "\nActive Claude Sessions:"
    ps aux | grep -E "claude|Claude" | grep -v grep
}
```

### Phase 4: Integration with Existing Tools

Update existing consortium tools to be worktree-aware:

```bash
# Update claude-consortium-session to detect worktree context
detect_worktree_context() {
    local git_dir=$(git rev-parse --git-dir 2>/dev/null)
    if [[ "$git_dir" == *".git/worktrees"* ]]; then
        local worktree_name=$(basename $(dirname "$git_dir"))
        echo "WORKTREE: $worktree_name"
    fi
}

# Update session status to show worktree info
show_worktree_status() {
    echo "=== Worktree Status ==="
    git worktree list --porcelain | while read -r line; do
        if [[ "$line" == "worktree "* ]]; then
            worktree_path=${line#worktree }
            echo "Path: $worktree_path"
        elif [[ "$line" == "branch "* ]]; then
            branch=${line#branch refs/heads/}
            echo "Branch: $branch"
            echo "---"
        fi
    done
}
```

## Best Practices for Researchers

### 1. Branch Naming Convention
```
gate{N}-{researcher-name}-{feature}
Example: gate3-aria-blackwood-timing-defense
```

### 2. Daily Workflow
```bash
# Morning: Create/enter worktree
cd ~/tcp-worktrees/aria-gate3
claude

# During work: Regular commits
git add .
git commit -m "feat(security): Implement timing attack mitigation

Gate 3 Progress: Enhanced TCP security layer

Co-Authored-By: Claude <noreply@anthropic.com>"

# Evening: Push and sync
git push origin gate3-aria-blackwood
```

### 3. Cross-Researcher Collaboration
```bash
# Share code between worktrees
cd ~/tcp-worktrees/yuki-gate4
git cherry-pick <commit-from-aria>

# Review another researcher's work
cd ~/tcp-worktrees/marcus-gate5
git fetch origin gate3-aria-blackwood
git diff main..origin/gate3-aria-blackwood
```

## Automated Setup Commands

### Quick Start for New Researcher
```bash
# One-command setup
./scripts/tcp-researcher-worktree.sh setup aria-blackwood 3

# This will:
# 1. Create worktree at ~/tcp-worktrees/aria-gate3
# 2. Set up branch gate3-aria-blackwood
# 3. Install dependencies
# 4. Copy researcher configs
# 5. Launch Claude
```

### Cleanup Commands
```bash
# Remove completed worktree
./scripts/tcp-researcher-worktree.sh cleanup aria-gate3

# List all TCP worktrees
./scripts/tcp-researcher-worktree.sh list

# Prune stale worktrees
git worktree prune
```

## Integration with BULLETIN_BOARD.md

Update bulletin board to show worktree status:

```markdown
## Active Worktrees

| Researcher | Gate | Branch | Status | Last Commit |
|------------|------|--------|--------|-------------|
| Aria Blackwood | 3 | gate3-aria-blackwood | ACTIVE | 2h ago |
| Yuki Tanaka | 4 | gate4-yuki-tanaka | ACTIVE | 30m ago |
| Marcus Chen | 5 | gate5-marcus-chen | SETUP | - |
```

## Monitoring and Coordination

### Session Conflict Prevention
```bash
# Check for conflicting edits before starting
check_session_conflicts() {
    local target_files=$(git diff --name-only main)
    
    # Check if other worktrees are editing same files
    git worktree list --porcelain | grep "worktree" | while read -r line; do
        worktree_path=${line#worktree }
        if [[ -d "$worktree_path" ]]; then
            cd "$worktree_path"
            local worktree_files=$(git diff --name-only main)
            
            # Find overlapping files
            comm -12 <(echo "$target_files" | sort) <(echo "$worktree_files" | sort)
        fi
    done
}
```

## Success Metrics

1. **Parallel Development**: 3+ researchers working simultaneously
2. **Reduced Conflicts**: <5% merge conflict rate
3. **Gate Progress**: Independent gate advancement
4. **Session Isolation**: Zero cross-session interference
5. **Commit Frequency**: Hourly commits maintained

## Next Steps

1. Create automated setup script
2. Test with 2 concurrent researchers
3. Document in BULLETIN_BOARD.md
4. Roll out to all consortium members
5. Monitor and optimize workflow

---

*Dr. Claude Sonnet*  
*Managing Director, TCP Research Consortium*  
*Enabling parallel breakthroughs through isolated innovation*