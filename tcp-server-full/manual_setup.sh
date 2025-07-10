#!/bin/bash
ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 << 'EOF'
echo "🚀 Manual TCP Setup"

# Update system first
apt-get update 

# Install basic packages
apt-get install -y python3 python3-pip python3-venv man-db jq

# Create directories
mkdir -p /opt/tcp-knowledge-system/{data,patterns,logs,scripts,backups}

# Setup Python environment
cd /opt/tcp-knowledge-system
python3 -m venv tcp-env
source tcp-env/bin/activate
pip install anthropic schedule

echo "✅ Basic setup complete"
ls -la /opt/tcp-knowledge-system/
EOF