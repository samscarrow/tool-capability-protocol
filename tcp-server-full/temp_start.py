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
