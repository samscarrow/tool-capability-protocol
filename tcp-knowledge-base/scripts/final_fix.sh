#!/bin/bash
ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 << 'EOF'
echo "🔧 Final TCP System Fix..."

# Install required packages
DEBIAN_FRONTEND=noninteractive apt install -y python3.10-venv python3-pip python3-setuptools

# Recreate virtual environment properly
cd /opt/tcp-knowledge-system
rm -rf tcp-env
python3 -m venv tcp-env

# Activate and install packages using system pip first
/opt/tcp-knowledge-system/tcp-env/bin/python -m ensurepip --upgrade
/opt/tcp-knowledge-system/tcp-env/bin/pip install --upgrade pip
/opt/tcp-knowledge-system/tcp-env/bin/pip install anthropic schedule

echo "✅ Python environment ready"

# Test import
/opt/tcp-knowledge-system/tcp-env/bin/python -c "import anthropic; print('Anthropic library working')"

# Fix permissions
chown -R tcp:tcp /opt/tcp-knowledge-system

# Restart service
systemctl restart tcp-knowledge-growth
sleep 3
systemctl status tcp-knowledge-growth --no-pager

echo "✅ TCP system should now be running!"
EOF