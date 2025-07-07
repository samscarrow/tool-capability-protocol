#!/bin/bash
#
# TCP Conflict Monitor Installation Script
# Dr. Sam Mitchell - Hardware Security Engineer
#
# Sets up the conflict monitoring system for the TCP consortium

set -euo pipefail

echo "TCP Consortium Conflict Monitor Setup"
echo "===================================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$python_version >= 3.8" | bc) -ne 1 ]]; then
    echo "❌ Python 3.8+ required (found $python_version)"
    exit 1
fi
echo "✓ Python $python_version detected"

# Install required packages
echo "Installing dependencies..."
pip3 install --upgrade pip
pip3 install watchdog

# Create directories
echo "Creating necessary directories..."
mkdir -p ~/.tcp_conflicts
mkdir -p ~/.tcp_conflict_backups

# Create systemd service (optional)
if command -v systemctl &> /dev/null; then
    echo "Creating systemd service..."
    
    cat > /tmp/tcp-conflict-monitor.service << EOF
[Unit]
Description=TCP Consortium Conflict Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/tcp_conflict_monitor.py --root ../..
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

    echo "To install as system service, run:"
    echo "  sudo cp /tmp/tcp-conflict-monitor.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable tcp-conflict-monitor"
    echo "  sudo systemctl start tcp-conflict-monitor"
fi

# Create launcher script
echo "Creating launcher script..."
cat > start_conflict_monitor.sh << 'EOF'
#!/bin/bash
# TCP Conflict Monitor Launcher

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Starting TCP Conflict Monitor..."
echo "Dashboard will be available at: http://localhost:8888"
echo "Press Ctrl+C to stop"
echo ""

python3 tcp_conflict_monitor.py --root ../..
EOF

chmod +x start_conflict_monitor.sh

# Test import
echo "Testing installation..."
if python3 -c "import watchdog; import sqlite3; import asyncio" 2>/dev/null; then
    echo "✓ All dependencies installed successfully"
else
    echo "❌ Some dependencies missing"
    exit 1
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "To start the conflict monitor:"
echo "  ./start_conflict_monitor.sh"
echo ""
echo "The dashboard will be available at:"
echo "  http://localhost:8888"
echo ""
echo "For enhanced features, use the Python API:"
echo "  from tcp_conflict_monitor import create_enhanced_monitor"
echo "  monitor = create_enhanced_monitor()"
echo ""