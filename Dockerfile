# TCP Security System with Ollama on Ubuntu
FROM ubuntu:22.04

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /tcp-security

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    man-db \
    manpages \
    manpages-dev \
    build-essential \
    git \
    vim \
    less \
    grep \
    coreutils \
    util-linux \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Create a non-root user for running the application
RUN useradd -m -s /bin/bash tcpuser && \
    usermod -aG sudo tcpuser

# Copy TCP security system files
COPY tcp/ ./tcp/
COPY *.py ./
COPY *.md ./

# Set up Python virtual environment
RUN python3 -m venv /opt/tcp-venv && \
    /opt/tcp-venv/bin/pip install --upgrade pip

# Create startup script with proper escaping
RUN cat > /tcp-security/start-tcp-system.sh << 'EOF'
#!/bin/bash

echo "🐳 Starting TCP Security System in Docker"
echo "=========================================="

# Start Ollama service in background
echo "🚀 Starting Ollama service..."
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Ollama failed to start in 30 seconds"
        exit 1
    fi
    sleep 1
done

# Pull the default model
echo "📥 Pulling llama3.2:latest model (this may take a while)..."
ollama pull llama3.2:latest

echo "🎯 Ollama setup complete!"
echo ""
echo "🔐 TCP Security System is ready!"
echo "================================"
echo ""
echo "Available commands:"
echo "  python3 tcp/local_ollama_demo.py        - Run local Ollama demonstration"
echo "  python3 tcp/demo_complete_security_system.py - Run complete security demo"
echo "  python3 tcp/enrichment/manpage_enricher.py  - Test man page enrichment"
echo "  python3 tcp/security/secure_tcp_agent.py    - Test secure agent"
echo ""
echo "📊 System Status:"
echo "  Ollama:    ✅ Running (PID: $OLLAMA_PID)"
echo "  Model:     ✅ llama3.2:latest"
echo "  TCP:       ✅ Ready"
echo "  Ubuntu:    ✅ $(lsb_release -d | cut -f2)"
echo ""
echo "🏠 All processing is local - no external APIs needed!"
echo ""

# Keep container running and show logs
echo "📋 Monitoring Ollama service..."
echo "   (Ctrl+C to stop, then 'exit' to close container)"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down TCP Security System..."
    kill $OLLAMA_PID 2>/dev/null
    echo "✅ Ollama stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Monitor Ollama and keep container alive
while kill -0 $OLLAMA_PID 2>/dev/null; do
    sleep 5
done

echo "❌ Ollama service stopped unexpectedly"
exit 1
EOF

# Make startup script executable
RUN chmod +x /tcp-security/start-tcp-system.sh

# Create demo runner script
RUN cat > /tcp-security/run-demo.sh << 'EOF'
#!/bin/bash

echo "🎬 TCP Security System Demo Runner"
echo "=================================="
echo ""
echo "Which demonstration would you like to run?"
echo ""
echo "1) Local Ollama Demo (Privacy-first with local LLM)"
echo "2) Complete Security System Demo (Full integration)"
echo "3) Man Page Enrichment Test"
echo "4) Secure Agent Test" 
echo "5) Interactive Shell"
echo ""
read -p "Choose option (1-5): " choice

case $choice in
    1)
        echo "🏠 Running Local Ollama Demo..."
        python3 tcp/local_ollama_demo.py
        ;;
    2)
        echo "🔐 Running Complete Security System Demo..."
        python3 tcp/demo_complete_security_system.py
        ;;
    3)
        echo "📚 Testing Man Page Enrichment..."
        python3 tcp/enrichment/manpage_enricher.py
        ;;
    4)
        echo "🤖 Testing Secure Agent..."
        python3 tcp/security/secure_tcp_agent.py
        ;;
    5)
        echo "🐚 Starting interactive shell..."
        echo "Available commands:"
        echo "  python3 tcp/local_ollama_demo.py"
        echo "  python3 tcp/demo_complete_security_system.py"
        echo "  ollama list"
        echo "  ollama ps"
        bash
        ;;
    *)
        echo "❌ Invalid option. Please choose 1-5."
        exit 1
        ;;
esac
EOF

RUN chmod +x /tcp-security/run-demo.sh

# Create health check script
RUN cat > /tcp-security/health-check.sh << 'EOF'
#!/bin/bash

echo "🏥 TCP Security System Health Check"
echo "==================================="

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama service: Running"
    
    # Check models
    models=$(ollama list 2>/dev/null | grep -v "NAME" | wc -l)
    if [ $models -gt 0 ]; then
        echo "✅ Ollama models: $models available"
        ollama list
    else
        echo "⚠️  Ollama models: None installed"
    fi
else
    echo "❌ Ollama service: Not running"
fi

# Check Python
if python3 --version > /dev/null 2>&1; then
    echo "✅ Python: $(python3 --version)"
else
    echo "❌ Python: Not available"
fi

# Check TCP system files
if [ -f "tcp/local_ollama_demo.py" ]; then
    echo "✅ TCP system: Files present"
else
    echo "❌ TCP system: Files missing"
fi

# Check man pages
if man ls > /dev/null 2>&1; then
    echo "✅ Man pages: Available"
else
    echo "❌ Man pages: Not available"
fi

# System info
echo ""
echo "📊 System Information:"
echo "   OS: $(lsb_release -d | cut -f2)"
echo "   Kernel: $(uname -r)"
echo "   Architecture: $(uname -m)"
echo "   Memory: $(free -h | grep Mem | awk '{print $2}')"
echo "   Disk: $(df -h / | tail -1 | awk '{print $4}') available"
EOF

RUN chmod +x /tcp-security/health-check.sh

# Create interactive TCP shell script
RUN cat > /tcp-security/tcp-shell.sh << 'EOF'
#!/bin/bash

echo "🔐 TCP Security Interactive Shell"
echo "================================="
echo ""
echo "This is a secure TCP environment with:"
echo "  • Local Ollama LLM for security analysis"
echo "  • Enhanced TCP descriptors with embedded security"
echo "  • Human-controlled sandbox for tool execution"
echo "  • Complete privacy - all processing local"
echo ""
echo "Quick commands:"
echo "  tcp-demo     - Run demonstration menu"
echo "  tcp-health   - Check system health"
echo "  tcp-ollama   - Interact with Ollama directly"
echo "  tcp-analyze  - Analyze a command's security"
echo ""

# Add custom aliases
alias tcp-demo='/tcp-security/run-demo.sh'
alias tcp-health='/tcp-security/health-check.sh'
alias tcp-ollama='ollama'

# Function to analyze a command
tcp-analyze() {
    if [ -z "$1" ]; then
        echo "Usage: tcp-analyze <command>"
        echo "Example: tcp-analyze rm"
        return 1
    fi
    
    echo "🔍 Analyzing command: $1"
    python3 -c "
from tcp.enrichment.manpage_enricher import ManPageEnricher
from tcp.enrichment.tcp_encoder import EnrichedTCPEncoder
from tcp.enrichment.risk_assessment_auditor import TransparentRiskAssessor

enricher = ManPageEnricher()
encoder = EnrichedTCPEncoder(enricher)
assessor = TransparentRiskAssessor()

command = '$1'
print(f'📋 Processing: {command}')

# Get man page data
man_data = enricher.enrich_command(command)
if man_data:
    print(f'✅ Security Level: {man_data.security_level.value}')
    print(f'✅ Privileges: {man_data.privilege_requirements.value}')
    
    # Generate TCP descriptor
    descriptor = encoder.encode_enhanced_tcp(command)
    binary_data = encoder.to_binary(descriptor)
    
    print(f'✅ Binary Size: {len(binary_data)} bytes')
    print(f'✅ Security Flags: 0x{descriptor.security_flags:08x}')
    
    # Risk assessment
    audit = assessor.assess_command_risk(command, man_data)
    print(f'✅ Risk Score: {audit.security_score:.3f}')
    print(f'✅ Evidence Pieces: {len(audit.risk_evidence)}')
else:
    print('❌ Failed to analyze command')
"
}

export -f tcp-analyze

echo "🚀 TCP Security Shell ready! Try 'tcp-demo' to get started."
bash
EOF

RUN chmod +x /tcp-security/tcp-shell.sh

# Set proper ownership
RUN chown -R tcpuser:tcpuser /tcp-security

# Switch to non-root user
USER tcpuser

# Set environment variables
ENV PATH="/opt/tcp-venv/bin:$PATH"
ENV OLLAMA_HOST="0.0.0.0:11434"

# Expose Ollama port (optional, for external access)
EXPOSE 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Default command starts the full system
CMD ["/tcp-security/start-tcp-system.sh"]