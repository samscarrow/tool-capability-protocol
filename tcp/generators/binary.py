"""Binary format generator for TCP descriptors."""

import struct
import hashlib
from typing import Dict, Any, List
from ..core.descriptors import CapabilityDescriptor, ParameterType


class BinaryGenerator:
    """Generate binary TCP descriptors."""

    def generate(self, descriptor: CapabilityDescriptor) -> bytes:
        """
        Generate compact binary descriptor (20 bytes).

        Format: Magic(4) + Version(2) + Capabilities(4) + Performance(8) + CRC(2)
        """
        # Magic bytes (4 bytes) - use tool name hash
        magic = hashlib.md5(descriptor.name.encode(), usedforsecurity=False).digest()[
            :4
        ]

        # Version (2 bytes) - encode version as integer
        version_int = self._encode_version(descriptor.version or "0.0")
        version = struct.pack(">H", version_int)

        # Capabilities flags (4 bytes)
        cap_flags = self._encode_capability_flags(descriptor)
        capabilities_bytes = struct.pack(">I", cap_flags)

        # Performance metrics (8 bytes)
        performance = self._encode_performance(descriptor)

        # Calculate CRC16 for integrity
        data = magic + version + capabilities_bytes + performance
        crc = struct.pack(">H", self._calculate_crc16(data))

        return data + crc

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

    def _encode_capability_flags(self, descriptor: CapabilityDescriptor) -> int:
        """Encode capability flags as 32-bit integer."""
        flags = 0

        # Process input/output formats
        if descriptor.input_formats:
            for fmt in descriptor.input_formats:
                if "text" in str(fmt).lower():
                    flags |= 1 << 0
                elif "json" in str(fmt).lower():
                    flags |= 1 << 1
                elif "file" in str(fmt).lower():
                    flags |= 1 << 2
                elif "stdin" in str(fmt).lower():
                    flags |= 1 << 3

        # Process capabilities from metadata
        if hasattr(descriptor, "capabilities") and descriptor.capabilities:
            caps = descriptor.capabilities
            if caps.get("supports_recursion"):
                flags |= 1 << 4
            if caps.get("supports_parallel"):
                flags |= 1 << 5
            if caps.get("supports_streaming"):
                flags |= 1 << 6
            if caps.get("supports_files"):
                flags |= 1 << 7

        # Process commands to infer capabilities
        for command in descriptor.commands:
            for param in command.parameters:
                if "recursive" in param.name.lower():
                    flags |= 1 << 4
                elif "parallel" in param.name.lower():
                    flags |= 1 << 5
                elif "file" in param.name.lower():
                    flags |= 1 << 7

        return flags

    def _encode_performance(self, descriptor: CapabilityDescriptor) -> bytes:
        """Encode performance metrics as 8 bytes."""
        # Handle both 'performance' and 'performance_metrics' for compatibility
        perf = getattr(descriptor, "performance", None) or getattr(
            descriptor, "performance_metrics", None
        )
        if perf:
            memory_mb = min(getattr(perf, "memory_usage_mb", 10), 65535)
            cpu_percent = min(getattr(perf, "cpu_usage_percent", 10), 255)
            throughput = min(getattr(perf, "throughput_ops_per_sec", 100), 65535)
        else:
            memory_mb = 10  # Default: 10MB
            cpu_percent = 10  # Default: 10% CPU
            throughput = 100  # Default: 100 ops/sec

        # Pack as: memory(2) + cpu(1) + throughput(2) + reserved(3)
        return struct.pack(
            ">HBHBBB",
            memory_mb,  # Memory usage in MB
            cpu_percent,  # CPU usage percentage
            throughput,  # Operations per second
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
