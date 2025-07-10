#!/bin/bash
ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 << 'EOF'
echo "🔧 Fixing Python environment..."

# Wait for apt lock to clear
sleep 30

# Install python venv
apt install -y python3.10-venv

# Recreate virtual environment
cd /opt/tcp-knowledge-system
rm -rf tcp-env
python3 -m venv tcp-env
source tcp-env/bin/activate
pip install --upgrade pip
pip install anthropic schedule

echo "✅ Python environment ready"
EOF