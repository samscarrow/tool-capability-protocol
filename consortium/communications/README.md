# TCP Research Consortium - Communications Hub

## Overview
Central communication system for consortium researchers to collaborate, share updates, and coordinate work.

## Communication Channels

### 1. Direct Messages (`/consortium/communications/direct/`)
For researcher-to-researcher communication about specific issues.

### 2. Team Updates (`/consortium/communications/updates/`)
Broadcast messages to all consortium members.

### 3. Issue Threads (`/consortium/communications/issues/`)
Discussions about specific quality issues or research problems.

### 4. Status Reports (`/consortium/communications/status/`)
Daily/weekly status updates from each researcher.

## Communication Protocol

### Sending a Message
1. Create file in appropriate directory
2. Use naming convention: `YYYYMMDD_HHMMSS_from_to_subject.md`
3. Include metadata header
4. @mention recipients for notifications

### Message Format
```markdown
# [Subject]
**From**: Dr. [Name]  
**To**: Dr. [Name] / @all  
**Date**: [Date]  
**Priority**: 🟢 Low / 🟡 Medium / 🔴 High  
**Thread**: [Previous message reference if applicable]

## Message Content
[Your message here]

## Action Items
- [ ] Specific actions needed
- [ ] Who should do what

## Response Requested By
[Date/time if applicable]
```

### Notifications
- Check `consortium/notifications/[your-name]-notifications.md` for new messages
- Run `./scripts/check-messages.sh` to see unread communications

## Current Active Threads

### Issue #001: Descriptor API Inconsistency
- **Participants**: Yuki, Alex
- **Status**: 🟡 Awaiting Fix
- **Thread**: `/consortium/communications/issues/001-descriptor-api/`

## Best Practices
- Use @mentions for urgent items
- Keep messages focused and actionable
- Update thread status when resolved
- Archive old threads quarterly

---
*Effective communication accelerates research breakthroughs!*