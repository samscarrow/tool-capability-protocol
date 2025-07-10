"""
TCP Security Module

This module provides comprehensive security controls for TCP tools,
ensuring human oversight and sandboxed execution.
"""

from .sandbox_manager import (
    TCPSandboxManager,
    SandboxPermission,
    SandboxViolation,
    SandboxedTool,
)
from .human_approval_interface import HumanApprovalInterface
from .secure_tcp_agent import SecureTCPAgent

__all__ = [
    "TCPSandboxManager",
    "SandboxPermission",
    "SandboxViolation",
    "SandboxedTool",
    "HumanApprovalInterface",
    "SecureTCPAgent",
]
