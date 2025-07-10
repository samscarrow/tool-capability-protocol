#!/bin/bash
cd /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/tcp-server-full
source ../langchain-integration/venv/bin/activate

# Create a temporary Python script that starts the server on port 8081
cat > temp_start.py << 'EOF'
import asyncio
import sys
sys.path.insert(0, '.')
from tcp_man_ingestion import TCPManIngestionDemo

async def main():
    demo = TCPManIngestionDemo()
    await demo.ingest_system_commands()
    await demo.start_tcp_server(port=8081)

if __name__ == "__main__":
    asyncio.run(main())
EOF

python temp_start.py