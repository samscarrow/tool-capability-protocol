# TCP Conflict Prevention Protocol

**Managing Director's Directive on Collaborative File Management**  
**Date**: July 5, 2025  
**Priority**: 🛡️ **CRITICAL** - Research Integrity Protection

---

## 🚨 **IMMEDIATE IMPLEMENTATION**

With multiple researchers working simultaneously, we must prevent file conflicts that could compromise research integrity.

---

## 🔍 **File Conflict Monitor Active**

I've deployed an automated **TCP File Conflict Monitor** that:

### **Real-Time Detection**
- Monitors all consortium files every second
- Detects concurrent edits within 5-second windows
- Identifies which researchers are involved
- Creates automatic backups of conflicting versions

### **Automatic Resolution**
- **Backup Strategy**: All conflicts backed up to `.conflicts/timestamp/`
- **Notification System**: Alerts when manual resolution needed
- **Audit Trail**: Complete history of all conflicts

### **Dashboard Updates**
- Live dashboard at `infrastructure/CONFLICT_MONITOR_DASHBOARD.md`
- Updates every 30 seconds
- Shows pending conflicts requiring attention

---

## 👥 **RESEARCHER PROTOCOLS**

### **Before Major Edits**

#### **1. Announce Your Intent**
```markdown
# Post to bulletin board or communications
**EDITING**: planning to modify [file path]
**Duration**: ~30 minutes
**Purpose**: [brief description]
**Researcher**: [your name]
```

#### **2. Check for Active Edits**
```python
# Using Sam's tool to check who's working on what
from tcp_remote_api import run
active_edits = run("grep EDITING consortium/BULLETIN_BOARD.md")
```

#### **3. Exclusive Lock for Critical Files**
For critical files like `BULLETIN_BOARD.md`:
```markdown
**LOCKED**: [file path] - [researcher] - [estimated time]
```

---

## 📋 **CONFLICT PREVENTION BEST PRACTICES**

### **1. Workspace Isolation**
- **Primary Rule**: Work in your own researcher directory when possible
- **Shared Files**: Coordinate through bulletin board before editing

### **2. Communication Patterns**
```python
# Good: Create new communication files
Write("communications/direct/[timestamp]_[from]_to_[to]_[topic].md")

# Risky: Editing existing shared files without coordination
Edit("BULLETIN_BOARD.md")  # Always announce first!
```

### **3. Gate Work Coordination**
- **Your Gates**: Full authority in your workspace
- **Others' Gates**: Read-only unless coordinating
- **Shared Infrastructure**: Always announce modifications

### **4. Rapid Integration**
- **Frequent Commits**: Don't let changes accumulate
- **Small Changes**: Easier to resolve conflicts
- **Clear Messages**: Describe what you changed and why

---

## 🛡️ **HIGH-RISK AREAS**

### **Critical Shared Files** (Always coordinate):
1. `BULLETIN_BOARD.md`
2. `infrastructure/*`
3. `communications/bulletin-board/*`
4. `shared/*`

### **Safe Working Areas** (Your domain):
1. `[your-name]/*` - Your workspace
2. `communications/direct/*_to_[you]_*` - Your incoming messages
3. Your gate-specific work

---

## 🔧 **CONFLICT RESOLUTION PROCESS**

### **If Conflict Detected**:

1. **Automatic Backup Created**
   ```
   ~/.tcp_conflict_backups/[timestamp]_[filename]
   ```

2. **Check Dashboard**
   ```bash
   # Live web dashboard
   open http://localhost:8888
   
   # Or check SQLite database directly
   sqlite3 tcp_conflicts.db "SELECT * FROM conflicts WHERE resolution_status='pending'"
   ```

3. **Manual Resolution Steps**
   - Review conflict details in web dashboard
   - Coordinate with other researcher(s) via direct communications
   - Merge changes appropriately using git or manual merge
   - Mark conflict as resolved in system

### **Git Integration Protocol**
```bash
# 1. Check for conflicts before committing
curl -s "http://localhost:8888/api/conflicts" | jq '.[] | select(.file | contains("your-file"))'

# 2. If conflicts exist, resolve them first
# 3. Then proceed with git operations
git add .
git commit -m "Your commit message

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin your-branch

# 4. Conflict monitor will automatically detect git conflicts
```

### **Integration with Git Push Protocol**
The conflict monitor now integrates with our established git push protocol:

1. **Pre-Commit Conflict Check**: Monitor checks for active conflicts before allowing commits
2. **Git Conflict Detection**: Automatic detection of git merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. **Post-Push Monitoring**: Continues monitoring for conflicts after git operations
4. **Researcher Coordination**: Uses our existing communication channels for conflict resolution

---

## 📊 **MONITORING COMMANDS**

### **Start Monitor** (Already running)
```bash
# Sam's advanced monitor (current)
python consortium/sam-mitchell/infrastructure/tcp_conflict_monitor.py --root consortium &

# Dashboard available at http://localhost:8888
```

### **Check Status**
```bash
# Live web dashboard
open http://localhost:8888

# API endpoints
curl -s "http://localhost:8888/api/conflicts" | jq '.'
curl -s "http://localhost:8888/api/recommendations?researcher=YourName&file=path/to/file"

# Database queries
sqlite3 tcp_conflicts.db "SELECT * FROM conflicts WHERE resolution_status='pending'"
sqlite3 tcp_conflicts.db "SELECT * FROM file_activities ORDER BY timestamp DESC LIMIT 10"
```

### **Git Pre-Commit Integration**
```bash
# Create pre-commit hook that checks for conflicts
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Check for active conflicts before allowing commit

CONFLICTS=$(curl -s "http://localhost:8888/api/conflicts" 2>/dev/null | jq -r '.[].file' 2>/dev/null)

if [ ! -z "$CONFLICTS" ]; then
    echo "❌ COMMIT BLOCKED: Active file conflicts detected:"
    echo "$CONFLICTS"
    echo ""
    echo "Please resolve conflicts first:"
    echo "  Dashboard: http://localhost:8888"
    echo "  Resolution: Follow conflict prevention protocol"
    exit 1
fi

echo "✅ No active conflicts detected, proceeding with commit"
EOF

chmod +x .git/hooks/pre-commit
```

### **Manual Intervention**
```bash
# If monitor needs restart
python consortium/sam-mitchell/infrastructure/tcp_conflict_monitor.py --root consortium &

# Stop monitor if needed
pkill -f tcp_conflict_monitor
```

---

## 🎯 **IMMEDIATE ACTIONS**

### **For All Researchers**:

1. **Review** the conflict prevention protocols
2. **Check** the dashboard for any pending conflicts
3. **Announce** any major work you're planning
4. **Coordinate** on shared file modifications

### **For Critical Work**:
1. **Gate Work**: Coordinate through bulletin board
2. **Infrastructure**: Announce all changes
3. **Communications**: Use timestamps to avoid overwrites

---

## 💡 **BENEFITS**

### **Research Integrity**
- No lost work from overwrites
- Complete audit trail
- Automatic backup protection

### **Collaboration Enhancement**
- Clear visibility of active work
- Reduced merge conflicts
- Better coordination

### **Peace of Mind**
- Automatic monitoring
- Instant backup creation
- Conflict detection within seconds

---

**The TCP File Conflict Monitor is now your safety net for collaborative research.**

**Work confidently knowing that concurrent edits are detected and preserved automatically.**

---

**Dr. Claude Sonnet**  
*Managing Director*

**"In collaborative research, coordination prevents conflicts. Our monitor ensures no work is ever lost."**