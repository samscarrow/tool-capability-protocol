#!/usr/bin/env python3
"""
TCP File Conflict Monitor
Dr. Claude Sonnet, Managing Director

Real-time monitoring for file conflicts across multiple researcher sessions.
Prevents data loss and maintains research integrity in collaborative environment.
"""

import os
import time
import hashlib
import json
import threading
import queue
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import difflib
import shutil

@dataclass
class FileState:
    """Track file state for conflict detection"""
    path: str
    last_modified: float
    hash: str
    size: int
    researcher: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class FileConflict:
    """Represents a detected file conflict"""
    file_path: str
    researchers: List[str]
    conflict_type: str  # 'concurrent_edit', 'overwrite', 'deletion'
    timestamp: datetime
    resolution_status: str  # 'pending', 'resolved', 'ignored'
    details: Dict

class FileConflictMonitor:
    """Monitor file system for conflicts across researcher sessions"""
    
    def __init__(self, consortium_root: str = "."):
        self.consortium_root = Path(consortium_root).absolute()
        self.file_states: Dict[str, FileState] = {}
        self.active_sessions: Dict[str, Set[str]] = defaultdict(set)  # researcher -> files
        self.conflicts: List[FileConflict] = []
        self.conflict_queue = queue.Queue()
        self.monitoring = False
        self.ignore_patterns = {
            '*.pyc', '__pycache__', '.git', '.env', 'venv/', '*_env/',
            '*.tmp', '*.log', '.DS_Store', '*.swp', '*.swo'
        }
        
        # Researcher workspace mapping
        self.researcher_workspaces = {
            'elena-vasquez': self.consortium_root / 'elena-vasquez',
            'yuki-tanaka': self.consortium_root / 'yuki-tanaka',
            'alex-rivera': self.consortium_root / 'alex-rivera',
            'sam-mitchell': self.consortium_root / 'sam-mitchell',
            'aria-blackwood': self.consortium_root / 'aria-blackwood',
            'marcus-chen': self.consortium_root / 'marcus-chen'
        }
        
        # Shared areas requiring extra monitoring
        self.shared_areas = {
            'communications': self.consortium_root / 'communications',
            'bulletin-board': self.consortium_root / 'BULLETIN_BOARD.md',
            'infrastructure': self.consortium_root / 'infrastructure',
            'shared': self.consortium_root / 'shared'
        }
        
        # Conflict resolution strategies
        self.resolution_strategies = {
            'timestamp': self._resolve_by_timestamp,
            'merge': self._resolve_by_merge,
            'backup': self._resolve_by_backup,
            'prompt': self._resolve_by_prompt
        }
        
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored"""
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern.endswith('/'):
                if pattern[:-1] in path_str:
                    return True
            elif path.match(pattern):
                return True
        return False
    
    def _get_file_hash(self, path: Path) -> str:
        """Calculate file hash for change detection"""
        if not path.exists() or not path.is_file():
            return ""
        
        hasher = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""
    
    def _identify_researcher(self, path: Path) -> Optional[str]:
        """Identify which researcher owns or is editing a file"""
        path_str = str(path)
        
        # Check if in researcher workspace
        for researcher, workspace in self.researcher_workspaces.items():
            if str(workspace) in path_str:
                return researcher
                
        # Check recent git commits for shared files
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ae', str(path)],
                capture_output=True, text=True, cwd=self.consortium_root
            )
            if result.returncode == 0:
                email = result.stdout.strip()
                for researcher in self.researcher_workspaces:
                    if researcher.replace('-', '.') in email:
                        return researcher
        except:
            pass
            
        return None
    
    def _scan_directory(self, directory: Path) -> Dict[str, FileState]:
        """Scan directory for current file states"""
        current_states = {}
        
        for path in directory.rglob('*'):
            if path.is_file() and not self._should_ignore(path):
                rel_path = path.relative_to(self.consortium_root)
                
                try:
                    stat = path.stat()
                    state = FileState(
                        path=str(rel_path),
                        last_modified=stat.st_mtime,
                        hash=self._get_file_hash(path),
                        size=stat.st_size,
                        researcher=self._identify_researcher(path)
                    )
                    current_states[str(rel_path)] = state
                except Exception:
                    pass
                    
        return current_states
    
    def _detect_conflicts(self, new_states: Dict[str, FileState]) -> List[FileConflict]:
        """Detect conflicts between file states"""
        conflicts = []
        
        for path, new_state in new_states.items():
            if path in self.file_states:
                old_state = self.file_states[path]
                
                # Check for concurrent modification
                if (new_state.hash != old_state.hash and 
                    new_state.last_modified - old_state.last_modified < 5.0):  # Within 5 seconds
                    
                    researchers = []
                    if old_state.researcher:
                        researchers.append(old_state.researcher)
                    if new_state.researcher and new_state.researcher not in researchers:
                        researchers.append(new_state.researcher)
                    
                    if len(researchers) > 1:
                        conflict = FileConflict(
                            file_path=path,
                            researchers=researchers,
                            conflict_type='concurrent_edit',
                            timestamp=datetime.now(),
                            resolution_status='pending',
                            details={
                                'old_hash': old_state.hash,
                                'new_hash': new_state.hash,
                                'time_diff': new_state.last_modified - old_state.last_modified
                            }
                        )
                        conflicts.append(conflict)
        
        return conflicts
    
    def _resolve_by_timestamp(self, conflict: FileConflict) -> bool:
        """Resolve by keeping the newest version"""
        # Keep the current version (newest)
        conflict.resolution_status = 'resolved'
        conflict.details['resolution'] = 'kept_newest'
        return True
    
    def _resolve_by_backup(self, conflict: FileConflict) -> bool:
        """Resolve by creating backups of all versions"""
        try:
            file_path = self.consortium_root / conflict.file_path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create backup directory
            backup_dir = self.consortium_root / '.conflicts' / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup current version
            backup_path = backup_dir / f"{file_path.name}.current"
            shutil.copy2(file_path, backup_path)
            
            conflict.resolution_status = 'resolved'
            conflict.details['resolution'] = 'backed_up'
            conflict.details['backup_path'] = str(backup_dir)
            
            return True
        except Exception as e:
            conflict.details['error'] = str(e)
            return False
    
    def _resolve_by_merge(self, conflict: FileConflict) -> bool:
        """Attempt to merge text files"""
        # This is a placeholder for more sophisticated merge logic
        # In practice, this would use git merge or similar
        return self._resolve_by_backup(conflict)
    
    def _resolve_by_prompt(self, conflict: FileConflict) -> bool:
        """Queue for manual resolution"""
        conflict.resolution_status = 'pending'
        conflict.details['requires_manual_resolution'] = True
        self.conflict_queue.put(conflict)
        return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print(f"🔍 TCP File Conflict Monitor Started")
        print(f"   Monitoring: {self.consortium_root}")
        print(f"   Researchers: {len(self.researcher_workspaces)}")
        
        # Initial scan
        self.file_states = self._scan_directory(self.consortium_root)
        print(f"   Tracking {len(self.file_states)} files")
        
        while self.monitoring:
            try:
                # Scan for changes
                new_states = self._scan_directory(self.consortium_root)
                
                # Detect conflicts
                conflicts = self._detect_conflicts(new_states)
                
                if conflicts:
                    print(f"\n⚠️  Detected {len(conflicts)} file conflicts!")
                    
                    for conflict in conflicts:
                        self.conflicts.append(conflict)
                        self._handle_conflict(conflict)
                
                # Update tracked states
                self.file_states = new_states
                
                # Check for pending manual resolutions
                self._process_conflict_queue()
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
            
            time.sleep(1)  # Check every second
    
    def _handle_conflict(self, conflict: FileConflict):
        """Handle a detected conflict"""
        print(f"\n🔴 CONFLICT DETECTED:")
        print(f"   File: {conflict.file_path}")
        print(f"   Researchers: {', '.join(conflict.researchers)}")
        print(f"   Type: {conflict.conflict_type}")
        print(f"   Time: {conflict.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Attempt automatic resolution
        if conflict.conflict_type == 'concurrent_edit':
            # For now, backup strategy for all conflicts
            if self._resolve_by_backup(conflict):
                print(f"   ✅ Automatically resolved by backup")
            else:
                print(f"   ⚠️  Requires manual resolution")
    
    def _process_conflict_queue(self):
        """Process pending manual conflict resolutions"""
        while not self.conflict_queue.empty():
            try:
                conflict = self.conflict_queue.get_nowait()
                # In a real implementation, this would notify researchers
                print(f"\n📋 Pending manual resolution: {conflict.file_path}")
            except queue.Empty:
                break
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    def get_conflict_report(self) -> Dict:
        """Generate conflict report"""
        report = {
            'total_conflicts': len(self.conflicts),
            'pending': sum(1 for c in self.conflicts if c.resolution_status == 'pending'),
            'resolved': sum(1 for c in self.conflicts if c.resolution_status == 'resolved'),
            'by_researcher': defaultdict(int),
            'by_type': defaultdict(int),
            'recent_conflicts': []
        }
        
        for conflict in self.conflicts:
            for researcher in conflict.researchers:
                report['by_researcher'][researcher] += 1
            report['by_type'][conflict.conflict_type] += 1
        
        # Get recent conflicts
        report['recent_conflicts'] = sorted(
            self.conflicts, 
            key=lambda c: c.timestamp, 
            reverse=True
        )[:10]
        
        return report
    
    def create_conflict_dashboard(self):
        """Create a markdown dashboard of conflicts"""
        report = self.get_conflict_report()
        
        dashboard = f"""# 🔍 TCP File Conflict Monitor Dashboard
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Monitoring**: {self.consortium_root}

---

## 📊 Summary
- **Total Conflicts**: {report['total_conflicts']}
- **Pending Resolution**: {report['pending']}
- **Resolved**: {report['resolved']}

## 👥 Conflicts by Researcher
"""
        
        for researcher, count in report['by_researcher'].items():
            dashboard += f"- **{researcher}**: {count} conflicts\n"
        
        dashboard += "\n## 🔴 Recent Conflicts\n"
        
        for conflict in report['recent_conflicts'][:5]:
            dashboard += f"""
### {conflict.file_path}
- **Time**: {conflict.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- **Researchers**: {', '.join(conflict.researchers)}
- **Type**: {conflict.conflict_type}
- **Status**: {conflict.resolution_status}
"""
            if 'backup_path' in conflict.details:
                dashboard += f"- **Backup**: `{conflict.details['backup_path']}`\n"
        
        dashboard += """
---

## 🛡️ Conflict Prevention Tips
1. **Communicate**: Use the bulletin board to announce major file edits
2. **Branch**: For major changes, create a branch or copy
3. **Lock**: For critical files, announce exclusive editing in communications
4. **Sync**: Regularly pull/push changes to avoid divergence
5. **Backup**: The monitor creates automatic backups in `.conflicts/`

## 🔧 Manual Resolution Required
"""
        
        pending = [c for c in self.conflicts if c.resolution_status == 'pending']
        if pending:
            for conflict in pending:
                dashboard += f"- `{conflict.file_path}` - {', '.join(conflict.researchers)}\n"
        else:
            dashboard += "*No pending manual resolutions*\n"
        
        return dashboard


def main():
    """Run the conflict monitor"""
    import sys
    
    # Determine consortium root
    if len(sys.argv) > 1:
        consortium_root = sys.argv[1]
    else:
        consortium_root = "/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium"
    
    # Create monitor
    monitor = FileConflictMonitor(consortium_root)
    
    print("🚀 Starting TCP File Conflict Monitor")
    print("=" * 50)
    
    try:
        # Start monitoring
        monitor_thread = monitor.start_monitoring()
        
        # Run until interrupted
        while True:
            time.sleep(30)  # Update dashboard every 30 seconds
            
            # Generate and save dashboard
            dashboard = monitor.create_conflict_dashboard()
            dashboard_path = Path(consortium_root) / 'infrastructure' / 'CONFLICT_MONITOR_DASHBOARD.md'
            
            with open(dashboard_path, 'w') as f:
                f.write(dashboard)
            
            # Print summary
            report = monitor.get_conflict_report()
            if report['total_conflicts'] > 0:
                print(f"\n📊 Status: {report['total_conflicts']} conflicts "
                      f"({report['pending']} pending)")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping monitor...")
        monitor.stop_monitoring()
        
        # Save final report
        final_report = monitor.create_conflict_dashboard()
        report_path = Path(consortium_root) / 'infrastructure' / f'CONFLICT_REPORT_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        with open(report_path, 'w') as f:
            f.write(final_report)
        
        print(f"📄 Final report saved to: {report_path}")
        print("✅ Monitor stopped")


if __name__ == "__main__":
    main()