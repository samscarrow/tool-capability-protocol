#!/bin/bash
# tcp_branch_sync.sh - Main synchronization script for TCP branches
# Orchestrates the complete synchronization process with validation and logging

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/.tcp_sync_log"

# Configuration
MAIN_BRANCH="main"
EXPERIMENTAL_BRANCH="linguistic-evolution"
SYNC_TYPE="${1:-auto-merge}"  # auto-merge, cherry-pick, manual

echo "🔄 TCP Branch Synchronization Started"
echo "📅 $(date)"
echo "🎯 Sync type: $SYNC_TYPE"
echo "📂 Repository: $SCRIPT_DIR"

# Ensure we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Ensure required branches exist
if ! git rev-parse --verify $MAIN_BRANCH >/dev/null 2>&1; then
    echo "❌ Error: Main branch '$MAIN_BRANCH' does not exist"
    exit 1
fi

if ! git rev-parse --verify $EXPERIMENTAL_BRANCH >/dev/null 2>&1; then
    echo "❌ Error: Experimental branch '$EXPERIMENTAL_BRANCH' does not exist"
    echo "ℹ️  Creating experimental branch from main..."
    git checkout $MAIN_BRANCH
    git checkout -b $EXPERIMENTAL_BRANCH
    git push -u origin $EXPERIMENTAL_BRANCH
    echo "✅ Experimental branch created"
fi

# Pre-sync validation
echo "🔍 Running pre-sync validation..."
if ! "$SCRIPT_DIR/pre_sync_validation.sh"; then
    echo "❌ Pre-sync validation failed"
    exit 1
fi

# Record sync attempt
MAIN_COMMIT=$(git rev-parse $MAIN_BRANCH)
LINGUISTIC_COMMIT=$(git rev-parse $EXPERIMENTAL_BRANCH)

# Initialize log file if it doesn't exist
if [[ ! -f "$LOG_FILE" ]]; then
    echo "# TCP Sync Log - Format: timestamp,main_commit,linguistic_commit,sync_type,conflicts,status" > "$LOG_FILE"
fi

echo "$(date -Iseconds),$MAIN_COMMIT,$LINGUISTIC_COMMIT,$SYNC_TYPE,syncing,in_progress" >> "$LOG_FILE"

# Function to update log with final status
update_log_status() {
    local status="$1"
    local conflicts="${2:-0}"
    
    # Update the last line in the log
    if [[ -f "$LOG_FILE" ]]; then
        # Use a temporary file for cross-platform compatibility
        local temp_file=$(mktemp)
        head -n -1 "$LOG_FILE" > "$temp_file"
        echo "$(date -Iseconds),$MAIN_COMMIT,$(git rev-parse $EXPERIMENTAL_BRANCH),$SYNC_TYPE,$conflicts,$status" >> "$temp_file"
        mv "$temp_file" "$LOG_FILE"
    fi
}

# Function to handle sync failure
handle_sync_failure() {
    local error_msg="$1"
    echo "❌ Sync failed: $error_msg"
    update_log_status "failed" "0"
    
    # Try to get back to a clean state
    echo "🔧 Attempting to restore clean state..."
    git checkout $EXPERIMENTAL_BRANCH 2>/dev/null || true
    if git status | grep -q "You have unmerged paths"; then
        git merge --abort 2>/dev/null || git reset --hard HEAD 2>/dev/null || true
    fi
    
    exit 1
}

# Trap to handle failures
trap 'handle_sync_failure "Unexpected error occurred"' ERR

# Perform synchronization based on type
case $SYNC_TYPE in
    "auto-merge")
        echo "🔄 Performing automatic merge synchronization..."
        
        # Check if there are any commits to sync
        commits_behind=$(git rev-list --count $EXPERIMENTAL_BRANCH..$MAIN_BRANCH)
        if [[ $commits_behind -eq 0 ]]; then
            echo "✅ Experimental branch is already up to date with main"
            update_log_status "success" "0"
            echo "📊 Sync health:"
            python "$SCRIPT_DIR/sync_health_dashboard.py"
            exit 0
        fi
        
        echo "📥 Found $commits_behind commits to sync from main"
        
        # Run the main sync script
        if "$SCRIPT_DIR/sync_linguistic_branch.sh"; then
            echo "✅ Automatic merge completed successfully"
            update_log_status "success" "0"
        else
            # Check if it failed due to conflicts
            if git status | grep -q "You have unmerged paths"; then
                echo "⚠️  Merge conflicts detected - manual resolution required"
                
                # Count conflicts
                conflict_files=$(git status --porcelain | grep "^UU" | wc -l)
                echo "🔧 Found $conflict_files files with conflicts"
                
                echo "📋 Conflicted files:"
                git status --porcelain | grep "^UU" || echo "   (Unable to list conflicted files)"
                
                echo ""
                echo "🛠️  Manual resolution steps:"
                echo "   1. git mergetool                    # Resolve conflicts"
                echo "   2. git commit                       # Complete the merge"
                echo "   3. ./post_sync_validation.sh        # Validate the result"
                echo "   4. git push origin $EXPERIMENTAL_BRANCH  # Push if validation passes"
                
                update_log_status "conflict" "$conflict_files"
                exit 1
            else
                handle_sync_failure "Merge failed for unknown reason"
            fi
        fi
        ;;
        
    "cherry-pick")
        echo "🍒 Performing selective cherry-pick synchronization..."
        
        # Show available commits for manual selection
        echo "📋 Available commits from main:"
        git log --oneline $EXPERIMENTAL_BRANCH..$MAIN_BRANCH | head -10
        
        echo ""
        echo "ℹ️  Cherry-pick mode requires manual commit selection"
        echo "   Use: git cherry-pick <commit-hash>"
        echo "   Then run: ./post_sync_validation.sh"
        
        update_log_status "manual_required" "0"
        exit 0
        ;;
        
    "manual")
        echo "🔧 Manual sync mode - review changes and merge manually"
        
        # Show what would be merged
        echo "📊 Changes in main branch since last sync:"
        git log --oneline $EXPERIMENTAL_BRANCH..$MAIN_BRANCH
        
        echo ""
        echo "📈 Statistics:"
        echo "   Commits ahead: $(git rev-list --count $EXPERIMENTAL_BRANCH..$MAIN_BRANCH)"
        echo "   Files changed: $(git diff --name-only $EXPERIMENTAL_BRANCH..$MAIN_BRANCH | wc -l)"
        
        echo ""
        echo "🛠️  Manual sync steps:"
        echo "   1. git checkout $EXPERIMENTAL_BRANCH"
        echo "   2. git merge $MAIN_BRANCH"
        echo "   3. Resolve any conflicts"
        echo "   4. ./post_sync_validation.sh"
        echo "   5. git push origin $EXPERIMENTAL_BRANCH"
        
        update_log_status "manual_required" "0"
        exit 0
        ;;
        
    *)
        handle_sync_failure "Unknown sync type: $SYNC_TYPE"
        ;;
esac

# Post-sync validation
echo "🧪 Running post-sync validation..."
if ! "$SCRIPT_DIR/post_sync_validation.sh"; then
    echo "⚠️  Post-sync validation issues detected - manual review recommended"
    echo "   However, sync completed successfully"
fi

# Update sync log with final status
NEW_LINGUISTIC_COMMIT=$(git rev-parse $EXPERIMENTAL_BRANCH)
update_log_status "success" "0"

echo ""
echo "✅ TCP Branch Synchronization Complete"
echo "📊 Final status:"
echo "   Main branch: $MAIN_COMMIT"
echo "   Experimental branch: $NEW_LINGUISTIC_COMMIT"
echo "   Commits synchronized: $(git rev-list --count $LINGUISTIC_COMMIT..$NEW_LINGUISTIC_COMMIT)"

echo ""
echo "📊 Sync health dashboard:"
python "$SCRIPT_DIR/sync_health_dashboard.py"

echo ""
echo "🎯 Next steps:"
echo "   - Continue experimental development on $EXPERIMENTAL_BRANCH"
echo "   - Run validation tests for both approaches"
echo "   - Monitor sync health with: python sync_health_dashboard.py"