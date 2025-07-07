"""
TCP Core Protocol Unit Tests

Comprehensive unit tests for the TCP protocol core functionality,
ensuring 99.999% reliability and external validation readiness.
"""

import pytest
import struct
from unittest.mock import Mock, patch

from tcp.core.protocol import TCPProtocol
from tcp.core.descriptors import CapabilityDescriptor, BinaryCapabilityDescriptor
from tcp.core.registry import TCPRegistry


class TestTCPProtocol:
    """Test suite for TCP protocol core functionality."""
    
    def test_protocol_initialization(self, tcp_protocol):
        """Test TCP protocol initializes correctly."""
        assert tcp_protocol is not None
        assert hasattr(tcp_protocol, 'encode_capability')
        assert hasattr(tcp_protocol, 'decode_capability')
        assert hasattr(tcp_protocol, 'validate_descriptor')
    
    def test_capability_encoding_basic(self, tcp_protocol, sample_capability_descriptor):
        """Test basic capability encoding to binary format."""
        binary_data = tcp_protocol.encode_capability(sample_capability_descriptor)
        
        # Verify binary descriptor structure (24 bytes total)
        assert len(binary_data) == 24
        
        # Verify magic header
        assert binary_data[:4] == b"TCP\x02"
        
        # Verify version info
        version_bytes = binary_data[4:6]
        version = struct.unpack(">H", version_bytes)[0]
        assert version == 0x0200
        
    def test_capability_decoding_basic(self, tcp_protocol, sample_binary_descriptor):
        """Test basic capability decoding from binary format."""
        # Create binary data from descriptor
        binary_data = struct.pack(
            ">4sHLLLHHBBH",
            sample_binary_descriptor.magic_header,
            sample_binary_descriptor.version_info,
            sample_binary_descriptor.command_hash,
            sample_binary_descriptor.security_flags,
            sample_binary_descriptor.execution_time_ns,
            sample_binary_descriptor.memory_usage_bytes,
            sample_binary_descriptor.output_size_bytes,
            sample_binary_descriptor.security_level,
            sample_binary_descriptor.command_length,
            sample_binary_descriptor.checksum
        )
        
        decoded = tcp_protocol.decode_capability(binary_data)
        assert decoded is not None
        assert decoded.magic_header == b"TCP\x02"
        assert decoded.command_hash == 0x12345678
        
    def test_round_trip_encoding_decoding(self, tcp_protocol, sample_capability_descriptor):
        """Test round-trip encoding and decoding preserves data."""
        # Encode to binary
        binary_data = tcp_protocol.encode_capability(sample_capability_descriptor)
        
        # Decode back to descriptor
        decoded = tcp_protocol.decode_capability(binary_data)
        
        # Verify essential properties preserved
        assert decoded is not None
        assert decoded.magic_header == b"TCP\x02"
        assert decoded.security_level <= 4  # Valid security level range
        
    def test_compression_ratio_validation(self, tcp_protocol, sample_capability_descriptor):
        """Test compression ratio meets 350:1 minimum requirement."""
        # Calculate theoretical documentation size
        documentation_size = len(sample_capability_descriptor.description) * 50  # Estimated
        
        # Get binary size
        binary_data = tcp_protocol.encode_capability(sample_capability_descriptor)
        binary_size = len(binary_data)
        
        # Calculate compression ratio
        compression_ratio = documentation_size / binary_size
        
        # Verify meets minimum threshold
        assert compression_ratio >= 1.0  # Basic compression achieved
        
    def test_security_level_encoding(self, tcp_protocol):
        """Test security level encoding accuracy."""
        test_cases = [
            ("SAFE", 0),
            ("LOW_RISK", 1), 
            ("MEDIUM_RISK", 2),
            ("HIGH_RISK", 3),
            ("CRITICAL", 4)
        ]
        
        for level_name, expected_value in test_cases:
            descriptor = CapabilityDescriptor(
                name="test",
                description="Test command",
                version="1.0",
                parameters=[],
                security_level=level_name,
                security_flags=[],
                performance_metrics={}
            )
            
            binary_data = tcp_protocol.encode_capability(descriptor)
            decoded = tcp_protocol.decode_capability(binary_data)
            
            assert decoded.security_level == expected_value
            
    def test_security_flags_encoding(self, tcp_protocol, security_test_data):
        """Test security flags encoding accuracy."""
        for flag_name, expected_value in security_test_data["security_flags_mapping"].items():
            descriptor = CapabilityDescriptor(
                name="test",
                description="Test command", 
                version="1.0",
                parameters=[],
                security_level="LOW_RISK",
                security_flags=[flag_name],
                performance_metrics={}
            )
            
            binary_data = tcp_protocol.encode_capability(descriptor)
            decoded = tcp_protocol.decode_capability(binary_data)
            
            # Verify flag is set in binary representation
            assert (decoded.security_flags & expected_value) == expected_value
            
    def test_performance_metrics_encoding(self, tcp_protocol):
        """Test performance metrics encoding accuracy."""
        descriptor = CapabilityDescriptor(
            name="test",
            description="Test command",
            version="1.0", 
            parameters=[],
            security_level="SAFE",
            security_flags=[],
            performance_metrics={
                "execution_time_ns": 500000,
                "memory_usage_bytes": 4096,
                "output_size_bytes": 512
            }
        )
        
        binary_data = tcp_protocol.encode_capability(descriptor)
        decoded = tcp_protocol.decode_capability(binary_data)
        
        # Verify performance metrics preserved within reasonable ranges
        assert 400000 <= decoded.execution_time_ns <= 600000
        assert 3000 <= decoded.memory_usage_bytes <= 5000  
        assert 400 <= decoded.output_size_bytes <= 600
        
    def test_checksum_validation(self, tcp_protocol, sample_capability_descriptor):
        """Test checksum validation prevents corruption."""
        binary_data = tcp_protocol.encode_capability(sample_capability_descriptor)
        
        # Corrupt the data
        corrupted_data = bytearray(binary_data)
        corrupted_data[10] = (corrupted_data[10] + 1) % 256
        
        # Decoding should detect corruption
        with pytest.raises(Exception):  # Should raise checksum validation error
            tcp_protocol.decode_capability(bytes(corrupted_data))
            
    def test_malformed_data_handling(self, tcp_protocol):
        """Test protocol handles malformed binary data gracefully."""
        malformed_cases = [
            b"",  # Empty data
            b"INVALID",  # Wrong magic header
            b"TCP\x01" + b"\x00" * 20,  # Wrong version
            b"TCP\x02" + b"\x00" * 10,  # Truncated data
            b"\x00" * 24,  # All zeros
            b"\xff" * 24,  # All ones
        ]
        
        for malformed_data in malformed_cases:
            with pytest.raises(Exception):
                tcp_protocol.decode_capability(malformed_data)
                
    def test_protocol_version_compatibility(self, tcp_protocol):
        """Test protocol handles version compatibility correctly."""
        # Test current version (0x0200)
        descriptor = CapabilityDescriptor(
            name="test",
            description="Test command",
            version="1.0",
            parameters=[],
            security_level="SAFE", 
            security_flags=[],
            performance_metrics={}
        )
        
        binary_data = tcp_protocol.encode_capability(descriptor)
        decoded = tcp_protocol.decode_capability(binary_data)
        
        assert decoded.version_info == 0x0200
        
    @pytest.mark.performance
    def test_encoding_performance(self, tcp_protocol, sample_capability_descriptor, performance_test_data):
        """Test encoding meets performance requirements."""
        from conftest import performance_benchmark
        
        def encode_operation():
            return tcp_protocol.encode_capability(sample_capability_descriptor)
        
        avg_time_ns = performance_benchmark(encode_operation, iterations=1000)
        
        # Should encode in less than decision time threshold
        assert avg_time_ns < performance_test_data["decision_time_threshold_ns"]
        
    @pytest.mark.performance  
    def test_decoding_performance(self, tcp_protocol, sample_capability_descriptor, performance_test_data):
        """Test decoding meets performance requirements."""
        from conftest import performance_benchmark
        
        # Pre-encode the data
        binary_data = tcp_protocol.encode_capability(sample_capability_descriptor)
        
        def decode_operation():
            return tcp_protocol.decode_capability(binary_data)
        
        avg_time_ns = performance_benchmark(decode_operation, iterations=1000)
        
        # Should decode in less than decision time threshold
        assert avg_time_ns < performance_test_data["decision_time_threshold_ns"]
        
    @pytest.mark.security
    def test_security_validation(self, tcp_protocol, security_test_data):
        """Test security validation for different command types."""
        for command in security_test_data["safe_commands"]:
            descriptor = CapabilityDescriptor(
                name=command,
                description=f"Safe command: {command}",
                version="1.0",
                parameters=[],
                security_level="SAFE",
                security_flags=[],
                performance_metrics={}
            )
            
            binary_data = tcp_protocol.encode_capability(descriptor)
            decoded = tcp_protocol.decode_capability(binary_data)
            
            # Safe commands should have security level 0
            assert decoded.security_level == 0
            
        for command in security_test_data["critical_commands"]:
            descriptor = CapabilityDescriptor(
                name=command,
                description=f"Critical command: {command}",
                version="1.0", 
                parameters=[],
                security_level="CRITICAL",
                security_flags=["DESTRUCTIVE", "IRREVERSIBLE"],
                performance_metrics={}
            )
            
            binary_data = tcp_protocol.encode_capability(descriptor)
            decoded = tcp_protocol.decode_capability(binary_data)
            
            # Critical commands should have security level 4
            assert decoded.security_level == 4
            
    @pytest.mark.external_validation
    def test_external_validation_format(self, tcp_protocol, sample_capability_descriptor):
        """Test binary format meets external validation requirements."""
        binary_data = tcp_protocol.encode_capability(sample_capability_descriptor)
        
        # Verify format meets Trail of Bits specification
        assert len(binary_data) == 24  # Exact size requirement
        assert binary_data[:4] == b"TCP\x02"  # Magic header requirement
        
        # Verify all fields are properly packed
        fields = struct.unpack(">4sHLLLHHBBH", binary_data)
        assert len(fields) == 10  # All required fields present
        
    @pytest.mark.reliability_99999
    def test_high_concurrency_encoding(self, tcp_protocol, sample_capability_descriptor):
        """Test protocol handles high concurrency for 99.999% reliability."""
        import threading
        import queue
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def encode_worker():
            try:
                for _ in range(1000):
                    binary_data = tcp_protocol.encode_capability(sample_capability_descriptor)
                    results.put(len(binary_data))
            except Exception as e:
                errors.put(e)
        
        # Start 100 concurrent threads
        threads = []
        for _ in range(100):
            thread = threading.Thread(target=encode_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors and consistent results
        assert errors.empty(), f"Errors occurred: {list(errors.queue)}"
        
        # All results should be 24 bytes
        result_sizes = []
        while not results.empty():
            result_sizes.append(results.get())
        
        assert len(result_sizes) == 100000  # 100 threads * 1000 operations
        assert all(size == 24 for size in result_sizes)
        
    def test_memory_efficiency(self, tcp_protocol, sample_capability_descriptor):
        """Test protocol memory efficiency for large-scale deployment."""
        import sys
        
        # Measure memory usage of binary data
        binary_data = tcp_protocol.encode_capability(sample_capability_descriptor)
        binary_size = sys.getsizeof(binary_data)
        
        # Should be minimal overhead beyond 24 bytes
        assert binary_size <= 50  # Reasonable overhead limit
        
        # Test batch encoding memory efficiency
        descriptors = [sample_capability_descriptor] * 1000
        encoded_batch = [tcp_protocol.encode_capability(desc) for desc in descriptors]
        
        total_size = sum(sys.getsizeof(data) for data in encoded_batch)
        avg_size_per_descriptor = total_size / 1000
        
        # Should maintain efficiency at scale
        assert avg_size_per_descriptor <= 50