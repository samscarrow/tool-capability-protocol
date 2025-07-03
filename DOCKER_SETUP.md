# TCP Security System - Docker Setup Guide

## 🐳 Complete Dockerized Ubuntu Environment

This setup provides a fully containerized TCP Security System with:
- **Ubuntu 22.04** base environment
- **Ollama** for local LLM processing
- **Complete TCP Security System** with all components
- **Interactive tools** for demonstration and analysis
- **Persistent data** with Docker volumes
- **Privacy-first** approach - all processing stays in container

## 🚀 Quick Start

### 1. Build and Run the Container

```bash
# Build the Docker image
docker-compose build

# Start the TCP Security System
docker-compose up -d

# Access the interactive container
docker-compose exec tcp-security bash
```

### 2. Alternative: Direct Docker Commands

```bash
# Build the image
docker build -t tcp-security .

# Run with interactive shell
docker run -it \
  --name tcp-security-system \
  -p 11434:11434 \
  -v tcp_data:/tcp-security/data \
  -v ollama_models:/home/tcpuser/.ollama \
  tcp-security
```

## 🔧 Container Features

### Built-in Commands

Once inside the container, you have access to:

```bash
# Quick demonstration menu
tcp-demo

# System health check
tcp-health

# Analyze any command's security
tcp-analyze rm
tcp-analyze curl
tcp-analyze sudo

# Ollama direct access
tcp-ollama list
tcp-ollama ps

# Run specific demonstrations
python3 tcp/local_ollama_demo.py
python3 tcp/demo_complete_security_system.py
```

### Interactive TCP Shell

```bash
# Start the enhanced TCP shell
/tcp-security/tcp-shell.sh
```

This provides:
- ✅ Custom aliases for TCP commands
- ✅ Security analysis functions
- ✅ Ollama integration
- ✅ Man page enrichment tools
- ✅ Interactive demonstration menu

## 📊 System Architecture

### Container Components

```
tcp-security-system/
├── Ubuntu 22.04 base
├── Python 3.10 + virtual environment
├── Ollama service + llama3.2:latest model
├── Complete TCP Security System
├── Man pages and system tools
├── Interactive scripts and demos
└── Persistent data volumes
```

### Volume Mounts

| Volume | Purpose | Path |
|--------|---------|------|
| `tcp_data` | Application data and logs | `/tcp-security/data` |
| `tcp_cache` | Man page cache and analysis | `/tcp-security/tcp_cache` |
| `tcp_logs` | System and audit logs | `/tcp-security/logs` |
| `ollama_models` | Ollama models storage | `/home/tcpuser/.ollama` |

## 🎬 Demonstration Scenarios

### Scenario 1: Privacy-First Local Analysis

```bash
# Enter container
docker-compose exec tcp-security bash

# Run local Ollama demo
tcp-demo
# Choose option 1: Local Ollama Demo

# Result: Complete privacy-first analysis with local LLM
```

### Scenario 2: Interactive Security Analysis

```bash
# Analyze different commands
tcp-analyze ls      # Safe command
tcp-analyze rm      # Dangerous command  
tcp-analyze sudo    # Privilege escalation
tcp-analyze curl    # Network operations

# Each analysis shows:
# - Security level classification
# - Privilege requirements
# - Binary descriptor with embedded intelligence
# - Risk assessment with evidence
```

### Scenario 3: Complete System Integration

```bash
# Run full security system demo
python3 tcp/demo_complete_security_system.py

# Shows complete workflow:
# 1. Man page enrichment
# 2. Enhanced TCP encoding
# 3. Risk assessment with audit trails
# 4. Human-controlled sandbox
# 5. Naive agent security understanding
```

## 🔒 Security & Privacy Benefits

### Complete Isolation
- **✅ Containerized environment** - No impact on host system
- **✅ Air-gapped operation** - Can run without internet after initial setup
- **✅ Local processing only** - No external API dependencies
- **✅ Data sovereignty** - All data stays in your container

### Enterprise Ready
- **✅ Reproducible deployments** - Same environment everywhere
- **✅ Resource control** - Memory and CPU limits configured
- **✅ Health monitoring** - Built-in health checks
- **✅ Persistent storage** - Data survives container restarts

## 🛠 Advanced Usage

### Custom Model Configuration

```bash
# Access container shell
docker-compose exec tcp-security bash

# Install different Ollama model
ollama pull mistral:latest
ollama pull codellama:latest

# Update configuration to use different model
# Edit tcp/local_ollama_demo.py and change model_name
```

### Scaling and Performance

```bash
# Adjust resources in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G      # Increase for larger models
      cpus: '4.0'     # More cores for faster processing
```

### Production Deployment

```bash
# Run detached with restart policy
docker-compose up -d

# Monitor logs
docker-compose logs -f tcp-security

# Check health
docker-compose exec tcp-security tcp-health
```

## 📋 Troubleshooting

### Common Issues

1. **Ollama fails to start**
   ```bash
   # Check logs
   docker-compose logs tcp-security
   
   # Increase memory allocation
   # Edit docker-compose.yml memory limits
   ```

2. **Model download slow/fails**
   ```bash
   # Pre-download models on host, then copy
   docker cp model_files tcp-security-system:/home/tcpuser/.ollama/
   ```

3. **Permission issues**
   ```bash
   # Fix ownership
   docker-compose exec tcp-security chown -R tcpuser:tcpuser /tcp-security
   ```

### Health Monitoring

```bash
# Container health status
docker-compose ps

# Detailed health check
docker-compose exec tcp-security tcp-health

# Ollama service status
docker-compose exec tcp-security ollama ps
```

## 🎯 Use Cases

### 1. Security Research Environment
- Isolated environment for testing dangerous commands
- Complete audit trails for analysis
- No risk to host system

### 2. Compliance Demonstration
- Show data locality and privacy controls
- Generate audit reports for regulatory requirements
- Demonstrate human oversight mechanisms

### 3. AI Security Training
- Teach agents about command security risks
- Demonstrate naive agent binary understanding
- Show transparent risk assessment processes

### 4. Enterprise POC
- Proof of concept for secure AI automation
- Test local LLM integration
- Validate privacy-first approaches

## 🚀 Next Steps

After setup, try:

1. **Basic Analysis**: `tcp-analyze rm`
2. **Full Demo**: `tcp-demo` → Option 1
3. **Interactive Exploration**: `/tcp-security/tcp-shell.sh`
4. **Custom Analysis**: Modify commands and test security classification

## 📖 Documentation Reference

- `/tcp-security/LOCAL_OLLAMA_TCP_COMPLETE.md` - Privacy-first implementation details
- `/tcp-security/SECURITY_FIRST_TCP_COMPLETE.md` - Complete security system overview
- `/tcp-security/tcp/` - Source code and components

---

## 🎉 Ready to Deploy!

This Dockerized setup provides a complete, portable, privacy-first TCP Security System that can run anywhere Docker is available. Perfect for:

- **Development environments**
- **Security demonstrations** 
- **Compliance validation**
- **Air-gapped deployments**
- **Educational purposes**

**🐳 Docker + TCP Security = Portable Privacy-First AI Security**