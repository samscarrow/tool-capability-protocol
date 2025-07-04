#!/bin/bash
# TCP Research Consortium - Git Operational Oversight
# Ensures proper version control usage and prevents work loss

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 TCP Research Consortium - Git Operational Oversight"
echo "===================================================="
echo "⏰ Analysis Time: $(date)"
echo ""

# Check for uncommitted changes
echo "📊 Version Control Status"
echo "========================"

# Count uncommitted files
MODIFIED_COUNT=$(git ls-files -m | wc -l)
UNTRACKED_COUNT=$(git ls-files -o --exclude-standard | wc -l)
TOTAL_UNCOMMITTED=$((MODIFIED_COUNT + UNTRACKED_COUNT))

if [[ $TOTAL_UNCOMMITTED -gt 0 ]]; then
    echo -e "${RED}⚠️  CRITICAL: $TOTAL_UNCOMMITTED uncommitted files detected!${NC}"
    echo "   - Modified: $MODIFIED_COUNT files"
    echo "   - Untracked: $UNTRACKED_COUNT files"
else
    echo -e "${GREEN}✅ All changes committed${NC}"
fi

# Check researcher branches
echo ""
echo "🌿 Researcher Branch Status"
echo "=========================="

for researcher in elena-vasquez marcus-chen yuki-tanaka aria-blackwood sam-mitchell dr-alex-rivera; do
    echo ""
    echo "👤 $researcher:"
    
    # Find researcher's branches
    BRANCHES=$(git branch -r | grep "research.*$researcher" | sed 's/origin\///' | head -5)
    
    if [[ -n "$BRANCHES" ]]; then
        while read -r branch; do
            # Get last commit info
            LAST_COMMIT=$(git log -1 --format="%cr by %an" "origin/$branch" 2>/dev/null || echo "Unknown")
            echo "   📌 $branch - $LAST_COMMIT"
            
            # Check if branch has unpushed commits
            if git rev-parse --verify "$branch" >/dev/null 2>&1; then
                UNPUSHED=$(git rev-list "origin/$branch".."$branch" --count 2>/dev/null || echo "0")
                if [[ "$UNPUSHED" -gt 0 ]]; then
                    echo -e "      ${YELLOW}⚠️  $UNPUSHED unpushed commits${NC}"
                fi
            fi
        done <<< "$BRANCHES"
    else
        echo -e "   ${YELLOW}⚠️  No research branches found${NC}"
    fi
done

# Analyze consortium directory
echo ""
echo "📁 Consortium Directory Analysis"
echo "==============================="

# Count files by researcher
for researcher in elena-vasquez marcus-chen yuki-tanaka aria-blackwood sam-mitchell dr-alex-rivera; do
    PY_COUNT=$(find "consortium/$researcher" -name "*.py" -not -path "*_env/*" 2>/dev/null | wc -l)
    MD_COUNT=$(find "consortium/$researcher" -name "*.md" 2>/dev/null | wc -l)
    
    if [[ $PY_COUNT -gt 0 || $MD_COUNT -gt 0 ]]; then
        echo "👤 $researcher: $PY_COUNT Python, $MD_COUNT Markdown files"
        
        # Check for uncommitted work
        UNCOMMITTED=$(git status --porcelain "consortium/$researcher" 2>/dev/null | wc -l)
        if [[ $UNCOMMITTED -gt 0 ]]; then
            echo -e "   ${RED}⚠️  $UNCOMMITTED uncommitted changes${NC}"
        fi
    fi
done

# Risk Assessment
echo ""
echo "⚠️  Risk Assessment"
echo "=================="

CRITICAL_RISKS=0

# Check for large uncommitted Python files
LARGE_PY=$(find consortium -name "*.py" -not -path "*_env/*" -size +100k | wc -l)
if [[ $LARGE_PY -gt 0 ]]; then
    echo -e "${RED}🔥 CRITICAL: $LARGE_PY large Python files (>100KB) not in version control${NC}"
    ((CRITICAL_RISKS++))
fi

# Check for convergence work not committed
CONVERGENCE_UNCOMMITTED=$(git status --porcelain | grep -c "convergence" || true)
if [[ $CONVERGENCE_UNCOMMITTED -gt 0 ]]; then
    echo -e "${RED}🔥 CRITICAL: Convergence breakthrough work not committed!${NC}"
    ((CRITICAL_RISKS++))
fi

# Check time since last commit
LAST_COMMIT_TIME=$(git log -1 --format="%cr" 2>/dev/null || echo "Never")
echo "⏰ Last commit: $LAST_COMMIT_TIME"

if [[ "$LAST_COMMIT_TIME" == *"hour"* ]] || [[ "$LAST_COMMIT_TIME" == *"day"* ]]; then
    echo -e "${YELLOW}⚠️  WARNING: No commits in over an hour during active research${NC}"
fi

# Recommendations
echo ""
echo "📋 Operational Recommendations"
echo "============================="

if [[ $CRITICAL_RISKS -gt 0 ]]; then
    echo -e "${RED}🚨 IMMEDIATE ACTIONS REQUIRED:${NC}"
    echo "1. Commit all convergence breakthrough work immediately"
    echo "2. Create researcher-specific commits for their work"
    echo "3. Push all branches to prevent work loss"
    echo ""
fi

echo "🔧 Suggested Git Workflow Improvements:"
echo ""
echo "1. HOURLY COMMITS during active research:"
echo "   git add consortium/[researcher]/"
echo "   git commit -m \"feat(researcher): Work in progress - [description]\""
echo ""
echo "2. FEATURE BRANCHES for each research task:"
echo "   git checkout -b research/[researcher]-[task]-$(date +%Y%m%d_%H%M%S)"
echo ""
echo "3. AUTOMATED COMMITS every 30 minutes:"
echo "   */30 * * * * cd $PROJECT_ROOT && git add consortium && git commit -m \"auto: Research checkpoint \$(date)\" || true"
echo ""
echo "4. BRANCH PROTECTION for convergence work:"
echo "   - Require PR reviews for main branch"
echo "   - Auto-backup critical branches"

# Create commit helper script
echo ""
echo "💡 Creating Git Helper Scripts..."

cat > "$PROJECT_ROOT/scripts/commit-researcher-work.sh" << 'EOF'
#!/bin/bash
# Quick commit for researcher work

RESEARCHER="$1"
MESSAGE="$2"

if [[ -z "$RESEARCHER" || -z "$MESSAGE" ]]; then
    echo "Usage: $0 <researcher-name> <commit-message>"
    echo "Example: $0 elena-vasquez 'Complete behavioral analysis framework'"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Add researcher's work
git add "consortium/$RESEARCHER/"

# Commit with standardized message
git commit -m "feat($RESEARCHER): $MESSAGE" || echo "No changes to commit"

# Show status
git status --short "consortium/$RESEARCHER/"
EOF

chmod +x "$PROJECT_ROOT/scripts/commit-researcher-work.sh"

# Create auto-save script
cat > "$PROJECT_ROOT/scripts/auto-save-research.sh" << 'EOF'
#!/bin/bash
# Auto-save all research work

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Create checkpoint branch if needed
CHECKPOINT_BRANCH="checkpoint/auto-$(date +%Y%m%d_%H%M%S)"
git checkout -b "$CHECKPOINT_BRANCH" 2>/dev/null || true

# Add all consortium work
git add consortium/

# Commit if there are changes
if ! git diff --cached --quiet; then
    git commit -m "checkpoint: Auto-save research work $(date)"
    echo "✅ Research work auto-saved to $CHECKPOINT_BRANCH"
else
    echo "ℹ️  No changes to save"
fi
EOF

chmod +x "$PROJECT_ROOT/scripts/auto-save-research.sh"

echo -e "${GREEN}✅ Helper scripts created:${NC}"
echo "   - scripts/commit-researcher-work.sh"
echo "   - scripts/auto-save-research.sh"

# Final summary
echo ""
echo "📊 Executive Summary"
echo "==================="
echo "Total Uncommitted Files: $TOTAL_UNCOMMITTED"
echo "Critical Risks: $CRITICAL_RISKS"
echo "Last Commit: $LAST_COMMIT_TIME"

if [[ $CRITICAL_RISKS -gt 0 || $TOTAL_UNCOMMITTED -gt 100 ]]; then
    echo ""
    echo -e "${RED}🚨 ACTION REQUIRED: Commit critical research work immediately!${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ Git hygiene acceptable${NC}"
fi