#!/bin/bash
# TCP Research Consortium - Multi-Researcher Team Activation
# Usage: ./scripts/activate-team.sh [researcher1] [researcher2] [researcher3] ...

set -euo pipefail

RESEARCHERS=("elena-vasquez" "marcus-chen" "yuki-tanaka" "aria-blackwood" "sam-mitchell")
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Validate input
if [[ $# -lt 2 ]]; then
    echo "Usage: $0 [researcher1] [researcher2] [researcher3] ..."
    echo "Available researchers: ${RESEARCHERS[*]}"
    echo "Example: $0 elena-vasquez marcus-chen"
    exit 1
fi

# Validate all researcher names
TEAM_MEMBERS=()
for researcher in "$@"; do
    if [[ ! " ${RESEARCHERS[*]} " =~ " ${researcher} " ]]; then
        echo "❌ Unknown researcher: $researcher"
        echo "Available researchers: ${RESEARCHERS[*]}"
        exit 1
    fi
    TEAM_MEMBERS+=("$researcher")
done

# Create collaboration session
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEAM_NAME=$(IFS=-; echo "${TEAM_MEMBERS[*]}" | tr ' ' '-')
SESSION_BRANCH="collaborative/${TEAM_NAME}-${TIMESTAMP}"

echo "🤝 TCP Research Consortium - Team Collaboration Activation"
echo "=========================================================="
echo "👥 Team Members:"
for member in "${TEAM_MEMBERS[@]}"; do
    echo "   • Dr. $(echo $member | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1))substr($i,2)}1')"
done
echo "🌿 Collaboration Branch: $SESSION_BRANCH"
echo "⏰ Activation Time: $(date)"

# Create and switch to collaboration branch
git checkout -b "$SESSION_BRANCH" 2>/dev/null || git checkout "$SESSION_BRANCH"

# Create collaboration workspace
mkdir -p "collaborative/${TEAM_NAME}-workspace"
cd "collaborative/${TEAM_NAME}-workspace"

# Generate collaboration manifest
cat > collaboration-manifest.md << EOF
# Team Collaboration Session

**Session ID**: ${TEAM_NAME}-${TIMESTAMP}
**Start Time**: $(date)
**Team Members**: 
$(for member in "${TEAM_MEMBERS[@]}"; do echo "- Dr. $(echo $member | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1))substr($i,2)}1')"; done)

## Research Objectives
- [ ] Define collaboration goals
- [ ] Establish research questions
- [ ] Identify expertise intersections
- [ ] Plan deliverables

## Team Expertise Matrix
$(for member in "${TEAM_MEMBERS[@]}"; do
    echo "### Dr. $(echo $member | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1))substr($i,2)}1')"
    echo "\`\`\`"
    head -n 15 "$PROJECT_ROOT/consortium/$member/CLAUDE.md" | tail -n +6
    echo "\`\`\`"
    echo ""
done)

## Collaboration Notes
$(date): Team collaboration session initiated

## Action Items
- [ ] TBD

## Research Artifacts
- [ ] TBD
EOF

# Create shared workspace directories
mkdir -p shared-code shared-docs shared-data shared-analysis

echo -e "\n🎯 Team Collaboration Active"
echo "   • Shared workspace: collaborative/${TEAM_NAME}-workspace/"
echo "   • Each member has read access to all research"
echo "   • Collaborative branch for shared development"
echo "   • PR approval required for core system changes"

# Show team expertise summary
echo -e "\n🧠 Team Expertise Overview:"
for member in "${TEAM_MEMBERS[@]}"; do
    philosophy=$(grep "Core Philosophy" "$PROJECT_ROOT/consortium/$member/CLAUDE.md" -A 1 | tail -n 1 | sed 's/^[*]*//')
    echo "   • $(echo $member | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1))substr($i,2)}1'): $philosophy"
done

echo -e "\n✅ Team collaboration activated!"
echo "📋 Next steps:"
echo "   1. Review collaboration-manifest.md"
echo "   2. Define research objectives"
echo "   3. Begin collaborative development"
echo "   4. Use PR process for core system integration"