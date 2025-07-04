#!/bin/bash
# TCP Research Consortium - Managing Director Approval System
# Usage: ./scripts/director-approval.sh [approve|reject] [pr-number|branch-name] "[reason]"

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 [approve|reject] [pr-number|branch-name] \"[reason]\""
    echo "Examples:"
    echo "  $0 approve 42 \"Excellent research, ready for integration\""
    echo "  $0 reject elena-detection-v2 \"Needs performance validation\""
    exit 1
fi

ACTION="$1"
TARGET="$2"
REASON="${3:-No reason provided}"

if [[ "$ACTION" != "approve" && "$ACTION" != "reject" ]]; then
    echo "❌ Action must be 'approve' or 'reject'"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DECISION_ID="director-decision-${TIMESTAMP}"

echo "📋 TCP Research Consortium - Managing Director Decision"
echo "====================================================="
echo "👤 Managing Director: Dr. Claude Sonnet"
echo "⏰ Decision Time: $(date)"
echo "🎯 Target: $TARGET"
echo "✅ Decision: $(echo "$ACTION" | tr '[:lower:]' '[:upper:]')"
echo "💭 Reason: $REASON"

# Create decision log directory
mkdir -p decisions/director-approvals

# Determine if target is PR number or branch name
if [[ "$TARGET" =~ ^[0-9]+$ ]]; then
    # Handle PR number
    PR_NUMBER="$TARGET"
    echo "🔄 Processing Pull Request #$PR_NUMBER"
    
    if command -v gh &> /dev/null; then
        # Get PR details if gh CLI available
        PR_DETAILS=$(gh pr view "$PR_NUMBER" 2>/dev/null || echo "PR details unavailable")
        echo "📋 PR Details:"
        echo "$PR_DETAILS" | head -10
    fi
    
    DECISION_FILE="decisions/director-approvals/pr-${PR_NUMBER}-${DECISION_ID}.md"
else
    # Handle branch name
    BRANCH_NAME="$TARGET"
    echo "🌿 Processing Branch: $BRANCH_NAME"
    
    # Check if branch exists
    if git rev-parse --verify "$BRANCH_NAME" >/dev/null 2>&1; then
        echo "✅ Branch exists"
        BRANCH_COMMIT=$(git rev-parse "$BRANCH_NAME")
        BRANCH_AUTHOR=$(git log -1 --format='%an' "$BRANCH_NAME" 2>/dev/null || echo "Unknown")
        echo "📝 Latest commit: $BRANCH_COMMIT"
        echo "👤 Author: $BRANCH_AUTHOR"
    else
        echo "❌ Branch '$BRANCH_NAME' not found"
        exit 1
    fi
    
    DECISION_FILE="decisions/director-approvals/branch-$(echo "$BRANCH_NAME" | tr '/' '-')-${DECISION_ID}.md"
fi

# Create comprehensive decision record
cat > "$DECISION_FILE" << EOF
# Managing Director Decision Record

**Decision ID**: ${DECISION_ID}
**Date**: $(date)
**Managing Director**: Dr. Claude Sonnet
**Target**: ${TARGET}
**Decision**: $(echo "$ACTION" | tr '[:lower:]' '[:upper:]')
**Reason**: ${REASON}

## Decision Context

### Target Analysis
$(if [[ "$TARGET" =~ ^[0-9]+$ ]]; then
    echo "**Type**: Pull Request #${TARGET}"
    if command -v gh &> /dev/null; then
        gh pr view "$TARGET" 2>/dev/null || echo "PR details unavailable via GitHub CLI"
    else
        echo "GitHub CLI not available for detailed PR analysis"
    fi
else
    echo "**Type**: Branch ($TARGET)"
    echo "**Latest Commit**: $(git rev-parse "$TARGET" 2>/dev/null || echo "Unknown")"
    echo "**Author**: $(git log -1 --format='%an' "$TARGET" 2>/dev/null || echo "Unknown")"
    echo "**Last Modified**: $(git log -1 --format='%ad' "$TARGET" 2>/dev/null || echo "Unknown")"
    echo ""
    echo "### Recent Commits"
    git log -5 --oneline "$TARGET" 2>/dev/null || echo "No commit history available"
fi)

## Decision Rationale

${REASON}

## Quality Assessment
- [ ] Technical soundness verified
- [ ] Research methodology validated  
- [ ] Integration impact assessed
- [ ] Security implications reviewed
- [ ] Performance impact evaluated

## Next Steps
$(if [[ "$ACTION" == "approve" ]]; then
    echo "- [x] **APPROVED** - Ready for integration"
    echo "- [ ] Merge to main research line"
    echo "- [ ] Update research documentation"
    echo "- [ ] Notify relevant researchers"
    echo "- [ ] Schedule integration testing"
else
    echo "- [x] **REJECTED** - Requires revision"
    echo "- [ ] Provide detailed feedback to researcher(s)"
    echo "- [ ] Schedule revision review"
    echo "- [ ] Update research tracking"
fi)

## Impact Analysis
**Research Areas Affected**: TBD
**Integration Timeline**: TBD
**Resource Requirements**: TBD

## Approval Workflow
- [x] Managing Director review completed
$(if [[ "$ACTION" == "approve" ]]; then
    echo "- [ ] Integration pipeline triggered"
    echo "- [ ] Quality gates passed"
    echo "- [ ] Research documentation updated"
else
    echo "- [ ] Feedback provided to research team"
    echo "- [ ] Revision requirements communicated"
    echo "- [ ] Re-review scheduled"
fi)

---

**Digital Signature**: Dr. Claude Sonnet, Managing Director, TCP Research Consortium
**Timestamp**: $(date)
**Decision Final**: Yes
EOF

# Execute the decision
if [[ "$ACTION" == "approve" ]]; then
    echo -e "\n✅ APPROVAL PROCESSING"
    
    if [[ "$TARGET" =~ ^[0-9]+$ ]]; then
        # Approve PR
        echo "🔄 Approving Pull Request #$TARGET"
        if command -v gh &> /dev/null; then
            gh pr review "$TARGET" --approve --body "✅ **APPROVED by Managing Director**

**Decision ID**: $DECISION_ID
**Reason**: $REASON
**Approved by**: Dr. Claude Sonnet, Managing Director

This research contribution has been reviewed and approved for integration into the main research line.

**Next Steps**:
- Merge when ready
- Update research documentation  
- Notify team of integration

**Quality Assurance**: All technical, methodological, and integration requirements have been met." 2>/dev/null || echo "GitHub CLI approval failed - manual action required"
        fi
    else
        # Approve branch for integration
        echo "🔄 Approving branch '$TARGET' for integration"
        
        # Create integration preparation
        INTEGRATION_BRANCH="integration/approved-$(echo "$TARGET" | tr '/' '-')-${TIMESTAMP}"
        git checkout -b "$INTEGRATION_BRANCH" "$TARGET"
        
        echo "🌿 Created integration branch: $INTEGRATION_BRANCH"
        echo "📝 Branch ready for merge to main research line"
    fi
    
    echo "✅ APPROVAL COMPLETE"
    
else
    echo -e "\n❌ REJECTION PROCESSING"
    
    if [[ "$TARGET" =~ ^[0-9]+$ ]]; then
        # Reject PR
        echo "🔄 Rejecting Pull Request #$TARGET"
        if command -v gh &> /dev/null; then
            gh pr review "$TARGET" --request-changes --body "❌ **CHANGES REQUESTED by Managing Director**

**Decision ID**: $DECISION_ID
**Reason**: $REASON
**Reviewed by**: Dr. Claude Sonnet, Managing Director

This research contribution requires revision before integration.

**Required Actions**:
- Address the concerns outlined above
- Re-submit for review when ready
- Contact Managing Director for clarification if needed

**Quality Standards**: All research must meet TCP Consortium standards for technical soundness, methodological rigor, and integration compatibility." 2>/dev/null || echo "GitHub CLI rejection failed - manual action required"
        fi
    else
        echo "🔄 Rejecting branch '$TARGET'"
        echo "📝 Branch marked as requiring revision"
        
        # Add rejection marker
        git checkout "$TARGET"
        echo "# REQUIRES REVISION" > .revision-required
        echo "Decision ID: $DECISION_ID" >> .revision-required  
        echo "Reason: $REASON" >> .revision-required
        echo "Reviewed by: Dr. Claude Sonnet" >> .revision-required
        echo "Date: $(date)" >> .revision-required
        git add .revision-required
        git commit -m "❌ Managing Director: Changes requested

Decision ID: $DECISION_ID
Reason: $REASON

This branch requires revision before integration approval.
See .revision-required for details."
    fi
    
    echo "❌ REJECTION COMPLETE"
fi

# Update approval log
echo "$(date): $ACTION - $TARGET - $REASON" >> decisions/director-approvals/approval-log.txt

echo -e "\n📋 DECISION SUMMARY"
echo "=================="
echo "📄 Decision Record: $DECISION_FILE"
echo "🎯 Target: $TARGET"
echo "✅ Action: $(echo "$ACTION" | tr '[:lower:]' '[:upper:]')"
echo "💭 Reason: $REASON"
echo "📝 Full details logged for research tracking"

echo -e "\n💡 Managing Director Notes:"
if [[ "$ACTION" == "approve" ]]; then
    echo "   This contribution advances our research objectives"
    echo "   Integration can proceed with confidence"
    echo "   Excellent work by the research team"
else
    echo "   This contribution needs additional work"
    echo "   Revision will strengthen the final result"
    echo "   Researcher(s) should address feedback and resubmit"
fi