#!/bin/bash
# TCP Research Consortium - File Diff Tracker
# Shows actual changes in researcher files with intelligent analysis

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIFF_LOG="$PROJECT_ROOT/consortium/research-diffs.log"
SNAPSHOTS_DIR="$PROJECT_ROOT/consortium/file-snapshots"

# Create tracking infrastructure
mkdir -p "$SNAPSHOTS_DIR"

echo "📝 TCP Research Consortium - Diff Tracker"
echo "========================================"
echo "⏰ Tracker Time: $(date)"

# Function to create file snapshot and detect changes
track_file_changes() {
    local file="$1"
    local researcher="$2"
    local relative_path="${file#$PROJECT_ROOT/}"
    
    # Create snapshot filename
    local snapshot_file="$SNAPSHOTS_DIR/${researcher}_$(basename "$file").snapshot"
    local current_hash=""
    local previous_hash=""
    
    if [[ -f "$file" ]]; then
        current_hash=$(md5 -q "$file" 2>/dev/null || echo "")
        
        # Check if we have a previous snapshot
        if [[ -f "$snapshot_file" ]]; then
            previous_hash=$(head -n 1 "$snapshot_file" 2>/dev/null || echo "")
            
            # If file changed, analyze the diff
            if [[ "$current_hash" != "$previous_hash" && -n "$current_hash" ]]; then
                echo "🔄 CHANGE DETECTED: $researcher - $(basename "$file")"
                
                # Get previous content
                local previous_content="$SNAPSHOTS_DIR/${researcher}_$(basename "$file").prev"
                if [[ -f "$previous_content" ]]; then
                    # Create intelligent diff analysis
                    local diff_summary="$SNAPSHOTS_DIR/${researcher}_$(basename "$file").diff"
                    
                    echo "# Change Analysis: $(basename "$file") - $researcher" > "$diff_summary"
                    echo "**Timestamp**: $(date)" >> "$diff_summary"
                    echo "**File**: $relative_path" >> "$diff_summary"
                    echo "" >> "$diff_summary"
                    
                    # Line count change
                    local old_lines=$(wc -l < "$previous_content" 2>/dev/null || echo "0")
                    local new_lines=$(wc -l < "$file" 2>/dev/null || echo "0")
                    local line_diff=$((new_lines - old_lines))
                    
                    echo "## Summary" >> "$diff_summary"
                    echo "- **Lines changed**: $old_lines → $new_lines (${line_diff:+$line_diff})" >> "$diff_summary"
                    
                    # Analyze type of changes
                    if diff -q "$previous_content" "$file" >/dev/null 2>&1; then
                        echo "- **Change type**: Metadata only" >> "$diff_summary"
                    else
                        echo "- **Change type**: Content modification" >> "$diff_summary"
                        
                        # Key change indicators
                        if grep -q "class\|def\|function" "$file" 2>/dev/null; then
                            echo "- **Contains**: Code structures (classes/functions)" >> "$diff_summary"
                        fi
                        if grep -q "TODO\|FIXME\|NOTE" "$file" 2>/dev/null; then
                            echo "- **Contains**: Development notes" >> "$diff_summary"
                        fi
                        if grep -q "import\|require\|include" "$file" 2>/dev/null; then
                            echo "- **Contains**: Dependencies/imports" >> "$diff_summary"
                        fi
                    fi
                    
                    echo "" >> "$diff_summary"
                    echo "## Detailed Diff" >> "$diff_summary"
                    echo "\`\`\`diff" >> "$diff_summary"
                    diff -u "$previous_content" "$file" 2>/dev/null | head -100 >> "$diff_summary" || echo "Binary file or diff error" >> "$diff_summary"
                    echo "\`\`\`" >> "$diff_summary"
                    
                    # Log the change
                    echo "[$(date)] $researcher: $(basename "$file") - $line_diff lines, content modified" >> "$DIFF_LOG"
                    
                    echo "   📊 Lines: $old_lines → $new_lines ($line_diff)"
                    echo "   📁 Diff saved: $(basename "$diff_summary")"
                fi
                
                # Save current content as previous for next run
                cp "$file" "$previous_content"
            fi
        else
            # First time seeing this file
            echo "🆕 NEW FILE: $researcher - $(basename "$file")"
            echo "[$(date)] $researcher: $(basename "$file") - NEW FILE created" >> "$DIFF_LOG"
            cp "$file" "$SNAPSHOTS_DIR/${researcher}_$(basename "$file").prev"
        fi
        
        # Update snapshot
        echo "$current_hash" > "$snapshot_file"
        echo "$relative_path" >> "$snapshot_file"
        echo "$(date)" >> "$snapshot_file"
    fi
}

# Track all Python, shell, and markdown files in researcher workspaces
RESEARCHERS=("elena-vasquez" "marcus-chen" "yuki-tanaka" "aria-blackwood" "sam-mitchell")

echo -e "\n🔍 Tracking file changes in researcher workspaces..."

for researcher in "${RESEARCHERS[@]}"; do
    workspace="$PROJECT_ROOT/consortium/$researcher"
    
    if [[ -d "$workspace" ]]; then
        echo "📂 Checking $researcher..."
        
        # Find trackable files (code, docs, configs)
        find "$workspace" -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \) | while read -r file; do
            track_file_changes "$file" "$researcher"
        done
    fi
done

# Generate research direction analysis
echo -e "\n🎯 Analyzing research directions..."

direction_analysis="$PROJECT_ROOT/consortium/research-directions-$(date +%Y%m%d_%H%M%S).md"
cat > "$direction_analysis" << EOF
# TCP Research Consortium - Research Direction Analysis

**Generated**: $(date)

## Recent Research Activity

$(if [[ -f "$DIFF_LOG" ]]; then
    echo "### Change Timeline"
    tail -n 20 "$DIFF_LOG" | while read -r line; do
        echo "- $line"
    done
else
    echo "No changes tracked yet"
fi)

## Research Focus Analysis

$(for researcher in "${RESEARCHERS[@]}"; do
    echo "### $researcher"
    
    # Count different file types
    workspace="$PROJECT_ROOT/consortium/$researcher"
    if [[ -d "$workspace" ]]; then
        py_files=$(find "$workspace" -name "*.py" | wc -l)
        md_files=$(find "$workspace" -name "*.md" | wc -l)
        sh_files=$(find "$workspace" -name "*.sh" | wc -l)
        
        echo "- **Python files**: $py_files (analysis tools, algorithms)"
        echo "- **Documentation**: $md_files (research notes, plans)"
        echo "- **Scripts**: $sh_files (automation, testing)"
        
        # Recent activity
        recent_diffs=$(ls -1 "$SNAPSHOTS_DIR"/${researcher}_*.diff 2>/dev/null | wc -l || echo "0")
        echo "- **Recent changes**: $recent_diffs files modified"
        
        # Look for research focus indicators
        if [[ -d "$workspace" ]]; then
            keywords=$(find "$workspace" -name "*.py" -o -name "*.md" | xargs grep -l -i "behavioral\|statistical\|network\|performance\|security\|kernel" 2>/dev/null | wc -l || echo "0")
            echo "- **Focus keywords found**: $keywords files mention core research terms"
        fi
    else
        echo "- Workspace not found"
    fi
    echo ""
done)

## Collaboration Indicators

$(echo "### Cross-researcher file analysis")
$(if [[ -f "$DIFF_LOG" ]]; then
    echo "Recent activity suggests researchers are:"
    
    elena_active=$(grep -c "elena-vasquez" "$DIFF_LOG" 2>/dev/null || echo "0")
    marcus_active=$(grep -c "marcus-chen" "$DIFF_LOG" 2>/dev/null || echo "0")
    yuki_active=$(grep -c "yuki-tanaka" "$DIFF_LOG" 2>/dev/null || echo "0")
    aria_active=$(grep -c "aria-blackwood" "$DIFF_LOG" 2>/dev/null || echo "0")
    sam_active=$(grep -c "sam-mitchell" "$DIFF_LOG" 2>/dev/null || echo "0")
    
    echo "- Elena (behavioral): $elena_active recent changes"
    echo "- Marcus (distributed): $marcus_active recent changes"
    echo "- Yuki (performance): $yuki_active recent changes"
    echo "- Aria (security): $aria_active recent changes"
    echo "- Sam (kernel): $sam_active recent changes"
else
    echo "No collaboration data available yet"
fi)

---
*Analysis generated by TCP Research Consortium Diff Tracker*
EOF

echo "✅ Direction analysis saved: $direction_analysis"

# Show recent changes summary
echo -e "\n📈 Recent Research Changes Summary:"
echo "================================="

if [[ -f "$DIFF_LOG" ]]; then
    echo "Last 5 changes:"
    tail -n 5 "$DIFF_LOG"
else
    echo "No changes tracked yet - this may be first run"
fi

echo -e "\n💡 Available Analysis Files:"
ls -1 "$SNAPSHOTS_DIR"/*.diff 2>/dev/null | tail -5 | sed 's/.*\//• /' || echo "No diff analyses available yet"

echo -e "\n✅ Diff tracking complete!"
echo "📊 Run again to track new changes and see research evolution"