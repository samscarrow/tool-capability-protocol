#!/bin/bash
# TCP Research Consortium - Real-Time Research Dashboard
# Usage: ./scripts/research-dashboard.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESEARCHERS=("elena-vasquez" "marcus-chen" "yuki-tanaka" "aria-blackwood" "sam-mitchell")

echo "🔬 TCP Research Consortium - Research Dashboard"
echo "================================================"
echo "⏰ Dashboard Time: $(date)"
echo "📁 Project: $(basename "$PROJECT_ROOT")"

# Check git status
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)
echo "🌿 Current Branch: $CURRENT_BRANCH"

echo -e "\n🏃 Active Researchers (last 24 hours):"
ACTIVE_COUNT=0
for researcher in "${RESEARCHERS[@]}"; do
    # Check for recent activity
    RECENT_COMMITS=$(git log --since="24 hours ago" --author="*$(echo $researcher | tr '-' ' ')*" --oneline 2>/dev/null | wc -l)
    if [[ $RECENT_COMMITS -gt 0 ]]; then
        ACTIVE_COUNT=$((ACTIVE_COUNT + 1))
        LATEST_COMMIT=$(git log -1 --author="*$(echo $researcher | tr '-' ' ')*" --oneline 2>/dev/null | head -n 1 || echo "No commits found")
        echo "  ✅ Dr. $(echo $researcher | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1))substr($i,2)}1') ($RECENT_COMMITS commits)"
        echo "     Latest: $LATEST_COMMIT"
    else
        echo "  💤 Dr. $(echo $researcher | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1))substr($i,2)}1') (inactive)"
    fi
done

if [[ $ACTIVE_COUNT -eq 0 ]]; then
    echo "  🔇 No recent researcher activity detected"
fi

echo -e "\n📊 Current Research Branches:"
RESEARCH_BRANCHES=$(git branch -a | grep "research/" | head -10)
if [[ -n "$RESEARCH_BRANCHES" ]]; then
    echo "$RESEARCH_BRANCHES" | while read -r branch; do
        branch_name=$(echo "$branch" | sed 's/.*\///')
        last_commit=$(git log -1 --oneline "$branch" 2>/dev/null | head -n 1 || echo "No commits")
        echo "  🔬 $branch_name"
        echo "     $last_commit"
    done
else
    echo "  📝 No active research branches"
fi

echo -e "\n🤝 Active Collaborations:"
COLLAB_BRANCHES=$(git branch -a | grep "collaborative/" | head -5)
if [[ -n "$COLLAB_BRANCHES" ]]; then
    echo "$COLLAB_BRANCHES" | while read -r branch; do
        branch_name=$(echo "$branch" | sed 's/.*\///')
        last_commit=$(git log -1 --oneline "$branch" 2>/dev/null | head -n 1 || echo "No commits")
        echo "  🤝 $branch_name"
        echo "     $last_commit"
    done
else
    echo "  🔇 No active collaborative branches"
fi

echo -e "\n⏳ Recent Integration Activity:"
INTEGRATION_BRANCHES=$(git branch -a | grep "integration/" | head -3)
if [[ -n "$INTEGRATION_BRANCHES" ]]; then
    echo "$INTEGRATION_BRANCHES" | while read -r branch; do
        branch_name=$(echo "$branch" | sed 's/.*\///')
        last_commit=$(git log -1 --oneline "$branch" 2>/dev/null | head -n 1 || echo "No commits")
        echo "  🔗 $branch_name"
        echo "     $last_commit"
    done
else
    echo "  📝 No recent integration activity"
fi

# Check for pending PRs (if gh CLI is available)
if command -v gh &> /dev/null; then
    echo -e "\n🔄 Pending Pull Requests:"
    PENDING_PRS=$(gh pr list --limit 5 2>/dev/null || echo "")
    if [[ -n "$PENDING_PRS" ]]; then
        echo "$PENDING_PRS"
    else
        echo "  ✅ No pending pull requests"
    fi
fi

# Research file activity
echo -e "\n📁 Recent File Activity (last 7 days):"
RECENT_FILES=$(git log --since="7 days ago" --name-only --pretty="" | sort | uniq -c | sort -nr | head -10)
if [[ -n "$RECENT_FILES" ]]; then
    echo "$RECENT_FILES" | while read -r count file; do
        if [[ -n "$file" ]]; then
            echo "  📄 $file ($count changes)"
        fi
    done
else
    echo "  📝 No recent file activity"
fi

# Research workspace status
echo -e "\n🏠 Research Workspace Status:"
if [[ -d "consortium" ]]; then
    for researcher in "${RESEARCHERS[@]}"; do
        if [[ -d "consortium/$researcher" ]]; then
            file_count=$(find "consortium/$researcher" -type f | wc -l)
            echo "  📂 $researcher: $file_count files"
        fi
    done
    
    if [[ -d "collaborative" ]]; then
        collab_count=$(find collaborative -maxdepth 1 -type d | wc -l)
        echo "  🤝 Collaborative workspaces: $((collab_count - 1))"
    fi
fi

# System health check
echo -e "\n🏥 System Health:"
echo "  🔧 Git status: $(git status --porcelain | wc -l) uncommitted changes"
echo "  📊 Total commits: $(git rev-list --count HEAD)"
echo "  🌿 Total branches: $(git branch -a | wc -l)"

# Quick stats
echo -e "\n📈 Research Statistics:"
TOTAL_COMMITS=$(git rev-list --count HEAD)
TOTAL_AUTHORS=$(git log --format='%an' | sort | uniq | wc -l)
FIRST_COMMIT=$(git log --reverse --oneline | head -n 1 | cut -d' ' -f2-)
echo "  📊 Total commits: $TOTAL_COMMITS"
echo "  👥 Contributing researchers: $TOTAL_AUTHORS"
echo "  🎬 First commit: $FIRST_COMMIT"

echo -e "\n✅ Dashboard update complete"
echo "💡 Use './scripts/activate-researcher.sh [name]' to start research session"
echo "🤝 Use './scripts/activate-team.sh [name1] [name2]' for collaboration"