#!/usr/bin/env python3
"""
TCP Knowledge Growth - BURST MODE
Complete full system analysis in 5 minutes
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from anthropic import Anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class TCPBurstAnalyzer:
    def __init__(self):
        # Get API key from environment
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            print("ERROR: ANTHROPIC_API_KEY not found in environment")
            sys.exit(1)
            
        self.client = Anthropic(api_key=self.api_key)
        self.data_dir = "/opt/tcp-knowledge-system/data"
        self.discovered_commands = set()
        self.completed = 0
        self.failed = 0
        self.lock = threading.Lock()
        
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load previously discovered commands
        self.load_discovered_commands()
        
    def load_discovered_commands(self):
        """Load previously discovered commands"""
        discovered_file = os.path.join(self.data_dir, "discovered_commands.json")
        if os.path.exists(discovered_file):
            with open(discovered_file, 'r') as f:
                data = json.load(f)
                self.discovered_commands = set(data.get("commands", []))
        print(f"Loaded {len(self.discovered_commands)} previously discovered commands")
    
    def save_discovered_commands(self):
        """Save discovered commands"""
        discovered_file = os.path.join(self.data_dir, "discovered_commands.json")
        with open(discovered_file, 'w') as f:
            json.dump({
                "commands": list(self.discovered_commands),
                "last_updated": datetime.now().isoformat(),
                "total_analyzed": len(self.discovered_commands)
            }, f, indent=2)
    
    def get_all_commands(self):
        """Get all system commands"""
        try:
            result = subprocess.run(
                ["bash", "-c", "compgen -c | sort | uniq"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return set(result.stdout.strip().split('\n'))
            else:
                print(f"Command discovery failed: {result.stderr}")
                return set()
        except Exception as e:
            print(f"Error getting commands: {e}")
            return set()
    
    def analyze_command(self, command):
        """Analyze a command using Claude with retry logic"""
        max_retries = 3
        retry_delay = 0.2
        
        for attempt in range(max_retries):
            try:
                prompt = f"""Analyze Unix command '{command}':
1. Risk: SAFE/LOW_RISK/MEDIUM_RISK/HIGH_RISK/CRITICAL
2. Main concerns
3. Needs root? Y/N
Under 50 words."""
                
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                analysis = response.content[0].text
                
                # Save analysis
                analysis_file = os.path.join(self.data_dir, f"{command}_analysis.json")
                with open(analysis_file, 'w') as f:
                    json.dump({
                        "command": command,
                        "analysis": analysis,
                        "timestamp": datetime.now().isoformat()
                    }, f, indent=2)
                
                with self.lock:
                    self.completed += 1
                    self.discovered_commands.add(command)
                    if self.completed % 50 == 0:
                        print(f"Progress: {self.completed} analyzed, {self.failed} failed")
                        self.save_discovered_commands()
                
                return True
                
            except Exception as e:
                if "rate" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    with self.lock:
                        self.failed += 1
                    return False
    
    def burst_analyze(self):
        """Analyze all commands in burst mode"""
        print("\n🚀 TCP BURST MODE - Analyzing entire system in 5 minutes!")
        print("=" * 60)
        
        # Get all commands
        all_commands = self.get_all_commands()
        new_commands = all_commands - self.discovered_commands
        
        if not new_commands:
            print("All commands already analyzed!")
            return
        
        print(f"📊 Total commands to analyze: {len(new_commands)}")
        print(f"⚡ Using 50 concurrent threads")
        print(f"🎯 Target: Complete in 5 minutes\n")
        
        start_time = time.time()
        
        # Process in batches to avoid overwhelming the API
        batch_size = 500
        commands_list = list(new_commands)
        
        for i in range(0, len(commands_list), batch_size):
            batch = commands_list[i:i+batch_size]
            print(f"\n📦 Processing batch {i//batch_size + 1} ({len(batch)} commands)...")
            
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(self.analyze_command, cmd) for cmd in batch]
                
                # Wait for batch to complete
                for future in as_completed(futures):
                    pass
            
            # Small delay between batches
            if i + batch_size < len(commands_list):
                print(f"   Completed: {self.completed}, Failed: {self.failed}")
                time.sleep(2)
        
        # Final save
        self.save_discovered_commands()
        
        elapsed = time.time() - start_time
        print(f"\n✅ BURST MODE COMPLETE!")
        print(f"⏱️  Time taken: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"📊 Total analyzed: {self.completed}")
        print(f"❌ Failed: {self.failed}")
        print(f"🎯 Success rate: {(self.completed/(self.completed+self.failed)*100):.1f}%")
        print(f"⚡ Speed: {self.completed/elapsed:.1f} commands/second")

if __name__ == "__main__":
    print("TCP Knowledge Growth System - BURST MODE")
    print("WARNING: This will make many API calls very quickly!")
    
    analyzer = TCPBurstAnalyzer()
    analyzer.burst_analyze()