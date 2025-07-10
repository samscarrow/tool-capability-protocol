#!/usr/bin/env python3
"""
TCP Live Monitor - Real-time command discovery and analysis tracking
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from collections import defaultdict

class TCPLiveMonitor:
    def __init__(self, remote_host="root@167.99.149.241", key_path="/Users/sam/.ssh/tcp_deployment_key"):
        self.remote_host = remote_host
        self.key_path = key_path
        self.data_dir = "/opt/tcp-knowledge-system/data"
        self.initial_commands = set()
        self.command_history = defaultdict(list)
        
    def get_current_commands(self):
        """Get current list of analyzed commands"""
        cmd = f"ssh -i {self.key_path} {self.remote_host} 'cat {self.data_dir}/discovered_commands.json'"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return set(data.get("commands", []))
        except:
            pass
        return set()
    
    def get_system_commands(self):
        """Get all available system commands"""
        cmd = f"ssh -i {self.key_path} {self.remote_host} 'compgen -c | sort | uniq | wc -l'"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return 0
    
    def get_latest_analysis(self, command):
        """Get analysis for a specific command"""
        cmd = f"ssh -i {self.key_path} {self.remote_host} 'cat {self.data_dir}/{command}_analysis.json 2>/dev/null'"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return None
    
    def monitor_changes(self, interval=5):
        """Monitor for new commands being analyzed"""
        print("🔍 TCP Live Monitor - Starting...")
        print("=" * 60)
        
        # Get initial state
        self.initial_commands = self.get_current_commands()
        initial_system = self.get_system_commands()
        
        print(f"📊 Initial State:")
        print(f"   • Analyzed commands: {len(self.initial_commands)}")
        print(f"   • System commands: {initial_system}")
        print(f"\n⏳ Monitoring for changes every {interval} seconds...")
        print("-" * 60)
        
        last_count = len(self.initial_commands)
        
        while True:
            try:
                current_commands = self.get_current_commands()
                system_count = self.get_system_commands()
                current_count = len(current_commands)
                
                # Check for new commands
                new_commands = current_commands - self.initial_commands
                
                if new_commands:
                    print(f"\n🆕 [{datetime.now().strftime('%H:%M:%S')}] New commands analyzed: {len(new_commands)}")
                    
                    # Show details of new commands
                    for cmd in sorted(new_commands)[:10]:  # Show first 10
                        analysis = self.get_latest_analysis(cmd)
                        if analysis:
                            risk = "UNKNOWN"
                            # Extract risk level from analysis
                            analysis_text = analysis.get("analysis", "").upper()
                            for level in ["CRITICAL", "HIGH_RISK", "MEDIUM_RISK", "LOW_RISK", "SAFE"]:
                                if level in analysis_text:
                                    risk = level
                                    break
                            
                            print(f"   • {cmd:<20} [{risk}]")
                            self.command_history[cmd].append({
                                "time": datetime.now().isoformat(),
                                "risk": risk
                            })
                    
                    if len(new_commands) > 10:
                        print(f"   ... and {len(new_commands) - 10} more")
                    
                    self.initial_commands = current_commands
                
                # Show progress bar
                if system_count > 0:
                    progress = (current_count / system_count) * 100
                    bar_length = 40
                    filled = int(bar_length * current_count / system_count)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    
                    sys.stdout.write(f"\r📈 Progress: [{bar}] {current_count}/{system_count} ({progress:.1f}%)")
                    sys.stdout.flush()
                
                # Check for significant changes
                if current_count != last_count:
                    rate = (current_count - last_count) / interval
                    if rate > 0:
                        remaining = system_count - current_count
                        eta_seconds = remaining / rate if rate > 0 else 0
                        eta_minutes = eta_seconds / 60
                        
                        sys.stdout.write(f" | Rate: {rate:.1f} cmd/s | ETA: {eta_minutes:.1f}m")
                        sys.stdout.flush()
                    
                    last_count = current_count
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n\n✋ Monitoring stopped")
                self.show_summary()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                time.sleep(interval)
    
    def show_summary(self):
        """Show summary of monitoring session"""
        print("\n" + "=" * 60)
        print("📊 Monitoring Summary")
        print("=" * 60)
        
        total_new = len(self.command_history)
        print(f"🆕 Total new commands discovered: {total_new}")
        
        if self.command_history:
            # Risk distribution
            risk_counts = defaultdict(int)
            for cmd, history in self.command_history.items():
                if history:
                    risk_counts[history[-1]["risk"]] += 1
            
            print("\n🎯 Risk Distribution:")
            for risk, count in sorted(risk_counts.items()):
                print(f"   • {risk:<15} {count:>4} commands")
            
            # Show some interesting commands
            print("\n🔍 Notable Commands:")
            critical = [cmd for cmd, h in self.command_history.items() 
                       if h and h[-1]["risk"] == "CRITICAL"]
            high_risk = [cmd for cmd, h in self.command_history.items() 
                        if h and h[-1]["risk"] == "HIGH_RISK"]
            
            if critical:
                print("   CRITICAL:")
                for cmd in critical[:5]:
                    print(f"      • {cmd}")
            
            if high_risk:
                print("   HIGH_RISK:")
                for cmd in high_risk[:5]:
                    print(f"      • {cmd}")

if __name__ == "__main__":
    monitor = TCPLiveMonitor()
    try:
        monitor.monitor_changes(interval=3)  # Check every 3 seconds for responsiveness
    except KeyboardInterrupt:
        print("\nExiting...")