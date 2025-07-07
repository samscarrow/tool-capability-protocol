#!/usr/bin/env python3
"""
TCP Conflict Monitor API Examples
Dr. Sam Mitchell - Hardware Security Engineer

Shows how researchers can integrate conflict monitoring into their workflows
"""

import sys
import time
from pathlib import Path

# Add conflict monitor to path
sys.path.append(str(Path(__file__).parent))

from tcp_conflict_monitor import (
    ConflictDatabase, 
    ResearcherCoordinator,
    FileActivity,
    create_enhanced_monitor
)

def example_check_before_editing():
    """Example: Check if file is safe to edit before starting work"""
    
    print("=== Example 1: Pre-edit Safety Check ===")
    
    # Initialize components
    db = ConflictDatabase()
    coordinator = ResearcherCoordinator(db)
    
    # Register research session
    researcher_name = "Sam Mitchell"
    coordinator.register_session(researcher_name)
    
    # Check file before editing
    file_to_edit = "../yuki-tanaka/tcp_performance_profiler.py"
    
    recommendations = coordinator.get_file_recommendations(researcher_name, file_to_edit)
    
    if recommendations['safe_to_edit']:
        print(f"✓ Safe to edit {file_to_edit}")
        print(f"  Reason: {recommendations['reason']}")
        print(f"  Recommendations: {', '.join(recommendations['recommendations'])}")
        
        # Lock file for exclusive editing
        db.lock_file(file_to_edit, researcher_name, duration=3600)  # 1 hour
        print(f"✓ File locked for editing")
    else:
        print(f"❌ Not safe to edit {file_to_edit}")
        print(f"  Reason: {recommendations['reason']}")
        print(f"  Alternatives: {', '.join(recommendations['alternatives'])}")
    
    # Cleanup
    coordinator.unregister_session(researcher_name)

def example_programmatic_activity_tracking():
    """Example: Programmatically track file activities"""
    
    print("\n=== Example 2: Programmatic Activity Tracking ===")
    
    db = ConflictDatabase()
    
    # Record a file modification
    activity = FileActivity(
        file_path="../elena-vasquez/statistical_validation_framework.py",
        researcher="Elena Vasquez",
        action="modified",
        timestamp=datetime.now(),
        content_hash="abc123def456",
        file_size=4096,
        backup_path=None
    )
    
    db.record_activity(activity)
    print("✓ Activity recorded")
    
    # Check recent activities
    recent = db.get_recent_activities(activity.file_path, hours=1)
    print(f"  Recent activities on file: {len(recent)}")
    for act in recent:
        print(f"    - {act.researcher} {act.action} at {act.timestamp}")

def example_conflict_resolution_api():
    """Example: Get conflict resolution suggestions"""
    
    print("\n=== Example 3: Conflict Resolution API ===")
    
    from tcp_conflict_monitor import ConflictResolver, ConflictEvent, ConflictType
    
    db = ConflictDatabase()
    resolver = ConflictResolver(db)
    
    # Simulate a conflict
    conflict = ConflictEvent(
        conflict_id="example_001",
        conflict_type=ConflictType.SIMULTANEOUS_EDIT,
        file_path="../marcus-chen/distributed_architecture_proposal.md",
        researchers=["Marcus Chen", "Sam Mitchell"],
        timestamp=datetime.now(),
        description="Both researchers editing architecture document"
    )
    
    # Get resolution suggestion
    resolution = resolver.suggest_resolution(conflict)
    
    print(f"Conflict Type: {conflict.conflict_type.value}")
    print(f"Resolution: {resolution['description']}")
    print("Steps:")
    for step in resolution.get('steps', []):
        print(f"  {step}")

def example_collaboration_network():
    """Example: Analyze researcher collaboration patterns"""
    
    print("\n=== Example 4: Collaboration Network Analysis ===")
    
    db = ConflictDatabase()
    coordinator = ResearcherCoordinator(db)
    
    # Get collaboration graph
    collaborations = coordinator.get_collaboration_graph()
    
    if collaborations:
        print("Researcher Collaboration Network:")
        for researcher, collaborators in collaborations.items():
            if collaborators:
                print(f"  {researcher} works with: {', '.join(collaborators)}")
    else:
        print("No collaboration patterns detected yet")

def example_schedule_editing_window():
    """Example: Schedule exclusive editing window"""
    
    print("\n=== Example 5: Schedule Editing Window ===")
    
    db = ConflictDatabase()
    coordinator = ResearcherCoordinator(db)
    
    # Schedule editing window
    success = coordinator.schedule_editing_window(
        researcher="Yuki Tanaka",
        file_path="../convergence-20250704-elena-marcus/hierarchical_aggregation_protocol.py",
        start_time=datetime.now(),
        duration_hours=4
    )
    
    if success:
        print("✓ Editing window scheduled successfully")
        print("  File will be exclusively locked for 4 hours")
    else:
        print("❌ Could not schedule editing window")
        print("  File may already be locked")

def example_api_integration():
    """Example: Integrate with research workflow"""
    
    print("\n=== Example 6: Workflow Integration ===")
    
    class ResearchWorkflow:
        def __init__(self, researcher_name):
            self.researcher = researcher_name
            self.db = ConflictDatabase()
            self.coordinator = ResearcherCoordinator(self.db)
            
        def __enter__(self):
            self.coordinator.register_session(self.researcher)
            print(f"✓ Research session started for {self.researcher}")
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.coordinator.unregister_session(self.researcher)
            print(f"✓ Research session ended for {self.researcher}")
            
        def edit_file(self, file_path):
            """Safely edit a file with conflict checking"""
            
            # Check if safe to edit
            recommendations = self.coordinator.get_file_recommendations(
                self.researcher, file_path
            )
            
            if not recommendations['safe_to_edit']:
                raise RuntimeError(f"Cannot edit {file_path}: {recommendations['reason']}")
            
            # Lock file
            self.db.lock_file(file_path, self.researcher)
            print(f"✓ Locked {file_path} for editing")
            
            # Simulate editing
            print(f"  Editing {file_path}...")
            time.sleep(1)
            
            # Record activity
            activity = FileActivity(
                file_path=file_path,
                researcher=self.researcher,
                action="modified",
                timestamp=datetime.now(),
                content_hash="xyz789",
                file_size=5000,
                backup_path=None
            )
            self.db.record_activity(activity)
            
            # Unlock file
            self.db.unlock_file(file_path)
            print(f"✓ Unlocked {file_path}")
    
    # Use the workflow
    with ResearchWorkflow("Aria Blackwood") as workflow:
        try:
            workflow.edit_file("../aria-blackwood/tcp_security_research_binary.py")
        except RuntimeError as e:
            print(f"❌ {e}")

def example_realtime_monitoring():
    """Example: Real-time monitoring with callbacks"""
    
    print("\n=== Example 7: Real-time Monitoring ===")
    
    # This would typically run in a separate thread/process
    print("To enable real-time monitoring, run:")
    print("  python tcp_conflict_monitor.py --root ../..")
    print("")
    print("Or programmatically:")
    print("  from tcp_conflict_monitor import create_enhanced_monitor")
    print("  EnhancedMonitor = create_enhanced_monitor()")
    print("  monitor = EnhancedMonitor('../..')")
    print("  monitor.start_monitoring()  # Runs forever")

# Main demonstration
if __name__ == "__main__":
    from datetime import datetime
    
    print("TCP Conflict Monitor API Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_check_before_editing()
        example_programmatic_activity_tracking()
        example_conflict_resolution_api()
        example_collaboration_network()
        example_schedule_editing_window()
        example_api_integration()
        example_realtime_monitoring()
        
    except Exception as e:
        print(f"\nError in example: {e}")
        print("Make sure the conflict monitor is properly installed")