#!/bin/bash
# TCP Research Consortium - Single Researcher Activation
# Usage: ./scripts/activate-researcher.sh [researcher-name]

set -euo pipefail

RESEARCHERS=("elena-vasquez" "marcus-chen" "yuki-tanaka" "aria-blackwood" "sam-mitchell")
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Validate researcher name
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 [researcher-name]"
    echo "Available researchers: ${RESEARCHERS[*]}"
    exit 1
fi

RESEARCHER="$1"
if [[ ! " ${RESEARCHERS[*]} " =~ " ${RESEARCHER} " ]]; then
    echo "❌ Unknown researcher: $RESEARCHER"
    echo "Available researchers: ${RESEARCHERS[*]}"
    exit 1
fi

# Create research session
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SESSION_BRANCH="research/${RESEARCHER}-session-${TIMESTAMP}"

echo "🔬 TCP Research Consortium - Researcher Activation"
echo "=================================================="
echo "👤 Researcher: Dr. $(echo $RESEARCHER | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1))substr($i,2)}1')"
echo "🌿 Session Branch: $SESSION_BRANCH"
echo "📁 Research Directory: consortium/$RESEARCHER/"
echo "⏰ Activation Time: $(date)"

# Create and switch to research branch
git checkout -b "$SESSION_BRANCH" 2>/dev/null || git checkout "$SESSION_BRANCH"

# Set research context
cd "$PROJECT_ROOT/consortium/$RESEARCHER"
echo "📖 Loading researcher profile..."
cat CLAUDE.md | head -n 10

echo -e "\n🎯 Research Session Active"
echo "   • Full write access to consortium/$RESEARCHER/"
echo "   • Read access to all other research"
echo "   • PR approval required for core changes"
echo "   • Session branch: $SESSION_BRANCH"

# Create session log
echo "Research Session: Dr. $(echo $RESEARCHER | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1))substr($i,2)}1')" > session.log
echo "Start Time: $(date)" >> session.log
echo "Session Branch: $SESSION_BRANCH" >> session.log
echo "Research Focus: TBD" >> session.log

echo -e "\n✅ Researcher activated! Ready for research."
echo "💡 Tip: Use 'git status' to see your research workspace"
echo "📋 Use './scripts/research-dashboard.sh' to see consortium activity"