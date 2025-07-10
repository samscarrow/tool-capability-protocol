#!/usr/bin/env python3
"""
TCP Knowledge Growth - DISTRIBUTED BURST MODE
Leverages local LLMs on MacBook and Gentoo for massive parallel processing
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

class DistributedTCPAnalyzer:
    def __init__(self):
        self.data_dir = "/opt/tcp-knowledge-system/data"
        self.discovered_commands = set()
        self.completed = 0
        self.failed = 0
        self.lock = threading.Lock()
        
        # LLM endpoints
        self.llm_endpoints = [
            # MacBookPro with Ollama
            {
                "name": "MacBookPro-Ollama",
                "host": "192.168.1.229",
                "port": 11434,
                "model": "llama2",
                "type": "ollama"
            },
            # Gentoo with Ollama
            {
                "name": "Gentoo-Ollama", 
                "host": "gentoo.local",
                "port": 11434,
                "model": "mistral",
                "type": "ollama"
            },
            # MacBookPro with MLX
            {
                "name": "MacBookPro-MLX",
                "host": "192.168.1.229",
                "port": 8080,
                "model": "phi-2",
                "type": "mlx"
            },
            # Local Ollama if available
            {
                "name": "Local-Ollama",
                "host": "localhost",
                "port": 11434,
                "model": "codellama",
                "type": "ollama"
            }
        ]
        
        # Test endpoints and keep only working ones
        self.active_endpoints = self.test_endpoints()
        print(f"Active LLM endpoints: {len(self.active_endpoints)}")
        
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load previously discovered commands
        self.load_discovered_commands()
    
    def test_endpoints(self):
        """Test which LLM endpoints are available"""
        active = []
        for endpoint in self.llm_endpoints:
            try:
                if endpoint["type"] == "ollama":
                    # Test Ollama endpoint
                    url = f"http://{endpoint['host']}:{endpoint['port']}/api/tags"
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        active.append(endpoint)
                        print(f"✓ {endpoint['name']} is active")
                elif endpoint["type"] == "mlx":
                    # Test MLX endpoint
                    url = f"http://{endpoint['host']}:{endpoint['port']}/health"
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        active.append(endpoint)
                        print(f"✓ {endpoint['name']} is active")
            except:
                print(f"✗ {endpoint['name']} is not available")
        return active
    
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
                "total_analyzed": len(self.discovered_commands),
                "llm_endpoints_used": len(self.active_endpoints)
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
    
    def analyze_with_ollama(self, command, endpoint):
        """Analyze command using Ollama API"""
        try:
            prompt = f"""Analyze Unix command '{command}' for security:
1. Risk level: SAFE/LOW_RISK/MEDIUM_RISK/HIGH_RISK/CRITICAL
2. Main security concerns (if any)
3. Requires root/sudo? Yes/No
Keep under 50 words."""
            
            url = f"http://{endpoint['host']}:{endpoint['port']}/api/generate"
            data = {
                "model": endpoint["model"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 100
                }
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                return response.json().get("response", "")
            return None
        except Exception as e:
            return None
    
    def analyze_with_mlx(self, command, endpoint):
        """Analyze command using MLX API"""
        try:
            prompt = f"Analyze Unix command '{command}': risk level (SAFE/LOW_RISK/MEDIUM_RISK/HIGH_RISK/CRITICAL), concerns, needs root?"
            
            url = f"http://{endpoint['host']}:{endpoint['port']}/generate"
            data = {
                "prompt": prompt,
                "max_tokens": 100,
                "temperature": 0.3
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                return response.json().get("text", "")
            return None
        except:
            return None
    
    def analyze_command(self, command, endpoint_index):
        """Analyze a command using specified endpoint"""
        endpoint = self.active_endpoints[endpoint_index % len(self.active_endpoints)]
        
        try:
            # Choose analysis method based on endpoint type
            if endpoint["type"] == "ollama":
                analysis = self.analyze_with_ollama(command, endpoint)
            elif endpoint["type"] == "mlx":
                analysis = self.analyze_with_mlx(command, endpoint)
            else:
                analysis = None
            
            if analysis:
                # Save analysis
                analysis_file = os.path.join(self.data_dir, f"{command}_analysis.json")
                with open(analysis_file, 'w') as f:
                    json.dump({
                        "command": command,
                        "analysis": analysis,
                        "llm_endpoint": endpoint["name"],
                        "timestamp": datetime.now().isoformat()
                    }, f, indent=2)
                
                with self.lock:
                    self.completed += 1
                    self.discovered_commands.add(command)
                    if self.completed % 100 == 0:
                        print(f"Progress: {self.completed} analyzed ({self.completed/60:.1f}/sec)")
                        self.save_discovered_commands()
                
                return True
            else:
                with self.lock:
                    self.failed += 1
                return False
                
        except Exception as e:
            with self.lock:
                self.failed += 1
            return False
    
    def distributed_burst_analyze(self):
        """Analyze all commands using distributed LLMs"""
        print("\n🚀 DISTRIBUTED TCP BURST MODE - Using Local LLMs!")
        print("=" * 60)
        
        if not self.active_endpoints:
            print("❌ No active LLM endpoints found!")
            print("\nTo set up local LLMs:")
            print("1. MacBook: brew install ollama && ollama serve")
            print("2. Gentoo: emerge ollama && ollama serve")
            print("3. Start MLX server on MacBook")
            return
        
        # Get all commands
        all_commands = self.get_all_commands()
        new_commands = all_commands - self.discovered_commands
        
        if not new_commands:
            print("All commands already analyzed!")
            return
        
        print(f"📊 Total commands to analyze: {len(new_commands)}")
        print(f"🖥️  Active LLM endpoints: {len(self.active_endpoints)}")
        print(f"⚡ Using {len(self.active_endpoints) * 20} concurrent threads")
        print(f"🎯 Target: Complete in 2-3 minutes with local processing\n")
        
        start_time = time.time()
        
        # Create thread pool with workers per endpoint
        max_workers = len(self.active_endpoints) * 20
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Distribute commands across endpoints
            futures = []
            for i, cmd in enumerate(new_commands):
                future = executor.submit(self.analyze_command, cmd, i)
                futures.append(future)
            
            # Process results
            for future in as_completed(futures):
                pass
        
        # Final save
        self.save_discovered_commands()
        
        elapsed = time.time() - start_time
        print(f"\n✅ DISTRIBUTED BURST MODE COMPLETE!")
        print(f"⏱️  Time taken: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"📊 Total analyzed: {self.completed}")
        print(f"❌ Failed: {self.failed}")
        print(f"🎯 Success rate: {(self.completed/(self.completed+self.failed)*100):.1f}%")
        print(f"⚡ Speed: {self.completed/elapsed:.1f} commands/second")
        print(f"🖥️  Commands per endpoint: ~{self.completed/len(self.active_endpoints):.0f}")

if __name__ == "__main__":
    print("TCP Knowledge Growth System - DISTRIBUTED BURST MODE")
    print("Using local LLMs on MacBook and Gentoo systems")
    
    analyzer = DistributedTCPAnalyzer()
    analyzer.distributed_burst_analyze()