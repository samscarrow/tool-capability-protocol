#!/usr/bin/env python3
"""
TCP Remote API - Simplified Interface
Dr. Sam Mitchell - Hardware Security Engineer

Ultra-simple API for researchers to use gentoo.local hardware without SSH commands.
Just import and use - connection handling is automatic.
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Union
from tcp_gentoo_orchestrator import TCPRemote, ResourceRequest

class TCP:
    """Ultra-simple TCP remote interface"""
    
    def __init__(self, host: str = None, username: str = None):
        self._remote = None
        self._host = host
        self._username = username
        self._connected = False
    
    async def _ensure_connected(self):
        """Ensure connection is established"""
        if not self._connected:
            self._remote = TCPRemote(self._host, self._username)
            await self._remote.__aenter__()
            self._connected = True
    
    async def _disconnect(self):
        """Disconnect from remote"""
        if self._connected and self._remote:
            await self._remote.__aexit__(None, None, None)
            self._connected = False
    
    # Synchronous wrappers for async operations
    
    def validate(self, descriptors: Union[List[bytes], str], backend: str = "cpu") -> Dict[str, Any]:
        """Validate TCP descriptors on gentoo.local
        
        Args:
            descriptors: List of 24-byte TCP descriptors or path to binary file
            backend: 'cpu', 'gpu', or 'fpga'
            
        Returns:
            Validation results dictionary
        """
        return asyncio.run(self._validate_async(descriptors, backend))
    
    async def _validate_async(self, descriptors, backend):
        await self._ensure_connected()
        return await self._remote.validate(descriptors, backend)
    
    def benchmark(self, tools: int = 1000, iterations: int = 100, 
                 backends: List[str] = None) -> Dict[str, Any]:
        """Run TCP vs LLM benchmark on gentoo.local
        
        Args:
            tools: Number of tools to test
            iterations: Iterations per tool
            backends: List of backends to test ['cpu', 'gpu', 'fpga']
            
        Returns:
            Benchmark results dictionary
        """
        return asyncio.run(self._benchmark_async(tools, iterations, backends))
    
    async def _benchmark_async(self, tools, iterations, backends):
        await self._ensure_connected()
        return await self._remote.benchmark(tools, iterations, backends)
    
    def status(self) -> Dict[str, Any]:
        """Get gentoo.local system status
        
        Returns:
            System status including CPU, memory, GPU, FPGA
        """
        return asyncio.run(self._status_async())
    
    async def _status_async(self):
        await self._ensure_connected()
        return await self._remote.status()
    
    def run(self, command: str, cpu_cores: int = 4, memory_gb: int = 16,
           gpu: bool = False, fpga: bool = False, hours: int = 4) -> Dict[str, Any]:
        """Run arbitrary command on gentoo.local
        
        Args:
            command: Shell command to execute
            cpu_cores: Number of CPU cores to allocate
            memory_gb: Memory limit in GB
            gpu: Whether to allocate GPU
            fpga: Whether to allocate FPGA
            hours: Maximum runtime in hours
            
        Returns:
            Job result with stdout, stderr, exit_code
        """
        return asyncio.run(self._run_async(command, cpu_cores, memory_gb, gpu, fpga, hours))
    
    async def _run_async(self, command, cpu_cores, memory_gb, gpu, fpga, hours):
        await self._ensure_connected()
        
        resources = ResourceRequest(
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            gpu_count=1 if gpu else 0,
            fpga_required=fpga,
            max_runtime_hours=hours
        )
        
        result = await self._remote.orchestrator.submit_job(command, resources)
        
        return {
            'exit_code': result.exit_code,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'execution_time': result.execution_time,
            'status': result.status.value
        }
    
    def __del__(self):
        """Cleanup on deletion"""
        if self._connected:
            try:
                asyncio.run(self._disconnect())
            except:
                pass

# Global instance for even simpler usage
_global_tcp = None

def get_tcp_instance() -> TCP:
    """Get global TCP instance"""
    global _global_tcp
    if _global_tcp is None:
        _global_tcp = TCP()
    return _global_tcp

# Ultra-simple functions for immediate use

def validate(descriptors: Union[List[bytes], str], backend: str = "cpu") -> Dict[str, Any]:
    """Validate TCP descriptors on gentoo.local (simple function)"""
    return get_tcp_instance().validate(descriptors, backend)

def benchmark(tools: int = 1000, iterations: int = 100, 
             backends: List[str] = None) -> Dict[str, Any]:
    """Run TCP benchmark on gentoo.local (simple function)"""
    return get_tcp_instance().benchmark(tools, iterations, backends)

def status() -> Dict[str, Any]:
    """Get gentoo.local status (simple function)"""
    return get_tcp_instance().status()

def run(command: str, **kwargs) -> Dict[str, Any]:
    """Run command on gentoo.local (simple function)"""
    return get_tcp_instance().run(command, **kwargs)

# Context manager for explicit resource management

class TCPSession:
    """Context manager for TCP operations"""
    
    def __init__(self, host: str = None, username: str = None):
        self.tcp = TCP(host, username)
    
    def __enter__(self):
        return self.tcp
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            asyncio.run(self.tcp._disconnect())
        except:
            pass

# Example usage functions

def example_basic_usage():
    """Example: Basic TCP operations"""
    
    print("=== Basic TCP Operations Example ===")
    
    # Get system status
    print("1. Checking gentoo.local status...")
    sys_status = status()
    print(f"   CPU cores: {sys_status['cpu']['cores']}")
    print(f"   Memory: {sys_status['memory']['available_gb']}GB available")
    print(f"   GPUs: {len(sys_status['gpu'])}")
    
    # Run simple command
    print("\n2. Running simple command...")
    result = run("echo 'Hello from gentoo.local'")
    print(f"   Output: {result['stdout'].strip()}")
    
    # TCP validation example
    print("\n3. TCP validation example...")
    # Create sample TCP descriptors
    sample_descriptors = [b"TCP\x02" + b"\x00" * 20 for _ in range(10)]
    
    validation_result = validate(sample_descriptors, backend="cpu")
    print(f"   Validated {len(sample_descriptors)} descriptors")
    print(f"   Results: {validation_result}")

def example_benchmark():
    """Example: Running TCP benchmark"""
    
    print("=== TCP Benchmark Example ===")
    
    # Run comprehensive benchmark
    print("Running TCP vs LLM benchmark...")
    print("This may take several minutes...")
    
    benchmark_results = benchmark(
        tools=100,          # Test 100 tools
        iterations=50,      # 50 iterations each
        backends=['cpu', 'gpu']  # Test both CPU and GPU
    )
    
    print(f"TCP average time: {benchmark_results.get('tcp_performance', {}).get('mean_us', 0):.2f} μs")
    print(f"LLM average time: {benchmark_results.get('llm_performance', {}).get('mean_ms', 0):.2f} ms")
    print(f"Speedup factor: {benchmark_results.get('comparison', {}).get('speedup_factor', 0):.1f}x")

def example_fpga_usage():
    """Example: FPGA acceleration"""
    
    print("=== FPGA Acceleration Example ===")
    
    with TCPSession() as tcp:
        # Check FPGA status
        fpga_status = asyncio.run(tcp._remote.fpga())
        print(f"FPGA available: {fpga_status.get('available', False)}")
        
        if fpga_status.get('available'):
            # Run FPGA validation
            print("Running FPGA validation...")
            sample_descriptors = [b"TCP\x02" + b"\x00" * 20 for _ in range(1000)]
            
            fpga_results = tcp.validate(sample_descriptors, backend="fpga")
            print(f"FPGA validation completed: {fpga_results}")
        else:
            print("FPGA not available or already in use")

def example_custom_experiment():
    """Example: Custom experiment workflow"""
    
    print("=== Custom Experiment Example ===")
    
    with TCPSession() as tcp:
        # Upload custom script
        script_content = """
#!/bin/bash
echo "Starting custom TCP experiment..."
tcp-benchmark --tools 500 --iterations 20 --detailed-stats
echo "Experiment completed successfully"
"""
        
        # Write script to file
        with open('/tmp/custom_experiment.sh', 'w') as f:
            f.write(script_content)
        
        # Make executable and run
        result = tcp.run(
            "chmod +x /tmp/custom_experiment.sh && /tmp/custom_experiment.sh",
            cpu_cores=8,
            memory_gb=32,
            hours=2
        )
        
        print(f"Custom experiment result:")
        print(f"Exit code: {result['exit_code']}")
        print(f"Output: {result['stdout']}")
        if result['stderr']:
            print(f"Errors: {result['stderr']}")

if __name__ == "__main__":
    """Demo all examples"""
    
    print("TCP Remote API Demo")
    print("=" * 50)
    
    try:
        example_basic_usage()
        print("\n" + "=" * 50)
        
        # Uncomment to run other examples
        # example_benchmark()
        # example_fpga_usage()
        # example_custom_experiment()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have:")
        print("1. SSH access to gentoo.local configured")
        print("2. TCP consortium VPN connected")
        print("3. Your SSH key in ~/.ssh/tcp_rsa")