#!/bin/bash
"""
Enhanced TCP DigitalOcean deployment with 1Password secrets
"""

set -euo pipefail

# Load 1Password secrets
source ~/.config/op-secrets.sh

# Get API keys from 1Password
export ANTHROPIC_API_KEY=$(op_secret anthropic)
export DO_API_TOKEN=$(op_secret digitalocean)

# Validate secrets
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Failed to get Anthropic API key from 1Password"
    exit 1
fi

if [ -z "$DO_API_TOKEN" ]; then
    echo "❌ Failed to get DigitalOcean API token from 1Password" 
    exit 1
fi

echo "✅ Secrets loaded from 1Password"

# Set doctl authentication
doctl auth init --access-token "$DO_API_TOKEN"

# Configuration
DROPLET_NAME="tcp-knowledge-growth"
DROPLET_SIZE="s-2vcpu-4gb"  # $24/month
DROPLET_REGION="nyc1" 
DROPLET_IMAGE="ubuntu-22-04-x64"

echo "🌊 Deploying TCP Knowledge Growth to DigitalOcean"
echo "Droplet: $DROPLET_NAME ($DROPLET_SIZE in $DROPLET_REGION)"

# Create or get droplet
if ! doctl compute droplet list | grep -q "$DROPLET_NAME"; then
    echo "📦 Creating new droplet..."
    
    # Ensure SSH key exists
    if ! doctl compute ssh-key list | grep -q "tcp-deployment"; then
        echo "🔑 Creating SSH key..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/tcp_deployment_key -N ""
        doctl compute ssh-key import tcp-deployment --public-key-file ~/.ssh/tcp_deployment_key.pub
    fi
    
    doctl compute droplet create $DROPLET_NAME \
        --size $DROPLET_SIZE \
        --image $DROPLET_IMAGE \
        --region $DROPLET_REGION \
        --ssh-keys tcp-deployment \
        --wait
    
    echo "✅ Droplet created"
else
    echo "ℹ️  Using existing droplet"
fi

# Get droplet IP
DROPLET_IP=$(doctl compute droplet list --format "Name,PublicIPv4" | grep "$DROPLET_NAME" | awk '{print $2}')
echo "🌐 Droplet IP: $DROPLET_IP"

# Wait for SSH
echo "⏳ Waiting for SSH access..."
for i in {1..30}; do
    if ssh -i ~/.ssh/tcp_deployment_key -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@$DROPLET_IP "echo 'ready'" &> /dev/null; then
        echo "✅ SSH ready"
        break
    fi
    sleep 10
done

# Create setup script
cat > /tmp/tcp_droplet_setup.sh << 'SETUP_EOF'
#!/bin/bash
set -euo pipefail

echo "🚀 Setting up TCP Knowledge Growth System..."

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y \
    python3 python3-pip python3-venv \
    git curl wget \
    man-db apropos \
    htop tmux \
    logrotate

# Create tcp user
useradd -m -s /bin/bash -G sudo tcp || true

# Create application structure
mkdir -p /opt/tcp-knowledge-system/{data,patterns,logs,scripts,backups}

# Setup Python environment
cd /opt/tcp-knowledge-system
python3 -m venv tcp-env
source tcp-env/bin/activate
pip install --upgrade pip
pip install anthropic schedule requests

# Setup logging
touch /var/log/tcp-knowledge-growth.log
chmod 644 /var/log/tcp-knowledge-growth.log

# Setup log rotation
cat > /etc/logrotate.d/tcp-knowledge-growth << 'LOGROTATE_EOF'
/var/log/tcp-knowledge-growth.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 tcp tcp
}
LOGROTATE_EOF

echo "✅ System setup complete"
SETUP_EOF

# Upload and run setup
scp -i ~/.ssh/tcp_deployment_key /tmp/tcp_droplet_setup.sh root@$DROPLET_IP:/tmp/
ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP "chmod +x /tmp/tcp_droplet_setup.sh && /tmp/tcp_droplet_setup.sh"

# Deploy TCP code
echo "📁 Deploying TCP application code..."

# Package code
cd /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/tcp-server-full
tar -czf /tmp/tcp-app.tar.gz \
    digitalocean_deployment.py \
    enhanced_tcp_analyzer.py \
    tcp_man_ingestion.py \
    quick_llm_enhancement.py \
    validate_enhanced_tcp.py

# Upload application
scp -i ~/.ssh/tcp_deployment_key /tmp/tcp-app.tar.gz root@$DROPLET_IP:/tmp/

# Extract and configure
ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP << DEPLOY_EOF
cd /opt/tcp-knowledge-system
tar -xzf /tmp/tcp-app.tar.gz -C scripts/

# Set environment variables with secrets
cat > .env << 'ENV_EOF'
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
PYTHONPATH=/opt/tcp-knowledge-system/scripts
ENV_EOF

chmod 600 .env
chown -R tcp:tcp /opt/tcp-knowledge-system

# Create systemd service
cat > /etc/systemd/system/tcp-knowledge-growth.service << 'SERVICE_EOF'
[Unit]
Description=TCP Knowledge Growth System
After=network.target

[Service]
Type=simple
User=tcp
Group=tcp
WorkingDirectory=/opt/tcp-knowledge-system
Environment=PYTHONPATH=/opt/tcp-knowledge-system/scripts
EnvironmentFile=/opt/tcp-knowledge-system/.env
ExecStart=/opt/tcp-knowledge-system/tcp-env/bin/python scripts/digitalocean_deployment.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Enable and start service
systemctl daemon-reload
systemctl enable tcp-knowledge-growth

echo "✅ Service configured"
DEPLOY_EOF

# Create management tools
echo "🔧 Setting up management tools..."

ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP << 'TOOLS_EOF'
# Create management script
cat > /usr/local/bin/tcp-manage << 'MANAGE_EOF'
#!/bin/bash

case "$1" in
    start)
        systemctl start tcp-knowledge-growth
        echo "✅ TCP Knowledge Growth started"
        ;;
    stop)
        systemctl stop tcp-knowledge-growth
        echo "🛑 TCP Knowledge Growth stopped"
        ;;
    restart)
        systemctl restart tcp-knowledge-growth
        echo "🔄 TCP Knowledge Growth restarted"
        ;;
    status)
        echo "📊 TCP Knowledge Growth Status"
        echo "=============================="
        systemctl status tcp-knowledge-growth --no-pager
        echo ""
        echo "💾 Disk Usage:"
        df -h /opt/tcp-knowledge-system
        echo ""
        echo "📈 Recent Activity:"
        tail -n 10 /var/log/tcp-knowledge-growth.log
        ;;
    logs)
        tail -f /var/log/tcp-knowledge-growth.log
        ;;
    backup)
        cd /opt/tcp-knowledge-system
        tar -czf backups/tcp-backup-$(date +%Y%m%d-%H%M%S).tar.gz data/ patterns/
        echo "✅ Backup created in /opt/tcp-knowledge-system/backups/"
        ;;
    metrics)
        if [ -f /opt/tcp-knowledge-system/data/enhancement_history.json ]; then
            echo "📊 TCP Metrics:"
            echo "Commands analyzed: $(jq '.analyzed_commands | length' /opt/tcp-knowledge-system/data/enhancement_history.json 2>/dev/null || echo 'N/A')"
            echo "Enhancement cycles: $(jq '.enhancements | length' /opt/tcp-knowledge-system/data/enhancement_history.json 2>/dev/null || echo 'N/A')"
        else
            echo "📊 No metrics available yet"
        fi
        ;;
    *)
        echo "Usage: tcp-manage {start|stop|restart|status|logs|backup|metrics}"
        exit 1
        ;;
esac
MANAGE_EOF

chmod +x /usr/local/bin/tcp-manage

# Start the service
systemctl start tcp-knowledge-growth

echo "✅ Management tools installed"
TOOLS_EOF

echo ""
echo "🎉 TCP Knowledge Growth deployment complete!"
echo ""
echo "📊 Deployment Details:"
echo "   Droplet: $DROPLET_NAME"
echo "   IP: $DROPLET_IP"
echo "   Cost: ~$24/month"
echo "   SSH: ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP"
echo ""
echo "🔧 Management Commands:"
echo "   Status:  ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP 'tcp-manage status'"
echo "   Logs:    ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP 'tcp-manage logs'"
echo "   Metrics: ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP 'tcp-manage metrics'"
echo ""
echo "📈 The system will:"
echo "   • Discover new commands every 6 hours"
echo "   • Analyze them with Claude for security patterns"
echo "   • Continuously improve TCP ground truth"
echo "   • Cost ~$0.50-2.00/day in API calls"
echo ""
echo "🌱 Your TCP knowledge base is now growing automatically!"

