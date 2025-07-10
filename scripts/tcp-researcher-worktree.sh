#!/bin/bash
# TCP Researcher Worktree Management Script
# Enables parallel Claude Code sessions for consortium researchers

set -euo pipefail

# Configuration
WORKTREE_ROOT="${TCP_WORKTREE_ROOT:-${HOME}/tcp-worktrees}"
MAIN_REPO_PATH="$(git rev-parse --show-toplevel 2>/dev/null || echo "${PWD}")"
RESEARCHERS=("aria-blackwood" "elena-vasquez" "marcus-chen" "yuki-tanaka" "sam-mitchell" "alex-rivera" "claude-sonnet")

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Validate researcher name
validate_researcher() {
    local researcher=$1
    if [[ ! " ${RESEARCHERS[@]} " =~ " ${researcher} " ]]; then
        log_error "Unknown researcher: $researcher"
        echo "Valid researchers: ${RESEARCHERS[*]}"
        exit 1
    fi
}

# Create worktree for researcher
setup_worktree() {
    local researcher=$1
    local gate=$2
    local feature=${3:-""}
    
    validate_researcher "$researcher"
    
    # Construct branch name
    local branch_name="gate${gate}-${researcher}"
    if [[ -n "$feature" ]]; then
        branch_name="${branch_name}-${feature}"
    fi
    
    local worktree_dir="${WORKTREE_ROOT}/${researcher}-gate${gate}"
    if [[ -n "$feature" ]]; then
        worktree_dir="${worktree_dir}-${feature}"
    fi
    
    # Check if worktree already exists
    if [[ -d "$worktree_dir" ]]; then
        log_warning "Worktree already exists at: $worktree_dir"
        read -p "Remove and recreate? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git worktree remove "$worktree_dir" --force
        else
            log_info "Entering existing worktree..."
            cd "$worktree_dir"
            return 0
        fi
    fi
    
    # Create worktree directory
    mkdir -p "$WORKTREE_ROOT"
    
    log_info "Creating worktree for ${researcher} at Gate ${gate}..."
    
    # Create new branch from main and add worktree
    cd "$MAIN_REPO_PATH"
    git worktree add -b "$branch_name" "$worktree_dir" main
    
    # Initialize researcher environment
    cd "$worktree_dir"
    
    # Copy researcher-specific configurations
    if [[ -d "${MAIN_REPO_PATH}/consortium/${researcher}/.claude" ]]; then
        cp -r "${MAIN_REPO_PATH}/consortium/${researcher}/.claude" ./
        log_info "Copied .claude configuration"
    fi
    
    if [[ -f "${MAIN_REPO_PATH}/consortium/${researcher}/CLAUDE.md" ]]; then
        cp "${MAIN_REPO_PATH}/consortium/${researcher}/CLAUDE.md" ./
        log_info "Copied CLAUDE.md"
    fi
    
    # Copy identity context if exists
    if [[ -f "${MAIN_REPO_PATH}/consortium/${researcher}/IDENTITY_CONTEXT_REMINDER.md" ]]; then
        cp "${MAIN_REPO_PATH}/consortium/${researcher}/IDENTITY_CONTEXT_REMINDER.md" ./
        log_info "Copied identity context"
    fi
    
    # Install dependencies if poetry.lock exists
    if [[ -f "poetry.lock" ]]; then
        log_info "Installing dependencies with Poetry..."
        poetry install --quiet
    fi
    
    # Create initial commit
    git add .
    git commit -m "init: Setup worktree for ${researcher} at Gate ${gate}

Initialized isolated development environment for parallel Claude Code session.

Branch: ${branch_name}
Researcher: ${researcher}
Gate: ${gate}
${feature:+Feature: ${feature}}

Co-Authored-By: TCP Worktree Setup <tcp@consortium.ai>" || true
    
    log_success "Worktree created at: $worktree_dir"
    log_info "Branch: $branch_name"
    
    # Provide next steps
    echo
    echo "Next steps:"
    echo "1. cd $worktree_dir"
    echo "2. claude"
    echo "3. Start your Gate ${gate} research!"
}

# List all TCP worktrees
list_worktrees() {
    log_info "Active TCP Worktrees:"
    echo
    
    git worktree list | while IFS= read -r line; do
        if [[ "$line" =~ gate[0-9] ]]; then
            # Extract path and branch
            path=$(echo "$line" | awk '{print $1}')
            branch=$(echo "$line" | grep -o '\[.*\]' | tr -d '[]')
            
            # Get last commit info
            if [[ -d "$path" ]]; then
                cd "$path"
                last_commit=$(git log -1 --format="%ar" 2>/dev/null || echo "no commits")
                modified_files=$(git status --porcelain | wc -l | tr -d ' ')
                
                # Determine researcher from branch name
                researcher=$(echo "$branch" | cut -d'-' -f2,3)
                gate=$(echo "$branch" | grep -o 'gate[0-9]' | grep -o '[0-9]')
                
                # Print formatted info
                printf "%-20s Gate %-2s %-40s %s\n" \
                    "$researcher" "$gate" "$path" "($last_commit, $modified_files modified)"
            fi
        fi
    done
    
    cd "$MAIN_REPO_PATH"
}

# Remove a worktree
cleanup_worktree() {
    local worktree_name=$1
    
    # Find the worktree path
    local worktree_path=$(git worktree list | grep "$worktree_name" | awk '{print $1}')
    
    if [[ -z "$worktree_path" ]]; then
        log_error "Worktree not found: $worktree_name"
        list_worktrees
        exit 1
    fi
    
    # Check for uncommitted changes
    cd "$worktree_path"
    if [[ -n $(git status --porcelain) ]]; then
        log_warning "Uncommitted changes in worktree!"
        git status --short
        read -p "Proceed with removal? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    cd "$MAIN_REPO_PATH"
    
    log_info "Removing worktree: $worktree_path"
    git worktree remove "$worktree_path" --force
    
    # Also remove the branch if it's not checked out elsewhere
    local branch_name=$(git worktree list | grep "$worktree_name" | grep -o '\[.*\]' | tr -d '[]')
    if [[ -n "$branch_name" ]]; then
        git branch -D "$branch_name" 2>/dev/null || true
    fi
    
    log_success "Worktree removed"
}

# Check for session conflicts
check_conflicts() {
    log_info "Checking for potential conflicts..."
    
    local conflict_found=false
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    
    # Get list of modified files in current branch
    local current_files=$(git diff --name-only main...HEAD | sort)
    
    if [[ -z "$current_files" ]]; then
        log_info "No modified files in current branch"
        return 0
    fi
    
    # Check each worktree
    git worktree list --porcelain | grep "^worktree " | while read -r line; do
        local worktree_path=${line#worktree }
        
        if [[ "$worktree_path" != "$PWD" && -d "$worktree_path" ]]; then
            cd "$worktree_path"
            local worktree_branch=$(git rev-parse --abbrev-ref HEAD)
            local worktree_files=$(git diff --name-only main...HEAD 2>/dev/null | sort)
            
            if [[ -n "$worktree_files" ]]; then
                # Find overlapping files
                local conflicts=$(comm -12 <(echo "$current_files") <(echo "$worktree_files"))
                
                if [[ -n "$conflicts" ]]; then
                    conflict_found=true
                    log_warning "Potential conflicts with $worktree_branch:"
                    echo "$conflicts" | sed 's/^/  - /'
                fi
            fi
        fi
    done
    
    cd "$MAIN_REPO_PATH"
    
    if [[ "$conflict_found" == false ]]; then
        log_success "No conflicts detected"
    fi
}

# Launch Claude in worktree
launch_claude() {
    local researcher=$1
    local gate=$2
    
    validate_researcher "$researcher"
    
    local worktree_dir="${WORKTREE_ROOT}/${researcher}-gate${gate}"
    
    if [[ ! -d "$worktree_dir" ]]; then
        log_error "Worktree not found: $worktree_dir"
        echo "Run: $0 setup $researcher $gate"
        exit 1
    fi
    
    log_info "Launching Claude for $researcher at Gate $gate..."
    
    # On macOS, open new Terminal window
    if [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e "
            tell application \"Terminal\"
                do script \"cd $worktree_dir && claude\"
                activate
            end tell
        "
    else
        # On Linux, try common terminal emulators
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "cd $worktree_dir && claude; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -e "cd $worktree_dir && claude; bash" &
        else
            log_error "No supported terminal emulator found"
            echo "Please manually run: cd $worktree_dir && claude"
        fi
    fi
}

# Show usage
usage() {
    cat << EOF
TCP Researcher Worktree Management

Usage: $0 <command> [arguments]

Commands:
    setup <researcher> <gate> [feature]
        Create a new worktree for researcher at specified gate
        Example: $0 setup aria-blackwood 3
        Example: $0 setup yuki-tanaka 4 performance-opt

    list
        List all active TCP worktrees with status
        
    cleanup <worktree-name>
        Remove a worktree and its branch
        Example: $0 cleanup aria-gate3
        
    conflicts
        Check for file conflicts between worktrees
        
    launch <researcher> <gate>
        Launch Claude in researcher's worktree
        Example: $0 launch marcus-chen 5

Available researchers:
    ${RESEARCHERS[*]}

Environment variables:
    TCP_WORKTREE_ROOT - Base directory for worktrees (default: ~/tcp-worktrees)
EOF
}

# Main command dispatcher
case "${1:-}" in
    setup)
        if [[ $# -lt 3 ]]; then
            log_error "Usage: $0 setup <researcher> <gate> [feature]"
            exit 1
        fi
        setup_worktree "$2" "$3" "${4:-}"
        ;;
    list)
        list_worktrees
        ;;
    cleanup)
        if [[ $# -lt 2 ]]; then
            log_error "Usage: $0 cleanup <worktree-name>"
            exit 1
        fi
        cleanup_worktree "$2"
        ;;
    conflicts)
        check_conflicts
        ;;
    launch)
        if [[ $# -lt 3 ]]; then
            log_error "Usage: $0 launch <researcher> <gate>"
            exit 1
        fi
        launch_claude "$2" "$3"
        ;;
    *)
        usage
        exit 1
        ;;
esac