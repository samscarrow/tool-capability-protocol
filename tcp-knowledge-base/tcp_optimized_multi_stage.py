#!/usr/bin/env python3
"""
TCP Optimized Multi-Stage Refinery - Uses best models for each stage
Stage-specific model selection for maximum accuracy
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
    model_used: Optional[str] = None


@dataclass
class CommandAnalysis:
    """Complete multi-stage analysis results"""

    command: str
    stages: Dict[str, StageResult] = field(default_factory=dict)
    final_risk: Optional[RiskLevel] = None
    final_capabilities: List[str] = field(default_factory=list)
    binary_descriptor: Optional[bytes] = None
    man_page_found: bool = False


class OptimizedMultiStageTCPRefinery:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.man_cache = {}
        self.analyses = {}

        # Model selection by stage for optimal performance
        self.stage_models = {
            "parsing": "llama3.2:latest",  # Good for factual extraction
            "safety": "llama3:latest",  # Good for security analysis
            "logic": "mistral:latest",  # Strong reasoning capabilities
            "encoding": "llama3.2:latest",  # Good for technical mapping
        }

        # Comprehensive rule-based command classification
        # SAFE commands - read-only operations with no destructive capability
        self.safe_commands = {
            "ls",
            "cat",
            "echo",
            "pwd",
            "date",
            "whoami",
            "id",
            "uptime",
            "df",
            "free",
            "ps",
            "top",
            "which",
            "whereis",
            "file",
            "wc",
            "head",
            "tail",
            "grep",
            "awk",
            "sed",
            "sort",
            "uniq",
            "cut",
            "less",
            "more",
            "find",
            "locate",
            "type",
            "help",
            "man",
            "history",
            "alias",
            "env",
            "printenv",
            "uname",
            "hostname",
        }

        # LOW_RISK commands - minor system changes, reversible
        self.low_risk_commands = {
            "mkdir",
            "touch",
            "ln",
            "symlink",
            "cd",
            "pushd",
            "popd",
            "export",
            "unset",
            "source",
            "eval",
            "test",
            "true",
            "false",
        }

        # MEDIUM_RISK commands - system changes requiring caution
        self.medium_risk_commands = {
            "chmod",
            "chown",
            "chgrp",
            "kill",
            "killall",
            "jobs",
            "bg",
            "fg",
            "nohup",
            "screen",
            "tmux",
            "crontab",
            "at",
            "batch",
        }

        # HIGH_RISK commands - potential for significant damage
        self.high_risk_commands = {
            "rm",
            "mv",
            "cp",
            "sudo",
            "su",
            "mount",
            "umount",
            "fsck",
            "systemctl",
            "service",
            "iptables",
            "firewall-cmd",
            "passwd",
            "usermod",
            "groupmod",
            "useradd",
            "userdel",
            "groupadd",
            "groupdel",
        }

        # CRITICAL commands - extreme danger, can destroy systems
        self.critical_commands = {
            "dd",
            "shred",
            "wipefs",
            "mkfs",
            "fdisk",
            "parted",
            "mkswap",
            "swapon",
            "swapoff",
            "reboot",
            "shutdown",
            "halt",
            "init",
            "poweroff",
            "telinit",
            "runlevel",
            "format",
            "deltree",
        }

        self.stats = {
            "total_processed": 0,
            "rule_overrides": 0,
            "model_accuracy": {},
            "risk_distribution": {},
        }

    def _get_rule_based_flags(
        self, command: str, risk_level: str
    ) -> Optional[List[str]]:
        """Get capability flags based on known command behavior patterns"""
        # Define known capability patterns

        # Read-only commands (SAFE) - minimal flags
        if command in self.safe_commands:
            if command in ["ls", "pwd", "date", "whoami", "id", "uptime"]:
                return []  # No special capabilities
            elif command in ["cat", "head", "tail", "less", "more"]:
                return ["FILE_OPS"]  # Only file reading
            elif command in ["ps", "top", "free", "df"]:
                return ["SYSTEM"]  # System information only
            else:
                return ["FILE_OPS"]  # Default safe file operations

        # Commands that modify files but are generally safe
        elif command in self.low_risk_commands:
            if command in ["mkdir", "touch"]:
                return ["FILE_OPS"]
            elif command in ["export", "unset"]:
                return ["SYSTEM"]
            else:
                return ["FILE_OPS"]

        # Commands with moderate system impact
        elif command in self.medium_risk_commands:
            if command in ["chmod", "chown", "chgrp"]:
                return ["FILE_OPS", "SUDO"]
            elif command in ["kill", "killall"]:
                return ["PROCESS", "SUDO"]
            else:
                return ["FILE_OPS", "SYSTEM"]

        # High-risk commands
        elif command in self.high_risk_commands:
            if command == "rm":
                return ["FILE_OPS", "DESTRUCTIVE"]
            elif command in ["mv", "cp"]:
                return ["FILE_OPS", "DESTRUCTIVE"]
            elif command in ["sudo", "su"]:
                return ["SUDO", "SYSTEM", "PROCESS"]
            elif command in ["mount", "umount"]:
                return ["SYSTEM", "SUDO"]
            else:
                return ["FILE_OPS", "DESTRUCTIVE", "SUDO"]

        # Critical commands
        elif command in self.critical_commands:
            if command == "dd":
                return ["FILE_OPS", "DESTRUCTIVE", "SYSTEM"]
            elif command in ["shutdown", "reboot", "halt"]:
                return ["SYSTEM", "SUDO"]
            else:
                return ["FILE_OPS", "DESTRUCTIVE", "SYSTEM", "SUDO"]

        return None  # Use LLM for unknown commands

    def get_best_model(self, stage: str) -> str:
        """Get the best model for a specific stage"""
        return self.stage_models.get(stage, "llama3:latest")

    def get_man_page(self, command: str) -> Optional[str]:
        """Extract man page content for a command"""
        if command in self.man_cache:
            return self.man_cache[command]

        try:
            result = subprocess.run(
                ["man", command],
                capture_output=True,
                text=True,
                env={**os.environ, "MANPAGER": "cat", "MANWIDTH": "80"},
            )

            if result.returncode == 0 and result.stdout:
                man_text = result.stdout
                man_text = re.sub(r".\x08", "", man_text)  # Remove backspace sequences
                # Limit to relevant sections for LLM processing
                man_text = man_text[:3000]  # Increased for better context
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
            "see_also": "",
        }

        current_section = None
        lines = man_page.split("\n")

        for line in lines:
            line_upper = line.strip().upper()

            # Detect section headers
            if line_upper in [
                "NAME",
                "SYNOPSIS",
                "DESCRIPTION",
                "OPTIONS",
                "FLAGS",
                "EXAMPLES",
                "WARNINGS",
                "CAUTION",
                "SECURITY",
                "BUGS",
                "SEE ALSO",
            ]:
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
                if len(sections[current_section]) > 800:
                    sections[current_section] = sections[current_section][:800] + "..."

        return sections

    def ollama_request(
        self, prompt: str, model: str, temperature: float = 0.1, max_tokens: int = 300
    ) -> Optional[str]:
        """Make a request to Ollama with specified model"""
        try:
            cmd = [
                "curl",
                "-s",
                "-X",
                "POST",
                f"{self.ollama_url}/api/generate",
                "-d",
                json.dumps(
                    {
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                            "seed": 42,
                        },
                    }
                ),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                response = json.loads(result.stdout)
                return response.get("response", "")

        except Exception as e:
            print(f"   ❌ Ollama error with {model}: {e}")

        return None

    # STAGE 1: Pure Parsing (llama3.2)
    def stage1_pure_parsing(
        self, command: str, man_sections: Dict[str, str]
    ) -> StageResult:
        """Stage 1: Extract what the command does using llama3.2"""
        start_time = time.time()
        model = self.get_best_model("parsing")

        prompt = f"""Analyze the '{command}' command based on its official documentation.

NAME: {man_sections['name'][:150]}
SYNOPSIS: {man_sections['synopsis'][:200]}
DESCRIPTION: {man_sections['description'][:400]}

Extract factual information:
1. What does this command do? (primary function)
2. What operations can it perform?
3. What type of command is it? (file, network, system, process)
4. What are its main capabilities?

Be precise and factual. No safety assessment. Keep under 200 words."""

        response = self.ollama_request(prompt, model, temperature=0.1, max_tokens=250)

        if response:
            data = {
                "description": response,
                "command_type": self._extract_command_type(response),
                "operations": self._extract_operations(response),
                "primary_function": self._extract_primary_function(response),
            }

            return StageResult(
                stage_name="pure_parsing",
                success=True,
                data=data,
                processing_time_ms=int((time.time() - start_time) * 1000),
                model_used=model,
            )

        return StageResult(
            stage_name="pure_parsing",
            success=False,
            data={},
            error="Failed to parse command functionality",
            processing_time_ms=int((time.time() - start_time) * 1000),
            model_used=model,
        )

    # STAGE 2: Pure Safety (llama3:8b-instruct-fp16)
    def stage2_pure_safety(
        self, command: str, man_sections: Dict[str, str], parsing_result: Dict[str, Any]
    ) -> StageResult:
        """Stage 2: Focused safety analysis using best instruct model"""
        start_time = time.time()
        model = self.get_best_model("safety")

        # Check for rule-based classification first (comprehensive)
        rule_risk = None
        if command in self.safe_commands:
            rule_risk = "SAFE"
        elif command in self.low_risk_commands:
            rule_risk = "LOW_RISK"
        elif command in self.medium_risk_commands:
            rule_risk = "MEDIUM_RISK"
        elif command in self.high_risk_commands:
            rule_risk = "HIGH_RISK"
        elif command in self.critical_commands:
            rule_risk = "CRITICAL"

        if rule_risk:
            self.stats["rule_overrides"] += 1

            data = {
                "risk_level": rule_risk,
                "safety_analysis": f"RULE-BASED CLASSIFICATION: '{command}' is classified as {rule_risk} based on known behavior patterns",
                "rule_override": True,
                "can_destroy_data": rule_risk in ["CRITICAL", "HIGH_RISK"],
                "requires_privileges": rule_risk
                in ["CRITICAL", "HIGH_RISK", "MEDIUM_RISK"],
                "security_concerns": [f"Rule-based classification: {rule_risk}"],
            }

            return StageResult(
                stage_name="pure_safety",
                success=True,
                data=data,
                processing_time_ms=int((time.time() - start_time) * 1000),
                model_used="rule_override",
            )

        # Enhanced safety prompt for instruct model
        prompt = f"""You are a cybersecurity expert analyzing Unix command safety.

Command: '{command}'
Function: {parsing_result.get('description', 'Unknown')[:300]}

Documentation Warnings:
{man_sections['warnings'][:200] if man_sections['warnings'] else 'None documented'}

CRITICAL SAFETY ANALYSIS:
Assess these specific risks:
1. Data destruction: Can it permanently delete/overwrite data?
2. System damage: Can it damage the operating system?
3. Security bypass: Can it escalate privileges or bypass security?
4. Irreversible changes: Are its effects permanent?
5. Requires root: Does it need administrator privileges?

Risk Categories:
- SAFE: Read-only operations, no system impact
- LOW_RISK: Minor modifications, easily reversible
- MEDIUM_RISK: Significant changes, some recovery possible
- HIGH_RISK: Major system changes, difficult recovery
- CRITICAL: Can destroy entire systems, data loss

Provide risk level and explain WHY. Be conservative with security."""

        response = self.ollama_request(prompt, model, temperature=0.1, max_tokens=200)

        if response:
            risk = self._extract_risk_level_enhanced(response)

            data = {
                "risk_level": risk,
                "safety_analysis": response,
                "rule_override": False,
                "can_destroy_data": self._check_destructive_enhanced(response),
                "requires_privileges": self._check_privileges_enhanced(response),
                "security_concerns": self._extract_security_concerns_enhanced(response),
            }

            return StageResult(
                stage_name="pure_safety",
                success=True,
                data=data,
                processing_time_ms=int((time.time() - start_time) * 1000),
                model_used=model,
            )

        return StageResult(
            stage_name="pure_safety",
            success=False,
            data={},
            error="Failed to assess safety",
            processing_time_ms=int((time.time() - start_time) * 1000),
            model_used=model,
        )

    # Enhanced helper methods
    def _extract_risk_level_enhanced(self, text: str) -> str:
        """Enhanced risk level extraction with better patterns"""
        text_upper = text.upper()

        # Direct mentions
        if "CRITICAL" in text_upper:
            return "CRITICAL"
        elif "HIGH_RISK" in text_upper or "HIGH RISK" in text_upper:
            return "HIGH_RISK"
        elif "MEDIUM_RISK" in text_upper or "MEDIUM RISK" in text_upper:
            return "MEDIUM_RISK"
        elif "LOW_RISK" in text_upper or "LOW RISK" in text_upper:
            return "LOW_RISK"
        elif "SAFE" in text_upper:
            return "SAFE"

        # Infer from dangerous keywords
        critical_keywords = [
            "destroy",
            "overwrite",
            "format",
            "wipe",
            "erase",
            "delete permanently",
        ]
        high_risk_keywords = ["delete", "remove", "kill", "terminate", "modify system"]

        if any(kw.upper() in text_upper for kw in critical_keywords):
            return "CRITICAL"
        elif any(kw.upper() in text_upper for kw in high_risk_keywords):
            return "HIGH_RISK"

        return "MEDIUM_RISK"  # Conservative default

    def _check_destructive_enhanced(self, text: str) -> bool:
        """Enhanced destructive capability detection"""
        destructive_patterns = [
            "destroy",
            "delete",
            "remove",
            "erase",
            "wipe",
            "format",
            "overwrite",
            "truncate",
            "shred",
            "zero out",
            "permanently",
        ]
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in destructive_patterns)

    def _check_privileges_enhanced(self, text: str) -> bool:
        """Enhanced privilege requirement detection"""
        privilege_patterns = [
            "root",
            "sudo",
            "administrator",
            "privilege",
            "elevated",
            "superuser",
            "admin",
            "requires root",
            "must be root",
        ]
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in privilege_patterns)

    def _extract_security_concerns_enhanced(self, text: str) -> List[str]:
        """Enhanced security concern extraction"""
        concerns = []
        text_lower = text.lower()

        concern_patterns = {
            "data loss": ["data loss", "lose data", "permanent deletion"],
            "system damage": ["system damage", "corrupt", "break system"],
            "privilege escalation": ["privilege", "escalation", "bypass security"],
            "irreversible": ["irreversible", "permanent", "cannot undo"],
        }

        for concern_type, patterns in concern_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                concerns.append(concern_type)

        return concerns

    def _extract_primary_function(self, text: str) -> str:
        """Extract primary function from description"""
        text_lower = text.lower()

        if "copy" in text_lower or "backup" in text_lower:
            return "data_copy"
        elif "delete" in text_lower or "remove" in text_lower:
            return "data_deletion"
        elif "format" in text_lower or "filesystem" in text_lower:
            return "filesystem_ops"
        elif "network" in text_lower or "connection" in text_lower:
            return "network_ops"
        elif "process" in text_lower or "signal" in text_lower:
            return "process_control"
        else:
            return "utility"

    # Continue with other stages using appropriate models...
    def stage3_logic_review(
        self, command: str, parsing_data: Dict[str, Any], safety_data: Dict[str, Any]
    ) -> StageResult:
        """Stage 3: Logic review using Mistral"""
        start_time = time.time()
        model = self.get_best_model("logic")

        prompt = f"""Logical analysis of '{command}' command safety assessment.

Function: {parsing_data.get('description', 'Unknown')[:200]}
Safety Assessment: {safety_data.get('risk_level', 'Unknown')}
Analysis: {safety_data.get('safety_analysis', '')[:300]}

Logical Review Questions:
1. Is the risk assessment consistent with the command's actual capabilities?
2. Are there dangerous flags or options not considered?
3. What context makes this command more/less dangerous?
4. Is the risk level appropriate given real-world usage?

Provide logical reasoning and any risk adjustments needed."""

        response = self.ollama_request(prompt, model, temperature=0.2, max_tokens=200)

        if response:
            # Logic review can adjust risk but not below rule overrides
            revised_risk = safety_data.get("risk_level", "MEDIUM_RISK")
            if not safety_data.get("rule_override", False):
                extracted_risk = self._extract_risk_level_enhanced(response)
                if extracted_risk != "UNKNOWN":
                    revised_risk = extracted_risk

            data = {
                "logical_analysis": response,
                "revised_risk": revised_risk,
                "logic_adjustments": self._extract_logic_adjustments(response),
                "context_factors": self._extract_context_factors(response),
            }

            return StageResult(
                stage_name="logic_review",
                success=True,
                data=data,
                processing_time_ms=int((time.time() - start_time) * 1000),
                model_used=model,
            )

        return StageResult(
            stage_name="logic_review",
            success=False,
            data={},
            error="Failed logical review",
            processing_time_ms=int((time.time() - start_time) * 1000),
            model_used=model,
        )

    def stage4_encoding_review(
        self, command: str, all_data: Dict[str, Any]
    ) -> StageResult:
        """Stage 4: Encoding review with rule-based capability flags"""
        start_time = time.time()
        model = self.get_best_model("encoding")

        final_risk = all_data.get("logic", {}).get("revised_risk", "MEDIUM_RISK")

        # Rule-based capability flag assignment
        rule_flags = self._get_rule_based_flags(command, final_risk)
        if rule_flags is not None:
            data = {
                "encoding_analysis": f"RULE-BASED FLAGS: '{command}' assigned flags based on known behavior patterns",
                "flags_to_set": rule_flags,
                "flag_justification": f"Rule-based assignment for {command} command",
            }

            return StageResult(
                stage_name="encoding_review",
                success=True,
                data=data,
                processing_time_ms=int((time.time() - start_time) * 1000),
                model_used="rule_override",
            )

        prompt = f"""Map '{command}' to binary capability flags.

Risk Level: {final_risk}
Primary Function: {all_data.get('parsing', {}).get('primary_function', 'unknown')}
Security Concerns: {all_data.get('safety', {}).get('security_concerns', [])}

Binary Flags Available:
- FILE_OPS (0x0100): File/directory operations
- NETWORK (0x0200): Network access
- SUDO (0x0400): Requires elevated privileges  
- DESTRUCTIVE (0x0800): Can destroy/delete data
- SYSTEM (0x1000): System configuration changes
- PROCESS (0x2000): Process control/signals

Which flags should be set? Consider:
- What the command actually does
- Security implications
- Privilege requirements
- Potential for data loss

List each applicable flag with justification."""

        response = self.ollama_request(prompt, model, temperature=0.1, max_tokens=200)

        if response:
            flags = self._extract_capability_flags(response, all_data)

            data = {
                "encoding_analysis": response,
                "flags_to_set": flags,
                "flag_justification": response,
            }

            return StageResult(
                stage_name="encoding_review",
                success=True,
                data=data,
                processing_time_ms=int((time.time() - start_time) * 1000),
                model_used=model,
            )

        return StageResult(
            stage_name="encoding_review",
            success=False,
            data={},
            error="Failed encoding review",
            processing_time_ms=int((time.time() - start_time) * 1000),
            model_used=model,
        )

    def _extract_capability_flags(
        self, response: str, all_data: Dict[str, Any]
    ) -> List[str]:
        """Enhanced capability flag extraction"""
        flags = []
        response_lower = response.lower()

        # Direct mentions in response
        if "file_ops" in response_lower or "file" in response_lower:
            flags.append("FILE_OPS")
        if "network" in response_lower:
            flags.append("NETWORK")
        if "sudo" in response_lower or "privilege" in response_lower:
            flags.append("SUDO")
        if (
            "destructive" in response_lower
            or "destroy" in response_lower
            or "delete" in response_lower
        ):
            flags.append("DESTRUCTIVE")
        if "system" in response_lower:
            flags.append("SYSTEM")
        if "process" in response_lower:
            flags.append("PROCESS")

        # Infer from analysis data
        safety_data = all_data.get("safety", {})
        if safety_data.get("can_destroy_data", False):
            if "DESTRUCTIVE" not in flags:
                flags.append("DESTRUCTIVE")

        if safety_data.get("requires_privileges", False):
            if "SUDO" not in flags:
                flags.append("SUDO")

        # Command-specific logic
        primary_function = all_data.get("parsing", {}).get("primary_function", "")
        if primary_function in ["data_copy", "filesystem_ops"]:
            if "FILE_OPS" not in flags:
                flags.append("FILE_OPS")

        return flags

    def _extract_logic_adjustments(self, text: str) -> List[str]:
        """Extract logic-based adjustments"""
        adjustments = []
        if "too high" in text.lower():
            adjustments.append("risk_assessment_too_high")
        if "too low" in text.lower():
            adjustments.append("risk_assessment_too_low")
        if "depends on" in text.lower():
            adjustments.append("context_dependent")
        return adjustments

    def _extract_context_factors(self, text: str) -> List[str]:
        """Extract context factors"""
        factors = []
        if "flag" in text.lower() or "option" in text.lower():
            factors.append("command_line_options")
        if "user" in text.lower():
            factors.append("user_context")
        if "system" in text.lower():
            factors.append("system_context")
        return factors

    # Helper methods from original implementation
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
            "process": ["kill", "terminate", "signal", "control"],
        }

        for op, keywords in operation_keywords.items():
            if any(kw in text_lower for kw in keywords):
                operations.append(op)

        return operations

    # Stage 5 and main processing methods (similar to original)
    def stage5_algorithmic_encoding(
        self, command: str, risk: str, capabilities: List[str]
    ) -> StageResult:
        """Stage 5: Final binary descriptor generation"""
        start_time = time.time()

        # Risk level mapping
        risk_flags = {
            "SAFE": 0x01,
            "LOW_RISK": 0x02,
            "MEDIUM_RISK": 0x04,
            "HIGH_RISK": 0x08,
            "CRITICAL": 0x10,
        }

        # Capability flags
        cap_flags = 0
        cap_mapping = {
            "FILE_OPS": 0x0100,
            "NETWORK": 0x0200,
            "SUDO": 0x0400,
            "DESTRUCTIVE": 0x0800,
            "SYSTEM": 0x1000,
            "PROCESS": 0x2000,
        }

        for cap in capabilities:
            if cap in cap_mapping:
                cap_flags |= cap_mapping[cap]

        # Build descriptor
        magic = b"TCP\x02"
        version = struct.pack(">H", 2)
        cmd_hash = hashlib.md5(command.encode()).digest()[:4]
        security_flags = struct.pack(">I", risk_flags.get(risk, 0x04) | cap_flags)

        # Performance placeholders
        exec_time = struct.pack(">I", 100)
        memory = struct.pack(">H", 10)
        output = struct.pack(">H", 1)

        # Calculate CRC
        data = magic + version + cmd_hash + security_flags + exec_time + memory + output
        crc = struct.pack(">H", sum(data) & 0xFFFF)

        descriptor = data + crc

        return StageResult(
            stage_name="algorithmic_encoding",
            success=True,
            data={
                "binary_descriptor": descriptor.hex(),
                "risk_encoded": risk,
                "capabilities_encoded": capabilities,
                "descriptor_size": len(descriptor),
            },
            processing_time_ms=int((time.time() - start_time) * 1000),
        )

    def process_command(self, command: str) -> CommandAnalysis:
        """Process a command through all optimized stages"""
        print(f"\n🔧 Processing '{command}' with optimized models")
        analysis = CommandAnalysis(command=command)

        # Get man page
        man_page = self.get_man_page(command)
        if not man_page:
            print(f"   ❌ No man page found for {command}")
            analysis.man_page_found = False
            return analysis

        analysis.man_page_found = True
        man_sections = self.extract_man_sections(man_page)

        # Stage 1: Pure Parsing (llama3.2)
        print(f"   📝 Stage 1: Parsing with {self.get_best_model('parsing')}")
        stage1 = self.stage1_pure_parsing(command, man_sections)
        analysis.stages["parsing"] = stage1
        if not stage1.success:
            return analysis

        # Stage 2: Safety Analysis (llama3:8b-instruct-fp16)
        print(f"   🛡️ Stage 2: Safety with {self.get_best_model('safety')}")
        stage2 = self.stage2_pure_safety(command, man_sections, stage1.data)
        analysis.stages["safety"] = stage2
        if not stage2.success:
            return analysis
        print(
            f"      ✅ Risk: {stage2.data.get('risk_level')} ({'OVERRIDE' if stage2.data.get('rule_override') else 'LLM'})"
        )

        # Stage 3: Logic Review (mistral)
        print(f"   🧠 Stage 3: Logic with {self.get_best_model('logic')}")
        stage3 = self.stage3_logic_review(command, stage1.data, stage2.data)
        analysis.stages["logic"] = stage3
        if not stage3.success:
            return analysis

        # Stage 4: Encoding Review (llama3)
        print(f"   🔤 Stage 4: Encoding with {self.get_best_model('encoding')}")
        all_data = {"parsing": stage1.data, "safety": stage2.data, "logic": stage3.data}
        stage4 = self.stage4_encoding_review(command, all_data)
        analysis.stages["encoding"] = stage4
        if not stage4.success:
            return analysis

        # Stage 5: Binary Encoding
        print("   💾 Stage 5: Binary Encoding")
        final_risk = stage3.data.get("revised_risk", "MEDIUM_RISK")
        final_capabilities = stage4.data.get("flags_to_set", [])

        stage5 = self.stage5_algorithmic_encoding(
            command, final_risk, final_capabilities
        )
        analysis.stages["binary"] = stage5

        # Set final values
        analysis.final_risk = RiskLevel(final_risk)
        analysis.final_capabilities = final_capabilities
        analysis.binary_descriptor = bytes.fromhex(
            stage5.data.get("binary_descriptor", "")
        )

        # Update stats
        self.stats["total_processed"] += 1
        self.stats["risk_distribution"][final_risk] = (
            self.stats["risk_distribution"].get(final_risk, 0) + 1
        )

        print(f"      ✅ Final: {final_risk} | {', '.join(final_capabilities)}")

        return analysis

    def demo(self):
        """Run optimized demo focusing on accuracy"""
        print("🚀 TCP Optimized Multi-Stage Refinery")
        print("Using best models for each stage")
        print("=" * 60)

        # Test critical commands that should show proper risk assessment
        test_commands = [
            "dd",
            "rm",
            "sudo",  # Should be HIGH_RISK/CRITICAL
            "ls",
            "cat",
            "echo",  # Should be SAFE/LOW_RISK
        ]

        print(f"\n🎯 Testing {len(test_commands)} commands for accuracy...")
        print("Expected: Dangerous commands as HIGH_RISK/CRITICAL")

        start_time = time.time()

        for i, command in enumerate(test_commands, 1):
            print(f"\n[{i}/{len(test_commands)}] Command: {command}")
            analysis = self.process_command(command)
            self.analyses[command] = analysis

        # Report results
        total_time = time.time() - start_time
        print(f"\n" + "=" * 60)
        print("📊 Optimized Refinery Results")
        print("=" * 60)

        print(f"Total Time: {total_time:.1f}s")
        print(f"Rule Overrides: {self.stats['rule_overrides']}")

        print("\n🎯 Risk Assessment Results:")
        for cmd, analysis in self.analyses.items():
            if analysis.final_risk:
                override = (
                    "🔧"
                    if analysis.stages.get("safety", {}).data.get("rule_override")
                    else "🤖"
                )
                print(f"   {cmd:<10} {analysis.final_risk.value:<12} {override}")

        print("\n⚠️ Risk Distribution:")
        for risk, count in sorted(self.stats["risk_distribution"].items()):
            print(f"   {risk:<15} {count}")

        # Save results
        self.save_results()

    def save_results(self):
        """Save optimized analysis results"""
        output = {
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_commands": len(self.analyses),
                "method": "optimized_multi_stage",
                "models_used": self.stage_models,
                "rule_overrides": self.stats["rule_overrides"],
                "stats": self.stats,
            },
            "commands": {},
        }

        for cmd, analysis in self.analyses.items():
            output["commands"][cmd] = {
                "man_page_found": analysis.man_page_found,
                "final_risk": analysis.final_risk.value
                if analysis.final_risk
                else "UNKNOWN",
                "final_capabilities": analysis.final_capabilities,
                "binary_descriptor": analysis.binary_descriptor.hex()
                if analysis.binary_descriptor
                else "",
                "stages": {
                    name: {
                        "success": stage.success,
                        "error": stage.error,
                        "processing_time_ms": stage.processing_time_ms,
                        "model_used": stage.model_used,
                        "data": stage.data,
                    }
                    for name, stage in analysis.stages.items()
                },
            }

        with open("optimized_multi_stage_results.json", "w") as f:
            json.dump(output, f, indent=2)

        print(f"\n💾 Results saved to: optimized_multi_stage_results.json")


if __name__ == "__main__":
    refinery = OptimizedMultiStageTCPRefinery()
    refinery.demo()
