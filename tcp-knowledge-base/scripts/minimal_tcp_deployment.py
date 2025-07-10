#!/usr/bin/env python3
"""
Minimal TCP Knowledge Growth System for DigitalOcean
Simplified version with no external dependencies except anthropic
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
import schedule
from anthropic import Anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed


class MinimalTCPSystem:
    def __init__(self):
        # Get API key from environment
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("ERROR: ANTHROPIC_API_KEY not found in environment")
            sys.exit(1)

        self.client = Anthropic(api_key=self.api_key)
        self.data_dir = "/opt/tcp-knowledge-system/data"
        self.discovered_commands = set()

        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)

        # Load previously discovered commands
        self.load_discovered_commands()

    def load_discovered_commands(self):
        """Load previously discovered commands"""
        discovered_file = os.path.join(self.data_dir, "discovered_commands.json")
        if os.path.exists(discovered_file):
            with open(discovered_file, "r") as f:
                data = json.load(f)
                self.discovered_commands = set(data.get("commands", []))
        print(f"Loaded {len(self.discovered_commands)} previously discovered commands")

    def save_discovered_commands(self):
        """Save discovered commands"""
        discovered_file = os.path.join(self.data_dir, "discovered_commands.json")
        with open(discovered_file, "w") as f:
            json.dump(
                {
                    "commands": list(self.discovered_commands),
                    "last_updated": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )

    def discover_new_commands(self):
        """Discover new system commands"""
        print(f"\n[{datetime.now()}] Starting command discovery...")

        try:
            # Get list of all executables in PATH
            result = subprocess.run(
                ["bash", "-c", "compgen -c | sort | uniq"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                all_commands = set(result.stdout.strip().split("\n"))
                new_commands = all_commands - self.discovered_commands

                if new_commands:
                    print(f"Found {len(new_commands)} new commands to analyze")
                    # Analyze 350 commands concurrently for ultra-fast completion in 5 minutes
                    commands_to_analyze = list(new_commands)[:350]

                    # Use large thread pool for maximum concurrent API calls
                    with ThreadPoolExecutor(max_workers=20) as executor:
                        future_to_cmd = {
                            executor.submit(self.analyze_command, cmd): cmd
                            for cmd in commands_to_analyze
                        }

                        for future in as_completed(future_to_cmd):
                            cmd = future_to_cmd[future]
                            try:
                                if future.result():
                                    self.discovered_commands.add(cmd)
                            except Exception as e:
                                print(f"    ✗ Error analyzing {cmd}: {e}")

                    self.save_discovered_commands()
                else:
                    print("No new commands found")
            else:
                print(f"Command discovery failed: {result.stderr}")

        except Exception as e:
            print(f"Error during discovery: {e}")

    def analyze_command(self, command):
        """Analyze a command using Claude with retry logic"""
        max_retries = 3
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                # Simple prompt for TCP analysis
                prompt = f"""Analyze the Unix command '{command}' for security classification.

Provide a brief assessment including:
1. Risk level: SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, or CRITICAL
2. Main security concerns (if any)
3. Whether it requires root/sudo

Keep response under 100 words."""

                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}],
                )

                analysis = response.content[0].text

                # Save analysis
                analysis_file = os.path.join(self.data_dir, f"{command}_analysis.json")
                with open(analysis_file, "w") as f:
                    json.dump(
                        {
                            "command": command,
                            "analysis": analysis,
                            "timestamp": datetime.now().isoformat(),
                        },
                        f,
                        indent=2,
                    )

                return True

            except Exception as e:
                if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    return False

    def run_continuous_learning(self):
        """Run continuous learning cycles"""
        print("Starting TCP Knowledge Growth System...")
        print(f"API Key configured: {'Yes' if self.api_key else 'No'}")
        print(f"Data directory: {self.data_dir}")

        # Schedule discovery every minute for continuous learning
        schedule.every(1).minutes.do(self.discover_new_commands)

        # Run initial discovery
        self.discover_new_commands()

        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(10)  # Check every 10 seconds for more responsive scheduling


if __name__ == "__main__":
    print("TCP Knowledge Growth System - Minimal Version")
    print("=" * 50)

    system = MinimalTCPSystem()
    system.run_continuous_learning()
