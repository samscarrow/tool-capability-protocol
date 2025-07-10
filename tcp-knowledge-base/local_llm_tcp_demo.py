#!/usr/bin/env python3
"""
Local LLM TCP Demo - Process 100 commands using only local Ollama
No internet connection required!
"""

import subprocess
import json
import time
import requests
from typing import Dict, List, Optional
import random


class LocalLLMTCPProcessor:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.available_models = []
        self.commands_to_analyze = []
        self.analysis_results = {}

    def check_ollama(self) -> bool:
        """Check if Ollama is running locally"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                self.available_models = [m["name"] for m in models]
                return True
        except:
            pass
        return False

    def start_ollama(self):
        """Start Ollama if not running"""
        print("🚀 Starting local Ollama server...")
        try:
            # Check if ollama is installed
            result = subprocess.run(["which", "ollama"], capture_output=True)
            if result.returncode != 0:
                print("❌ Ollama not installed. Install with: brew install ollama")
                return False

            # Start ollama serve in background
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Wait for startup
            print("⏳ Waiting for Ollama to start...")
            for i in range(10):
                time.sleep(2)
                if self.check_ollama():
                    print("✅ Ollama started successfully")
                    return True

            print("❌ Ollama failed to start")
            return False

        except Exception as e:
            print(f"❌ Error starting Ollama: {e}")
            return False

    def ensure_model(self, model_name: str = "phi3:mini"):
        """Ensure a lightweight model is available"""
        if model_name in self.available_models:
            print(f"✅ Model '{model_name}' already available")
            return True

        print(f"📥 Pulling lightweight model '{model_name}'...")
        try:
            # Pull a small, fast model
            result = subprocess.run(
                ["ollama", "pull", model_name], capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"✅ Model '{model_name}' ready")
                self.available_models.append(model_name)
                return True
            else:
                print(f"❌ Failed to pull model: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error pulling model: {e}")
            return False

    def get_sample_commands(self, count: int = 100) -> List[str]:
        """Get sample Unix commands to analyze"""
        # Common Unix commands across different categories
        all_commands = [
            # File operations
            "ls",
            "cd",
            "pwd",
            "mkdir",
            "rmdir",
            "cp",
            "mv",
            "rm",
            "touch",
            "cat",
            "head",
            "tail",
            "less",
            "more",
            "grep",
            "find",
            "locate",
            "which",
            "file",
            "stat",
            "du",
            "df",
            "ln",
            "readlink",
            "basename",
            "dirname",
            # Text processing
            "sed",
            "awk",
            "cut",
            "sort",
            "uniq",
            "tr",
            "wc",
            "split",
            "join",
            "paste",
            "comm",
            "diff",
            "patch",
            "col",
            "expand",
            "unexpand",
            "fmt",
            "fold",
            # System info
            "ps",
            "top",
            "htop",
            "free",
            "uptime",
            "who",
            "w",
            "last",
            "id",
            "groups",
            "hostname",
            "uname",
            "date",
            "cal",
            "env",
            "printenv",
            "alias",
            "history",
            # Network
            "ping",
            "traceroute",
            "netstat",
            "ss",
            "ip",
            "ifconfig",
            "route",
            "arp",
            "dig",
            "nslookup",
            "host",
            "curl",
            "wget",
            "nc",
            "telnet",
            "ssh",
            "scp",
            # Process control
            "kill",
            "killall",
            "pkill",
            "nice",
            "renice",
            "nohup",
            "jobs",
            "fg",
            "bg",
            "wait",
            "sleep",
            "watch",
            "timeout",
            "at",
            "cron",
            "crontab",
            # Permissions & Security
            "chmod",
            "chown",
            "chgrp",
            "umask",
            "su",
            "sudo",
            "passwd",
            "useradd",
            "userdel",
            "usermod",
            "groupadd",
            "groupdel",
            "visudo",
            "chroot",
            # Archive & Compression
            "tar",
            "gzip",
            "gunzip",
            "zip",
            "unzip",
            "bzip2",
            "bunzip2",
            "xz",
            "7z",
            "rar",
            "unrar",
            "zcat",
            "bzcat",
            "xzcat",
            # Development
            "gcc",
            "g++",
            "make",
            "git",
            "svn",
            "diff",
            "patch",
            "gdb",
            "strace",
            "ltrace",
            "ldd",
            "nm",
            "objdump",
            "strings",
            "strip",
            # Package management
            "apt",
            "apt-get",
            "dpkg",
            "snap",
            "brew",
            "port",
            "pip",
            "npm",
            "gem",
            # Dangerous commands
            "dd",
            "mkfs",
            "fdisk",
            "parted",
            "shred",
            "wipefs",
        ]

        # Return requested number of commands
        return all_commands[:count] if count <= len(all_commands) else all_commands

    def analyze_command_local(self, command: str, model: str = "phi3:mini") -> Dict:
        """Analyze a command using local LLM"""
        prompt = f"""Analyze the Unix/Linux command '{command}' for security and capabilities.

Provide a brief assessment with:
1. Risk level: SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, or CRITICAL
2. Main capabilities (what it does)
3. Security concerns if any
4. Whether it requires sudo/root

Keep response under 100 words. Be concise."""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 150,
                        "seed": 42,  # For reproducibility
                    },
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                analysis = result.get("response", "")

                # Extract risk level
                risk = "UNKNOWN"
                analysis_upper = analysis.upper()
                for level in [
                    "CRITICAL",
                    "HIGH_RISK",
                    "MEDIUM_RISK",
                    "LOW_RISK",
                    "SAFE",
                ]:
                    if (
                        level.replace("_", " ") in analysis_upper
                        or level in analysis_upper
                    ):
                        risk = level
                        break

                return {
                    "command": command,
                    "risk": risk,
                    "analysis": analysis,
                    "model": model,
                    "processing_time_ms": result.get("total_duration", 0) // 1_000_000,
                }
            else:
                return {
                    "command": command,
                    "risk": "ERROR",
                    "analysis": f"API error: {response.status_code}",
                    "model": model,
                    "processing_time_ms": 0,
                }

        except Exception as e:
            return {
                "command": command,
                "risk": "ERROR",
                "analysis": f"Error: {str(e)}",
                "model": model,
                "processing_time_ms": 0,
            }

    def process_commands_batch(self, commands: List[str], model: str = "phi3:mini"):
        """Process multiple commands with progress tracking"""
        print(f"\n🔄 Processing {len(commands)} commands with local model '{model}'...")
        print("=" * 60)

        start_time = time.time()
        successful = 0
        failed = 0

        risk_distribution = {
            "SAFE": 0,
            "LOW_RISK": 0,
            "MEDIUM_RISK": 0,
            "HIGH_RISK": 0,
            "CRITICAL": 0,
            "UNKNOWN": 0,
            "ERROR": 0,
        }

        total_processing_time = 0

        for i, command in enumerate(commands, 1):
            # Show progress
            if i % 10 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                eta = (len(commands) - i) / rate
                print(
                    f"Progress: {i}/{len(commands)} ({i/len(commands)*100:.1f}%) | "
                    f"Rate: {rate:.1f} cmd/s | ETA: {eta:.0f}s"
                )

            # Analyze command
            result = self.analyze_command_local(command, model)
            self.analysis_results[command] = result

            # Update statistics
            risk_distribution[result["risk"]] += 1
            total_processing_time += result["processing_time_ms"]

            if result["risk"] != "ERROR":
                successful += 1
            else:
                failed += 1

            # Show sample results
            if i <= 5 or i % 20 == 0:
                print(f"\n📋 {command}: [{result['risk']}]")
                print(f"   {result['analysis'][:100]}...")
                print(f"   Processing time: {result['processing_time_ms']}ms")

        # Final statistics
        total_time = time.time() - start_time

        print("\n" + "=" * 60)
        print("📊 Processing Complete!")
        print("=" * 60)
        print(f"Total commands: {len(commands)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total time: {total_time:.1f}s")
        print(f"Average rate: {len(commands)/total_time:.1f} commands/second")
        print(
            f"Average LLM processing: {total_processing_time/len(commands):.0f}ms per command"
        )

        print("\n🎯 Risk Distribution:")
        for risk, count in sorted(risk_distribution.items()):
            if count > 0:
                percentage = (count / len(commands)) * 100
                bar = "█" * int(percentage / 2)
                print(f"  {risk:<12} {count:>3} ({percentage:>5.1f}%) {bar}")

        return self.analysis_results

    def save_results(self, filename: str = "local_llm_tcp_results.json"):
        """Save analysis results"""
        output = {
            "metadata": {
                "total_commands": len(self.analysis_results),
                "models_used": list(
                    set(r["model"] for r in self.analysis_results.values())
                ),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "processing_mode": "local_llm_only",
            },
            "results": self.analysis_results,
        }

        with open(filename, "w") as f:
            json.dump(output, f, indent=2)

        print(f"\n💾 Results saved to: {filename}")

    def demo(self):
        """Run the complete local LLM demo"""
        print("🏠 TCP Local LLM Demo - No Internet Required!")
        print("=" * 60)

        # Check/start Ollama
        if not self.check_ollama():
            if not self.start_ollama():
                print("\n⚠️  Please install and start Ollama:")
                print("   brew install ollama")
                print("   ollama serve")
                return

        print(f"\n📋 Available models: {', '.join(self.available_models)}")

        # Ensure we have a lightweight model
        model = "phi3:mini"  # Small, fast model
        if not self.available_models or model not in self.available_models:
            if not self.ensure_model(model):
                # Try alternative models
                for alt_model in ["tinyllama", "llama2:7b", "mistral"]:
                    if alt_model in self.available_models:
                        model = alt_model
                        break
                else:
                    print("❌ No suitable model available")
                    return

        # Get commands to analyze
        commands = self.get_sample_commands(100)
        print(f"\n🎯 Analyzing {len(commands)} Unix commands locally...")

        # Process commands
        results = self.process_commands_batch(commands, model)

        # Save results
        self.save_results()

        print("\n✨ Demo Complete!")
        print("   • Processed 100 commands using only local LLM")
        print("   • No internet connection required")
        print("   • Results saved for TCP binary generation")


if __name__ == "__main__":
    processor = LocalLLMTCPProcessor()
    processor.demo()
