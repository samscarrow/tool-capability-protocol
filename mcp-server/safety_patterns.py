#!/usr/bin/env python3
"""
Agent Safety Patterns: TCP-guided containment and safe alternatives

Implements proven safety patterns from TCP research for AI agent containment,
designed for future standalone TCP protocol adoption.
"""

import time
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)

class AgentSafetyMonitor:
    """
    TCP-guided Agent Safety Monitor
    
    Implements containment patterns and safe alternatives based on
    breakthrough TCP research, designed for future TCP protocol.
    """
    
    def __init__(self):
        self.decision_cache: Dict[str, Dict[str, Any]] = {}
        self.safety_patterns = self._load_safety_patterns()
        self.quarantine_counter = 0
        
        # TCP Safety Protocol Configuration
        self.tcp_safety_config = {
            "critical_auto_reject": True,
            "high_risk_require_approval": True,
            "quarantine_over_delete": True,
            "audit_all_decisions": True,
            "microsecond_decisions": True
        }
    
    def _load_safety_patterns(self) -> Dict[str, Any]:
        """Load TCP-validated safety patterns"""
        return {
            "safe_alternatives": {
                # File operations - quarantine instead of delete
                "rm": "mv {target} .tcp_quarantine_{timestamp}/",
                "rm -f": "mv {target} .tcp_quarantine_{timestamp}/",
                "rm -rf": "mv {target} .tcp_quarantine_{timestamp}/",
                "shred": "mv {target} .tcp_quarantine_{timestamp}/ && echo 'File quarantined instead of shredded'",
                
                # System operations - safe modes
                "dd": "echo 'TCP SAFETY: dd operation blocked - use specific backup tools'",
                "mkfs": "echo 'TCP SAFETY: Format operation blocked - manual verification required'",
                "fdisk": "fdisk -l",  # Read-only mode
                
                # Network operations - safe versions
                "curl": "curl --max-time 30 --max-filesize 10M",
                "wget": "wget --timeout=30 --quota=10M",
                
                # Package operations - simulation
                "apt install": "apt show",  # Show package info instead
                "yum install": "yum info",
                "pip install": "pip show",
            },
            
            "quarantine_patterns": {
                "directory_prefix": ".tcp_quarantine_",
                "timestamp_format": "%Y%m%d_%H%M%S",
                "recovery_instructions": True,
                "audit_log": True
            },
            
            "approval_workflows": {
                "high_risk_commands": [
                    "chmod 777", "chown -R", "mount", "umount",
                    "systemctl", "service", "kill -9"
                ],
                "critical_commands": [
                    "rm -rf /", "dd if=/dev/zero", "mkfs",
                    "fdisk", "parted", "wipefs"
                ]
            }
        }
    
    def make_decision(self, tcp_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make agent safety decision based on TCP analysis
        
        Returns decision with action, reasoning, and timing
        """
        start_time = time.perf_counter()
        command = tcp_analysis["command"]
        risk_level = tcp_analysis["risk_level"]
        capabilities = tcp_analysis.get("capabilities", [])
        
        # Check cache for recent decisions
        cache_key = f"{command}:{risk_level}"
        if cache_key in self.decision_cache:
            cached = self.decision_cache[cache_key]
            cached["from_cache"] = True
            return cached
        
        decision = self._evaluate_tcp_safety(command, risk_level, capabilities)
        
        # Add timing information
        analysis_time = (time.perf_counter() - start_time) * 1000  # milliseconds
        decision["analysis_time_ms"] = round(analysis_time, 3)
        decision["tcp_protocol"] = "v2.0"
        decision["decision_timestamp"] = datetime.now().isoformat()
        
        # Cache decision
        self.decision_cache[cache_key] = decision
        
        # Audit logging
        if self.tcp_safety_config["audit_all_decisions"]:
            self._audit_decision(command, decision)
        
        logger.info("TCP safety decision made",
                   command=command,
                   risk_level=risk_level, 
                   action=decision["action"],
                   time_ms=analysis_time)
        
        return decision
    
    def _evaluate_tcp_safety(self, command: str, risk_level: str, capabilities: List[str]) -> Dict[str, Any]:
        """Evaluate safety based on TCP intelligence"""
        
        # CRITICAL commands - automatic rejection
        if risk_level == "CRITICAL":
            return {
                "action": "REJECT",
                "reasoning": "TCP CRITICAL classification - automatic rejection for agent safety",
                "alternative_available": self._has_safe_alternative(command),
                "tcp_guidance": "Command classified as CRITICAL by TCP binary descriptor analysis",
                "human_override": "Manual execution possible with explicit approval"
            }
        
        # HIGH_RISK commands - require approval
        if risk_level == "HIGH_RISK":
            return {
                "action": "REQUIRE_APPROVAL", 
                "reasoning": "TCP HIGH_RISK classification - human approval required",
                "risk_factors": self._analyze_risk_factors(capabilities),
                "alternative_available": self._has_safe_alternative(command),
                "tcp_guidance": "Command requires elevated privileges or system modifications"
            }
        
        # MEDIUM_RISK commands - caution mode with monitoring
        if risk_level == "MEDIUM_RISK":
            return {
                "action": "CAUTION_MODE",
                "reasoning": "TCP MEDIUM_RISK classification - proceed with monitoring",
                "monitoring": "File operations will be tracked and logged",
                "rollback_possible": self._assess_rollback_capability(command, capabilities),
                "tcp_guidance": "Command may modify files or data"
            }
        
        # LOW_RISK and SAFE commands - approve with logging
        return {
            "action": "APPROVED",
            "reasoning": f"TCP {risk_level} classification - safe for autonomous execution",
            "monitoring": "Basic execution logging enabled",
            "tcp_guidance": "Command classified as safe by TCP binary analysis"
        }
    
    def _analyze_risk_factors(self, capabilities: List[str]) -> List[str]:
        """Analyze specific risk factors from TCP capabilities"""
        risk_factors = []
        
        if "DESTRUCTIVE" in capabilities:
            risk_factors.append("Can permanently destroy data")
        if "REQUIRES_ROOT" in capabilities:
            risk_factors.append("Requires administrative privileges")
        if "SYSTEM_MODIFICATION" in capabilities:
            risk_factors.append("Modifies system configuration")
        if "FILE_MODIFICATION" in capabilities:
            risk_factors.append("Modifies file contents or permissions")
        if "NETWORK_ACCESS" in capabilities:
            risk_factors.append("Makes network connections")
        if "PRIVILEGE_ESCALATION" in capabilities:
            risk_factors.append("Can escalate user privileges")
        
        return risk_factors
    
    def _assess_rollback_capability(self, command: str, capabilities: List[str]) -> bool:
        """Assess if command effects can be rolled back"""
        
        # Commands with irreversible effects
        if "DESTRUCTIVE" in capabilities:
            return False
        
        # File operations are often reversible
        if "FILE_MODIFICATION" in capabilities and command.startswith(("cp", "mv")):
            return True
        
        # System modifications are harder to rollback
        if "SYSTEM_MODIFICATION" in capabilities:
            return False
        
        return True
    
    def generate_safe_alternative(self, dangerous_cmd: str) -> str:
        """Generate TCP-guided safe alternative for dangerous command"""
        
        # Parse command
        cmd_parts = dangerous_cmd.split()
        base_cmd = cmd_parts[0] if cmd_parts else dangerous_cmd
        
        # Check for direct safe alternative
        if base_cmd in self.safety_patterns["safe_alternatives"]:
            alternative_pattern = self.safety_patterns["safe_alternatives"][base_cmd]
            
            # Handle special patterns
            if "{target}" in alternative_pattern:
                target = self._extract_target(dangerous_cmd)
                timestamp = datetime.now().strftime(self.safety_patterns["quarantine_patterns"]["timestamp_format"])
                
                alternative = alternative_pattern.format(
                    target=target,
                    timestamp=timestamp
                )
            elif "{timestamp}" in alternative_pattern:
                timestamp = datetime.now().strftime(self.safety_patterns["quarantine_patterns"]["timestamp_format"])
                alternative = alternative_pattern.format(timestamp=timestamp)
            else:
                alternative = alternative_pattern
            
            logger.info("Generated safe alternative",
                       original=dangerous_cmd,
                       alternative=alternative,
                       pattern="direct_mapping")
            
            return alternative
        
        # Generate quarantine-based alternative for file operations
        if self._is_file_operation(base_cmd):
            return self._generate_quarantine_alternative(dangerous_cmd)
        
        # Generate safe inspection alternative
        return self._generate_inspection_alternative(dangerous_cmd)
    
    def _extract_target(self, command: str) -> str:
        """Extract target file/directory from command"""
        cmd_parts = command.split()
        
        # For rm commands, target is usually the last argument
        if cmd_parts[0] == "rm":
            # Skip flags and get the target
            targets = [part for part in cmd_parts[1:] if not part.startswith("-")]
            return targets[0] if targets else "unknown_target"
        
        # For other commands, try to find file-like arguments
        for part in cmd_parts[1:]:
            if not part.startswith("-") and ("/" in part or "." in part):
                return part
        
        return "target_file"
    
    def _is_file_operation(self, command: str) -> bool:
        """Check if command is a file operation"""
        file_commands = ["rm", "mv", "cp", "shred", "chmod", "chown", "ln"]
        return command in file_commands
    
    def _generate_quarantine_alternative(self, dangerous_cmd: str) -> str:
        """Generate quarantine-based safe alternative"""
        target = self._extract_target(dangerous_cmd)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        quarantine_dir = f".tcp_quarantine_{timestamp}"
        
        alternative = f"mkdir -p {quarantine_dir} && mv {target} {quarantine_dir}/ && echo 'File quarantined to {quarantine_dir}/ - recoverable'"
        
        logger.info("Generated quarantine alternative",
                   original=dangerous_cmd,
                   quarantine_dir=quarantine_dir)
        
        return alternative
    
    def _generate_inspection_alternative(self, dangerous_cmd: str) -> str:
        """Generate safe inspection alternative"""
        cmd_parts = dangerous_cmd.split()
        base_cmd = cmd_parts[0]
        
        # Common inspection alternatives
        inspection_alternatives = {
            "dd": "echo 'TCP SAFETY: Use specific backup tools instead of dd'",
            "mkfs": "echo 'TCP SAFETY: Format blocked - verify target device manually'",
            "fdisk": "fdisk -l",  # List mode
            "mount": "mount | grep", # Show current mounts
            "kill": "ps aux | grep",  # Show processes instead
            "killall": "pgrep -l",  # List processes instead
        }
        
        if base_cmd in inspection_alternatives:
            return inspection_alternatives[base_cmd]
        
        # Generic safe alternative
        return f"echo 'TCP SAFETY: {dangerous_cmd} blocked - manual review required'"
    
    def _has_safe_alternative(self, command: str) -> bool:
        """Check if safe alternative exists for command"""
        base_cmd = command.split()[0]
        return (base_cmd in self.safety_patterns["safe_alternatives"] or
                self._is_file_operation(base_cmd))
    
    def _audit_decision(self, command: str, decision: Dict[str, Any]):
        """Audit safety decision for compliance"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "decision": decision["action"],
            "reasoning": decision["reasoning"],
            "tcp_protocol": "v2.0",
            "safety_monitor": "AgentSafetyMonitor"
        }
        
        # In production, this would write to audit log
        logger.info("TCP safety audit", **audit_entry)
    
    def get_safety_statistics(self) -> Dict[str, Any]:
        """Get safety monitoring statistics"""
        total_decisions = len(self.decision_cache)
        
        if total_decisions == 0:
            return {
                "total_decisions": 0,
                "safety_status": "no_decisions_yet"
            }
        
        # Analyze decision distribution
        decisions = list(self.decision_cache.values())
        action_counts = {}
        
        for decision in decisions:
            action = decision["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            "total_decisions": total_decisions,
            "action_distribution": action_counts,
            "cache_size": len(self.decision_cache),
            "quarantine_operations": self.quarantine_counter,
            "tcp_protocol": "v2.0",
            "safety_config": self.tcp_safety_config
        }
    
    def reset_cache(self):
        """Reset decision cache (for testing)"""
        self.decision_cache.clear()
        self.quarantine_counter = 0
        logger.info("TCP safety monitor cache reset")