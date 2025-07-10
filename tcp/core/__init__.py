"""Core TCP protocol implementation."""

from .protocol import ToolCapabilityProtocol
from .descriptors import (
    CapabilityDescriptor,
    BinaryCapabilityDescriptor,
    CommandDescriptor,
    ParameterDescriptor,
    FormatDescriptor,
)
from .registry import CapabilityRegistry
from .discovery import DiscoveryService

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
