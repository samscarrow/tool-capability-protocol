#!/usr/bin/env python3
"""
TCP Multi-Stage Refinery - Systematic command analysis pipeline
Stages:
1. Pure Parsing - Extract what the command does from man pages
2. Pure Safety - Focused safety analysis only
3. Logic LLM Review - Comprehensive logical analysis
4. Encoding Review - LLM determines encoding pathways
5. Algorithmic Encoding - Final binary descriptor generation
"""

import subprocess
import json
import time
import re
import os
import struct
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class RiskLevel(Enum):
    SAFE = "SAFE"
    LOW_RISK = "LOW_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"

@dataclass
class StageResult:
    """Result from each processing stage"""
    stage_name: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    processing_time_ms: int = 0

@dataclass
class CommandAnalysis:
    """Complete multi-stage analysis results"""
    command: str
    stages: Dict[str, StageResult] = field(default_factory=dict)
    final_risk: Optional[RiskLevel] = None
    final_capabilities: List[str] = field(default_factory=list)
    binary_descriptor: Optional[bytes] = None
    man_page_found: bool = False

class MultiStageTCPRefinery:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.man_cache = {}
        self.analyses = {}
        self.stats = {
            "total_processed": 0,
            "stage_successes": {},
            "stage_failures": {},
            "risk_distribution": {}
        }
        
    def get_man_page(self, command: str) -> Optional[str]:
        """Extract man page content for a command"""
        if command in self.man_cache:
            return self.man_cache[command]
        
        try:
            result = subprocess.run(
                ["man", command],
                capture_output=True,
                text=True,
                env={**os.environ, "MANPAGER": "cat", "MANWIDTH": "80"}
            )
            
            if result.returncode == 0 and result.stdout:
                man_text = result.stdout
                man_text = re.sub(r'.\x08', '', man_text)  # Remove backspace sequences
                self.man_cache[command] = man_text
                return man_text
                
        except Exception as e:
            print(f"   ⚠️ Error getting man page for {command}: {e}")
        
        return None
    
    def extract_man_sections(self, man_page: str) -> Dict[str, str]:
        """Extract specific sections from man page"""
        sections = {
            "name": "",
            "synopsis": "",
            "description": "",
            "options": "",
            "examples": "",
            "warnings": "",
            "security": "",
            "see_also": ""
        }
        
        current_section = None
        lines = man_page.split('\n')
        
        for line in lines:
            line_upper = line.strip().upper()
            
            # Detect section headers
            if line_upper in ["NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "FLAGS", 
                             "EXAMPLES", "WARNINGS", "CAUTION", "SECURITY", "BUGS", "SEE ALSO"]:
                if "NAME" in line_upper:
                    current_section = "name"
                elif "SYNOPSIS" in line_upper:
                    current_section = "synopsis"
                elif "DESCRIPTION" in line_upper:
                    current_section = "description"
                elif any(opt in line_upper for opt in ["OPTIONS", "FLAGS"]):
                    current_section = "options"
                elif "EXAMPLE" in line_upper:
                    current_section = "examples"
                elif any(warn in line_upper for warn in ["WARNING", "CAUTION", "BUGS"]):
                    current_section = "warnings"
                elif "SECURITY" in line_upper:
                    current_section = "security"
                elif "SEE ALSO" in line_upper:
                    current_section = "see_also"
                continue
            
            # Collect section content
            if current_section and line.strip():
                sections[current_section] += line + "\n"
                if len(sections[current_section]) > 1000:
                    sections[current_section] = sections[current_section][:1000] + "..."
        
        return sections
    
    def ollama_request(self, prompt: str, model: str = "tinyllama:latest", 
                      temperature: float = 0.1, max_tokens: int = 200) -> Optional[str]:
        """Make a request to Ollama"""
        try:
            cmd = [
                "curl", "-s", "-X", "POST",
                f"{self.ollama_url}/api/generate",
                "-d", json.dumps({
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "seed": 42
                    }
                })
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response.get("response", "")
                
        except Exception as e:
            print(f"   ❌ Ollama error: {e}")
        
        return None
    
    # STAGE 1: Pure Parsing
    def stage1_pure_parsing(self, command: str, man_sections: Dict[str, str]) -> StageResult:
        """Stage 1: Extract what the command does from documentation"""
        start_time = time.time()
        
        prompt = f"""Based on the man page documentation, describe what the '{command}' command does.

NAME: {man_sections['name'][:200]}
SYNOPSIS: {man_sections['synopsis'][:300]}
DESCRIPTION: {man_sections['description'][:500]}

Provide a factual description of:
1. Primary function (what it does)
2. Main operations it performs
3. Type of command (file operation, network, system, etc.)
4. Common use cases

Be objective and factual. No safety assessment. Keep under 150 words."""

        response = self.ollama_request(prompt, temperature=0.1)
        
        if response:
            # Extract structured information
            data = {
                "description": response,
                "command_type": self._extract_command_type(response),
                "operations": self._extract_operations(response),
                "use_cases": self._extract_use_cases(response)
            }
            
            return StageResult(
                stage_name="pure_parsing",
                success=True,
                data=data,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        return StageResult(
            stage_name="pure_parsing",
            success=False,
            data={},
            error="Failed to parse command functionality",
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
    
    # STAGE 2: Pure Safety
    def stage2_pure_safety(self, command: str, man_sections: Dict[str, str], 
                          parsing_result: Dict[str, Any]) -> StageResult:
        """Stage 2: Focused safety analysis only"""
        start_time = time.time()
        
        prompt = f"""Analyze the safety implications of the '{command}' command.

Command Function: {parsing_result.get('description', 'Unknown')}

Documentation Warnings:
{man_sections['warnings'][:300] if man_sections['warnings'] else 'None found'}

Security Notes:
{man_sections['security'][:300] if man_sections['security'] else 'None found'}

Assess ONLY safety concerns:
1. Can it destroy/delete data?
2. Can it modify system files?
3. Can it compromise security?
4. Does it require elevated privileges?
5. What are the risks of misuse?

Categorize risk as: SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, or CRITICAL
Explain your reasoning. Keep under 100 words."""

        response = self.ollama_request(prompt, temperature=0.1)
        
        if response:
            risk = self._extract_risk_level(response)
            
            data = {
                "risk_level": risk,
                "safety_analysis": response,
                "can_destroy_data": self._check_destructive(response),
                "requires_privileges": self._check_privileges(response),
                "security_concerns": self._extract_security_concerns(response)
            }
            
            return StageResult(
                stage_name="pure_safety",
                success=True,
                data=data,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        return StageResult(
            stage_name="pure_safety",
            success=False,
            data={},
            error="Failed to assess safety",
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
    
    # STAGE 3: Logic LLM Review
    def stage3_logic_review(self, command: str, parsing_data: Dict[str, Any], 
                           safety_data: Dict[str, Any]) -> StageResult:
        """Stage 3: Comprehensive logical analysis"""
        start_time = time.time()
        
        prompt = f"""Perform logical analysis of the '{command}' command.

Function: {parsing_data.get('description', 'Unknown')}
Safety Assessment: {safety_data.get('risk_level', 'Unknown')} - {safety_data.get('safety_analysis', '')}

Analyze:
1. Is the safety assessment consistent with the functionality?
2. Are there edge cases or special flags that change risk?
3. What capabilities does this command truly have?
4. Is the risk assessment too high or too low?
5. What context affects its safety?

Provide logical reasoning and any corrections needed. Keep under 150 words."""

        response = self.ollama_request(prompt, temperature=0.2)
        
        if response:
            # Re-evaluate risk based on logical analysis
            revised_risk = self._extract_risk_level(response)
            if revised_risk == "UNKNOWN":
                revised_risk = safety_data.get('risk_level', 'MEDIUM_RISK')
            
            data = {
                "logical_analysis": response,
                "revised_risk": revised_risk,
                "edge_cases": self._extract_edge_cases(response),
                "true_capabilities": self._extract_capabilities_from_logic(response),
                "context_factors": self._extract_context_factors(response)
            }
            
            return StageResult(
                stage_name="logic_review",
                success=True,
                data=data,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        return StageResult(
            stage_name="logic_review",
            success=False,
            data={},
            error="Failed logical review",
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
    
    # STAGE 4: Encoding Review
    def stage4_encoding_review(self, command: str, all_previous_data: Dict[str, Any]) -> StageResult:
        """Stage 4: LLM determines encoding pathways"""
        start_time = time.time()
        
        capabilities_found = set()
        # Gather capabilities from all stages
        if 'parsing' in all_previous_data:
            capabilities_found.update(all_previous_data['parsing'].get('operations', []))
        if 'logic' in all_previous_data:
            capabilities_found.update(all_previous_data['logic'].get('true_capabilities', []))
        
        prompt = f"""Determine binary encoding pathways for '{command}'.

Risk Level: {all_previous_data.get('logic', {}).get('revised_risk', 'UNKNOWN')}
Capabilities Found: {list(capabilities_found)}

Map to these binary flags:
- FILE_OPS (0x0100): File/directory operations
- NETWORK (0x0200): Network access
- SUDO (0x0400): Requires elevated privileges  
- DESTRUCTIVE (0x0800): Can destroy data
- SYSTEM (0x1000): System modification
- PROCESS (0x2000): Process control

Which flags should be set? Consider:
1. Primary capabilities
2. Secondary effects
3. Potential misuse vectors
4. Special flags or modes

List each flag that should be set and why. Be precise."""

        response = self.ollama_request(prompt, temperature=0.1)
        
        if response:
            flags_to_set = []
            response_lower = response.lower()
            
            if "file_ops" in response_lower or "0x0100" in response_lower:
                flags_to_set.append("FILE_OPS")
            if "network" in response_lower or "0x0200" in response_lower:
                flags_to_set.append("NETWORK")
            if "sudo" in response_lower or "0x0400" in response_lower:
                flags_to_set.append("SUDO")
            if "destructive" in response_lower or "0x0800" in response_lower:
                flags_to_set.append("DESTRUCTIVE")
            if "system" in response_lower or "0x1000" in response_lower:
                flags_to_set.append("SYSTEM")
            if "process" in response_lower or "0x2000" in response_lower:
                flags_to_set.append("PROCESS")
            
            data = {
                "encoding_analysis": response,
                "flags_to_set": flags_to_set,
                "encoding_rationale": response
            }
            
            return StageResult(
                stage_name="encoding_review",
                success=True,
                data=data,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        return StageResult(
            stage_name="encoding_review",
            success=False,
            data={},
            error="Failed encoding review",
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
    
    # STAGE 5: Algorithmic Encoding
    def stage5_algorithmic_encoding(self, command: str, risk: str, 
                                   capabilities: List[str]) -> StageResult:
        """Stage 5: Final binary descriptor generation"""
        start_time = time.time()
        
        # Risk level mapping
        risk_flags = {
            "SAFE": 0x01,
            "LOW_RISK": 0x02,
            "MEDIUM_RISK": 0x04,
            "HIGH_RISK": 0x08,
            "CRITICAL": 0x10
        }
        
        # Capability flags
        cap_flags = 0
        cap_mapping = {
            "FILE_OPS": 0x0100,
            "NETWORK": 0x0200,
            "SUDO": 0x0400,
            "DESTRUCTIVE": 0x0800,
            "SYSTEM": 0x1000,
            "PROCESS": 0x2000
        }
        
        for cap in capabilities:
            if cap in cap_mapping:
                cap_flags |= cap_mapping[cap]
        
        # Build descriptor
        magic = b'TCP\x02'
        version = struct.pack('>H', 2)
        cmd_hash = hashlib.md5(command.encode()).digest()[:4]
        security_flags = struct.pack('>I', risk_flags.get(risk, 0x04) | cap_flags)
        
        # Performance placeholders
        exec_time = struct.pack('>I', 100)
        memory = struct.pack('>H', 10)
        output = struct.pack('>H', 1)
        
        # Calculate CRC
        data = magic + version + cmd_hash + security_flags + exec_time + memory + output
        crc = struct.pack('>H', sum(data) & 0xFFFF)
        
        descriptor = data + crc
        
        return StageResult(
            stage_name="algorithmic_encoding",
            success=True,
            data={
                "binary_descriptor": descriptor.hex(),
                "risk_encoded": risk,
                "capabilities_encoded": capabilities,
                "descriptor_size": len(descriptor)
            },
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
    
    # Helper methods for extraction
    def _extract_command_type(self, text: str) -> str:
        """Extract command type from description"""
        text_lower = text.lower()
        if any(word in text_lower for word in ["file", "directory", "filesystem"]):
            return "file_operation"
        elif any(word in text_lower for word in ["network", "connection", "socket"]):
            return "network"
        elif any(word in text_lower for word in ["process", "pid", "signal"]):
            return "process_control"
        elif any(word in text_lower for word in ["system", "kernel", "boot"]):
            return "system"
        else:
            return "utility"
    
    def _extract_operations(self, text: str) -> List[str]:
        """Extract operations from description"""
        operations = []
        text_lower = text.lower()
        
        operation_keywords = {
            "read": ["read", "display", "show", "list"],
            "write": ["write", "create", "modify", "update"],
            "delete": ["delete", "remove", "erase", "destroy"],
            "execute": ["execute", "run", "launch", "start"],
            "network": ["connect", "download", "upload", "transfer"],
            "process": ["kill", "terminate", "signal", "control"]
        }
        
        for op, keywords in operation_keywords.items():
            if any(kw in text_lower for kw in keywords):
                operations.append(op)
        
        return operations
    
    def _extract_use_cases(self, text: str) -> List[str]:
        """Extract common use cases"""
        # Simple extraction - could be enhanced
        use_cases = []
        if "commonly used" in text.lower():
            # Extract sentence with "commonly used"
            sentences = text.split('.')
            for s in sentences:
                if "commonly used" in s.lower():
                    use_cases.append(s.strip())
        return use_cases[:3]  # Limit to 3
    
    def _extract_risk_level(self, text: str) -> str:
        """Extract risk level from text"""
        text_upper = text.upper()
        
        for level in ["CRITICAL", "HIGH_RISK", "MEDIUM_RISK", "LOW_RISK", "SAFE"]:
            if level.replace("_", " ") in text_upper or level in text_upper:
                return level
        
        # Infer from keywords
        danger_keywords = ["destroy", "delete", "format", "wipe", "kill", "erase"]
        if any(kw in text_upper for kw in danger_keywords):
            return "HIGH_RISK"
        
        return "UNKNOWN"
    
    def _check_destructive(self, text: str) -> bool:
        """Check if command can destroy data"""
        destructive_keywords = ["destroy", "delete", "remove", "erase", "wipe", "format"]
        return any(kw in text.lower() for kw in destructive_keywords)
    
    def _check_privileges(self, text: str) -> bool:
        """Check if command requires privileges"""
        privilege_keywords = ["root", "sudo", "administrator", "privilege", "elevated"]
        return any(kw in text.lower() for kw in privilege_keywords)
    
    def _extract_security_concerns(self, text: str) -> List[str]:
        """Extract security concerns"""
        concerns = []
        text_lower = text.lower()
        
        if "security" in text_lower or "vulnerability" in text_lower:
            # Extract sentences with security keywords
            sentences = text.split('.')
            for s in sentences:
                if any(kw in s.lower() for kw in ["security", "vulnerability", "exploit"]):
                    concerns.append(s.strip())
        
        return concerns[:2]  # Limit to 2
    
    def _extract_edge_cases(self, text: str) -> List[str]:
        """Extract edge cases from logical analysis"""
        edge_cases = []
        if "edge case" in text.lower() or "special" in text.lower():
            sentences = text.split('.')
            for s in sentences:
                if any(kw in s.lower() for kw in ["edge", "special", "flag", "option"]):
                    edge_cases.append(s.strip())
        return edge_cases[:2]
    
    def _extract_capabilities_from_logic(self, text: str) -> List[str]:
        """Extract true capabilities from logical analysis"""
        capabilities = []
        text_lower = text.lower()
        
        cap_keywords = {
            "file operations": ["file", "directory", "filesystem"],
            "network access": ["network", "internet", "connection"],
            "process control": ["process", "kill", "signal"],
            "system modification": ["system", "kernel", "configuration"],
            "data destruction": ["destroy", "delete", "remove"]
        }
        
        for cap, keywords in cap_keywords.items():
            if any(kw in text_lower for kw in keywords):
                capabilities.append(cap)
        
        return capabilities
    
    def _extract_context_factors(self, text: str) -> List[str]:
        """Extract context factors"""
        factors = []
        if "context" in text.lower() or "depends" in text.lower():
            sentences = text.split('.')
            for s in sentences:
                if any(kw in s.lower() for kw in ["context", "depends", "when", "if"]):
                    factors.append(s.strip())
        return factors[:2]
    
    # Main processing method
    def process_command(self, command: str) -> CommandAnalysis:
        """Process a command through all stages"""
        print(f"\n🔧 Processing '{command}' through multi-stage pipeline")
        analysis = CommandAnalysis(command=command)
        
        # Get man page
        man_page = self.get_man_page(command)
        if not man_page:
            print(f"   ❌ No man page found for {command}")
            analysis.man_page_found = False
            return analysis
        
        analysis.man_page_found = True
        man_sections = self.extract_man_sections(man_page)
        
        # Stage 1: Pure Parsing
        print("   📝 Stage 1: Pure Parsing...")
        stage1 = self.stage1_pure_parsing(command, man_sections)
        analysis.stages["parsing"] = stage1
        if not stage1.success:
            print(f"      ❌ Failed: {stage1.error}")
            return analysis
        print(f"      ✅ Type: {stage1.data.get('command_type', 'unknown')}")
        
        # Stage 2: Pure Safety
        print("   🛡️ Stage 2: Pure Safety Analysis...")
        stage2 = self.stage2_pure_safety(command, man_sections, stage1.data)
        analysis.stages["safety"] = stage2
        if not stage2.success:
            print(f"      ❌ Failed: {stage2.error}")
            return analysis
        print(f"      ✅ Risk: {stage2.data.get('risk_level', 'unknown')}")
        
        # Stage 3: Logic Review
        print("   🧠 Stage 3: Logic Review...")
        stage3 = self.stage3_logic_review(command, stage1.data, stage2.data)
        analysis.stages["logic"] = stage3
        if not stage3.success:
            print(f"      ❌ Failed: {stage3.error}")
            return analysis
        print(f"      ✅ Revised Risk: {stage3.data.get('revised_risk', 'unknown')}")
        
        # Stage 4: Encoding Review
        print("   🔤 Stage 4: Encoding Review...")
        all_data = {
            "parsing": stage1.data,
            "safety": stage2.data,
            "logic": stage3.data
        }
        stage4 = self.stage4_encoding_review(command, all_data)
        analysis.stages["encoding"] = stage4
        if not stage4.success:
            print(f"      ❌ Failed: {stage4.error}")
            return analysis
        print(f"      ✅ Flags: {', '.join(stage4.data.get('flags_to_set', []))}")
        
        # Stage 5: Algorithmic Encoding
        print("   💾 Stage 5: Algorithmic Encoding...")
        final_risk = stage3.data.get('revised_risk', 'MEDIUM_RISK')
        final_capabilities = stage4.data.get('flags_to_set', [])
        
        stage5 = self.stage5_algorithmic_encoding(command, final_risk, final_capabilities)
        analysis.stages["binary"] = stage5
        if not stage5.success:
            print(f"      ❌ Failed: {stage5.error}")
            return analysis
        print(f"      ✅ Descriptor: {stage5.data.get('binary_descriptor', '')[:32]}...")
        
        # Set final values
        analysis.final_risk = RiskLevel(final_risk)
        analysis.final_capabilities = final_capabilities
        analysis.binary_descriptor = bytes.fromhex(stage5.data.get('binary_descriptor', ''))
        
        # Update stats
        self.stats["total_processed"] += 1
        self.stats["risk_distribution"][final_risk] = self.stats["risk_distribution"].get(final_risk, 0) + 1
        
        return analysis
    
    def batch_process(self, commands: List[str]) -> Dict[str, CommandAnalysis]:
        """Process multiple commands"""
        print("🏭 Multi-Stage TCP Refinery")
        print("=" * 60)
        
        start_time = time.time()
        
        for i, command in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] Command: {command}")
            analysis = self.process_command(command)
            self.analyses[command] = analysis
            
            # Show progress
            if i % 5 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                print(f"\n📊 Progress: {i}/{len(commands)} ({rate:.1f} cmd/min)")
        
        return self.analyses
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "=" * 60)
        print("📊 Multi-Stage Refinery Report")
        print("=" * 60)
        
        print(f"\nTotal Processed: {self.stats['total_processed']}")
        
        # Success rate by stage
        print("\n🎯 Stage Success Rates:")
        stage_names = ["parsing", "safety", "logic", "encoding", "binary"]
        for stage in stage_names:
            successes = sum(1 for a in self.analyses.values() 
                          if stage in a.stages and a.stages[stage].success)
            total = len(self.analyses)
            rate = (successes / total * 100) if total > 0 else 0
            print(f"   {stage:<15} {successes}/{total} ({rate:.1f}%)")
        
        # Risk distribution
        print("\n⚠️ Risk Distribution:")
        for risk, count in sorted(self.stats["risk_distribution"].items()):
            percentage = (count / self.stats["total_processed"] * 100) if self.stats["total_processed"] > 0 else 0
            print(f"   {risk:<15} {count:>3} ({percentage:.1f}%)")
        
        # Save detailed results
        self.save_results()
    
    def save_results(self):
        """Save analysis results"""
        output = {
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_commands": len(self.analyses),
                "pipeline_stages": 5,
                "stats": self.stats
            },
            "commands": {}
        }
        
        for cmd, analysis in self.analyses.items():
            output["commands"][cmd] = {
                "man_page_found": analysis.man_page_found,
                "final_risk": analysis.final_risk.value if analysis.final_risk else "UNKNOWN",
                "final_capabilities": analysis.final_capabilities,
                "binary_descriptor": analysis.binary_descriptor.hex() if analysis.binary_descriptor else "",
                "stages": {
                    name: {
                        "success": stage.success,
                        "error": stage.error,
                        "processing_time_ms": stage.processing_time_ms,
                        "data": stage.data
                    }
                    for name, stage in analysis.stages.items()
                }
            }
        
        with open("multi_stage_refinery_results.json", 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Results saved to: multi_stage_refinery_results.json")
    
    def demo(self):
        """Run demo with critical commands"""
        print("🔬 TCP Multi-Stage Refinery Demo")
        print("Systematic 5-stage analysis pipeline")
        print("=" * 60)
        
        # Focus on commands that need accurate assessment
        critical_commands = [
            # Definitely dangerous
            "dd", "mkfs", "fdisk", "shred", "rm",
            # System critical
            "sudo", "chown", "chmod", "kill", "systemctl",
            # Network tools
            "nc", "nmap", "tcpdump", "iptables",
            # Safe utilities
            "ls", "cat", "echo", "date", "whoami"
        ]
        
        print(f"\n📋 Testing {len(critical_commands)} critical commands...")
        
        self.batch_process(critical_commands)
        self.generate_report()
        
        # Show example analysis
        if "dd" in self.analyses:
            print("\n🔍 Example: 'dd' command analysis")
            dd_analysis = self.analyses["dd"]
            print(f"   Final Risk: {dd_analysis.final_risk.value if dd_analysis.final_risk else 'UNKNOWN'}")
            print(f"   Capabilities: {', '.join(dd_analysis.final_capabilities)}")
            if "safety" in dd_analysis.stages:
                print(f"   Safety Analysis: {dd_analysis.stages['safety'].data.get('safety_analysis', '')[:150]}...")

if __name__ == "__main__":
    refinery = MultiStageTCPRefinery()
    refinery.demo()