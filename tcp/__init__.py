"""Tool Capability Protocol (TCP) - Universal tool capability description."""

from .core.protocol import ToolCapabilityProtocol
from .core.descriptors import (
    CapabilityDescriptor,
    BinaryCapabilityDescriptor,
    CommandDescriptor,
    ParameterDescriptor,
    FormatDescriptor,
)
from .core.registry import CapabilityRegistry
from .core.discovery import DiscoveryService
from .generators import (
    JSONGenerator,
    OpenAPIGenerator,
    GraphQLGenerator,
    ProtobufGenerator,
    BinaryGenerator,
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
