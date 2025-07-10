#!/usr/bin/env python3
"""
TCP Visual Monitor - Real-time visualization of command discovery
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from collections import defaultdict, deque
import curses


class TCPVisualMonitor:
    def __init__(
        self,
        remote_host="root@167.99.149.241",
        key_path="/Users/sam/.ssh/tcp_deployment_key",
    ):
        self.remote_host = remote_host
        self.key_path = key_path
        self.data_dir = "/opt/tcp-knowledge-system/data"
        self.command_history = deque(maxlen=20)
        self.risk_counts = defaultdict(int)
        self.discovery_rate = deque(maxlen=60)  # 1 minute of data

    def get_tcp_stats(self):
        """Get current TCP statistics"""
        cmd = f"ssh -i {self.key_path} {self.remote_host} 'cat {self.data_dir}/discovered_commands.json'"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "total": len(data.get("commands", [])),
                    "commands": set(data.get("commands", [])),
                    "last_updated": data.get("last_updated", ""),
                }
        except:
            pass
        return {"total": 0, "commands": set(), "last_updated": ""}

    def get_system_count(self):
        """Get total system commands"""
        cmd = f"ssh -i {self.key_path} {self.remote_host} 'compgen -c | sort | uniq | wc -l'"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return 0

    def get_latest_analyses(self, limit=5):
        """Get latest analyzed commands"""
        cmd = f"ssh -i {self.key_path} {self.remote_host} 'ls -t {self.data_dir}/*_analysis.json | head -{limit}'"
        analyses = []
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                for filepath in result.stdout.strip().split("\n"):
                    if filepath:
                        cmd_name = os.path.basename(filepath).replace(
                            "_analysis.json", ""
                        )
                        # Get analysis
                        cmd2 = f"ssh -i {self.key_path} {self.remote_host} 'cat {filepath}'"
                        result2 = subprocess.run(
                            cmd2, shell=True, capture_output=True, text=True
                        )
                        if result2.returncode == 0:
                            data = json.loads(result2.stdout)
                            risk = self.extract_risk(data.get("analysis", ""))
                            analyses.append(
                                {
                                    "command": cmd_name,
                                    "risk": risk,
                                    "timestamp": data.get("timestamp", ""),
                                }
                            )
        except:
            pass
        return analyses

    def extract_risk(self, analysis_text):
        """Extract risk level from analysis"""
        text = analysis_text.upper()
        for level in ["CRITICAL", "HIGH_RISK", "MEDIUM_RISK", "LOW_RISK", "SAFE"]:
            if level in text:
                return level
        return "UNKNOWN"

    def draw_interface(self, stdscr):
        """Draw the monitoring interface"""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)  # Non-blocking input

        # Color pairs
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        last_total = 0
        last_check = time.time()

        while True:
            try:
                # Get current stats
                stats = self.get_tcp_stats()
                system_total = self.get_system_count()
                current_total = stats["total"]

                # Calculate rate
                current_time = time.time()
                if current_time - last_check >= 1:
                    rate = current_total - last_total
                    self.discovery_rate.append(rate)
                    last_total = current_total
                    last_check = current_time

                # Clear screen
                stdscr.clear()
                height, width = stdscr.getmaxyx()

                # Header
                header = "🔍 TCP Knowledge Growth - Live Monitor"
                stdscr.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD)
                stdscr.addstr(1, 0, "=" * width)

                # Stats panel
                row = 3
                stdscr.addstr(row, 2, "📊 System Statistics", curses.A_BOLD)
                row += 1
                stdscr.addstr(row, 4, f"Total Commands: {system_total}")
                row += 1
                stdscr.addstr(
                    row, 4, f"Analyzed: {current_total} ", curses.color_pair(1)
                )
                stdscr.addstr(
                    f"({(current_total/system_total*100):.1f}%)"
                    if system_total > 0
                    else ""
                )
                row += 1
                stdscr.addstr(row, 4, f"Remaining: {system_total - current_total}")

                # Progress bar
                row += 2
                if system_total > 0:
                    progress = current_total / system_total
                    bar_width = width - 10
                    filled = int(bar_width * progress)
                    bar = "█" * filled + "░" * (bar_width - filled)
                    stdscr.addstr(row, 4, f"[{bar}]", curses.color_pair(1))

                # Discovery rate
                row += 2
                avg_rate = (
                    sum(self.discovery_rate) / len(self.discovery_rate)
                    if self.discovery_rate
                    else 0
                )
                stdscr.addstr(row, 2, "⚡ Discovery Rate", curses.A_BOLD)
                row += 1
                stdscr.addstr(
                    row,
                    4,
                    f"Current: {self.discovery_rate[-1] if self.discovery_rate else 0} cmd/s",
                )
                row += 1
                stdscr.addstr(row, 4, f"Average: {avg_rate:.1f} cmd/s")
                if avg_rate > 0 and system_total > current_total:
                    eta = (system_total - current_total) / avg_rate
                    row += 1
                    stdscr.addstr(row, 4, f"ETA: {eta/60:.1f} minutes")

                # Recent discoveries
                row += 2
                stdscr.addstr(row, 2, "🆕 Recent Discoveries", curses.A_BOLD)
                row += 1

                analyses = self.get_latest_analyses(8)
                for analysis in analyses:
                    if row < height - 5:
                        risk = analysis["risk"]
                        color = 1  # Green
                        if risk == "CRITICAL":
                            color = 3  # Red
                        elif risk == "HIGH_RISK":
                            color = 2  # Yellow
                        elif risk == "MEDIUM_RISK":
                            color = 5  # Magenta

                        cmd_str = f"{analysis['command']:<20}"
                        risk_str = f"[{risk}]"

                        stdscr.addstr(row, 4, cmd_str)
                        stdscr.addstr(row, 25, risk_str, curses.color_pair(color))
                        row += 1

                # Footer
                footer = "Press 'q' to quit | Updates every second"
                stdscr.addstr(
                    height - 2, (width - len(footer)) // 2, footer, curses.A_DIM
                )

                stdscr.refresh()

                # Check for quit
                key = stdscr.getch()
                if key == ord("q"):
                    break

                time.sleep(1)

            except KeyboardInterrupt:
                break
            except Exception as e:
                stdscr.addstr(
                    height - 3, 2, f"Error: {str(e)[:width-4]}", curses.color_pair(3)
                )
                stdscr.refresh()
                time.sleep(2)

    def run(self):
        """Run the visual monitor"""
        try:
            curses.wrapper(self.draw_interface)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")


if __name__ == "__main__":
    print("Starting TCP Visual Monitor...")
    print("This will display a live dashboard of command discovery.")
    print("Press any key to continue...")
    input()

    monitor = TCPVisualMonitor()
    monitor.run()
