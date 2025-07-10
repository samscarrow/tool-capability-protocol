#!/bin/bash
ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 << 'EOF'
chmod +x /tmp/droplet_setup.sh
/tmp/droplet_setup.sh
EOF