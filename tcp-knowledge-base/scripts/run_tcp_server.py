#!/usr/bin/env python3
"""Run TCP server on port 8081"""
import asyncio
import sys

sys.path.insert(0, ".")
from tcp_man_ingestion import TCPManIngestionServer


async def main():
    server = TCPManIngestionServer()
    await server.ingest_system_commands()
    await server.start_tcp_server(port=8081)


if __name__ == "__main__":
    asyncio.run(main())
