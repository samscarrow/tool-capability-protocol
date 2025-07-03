# TCP Security System - Docker Deployment

## 🐳 Dockerized Ubuntu Environment

This provides a complete Ubuntu environment with the TCP Security System, including:

- **Ubuntu 22.04** base with all necessary tools
- **Ollama** for local LLM processing
- **Python 3** with TCP security components
- **Man pages** for security analysis
- **Secure sandbox** environment
- **Complete isolation** and portability

## 🚀 Quick Start

### Option 1: Using the Docker Runner Script (Recommended)

```bash
# Build the Docker image
./docker-run.sh build

# Run the container interactively
./docker-run.sh run

# Once inside the container, run demos:
python tcp/local_ollama_demo.py
```

### Option 2: Using Docker Compose

```bash
# Start the entire stack
docker-compose up -d

# Open a shell in the container
docker-compose exec tcp-security bash

# Run demos inside container
python tcp/local_ollama_demo.py
```

### Option 3: Manual Docker Commands

```bash
# Build image
docker build -t tcp-security .

# Run container
docker run -it --name tcp-security-system \
  -p 11434:11434 \
  -v tcp-data:/tcp-security/data \
  tcp-security
```

## 📋 Available Commands

The `docker-run.sh` script provides convenient management:

```bash
./docker-run.sh build      # Build the image
./docker-run.sh run        # Run container interactively
./docker-run.sh start      # Start existing container
./docker-run.sh stop       # Stop container
./docker-run.sh shell      # Open shell in running container
./docker-run.sh demo       # Run Ollama demo
./docker-run.sh security   # Run security demo
./docker-run.sh status     # Show container status
./docker-run.sh logs       # Show container logs
./docker-run.sh health     # Check health status
./docker-run.sh clean      # Remove container and image
```

## 🔧 Container Features

### Installed Components
- **Ubuntu 22.04** with essential tools
- **Python 3.10+** with virtual environment
- **Ollama** for local LLM processing
- **Man pages** (comprehensive collection)
- **TCP Security System** (all components)
- **Development tools** (vim, git, curl, etc.)

### Security Features
- **Non-root user** (`tcpuser`) for running applications
- **Resource limits** (4GB RAM, 2 CPU cores)
- **Security options** (`no-new-privileges`)
- **Network isolation** (custom bridge network)
- **Volume isolation** (separate volumes for data/cache/logs)

### Persistent Storage
- **tcp-data**: Application data and configurations
- **tcp-cache**: Man page and analysis cache
- **tcp-logs**: Audit trails and system logs
- **tcp-models**: Ollama model storage

## 🏃‍♂️ Running Demonstrations

### Inside the Container

Once you're in the container shell:

```bash
# Activate Python environment (auto-activated)
source /tcp-security/venv/bin/activate

# Run local Ollama demonstration
python tcp/local_ollama_demo.py

# Run complete security system demo
python tcp/demo_complete_security_system.py

# Test individual components
python tcp/enrichment/manpage_enricher.py
python tcp/security/sandbox_manager.py
```

### From Outside the Container

```bash
# Run demos directly from host
./docker-run.sh demo       # Local Ollama demo
./docker-run.sh security   # Complete security demo

# Or run custom commands
docker exec -it tcp-security-system python tcp/local_ollama_demo.py
```

## 🔍 System Architecture

### Container Layout
```
/tcp-security/
├── tcp/                    # Main TCP system code
│   ├── enrichment/         # Man page enrichment
│   ├── security/           # Sandbox and security
│   └── *.py               # Demo scripts
├── data/                   # Persistent application data
├── cache/                  # Man page and analysis cache
├── logs/                   # Audit and system logs
├── venv/                   # Python virtual environment
└── start-tcp.sh          # Container startup script
```

### Network Configuration
- **Port 11434**: Ollama API (exposed to host)
- **Port 8080**: Optional web interface
- **Custom network**: `tcp-security-network` for isolation

### Health Monitoring
- **Health check**: Verifies Ollama responsiveness every 30s
- **Startup grace period**: 60s for Ollama model loading
- **Automatic restart**: Unless explicitly stopped

## 🛡️ Security Considerations

### Container Security
- **Non-privileged user**: Applications run as `tcpuser`
- **No new privileges**: Prevents privilege escalation
- **Resource limits**: Prevents resource exhaustion
- **Read-only mounts**: Where appropriate for security
- **Network isolation**: Custom bridge network

### TCP Security Features
- **Local-only processing**: No external API dependencies
- **Human approval required**: For all tool access
- **Complete audit trails**: All operations logged
- **Sandbox isolation**: Tools run in controlled environment

## 🔧 Development & Customization

### Mounting Development Code
```bash
# Mount local development directory
docker run -it \
  -v $(pwd)/tcp:/tcp-security/tcp-dev \
  tcp-security bash
```

### Environment Variables
```bash
# Customize behavior
docker run -it \
  -e TCP_SECURITY_LEVEL=strict \
  -e TCP_AUDIT_ENABLED=true \
  -e TCP_LOCAL_ONLY=true \
  tcp-security
```

### Adding Custom Models
```bash
# Exec into running container
docker exec -it tcp-security-system bash

# Pull additional models
ollama pull llama3.1:latest
ollama pull codellama:latest
```

## 📊 Monitoring & Troubleshooting

### Check Container Status
```bash
./docker-run.sh status     # Overall status
./docker-run.sh health     # Health check details
./docker-run.sh logs       # View logs
```

### Debugging Issues
```bash
# Get shell access
./docker-run.sh shell

# Check Ollama status
curl http://localhost:11434/api/tags

# Check Python environment
source /tcp-security/venv/bin/activate
python --version

# Check TCP components
python -c "from tcp.enrichment.manpage_enricher import ManPageEnricher; print('TCP imports OK')"
```

### Resource Monitoring
```bash
# Monitor resource usage
docker stats tcp-security-system

# Check disk usage
docker system df
```

## 🚀 Production Deployment

### Scaling Considerations
- **Memory**: Minimum 4GB for Ollama models
- **CPU**: 2+ cores recommended for LLM processing
- **Storage**: 10GB+ for models and cache
- **Network**: Isolated network for security

### Backup & Recovery
```bash
# Backup volumes
docker run --rm \
  -v tcp-security-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/tcp-data-backup.tar.gz -C /data .

# Restore volumes
docker run --rm \
  -v tcp-security-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/tcp-data-backup.tar.gz -C /data
```

## 🎯 Benefits of Docker Deployment

### ✅ **Portability**
- **Consistent environment** across different systems
- **Easy deployment** on any Docker-capable host
- **Version control** of entire system stack
- **Reproducible builds** and deployments

### ✅ **Isolation**
- **Security isolation** from host system
- **Resource control** and limits
- **Network isolation** for security
- **Clean separation** of concerns

### ✅ **Scalability**
- **Horizontal scaling** with container orchestration
- **Resource allocation** based on workload
- **Load balancing** across multiple instances
- **Easy upgrades** and rollbacks

### ✅ **Development**
- **Consistent dev environment** for all team members
- **Easy onboarding** for new developers
- **Testing isolation** from host system
- **CI/CD integration** ready

## 🎉 Ready to Deploy!

The TCP Security System is now fully containerized and ready for:

- **Development environments**
- **Testing and validation**
- **Production deployments**
- **Air-gapped installations**
- **Cloud or on-premises hosting**

Start with `./docker-run.sh build` and explore the privacy-first TCP security system in a completely isolated, portable environment!