#!/usr/bin/env python3
"""
TCP Progress Monitor - Real-time tracking for consortium researchers
Provides comprehensive visibility into command analysis progress, quality metrics, and processing rates
"""

import os
import json
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import threading
import sys


@dataclass
class ProgressMetrics:
    """Progress tracking metrics"""

    total_commands: int = 0
    analyzed_commands: int = 0
    reprocessed_commands: int = 0
    failed_commands: int = 0
    processing_rate: float = 0.0  # commands per minute
    accuracy_rate: float = 0.0  # percentage
    eta_hours: float = 0.0
    current_stage: str = "idle"


@dataclass
class QualityMetrics:
    """Analysis quality metrics"""

    risk_distribution: Dict[str, int]
    rule_overrides: int = 0
    llm_classifications: int = 0
    man_page_coverage: float = 0.0
    dangerous_commands_correct: int = 0
    safe_commands_correct: int = 0


class TCPProgressMonitor:
    def __init__(self, data_dir="data", output_dir="progress_reports"):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.progress_file = os.path.join(output_dir, "tcp_progress.json")
        self.log_file = os.path.join(output_dir, "progress_log.txt")

        os.makedirs(output_dir, exist_ok=True)

        # Known dangerous commands for accuracy tracking
        self.dangerous_commands = {
            "dd",
            "fdisk",
            "mkfs",
            "parted",
            "shred",
            "wipefs",
            "rm",
            "sudo",
            "chmod",
            "chown",
            "kill",
            "systemctl",
            "iptables",
            "nmap",
            "tcpdump",
            "wireshark",
            "aircrack-ng",
            "hydra",
            "john",
        }

        # Safe commands for accuracy tracking
        self.safe_commands = {
            "ls",
            "cat",
            "echo",
            "pwd",
            "date",
            "whoami",
            "id",
            "uptime",
            "which",
            "whereis",
            "man",
            "help",
            "info",
            "head",
            "tail",
        }

        self.start_time = time.time()
        self.last_update = time.time()
        self.monitoring = False

    def get_system_command_count(self) -> int:
        """Get total number of commands available on system"""
        try:
            result = subprocess.run(
                ["bash", "-c", "compgen -c | sort | uniq | wc -l"],
                capture_output=True,
                text=True,
            )
            return int(result.stdout.strip()) if result.returncode == 0 else 3865
        except:
            return 3865  # Fallback estimate

    def scan_analysis_files(self) -> Tuple[List[str], Dict[str, Dict]]:
        """Scan for existing analysis files and load metadata"""
        analysis_files = []
        command_data = {}

        if not os.path.exists(self.data_dir):
            return analysis_files, command_data

        for filename in os.listdir(self.data_dir):
            if filename.endswith("_analysis.json"):
                command = filename.replace("_analysis.json", "")
                analysis_files.append(command)

                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                        command_data[command] = {
                            "analysis": data.get("analysis", ""),
                            "timestamp": data.get("timestamp", ""),
                            "method": data.get("method", "legacy"),
                            "risk": self._extract_risk_from_analysis(
                                data.get("analysis", "")
                            ),
                        }
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

        return analysis_files, command_data

    def _extract_risk_from_analysis(self, analysis: str) -> str:
        """Extract risk level from analysis text"""
        if not analysis:
            return "UNKNOWN"

        analysis_upper = analysis.upper()
        for risk in ["CRITICAL", "HIGH_RISK", "MEDIUM_RISK", "LOW_RISK", "SAFE"]:
            if risk.replace("_", " ") in analysis_upper or risk in analysis_upper:
                return risk
        return "UNKNOWN"

    def calculate_metrics(self) -> Tuple[ProgressMetrics, QualityMetrics]:
        """Calculate comprehensive progress and quality metrics"""
        analyzed_commands, command_data = self.scan_analysis_files()
        total_commands = self.get_system_command_count()

        # Progress metrics
        progress = ProgressMetrics()
        progress.total_commands = total_commands
        progress.analyzed_commands = len(analyzed_commands)

        # Calculate processing rate
        elapsed_hours = (time.time() - self.start_time) / 3600
        if elapsed_hours > 0:
            progress.processing_rate = len(analyzed_commands) / (
                elapsed_hours * 60
            )  # per minute

        remaining = total_commands - len(analyzed_commands)
        if progress.processing_rate > 0:
            progress.eta_hours = remaining / (progress.processing_rate * 60)

        # Quality metrics
        quality = QualityMetrics(risk_distribution=defaultdict(int))

        dangerous_correct = 0
        safe_correct = 0
        man_page_count = 0

        for command, data in command_data.items():
            risk = data["risk"]
            quality.risk_distribution[risk] += 1

            # Check accuracy for known command types
            if command in self.dangerous_commands:
                if risk in ["CRITICAL", "HIGH_RISK"]:
                    dangerous_correct += 1
            elif command in self.safe_commands:
                if risk in ["SAFE", "LOW_RISK"]:
                    safe_correct += 1

            # Count LLM vs rule-based
            if data.get("method") == "rule_override":
                quality.rule_overrides += 1
            else:
                quality.llm_classifications += 1

            # Check man page availability (rough estimate)
            if len(data.get("analysis", "")) > 100:  # Longer analysis suggests man page
                man_page_count += 1

        quality.dangerous_commands_correct = dangerous_correct
        quality.safe_commands_correct = safe_correct
        quality.man_page_coverage = (
            (man_page_count / len(analyzed_commands) * 100) if analyzed_commands else 0
        )

        # Calculate accuracy rate
        total_known = len(
            [
                c
                for c in analyzed_commands
                if c in self.dangerous_commands or c in self.safe_commands
            ]
        )
        if total_known > 0:
            progress.accuracy_rate = (
                (dangerous_correct + safe_correct) / total_known
            ) * 100

        return progress, quality

    def generate_progress_report(self) -> Dict:
        """Generate comprehensive progress report"""
        progress, quality = self.calculate_metrics()

        report = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_duration_hours": (time.time() - self.start_time) / 3600,
            "progress": {
                "total_commands": progress.total_commands,
                "analyzed_commands": progress.analyzed_commands,
                "completion_percentage": (
                    progress.analyzed_commands / progress.total_commands
                )
                * 100,
                "remaining_commands": progress.total_commands
                - progress.analyzed_commands,
                "processing_rate_per_minute": progress.processing_rate,
                "estimated_completion_hours": progress.eta_hours,
                "estimated_completion_time": (
                    datetime.now() + timedelta(hours=progress.eta_hours)
                ).isoformat()
                if progress.eta_hours < 100
                else "TBD",
            },
            "quality": {
                "accuracy_rate_percentage": progress.accuracy_rate,
                "risk_distribution": dict(quality.risk_distribution),
                "rule_overrides": quality.rule_overrides,
                "llm_classifications": quality.llm_classifications,
                "man_page_coverage_percentage": quality.man_page_coverage,
                "dangerous_commands_correct": quality.dangerous_commands_correct,
                "safe_commands_correct": quality.safe_commands_correct,
            },
            "performance": {
                "average_processing_time_seconds": 60 / progress.processing_rate
                if progress.processing_rate > 0
                else 0,
                "commands_per_hour": progress.processing_rate * 60,
                "daily_processing_capacity": progress.processing_rate * 60 * 24,
            },
        }

        return report

    def save_progress_report(self, report: Dict):
        """Save progress report to file"""
        with open(self.progress_file, "w") as f:
            json.dump(report, f, indent=2)

    def log_progress(self, message: str):
        """Log progress message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        with open(self.log_file, "a") as f:
            f.write(log_entry)

        print(log_entry.strip())

    def display_live_dashboard(self):
        """Display live progress dashboard"""
        os.system("clear" if os.name == "posix" else "cls")

        report = self.generate_progress_report()
        progress = report["progress"]
        quality = report["quality"]
        performance = report["performance"]

        print("🔬 TCP CONSORTIUM PROGRESS DASHBOARD")
        print("=" * 70)
        print(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(
            f"⏱️  Monitoring Duration: {report['monitoring_duration_hours']:.1f} hours"
        )

        # Progress Section
        print("\n📊 ANALYSIS PROGRESS")
        print("-" * 30)
        completion = progress["completion_percentage"]
        bar_length = 40
        filled = int(bar_length * completion / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"Progress: [{bar}] {completion:.1f}%")
        print(
            f"Analyzed: {progress['analyzed_commands']:,} / {progress['total_commands']:,} commands"
        )
        print(f"Remaining: {progress['remaining_commands']:,} commands")

        if progress["estimated_completion_hours"] < 100:
            print(f"ETA: {progress['estimated_completion_hours']:.1f} hours")
            print(f"Completion: {progress['estimated_completion_time'][:19]}")
        else:
            print("ETA: TBD (low processing rate)")

        # Performance Section
        print("\n⚡ PERFORMANCE METRICS")
        print("-" * 30)
        print(
            f"Processing Rate: {progress['processing_rate_per_minute']:.1f} commands/minute"
        )
        print(f"Hourly Capacity: {performance['commands_per_hour']:.0f} commands/hour")
        print(
            f"Avg Time/Command: {performance['average_processing_time_seconds']:.1f} seconds"
        )

        # Quality Section
        print("\n🎯 QUALITY METRICS")
        print("-" * 30)
        print(f"Accuracy Rate: {quality['accuracy_rate_percentage']:.1f}%")
        print(f"Man Page Coverage: {quality['man_page_coverage_percentage']:.1f}%")
        print(f"Rule Overrides: {quality['rule_overrides']}")
        print(f"LLM Classifications: {quality['llm_classifications']}")

        # Risk Distribution
        print("\n⚠️  RISK DISTRIBUTION")
        print("-" * 30)
        for risk, count in sorted(quality["risk_distribution"].items()):
            if count > 0:
                percentage = (count / progress["analyzed_commands"]) * 100
                print(f"{risk:<15} {count:>4} ({percentage:>5.1f}%)")

        # Accuracy Breakdown
        print("\n✅ ACCURACY BREAKDOWN")
        print("-" * 30)
        print(f"Dangerous Commands Correct: {quality['dangerous_commands_correct']}")
        print(f"Safe Commands Correct: {quality['safe_commands_correct']}")

        print(f"\n🔄 Press Ctrl+C to stop monitoring")

    def start_monitoring(self, update_interval: int = 30):
        """Start real-time monitoring with specified update interval"""
        self.monitoring = True
        self.log_progress("TCP Progress Monitor started")

        try:
            while self.monitoring:
                self.display_live_dashboard()

                # Save progress report
                report = self.generate_progress_report()
                self.save_progress_report(report)

                time.sleep(update_interval)

        except KeyboardInterrupt:
            self.monitoring = False
            self.log_progress("TCP Progress Monitor stopped by user")
            print("\n\n📊 Final Report Saved to:", self.progress_file)

    def generate_consortium_report(self) -> str:
        """Generate detailed report for consortium researchers"""
        report = self.generate_progress_report()

        consortium_report = f"""
# TCP Knowledge Base Progress Report
**Generated**: {report['timestamp']}
**Monitoring Duration**: {report['monitoring_duration_hours']:.1f} hours

## Executive Summary
- **Completion**: {report['progress']['completion_percentage']:.1f}% ({report['progress']['analyzed_commands']:,}/{report['progress']['total_commands']:,} commands)
- **Quality**: {report['quality']['accuracy_rate_percentage']:.1f}% accuracy on known command classifications
- **Performance**: {report['performance']['commands_per_hour']:.0f} commands/hour processing capacity

## Progress Metrics
| Metric | Value |
|--------|-------|
| Total Commands | {report['progress']['total_commands']:,} |
| Analyzed Commands | {report['progress']['analyzed_commands']:,} |
| Remaining Commands | {report['progress']['remaining_commands']:,} |
| Processing Rate | {report['progress']['processing_rate_per_minute']:.1f}/min |
| ETA | {report['progress']['estimated_completion_hours']:.1f} hours |

## Quality Assessment
| Category | Count | Percentage |
|----------|-------|------------|"""

        for risk, count in sorted(report["quality"]["risk_distribution"].items()):
            if count > 0:
                pct = (count / report["progress"]["analyzed_commands"]) * 100
                consortium_report += f"\n| {risk} | {count} | {pct:.1f}% |"

        consortium_report += f"""

## Research Implications
- **Rule-based Overrides**: {report['quality']['rule_overrides']} commands
- **LLM Classifications**: {report['quality']['llm_classifications']} commands  
- **Man Page Coverage**: {report['quality']['man_page_coverage_percentage']:.1f}%
- **Accuracy on Dangerous Commands**: {report['quality']['dangerous_commands_correct']} correct
- **Accuracy on Safe Commands**: {report['quality']['safe_commands_correct']} correct

## Recommendations
1. **High Priority**: Focus on remaining dangerous commands with rule-based overrides
2. **Processing Optimization**: Current rate of {report['performance']['commands_per_hour']:.0f}/hour suggests {report['progress']['estimated_completion_hours']:.1f} hour completion time
3. **Quality Validation**: {report['quality']['accuracy_rate_percentage']:.1f}% accuracy indicates {"excellent" if report['quality']['accuracy_rate_percentage'] > 90 else "good" if report['quality']['accuracy_rate_percentage'] > 80 else "needs improvement"} classification performance

---
*Generated by TCP Progress Monitor for Consortium Research Team*
"""

        # Save consortium report
        consortium_file = os.path.join(
            self.output_dir,
            f"consortium_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        )
        with open(consortium_file, "w") as f:
            f.write(consortium_report)

        return consortium_file

    def quick_status(self):
        """Quick status check for command line"""
        progress, quality = self.calculate_metrics()

        print(
            f"🔬 TCP Progress: {progress.analyzed_commands:,}/{progress.total_commands:,} ({(progress.analyzed_commands/progress.total_commands)*100:.1f}%)"
        )
        print(
            f"⚡ Rate: {progress.processing_rate:.1f}/min | ETA: {progress.eta_hours:.1f}h"
        )
        print(
            f"🎯 Accuracy: {progress.accuracy_rate:.1f}% | Overrides: {quality.rule_overrides}"
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="TCP Progress Monitor for Consortium Researchers"
    )
    parser.add_argument(
        "--mode",
        choices=["monitor", "report", "status"],
        default="monitor",
        help="Monitoring mode",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Update interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--data-dir", default="data", help="Directory containing analysis files"
    )
    parser.add_argument(
        "--output-dir", default="progress_reports", help="Output directory for reports"
    )

    args = parser.parse_args()

    monitor = TCPProgressMonitor(args.data_dir, args.output_dir)

    if args.mode == "monitor":
        print("🔬 Starting TCP Progress Monitor for Consortium...")
        print(f"📊 Data Directory: {args.data_dir}")
        print(f"📁 Reports Directory: {args.output_dir}")
        print(f"⏱️  Update Interval: {args.interval} seconds")
        print("-" * 50)
        monitor.start_monitoring(args.interval)

    elif args.mode == "report":
        print("📊 Generating Consortium Report...")
        report_file = monitor.generate_consortium_report()
        print(f"✅ Report saved to: {report_file}")

    elif args.mode == "status":
        monitor.quick_status()


if __name__ == "__main__":
    main()
