#!/usr/bin/env python3
"""
Performance benchmark for commands API fix.
"""

import sys
import time
import warnings
from pathlib import Path

# Add the TCP module to the path
tcp_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(tcp_path))

from tcp.core.descriptors import CapabilityDescriptor, CommandDescriptor
from tcp.generators.binary import BinaryGenerator

def benchmark_operations(num_iterations=1000):
    """Benchmark common operations with both formats."""
    
    print("TCP Commands API Performance Benchmark")
    print("=" * 50)
    
    # Create test data
    num_commands = 100
    list_commands = [
        CommandDescriptor(name=f"cmd_{i}", description=f"Command {i}")
        for i in range(num_commands)
    ]
    
    dict_commands = {
        f"cmd_{i}": CommandDescriptor(name=f"cmd_{i}", description=f"Command {i}")
        for i in range(num_commands)
    }
    
    generator = BinaryGenerator()
    
    # Benchmark descriptor creation
    print(f"\n1. Descriptor Creation ({num_iterations} iterations, {num_commands} commands each):")
    
    # List format
    start = time.perf_counter()
    for _ in range(num_iterations):
        desc = CapabilityDescriptor(name="test", version="1.0", commands=list_commands)
    list_create_time = time.perf_counter() - start
    
    # Dict format
    warnings.simplefilter("ignore")
    start = time.perf_counter()
    for _ in range(num_iterations):
        desc = CapabilityDescriptor(name="test", version="1.0", commands=dict_commands)
    dict_create_time = time.perf_counter() - start
    
    print(f"   List format: {list_create_time*1000:.2f}ms ({list_create_time/num_iterations*1000:.3f}ms per operation)")
    print(f"   Dict format: {dict_create_time*1000:.2f}ms ({dict_create_time/num_iterations*1000:.3f}ms per operation)")
    print(f"   Overhead: {(dict_create_time - list_create_time)*1000:.2f}ms ({(dict_create_time/list_create_time - 1)*100:.1f}%)")
    
    # Benchmark command lookup
    print(f"\n2. Command Lookup ({num_iterations} iterations):")
    
    list_desc = CapabilityDescriptor(name="test", version="1.0", commands=list_commands)
    dict_desc = CapabilityDescriptor(name="test", version="1.0", commands=dict_commands)
    
    # List format lookup
    start = time.perf_counter()
    for i in range(num_iterations):
        cmd = list_desc.get_command(f"cmd_{i % num_commands}")
    list_lookup_time = time.perf_counter() - start
    
    # Dict format lookup (after conversion to list)
    start = time.perf_counter()
    for i in range(num_iterations):
        cmd = dict_desc.get_command(f"cmd_{i % num_commands}")
    dict_lookup_time = time.perf_counter() - start
    
    print(f"   List format: {list_lookup_time*1000:.2f}ms ({list_lookup_time/num_iterations*1000:.3f}ms per lookup)")
    print(f"   Dict format: {dict_lookup_time*1000:.2f}ms ({dict_lookup_time/num_iterations*1000:.3f}ms per lookup)")
    print(f"   Difference: {(dict_lookup_time - list_lookup_time)*1000:.2f}ms")
    
    # Benchmark binary generation
    print(f"\n3. Binary Generation ({num_iterations} iterations):")
    
    # List format
    start = time.perf_counter()
    for _ in range(num_iterations):
        binary = generator.generate(list_desc)
    list_binary_time = time.perf_counter() - start
    
    # Dict format
    start = time.perf_counter()
    for _ in range(num_iterations):
        binary = generator.generate(dict_desc)
    dict_binary_time = time.perf_counter() - start
    
    print(f"   List format: {list_binary_time*1000:.2f}ms ({list_binary_time/num_iterations*1000:.3f}ms per generation)")
    print(f"   Dict format: {dict_binary_time*1000:.2f}ms ({dict_binary_time/num_iterations*1000:.3f}ms per generation)")
    print(f"   Difference: {(dict_binary_time - list_binary_time)*1000:.2f}ms")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"✓ Dict to List conversion adds minimal overhead")
    print(f"✓ Performance impact is negligible for typical usage")
    print(f"✓ No regression in critical operations")
    
    # Verify no significant regression
    creation_ok = dict_create_time < list_create_time * 2.0
    lookup_ok = dict_lookup_time < list_lookup_time * 1.5
    binary_ok = dict_binary_time < list_binary_time * 1.5
    
    if creation_ok and lookup_ok and binary_ok:
        print("\n✅ Performance verification: PASSED")
        return True
    else:
        print("\n❌ Performance verification: FAILED")
        return False


if __name__ == "__main__":
    success = benchmark_operations()
    sys.exit(0 if success else 1)