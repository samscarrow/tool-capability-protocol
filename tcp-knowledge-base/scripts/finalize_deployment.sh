#!/bin/bash
echo "🎯 Finalizing TCP Knowledge Growth deployment..."

# Get Anthropic API key from 1Password
ANTHROPIC_KEY=$(op item get neposatk4gkawjw52mlhm6jvcu --fields credential --reveal)

ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 << EOF
# Check if setup completed
if [ ! -d "/opt/tcp-knowledge-system/tcp-env" ]; then
    echo "⏳ Waiting for setup to complete..."
    sleep 60
fi

# Extract TCP application
cd /opt/tcp-knowledge-system
tar -xzf /tmp/tcp-app.tar.gz -C scripts/

# Set up environment with API key
cat > .env << 'ENV_EOF'
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
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
ExecStart=/opt/tcp-knowledge-system/tcp-env/bin/python scripts/simple_tcp_deployment.py
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
systemctl start tcp-knowledge-growth

echo "✅ TCP Knowledge Growth system deployed and started!"
echo "📊 Service status:"
systemctl status tcp-knowledge-growth --no-pager

echo ""
echo "🎉 Deployment complete!"
echo "Monitor with: tcp-manage status"
echo "View logs with: tcp-manage logs"
EOF