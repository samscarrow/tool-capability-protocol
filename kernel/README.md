# TCP Kernel Integration Module

## Overview

This kernel module demonstrates the integration of TCP (Tool Capability Protocol) directly into the Linux kernel, providing deep system-level security that operates below userspace applications.

## Features

- **System Call Monitoring**: Intercepts and analyzes system calls before execution
- **TCP Descriptor Database**: Kernel-space database of command security profiles
- **Real-time Security Analysis**: Sub-microsecond security decisions
- **Performance Optimized**: Fast-path optimization for benign operations
- **Configurable Security Levels**: Adaptive security based on threat level
- **Comprehensive Logging**: Detailed audit trail of security events

## Architecture

```
┌─────────────────────────────────────┐
│         User Applications           │
├─────────────────────────────────────┤
│          System Calls              │
├─────────────────────────────────────┤
│        TCP Kernel Module            │ ← This Module
│   ┌─────────────┬─────────────────┐ │
│   │ Descriptor  │ Security        │ │
│   │ Database    │ Analysis        │ │
│   └─────────────┴─────────────────┘ │
├─────────────────────────────────────┤
│         Linux Kernel               │
└─────────────────────────────────────┘
```

## Building

### Prerequisites

```bash
# Install kernel headers (Ubuntu/Debian)
sudo apt-get install linux-headers-$(uname -r)

# Install kernel headers (CentOS/RHEL)
sudo yum install kernel-devel

# Install kernel headers (Fedora)
sudo dnf install kernel-devel
```

### Compilation

```bash
# Build the module
make

# Check kernel compatibility
make check

# Build with verbose output (for debugging)
make dev
```

## Installation and Usage

### Quick Test

```bash
# Build, load, test, and show status (requires root)
sudo make test
```

### Manual Installation

```bash
# Build the module
make

# Load the module
sudo make load

# Check status
cat /proc/tcp_kernel

# View kernel messages
dmesg | tail -20 | grep TCP

# Unload the module
sudo make unload
```

### Persistent Installation

```bash
# Install to system modules directory
sudo make install

# Load module automatically at boot
echo "tcp_kernel" | sudo tee -a /etc/modules

# Load immediately
sudo modprobe tcp_kernel
```

## Configuration

### Security Levels

The module supports different security levels:

- **Level 0 (Minimal)**: Only monitors critical system calls
- **Level 1 (Normal)**: Standard protection (default)
- **Level 2 (Paranoid)**: Blocks critical operations from non-root users
- **Level 3 (Learning)**: Machine learning mode (future feature)

### Runtime Configuration

```bash
# View current status
cat /proc/tcp_kernel

# Check loaded modules
lsmod | grep tcp_kernel

# View detailed module information
modinfo tcp_kernel.ko
```

## Monitoring and Analysis

### Real-time Monitoring

```bash
# Watch TCP events in real-time
sudo dmesg -w | grep TCP

# Monitor statistics
watch -n 1 'cat /proc/tcp_kernel | grep -A 10 "Statistics:"'
```

### Performance Testing

```bash
# Run performance benchmarks
sudo make perf-test

# Test security functionality
sudo make security-test
```

### Log Analysis

```bash
# Check recent TCP security events
journalctl -k | grep TCP | tail -20

# Count blocked operations
dmesg | grep "TCP.*Blocking" | wc -l

# Show most recent security alerts
dmesg | grep "TCP.*Critical" | tail -10
```

## TCP Descriptor Database

The module includes a kernel-space database of TCP descriptors:

### Example Descriptors

| System Call | Security Flags | Pattern | Risk Level |
|-------------|----------------|---------|------------|
| `unlink()` | DESTRUCTIVE, FILESYSTEM | file_deletion | Medium |
| `execve()` | EXECUTION, CRITICAL | program_exec | High |
| `init_module()` | CRITICAL, KERNEL | module_load | Critical |
| `getpid()` | SAFE | pid_query | None |

### Adding Custom Descriptors

Modify the `tcp_descriptors` array in `tcp_kernel_module.c`:

```c
{
    .syscall_nr = __NR_your_syscall,
    .security_flags = TCP_FLAG_DESTRUCTIVE,
    .context_mask = TCP_CTX_ADMIN,
    .privilege_level = TCP_PRIV_ROOT,
    .pattern = "your_pattern",
    .checksum = 0x12345678
}
```

## Security Analysis

### Threat Detection

The module can detect and respond to:

1. **Privilege Escalation Attempts**
   - Unexpected UID changes
   - Kernel memory access from userspace

2. **Container Escape Attempts**
   - Namespace boundary violations
   - Privilege operations from containers

3. **Rootkit Activity**
   - System call table modifications
   - Kernel module tampering

4. **Malicious Operations**
   - Destructive file operations
   - Unauthorized kernel module loading

### Response Actions

- **Logging**: All security events are logged to kernel log
- **Blocking**: Critical operations can be blocked (configurable)
- **Alerting**: Real-time notifications of security events
- **Statistics**: Performance and security metrics collection

## Performance Characteristics

### Typical Overhead

- **Safe system calls**: < 100 nanoseconds overhead
- **Analyzed calls**: < 1 microsecond overhead
- **Total system impact**: < 2% for typical workloads

### Optimization Features

- **Fast-path processing**: Immediate approval for known-safe operations
- **Hash table lookups**: O(1) descriptor database access
- **Atomic operations**: Lock-free statistics collection
- **Selective monitoring**: Focus on high-risk operations

## Troubleshooting

### Common Issues

1. **Module won't load**
   ```bash
   # Check kernel headers
   make check
   
   # Rebuild module
   make clean && make
   ```

2. **Permission denied**
   ```bash
   # Ensure root privileges
   sudo make load
   ```

3. **High performance impact**
   ```bash
   # Check if in paranoid mode
   cat /proc/tcp_kernel | grep "Security Level"
   ```

### Debug Information

```bash
# Enable debug output
echo 8 > /proc/sys/kernel/printk

# View debug messages
dmesg | grep TCP

# Check module parameters
cat /sys/module/tcp_kernel/parameters/*
```

## Development

### Adding New Features

1. **Modify source code**: Edit `tcp_kernel_module.c`
2. **Rebuild**: `make clean && make`
3. **Test**: `sudo make test`
4. **Debug**: `make dev` for verbose compilation

### Testing Framework

```bash
# Unit tests
sudo make test

# Performance benchmarks
sudo make perf-test

# Security validation
sudo make security-test
```

## Security Considerations

### Self-Protection

The module includes basic self-protection mechanisms:

- Integrity checking of module code
- Protection against tampering
- Secure initialization and cleanup

### Limitations

- **Not a complete security solution**: Should be used as part of layered security
- **Performance impact**: May affect high-throughput applications
- **Compatibility**: Requires recent Linux kernel (5.4+)

### Best Practices

1. **Test thoroughly** before production deployment
2. **Monitor performance** impact on critical workloads
3. **Regular updates** to descriptor database
4. **Integrate with existing** security monitoring tools

## License

This module is licensed under GPL v2, compatible with the Linux kernel.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions:

- Check the troubleshooting section
- Review kernel logs: `dmesg | grep TCP`
- Verify kernel compatibility: `make check`
- Test with minimal configuration: `sudo make test`