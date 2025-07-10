#!/usr/bin/env python3
"""
TCP Consortium Conflict Monitor
Dr. Sam Mitchell - Hardware Security Engineer

Real-time file conflict detection and prevention for multi-researcher collaboration.
Monitors shared files and alerts researchers to potential conflicts.
"""

import os
import sys
import time
import json
import hashlib
import asyncio
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from collections import defaultdict
import difflib
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConflictType(Enum):
    SIMULTANEOUS_EDIT = "simultaneous_edit"
    RAPID_SUCCESSION = "rapid_succession"
    MERGE_CONFLICT = "merge_conflict"
    LOCKED_FILE = "locked_file"
    OVERWRITE_RISK = "overwrite_risk"
    SHARED_RESOURCE = "shared_resource"

class FileStatus(Enum):
    AVAILABLE = "available"
    BEING_EDITED = "being_edited"
    LOCKED = "locked"
    CONFLICT = "conflict"
    RESOLVED = "resolved"

@dataclass
class FileActivity:
    """Track file modification activity"""
    file_path: str
    researcher: str
    action: str  # 'created', 'modified', 'deleted', 'moved'
    timestamp: datetime
    content_hash: str
    file_size: int
    backup_path: Optional[str] = None

@dataclass
class ConflictEvent:
    """Record of a detected conflict"""
    conflict_id: str
    conflict_type: ConflictType
    file_path: str
    researchers: List[str]
    timestamp: datetime
    description: str
    resolution_status: str = "pending"
    resolution_details: Optional[str] = None

class ConflictDatabase:
    """SQLite database for tracking file activities and conflicts"""
    
    def __init__(self, db_path: str = "tcp_conflicts.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables"""
        with self.lock:
            cursor = self.conn.cursor()
            
            # File activities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    researcher TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    content_hash TEXT,
                    file_size INTEGER,
                    backup_path TEXT
                )
            ''')
            
            # Create indexes for file_activities table
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_path ON file_activities(file_path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_researcher ON file_activities(researcher)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON file_activities(timestamp)')
            
            # Conflicts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conflicts (
                    conflict_id TEXT PRIMARY KEY,
                    conflict_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    researchers TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    description TEXT,
                    resolution_status TEXT DEFAULT 'pending',
                    resolution_details TEXT
                )
            ''')
            
            # Create indexes for conflicts table
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON conflicts(resolution_status)')
            
            # File locks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_locks (
                    file_path TEXT PRIMARY KEY,
                    researcher TEXT NOT NULL,
                    lock_time TIMESTAMP NOT NULL,
                    expected_duration INTEGER DEFAULT 3600
                )
            ''')
            
            self.conn.commit()
    
    def record_activity(self, activity: FileActivity):
        """Record file activity"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO file_activities 
                (file_path, researcher, action, timestamp, content_hash, file_size, backup_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                activity.file_path,
                activity.researcher,
                activity.action,
                activity.timestamp,
                activity.content_hash,
                activity.file_size,
                activity.backup_path
            ))
            self.conn.commit()
    
    def record_conflict(self, conflict: ConflictEvent):
        """Record detected conflict"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO conflicts
                (conflict_id, conflict_type, file_path, researchers, timestamp, 
                 description, resolution_status, resolution_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                conflict.conflict_id,
                conflict.conflict_type.value,
                conflict.file_path,
                json.dumps(conflict.researchers),
                conflict.timestamp,
                conflict.description,
                conflict.resolution_status,
                conflict.resolution_details
            ))
            self.conn.commit()
    
    def get_recent_activities(self, file_path: str, 
                            hours: int = 1) -> List[FileActivity]:
        """Get recent activities for a file"""
        with self.lock:
            cursor = self.conn.cursor()
            since = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT * FROM file_activities
                WHERE file_path = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (file_path, since))
            
            activities = []
            for row in cursor.fetchall():
                activities.append(FileActivity(
                    file_path=row[1],
                    researcher=row[2],
                    action=row[3],
                    timestamp=datetime.fromisoformat(row[4]),
                    content_hash=row[5],
                    file_size=row[6],
                    backup_path=row[7]
                ))
            
            return activities
    
    def is_file_locked(self, file_path: str) -> Optional[Tuple[str, datetime]]:
        """Check if file is locked"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT researcher, lock_time FROM file_locks
                WHERE file_path = ?
            ''', (file_path,))
            
            row = cursor.fetchone()
            if row:
                return (row[0], datetime.fromisoformat(row[1]))
            return None
    
    def lock_file(self, file_path: str, researcher: str, duration: int = 3600):
        """Lock a file for editing"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO file_locks
                (file_path, researcher, lock_time, expected_duration)
                VALUES (?, ?, ?, ?)
            ''', (file_path, researcher, datetime.now(), duration))
            self.conn.commit()
    
    def unlock_file(self, file_path: str):
        """Unlock a file"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM file_locks WHERE file_path = ?', (file_path,))
            self.conn.commit()
    
    def get_active_conflicts(self) -> List[ConflictEvent]:
        """Get unresolved conflicts"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM conflicts
                WHERE resolution_status = 'pending'
                ORDER BY timestamp DESC
            ''')
            
            conflicts = []
            for row in cursor.fetchall():
                conflicts.append(ConflictEvent(
                    conflict_id=row[0],
                    conflict_type=ConflictType(row[1]),
                    file_path=row[2],
                    researchers=json.loads(row[3]),
                    timestamp=datetime.fromisoformat(row[4]),
                    description=row[5],
                    resolution_status=row[6],
                    resolution_details=row[7]
                ))
            
            return conflicts

class ConflictDetector:
    """Detect potential file conflicts"""
    
    def __init__(self, db: ConflictDatabase):
        self.db = db
        self.active_editors: Dict[str, Set[str]] = defaultdict(set)
        self.file_hashes: Dict[str, str] = {}
        
    def detect_conflicts(self, file_path: str, researcher: str, 
                        action: str) -> Optional[ConflictEvent]:
        """Detect potential conflicts for file activity"""
        
        # Check if file is locked by another researcher
        lock_info = self.db.is_file_locked(file_path)
        if lock_info and lock_info[0] != researcher:
            return ConflictEvent(
                conflict_id=self._generate_conflict_id(),
                conflict_type=ConflictType.LOCKED_FILE,
                file_path=file_path,
                researchers=[researcher, lock_info[0]],
                timestamp=datetime.now(),
                description=f"File locked by {lock_info[0]} since {lock_info[1]}"
            )
        
        # Check recent activities
        recent_activities = self.db.get_recent_activities(file_path, hours=1)
        
        # Detect simultaneous editing
        active_researchers = set()
        for activity in recent_activities:
            if activity.action == 'modified' and activity.researcher != researcher:
                time_diff = datetime.now() - activity.timestamp
                if time_diff.total_seconds() < 300:  # Within 5 minutes
                    active_researchers.add(activity.researcher)
        
        if active_researchers:
            return ConflictEvent(
                conflict_id=self._generate_conflict_id(),
                conflict_type=ConflictType.SIMULTANEOUS_EDIT,
                file_path=file_path,
                researchers=[researcher] + list(active_researchers),
                timestamp=datetime.now(),
                description=f"Multiple researchers editing within 5 minutes"
            )
        
        # Detect rapid succession edits
        if len(recent_activities) >= 3:
            researchers = [a.researcher for a in recent_activities[:3]]
            if len(set(researchers)) > 1:
                return ConflictEvent(
                    conflict_id=self._generate_conflict_id(),
                    conflict_type=ConflictType.RAPID_SUCCESSION,
                    file_path=file_path,
                    researchers=list(set(researchers)),
                    timestamp=datetime.now(),
                    description="Multiple researchers making rapid changes"
                )
        
        # Check for merge conflicts in git
        if self._has_git_conflicts(file_path):
            return ConflictEvent(
                conflict_id=self._generate_conflict_id(),
                conflict_type=ConflictType.MERGE_CONFLICT,
                file_path=file_path,
                researchers=[researcher],
                timestamp=datetime.now(),
                description="Git merge conflicts detected"
            )
        
        return None
    
    def _generate_conflict_id(self) -> str:
        """Generate unique conflict ID"""
        return f"conflict_{int(time.time() * 1000)}"
    
    def _has_git_conflicts(self, file_path: str) -> bool:
        """Check if file has git merge conflicts"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                return '<<<<<<<' in content or '>>>>>>>' in content
        except:
            return False

class ConsortiumFileHandler(FileSystemEventHandler):
    """Handle file system events for consortium directories"""
    
    def __init__(self, db: ConflictDatabase, detector: ConflictDetector,
                 researcher_map: Dict[str, str]):
        self.db = db
        self.detector = detector
        self.researcher_map = researcher_map  # Map directory to researcher
        self.notifier = ConflictNotifier()
        
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_event(event.src_path, 'modified')
    
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_event(event.src_path, 'created')
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_file_event(event.src_path, 'deleted')
    
    def on_moved(self, event):
        if not event.is_directory:
            self._handle_file_event(event.dest_path, 'moved')
    
    def _handle_file_event(self, file_path: str, action: str):
        """Handle file system event"""
        
        # Skip temporary and system files
        if self._should_ignore(file_path):
            return
        
        # Determine researcher from path
        researcher = self._identify_researcher(file_path)
        if not researcher:
            return
        
        # Calculate file hash
        content_hash = self._calculate_file_hash(file_path) if action != 'deleted' else None
        file_size = os.path.getsize(file_path) if action != 'deleted' else 0
        
        # Create backup if modifying shared file
        backup_path = None
        if action == 'modified' and self._is_shared_file(file_path):
            backup_path = self._create_backup(file_path)
        
        # Record activity
        activity = FileActivity(
            file_path=file_path,
            researcher=researcher,
            action=action,
            timestamp=datetime.now(),
            content_hash=content_hash or "",
            file_size=file_size,
            backup_path=backup_path
        )
        self.db.record_activity(activity)
        
        # Detect conflicts
        conflict = self.detector.detect_conflicts(file_path, researcher, action)
        if conflict:
            self.db.record_conflict(conflict)
            self.notifier.notify_conflict(conflict)
            logger.warning(f"Conflict detected: {conflict.description}")
    
    def _should_ignore(self, file_path: str) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = [
            '__pycache__', '.git', '.DS_Store', '*.pyc', 
            '*.swp', '*.tmp', '~*', '.#*', 'venv', 'env'
        ]
        
        path = Path(file_path)
        for pattern in ignore_patterns:
            if pattern in str(path):
                return True
        
        return False
    
    def _identify_researcher(self, file_path: str) -> Optional[str]:
        """Identify researcher from file path"""
        for directory, researcher in self.researcher_map.items():
            if directory in file_path:
                return researcher
        return None
    
    def _is_shared_file(self, file_path: str) -> bool:
        """Check if file is in shared directory"""
        shared_dirs = [
            'communications', 'shared', 'consortium', 
            'BULLETIN_BOARD', 'convergence'
        ]
        
        return any(shared in file_path for shared in shared_dirs)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            return ""
    
    def _create_backup(self, file_path: str) -> str:
        """Create backup of file"""
        try:
            backup_dir = Path.home() / ".tcp_conflict_backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = Path(file_path).name
            backup_path = backup_dir / f"{timestamp}_{filename}"
            
            import shutil
            shutil.copy2(file_path, backup_path)
            
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""

class ConflictNotifier:
    """Notify researchers about conflicts"""
    
    def __init__(self):
        self.notification_methods = [
            self._log_notification,
            self._console_notification,
            self._file_notification,
            # self._email_notification,  # Uncomment if email configured
            # self._slack_notification,   # Uncomment if Slack configured
        ]
    
    def notify_conflict(self, conflict: ConflictEvent):
        """Send notifications about conflict"""
        for method in self.notification_methods:
            try:
                method(conflict)
            except Exception as e:
                logger.error(f"Notification failed: {e}")
    
    def _log_notification(self, conflict: ConflictEvent):
        """Log conflict to system log"""
        logger.warning(f"CONFLICT: {conflict.conflict_type.value} - "
                      f"File: {conflict.file_path} - "
                      f"Researchers: {', '.join(conflict.researchers)}")
    
    def _console_notification(self, conflict: ConflictEvent):
        """Print conflict to console"""
        print(f"\n{'='*60}")
        print(f"⚠️  CONFLICT DETECTED: {conflict.conflict_type.value}")
        print(f"📄 File: {conflict.file_path}")
        print(f"👥 Researchers: {', '.join(conflict.researchers)}")
        print(f"📝 Description: {conflict.description}")
        print(f"🕐 Time: {conflict.timestamp}")
        print(f"{'='*60}\n")
    
    def _file_notification(self, conflict: ConflictEvent):
        """Write conflict to notification file"""
        notification_dir = Path.home() / ".tcp_conflicts"
        notification_dir.mkdir(exist_ok=True)
        
        notification_file = notification_dir / "active_conflicts.json"
        
        # Load existing conflicts
        conflicts = []
        if notification_file.exists():
            with open(notification_file, 'r') as f:
                conflicts = json.load(f)
        
        # Add new conflict
        conflicts.append({
            'conflict_id': conflict.conflict_id,
            'type': conflict.conflict_type.value,
            'file': conflict.file_path,
            'researchers': conflict.researchers,
            'timestamp': conflict.timestamp.isoformat(),
            'description': conflict.description
        })
        
        # Save updated conflicts
        with open(notification_file, 'w') as f:
            json.dump(conflicts, f, indent=2)
    
    def _email_notification(self, conflict: ConflictEvent):
        """Send email notification (requires configuration)"""
        # This would require email server configuration
        pass
    
    def _slack_notification(self, conflict: ConflictEvent):
        """Send Slack notification (requires webhook)"""
        # This would require Slack webhook configuration
        pass

class ConflictMonitorDashboard:
    """Real-time dashboard for conflict monitoring"""
    
    def __init__(self, db: ConflictDatabase):
        self.db = db
        
    def generate_dashboard(self) -> str:
        """Generate dashboard HTML"""
        
        # Get active conflicts
        conflicts = self.db.get_active_conflicts()
        
        # Get recent activities
        activities = []
        # Would need to implement get_all_recent_activities
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>TCP Consortium Conflict Monitor</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .conflict {{ 
            background: #ffe6e6; 
            border: 1px solid #ff9999; 
            padding: 10px; 
            margin: 10px 0;
            border-radius: 5px;
        }}
        .activity {{
            background: #f0f0f0;
            padding: 5px;
            margin: 5px 0;
            border-radius: 3px;
        }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .researcher {{ font-weight: bold; color: #0066cc; }}
        .file-path {{ font-family: monospace; color: #006600; }}
    </style>
</head>
<body>
    <h1>🔍 TCP Consortium Conflict Monitor</h1>
    <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>⚠️ Active Conflicts ({len(conflicts)})</h2>
    {''.join(self._format_conflict(c) for c in conflicts)}
    
    <h2>📝 Recent Activities</h2>
    {''.join(self._format_activity(a) for a in activities[:20])}
</body>
</html>
"""
        return html
    
    def _format_conflict(self, conflict: ConflictEvent) -> str:
        """Format conflict for HTML display"""
        return f"""
<div class="conflict">
    <strong>{conflict.conflict_type.value.upper()}</strong><br>
    File: <span class="file-path">{conflict.file_path}</span><br>
    Researchers: <span class="researcher">{', '.join(conflict.researchers)}</span><br>
    Description: {conflict.description}<br>
    <span class="timestamp">{conflict.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</span>
</div>
"""
    
    def _format_activity(self, activity: FileActivity) -> str:
        """Format activity for HTML display"""
        return f"""
<div class="activity">
    <span class="researcher">{activity.researcher}</span> 
    {activity.action} 
    <span class="file-path">{activity.file_path}</span>
    <span class="timestamp">{activity.timestamp.strftime('%H:%M:%S')}</span>
</div>
"""

class ConflictMonitor:
    """Main conflict monitoring system"""
    
    def __init__(self, consortium_root: str):
        self.consortium_root = Path(consortium_root)
        self.db = ConflictDatabase()
        self.detector = ConflictDetector(self.db)
        self.dashboard = ConflictMonitorDashboard(self.db)
        
        # Map directories to researchers
        self.researcher_map = {
            'sam-mitchell': 'Sam Mitchell',
            'elena-vasquez': 'Elena Vasquez',
            'marcus-chen': 'Marcus Chen',
            'yuki-tanaka': 'Yuki Tanaka',
            'aria-blackwood': 'Aria Blackwood',
            'alex-rivera': 'Alex Rivera',
            'dr-alex-rivera': 'Alex Rivera'
        }
        
        self.observer = Observer()
        self.handler = ConsortiumFileHandler(self.db, self.detector, self.researcher_map)
        
    def start_monitoring(self):
        """Start monitoring consortium directories"""
        logger.info(f"Starting conflict monitor for {self.consortium_root}")
        
        # Monitor each researcher's directory
        for researcher_dir in self.researcher_map.keys():
            path = self.consortium_root / researcher_dir
            if path.exists():
                self.observer.schedule(self.handler, str(path), recursive=True)
                logger.info(f"Monitoring {path}")
        
        # Monitor shared directories
        shared_dirs = ['communications', 'shared', 'convergence-20250704-elena-marcus']
        for shared_dir in shared_dirs:
            path = self.consortium_root / shared_dir
            if path.exists():
                self.observer.schedule(self.handler, str(path), recursive=True)
                logger.info(f"Monitoring shared directory: {path}")
        
        # Start observer
        self.observer.start()
        
        # Start dashboard server
        self._start_dashboard_server()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            logger.info("Conflict monitor stopped")
        
        self.observer.join()
    
    def _start_dashboard_server(self):
        """Start web dashboard server"""
        import http.server
        import socketserver
        from functools import partial
        
        class DashboardHandler(http.server.BaseHTTPRequestHandler):
            def __init__(self, dashboard, *args, **kwargs):
                self.dashboard = dashboard
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(self.dashboard.generate_dashboard().encode())
                else:
                    self.send_error(404)
        
        handler = partial(DashboardHandler, self.dashboard)
        
        def serve():
            with socketserver.TCPServer(("", 8888), handler) as httpd:
                logger.info("Dashboard available at http://localhost:8888")
                httpd.serve_forever()
        
        dashboard_thread = threading.Thread(target=serve, daemon=True)
        dashboard_thread.start()

# Command-line interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="TCP Consortium Conflict Monitor")
    parser.add_argument('--root', default='..', 
                       help='Consortium root directory')
    parser.add_argument('--dashboard-only', action='store_true',
                       help='Only show dashboard for existing conflicts')
    
    args = parser.parse_args()
    
    if args.dashboard_only:
        db = ConflictDatabase()
        dashboard = ConflictMonitorDashboard(db)
        print(dashboard.generate_dashboard())
    else:
        monitor = ConflictMonitor(args.root)
        monitor.start_monitoring()

class ConflictResolver:
    """Automated conflict resolution suggestions"""
    
    def __init__(self, db: ConflictDatabase):
        self.db = db
        
    def suggest_resolution(self, conflict: ConflictEvent) -> Dict[str, Any]:
        """Suggest resolution for conflict"""
        
        if conflict.conflict_type == ConflictType.SIMULTANEOUS_EDIT:
            return self._resolve_simultaneous_edit(conflict)
        elif conflict.conflict_type == ConflictType.RAPID_SUCCESSION:
            return self._resolve_rapid_succession(conflict)
        elif conflict.conflict_type == ConflictType.MERGE_CONFLICT:
            return self._resolve_merge_conflict(conflict)
        elif conflict.conflict_type == ConflictType.LOCKED_FILE:
            return self._resolve_locked_file(conflict)
        else:
            return {'action': 'manual', 'description': 'Manual resolution required'}
    
    def _resolve_simultaneous_edit(self, conflict: ConflictEvent) -> Dict[str, Any]:
        """Suggest resolution for simultaneous edits"""
        return {
            'action': 'merge',
            'description': 'Merge changes from both researchers',
            'steps': [
                f"1. Notify {', '.join(conflict.researchers)} about simultaneous edits",
                "2. Create branch for each researcher's changes",
                "3. Use git merge or manual merge to combine changes",
                "4. Have both researchers review merged result"
            ]
        }
    
    def _resolve_rapid_succession(self, conflict: ConflictEvent) -> Dict[str, Any]:
        """Suggest resolution for rapid succession edits"""
        return {
            'action': 'coordinate',
            'description': 'Coordinate editing schedule',
            'steps': [
                "1. Establish editing order among researchers",
                "2. Use file locking mechanism",
                "3. Set up notification when file is available",
                "4. Consider breaking file into smaller modules"
            ]
        }
    
    def _resolve_merge_conflict(self, conflict: ConflictEvent) -> Dict[str, Any]:
        """Suggest resolution for git merge conflicts"""
        return {
            'action': 'git_merge',
            'description': 'Resolve git merge conflicts',
            'steps': [
                f"1. Open {conflict.file_path} in merge tool",
                "2. Review conflict markers (<<<<<<, ======, >>>>>>)",
                "3. Choose appropriate resolution for each conflict",
                "4. Remove conflict markers and test code",
                "5. Commit resolved version"
            ]
        }
    
    def _resolve_locked_file(self, conflict: ConflictEvent) -> Dict[str, Any]:
        """Suggest resolution for locked files"""
        lock_info = self.db.is_file_locked(conflict.file_path)
        if lock_info:
            lock_time = (datetime.now() - lock_info[1]).total_seconds() / 3600
            return {
                'action': 'wait_or_override',
                'description': f'File locked by {lock_info[0]} for {lock_time:.1f} hours',
                'steps': [
                    f"1. Contact {lock_info[0]} about lock status",
                    "2. Wait for lock to expire or be released",
                    "3. If urgent, request admin override",
                    "4. Consider working on copy and merging later"
                ]
            }
        return {'action': 'manual', 'description': 'Lock information unavailable'}

class ResearcherCoordinator:
    """Coordinate researcher activities and prevent conflicts"""
    
    def __init__(self, db: ConflictDatabase):
        self.db = db
        self.resolver = ConflictResolver(db)
        self.active_sessions: Dict[str, datetime] = {}
        
    def register_session(self, researcher: str):
        """Register active research session"""
        self.active_sessions[researcher] = datetime.now()
        logger.info(f"Research session started: {researcher}")
        
    def unregister_session(self, researcher: str):
        """Unregister research session"""
        if researcher in self.active_sessions:
            duration = datetime.now() - self.active_sessions[researcher]
            del self.active_sessions[researcher]
            logger.info(f"Research session ended: {researcher} (duration: {duration})")
    
    def get_file_recommendations(self, researcher: str, file_path: str) -> Dict[str, Any]:
        """Get recommendations before editing a file"""
        
        # Check if file is locked
        lock_info = self.db.is_file_locked(file_path)
        if lock_info and lock_info[0] != researcher:
            return {
                'safe_to_edit': False,
                'reason': f'File locked by {lock_info[0]}',
                'alternatives': ['Wait for lock release', 'Work on different file', 'Contact researcher']
            }
        
        # Check recent activities
        recent_activities = self.db.get_recent_activities(file_path, hours=2)
        active_editors = set()
        
        for activity in recent_activities:
            if activity.researcher != researcher and activity.action == 'modified':
                time_diff = datetime.now() - activity.timestamp
                if time_diff.total_seconds() < 600:  # Within 10 minutes
                    active_editors.add(activity.researcher)
        
        if active_editors:
            return {
                'safe_to_edit': False,
                'reason': f"Recently edited by: {', '.join(active_editors)}",
                'alternatives': ['Coordinate with other researchers', 'Use file locking', 'Wait 10 minutes']
            }
        
        return {
            'safe_to_edit': True,
            'reason': 'No conflicts detected',
            'recommendations': ['Consider using file lock for long edits', 'Commit changes frequently']
        }
    
    def schedule_editing_window(self, researcher: str, file_path: str, 
                              start_time: datetime, duration_hours: int) -> bool:
        """Schedule exclusive editing window"""
        # This would integrate with a calendar/scheduling system
        # For now, just use the locking mechanism
        
        # Check if window is available
        lock_info = self.db.is_file_locked(file_path)
        if lock_info:
            return False
        
        # Schedule the window (simplified - just lock immediately)
        self.db.lock_file(file_path, researcher, duration_hours * 3600)
        return True
    
    def get_collaboration_graph(self) -> Dict[str, List[str]]:
        """Get graph of researcher collaborations based on shared files"""
        collaborations = defaultdict(set)
        
        # Analyze recent activities to find collaborations
        # This is a simplified version - would query all recent activities
        conflicts = self.db.get_active_conflicts()
        
        for conflict in conflicts:
            researchers = conflict.researchers
            for i in range(len(researchers)):
                for j in range(i + 1, len(researchers)):
                    collaborations[researchers[i]].add(researchers[j])
                    collaborations[researchers[j]].add(researchers[i])
        
        # Convert sets to lists for JSON serialization
        return {k: list(v) for k, v in collaborations.items()}

# Update the main monitor class to include new components
def create_enhanced_monitor():
    """Create enhanced conflict monitor with all components"""
    
    class EnhancedConflictMonitor(ConflictMonitor):
        def __init__(self, consortium_root: str):
            super().__init__(consortium_root)
            self.coordinator = ResearcherCoordinator(self.db)
            self.resolver = ConflictResolver(self.db)
            
        def _start_dashboard_server(self):
            """Enhanced dashboard with coordination features"""
            import http.server
            import socketserver
            from functools import partial
            
            class EnhancedDashboardHandler(http.server.BaseHTTPRequestHandler):
                def __init__(self, monitor, *args, **kwargs):
                    self.monitor = monitor
                    super().__init__(*args, **kwargs)
                
                def do_GET(self):
                    if self.path == '/':
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(self._generate_enhanced_dashboard().encode())
                    elif self.path == '/api/recommendations':
                        self._handle_recommendations()
                    elif self.path == '/api/conflicts':
                        self._handle_conflicts()
                    else:
                        self.send_error(404)
                
                def _generate_enhanced_dashboard(self) -> str:
                    conflicts = self.monitor.db.get_active_conflicts()
                    active_sessions = self.monitor.coordinator.active_sessions
                    collaboration_graph = self.monitor.coordinator.get_collaboration_graph()
                    
                    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>TCP Consortium Conflict Monitor - Enhanced</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; text-align: center; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .panel {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .conflict {{ background: #ffe6e6; border: 1px solid #ff9999; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .resolution {{ background: #e6f3ff; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .active-session {{ background: #e6ffe6; padding: 5px 10px; margin: 5px 0; border-radius: 3px; }}
        .collaboration {{ background: #fff3e6; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .researcher {{ font-weight: bold; color: #0066cc; }}
        .file-path {{ font-family: monospace; color: #006600; }}
        .status-indicator {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }}
        .status-active {{ background: #4CAF50; }}
        .status-conflict {{ background: #f44336; }}
        .status-resolved {{ background: #2196F3; }}
        button {{ background: #2196F3; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }}
        button:hover {{ background: #1976D2; }}
    </style>
    <script>
        function requestRecommendations(researcher, filePath) {{
            fetch(`/api/recommendations?researcher=${{researcher}}&file=${{filePath}}`)
                .then(response => response.json())
                .then(data => alert(JSON.stringify(data, null, 2)));
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>🔍 TCP Consortium Conflict Monitor</h1>
        <p style="text-align: center;">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="grid">
            <div class="panel">
                <h2>⚠️ Active Conflicts ({len(conflicts)})</h2>
                {''.join(self._format_enhanced_conflict(c) for c in conflicts)}
            </div>
            
            <div class="panel">
                <h2>👥 Active Research Sessions ({len(active_sessions)})</h2>
                {''.join(self._format_session(r, t) for r, t in active_sessions.items())}
                
                <h3>🤝 Collaboration Network</h3>
                {''.join(self._format_collaboration(r, c) for r, c in collaboration_graph.items() if c)}
            </div>
        </div>
        
        <div class="panel" style="margin-top: 20px;">
            <h2>📊 System Statistics</h2>
            <p>Total monitored directories: {len(self.monitor.researcher_map) + 3}</p>
            <p>Database size: {os.path.getsize(self.monitor.db.db_path) / 1024 / 1024:.1f} MB</p>
        </div>
    </div>
</body>
</html>
"""
                    return html
                
                def _format_enhanced_conflict(self, conflict: ConflictEvent) -> str:
                    resolution = self.monitor.resolver.suggest_resolution(conflict)
                    return f"""
<div class="conflict">
    <span class="status-indicator status-conflict"></span>
    <strong>{conflict.conflict_type.value.upper()}</strong><br>
    File: <span class="file-path">{conflict.file_path}</span><br>
    Researchers: <span class="researcher">{', '.join(conflict.researchers)}</span><br>
    Description: {conflict.description}<br>
    <span class="timestamp">{conflict.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</span>
    
    <div class="resolution">
        <strong>Suggested Resolution:</strong> {resolution['description']}<br>
        {'<br>'.join(resolution.get('steps', []))}
    </div>
</div>
"""
                
                def _format_session(self, researcher: str, start_time: datetime) -> str:
                    duration = datetime.now() - start_time
                    return f"""
<div class="active-session">
    <span class="status-indicator status-active"></span>
    <span class="researcher">{researcher}</span> - Active for {duration.total_seconds() / 3600:.1f} hours
</div>
"""
                
                def _format_collaboration(self, researcher: str, collaborators: List[str]) -> str:
                    return f"""
<div class="collaboration">
    <span class="researcher">{researcher}</span> collaborates with: {', '.join(collaborators)}
</div>
"""
                
                def _handle_recommendations(self):
                    """API endpoint for file editing recommendations"""
                    # Parse query parameters
                    from urllib.parse import urlparse, parse_qs
                    query = parse_qs(urlparse(self.path).query)
                    
                    researcher = query.get('researcher', [''])[0]
                    file_path = query.get('file', [''])[0]
                    
                    if researcher and file_path:
                        recommendations = self.monitor.coordinator.get_file_recommendations(
                            researcher, file_path
                        )
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(recommendations).encode())
                    else:
                        self.send_error(400, "Missing parameters")
                
                def _handle_conflicts(self):
                    """API endpoint for conflict data"""
                    conflicts = self.monitor.db.get_active_conflicts()
                    conflict_data = []
                    
                    for conflict in conflicts:
                        resolution = self.monitor.resolver.suggest_resolution(conflict)
                        conflict_data.append({
                            'id': conflict.conflict_id,
                            'type': conflict.conflict_type.value,
                            'file': conflict.file_path,
                            'researchers': conflict.researchers,
                            'timestamp': conflict.timestamp.isoformat(),
                            'description': conflict.description,
                            'resolution': resolution
                        })
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(conflict_data).encode())
            
            handler = partial(EnhancedDashboardHandler, self)
            
            def serve():
                with socketserver.TCPServer(("", 8888), handler) as httpd:
                    logger.info("Enhanced dashboard available at http://localhost:8888")
                    httpd.serve_forever()
            
            dashboard_thread = threading.Thread(target=serve, daemon=True)
            dashboard_thread.start()
    
    return EnhancedConflictMonitor

if __name__ == "__main__":
    main()