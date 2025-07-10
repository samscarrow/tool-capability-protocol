#!/usr/bin/env python3
"""
TCP Knowledge Growth - HYBRID BURST MODE
Combines Anthropic API + Local LLMs for maximum speed
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import requests
from anthropic import Anthropic


class HybridTCPAnalyzer:
    def __init__(self):
        self.data_dir = "/opt/tcp-knowledge-system/data"
        self.discovered_commands = set()
        self.completed = 0
        self.failed = 0
        self.lock = threading.Lock()

        # Anthropic client
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if self.api_key:
            self.anthropic_client = Anthropic(api_key=self.api_key)
            print("✓ Anthropic API configured")
        else:
            self.anthropic_client = None
            print("✗ Anthropic API not available")

        # Local LLM endpoint (DigitalOcean local Ollama)
        self.setup_local_ollama()

        # Track analysis sources
        self.analysis_sources = {"anthropic": 0, "ollama": 0}

        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)

        # Load previously discovered commands
        self.load_discovered_commands()

    def setup_local_ollama(self):
        """Setup local Ollama on DigitalOcean droplet"""
        try:
            # Check if Ollama is installed
            result = subprocess.run(["which", "ollama"], capture_output=True)
            if result.returncode != 0:
                print("Installing Ollama locally...")
                subprocess.run(
                    ["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"],
                    shell=True,
                    capture_output=True,
                )

            # Start Ollama if not running
            if subprocess.run(["pgrep", "ollama"], capture_output=True).returncode != 0:
                print("Starting local Ollama...")
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(5)

            # Pull a fast model
            print("Pulling fast model for local analysis...")
            subprocess.run(["ollama", "pull", "tinyllama"], capture_output=True)

            # Test local endpoint
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print("✓ Local Ollama ready")
                self.local_ollama_available = True
            else:
                self.local_ollama_available = False
        except Exception as e:
            print(f"✗ Local Ollama setup failed: {e}")
            self.local_ollama_available = False

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
                    "total_analyzed": len(self.discovered_commands),
                    "analysis_sources": self.analysis_sources,
                },
                f,
                indent=2,
            )

    def get_all_commands(self):
        """Get all system commands"""
        try:
            result = subprocess.run(
                ["bash", "-c", "compgen -c | sort | uniq"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return set(result.stdout.strip().split("\n"))
            else:
                return set()
        except:
            return set()

    def analyze_with_anthropic(self, command):
        """Analyze using Anthropic API"""
        if not self.anthropic_client:
            return None

        try:
            prompt = f"""Analyze Unix command '{command}':
Risk: SAFE/LOW_RISK/MEDIUM_RISK/HIGH_RISK/CRITICAL
Concerns & root needed? <50 words"""

            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}],
            )

            with self.lock:
                self.analysis_sources["anthropic"] += 1

            return response.content[0].text
        except:
            return None

    def analyze_with_ollama(self, command):
        """Analyze using local Ollama"""
        if not self.local_ollama_available:
            return None

        try:
            prompt = f"Analyze Unix command '{command}' security risk (SAFE/LOW_RISK/MEDIUM_RISK/HIGH_RISK/CRITICAL), concerns, root?"

            url = "http://localhost:11434/api/generate"
            data = {
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 50},
            }

            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                with self.lock:
                    self.analysis_sources["ollama"] += 1
                return response.json().get("response", "")
            return None
        except:
            return None

    def analyze_command(self, command, use_anthropic=True):
        """Analyze command using best available method"""
        analysis = None
        source = "unknown"

        # Try Anthropic first for accuracy (if enabled)
        if use_anthropic and self.anthropic_client:
            analysis = self.analyze_with_anthropic(command)
            source = "anthropic"

        # Fallback to Ollama
        if not analysis and self.local_ollama_available:
            analysis = self.analyze_with_ollama(command)
            source = "ollama"

        if analysis:
            # Save analysis
            analysis_file = os.path.join(self.data_dir, f"{command}_analysis.json")
            with open(analysis_file, "w") as f:
                json.dump(
                    {
                        "command": command,
                        "analysis": analysis,
                        "source": source,
                        "timestamp": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )

            with self.lock:
                self.completed += 1
                self.discovered_commands.add(command)
                if self.completed % 50 == 0:
                    print(
                        f"Progress: {self.completed} analyzed (Anthropic: {self.analysis_sources['anthropic']}, Ollama: {self.analysis_sources['ollama']})"
                    )
                    self.save_discovered_commands()

            return True
        else:
            with self.lock:
                self.failed += 1
            return False

    def hybrid_burst_analyze(self):
        """Analyze using hybrid approach"""
        print("\n🚀 HYBRID TCP BURST MODE - Anthropic + Local LLMs!")
        print("=" * 60)

        # Get all commands
        all_commands = self.get_all_commands()
        new_commands = list(all_commands - self.discovered_commands)

        if not new_commands:
            print("All commands already analyzed!")
            return

        print(f"📊 Total commands to analyze: {len(new_commands)}")
        print(f"🔧 Available engines:")
        if self.anthropic_client:
            print(f"   ✓ Anthropic Claude API")
        if self.local_ollama_available:
            print(f"   ✓ Local Ollama (tinyllama)")
        print(f"⚡ Strategy: 80% Ollama (fast), 20% Anthropic (accurate)")
        print(f"🎯 Target: Complete in 3-5 minutes\n")

        start_time = time.time()

        # Split commands: 80% for Ollama, 20% for Anthropic
        ollama_count = int(len(new_commands) * 0.8)
        anthropic_commands = new_commands[: len(new_commands) - ollama_count]
        ollama_commands = new_commands[len(new_commands) - ollama_count :]

        print(
            f"📊 Distribution: {len(anthropic_commands)} Anthropic, {len(ollama_commands)} Ollama"
        )

        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = []

            # Submit Anthropic commands (slower but more accurate)
            for cmd in anthropic_commands:
                future = executor.submit(self.analyze_command, cmd, use_anthropic=True)
                futures.append(future)

            # Submit Ollama commands (faster)
            for cmd in ollama_commands:
                future = executor.submit(self.analyze_command, cmd, use_anthropic=False)
                futures.append(future)

            # Wait for completion
            for future in as_completed(futures):
                pass

        # Final save
        self.save_discovered_commands()

        elapsed = time.time() - start_time
        print(f"\n✅ HYBRID BURST MODE COMPLETE!")
        print(f"⏱️  Time taken: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"📊 Total analyzed: {self.completed}")
        print(f"   - Via Anthropic: {self.analysis_sources['anthropic']}")
        print(f"   - Via Ollama: {self.analysis_sources['ollama']}")
        print(f"❌ Failed: {self.failed}")
        print(
            f"🎯 Success rate: {(self.completed/(self.completed+self.failed)*100):.1f}%"
        )
        print(f"⚡ Speed: {self.completed/elapsed:.1f} commands/second")


if __name__ == "__main__":
    print("TCP Knowledge Growth System - HYBRID BURST MODE")

    analyzer = HybridTCPAnalyzer()
    analyzer.hybrid_burst_analyze()
