# TCP Consortium Conflict Monitor

**Real-time file conflict detection and prevention for multi-researcher collaboration**

Created by Dr. Sam Mitchell - Hardware Security Engineer  
TCP Research Consortium

---

## 🎯 Purpose

With multiple researchers working simultaneously on the TCP project, file conflicts are inevitable. This monitoring system provides:

- **Real-time conflict detection** - Instant alerts when multiple researchers edit the same file
- **Intelligent resolution suggestions** - Automated guidance for resolving conflicts
- **File locking mechanism** - Reserve files for exclusive editing
- **Collaboration insights** - Visualize researcher collaboration patterns
- **Web dashboard** - Monitor all activity from a central interface

---

## 🚀 Quick Start

### 1. Installation
```bash
# Run the installation script
./install_conflict_monitor.sh

# Or manually install dependencies
pip install watchdog
```

### 2. Start Monitoring
```bash
# Start the conflict monitor with dashboard
./start_conflict_monitor.sh

# Dashboard available at: http://localhost:8888
```

### 3. Python API Usage
```python
from tcp_conflict_monitor import ConflictDatabase, ResearcherCoordinator

# Check if file is safe to edit
db = ConflictDatabase()
coordinator = ResearcherCoordinator(db)

recommendations = coordinator.get_file_recommendations(
    "Sam Mitchell", 
    "../yuki-tanaka/tcp_performance.py"
)

if recommendations['safe_to_edit']:
    print("✓ Safe to edit")
else:
    print(f"❌ Not safe: {recommendations['reason']}")
```

---

## 📦 Features

### 1. **Conflict Detection**
- **Simultaneous edits** - Detects when multiple researchers edit within 5 minutes
- **Rapid succession** - Identifies rapid back-and-forth editing patterns
- **Git merge conflicts** - Detects unresolved merge conflict markers
- **File locking** - Prevents edits to locked files
- **Overwrite risks** - Warns about potential data loss

### 2. **Resolution Assistance**
- **Automated suggestions** - Step-by-step resolution guidance
- **Merge strategies** - Recommendations for combining changes
- **Communication prompts** - Suggests when to coordinate with others
- **Backup creation** - Automatic backups of shared files

### 3. **Coordination Tools**
- **File locking** - Reserve files for exclusive editing
- **Session tracking** - Monitor active research sessions
- **Edit scheduling** - Schedule editing windows
- **Collaboration graph** - Visualize who works together

### 4. **Web Dashboard**
- **Real-time updates** - Auto-refreshes every 30 seconds
- **Conflict overview** - All active conflicts with resolutions
- **Active sessions** - See who's currently working
- **System statistics** - Monitor system health
- **API endpoints** - RESTful API for integrations

---

## 🏗 Architecture

### Components

1. **ConflictDatabase** - SQLite storage for activities and conflicts
2. **ConflictDetector** - Analyzes file changes for potential conflicts
3. **ConsortiumFileHandler** - Watches file system for changes
4. **ConflictNotifier** - Multi-channel notification system
5. **ConflictResolver** - Suggests resolution strategies
6. **ResearcherCoordinator** - Manages researcher sessions and recommendations
7. **ConflictMonitorDashboard** - Web interface for monitoring

### Database Schema

```sql
-- File activities tracking
CREATE TABLE file_activities (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    researcher TEXT,
    action TEXT,  -- created, modified, deleted, moved
    timestamp TIMESTAMP,
    content_hash TEXT,
    file_size INTEGER,
    backup_path TEXT
);

-- Conflict records
CREATE TABLE conflicts (
    conflict_id TEXT PRIMARY KEY,
    conflict_type TEXT,  -- simultaneous_edit, rapid_succession, etc.
    file_path TEXT,
    researchers TEXT,  -- JSON array
    timestamp TIMESTAMP,
    description TEXT,
    resolution_status TEXT,
    resolution_details TEXT
);

-- File locks
CREATE TABLE file_locks (
    file_path TEXT PRIMARY KEY,
    researcher TEXT,
    lock_time TIMESTAMP,
    expected_duration INTEGER
);
```

---

## 🔧 Configuration

### Monitored Directories
The system monitors:
- Individual researcher directories (`sam-mitchell/`, `elena-vasquez/`, etc.)
- Shared directories (`communications/`, `shared/`, `convergence*/`)
- Consortium-wide files (`BULLETIN_BOARD.md`)

### Ignored Patterns
Automatically ignores:
- `__pycache__`, `.git`, `.DS_Store`
- `*.pyc`, `*.swp`, `*.tmp`
- Virtual environments (`venv/`, `env/`)

---

## 💻 API Reference

### Python API

#### Check File Safety
```python
coordinator.get_file_recommendations(researcher, file_path)
# Returns: {
#   'safe_to_edit': bool,
#   'reason': str,
#   'recommendations' or 'alternatives': list
# }
```

#### Lock/Unlock Files
```python
# Lock file for exclusive editing
db.lock_file(file_path, researcher, duration_seconds)

# Unlock file
db.unlock_file(file_path)

# Check lock status
lock_info = db.is_file_locked(file_path)
# Returns: (researcher, lock_time) or None
```

#### Record Activities
```python
activity = FileActivity(
    file_path="path/to/file.py",
    researcher="Researcher Name",
    action="modified",
    timestamp=datetime.now(),
    content_hash="sha256_hash",
    file_size=1024,
    backup_path="/backups/file.py.bak"
)
db.record_activity(activity)
```

#### Resolve Conflicts
```python
resolver = ConflictResolver(db)
resolution = resolver.suggest_resolution(conflict)
# Returns: {
#   'action': str,
#   'description': str,
#   'steps': list
# }
```

### REST API

#### Get Recommendations
```
GET /api/recommendations?researcher=Name&file=path/to/file
```

#### Get Active Conflicts
```
GET /api/conflicts
```

---

## 🚦 Conflict Types & Resolutions

### 1. Simultaneous Edit
**Detection**: Multiple researchers edit within 5 minutes  
**Resolution**: 
- Notify all researchers
- Create branches for each change
- Merge changes together
- Review merged result

### 2. Rapid Succession
**Detection**: 3+ edits by different researchers in short time  
**Resolution**:
- Establish editing order
- Use file locking
- Consider splitting file

### 3. Merge Conflict
**Detection**: Git conflict markers in file  
**Resolution**:
- Open in merge tool
- Resolve each conflict
- Remove markers
- Test and commit

### 4. Locked File
**Detection**: File has active lock  
**Resolution**:
- Contact lock owner
- Wait for release
- Request override if urgent

---

## 🛠 Advanced Usage

### Custom Monitoring
```python
from tcp_conflict_monitor import create_enhanced_monitor

# Create enhanced monitor with all features
EnhancedMonitor = create_enhanced_monitor()
monitor = EnhancedMonitor('/path/to/consortium')

# Start monitoring (runs forever)
monitor.start_monitoring()
```

### Workflow Integration
```python
class ResearchWorkflow:
    def __init__(self, researcher):
        self.researcher = researcher
        self.db = ConflictDatabase()
        self.coordinator = ResearcherCoordinator(self.db)
    
    def __enter__(self):
        self.coordinator.register_session(self.researcher)
        return self
    
    def __exit__(self, *args):
        self.coordinator.unregister_session(self.researcher)
    
    def safe_edit(self, file_path):
        # Check safety
        rec = self.coordinator.get_file_recommendations(
            self.researcher, file_path
        )
        if not rec['safe_to_edit']:
            raise RuntimeError(rec['reason'])
        
        # Lock and edit
        self.db.lock_file(file_path, self.researcher)
        try:
            # Your editing code here
            pass
        finally:
            self.db.unlock_file(file_path)

# Usage
with ResearchWorkflow("Sam Mitchell") as workflow:
    workflow.safe_edit("important_file.py")
```

---

## 🔍 Troubleshooting

### Monitor Not Starting
- Check Python version (3.8+ required)
- Verify watchdog is installed: `pip install watchdog`
- Check permissions on consortium directories

### Conflicts Not Detected
- Verify directories are being monitored (check logs)
- Ensure file changes are saved to disk
- Check ignored patterns aren't excluding files

### Dashboard Not Loading
- Verify port 8888 is available
- Check firewall settings
- Try different port: `--port 9999`

### Database Issues
- Database location: `tcp_conflicts.db`
- Reset database: `rm tcp_conflicts.db`
- Check disk space for database growth

---

## 📊 Best Practices

### For Researchers
1. **Check before editing** - Use the API or dashboard
2. **Lock long edits** - Reserve files for extended work
3. **Commit frequently** - Reduce conflict windows
4. **Communicate** - Coordinate with active editors

### For Integration
1. **Use context managers** - Ensure proper cleanup
2. **Handle exceptions** - Graceful degradation
3. **Monitor resources** - Database can grow large
4. **Regular backups** - Backup the conflicts database

---

## 🚀 Future Enhancements

### Planned Features
- **Slack/Email notifications** - Real-time alerts
- **Calendar integration** - Schedule editing windows
- **Diff visualization** - Show change conflicts
- **Auto-merge** - Attempt automatic resolution
- **Mobile app** - Monitor on the go

### Integration Points
- **Git hooks** - Pre-commit conflict checking
- **IDE plugins** - VSCode/PyCharm integration
- **CI/CD pipeline** - Prevent conflicting merges
- **Project management** - JIRA/GitHub integration

---

## 📞 Support

### Getting Help
- **Documentation**: This README and code comments
- **Examples**: `conflict_monitor_api_example.py`
- **Direct support**: sam.mitchell@tcp-consortium.org

### Reporting Issues
Include:
- Conflict type and files involved
- Researcher names
- Time of occurrence
- Dashboard screenshot if available

---

**Transform multi-researcher chaos into coordinated collaboration!**

The TCP Conflict Monitor ensures smooth teamwork by preventing conflicts before they happen and resolving them quickly when they do.

**Dr. Sam Mitchell**  
Hardware Security Engineer  
TCP Research Consortium