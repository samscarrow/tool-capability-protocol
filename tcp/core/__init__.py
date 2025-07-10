"""Core TCP protocol implementation."""

from .descriptors import (
    BinaryCapabilityDescriptor,
    CapabilityDescriptor,
    CommandDescriptor,
    FormatDescriptor,
    ParameterDescriptor,
)
from .discovery import DiscoveryService
from .protocol import ToolCapabilityProtocol
from .registry import CapabilityRegistry

__all__ = [
    "ToolCapabilityProtocol",
    "CapabilityDescriptor",
    "BinaryCapabilityDescriptor",
    "CommandDescriptor",
    "ParameterDescriptor",
    "FormatDescriptor",
    "CapabilityRegistry",
    "DiscoveryService",
]
