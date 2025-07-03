#!/usr/bin/env python3
"""
TCP Branch Synchronization Health Dashboard

Monitors and reports on the health of branch synchronization between
main and linguistic-evolution branches.
"""

import subprocess
import json
import datetime
import re
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SyncMetrics:
    """Synchronization health metrics"""
    commits_behind: int
    last_sync_age: datetime.timedelta
    conflict_rate: float
    sync_frequency: float
    branch_divergence: int
    health_score: int


class TCPSyncHealthMonitor:
    """Monitor TCP branch synchronization health"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.log_file = os.path.join(repo_path, ".tcp_sync_log")
        self.main_branch = "main"
        self.experimental_branch = "linguistic-evolution"
    
    def get_commits_behind(self, base_branch: str, target_branch: str) -> int:
        """Get number of commits target branch is behind base branch"""
        try:
            result = subprocess.run([
                "git", "rev-list", "--count", f"{target_branch}..{base_branch}"
            ], capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                return int(result.stdout.strip())
            else:
                return -1
        except Exception:
            return -1
    
    def get_last_sync_age(self) -> datetime.timedelta:
        """Get time since last synchronization"""
        try:
            if not os.path.exists(self.log_file):
                return datetime.timedelta(days=365)  # Very old if no log
            
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                return datetime.timedelta(days=365)
            
            # Parse the last line for timestamp
            last_line = lines[-1].strip()
            if last_line:
                # Expected format: timestamp,main_commit,linguistic_commit,sync_type,conflicts,status
                parts = last_line.split(',')
                if len(parts) >= 1:
                    timestamp_str = parts[0]
                    last_sync = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    return datetime.datetime.now(datetime.timezone.utc) - last_sync
            
            return datetime.timedelta(days=365)
        except Exception:
            return datetime.timedelta(days=365)
    
    def calculate_conflict_rate(self) -> float:
        """Calculate percentage of syncs that had conflicts"""
        try:
            if not os.path.exists(self.log_file):
                return 0.0
            
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                return 0.0
            
            total_syncs = len(lines)
            conflicts = 0
            
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 5:
                    conflict_count = parts[4]
                    if conflict_count.isdigit() and int(conflict_count) > 0:
                        conflicts += 1
            
            return (conflicts / total_syncs) * 100.0 if total_syncs > 0 else 0.0
        except Exception:
            return 0.0
    
    def calculate_sync_frequency(self) -> float:
        """Calculate average days between syncs"""
        try:
            if not os.path.exists(self.log_file):
                return 0.0
            
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
            
            if len(lines) < 2:
                return 0.0
            
            timestamps = []
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 1:
                    try:
                        timestamp_str = parts[0]
                        timestamp = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        timestamps.append(timestamp)
                    except ValueError:
                        continue
            
            if len(timestamps) < 2:
                return 0.0
            
            # Calculate average interval
            total_interval = datetime.timedelta(0)
            for i in range(1, len(timestamps)):
                total_interval += timestamps[i] - timestamps[i-1]
            
            avg_interval = total_interval / (len(timestamps) - 1)
            return avg_interval.total_seconds() / 86400  # Convert to days
        except Exception:
            return 0.0
    
    def measure_branch_divergence(self) -> int:
        """Measure overall divergence between branches"""
        try:
            # Count commits unique to each branch
            main_unique = self.get_commits_behind(self.experimental_branch, self.main_branch)
            exp_unique = self.get_commits_behind(self.main_branch, self.experimental_branch)
            
            if main_unique == -1 or exp_unique == -1:
                return -1
            
            return main_unique + exp_unique
        except Exception:
            return -1
    
    def get_git_status(self) -> Dict[str, bool]:
        """Get current git repository status"""
        try:
            result = subprocess.run([
                "git", "status", "--porcelain"
            ], capture_output=True, text=True, cwd=self.repo_path)
            
            has_uncommitted = len(result.stdout.strip()) > 0
            
            # Check if branches exist
            main_exists = subprocess.run([
                "git", "rev-parse", "--verify", self.main_branch
            ], capture_output=True, cwd=self.repo_path).returncode == 0
            
            exp_exists = subprocess.run([
                "git", "rev-parse", "--verify", self.experimental_branch
            ], capture_output=True, cwd=self.repo_path).returncode == 0
            
            return {
                "has_uncommitted": has_uncommitted,
                "main_exists": main_exists,
                "experimental_exists": exp_exists
            }
        except Exception:
            return {
                "has_uncommitted": True,
                "main_exists": False,
                "experimental_exists": False
            }
    
    def calculate_health_score(self, metrics: Dict) -> int:
        """Calculate overall health score (0-100)"""
        score = 100
        
        # Penalize being behind
        commits_behind = metrics.get('commits_behind', 0)
        if commits_behind > 0:
            score -= min(commits_behind * 5, 30)  # Max 30 point penalty
        
        # Penalize old syncs
        last_sync_days = metrics.get('last_sync_age', datetime.timedelta(days=0)).days
        if last_sync_days > 7:
            score -= min(last_sync_days * 2, 40)  # Max 40 point penalty
        
        # Penalize high conflict rate
        conflict_rate = metrics.get('conflict_rate', 0)
        if conflict_rate > 10:
            score -= min(conflict_rate * 2, 20)  # Max 20 point penalty
        
        # Penalize high divergence
        divergence = metrics.get('branch_divergence', 0)
        if divergence > 10:
            score -= min(divergence, 20)  # Max 20 point penalty
        
        return max(0, score)
    
    def analyze_sync_health(self) -> SyncMetrics:
        """Generate synchronization health report"""
        
        # Calculate sync metrics
        commits_behind = self.get_commits_behind(self.main_branch, self.experimental_branch)
        last_sync_age = self.get_last_sync_age()
        conflict_rate = self.calculate_conflict_rate()
        sync_frequency = self.calculate_sync_frequency()
        branch_divergence = self.measure_branch_divergence()
        
        metrics = {
            "commits_behind": commits_behind,
            "last_sync_age": last_sync_age,
            "conflict_rate": conflict_rate,
            "sync_frequency": sync_frequency,
            "branch_divergence": branch_divergence
        }
        
        # Generate health score (0-100)
        health_score = self.calculate_health_score(metrics)
        
        return SyncMetrics(
            commits_behind=commits_behind,
            last_sync_age=last_sync_age,
            conflict_rate=conflict_rate,
            sync_frequency=sync_frequency,
            branch_divergence=branch_divergence,
            health_score=health_score
        )
    
    def print_health_report(self) -> None:
        """Print comprehensive health report"""
        print("🏥 TCP Branch Synchronization Health Dashboard")
        print("=" * 50)
        
        # Get git status
        git_status = self.get_git_status()
        
        # Check if we're in a git repo with the right branches
        if not git_status["main_exists"] or not git_status["experimental_exists"]:
            print("❌ Error: Required branches not found")
            print(f"   Main branch ({self.main_branch}): {'✅' if git_status['main_exists'] else '❌'}")
            print(f"   Experimental branch ({self.experimental_branch}): {'✅' if git_status['experimental_exists'] else '❌'}")
            return
        
        # Get metrics
        metrics = self.analyze_sync_health()
        
        # Print health score
        print(f"📊 Overall Health Score: {metrics.health_score}/100")
        
        if metrics.health_score >= 90:
            print("🌟 Excellent sync health")
        elif metrics.health_score >= 70:
            print("✅ Good sync health")
        elif metrics.health_score >= 50:
            print("⚠️  Moderate sync health - improvements recommended")
        else:
            print("🔴 Poor sync health - immediate attention needed")
        
        print()
        
        # Detailed metrics
        print("📋 Detailed Metrics:")
        print(f"   📈 Commits behind main: {metrics.commits_behind}")
        print(f"   ⏰ Last sync: {self._format_timedelta(metrics.last_sync_age)} ago")
        print(f"   ⚡ Conflict rate: {metrics.conflict_rate:.1f}%")
        print(f"   🔄 Sync frequency: {metrics.sync_frequency:.1f} days")
        print(f"   📊 Branch divergence: {metrics.branch_divergence} commits")
        
        print()
        
        # Repository status
        print("🔍 Repository Status:")
        print(f"   📁 Uncommitted changes: {'❌ Yes' if git_status['has_uncommitted'] else '✅ Clean'}")
        print(f"   🌿 Main branch: {'✅ Available' if git_status['main_exists'] else '❌ Missing'}")
        print(f"   🧬 Experimental branch: {'✅ Available' if git_status['experimental_exists'] else '❌ Missing'}")
        
        print()
        
        # Recommendations
        print("💡 Recommendations:")
        if metrics.commits_behind > 5:
            print("   🔄 Run synchronization soon - experimental branch is getting behind")
        if metrics.last_sync_age.days > 7:
            print("   ⏰ Consider more frequent synchronization")
        if metrics.conflict_rate > 15:
            print("   🔧 Review merge strategies - high conflict rate detected")
        if git_status["has_uncommitted"]:
            print("   💾 Commit or stash changes before synchronization")
        
        if metrics.health_score >= 90:
            print("   🎯 Maintain current synchronization practices")
        
        print()
        
        # Quick actions
        print("🚀 Quick Actions:")
        print("   ./tcp_branch_sync.sh auto-merge    # Run automatic sync")
        print("   ./pre_sync_validation.sh          # Check sync readiness")
        print("   git status                         # Check current state")
        
    def _format_timedelta(self, td: datetime.timedelta) -> str:
        """Format timedelta for human reading"""
        if td.days > 0:
            return f"{td.days} day{'s' if td.days != 1 else ''}"
        elif td.seconds > 3600:
            hours = td.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''}"
        elif td.seconds > 60:
            minutes = td.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return "< 1 minute"
    
    def export_metrics_json(self, filename: str = "sync_health_metrics.json") -> None:
        """Export metrics to JSON file"""
        metrics = self.analyze_sync_health()
        git_status = self.get_git_status()
        
        data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "health_score": metrics.health_score,
            "commits_behind": metrics.commits_behind,
            "last_sync_age_days": metrics.last_sync_age.days,
            "conflict_rate": metrics.conflict_rate,
            "sync_frequency_days": metrics.sync_frequency,
            "branch_divergence": metrics.branch_divergence,
            "git_status": git_status
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📄 Metrics exported to {filename}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TCP Branch Synchronization Health Dashboard")
    parser.add_argument("--json", help="Export metrics to JSON file")
    parser.add_argument("--repo", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    monitor = TCPSyncHealthMonitor(args.repo)
    
    # Print health report
    monitor.print_health_report()
    
    # Export JSON if requested
    if args.json:
        monitor.export_metrics_json(args.json)


if __name__ == "__main__":
    main()