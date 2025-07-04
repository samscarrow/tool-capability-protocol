#!/bin/bash
# TCP Research Consortium - Notification System
# Automated detection and notification of coordination events

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "📢 TCP Research Consortium - Notification System"
echo "==============================================="
echo "⏰ Check Time: $(date)"

# Function to check for convergent discussion files
check_convergent_discussions() {
    echo -e "\n🎯 CONVERGENT DISCUSSION DETECTION"
    echo "=================================="
    
    local discussions_found=false
    
    # Look for convergent discussion files
    while IFS= read -r -d '' file; do
        discussions_found=true
        local timestamp=$(basename "$file" | sed 's/convergent-discussion-\(.*\)\.md/\1/')
        echo "🚨 **CONVERGENT DISCUSSION DETECTED**"
        echo "   📄 File: $(basename "$file")"
        echo "   📅 Timestamp: $timestamp"
        echo "   📍 Location: $file"
        
        # Extract participants from file
        if [[ -f "$file" ]]; then
            participants=$(grep "\\*\\*Participants\\*\\*:" "$file" | head -1 | cut -d: -f2- | sed 's/^[[:space:]]*//')
            if [[ -n "$participants" ]]; then
                echo "   👥 Participants: $participants"
            fi
            
            # Check for readiness status
            if grep -q "✅ READY" "$file"; then
                echo "   ✅ **ALL PARTICIPANTS READY FOR CONVERGENT RESEARCH**"
                echo ""
                echo "   🔴 **ACTION REQUIRED BY PARTICIPANTS:**"
                echo "   Code Word: **'CONVERGENCE-$timestamp'**"
                echo "   Message to participants: 'Please review convergent-discussion-$timestamp.md'"
                echo ""
            else
                echo "   ⏳ Waiting for participant readiness"
            fi
        fi
        
        echo "   ---"
    done < <(find "$PROJECT_ROOT/consortium" -name "convergent-discussion-*.md" -print0 2>/dev/null)
    
    if [[ "$discussions_found" == false ]]; then
        echo "   📭 No convergent discussions detected"
    fi
}

# Function to check for coordination files
check_coordination_files() {
    echo -e "\n📋 COORDINATION FILES DETECTION"
    echo "==============================="
    
    local coordination_found=false
    
    # Look for research direction files
    while IFS= read -r -d '' file; do
        coordination_found=true
        echo "📊 Research Direction Analysis: $(basename "$file")"
        echo "   📍 Location: $file"
        echo "   📅 Modified: $(date -r "$file" '+%Y-%m-%d %H:%M:%S')"
        
        # Check for collaboration indicators
        if grep -q "OPPORTUNITY" "$file" 2>/dev/null; then
            echo "   🎯 **Contains collaboration opportunities**"
        fi
        echo "   ---"
    done < <(find "$PROJECT_ROOT/consortium" -name "research-directions-*.md" -print0 2>/dev/null)
    
    # Look for other coordination files
    for coord_file in "team-integration-plan.md" "research-coordination.md" "consortium-status.md"; do
        if [[ -f "$PROJECT_ROOT/consortium/$coord_file" ]]; then
            coordination_found=true
            echo "📋 Coordination File: $coord_file"
            echo "   📅 Modified: $(date -r "$PROJECT_ROOT/consortium/$coord_file" '+%Y-%m-%d %H:%M:%S')"
            echo "   ---"
        fi
    done
    
    if [[ "$coordination_found" == false ]]; then
        echo "   📭 No coordination files detected"
    fi
}

# Function to generate researcher notifications
generate_researcher_notifications() {
    echo -e "\n📨 RESEARCHER NOTIFICATION GENERATION"
    echo "===================================="
    
    local notifications_dir="$PROJECT_ROOT/consortium/notifications"
    mkdir -p "$notifications_dir"
    
    # Generate notifications for each researcher
    RESEARCHERS=("elena-vasquez" "marcus-chen" "yuki-tanaka" "aria-blackwood" "sam-mitchell")
    
    for researcher in "${RESEARCHERS[@]}"; do
        local notification_file="$notifications_dir/${researcher}-notifications.md"
        
        echo "# Research Notifications for $researcher" > "$notification_file"
        echo "**Generated**: $(date)" >> "$notification_file"
        echo "" >> "$notification_file"
        
        # Check for convergent discussions involving this researcher
        while IFS= read -r -d '' file; do
            # Check both researcher name and variations (elena-vasquez -> Elena, marcus-chen -> Marcus)
            researcher_name=$(echo "$researcher" | cut -d- -f1)
            researcher_name_cap="$(tr '[:lower:]' '[:upper:]' <<< ${researcher_name:0:1})${researcher_name:1}"
            
            if grep -q -i "$researcher\|$researcher_name\|$researcher_name_cap" "$file" 2>/dev/null; then
                local timestamp=$(basename "$file" | sed 's/convergent-discussion-\(.*\)\.md/\1/')
                echo "## 🎯 CONVERGENT DISCUSSION ALERT" >> "$notification_file"
                echo "**Code Word**: CONVERGENCE-$timestamp" >> "$notification_file"
                echo "**Action**: Review convergent-discussion-$timestamp.md" >> "$notification_file"
                echo "**Location**: $file" >> "$notification_file"
                echo "**Summary**: Elena's mathematical bottlenecks require Marcus's distributed systems expertise" >> "$notification_file"
                echo "" >> "$notification_file"
            fi
        done < <(find "$PROJECT_ROOT/consortium" -name "convergent-discussion-*.md" -print0 2>/dev/null)
        
        # Check for mentions in other researchers' work
        for other_researcher in "${RESEARCHERS[@]}"; do
            if [[ "$researcher" != "$other_researcher" ]]; then
                local other_workspace="$PROJECT_ROOT/consortium/$other_researcher"
                if [[ -d "$other_workspace" ]] && grep -r -q "$researcher" "$other_workspace" 2>/dev/null; then
                    echo "## 🔗 COLLABORATION REFERENCE" >> "$notification_file"
                    echo "**$other_researcher** has referenced your work" >> "$notification_file"
                    echo "**Check**: $other_researcher's workspace for collaboration opportunities" >> "$notification_file"
                    echo "" >> "$notification_file"
                fi
            fi
        done
        
        echo "📨 Generated notification for $researcher: $notification_file"
    done
}

# Function to check notification pickup
check_notification_pickup() {
    echo -e "\n📬 NOTIFICATION PICKUP STATUS"
    echo "============================"
    
    local notifications_dir="$PROJECT_ROOT/consortium/notifications"
    
    if [[ -d "$notifications_dir" ]]; then
        for notification_file in "$notifications_dir"/*.md; do
            if [[ -f "$notification_file" ]]; then
                local researcher=$(basename "$notification_file" | sed 's/-notifications\.md//')
                local age_minutes=$(( ($(date +%s) - $(date -r "$notification_file" +%s)) / 60 ))
                
                echo "📧 $researcher: $age_minutes minutes old"
                
                # Check if researcher has been active since notification
                local workspace="$PROJECT_ROOT/consortium/$researcher"
                if [[ -d "$workspace" ]]; then
                    local recent_activity=$(find "$workspace" -newer "$notification_file" -name "*.py" -o -name "*.md" | wc -l)
                    if [[ "$recent_activity" -gt 0 ]]; then
                        echo "   ✅ **RESEARCHER ACTIVE SINCE NOTIFICATION**"
                        echo "   📝 $recent_activity files modified since notification"
                    else
                        echo "   ⏳ No activity since notification"
                    fi
                fi
            fi
        done
    else
        echo "   📭 No notifications directory found"
    fi
}

# Main notification system
check_convergent_discussions
check_coordination_files
generate_researcher_notifications
check_notification_pickup

echo -e "\n🎯 NOTIFICATION SYSTEM SUMMARY"
echo "============================="
echo "✅ Convergent discussion detection: ACTIVE"
echo "✅ Coordination file monitoring: ACTIVE"  
echo "✅ Researcher notification generation: ACTIVE"
echo "✅ Notification pickup tracking: ACTIVE"

echo -e "\n📋 **USAGE INSTRUCTIONS FOR RESEARCHERS**:"
echo "1. When you see code word 'CONVERGENCE-timestamp', check your notification file"
echo "2. Notification files are in consortium/notifications/[your-name]-notifications.md"
echo "3. Run this script periodically to check for new coordination events"
echo "4. Always review convergent discussion files when mentioned"

echo -e "\n💡 **FOR RESEARCH COORDINATOR**:"
echo "1. Run this script after creating convergent discussion files"
echo "2. Use generated code words to alert specific participants"
echo "3. Monitor notification pickup to ensure researchers are informed"
echo "4. Check for cross-researcher references and collaboration opportunities"