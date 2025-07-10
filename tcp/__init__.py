"""Tool Capability Protocol (TCP) - Universal tool capability description."""

from .core.descriptors import (
    BinaryCapabilityDescriptor,
    CapabilityDescriptor,
    CommandDescriptor,
    FormatDescriptor,
    ParameterDescriptor,
)
from .core.discovery import DiscoveryService
from .core.protocol import ToolCapabilityProtocol
from .core.registry import CapabilityRegistry
from .generators import (
    BinaryGenerator,
    GraphQLGenerator,
    JSONGenerator,
    OpenAPIGenerator,
    ProtobufGenerator,
)

__version__ = "0.1.0"
__author__ = "TCP Team"
__email__ = "team@tcp.dev"

__all__ = [
    # Core classes
    "ToolCapabilityProtocol",
    "CapabilityDescriptor",
    "BinaryCapabilityDescriptor",
    "CommandDescriptor",
    "ParameterDescriptor",
    "FormatDescriptor",
    "CapabilityRegistry",
    "DiscoveryService",
    # Generators
    "JSONGenerator",
    "OpenAPIGenerator",
    "GraphQLGenerator",
    "ProtobufGenerator",
    "BinaryGenerator",
]
