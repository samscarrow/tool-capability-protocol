#!/bin/bash
# TCP Research Consortium - Message Checker
# Check for new communications and notifications

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMS_DIR="$PROJECT_ROOT/consortium/communications"
NOTIFICATIONS_DIR="$PROJECT_ROOT/consortium/notifications"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "📬 TCP Research Consortium - Message Center"
echo "=========================================="
echo "⏰ Check Time: $(date)"
echo ""

# Function to check messages for a researcher
check_researcher_messages() {
    local researcher="$1"
    local found_messages=false
    
    echo "👤 Checking messages for: $researcher"
    echo "-----------------------------------"
    
    # Check notifications
    if [[ -f "$NOTIFICATIONS_DIR/${researcher}-notifications.md" ]]; then
        local notification_age=$(( ($(date +%s) - $(date -r "$NOTIFICATIONS_DIR/${researcher}-notifications.md" +%s)) / 60 ))
        echo "📋 Notifications: Updated $notification_age minutes ago"
        
        # Show urgent notifications
        if grep -q "🔴 High" "$NOTIFICATIONS_DIR/${researcher}-notifications.md" 2>/dev/null; then
            echo -e "${RED}🚨 URGENT notifications found!${NC}"
            found_messages=true
        fi
    fi
    
    # Check direct messages
    if ls "$COMMS_DIR/direct/"*"_to_${researcher}_"*.md >/dev/null 2>&1; then
        echo "✉️  Direct messages:"
        for msg in "$COMMS_DIR/direct/"*"_to_${researcher}_"*.md; do
            if [[ -f "$msg" ]]; then
                local sender=$(basename "$msg" | sed 's/.*_\([^_]*\)_to_.*/\1/')
                local subject=$(basename "$msg" | sed 's/.*_to_[^_]*_\(.*\)\.md/\1/')
                local priority=""
                if grep -q "🔴 High" "$msg" 2>/dev/null; then
                    priority="${RED}[HIGH]${NC} "
                fi
                echo -e "   • From $sender: ${priority}$subject"
                found_messages=true
            fi
        done
    fi
    
    # Check issue threads where researcher is mentioned
    if grep -r "@$researcher" "$COMMS_DIR/issues/" 2>/dev/null | grep -v "^Binary file" | head -1 >/dev/null; then
        echo "🔗 Mentioned in issue threads:"
        grep -r -l "@$researcher" "$COMMS_DIR/issues/" 2>/dev/null | while read -r file; do
            local issue=$(basename $(dirname "$file"))
            echo "   • Issue: $issue"
            found_messages=true
        done
    fi
    
    # Check team updates
    local latest_update=$(ls -t "$COMMS_DIR/updates/"*.md 2>/dev/null | head -1)
    if [[ -n "$latest_update" ]]; then
        local update_age=$(( ($(date +%s) - $(date -r "$latest_update" +%s)) / 3600 ))
        if [[ $update_age -lt 24 ]]; then
            echo "📢 New team update: $(basename "$latest_update")"
            found_messages=true
        fi
    fi
    
    if [[ "$found_messages" == false ]]; then
        echo "   📭 No new messages"
    fi
    
    echo ""
}

# Check if specific researcher specified
if [[ $# -eq 1 ]]; then
    check_researcher_messages "$1"
else
    # Check all researchers
    RESEARCHERS=("elena-vasquez" "marcus-chen" "yuki-tanaka" "aria-blackwood" "sam-mitchell" "dr-alex-rivera")
    
    for researcher in "${RESEARCHERS[@]}"; do
        check_researcher_messages "$researcher"
    done
fi

# Show active issue threads
echo "🔥 Active Issue Threads"
echo "====================="
if [[ -d "$COMMS_DIR/issues" ]]; then
    for issue_dir in "$COMMS_DIR/issues"/*; do
        if [[ -d "$issue_dir" ]]; then
            issue_name=$(basename "$issue_dir")
            latest_msg=$(ls -t "$issue_dir"/*.md 2>/dev/null | head -1)
            if [[ -n "$latest_msg" ]]; then
                echo "📌 $issue_name"
                echo "   Latest: $(basename "$latest_msg")"
                if grep -q "Status:.*In Progress" "$latest_msg" 2>/dev/null; then
                    echo -e "   Status: ${YELLOW}In Progress${NC}"
                elif grep -q "Status:.*Resolved" "$latest_msg" 2>/dev/null; then
                    echo -e "   Status: ${GREEN}Resolved${NC}"
                fi
            fi
        fi
    done
else
    echo "   No active issues"
fi

echo ""
echo "💡 Message Commands:"
echo "   • View notifications: cat $NOTIFICATIONS_DIR/[your-name]-notifications.md"
echo "   • Send message: Create file in $COMMS_DIR/direct/"
echo "   • Check specific user: $0 [researcher-name]"