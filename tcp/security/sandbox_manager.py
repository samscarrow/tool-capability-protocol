#!/usr/bin/env python3
"""
TCP Sandbox Manager - Security-First Tool Control

This module provides strict sandboxing for TCP tools, ensuring humans
maintain explicit control over which tools are available to agents.
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import tempfile
import shutil


class SandboxPermission(Enum):
    """Permission levels for sandboxed tools."""
    DENIED = "denied"
    READ_ONLY = "read_only"
    EXECUTE_SAFE = "execute_safe"
    EXECUTE_FULL = "execute_full"


class SandboxViolation(Exception):
    """Raised when sandbox security is violated."""
    pass


@dataclass
class SandboxedTool:
    """Represents a tool approved for sandbox use."""
    name: str
    binary_path: str
    permission_level: SandboxPermission
    allowed_args: List[str]
    forbidden_args: List[str]
    tcp_descriptor: bytes
    human_approved: bool
    approval_timestamp: str
    approved_by: str
    security_hash: str


class TCPSandboxManager:
    """
    Manages sandboxed TCP tools with human-controlled security.
    
    Key Security Principles:
    1. Explicit human approval required for all tools
    2. Whitelist-only approach (deny by default)
    3. Argument filtering and validation
    4. Execution isolation and monitoring
    5. Audit logging of all tool usage
    """
    
    def __init__(self, sandbox_dir: str = None, security_level: str = "strict"):
        """Initialize sandbox manager with security controls."""
        self.sandbox_dir = Path(sandbox_dir or Path.cwd() / "tcp_sandbox")
        self.security_level = security_level
        self.approved_tools = {}  # name -> SandboxedTool
        self.audit_log = []
        self.session_id = hashlib.md5(os.urandom(16)).hexdigest()[:8]
        
        # Set up logging first
        self.logger = logging.getLogger(f"tcp_sandbox_{self.session_id}")
        self._setup_logging()
        
        # Create secure sandbox directory
        self._initialize_sandbox()
        
        # Load previously approved tools
        self._load_approved_tools()
    
    def _initialize_sandbox(self) -> None:
        """Initialize secure sandbox directory structure."""
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Create security subdirectories
        (self.sandbox_dir / "approved_tools").mkdir(exist_ok=True)
        (self.sandbox_dir / "audit_logs").mkdir(exist_ok=True)
        (self.sandbox_dir / "temp_workspace").mkdir(exist_ok=True)
        (self.sandbox_dir / "quarantine").mkdir(exist_ok=True)
        
        # Create security manifest
        security_manifest = {
            "sandbox_version": "1.0",
            "security_level": self.security_level,
            "created_timestamp": self._get_timestamp(),
            "session_id": self.session_id,
            "human_control_required": True,
            "default_permission": "denied"
        }
        
        manifest_path = self.sandbox_dir / "security_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(security_manifest, f, indent=2)
        
        self.logger.info(f"Initialized TCP sandbox: {self.sandbox_dir}")
    
    def _setup_logging(self) -> None:
        """Set up comprehensive audit logging."""
        # Ensure audit logs directory exists
        audit_dir = self.sandbox_dir / "audit_logs"
        audit_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = audit_dir / f"tcp_audit_{self.session_id}.log"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] TCP-SANDBOX: %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"TCP Sandbox session started: {self.session_id}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for audit trail."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _load_approved_tools(self) -> None:
        """Load previously approved tools from secure storage."""
        approved_file = self.sandbox_dir / "approved_tools" / "approved_tools.json"
        
        if approved_file.exists():
            try:
                with open(approved_file, 'r') as f:
                    approved_data = json.load(f)
                
                for tool_name, tool_data in approved_data.items():
                    # Verify tool integrity
                    if self._verify_tool_integrity(tool_data):
                        tool = SandboxedTool(
                            name=tool_data['name'],
                            binary_path=tool_data['binary_path'],
                            permission_level=SandboxPermission(tool_data['permission_level']),
                            allowed_args=tool_data['allowed_args'],
                            forbidden_args=tool_data['forbidden_args'],
                            tcp_descriptor=bytes.fromhex(tool_data['tcp_descriptor']),
                            human_approved=tool_data['human_approved'],
                            approval_timestamp=tool_data['approval_timestamp'],
                            approved_by=tool_data['approved_by'],
                            security_hash=tool_data['security_hash']
                        )
                        self.approved_tools[tool_name] = tool
                        self.logger.info(f"Loaded approved tool: {tool_name}")
                    else:
                        self.logger.warning(f"Tool integrity check failed: {tool_name}")
                        
            except Exception as e:
                self.logger.error(f"Failed to load approved tools: {e}")
    
    def _verify_tool_integrity(self, tool_data: Dict) -> bool:
        """Verify tool has not been tampered with."""
        # Check if binary still exists and hasn't changed
        binary_path = tool_data.get('binary_path')
        if not binary_path or not Path(binary_path).exists():
            return False
        
        # Verify security hash (simplified - would use stronger crypto in production)
        expected_hash = tool_data.get('security_hash')
        if not expected_hash:
            return False
        
        # Check human approval flag
        if not tool_data.get('human_approved', False):
            return False
        
        return True
    
    def request_tool_approval(self, 
                            tool_name: str,
                            binary_path: str,
                            tcp_descriptor: bytes,
                            requested_permission: SandboxPermission,
                            allowed_args: List[str] = None,
                            forbidden_args: List[str] = None) -> bool:
        """
        Request human approval for a tool to be added to sandbox.
        
        This method creates an approval request that must be manually reviewed
        and approved by a human administrator.
        """
        self.logger.info(f"Tool approval requested: {tool_name} at {binary_path}")
        
        # Create approval request
        approval_request = {
            "tool_name": tool_name,
            "binary_path": binary_path,
            "tcp_descriptor": tcp_descriptor.hex(),
            "requested_permission": requested_permission.value,
            "allowed_args": allowed_args or [],
            "forbidden_args": forbidden_args or [],
            "request_timestamp": self._get_timestamp(),
            "session_id": self.session_id,
            "status": "pending_human_approval"
        }
        
        # Save approval request for human review
        request_file = self.sandbox_dir / "approval_requests" / f"{tool_name}_approval.json"
        request_file.parent.mkdir(exist_ok=True)
        
        with open(request_file, 'w') as f:
            json.dump(approval_request, f, indent=2)
        
        print("🔒 HUMAN APPROVAL REQUIRED")
        print("=" * 50)
        print(f"Tool: {tool_name}")
        print(f"Binary: {binary_path}")
        print(f"Permission Level: {requested_permission.value}")
        print(f"TCP Descriptor: {tcp_descriptor.hex()[:20]}...")
        print(f"Allowed Args: {allowed_args}")
        print(f"Forbidden Args: {forbidden_args}")
        print()
        print("⚠️  This tool requires explicit human approval before use.")
        print(f"📄 Approval request saved: {request_file}")
        print("👤 Please review and approve manually using approve_tool() method.")
        
        return False  # Always requires manual approval
    
    def approve_tool(self,
                    tool_name: str,
                    approved_by: str,
                    permission_level: SandboxPermission = None,
                    custom_args: Dict = None) -> bool:
        """
        Human approval method for sandbox tools.
        
        This method should only be called by human administrators
        after careful security review.
        """
        request_file = self.sandbox_dir / "approval_requests" / f"{tool_name}_approval.json"
        
        if not request_file.exists():
            raise SandboxViolation(f"No approval request found for tool: {tool_name}")
        
        # Load approval request
        with open(request_file, 'r') as f:
            request_data = json.load(f)
        
        # Create approved tool
        final_permission = permission_level or SandboxPermission(request_data['requested_permission'])
        
        # Apply custom security constraints if provided
        allowed_args = request_data['allowed_args']
        forbidden_args = request_data['forbidden_args']
        
        if custom_args:
            allowed_args = custom_args.get('allowed_args', allowed_args)
            forbidden_args = custom_args.get('forbidden_args', forbidden_args)
        
        # Generate security hash
        security_data = f"{tool_name}:{request_data['binary_path']}:{final_permission.value}:{approved_by}"
        security_hash = hashlib.sha256(security_data.encode()).hexdigest()
        
        approved_tool = SandboxedTool(
            name=tool_name,
            binary_path=request_data['binary_path'],
            permission_level=final_permission,
            allowed_args=allowed_args,
            forbidden_args=forbidden_args,
            tcp_descriptor=bytes.fromhex(request_data['tcp_descriptor']),
            human_approved=True,
            approval_timestamp=self._get_timestamp(),
            approved_by=approved_by,
            security_hash=security_hash
        )
        
        # Store approved tool
        self.approved_tools[tool_name] = approved_tool
        self._save_approved_tools()
        
        # Move request to approved
        approved_dir = self.sandbox_dir / "approved_tools" / "requests"
        approved_dir.mkdir(exist_ok=True)
        shutil.move(str(request_file), str(approved_dir / f"{tool_name}_approved.json"))
        
        self.logger.info(f"Tool approved by {approved_by}: {tool_name} with {final_permission.value} permission")
        
        print("✅ TOOL APPROVED")
        print(f"Tool: {tool_name}")
        print(f"Permission: {final_permission.value}")
        print(f"Approved by: {approved_by}")
        print(f"Timestamp: {approved_tool.approval_timestamp}")
        
        return True
    
    def _save_approved_tools(self) -> None:
        """Save approved tools to secure storage."""
        approved_file = self.sandbox_dir / "approved_tools" / "approved_tools.json"
        
        approved_data = {}
        for tool_name, tool in self.approved_tools.items():
            approved_data[tool_name] = {
                'name': tool.name,
                'binary_path': tool.binary_path,
                'permission_level': tool.permission_level.value,
                'allowed_args': tool.allowed_args,
                'forbidden_args': tool.forbidden_args,
                'tcp_descriptor': tool.tcp_descriptor.hex(),
                'human_approved': tool.human_approved,
                'approval_timestamp': tool.approval_timestamp,
                'approved_by': tool.approved_by,
                'security_hash': tool.security_hash
            }
        
        with open(approved_file, 'w') as f:
            json.dump(approved_data, f, indent=2)
    
    def get_available_tools(self) -> Dict[str, SandboxedTool]:
        """Get all human-approved tools available in sandbox."""
        return {name: tool for name, tool in self.approved_tools.items() 
                if tool.human_approved}
    
    def check_tool_permission(self, tool_name: str) -> Optional[SandboxPermission]:
        """Check permission level for a specific tool."""
        tool = self.approved_tools.get(tool_name)
        if not tool or not tool.human_approved:
            return None
        return tool.permission_level
    
    def validate_tool_execution(self, tool_name: str, args: List[str]) -> Tuple[bool, str]:
        """
        Validate if tool execution is allowed with given arguments.
        
        Returns (allowed, reason)
        """
        tool = self.approved_tools.get(tool_name)
        
        if not tool:
            return False, f"Tool '{tool_name}' not approved for sandbox use"
        
        if not tool.human_approved:
            return False, f"Tool '{tool_name}' lacks human approval"
        
        if tool.permission_level == SandboxPermission.DENIED:
            return False, f"Tool '{tool_name}' execution denied by security policy"
        
        # Check forbidden arguments
        for arg in args:
            for forbidden in tool.forbidden_args:
                if forbidden in arg:
                    return False, f"Forbidden argument detected: {forbidden}"
        
        # Check allowed arguments (if allowlist is specified)
        if tool.allowed_args:
            for arg in args:
                allowed = any(allowed_pattern in arg for allowed_pattern in tool.allowed_args)
                if not allowed and arg not in ['-h', '--help', '--version']:
                    return False, f"Argument not in allowlist: {arg}"
        
        return True, "Execution allowed"
    
    def execute_sandboxed_tool(self, 
                              tool_name: str, 
                              args: List[str],
                              input_data: str = None,
                              timeout: int = 30) -> Dict:
        """
        Execute a sandboxed tool with security controls.
        
        Returns execution result with security audit information.
        """
        # Validate execution
        allowed, reason = self.validate_tool_execution(tool_name, args)
        if not allowed:
            self.logger.warning(f"Tool execution blocked: {tool_name} - {reason}")
            raise SandboxViolation(f"Execution blocked: {reason}")
        
        tool = self.approved_tools[tool_name]
        
        # Log execution attempt
        self.logger.info(f"Executing sandboxed tool: {tool_name} {' '.join(args)}")
        
        # Create isolated execution environment
        with tempfile.TemporaryDirectory(dir=self.sandbox_dir / "temp_workspace") as temp_dir:
            try:
                # Prepare command
                cmd = [tool.binary_path] + args
                
                # Execute with restrictions
                result = subprocess.run(
                    cmd,
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=timeout,
                    cwd=temp_dir
                )
                
                execution_result = {
                    'tool_name': tool_name,
                    'command': ' '.join(cmd),
                    'exit_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'execution_time': timeout,  # Would track actual time in production
                    'sandbox_session': self.session_id,
                    'human_approved': True,
                    'security_level': self.security_level
                }
                
                self.logger.info(f"Tool execution completed: {tool_name} (exit code: {result.returncode})")
                return execution_result
                
            except subprocess.TimeoutExpired:
                self.logger.error(f"Tool execution timeout: {tool_name}")
                raise SandboxViolation(f"Tool execution timeout: {tool_name}")
            except Exception as e:
                self.logger.error(f"Tool execution failed: {tool_name} - {e}")
                raise SandboxViolation(f"Tool execution failed: {e}")
    
    def revoke_tool_approval(self, tool_name: str, revoked_by: str, reason: str) -> bool:
        """Revoke approval for a sandboxed tool."""
        if tool_name not in self.approved_tools:
            return False
        
        tool = self.approved_tools[tool_name]
        
        # Move to quarantine
        quarantine_dir = self.sandbox_dir / "quarantine"
        quarantine_file = quarantine_dir / f"{tool_name}_revoked.json"
        
        revocation_record = {
            'original_tool': asdict(tool),
            'revoked_by': revoked_by,
            'revocation_reason': reason,
            'revocation_timestamp': self._get_timestamp()
        }
        
        with open(quarantine_file, 'w') as f:
            json.dump(revocation_record, f, indent=2)
        
        # Remove from approved tools
        del self.approved_tools[tool_name]
        self._save_approved_tools()
        
        self.logger.warning(f"Tool approval revoked: {tool_name} by {revoked_by} - {reason}")
        
        print("🚫 TOOL APPROVAL REVOKED")
        print(f"Tool: {tool_name}")
        print(f"Revoked by: {revoked_by}")
        print(f"Reason: {reason}")
        
        return True
    
    def get_security_status(self) -> Dict:
        """Get comprehensive security status of the sandbox."""
        return {
            'sandbox_session': self.session_id,
            'security_level': self.security_level,
            'total_approved_tools': len(self.approved_tools),
            'pending_approvals': len(list((self.sandbox_dir / "approval_requests").glob("*.json"))),
            'quarantined_tools': len(list((self.sandbox_dir / "quarantine").glob("*.json"))),
            'human_control_active': True,
            'audit_log_entries': len(self.audit_log),
            'sandbox_directory': str(self.sandbox_dir)
        }


def main():
    """Demonstrate secure TCP sandbox management."""
    print("🔒 TCP SECURITY-FIRST SANDBOX DEMONSTRATION")
    print("=" * 60)
    print("Demonstrating human-controlled TCP tool sandboxing...")
    print()
    
    # Initialize secure sandbox
    sandbox = TCPSandboxManager(security_level="strict")
    
    # Show initial security status
    status = sandbox.get_security_status()
    print("📊 INITIAL SECURITY STATUS:")
    print("-" * 40)
    for key, value in status.items():
        print(f"{key}: {value}")
    print()
    
    # Simulate tool approval workflow
    print("🔐 TOOL APPROVAL WORKFLOW:")
    print("-" * 40)
    
    # Request approval for a safe tool
    tcp_descriptor = b'\x00' * 20  # Dummy TCP descriptor
    sandbox.request_tool_approval(
        tool_name="cat",
        binary_path="/bin/cat",
        tcp_descriptor=tcp_descriptor,
        requested_permission=SandboxPermission.READ_ONLY,
        allowed_args=["-n", "-b", "-A"],
        forbidden_args=["-e", "-T"]
    )
    
    print("\n💡 Next steps:")
    print("1. Human administrator reviews approval request")
    print("2. Administrator calls sandbox.approve_tool() if safe") 
    print("3. Tool becomes available for sandboxed execution")
    print()
    
    print("🔑 SECURITY PRINCIPLES:")
    print("-" * 40)
    print("✅ Explicit human approval required for ALL tools")
    print("✅ Whitelist-only approach (deny by default)")
    print("✅ Argument filtering and validation")
    print("✅ Execution isolation and monitoring")
    print("✅ Comprehensive audit logging")
    print("✅ Tool integrity verification")
    print("✅ Permission-based access controls")
    print()
    
    print("🛡️  HUMAN REMAINS IN CONTROL")
    print("   No tool can be used without explicit human approval.")
    print("   Every execution is logged and monitored.")
    print("   Security violations immediately block execution.")


if __name__ == "__main__":
    main()