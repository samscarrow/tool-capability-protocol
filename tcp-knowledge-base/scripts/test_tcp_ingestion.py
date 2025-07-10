#!/usr/bin/env python3
"""
Test TCP man page ingestion without starting the server
Shows the conversion of man pages to 24-byte descriptors
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tcp_man_ingestion import TCPManIngestionServer, ManPageAnalyzer


async def test_ingestion():
    """Test man page ingestion and show results"""
    print("🌟 TCP Man Page Ingestion Test")
    print("=" * 70)

    # Create analyzer
    analyzer = ManPageAnalyzer()

    # Test specific commands
    test_commands = ["ls", "rm", "dd", "chmod", "git", "docker"]

    print("\n📊 Analyzing Commands:")
    print("-" * 70)

    for command in test_commands:
        print(f"\n🔍 Command: {command}")

        # Get man page
        man_content = analyzer.get_man_page(command)

        if man_content:
            # Analyze
            analysis = analyzer.analyze_man_page(command, man_content)

            # Create TCP descriptor
            tcp_descriptor = analyzer.create_tcp_descriptor(analysis)

            # Calculate compression
            man_size = len(man_content)
            tcp_size = len(tcp_descriptor)
            compression_ratio = man_size / tcp_size

            # Display results
            print(f"📄 Man Page Size: {man_size:,} bytes")
            print(f"💾 TCP Size: {tcp_size} bytes")
            print(f"🗜️  Compression: {compression_ratio:.0f}:1")
            print(f"🎯 Risk Level: {analysis['risk_level']}")
            print(f"🔧 Capabilities: {', '.join(analysis['capabilities']) or 'None'}")

            # Show binary descriptor details
            print(f"🔢 Binary Descriptor (hex): {tcp_descriptor.hex()}")

            # Show dangerous options if any
            if analysis["dangerous_options"]:
                print(
                    f"⚠️  Dangerous Options: {', '.join(analysis['dangerous_options'])}"
                )

            # Show synopsis snippet
            if analysis["synopsis"]:
                print(f"📝 Synopsis: {analysis['synopsis'][:100]}...")
        else:
            print("❌ No man page found")

    print("\n\n✅ Test complete!")


async def test_server_limited():
    """Test server with limited commands"""
    server = TCPManIngestionServer()

    # Ingest just a few commands
    print("\n🚀 Testing Limited Server Ingestion")
    print("=" * 70)

    # Override command list for testing
    test_commands = ["ls", "rm", "cat", "chmod", "dd"]

    for command in test_commands:
        man_content = server.analyzer.get_man_page(command)
        if man_content:
            analysis = server.analyzer.analyze_man_page(command, man_content)
            tcp_descriptor = server.analyzer.create_tcp_descriptor(analysis)

            server.ingested_commands[command] = {
                "analysis": analysis,
                "descriptor": tcp_descriptor,
                "man_size": len(man_content),
                "tcp_size": 24,
                "compression_ratio": len(man_content) / 24,
            }

            server.compression_stats["total_man_size"] += len(man_content)
            server.compression_stats["total_tcp_size"] += 24
            server.compression_stats["commands_processed"] += 1

    server._display_ingestion_summary()

    # Test command analysis
    print("\n\n🧪 Testing Command Analysis:")
    print("-" * 70)

    test_queries = [
        "ls -la",
        "rm -rf /tmp/*",
        "cat /etc/passwd",
        "chmod 777 /",
        "dd if=/dev/zero of=/dev/sda",
    ]

    for query in test_queries:
        cmd_base = query.split()[0]
        if cmd_base in server.ingested_commands:
            ingested = server.ingested_commands[cmd_base]
            analysis = ingested["analysis"]

            risk_emoji = {
                "SAFE": "✅",
                "LOW_RISK": "🟢",
                "MEDIUM_RISK": "🟡",
                "HIGH_RISK": "🟠",
                "CRITICAL": "🔴",
            }.get(analysis["risk_level"], "❓")

            print(f"\n{risk_emoji} {query}")
            print(f"   Risk: {analysis['risk_level']}")
            print(f"   Compression: {ingested['compression_ratio']:.0f}:1")
            print(f"   Man→TCP: {ingested['man_size']:,} → 24 bytes")


if __name__ == "__main__":
    print("TCP Man Page Ingestion Test")
    print("Converting documentation to binary intelligence")
    print("=" * 60)

    try:
        # Run basic test
        asyncio.run(test_ingestion())

        # Run server test
        asyncio.run(test_server_limited())

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
