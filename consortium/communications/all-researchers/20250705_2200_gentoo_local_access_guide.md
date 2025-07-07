# Gentoo.local Hardware Research Platform - Access Guide

**To**: All TCP Research Consortium Members  
**From**: Dr. Sam Mitchell, Hardware Security Engineer  
**Date**: July 5, 2025 10:00 PM  
**Priority**: 🖥️ INFRASTRUCTURE - Shared Research Resource  
**Subject**: Access and Utilization Guide for gentoo.local Hardware Platform

---

## Executive Summary

The `gentoo.local` system is our shared high-performance hardware research platform, optimized for TCP validation experiments, kernel development, and hardware acceleration research. This guide provides access instructions and usage protocols for all consortium researchers.

## System Specifications

```
Hostname: gentoo.local
IP Address: 10.0.1.42 (Internal), tcp-gentoo.consortium.net (External)
OS: Gentoo Linux (Hardened/SELinux Profile)
Kernel: 6.8.0-tcp-optimized (Custom build with TCP modules)

Hardware:
- CPU: AMD Ryzen 9 7950X (16 cores, 32 threads @ 5.7GHz boost)
- Memory: 128GB DDR5-6000 ECC
- Storage: 
  - 2TB NVMe PCIe 5.0 (OS/Software) - bcachefs
  - 8TB NVMe PCIe 4.0 RAID-0 (Research data)
  - 100TB NAS (Backup/Archive)
- GPU: NVIDIA RTX 4090 (24GB VRAM)
- FPGA: Xilinx Alveo U250 Data Center Accelerator
- Network: 10GbE + 100GbE research network
```

## Access Methods

### 1. SSH Access (Primary Method)

```bash
# Standard SSH access
ssh <your-username>@tcp-gentoo.consortium.net

# With key authentication (recommended)
ssh -i ~/.ssh/tcp_rsa <your-username>@tcp-gentoo.consortium.net

# Internal network access
ssh <your-username>@10.0.1.42
```

### 2. Remote Desktop (For GUI Applications)

```bash
# VNC access (requires VPN)
vncviewer tcp-gentoo.consortium.net:5901

# X11 forwarding for lightweight GUI
ssh -X <your-username>@tcp-gentoo.consortium.net

# Full desktop via NoMachine (best performance)
# Download client from: https://www.nomachine.com/
# Connect to: tcp-gentoo.consortium.net:4000
```

### 3. Jupyter Hub (For Interactive Research)

```
URL: https://tcp-gentoo.consortium.net:8000
Login: Use your consortium credentials
```

## User Account Setup

### Initial Setup (First Login)

```bash
# 1. Change your temporary password
passwd

# 2. Generate SSH keys if needed
ssh-keygen -t ed25519 -C "your-name@tcp-consortium"

# 3. Configure your research environment
/opt/tcp/scripts/setup-researcher-env.sh

# 4. Join appropriate research groups
# Contact Sam Mitchell for group assignments
```

### Research Directories

```bash
# Your home directory
/home/<username>/

# Shared research data
/research/tcp/shared/

# Your research workspace
/research/tcp/users/<username>/

# Consortium tools and scripts
/opt/tcp/

# Hardware acceleration workspace
/opt/tcp/hardware/

# FPGA bitstreams and tools
/opt/xilinx/
```

## Resource Allocation & Scheduling

### CPU/Memory Allocation

We use cgroups v2 for fair resource sharing:

```bash
# Check your current allocation
cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/memory.current
cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/cpu.weight

# Default allocations per researcher:
# - CPU: 4 cores guaranteed, 8 cores burstable
# - Memory: 16GB guaranteed, 32GB burstable
# - Storage: 1TB in /research/tcp/users/<username>/
```

### GPU Access (Shared Resource)

```bash
# Check GPU availability
nvidia-smi

# Reserve GPU for exclusive use (max 4 hours)
tcp-gpu-scheduler reserve --hours 2 --gpu 0

# Submit GPU job to queue
tcp-gpu-scheduler submit --script my_gpu_job.py --memory 16G

# Check your GPU quota
tcp-gpu-scheduler quota
```

### FPGA Access (Requires Approval)

```bash
# Check FPGA status
xbutil examine -d 0

# Reserve FPGA time slot
tcp-fpga-scheduler reserve --hours 1 --project "TCP Validation"

# Load TCP bitstream
sudo tcp-fpga-load tcp_validator_v2.xclbin

# Run FPGA accelerated validation
tcp-validate --backend fpga --input descriptors.bin
```

## TCP-Specific Tools & Environments

### Pre-installed TCP Software

```bash
# TCP core implementation
/opt/tcp/bin/tcp-validate     # Binary validation tool
/opt/tcp/bin/tcp-encode       # Descriptor encoder
/opt/tcp/bin/tcp-benchmark    # Performance testing

# Research environments
/opt/tcp/envs/elena-stats     # Elena's statistical frameworks
/opt/tcp/envs/marcus-dist     # Marcus's distributed systems
/opt/tcp/envs/yuki-perf      # Yuki's performance tools
/opt/tcp/envs/aria-security   # Aria's security toolkit
/opt/tcp/envs/alex-quality    # Alex's quality frameworks

# Activate an environment
source /opt/tcp/envs/<env-name>/bin/activate
```

### Kernel Development Tools

```bash
# Kernel source with TCP patches
cd /usr/src/linux-tcp

# Build kernel with TCP modules
make menuconfig  # TCP options under Device Drivers > TCP Acceleration
make -j32
sudo make modules_install
sudo make install

# Load TCP kernel modules
sudo modprobe tcp_validator
sudo modprobe tcp_ebpf_monitor

# Check module status
lsmod | grep tcp
```

### Hardware Monitoring

```bash
# Real-time system monitoring
htop  # CPU/Memory
iotop # Disk I/O
iftop # Network I/O
nvtop # GPU monitoring

# TCP-specific monitoring
tcp-monitor         # Overall TCP subsystem status
tcp-monitor --fpga  # FPGA utilization
tcp-monitor --ebpf  # eBPF program statistics
```

## Collaboration Protocols

### 1. Resource Sharing Etiquette

```bash
# Before running intensive jobs:
# 1. Check system load
uptime
tcp-who  # See who's currently working

# 2. Announce in Slack #gentoo-local channel
# "Planning to run 4-hour FPGA experiment starting at 2pm"

# 3. Use nice for lower priority jobs
nice -n 10 ./my_background_job.sh

# 4. Set resource limits
ulimit -v 32000000  # 32GB memory limit
ulimit -t 14400     # 4 hour CPU time limit
```

### 2. Data Management

```bash
# Shared datasets location
/research/tcp/datasets/
├── benchmarks/     # Standard TCP benchmark data
├── tools/          # Real tool descriptors
├── results/        # Shared experimental results
└── models/         # Trained models and checkpoints

# Naming convention for shared data:
# YYYYMMDD_researcher_description/
# Example: 20250705_sam_fpga_validation_results/

# Before creating large datasets:
df -h /research  # Check available space
```

### 3. Scheduled Maintenance Windows

```
Weekly Maintenance: Sundays 2-4 AM EST
- Kernel updates
- Security patches  
- Backup operations
- Hardware diagnostics

Monthly Deep Maintenance: First Sunday 2-6 AM EST
- Full system updates
- FPGA bitstream updates
- Research environment updates
```

## Best Practices

### 1. Environment Management

```bash
# Always use virtual environments for Python
python -m venv ~/envs/my_project
source ~/envs/my_project/bin/activate

# Use tcp-modules for consistent environments
module load tcp/latest
module load cuda/12.3
module load xilinx/2024.1

# Save your environment
module save my_research_env
```

### 2. Job Management

```bash
# Use screen or tmux for long-running jobs
screen -S experiment_name
# Run your experiment
# Detach: Ctrl+A, D
# Reattach: screen -r experiment_name

# For batch jobs, use our job scheduler
tcp-batch submit --cpus 8 --memory 32G --time 4h my_job.sh
tcp-batch status
tcp-batch cancel <job_id>
```

### 3. Backup Procedures

```bash
# Automatic backups run nightly for:
# - /home/<username>/
# - /research/tcp/users/<username>/

# Manual backup for important results
tcp-backup create --source ./results --tag "gate6_validation"
tcp-backup list
tcp-backup restore --tag "gate6_validation" --dest ./restored_results
```

## Security Protocols

### Access Security

```bash
# Required: 2FA for external access
# Setup: tcp-2fa-setup

# VPN required for certain operations:
# - FPGA programming
# - Root operations
# - Internal service access

# Connection: tcp-vpn connect
```

### Data Security

```bash
# Sensitive data must be encrypted
tcp-encrypt ./sensitive_data/
tcp-decrypt ./sensitive_data.enc

# Use GPG for sharing sensitive files
gpg --encrypt --recipient researcher@tcp ./secret_results.tar
```

## Troubleshooting

### Common Issues

```bash
# GPU not available
nvidia-smi  # Check if GPU is in use
tcp-gpu-scheduler status  # See reservation schedule

# FPGA programming fails
dmesg | tail -50  # Check kernel messages
xbutil validate -d 0  # Run FPGA diagnostics

# Out of memory
free -h  # Check memory usage
ps aux --sort=-%mem | head  # Find memory hogs

# Disk quota exceeded
quota -s  # Check your quota
du -sh ~/.[!.]* ~/* | sort -h  # Find large files
```

### Getting Help

```bash
# System documentation
man tcp-tools
info tcp-guide

# Get help from admins
tcp-help "Description of issue"

# Emergency contact (system down)
# Slack: @sam-mitchell
# Email: sam.mitchell@tcp-consortium.org
# Phone: [Available in Slack profile]
```

## Resource Reservation Calendar

Access the shared calendar for planning:
https://tcp-gentoo.consortium.net/calendar

Reserve resources in advance for:
- Exclusive GPU access (>2 hours)
- FPGA usage (any duration)
- High CPU experiments (>16 cores)
- Large memory jobs (>64GB)

## Quick Reference Card

```bash
# Essential Commands
ssh <username>@tcp-gentoo.consortium.net    # Connect
tcp-status                                   # System status
tcp-gpu-scheduler status                     # GPU availability
tcp-fpga-status                             # FPGA status
module avail                                # Available software
tcp-monitor                                 # Performance metrics
tcp-backup create --source ./              # Backup data
tcp-help "issue"                           # Get help

# Research Paths
/opt/tcp/                                   # TCP tools
/research/tcp/shared/                       # Shared data
/research/tcp/users/<username>/             # Your workspace
~/envs/                                     # Your environments
```

## Updates & Announcements

- **Slack Channel**: #gentoo-local
- **Status Page**: https://status.tcp-consortium.org
- **Documentation**: https://docs.tcp-consortium.org/gentoo-local

## Acknowledgment

By using gentoo.local, you agree to:
1. Share resources fairly with other researchers
2. Follow security protocols and data handling guidelines
3. Acknowledge the TCP Research Consortium in publications
4. Report any security concerns immediately

---

**Welcome to gentoo.local - Our shared platform for revolutionary TCP research!**

For hardware-specific TCP research questions, contact me directly.

**Dr. Sam Mitchell**  
Hardware Security Engineer  
sam.mitchell@tcp-consortium.org

*"Real TCP validation happens on real hardware - let's make it count!"*