#!/usr/bin/env python3
"""
TCP Gentoo Hardware Orchestrator
Dr. Sam Mitchell - Hardware Security Engineer

Seamless access to gentoo.local hardware resources without manual SSH commands.
Provides high-level API for researchers to use remote hardware transparently.
"""

import asyncio
import asyncssh
import json
import os
import time
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import tempfile
import contextlib
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

class ResourceType(Enum):
    CPU = "cpu"
    GPU = "gpu" 
    FPGA = "fpga"
    MEMORY = "memory"
    STORAGE = "storage"

class JobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ResourceRequest:
    """Resource allocation request"""
    cpu_cores: int = 4
    memory_gb: int = 16
    gpu_count: int = 0
    fpga_required: bool = False
    storage_gb: int = 100
    max_runtime_hours: int = 4
    priority: int = 5  # 1-10, 10 being highest

@dataclass
class JobRequest:
    """Job execution request"""
    job_id: str
    command: str
    working_dir: str = "/tmp"
    environment: Dict[str, str] = None
    input_files: List[str] = None
    output_files: List[str] = None
    resources: ResourceRequest = None
    callback: Optional[Callable] = None

@dataclass
class JobResult:
    """Job execution result"""
    job_id: str
    status: JobStatus
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    resources_used: Dict[str, Any]
    output_files: List[str] = None

class GentooConnection:
    """Manages persistent connection to gentoo.local"""
    
    def __init__(self, host: str = "tcp-gentoo.consortium.net", 
                 username: str = None, 
                 key_filename: str = None):
        self.host = host
        self.username = username or os.getenv('USER', 'researcher')
        self.key_filename = key_filename or os.path.expanduser('~/.ssh/tcp_rsa')
        self.connection = None
        self.sftp = None
        self._connection_lock = asyncio.Lock()
        
    async def connect(self):
        """Establish SSH connection"""
        async with self._connection_lock:
            if self.connection and not self.connection.is_client_closed():
                return
                
            try:
                self.connection = await asyncssh.connect(
                    self.host,
                    username=self.username,
                    client_keys=[self.key_filename] if os.path.exists(self.key_filename) else None,
                    known_hosts=None,  # For development - use proper known_hosts in production
                    keepalive_interval=30
                )
                self.sftp = await self.connection.start_sftp_client()
                print(f"✓ Connected to {self.host} as {self.username}")
                
            except Exception as e:
                raise ConnectionError(f"Failed to connect to gentoo.local: {e}")
    
    async def disconnect(self):
        """Close SSH connection"""
        if self.sftp:
            self.sftp.exit()
        if self.connection:
            self.connection.close()
            await self.connection.wait_closed()
    
    async def execute(self, command: str, **kwargs) -> asyncssh.SSHCompletedProcess:
        """Execute command on remote system"""
        await self.connect()
        return await self.connection.run(command, **kwargs)
    
    async def upload_file(self, local_path: str, remote_path: str):
        """Upload file to remote system"""
        await self.connect()
        await self.sftp.put(local_path, remote_path)
    
    async def download_file(self, remote_path: str, local_path: str):
        """Download file from remote system"""
        await self.connect()
        await self.sftp.get(remote_path, local_path)
    
    async def upload_directory(self, local_dir: str, remote_dir: str):
        """Upload directory recursively"""
        await self.connect()
        
        # Create remote directory
        await self.execute(f"mkdir -p {remote_dir}")
        
        # Upload all files
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_file = os.path.join(root, file)
                rel_path = os.path.relpath(local_file, local_dir)
                remote_file = f"{remote_dir}/{rel_path}"
                
                # Create remote subdirectories
                remote_subdir = os.path.dirname(remote_file)
                if remote_subdir != remote_dir:
                    await self.execute(f"mkdir -p {remote_subdir}")
                
                await self.upload_file(local_file, remote_file)

class TCPGentooOrchestrator:
    """Main orchestrator for gentoo.local hardware resources"""
    
    def __init__(self, connection: GentooConnection = None):
        self.connection = connection or GentooConnection()
        self.active_jobs: Dict[str, JobRequest] = {}
        self.job_results: Dict[str, JobResult] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        await self.connection.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.disconnect()
    
    # High-level TCP operations
    
    async def tcp_validate(self, descriptors: Union[List[bytes], str], 
                         backend: str = "cpu") -> Dict[str, Any]:
        """Validate TCP descriptors using specified backend"""
        
        job_id = f"tcp_validate_{uuid.uuid4().hex[:8]}"
        
        # Prepare input data
        if isinstance(descriptors, str):
            input_file = descriptors
        else:
            # Create temporary file with descriptors
            input_file = f"/tmp/tcp_descriptors_{job_id}.bin"
            descriptor_data = b''.join(descriptors)
            
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(descriptor_data)
                local_temp = f.name
            
            await self.connection.upload_file(local_temp, input_file)
            os.unlink(local_temp)
        
        # Determine resource requirements
        resources = ResourceRequest(
            cpu_cores=8 if backend == "cpu" else 4,
            memory_gb=32 if len(descriptors) > 10000 else 16,
            gpu_count=1 if backend == "gpu" else 0,
            fpga_required=backend == "fpga"
        )
        
        # Build command
        command = f"tcp-validate --backend {backend} --input {input_file} --output /tmp/results_{job_id}.json"
        
        # Execute job
        result = await self.submit_job(
            command=command,
            resources=resources,
            output_files=[f"/tmp/results_{job_id}.json"]
        )
        
        # Download and parse results
        if result.status == JobStatus.COMPLETED:
            local_result_file = f"/tmp/local_results_{job_id}.json"
            await self.connection.download_file(f"/tmp/results_{job_id}.json", local_result_file)
            
            with open(local_result_file, 'r') as f:
                validation_results = json.load(f)
            
            os.unlink(local_result_file)
            return validation_results
        else:
            raise RuntimeError(f"TCP validation failed: {result.stderr}")
    
    async def tcp_benchmark(self, tool_count: int = 1000, 
                          iterations: int = 100,
                          backends: List[str] = None) -> Dict[str, Any]:
        """Run TCP vs LLM benchmark comparison"""
        
        backends = backends or ["cpu", "gpu", "fpga"]
        job_id = f"tcp_benchmark_{uuid.uuid4().hex[:8]}"
        
        # Resource requirements for comprehensive benchmark
        resources = ResourceRequest(
            cpu_cores=16,
            memory_gb=64,
            gpu_count=1,
            fpga_required="fpga" in backends,
            max_runtime_hours=8
        )
        
        # Build benchmark command
        command = f"""
        tcp-benchmark \\
            --tools {tool_count} \\
            --iterations {iterations} \\
            --backends {','.join(backends)} \\
            --output /tmp/benchmark_{job_id}.json \\
            --detailed-stats \\
            --statistical-analysis
        """
        
        result = await self.submit_job(
            command=command,
            resources=resources,
            output_files=[f"/tmp/benchmark_{job_id}.json"]
        )
        
        if result.status == JobStatus.COMPLETED:
            local_result_file = f"/tmp/local_benchmark_{job_id}.json"
            await self.connection.download_file(f"/tmp/benchmark_{job_id}.json", local_result_file)
            
            with open(local_result_file, 'r') as f:
                benchmark_results = json.load(f)
            
            os.unlink(local_result_file)
            return benchmark_results
        else:
            raise RuntimeError(f"TCP benchmark failed: {result.stderr}")
    
    async def tcp_fpga_program(self, bitstream_path: str = None) -> bool:
        """Program FPGA with TCP validation bitstream"""
        
        bitstream = bitstream_path or "/opt/tcp/bitstreams/tcp_validator_v2.xclbin"
        
        # Check FPGA availability
        fpga_status = await self.get_fpga_status()
        if not fpga_status.get('available'):
            raise RuntimeError("FPGA not available or already in use")
        
        # Reserve FPGA
        await self.reserve_fpga(hours=1)
        
        try:
            # Program FPGA
            result = await self.connection.execute(
                f"sudo tcp-fpga-load {bitstream}",
                check=False
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"FPGA programming failed: {result.stderr}")
            
            # Verify programming
            verify_result = await self.connection.execute("xbutil validate -d 0")
            return verify_result.returncode == 0
            
        except Exception as e:
            # Release FPGA on failure
            await self.release_fpga()
            raise e
    
    async def tcp_distributed_experiment(self, 
                                       experiment_config: Dict[str, Any],
                                       node_count: int = 1) -> Dict[str, Any]:
        """Run distributed TCP experiment across multiple nodes"""
        
        job_id = f"tcp_distributed_{uuid.uuid4().hex[:8]}"
        
        # Upload experiment configuration
        config_file = f"/tmp/experiment_config_{job_id}.json"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(experiment_config, f, indent=2)
            local_config = f.name
        
        await self.connection.upload_file(local_config, config_file)
        os.unlink(local_config)
        
        # Resource requirements for distributed experiment
        resources = ResourceRequest(
            cpu_cores=16,
            memory_gb=128,
            gpu_count=1,
            fpga_required=experiment_config.get('use_fpga', False),
            max_runtime_hours=12
        )
        
        # Build distributed experiment command
        command = f"""
        tcp-distributed-experiment \\
            --config {config_file} \\
            --nodes {node_count} \\
            --output /tmp/distributed_results_{job_id}/ \\
            --coordinator gentoo.local
        """
        
        result = await self.submit_job(
            command=command,
            resources=resources,
            output_files=[f"/tmp/distributed_results_{job_id}/"]
        )
        
        if result.status == JobStatus.COMPLETED:
            # Download results directory
            local_results_dir = f"/tmp/local_distributed_results_{job_id}"
            os.makedirs(local_results_dir, exist_ok=True)
            
            # Download all result files
            result_files = await self.connection.execute(
                f"find /tmp/distributed_results_{job_id}/ -type f"
            )
            
            for result_file in result_files.stdout.strip().split('\n'):
                if result_file.strip():
                    local_file = os.path.join(
                        local_results_dir, 
                        os.path.basename(result_file)
                    )
                    await self.connection.download_file(result_file, local_file)
            
            # Load main results
            main_results_file = os.path.join(local_results_dir, "experiment_results.json")
            if os.path.exists(main_results_file):
                with open(main_results_file, 'r') as f:
                    return json.load(f)
        
        raise RuntimeError(f"Distributed experiment failed: {result.stderr}")
    
    # Resource management methods
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system resource status"""
        
        status_command = """
        echo "{"
        echo '"timestamp": "$(date -Iseconds)",'
        echo '"cpu": {'
        echo '  "cores": $(nproc),'
        echo '  "usage": $(top -bn1 | grep "Cpu(s)" | awk '"'"'{print $2}'"'"' | sed '"'"'s/%us,//'"'"'),'
        echo '  "load": [$(cat /proc/loadavg | cut -d" " -f1-3 | tr " " ",")]'
        echo '},'
        echo '"memory": {'
        echo '  "total_gb": $(free -g | awk '"'"'NR==2{print $2}'"'"'),'
        echo '  "used_gb": $(free -g | awk '"'"'NR==2{print $3}'"'"'),'
        echo '  "available_gb": $(free -g | awk '"'"'NR==2{print $7}'"'"')'
        echo '},'
        echo '"gpu": $(nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | awk '"'"'BEGIN{print "["} {if(NR>1) print ","; printf "{\\"index\\":%s,\\"name\\":\\"%s\\",\\"memory_used_mb\\":%s,\\"memory_total_mb\\":%s,\\"utilization\\":%s}", $1, $2, $3, $4, $5} END{print "]"}'"'"'),'
        echo '"fpga": $(xbutil examine -d 0 --format json 2>/dev/null || echo '"'"'{"available": false}'"'"'),'
        echo '"storage": $(df -BG /research | awk '"'"'NR==2{printf "{\\"total_gb\\":%d,\\"used_gb\\":%d,\\"available_gb\\":%d}", $2, $3, $4}'"'"')'
        echo "}"
        """
        
        result = await self.connection.execute(status_command)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            raise RuntimeError(f"Failed to get system status: {result.stderr}")
    
    async def get_gpu_status(self) -> List[Dict[str, Any]]:
        """Get detailed GPU status"""
        
        result = await self.connection.execute(
            "nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw --format=csv,noheader,nounits"
        )
        
        if result.returncode != 0:
            return []
        
        gpus = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = [p.strip() for p in line.split(',')]
                gpus.append({
                    'index': int(parts[0]),
                    'name': parts[1],
                    'memory_used_mb': int(parts[2]),
                    'memory_total_mb': int(parts[3]),
                    'utilization_percent': int(parts[4]),
                    'temperature_c': int(parts[5]),
                    'power_draw_w': float(parts[6]) if parts[6] != '[N/A]' else 0
                })
        
        return gpus
    
    async def get_fpga_status(self) -> Dict[str, Any]:
        """Get FPGA status and availability"""
        
        result = await self.connection.execute(
            "xbutil examine -d 0 --format json 2>/dev/null || echo '{\"available\": false}'"
        )
        
        try:
            fpga_status = json.loads(result.stdout)
            
            # Check if programmed with TCP bitstream
            if 'devices' in fpga_status:
                device_info = fpga_status['devices'][0] if fpga_status['devices'] else {}
                fpga_status['tcp_programmed'] = 'tcp_validator' in device_info.get('xclbin', {}).get('uuid', '')
            
            return fpga_status
        except:
            return {'available': False, 'error': 'FPGA not accessible'}
    
    async def reserve_gpu(self, gpu_index: int = 0, hours: int = 2) -> bool:
        """Reserve GPU for exclusive use"""
        
        result = await self.connection.execute(
            f"tcp-gpu-scheduler reserve --gpu {gpu_index} --hours {hours}"
        )
        
        return result.returncode == 0
    
    async def reserve_fpga(self, hours: int = 1) -> bool:
        """Reserve FPGA for exclusive use"""
        
        result = await self.connection.execute(
            f"tcp-fpga-scheduler reserve --hours {hours}"
        )
        
        return result.returncode == 0
    
    async def release_gpu(self, gpu_index: int = 0) -> bool:
        """Release GPU reservation"""
        
        result = await self.connection.execute(
            f"tcp-gpu-scheduler release --gpu {gpu_index}"
        )
        
        return result.returncode == 0
    
    async def release_fpga(self) -> bool:
        """Release FPGA reservation"""
        
        result = await self.connection.execute("tcp-fpga-scheduler release")
        return result.returncode == 0
    
    # Job management methods
    
    async def submit_job(self, command: str, 
                        resources: ResourceRequest = None,
                        working_dir: str = "/tmp",
                        environment: Dict[str, str] = None,
                        input_files: List[str] = None,
                        output_files: List[str] = None) -> JobResult:
        """Submit and execute job on gentoo.local"""
        
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        resources = resources or ResourceRequest()
        
        job_request = JobRequest(
            job_id=job_id,
            command=command,
            working_dir=working_dir,
            environment=environment or {},
            input_files=input_files or [],
            output_files=output_files or [],
            resources=resources
        )
        
        self.active_jobs[job_id] = job_request
        
        try:
            result = await self._execute_job(job_request)
            self.job_results[job_id] = result
            return result
            
        except Exception as e:
            result = JobResult(
                job_id=job_id,
                status=JobStatus.FAILED,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=0.0,
                resources_used={}
            )
            self.job_results[job_id] = result
            return result
        
        finally:
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
    
    async def _execute_job(self, job: JobRequest) -> JobResult:
        """Execute job with resource management"""
        
        start_time = time.time()
        
        # Reserve resources if needed
        if job.resources.gpu_count > 0:
            await self.reserve_gpu(hours=job.resources.max_runtime_hours)
        
        if job.resources.fpga_required:
            await self.reserve_fpga(hours=job.resources.max_runtime_hours)
        
        try:
            # Set resource limits
            ulimit_cmd = f"""
            ulimit -v {job.resources.memory_gb * 1024 * 1024};
            ulimit -t {job.resources.max_runtime_hours * 3600};
            cd {job.working_dir};
            """
            
            # Set environment variables
            env_cmd = ""
            for key, value in job.environment.items():
                env_cmd += f"export {key}='{value}'; "
            
            # Full command
            full_command = f"{ulimit_cmd} {env_cmd} {job.command}"
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self.connection.execute(full_command, check=False),
                timeout=job.resources.max_runtime_hours * 3600
            )
            
            execution_time = time.time() - start_time
            
            return JobResult(
                job_id=job.job_id,
                status=JobStatus.COMPLETED if result.returncode == 0 else JobStatus.FAILED,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                resources_used={
                    'cpu_time': execution_time,
                    'memory_peak_gb': 0,  # Would need additional monitoring
                },
                output_files=job.output_files
            )
            
        except asyncio.TimeoutError:
            return JobResult(
                job_id=job.job_id,
                status=JobStatus.FAILED,
                exit_code=-1,
                stdout="",
                stderr="Job timed out",
                execution_time=time.time() - start_time,
                resources_used={}
            )
        
        finally:
            # Release resources
            if job.resources.gpu_count > 0:
                await self.release_gpu()
            
            if job.resources.fpga_required:
                await self.release_fpga()
    
    async def get_job_status(self, job_id: str) -> Optional[JobResult]:
        """Get job execution status"""
        return self.job_results.get(job_id)
    
    async def list_active_jobs(self) -> List[JobRequest]:
        """List currently active jobs"""
        return list(self.active_jobs.values())
    
    # File management methods
    
    async def upload_files(self, local_paths: List[str], 
                         remote_dir: str = "/tmp") -> List[str]:
        """Upload multiple files to remote system"""
        
        remote_paths = []
        
        for local_path in local_paths:
            if os.path.isfile(local_path):
                filename = os.path.basename(local_path)
                remote_path = f"{remote_dir}/{filename}"
                await self.connection.upload_file(local_path, remote_path)
                remote_paths.append(remote_path)
            elif os.path.isdir(local_path):
                dirname = os.path.basename(local_path)
                remote_path = f"{remote_dir}/{dirname}"
                await self.connection.upload_directory(local_path, remote_path)
                remote_paths.append(remote_path)
        
        return remote_paths
    
    async def download_files(self, remote_paths: List[str], 
                           local_dir: str = "/tmp") -> List[str]:
        """Download multiple files from remote system"""
        
        os.makedirs(local_dir, exist_ok=True)
        local_paths = []
        
        for remote_path in remote_paths:
            filename = os.path.basename(remote_path)
            local_path = os.path.join(local_dir, filename)
            await self.connection.download_file(remote_path, local_path)
            local_paths.append(local_path)
        
        return local_paths
    
    # Monitoring methods
    
    async def monitor_resources(self, interval: int = 5, 
                              duration: int = 60) -> List[Dict[str, Any]]:
        """Monitor system resources over time"""
        
        measurements = []
        end_time = time.time() + duration
        
        while time.time() < end_time:
            try:
                status = await self.get_system_status()
                measurements.append(status)
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error monitoring resources: {e}")
                break
        
        return measurements

# High-level convenience functions

class TCPRemote:
    """High-level interface for TCP remote operations"""
    
    def __init__(self, host: str = None, username: str = None):
        self.orchestrator = TCPGentooOrchestrator(
            GentooConnection(host=host, username=username)
        )
    
    async def __aenter__(self):
        await self.orchestrator.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.orchestrator.__aexit__(exc_type, exc_val, exc_tb)
    
    # Simplified TCP operations
    
    async def validate(self, descriptors, backend="cpu"):
        """Validate TCP descriptors"""
        return await self.orchestrator.tcp_validate(descriptors, backend)
    
    async def benchmark(self, tools=1000, iterations=100, backends=None):
        """Run TCP benchmark"""
        return await self.orchestrator.tcp_benchmark(tools, iterations, backends)
    
    async def status(self):
        """Get system status"""
        return await self.orchestrator.get_system_status()
    
    async def gpus(self):
        """Get GPU status"""
        return await self.orchestrator.get_gpu_status()
    
    async def fpga(self):
        """Get FPGA status"""
        return await self.orchestrator.get_fpga_status()
    
    async def run(self, command, **kwargs):
        """Run arbitrary command"""
        return await self.orchestrator.submit_job(command, **kwargs)

# CLI Interface

def create_cli():
    """Create command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TCP Gentoo Hardware Orchestrator")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get system status')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate TCP descriptors')
    validate_parser.add_argument('input', help='Input file with descriptors')
    validate_parser.add_argument('--backend', choices=['cpu', 'gpu', 'fpga'], 
                               default='cpu', help='Validation backend')
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser('benchmark', help='Run TCP benchmark')
    benchmark_parser.add_argument('--tools', type=int, default=1000, 
                                help='Number of tools to test')
    benchmark_parser.add_argument('--iterations', type=int, default=100,
                                help='Iterations per tool')
    benchmark_parser.add_argument('--backends', nargs='+', 
                                choices=['cpu', 'gpu', 'fpga'],
                                default=['cpu'], help='Backends to test')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor system resources')
    monitor_parser.add_argument('--interval', type=int, default=5,
                              help='Monitoring interval in seconds')
    monitor_parser.add_argument('--duration', type=int, default=60,
                              help='Monitoring duration in seconds')
    
    return parser

async def main():
    """Main CLI entry point"""
    parser = create_cli()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    async with TCPRemote() as tcp:
        if args.command == 'status':
            status = await tcp.status()
            print(json.dumps(status, indent=2))
            
        elif args.command == 'validate':
            with open(args.input, 'rb') as f:
                descriptors = f.read()
            
            # Split into 24-byte descriptors
            descriptor_list = [descriptors[i:i+24] for i in range(0, len(descriptors), 24)]
            
            results = await tcp.validate(descriptor_list, args.backend)
            print(json.dumps(results, indent=2))
            
        elif args.command == 'benchmark':
            results = await tcp.benchmark(
                tools=args.tools,
                iterations=args.iterations,
                backends=args.backends
            )
            print(json.dumps(results, indent=2))
            
        elif args.command == 'monitor':
            print(f"Monitoring system for {args.duration} seconds...")
            measurements = await tcp.orchestrator.monitor_resources(
                interval=args.interval,
                duration=args.duration
            )
            
            print(json.dumps(measurements, indent=2))

if __name__ == "__main__":
    asyncio.run(main())