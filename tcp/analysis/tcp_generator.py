"""TCP descriptor generation from LLM-extracted capabilities."""

import hashlib
import struct
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.descriptors import (
    BinaryCapabilityDescriptor,
    CapabilityDescriptor,
    CommandDescriptor,
    FormatDescriptor,
    FormatType,
    ParameterDescriptor,
    ParameterType,
    PerformanceMetrics,
    ProcessingMode,
)
from .llm_extractor import EnhancedCommand, EnhancedOption, ToolCapabilities


class TCPDescriptorGenerator:
    """Generate TCP descriptors from LLM-extracted capabilities."""

    def __init__(self):
        """Initialize TCP descriptor generator."""
        self.parameter_type_map = {
            "boolean": ParameterType.BOOLEAN,
            "string": ParameterType.STRING,
            "integer": ParameterType.INTEGER,
            "float": ParameterType.FLOAT,
            "enum": ParameterType.ENUM,
            "path": ParameterType.FILE,  # Use FILE for paths
            "url": ParameterType.STRING,  # Use STRING for URLs
        }

        self.format_type_map = {
            "text": FormatType.TEXT,
            "json": FormatType.JSON,
            "xml": FormatType.XML,
            "csv": FormatType.TEXT,  # Use TEXT for CSV
            "binary": FormatType.BINARY,
            "image": FormatType.IMAGE,
            "audio": FormatType.AUDIO,
            "video": FormatType.VIDEO,
            "stdin": FormatType.TEXT,  # Use TEXT for stdin
            "stdout": FormatType.TEXT,  # Use TEXT for stdout
            "file": FormatType.DOCUMENT,  # Use DOCUMENT for files
            "directory": FormatType.DOCUMENT,  # Use DOCUMENT for directories
        }

    def generate_tcp_descriptor(
        self, capabilities: ToolCapabilities
    ) -> CapabilityDescriptor:
        """Generate complete TCP descriptor from capabilities."""
        descriptor = CapabilityDescriptor(
            name=capabilities.tool_name,
            version=capabilities.version or "unknown",
            description=capabilities.description,
            homepage=capabilities.homepage or "",
            license=capabilities.license or "",
            created_at=datetime.utcnow(),
        )

        # Set input/output formats
        descriptor.input_formats = self._convert_formats(
            capabilities.input_formats or []
        )
        descriptor.output_formats = self._convert_formats(
            capabilities.output_formats or []
        )

        # Set processing modes
        descriptor.processing_modes = self._determine_processing_modes(capabilities)

        # Convert commands
        descriptor.commands = []
        for enhanced_cmd in capabilities.commands or []:
            tcp_cmd = self._convert_command(enhanced_cmd)
            descriptor.commands.append(tcp_cmd)

        # Set performance metrics
        descriptor.performance = self._generate_performance_metrics(capabilities)

        # Set capabilities flags
        descriptor.capability_flags = self._generate_capability_flags_int(capabilities)

        return descriptor

    def generate_binary_descriptor(self, capabilities: ToolCapabilities) -> bytes:
        """
        Generate ultra-compact binary descriptor (20 bytes).

        Format: Magic(4) + Version(2) + Capabilities(4) + Performance(8) + CRC(2)
        """
        # Magic bytes (4 bytes) - use tool name hash
        magic = hashlib.md5(
            capabilities.tool_name.encode(), usedforsecurity=False
        ).digest()[:4]

        # Version (2 bytes) - encode version as integer
        version_int = self._encode_version(capabilities.version or "0.0")
        version = struct.pack(">H", version_int)

        # Capabilities flags (4 bytes)
        cap_flags = self._encode_capability_flags(capabilities)
        capabilities_bytes = struct.pack(">I", cap_flags)

        # Performance metrics (8 bytes)
        performance = self._encode_performance(capabilities)

        # Calculate CRC16 for integrity
        data = magic + version + capabilities_bytes + performance
        crc = struct.pack(">H", self._calculate_crc16(data))

        return data + crc

    def generate_json_schema(self, capabilities: ToolCapabilities) -> Dict[str, Any]:
        """Generate JSON schema from capabilities."""
        schema = {
            "tool": capabilities.tool_name,
            "version": capabilities.version,
            "description": capabilities.description,
            "metadata": {
                "vendor": capabilities.vendor,
                "homepage": capabilities.homepage,
                "license": capabilities.license,
                "extraction_method": capabilities.extraction_method,
                "confidence_score": capabilities.confidence_score,
            },
            "capabilities": {
                "processing": {
                    "supports_stdin": capabilities.supports_stdin,
                    "supports_files": capabilities.supports_files,
                    "supports_directories": capabilities.supports_directories,
                    "supports_recursion": capabilities.supports_recursion,
                    "supports_parallel": capabilities.supports_parallel,
                    "supports_streaming": capabilities.supports_streaming,
                },
                "formats": {
                    "input": capabilities.input_formats or [],
                    "output": capabilities.output_formats or [],
                },
                "resources": {
                    "memory_usage": capabilities.memory_usage,
                    "cpu_usage": capabilities.cpu_usage,
                    "disk_usage": capabilities.disk_usage,
                    "network_usage": capabilities.network_usage,
                },
            },
            "commands": {},
        }

        # Add commands
        for cmd in capabilities.commands or []:
            schema["commands"][cmd.name] = {
                "description": cmd.description,
                "category": cmd.category,
                "parameters": {},
                "input_formats": cmd.input_formats or [],
                "output_formats": cmd.output_formats or [],
                "examples": cmd.examples or [],
            }

            # Add parameters
            for option in cmd.options or []:
                param_name = (option.long_flag or option.short_flag or "").lstrip("-")
                if param_name:
                    schema["commands"][cmd.name]["parameters"][param_name] = {
                        "type": option.parameter_type,
                        "description": option.description,
                        "required": option.is_required,
                        "flags": {"short": option.short_flag, "long": option.long_flag},
                        "default": option.default_value,
                        "examples": option.examples or [],
                        "category": option.category,
                    }

                    # Add type-specific constraints
                    if option.enum_values:
                        schema["commands"][cmd.name]["parameters"][param_name][
                            "enum"
                        ] = option.enum_values
                    if option.min_value is not None:
                        schema["commands"][cmd.name]["parameters"][param_name][
                            "minimum"
                        ] = option.min_value
                    if option.max_value is not None:
                        schema["commands"][cmd.name]["parameters"][param_name][
                            "maximum"
                        ] = option.max_value
                    if option.pattern:
                        schema["commands"][cmd.name]["parameters"][param_name][
                            "pattern"
                        ] = option.pattern

        return schema

    def _convert_formats(self, format_strings: List[str]) -> List[FormatDescriptor]:
        """Convert format strings to FormatDescriptor objects."""
        formats = []
        for fmt_str in format_strings:
            fmt_lower = fmt_str.lower()
            if fmt_lower in self.format_type_map:
                format_type = self.format_type_map[fmt_lower]
            else:
                # Try to infer format type
                if any(ext in fmt_lower for ext in [".txt", ".log", "text"]):
                    format_type = FormatType.TEXT
                elif any(ext in fmt_lower for ext in [".json", "json"]):
                    format_type = FormatType.JSON
                elif any(ext in fmt_lower for ext in [".xml", "xml"]):
                    format_type = FormatType.XML
                else:
                    format_type = FormatType.TEXT  # Default

            # Create FormatDescriptor
            descriptor = FormatDescriptor(
                name=fmt_str,
                type=format_type,
                description=f"{fmt_str} format",
            )
            formats.append(descriptor)

        return formats

    def _determine_processing_modes(
        self, capabilities: ToolCapabilities
    ) -> List[ProcessingMode]:
        """Determine processing modes from capabilities."""
        modes = []

        if capabilities.supports_streaming:
            modes.append(ProcessingMode.STREAM)
        else:
            modes.append(ProcessingMode.BATCH)

        if capabilities.supports_parallel:
            modes.append(ProcessingMode.SYNC)  # Use available mode

        return modes

    def _convert_command(self, enhanced_cmd: EnhancedCommand) -> CommandDescriptor:
        """Convert enhanced command to TCP command descriptor."""
        tcp_cmd = CommandDescriptor(
            name=enhanced_cmd.name, description=enhanced_cmd.description, parameters=[]
        )

        # Convert options to parameters
        for option in enhanced_cmd.options or []:
            param = ParameterDescriptor(
                name=(option.long_flag or option.short_flag or "").lstrip("-"),
                type=self.parameter_type_map.get(
                    option.parameter_type, ParameterType.STRING
                ),
                description=option.description,
                required=option.is_required,
                default=option.default_value,
            )

            # Set type-specific constraints
            if option.enum_values:
                param.enum_values = option.enum_values
            if option.min_value is not None:
                param.min_value = option.min_value
            if option.max_value is not None:
                param.max_value = option.max_value
            if option.pattern:
                param.pattern = option.pattern
            if option.examples:
                param.examples = option.examples

            tcp_cmd.parameters.append(param)

        # Set command examples if available
        if enhanced_cmd.examples:
            tcp_cmd.examples = [{"description": ex} for ex in enhanced_cmd.examples]

        return tcp_cmd

    def _generate_performance_metrics(
        self, capabilities: ToolCapabilities
    ) -> PerformanceMetrics:
        """Generate performance metrics from capabilities."""
        # Map qualitative to quantitative estimates
        memory_map = {"low": 50, "medium": 200, "high": 1000}  # MB

        return PerformanceMetrics(
            avg_processing_time_ms=100,  # Default estimate
            memory_usage_mb=memory_map.get(capabilities.memory_usage, 50),
            network_required=capabilities.network_usage != "none",
            concurrent_requests=1 if not capabilities.supports_parallel else 10,
        )

    def _generate_capability_flags_int(self, capabilities: ToolCapabilities) -> int:
        """Generate capability flags as integer for TCP descriptor."""
        flags = 0

        # Use the CapabilityFlags enum from descriptors
        from ..core.descriptors import CapabilityFlags

        if capabilities.supports_files:
            flags |= CapabilityFlags.SUPPORTS_FILES
        if capabilities.supports_stdin:
            flags |= CapabilityFlags.SUPPORTS_STDIN
        if capabilities.supports_parallel:
            flags |= CapabilityFlags.PARALLEL_PROCESSING
        if capabilities.supports_streaming:
            flags |= CapabilityFlags.STREAM_PROCESSING
        if capabilities.network_usage != "none":
            flags |= CapabilityFlags.SUPPORTS_NETWORK

        return flags

    def _generate_capability_flags(
        self, capabilities: ToolCapabilities
    ) -> Dict[str, bool]:
        """Generate capability flags dictionary."""
        return {
            "supports_stdin": capabilities.supports_stdin,
            "supports_files": capabilities.supports_files,
            "supports_directories": capabilities.supports_directories,
            "supports_recursion": capabilities.supports_recursion,
            "supports_parallel": capabilities.supports_parallel,
            "supports_streaming": capabilities.supports_streaming,
            "low_memory": capabilities.memory_usage == "low",
            "low_cpu": capabilities.cpu_usage == "low",
            "network_required": capabilities.network_usage != "none",
            "disk_writes": capabilities.disk_usage in ["temporary", "persistent"],
        }

    def _encode_version(self, version: str) -> int:
        """Encode version string as integer."""
        try:
            parts = version.split(".")
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            # Encode as major*100 + minor (max 655.35)
            return min(major * 100 + minor, 65535)
        except (ValueError, IndexError):
            return 0

    def _encode_capability_flags(self, capabilities: ToolCapabilities) -> int:
        """Encode capability flags as 32-bit integer."""
        flags = 0

        # Define bit positions for capabilities
        capability_bits = {
            "supports_stdin": 0,
            "supports_files": 1,
            "supports_directories": 2,
            "supports_recursion": 3,
            "supports_parallel": 4,
            "supports_streaming": 5,
        }

        for capability, bit_pos in capability_bits.items():
            if getattr(capabilities, capability, False):
                flags |= 1 << bit_pos

        # Add resource usage flags
        if capabilities.memory_usage == "low":
            flags |= 1 << 8
        if capabilities.cpu_usage == "low":
            flags |= 1 << 9
        if capabilities.network_usage != "none":
            flags |= 1 << 10

        return flags

    def _encode_performance(self, capabilities: ToolCapabilities) -> bytes:
        """Encode performance metrics as 8 bytes."""
        # Estimate performance metrics
        memory_map = {"low": 10, "medium": 100, "high": 1000}
        cpu_map = {"low": 10, "medium": 50, "high": 90}

        memory_mb = memory_map.get(capabilities.memory_usage, 10)
        cpu_percent = cpu_map.get(capabilities.cpu_usage, 10)

        # Pack as: memory(2) + cpu(1) + flags(1) + reserved(4)
        return struct.pack(
            ">HBBBBBB",
            min(memory_mb, 65535),  # Memory usage in MB
            min(cpu_percent, 255),  # CPU usage percentage
            1 if capabilities.supports_streaming else 0,  # Streaming flag
            1 if capabilities.supports_parallel else 0,  # Parallel flag
            0,
            0,
            0,  # Reserved bytes
        )

    def _calculate_crc16(self, data: bytes) -> int:
        """Calculate CRC16 checksum."""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc & 0xFFFF
