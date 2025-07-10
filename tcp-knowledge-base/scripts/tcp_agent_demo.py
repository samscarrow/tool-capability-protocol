#!/usr/bin/env python3
"""
TCP Agent Demo - Demonstrating how TCP makes AI agents aware of their tools
"""

import os
import json
import subprocess
import struct
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class TCPAwareAgent:
    """An AI agent that uses TCP to understand and safely use available tools"""
    
    def __init__(self, tcp_data_dir="/opt/tcp-knowledge-system/data"):
        self.tcp_data_dir = tcp_data_dir
        self.tcp_descriptors = {}
        self.safe_commands = []
        self.risky_commands = {}
        self.tool_capabilities = {}
        
        # Load TCP knowledge
        self.load_tcp_knowledge()
        
    def load_tcp_knowledge(self):
        """Load TCP descriptors and build tool awareness"""
        print("🧠 Loading TCP Knowledge Base...")
        
        # Connect to TCP system
        cmd = f"ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 'ls {self.tcp_data_dir}/*_analysis.json'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            files = result.stdout.strip().split('\n')
            
            for filepath in files[:100]:  # Sample first 100 for demo
                if filepath:
                    # Get command name
                    cmd_name = os.path.basename(filepath).replace('_analysis.json', '')
                    
                    # Load analysis
                    cmd2 = f"ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 'cat {filepath}'"
                    result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
                    
                    if result2.returncode == 0:
                        try:
                            data = json.loads(result2.stdout)
                            analysis = data.get("analysis", "")
                            
                            # Extract TCP intelligence
                            risk_level = self.extract_risk_level(analysis)
                            capabilities = self.extract_capabilities(analysis, cmd_name)
                            
                            # Store in agent's knowledge
                            self.tcp_descriptors[cmd_name] = {
                                "risk": risk_level,
                                "capabilities": capabilities,
                                "requires_sudo": "sudo" in analysis.lower() or "root" in analysis.lower(),
                                "analysis": analysis
                            }
                            
                            # Categorize for quick access
                            if risk_level == "SAFE":
                                self.safe_commands.append(cmd_name)
                            else:
                                if risk_level not in self.risky_commands:
                                    self.risky_commands[risk_level] = []
                                self.risky_commands[risk_level].append(cmd_name)
                            
                            # Build capability index
                            for cap in capabilities:
                                if cap not in self.tool_capabilities:
                                    self.tool_capabilities[cap] = []
                                self.tool_capabilities[cap].append(cmd_name)
                                
                        except:
                            pass
            
            print(f"✅ Loaded {len(self.tcp_descriptors)} tool descriptors")
            print(f"   • Safe tools: {len(self.safe_commands)}")
            print(f"   • Risky tools: {sum(len(cmds) for cmds in self.risky_commands.values())}")
            print(f"   • Capabilities indexed: {len(self.tool_capabilities)}")
    
    def extract_risk_level(self, analysis: str) -> str:
        """Extract risk level from TCP analysis"""
        analysis_upper = analysis.upper()
        for level in ["CRITICAL", "HIGH_RISK", "MEDIUM_RISK", "LOW_RISK", "SAFE"]:
            if level in analysis_upper:
                return level
        return "UNKNOWN"
    
    def extract_capabilities(self, analysis: str, cmd_name: str) -> List[str]:
        """Extract capabilities from analysis"""
        capabilities = []
        analysis_lower = analysis.lower()
        
        # File operations
        if any(word in analysis_lower for word in ["file", "directory", "path"]):
            if any(word in analysis_lower for word in ["create", "write", "modify"]):
                capabilities.append("file_write")
            if any(word in analysis_lower for word in ["read", "list", "show"]):
                capabilities.append("file_read")
            if any(word in analysis_lower for word in ["delete", "remove"]):
                capabilities.append("file_delete")
        
        # Network operations
        if any(word in analysis_lower for word in ["network", "internet", "connection", "port"]):
            capabilities.append("network_access")
        
        # System operations
        if any(word in analysis_lower for word in ["process", "system", "service"]):
            capabilities.append("system_control")
        
        # Data processing
        if any(word in analysis_lower for word in ["search", "find", "grep", "filter"]):
            capabilities.append("data_search")
        if any(word in analysis_lower for word in ["transform", "convert", "parse"]):
            capabilities.append("data_transform")
        
        # Container operations
        if any(word in cmd_name.lower() for word in ["docker", "container", "pod"]):
            capabilities.append("container_ops")
        
        # Security operations
        if any(word in analysis_lower for word in ["security", "scan", "audit", "vulnerability"]):
            capabilities.append("security_scan")
        
        return capabilities
    
    def find_tools_for_task(self, task_description: str) -> Dict[str, List[str]]:
        """Find appropriate tools for a given task using TCP knowledge"""
        print(f"\n🔍 Finding tools for: '{task_description}'")
        
        task_lower = task_description.lower()
        relevant_tools = {
            "recommended": [],
            "alternative": [],
            "avoid": []
        }
        
        # Determine needed capabilities
        needed_capabilities = []
        
        if any(word in task_lower for word in ["search", "find", "locate", "grep"]):
            needed_capabilities.append("data_search")
        if any(word in task_lower for word in ["file", "directory", "folder"]):
            if "list" in task_lower or "show" in task_lower:
                needed_capabilities.append("file_read")
            elif any(word in task_lower for word in ["create", "write", "save"]):
                needed_capabilities.append("file_write")
            elif any(word in task_lower for word in ["delete", "remove"]):
                needed_capabilities.append("file_delete")
        if any(word in task_lower for word in ["network", "download", "upload", "connect"]):
            needed_capabilities.append("network_access")
        if any(word in task_lower for word in ["container", "docker", "image"]):
            needed_capabilities.append("container_ops")
        if any(word in task_lower for word in ["security", "scan", "audit"]):
            needed_capabilities.append("security_scan")
        
        print(f"   Identified capabilities needed: {needed_capabilities}")
        
        # Find tools with needed capabilities
        candidate_tools = set()
        for cap in needed_capabilities:
            if cap in self.tool_capabilities:
                candidate_tools.update(self.tool_capabilities[cap])
        
        # Categorize by risk
        for tool in candidate_tools:
            if tool in self.tcp_descriptors:
                risk = self.tcp_descriptors[tool]["risk"]
                
                if risk == "SAFE" or risk == "LOW_RISK":
                    relevant_tools["recommended"].append((tool, risk))
                elif risk == "MEDIUM_RISK":
                    relevant_tools["alternative"].append((tool, risk))
                else:  # HIGH_RISK or CRITICAL
                    relevant_tools["avoid"].append((tool, risk))
        
        # Sort by safety
        for category in relevant_tools:
            relevant_tools[category].sort(key=lambda x: x[0])
        
        return relevant_tools
    
    def explain_tool(self, command: str) -> str:
        """Explain a tool's capabilities and risks using TCP knowledge"""
        if command in self.tcp_descriptors:
            desc = self.tcp_descriptors[command]
            explanation = f"\n📋 Tool: {command}\n"
            explanation += f"   Risk Level: {desc['risk']}\n"
            explanation += f"   Capabilities: {', '.join(desc['capabilities'])}\n"
            explanation += f"   Requires Sudo: {'Yes' if desc['requires_sudo'] else 'No'}\n"
            explanation += f"   Analysis: {desc['analysis'][:200]}..."
            return explanation
        else:
            return f"❓ No TCP data available for '{command}'"
    
    def suggest_safe_alternative(self, risky_command: str) -> Optional[str]:
        """Suggest safer alternatives to risky commands"""
        if risky_command not in self.tcp_descriptors:
            return None
        
        risky_caps = self.tcp_descriptors[risky_command]["capabilities"]
        
        # Find safe commands with similar capabilities
        alternatives = []
        for safe_cmd in self.safe_commands:
            if safe_cmd in self.tcp_descriptors:
                safe_caps = self.tcp_descriptors[safe_cmd]["capabilities"]
                # Check capability overlap
                overlap = set(risky_caps) & set(safe_caps)
                if overlap:
                    alternatives.append((safe_cmd, len(overlap)))
        
        # Sort by most capability overlap
        alternatives.sort(key=lambda x: x[1], reverse=True)
        
        if alternatives:
            return alternatives[0][0]
        return None
    
    def demonstrate_agent_awareness(self):
        """Demonstrate how TCP makes agents aware of their tools"""
        print("\n" + "="*60)
        print("🤖 TCP-Aware Agent Demonstration")
        print("="*60)
        
        # Demo 1: Task-based tool discovery
        tasks = [
            "search for configuration files",
            "list running docker containers",
            "scan network for open ports",
            "delete temporary files",
            "monitor system performance"
        ]
        
        for task in tasks:
            tools = self.find_tools_for_task(task)
            
            print(f"\n📌 Task: {task}")
            
            if tools["recommended"]:
                print("   ✅ Recommended (safe) tools:")
                for tool, risk in tools["recommended"][:3]:
                    print(f"      • {tool} [{risk}]")
            
            if tools["alternative"]:
                print("   ⚠️  Alternative (use with caution):")
                for tool, risk in tools["alternative"][:2]:
                    print(f"      • {tool} [{risk}]")
            
            if tools["avoid"]:
                print("   ❌ Avoid (high risk):")
                for tool, risk in tools["avoid"][:2]:
                    print(f"      • {tool} [{risk}]")
        
        # Demo 2: Risk mitigation
        print("\n\n🛡️ Risk Mitigation Examples:")
        risky_commands = ["rm", "dd", "chmod", "sudo"]
        
        for risky in risky_commands:
            if risky in self.tcp_descriptors:
                safe_alt = self.suggest_safe_alternative(risky)
                print(f"\n   ⚠️  Risky: {risky} [{self.tcp_descriptors[risky]['risk']}]")
                if safe_alt:
                    print(f"   ✅ Safer alternative: {safe_alt}")
                else:
                    print(f"   ⚡ No direct alternative - use with extreme caution!")
        
        # Demo 3: Capability awareness
        print("\n\n🔧 Tool Capability Index:")
        for cap, tools in list(self.tool_capabilities.items())[:5]:
            print(f"\n   📦 {cap}:")
            safe_tools = [t for t in tools if t in self.safe_commands][:3]
            if safe_tools:
                print(f"      Safe tools: {', '.join(safe_tools)}")
        
        # Demo 4: Binary descriptor simulation
        print("\n\n💾 TCP Binary Descriptors (24-byte format):")
        print("   Command    Risk  Caps  Sudo  Size")
        print("   --------   ----  ----  ----  ----")
        
        for cmd in ["ls", "rm", "docker", "nmap", "cat"][:5]:
            if cmd in self.tcp_descriptors:
                desc = self.tcp_descriptors[cmd]
                risk_byte = {"SAFE": 0x01, "LOW_RISK": 0x02, "MEDIUM_RISK": 0x04, 
                            "HIGH_RISK": 0x08, "CRITICAL": 0x10}.get(desc["risk"], 0x00)
                caps_byte = len(desc["capabilities"])
                sudo_byte = 0x01 if desc["requires_sudo"] else 0x00
                
                print(f"   {cmd:<10} 0x{risk_byte:02X}  0x{caps_byte:02X}  0x{sudo_byte:02X}  24B")

def main():
    print("🚀 TCP Agent Awareness Demonstration")
    print("Connecting to TCP Knowledge System...")
    
    agent = TCPAwareAgent()
    agent.demonstrate_agent_awareness()
    
    print("\n\n✨ This demonstrates how TCP enables AI agents to:")
    print("   1. Understand available tools and their risks")
    print("   2. Select appropriate tools for tasks")
    print("   3. Avoid dangerous operations")
    print("   4. Suggest safer alternatives")
    print("   5. Make microsecond safety decisions")
    print("\nThe 24-byte descriptors enable instant tool awareness!")

if __name__ == "__main__":
    main()