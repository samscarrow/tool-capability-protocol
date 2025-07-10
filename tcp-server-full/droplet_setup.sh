#!/bin/bash
set -e
echo "🚀 Setting up TCP Knowledge Growth System..."

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y \
    python3 python3-pip python3-venv \
    git curl wget \
    man-db apropos \
    htop tmux \
    jq

# Create tcp user
useradd -m -s /bin/bash tcp || true

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
    metrics)
        if [ -f /opt/tcp-knowledge-system/tcp_data/state.json ]; then
            echo "📊 TCP Metrics:"
            jq '.' /opt/tcp-knowledge-system/tcp_data/state.json
        else
            echo "📊 No metrics available yet"
        fi
        ;;
    *)
        echo "Usage: tcp-manage {start|stop|restart|status|logs|metrics}"
        exit 1
        ;;
esac
MANAGE_EOF

chmod +x /usr/local/bin/tcp-manage

echo "✅ Environment setup complete"