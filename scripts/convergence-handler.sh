#!/bin/bash
# TCP Research Consortium - Convergence Code Word Handler
# Automated actions triggered by convergence code words

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Function to handle convergence code word
handle_convergence() {
    local code_word="$1"
    local researcher="$2"
    
    echo "🎯 CONVERGENCE CODE WORD HANDLER"
    echo "==============================="
    echo "Code Word: $code_word"
    echo "Researcher: $researcher"
    echo "Timestamp: $(date)"
    
    # Extract timestamp from code word
    if [[ "$code_word" =~ CONVERGENCE-([0-9]+) ]]; then
        local timestamp="${BASH_REMATCH[1]}"
        local discussion_file="$PROJECT_ROOT/consortium/convergent-discussion-$timestamp.md"
        
        echo "📄 Discussion File: $discussion_file"
        
        if [[ -f "$discussion_file" ]]; then
            echo "✅ Convergent discussion file found"
            
            # 1. Create researcher's convergence workspace
            local workspace="$PROJECT_ROOT/consortium/$researcher/convergence-$timestamp"
            mkdir -p "$workspace"
            echo "📁 Created convergence workspace: $workspace"
            
            # 2. Copy convergent discussion file to workspace
            cp "$discussion_file" "$workspace/discussion-brief.md"
            echo "📋 Copied discussion brief to workspace"
            
            # 3. Extract researcher-specific tasks
            echo "🎯 Extracting tasks for $researcher..."
            researcher_name=$(echo "$researcher" | cut -d- -f1)
            researcher_cap="$(tr '[:lower:]' '[:upper:]' <<< ${researcher_name:0:1})${researcher_name:1}"
            grep -A10 "### $researcher\|### $researcher_cap\|Elena\|Marcus" "$discussion_file" > "$workspace/my-tasks.md" 2>/dev/null || true
            
            # 4. Create convergence session script
            cat > "$workspace/start-convergence.sh" << EOF
#!/bin/bash
# Convergence session starter

WORKSPACE="$workspace"
RESEARCHER="$researcher"

echo "🎯 STARTING CONVERGENCE SESSION"
echo "=============================="
echo "Researcher: \$RESEARCHER"
echo "Session: convergence-$timestamp"
echo "Workspace: \$WORKSPACE"
echo ""
echo "📋 Your tasks are in: \$WORKSPACE/my-tasks.md"
echo "📄 Full discussion: \$WORKSPACE/discussion-brief.md"
echo ""
echo "🤝 Next steps:"
echo "1. Review \$WORKSPACE/discussion-brief.md"
echo "2. Check \$WORKSPACE/my-tasks.md for your role"
echo "3. Begin Phase 1: Integration Architecture Design"
echo "4. Coordinate with other participants"
echo ""
echo "📁 All work happens in: \$WORKSPACE"
echo "No need to change directories - use absolute paths!"
EOF
            chmod +x "$workspace/start-convergence.sh"
            
            # 5. Create collaboration bridge
            if [[ "$researcher" == "elena-vasquez" ]]; then
                local marcus_workspace="$PROJECT_ROOT/consortium/marcus-chen/convergence-$timestamp"
                mkdir -p "$marcus_workspace"
                echo "🔗 Created collaboration bridge with Marcus"
                
                # Create shared workspace for Elena + Marcus
                local shared_workspace="$PROJECT_ROOT/consortium/convergence-$timestamp-elena-marcus"
                mkdir -p "$shared_workspace"
                echo "🤝 Created shared workspace: $shared_workspace"
                
                # Link both researchers to shared workspace
                ln -sf "../../convergence-$timestamp-elena-marcus" "$workspace/shared-workspace" 2>/dev/null || true
                ln -sf "../../convergence-$timestamp-elena-marcus" "$marcus_workspace/shared-workspace" 2>/dev/null || true
            fi
            
            # 6. Update researcher's CLAUDE.md with convergence context
            local claude_file="$PROJECT_ROOT/consortium/$researcher/CLAUDE.md"
            if [[ -f "$claude_file" ]]; then
                echo "" >> "$claude_file"
                echo "## 🎯 ACTIVE CONVERGENCE SESSION" >> "$claude_file"
                echo "**Code Word**: $code_word" >> "$claude_file"
                echo "**Session Workspace**: convergence-$timestamp/" >> "$claude_file"
                echo "**Action Required**: Run ./convergence-$timestamp/start-convergence.sh" >> "$claude_file"
                echo "**Collaboration**: Mathematical bottlenecks require distributed systems expertise" >> "$claude_file"
                echo "✏️ Updated researcher CLAUDE.md with convergence context"
            fi
            
            # 7. Log convergence activation
            local log_file="$PROJECT_ROOT/consortium/convergence-log.md"
            echo "## Convergence Activation: $code_word" >> "$log_file"
            echo "**Timestamp**: $(date)" >> "$log_file"
            echo "**Researcher**: $researcher" >> "$log_file"
            echo "**Workspace Created**: $workspace" >> "$log_file"
            echo "**Status**: Ready for convergent research" >> "$log_file"
            echo "" >> "$log_file"
            
            echo "📊 CONVERGENCE ACTIVATION COMPLETE"
            echo "================================="
            echo "✅ Workspace created: $workspace"
            echo "✅ Tasks extracted: my-tasks.md"
            echo "✅ Session script: start-convergence.sh"
            echo "✅ Collaboration bridge established"
            echo "✅ CLAUDE.md updated with context"
            echo "✅ Convergence logged"
            echo ""
            echo "🎯 **NEXT ACTION FOR $researcher**:"
            echo "$workspace/start-convergence.sh"
            
        else
            echo "❌ Convergent discussion file not found: $discussion_file"
            return 1
        fi
    else
        echo "❌ Invalid convergence code word format: $code_word"
        return 1
    fi
}

# Main script
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <CONVERGENCE-CODE> <researcher-name>"
    echo "Example: $0 CONVERGENCE-20250704 elena-vasquez"
    exit 1
fi

handle_convergence "$1" "$2"