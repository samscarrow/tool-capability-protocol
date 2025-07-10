#!/bin/bash
ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 << 'EOF'
echo "📦 Installing required packages..."
apt update
apt install -y python3.10-venv python3-pip

echo "✅ Packages installed"
EOF