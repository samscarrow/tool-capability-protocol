# TCP Remote Hardware Access Tool

**Seamless access to gentoo.local hardware without SSH commands**

Created by Dr. Sam Mitchell - Hardware Security Engineer  
TCP Research Consortium

---

## 🚀 Quick Start

### 1. One-Command Setup
```bash
python setup_tcp_remote.py
```

### 2. Instant Usage
```python
from tcp_remote_api import status, run, validate

# Check system status
print(status())

# Run any command
result = run("echo 'Hello from gentoo.local'")
print(result['stdout'])

# Validate TCP descriptors
validation_result = validate(my_descriptors, backend="gpu")
```

---

## 📦 What This Tool Provides

### Zero-Configuration Access
- **No SSH commands** - Just `import` and use
- **Automatic connection management** - Handles all networking
- **Resource allocation** - CPU, GPU, FPGA scheduling built-in
- **File transfer** - Seamless upload/download

### Hardware Abstraction
- **CPU clusters** - Multi-core job execution
- **GPU acceleration** - NVIDIA RTX 4090 access
- **FPGA acceleration** - Xilinx Alveo U250 programming
- **High-performance storage** - Bcachefs file system

### Research-Optimized
- **TCP validation** - Hardware-accelerated descriptor validation
- **Benchmarking** - TCP vs LLM comparison tools
- **Monitoring** - Real-time resource usage
- **Experiment management** - Job queuing and result collection

---

## 🛠 Setup Instructions

### Prerequisites
- Python 3.8+
- TCP Consortium VPN access
- Internet connection

### Automated Setup
```bash
# Clone or download the TCP remote tools
git clone <tcp-consortium-repo>
cd tcp-consortium/sam-mitchell/infrastructure/

# Run setup script
python setup_tcp_remote.py
```

### Manual Setup (if needed)
```bash
# Install dependencies
pip install asyncssh

# Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/tcp_rsa -C "yourname@tcp-consortium"

# Send public key to Sam Mitchell
cat ~/.ssh/tcp_rsa.pub
```

---

## 🐍 Python API Reference

### Simple Functions
```python
from tcp_remote_api import validate, benchmark, status, run

# System status
status = status()
print(f"Available CPUs: {status['cpu']['cores']}")
print(f"Available GPUs: {len(status['gpu'])}")

# Run commands
result = run("ls /opt/tcp/tools")
print(result['stdout'])

# TCP validation
descriptors = [b'TCP\x02' + b'\x00'*20 for _ in range(10)]
results = validate(descriptors, backend="gpu")

# Benchmarking
benchmark_results = benchmark(tools=100, iterations=50)
```

### Advanced Usage
```python
from tcp_remote_api import TCPSession, TCP

# Context manager (recommended for multiple operations)
with TCPSession() as tcp:
    status = tcp.status()
    result1 = tcp.run("command1")
    result2 = tcp.run("command2")

# Persistent instance
tcp = TCP()
status = tcp.status()
results = tcp.benchmark(tools=1000)

# Custom resource allocation
result = tcp.run(
    "intensive_computation.py",
    cpu_cores=16,
    memory_gb=64,
    gpu=True,
    fpga=True,
    hours=8
)
```

### Full Orchestrator Access
```python
from tcp_gentoo_orchestrator import TCPGentooOrchestrator

async def advanced_usage():
    async with TCPGentooOrchestrator() as orchestrator:
        # Upload files
        remote_paths = await orchestrator.upload_files(
            ["data.txt", "script.py"], 
            "/tmp/experiment/"
        )
        
        # Submit complex job
        result = await orchestrator.submit_job(
            command="python /tmp/experiment/script.py",
            resources=ResourceRequest(
                cpu_cores=8,
                memory_gb=32,
                gpu_count=1,
                max_runtime_hours=4
            )
        )
        
        # Download results
        await orchestrator.download_files(
            ["/tmp/experiment/results.json"],
            "./local_results/"
        )
```

---

## 🔧 Command Line Interface

### Direct CLI Usage
```bash
# System status
python tcp_gentoo_orchestrator.py status

# Validate descriptors
python tcp_gentoo_orchestrator.py validate descriptors.bin --backend fpga

# Run benchmark
python tcp_gentoo_orchestrator.py benchmark --tools 500 --backends cpu gpu

# Monitor resources
python tcp_gentoo_orchestrator.py monitor --duration 300
```

---

## 💡 Example Use Cases

### TCP Validation Research
```python
# Elena's statistical validation
from tcp_remote_api import validate

descriptors = load_statistical_samples()
results = validate(descriptors, backend="cpu")
statistical_analysis(results)

# Yuki's performance testing
benchmark_results = benchmark(
    tools=10000, 
    iterations=1000,
    backends=["cpu", "gpu", "fpga"]
)
analyze_performance(benchmark_results)
```

### Hardware Acceleration Testing
```python
# Marcus's distributed validation
with TCPSession() as tcp:
    # Test software baseline
    cpu_results = tcp.validate(descriptors, backend="cpu")
    
    # Test GPU acceleration
    gpu_results = tcp.validate(descriptors, backend="gpu")
    
    # Test FPGA acceleration
    fpga_results = tcp.validate(descriptors, backend="fpga")
    
    compare_performance(cpu_results, gpu_results, fpga_results)
```

### Custom Experiments
```python
# Aria's security testing
def security_experiment():
    with TCPSession() as tcp:
        # Upload security test suite
        tcp.run("scp security_tests.tar.gz gentoo.local:/tmp/")
        tcp.run("cd /tmp && tar -xzf security_tests.tar.gz")
        
        # Run comprehensive security analysis
        result = tcp.run(
            "cd /tmp/security_tests && ./run_all_tests.sh",
            cpu_cores=16,
            memory_gb=64,
            hours=6
        )
        
        return parse_security_results(result['stdout'])
```

### Real-time Monitoring
```python
# Alex's quality monitoring
async def monitor_experiment():
    async with TCPGentooOrchestrator() as orchestrator:
        # Start monitoring
        monitor_task = asyncio.create_task(
            orchestrator.monitor_resources(interval=1, duration=3600)
        )
        
        # Run experiment
        experiment_result = await orchestrator.tcp_benchmark(
            tools=5000, iterations=100
        )
        
        # Get monitoring data
        monitoring_data = await monitor_task
        
        return experiment_result, monitoring_data
```

---

## 🔍 Troubleshooting

### Connection Issues
```python
# Test basic connectivity
from tcp_remote_api import status
try:
    s = status()
    print("✓ Connection successful")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

**Common Solutions:**
1. **VPN Connection** - Ensure TCP consortium VPN is active
2. **SSH Key** - Verify key is registered with Sam Mitchell
3. **Network** - Check internet connectivity
4. **Permissions** - Ensure SSH key permissions are 600

### Resource Allocation
```python
# Check resource availability before large jobs
status = status()
if status['memory']['available_gb'] < 32:
    print("Insufficient memory, waiting...")
    time.sleep(300)  # Wait 5 minutes
```

### Error Handling
```python
# Robust error handling
from tcp_remote_api import TCPSession

def safe_experiment():
    try:
        with TCPSession() as tcp:
            result = tcp.run("my_experiment.py", cpu_cores=8, hours=2)
            if result['exit_code'] != 0:
                print(f"Experiment failed: {result['stderr']}")
                return None
            return result['stdout']
    
    except ConnectionError:
        print("Connection failed - check VPN and SSH key")
    except TimeoutError:
        print("Operation timed out - try with more time allocation")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None
```

---

## 📊 Performance Expectations

### Typical Latencies
- **Command execution**: 100-500ms
- **File upload (1MB)**: 1-2 seconds
- **TCP validation (1000 descriptors)**: 1-5ms
- **GPU job startup**: 2-5 seconds
- **FPGA programming**: 10-30 seconds

### Throughput Capabilities
- **CPU validation**: 1M descriptors/second
- **GPU validation**: 10M descriptors/second
- **FPGA validation**: 100M descriptors/second
- **Network transfer**: 1GB/s sustained

---

## 🔒 Security & Best Practices

### Resource Sharing
- **Fair usage** - Don't monopolize GPU/FPGA
- **Resource limits** - Set appropriate CPU/memory limits
- **Time limits** - Use realistic runtime estimates
- **Cleanup** - Remove temporary files after experiments

### Data Security
- **No sensitive data** - Don't upload confidential information
- **Temporary files** - Use /tmp for experimental data
- **Backup** - Important results are backed up nightly
- **Encryption** - All transfers are SSH encrypted

### Collaboration
- **Announce usage** - Post in #gentoo-local for major experiments
- **Resource coordination** - Check availability before long jobs
- **Help others** - Share useful scripts and techniques

---

## 📞 Support

### Getting Help
- **Documentation**: This README and inline code comments
- **Examples**: `tcp_remote_example.py` and function docstrings
- **Slack**: #gentoo-local channel for community help
- **Direct**: sam.mitchell@tcp-consortium.org for technical issues

### Reporting Issues
```python
# Include this information when reporting issues:
from tcp_remote_api import status
import platform

print(f"Python version: {platform.python_version()}")
print(f"Platform: {platform.platform()}")
print(f"TCP Remote status: {status()}")
```

### Feature Requests
- **Hardware needs** - New compute resources
- **Software tools** - Additional pre-installed tools
- **API features** - Enhanced functionality
- **Integration** - Connections to other systems

---

## 🎯 Next Steps

### For Researchers
1. **Run setup script**: `python setup_tcp_remote.py`
2. **Test connection**: `python tcp_remote_example.py`
3. **Start experimenting**: Use API for your research
4. **Share results**: Post findings in consortium channels

### For Development
1. **Extend API** - Add new hardware abstractions
2. **Optimize performance** - Improve resource scheduling
3. **Add backends** - Support additional hardware
4. **Enhance monitoring** - Better resource tracking

---

**Transform your TCP research with seamless hardware access!**

No more SSH commands, no more manual resource management.  
Just `import` and accelerate your research on gentoo.local.

**Dr. Sam Mitchell**  
Hardware Security Engineer  
TCP Research Consortium