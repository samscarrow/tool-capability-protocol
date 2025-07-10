#!/bin/bash
"""
DigitalOcean TCP Knowledge Growth Deployment Script
"""

set -euo pipefail

echo "🌊 TCP Knowledge Growth - DigitalOcean Deployment"
echo "================================================"

# Configuration
DROPLET_NAME="tcp-knowledge-growth"
DROPLET_SIZE="s-2vcpu-4gb"  # $24/month - good for continuous processing
DROPLET_REGION="nyc1"
DROPLET_IMAGE="ubuntu-22-04-x64"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check doctl (DigitalOcean CLI)
    if ! command -v doctl &> /dev/null; then
        log_error "doctl CLI not found. Install with: brew install doctl"
        exit 1
    fi
    
    # Check authentication
    if ! doctl account get &> /dev/null; then
        log_error "DigitalOcean authentication required. Run: doctl auth init"
        exit 1
    fi
    
    # Check SSH key
    if ! doctl compute ssh-key list | grep -q "tcp-deployment"; then
        log_warn "SSH key 'tcp-deployment' not found. Creating one..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/tcp_deployment_key -N ""
        doctl compute ssh-key import tcp-deployment --public-key-file ~/.ssh/tcp_deployment_key.pub
    fi
    
    log_info "Prerequisites check complete ✅"
}

# Create droplet
create_droplet() {
    log_info "Creating DigitalOcean droplet..."
    
    # Check if droplet already exists
    if doctl compute droplet list | grep -q "$DROPLET_NAME"; then
        log_warn "Droplet '$DROPLET_NAME' already exists"
        DROPLET_IP=$(doctl compute droplet list --format "Name,PublicIPv4" | grep "$DROPLET_NAME" | awk '{print $2}')
        log_info "Using existing droplet IP: $DROPLET_IP"
        return
    fi
    
    # Create droplet
    doctl compute droplet create $DROPLET_NAME \
        --size $DROPLET_SIZE \
        --image $DROPLET_IMAGE \
        --region $DROPLET_REGION \
        --ssh-keys tcp-deployment \
        --wait
    
    # Get IP address
    DROPLET_IP=$(doctl compute droplet list --format "Name,PublicIPv4" | grep "$DROPLET_NAME" | awk '{print $2}')
    log_info "Droplet created with IP: $DROPLET_IP"
    
    # Wait for SSH to be ready
    log_info "Waiting for SSH to be ready..."
    for i in {1..30}; do
        if ssh -i ~/.ssh/tcp_deployment_key -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@$DROPLET_IP "echo 'SSH ready'" &> /dev/null; then
            log_info "SSH connection established ✅"
            break
        fi
        sleep 10
    done
}

# Setup environment on droplet
setup_environment() {
    log_info "Setting up TCP environment on droplet..."
    
    # Create setup script
    cat > /tmp/tcp_setup.sh << 'EOF'
#!/bin/bash
set -euo pipefail

echo "🚀 Setting up TCP Knowledge Growth System..."

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y python3 python3-pip python3-venv git curl man-db apropos

# Create system user
useradd -m -s /bin/bash tcp-system || true

# Create application directory
mkdir -p /opt/tcp-knowledge-system
chown tcp-system:tcp-system /opt/tcp-knowledge-system

# Setup Python environment
cd /opt/tcp-knowledge-system
python3 -m venv tcp-env
source tcp-env/bin/activate

# Install Python packages
pip install anthropic schedule

# Create directory structure
mkdir -p {data,patterns,logs,scripts}

# Setup logging
touch /var/log/tcp-knowledge-growth.log
chown tcp-system:tcp-system /var/log/tcp-knowledge-growth.log

# Create systemd service
cat > /etc/systemd/system/tcp-knowledge-growth.service << 'SYSTEMD_EOF'
[Unit]
Description=TCP Knowledge Growth System
After=network.target

[Service]
Type=simple
User=tcp-system
WorkingDirectory=/opt/tcp-knowledge-system
Environment=PATH=/opt/tcp-knowledge-system/tcp-env/bin
ExecStart=/opt/tcp-knowledge-system/tcp-env/bin/python /opt/tcp-knowledge-system/scripts/digitalocean_deployment.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

# Enable service
systemctl daemon-reload
systemctl enable tcp-knowledge-growth

echo "✅ Environment setup complete"
EOF

    # Upload and run setup script
    scp -i ~/.ssh/tcp_deployment_key /tmp/tcp_setup.sh root@$DROPLET_IP:/tmp/
    ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP "chmod +x /tmp/tcp_setup.sh && /tmp/tcp_setup.sh"
}

# Deploy TCP code
deploy_tcp_code() {
    log_info "Deploying TCP code to droplet..."
    
    # Create deployment package
    cd /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/tcp-server-full
    
    # Package essential files
    tar -czf /tmp/tcp-deployment.tar.gz \
        digitalocean_deployment.py \
        enhanced_tcp_analyzer.py \
        tcp_man_ingestion.py \
        quick_llm_enhancement.py \
        validate_enhanced_tcp.py
    
    # Upload package
    scp -i ~/.ssh/tcp_deployment_key /tmp/tcp-deployment.tar.gz root@$DROPLET_IP:/tmp/
    
    # Extract and setup
    ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP << 'SSH_EOF'
cd /opt/tcp-knowledge-system
tar -xzf /tmp/tcp-deployment.tar.gz -C scripts/
chown -R tcp-system:tcp-system scripts/

# Set environment variables (you'll need to set ANTHROPIC_API_KEY)
cat > /opt/tcp-knowledge-system/.env << 'ENV_EOF'
ANTHROPIC_API_KEY=your_api_key_here
ENV_EOF

chown tcp-system:tcp-system .env
chmod 600 .env
SSH_EOF

    log_info "TCP code deployed ✅"
}

# Setup monitoring and management
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP << 'SSH_EOF'
# Create monitoring script
cat > /opt/tcp-knowledge-system/scripts/status_check.sh << 'MONITOR_EOF'
#!/bin/bash

echo "🔍 TCP Knowledge Growth System Status"
echo "===================================="

# Service status
echo "Service Status:"
systemctl status tcp-knowledge-growth --no-pager -l

echo -e "\nDisk Usage:"
df -h /opt/tcp-knowledge-system

echo -e "\nMemory Usage:"
free -h

echo -e "\nRecent Logs:"
tail -n 20 /var/log/tcp-knowledge-growth.log

echo -e "\nSystem Metrics:"
if [ -f /opt/tcp-knowledge-system/data/enhancement_history.json ]; then
    echo "Enhancement history file exists"
    wc -l /opt/tcp-knowledge-system/data/enhancement_history.json
else
    echo "No enhancement history yet"
fi
MONITOR_EOF

chmod +x /opt/tcp-knowledge-system/scripts/status_check.sh

# Create management script
cat > /opt/tcp-knowledge-system/scripts/manage.sh << 'MANAGE_EOF'
#!/bin/bash

case "$1" in
    start)
        systemctl start tcp-knowledge-growth
        echo "TCP Knowledge Growth started"
        ;;
    stop)
        systemctl stop tcp-knowledge-growth
        echo "TCP Knowledge Growth stopped"
        ;;
    restart)
        systemctl restart tcp-knowledge-growth
        echo "TCP Knowledge Growth restarted"
        ;;
    status)
        /opt/tcp-knowledge-system/scripts/status_check.sh
        ;;
    logs)
        tail -f /var/log/tcp-knowledge-growth.log
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
MANAGE_EOF

chmod +x /opt/tcp-knowledge-system/scripts/manage.sh
SSH_EOF

    log_info "Monitoring setup complete ✅"
}

# Main deployment function
deploy() {
    log_info "Starting TCP Knowledge Growth deployment to DigitalOcean..."
    
    check_prerequisites
    create_droplet
    setup_environment
    deploy_tcp_code
    setup_monitoring
    
    log_info "🎉 Deployment complete!"
    echo ""
    echo "📊 Droplet Information:"
    echo "   Name: $DROPLET_NAME"
    echo "   IP: $DROPLET_IP" 
    echo "   Size: $DROPLET_SIZE ($24/month)"
    echo "   SSH: ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP"
    echo ""
    echo "🔧 Management Commands:"
    echo "   Status: ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP '/opt/tcp-knowledge-system/scripts/manage.sh status'"
    echo "   Start:  ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP '/opt/tcp-knowledge-system/scripts/manage.sh start'"
    echo "   Logs:   ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP '/opt/tcp-knowledge-system/scripts/manage.sh logs'"
    echo ""
    echo "⚠️  Important: Set your ANTHROPIC_API_KEY in /opt/tcp-knowledge-system/.env"
    echo "   SSH command: ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP"
    echo "   Edit: nano /opt/tcp-knowledge-system/.env"
}

# Cleanup function
cleanup() {
    log_warn "Cleaning up DigitalOcean resources..."
    
    if doctl compute droplet list | grep -q "$DROPLET_NAME"; then
        doctl compute droplet delete $DROPLET_NAME -f
        log_info "Droplet deleted"
    fi
    
    # Note: SSH key is kept for reuse
}

# Command line interface
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    cleanup)
        cleanup
        ;;
    status)
        if doctl compute droplet list | grep -q "$DROPLET_NAME"; then
            DROPLET_IP=$(doctl compute droplet list --format "Name,PublicIPv4" | grep "$DROPLET_NAME" | awk '{print $2}')
            echo "Droplet Status: Running ($DROPLET_IP)"
            ssh -i ~/.ssh/tcp_deployment_key root@$DROPLET_IP '/opt/tcp-knowledge-system/scripts/manage.sh status'
        else
            echo "Droplet not found"
        fi
        ;;
    *)
        echo "Usage: $0 {deploy|cleanup|status}"
        exit 1
        ;;
esac