#!/usr/bin/env python3
"""Quick test of TCP with a broader sample of commands."""

import asyncio
import subprocess
import random
import re
from tcp_man_ingestion import TCPManIngestionServer, ManPageAnalyzer


async def quick_sample_test():
    """Test TCP with a quick sample of diverse commands."""
    print("🔍 Quick TCP Sampling Test")
    print("=" * 50)

    # Get a quick sample of available commands
    try:
        result = subprocess.run(
            ["man", "-k", "."], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.split("\n")[:500]  # First 500 lines only
            commands = []
            for line in lines:
                if line.strip():
                    match = re.match(r"^([a-zA-Z][a-zA-Z0-9_-]*)", line.strip())
                    if match:
                        cmd = match.group(1)
                        if len(cmd) > 1 and len(cmd) < 15:  # Reasonable command length
                            commands.append(cmd)

            # Take random sample
            unique_commands = list(set(commands))
            sample_size = min(20, len(unique_commands))  # Just 20 commands
            sampled = random.sample(unique_commands, sample_size)

            print(f"📊 Found {len(unique_commands)} commands, testing {sample_size}")
            print(
                f"Sample: {', '.join(sampled[:10])}{'...' if len(sampled) > 10 else ''}"
            )

            # Quick ingestion
            server = TCPManIngestionServer()
            analyzer = ManPageAnalyzer()

            results = []
            for i, cmd in enumerate(sampled, 1):
                print(f"[{i}/{sample_size}] {cmd}...", end=" ")
                try:
                    man_content = analyzer.get_man_page(cmd)
                    if man_content:
                        analysis = analyzer.analyze_command_text(cmd, man_content)
                        orig_size = len(man_content.encode())
                        tcp_size = 24  # Standard TCP descriptor size
                        compression = orig_size / tcp_size

                        risk_emoji = {
                            "SAFE": "✅",
                            "LOW_RISK": "🟢",
                            "MEDIUM_RISK": "🟡",
                            "HIGH_RISK": "🟠",
                            "CRITICAL": "🔴",
                        }.get(analysis["risk_level"], "❓")

                        print(
                            f"{risk_emoji} {analysis['risk_level']} ({compression:.0f}:1)"
                        )
                        results.append(
                            (cmd, analysis["risk_level"], compression, orig_size)
                        )
                    else:
                        print("❌ No man page")
                except Exception as e:
                    print(f"❌ Error: {str(e)[:30]}...")

            # Quick stats
            if results:
                total_orig = sum(r[3] for r in results)
                total_tcp = len(results) * 24
                avg_compression = total_orig / total_tcp

                risk_counts = {}
                for r in results:
                    risk_counts[r[1]] = risk_counts.get(r[1], 0) + 1

                print(f"\n📈 Quick Results:")
                print(f"   Processed: {len(results)} commands")
                print(f"   Average compression: {avg_compression:.1f}:1")
                print(f"   Risk distribution: {dict(risk_counts)}")
                print(f"   Total docs: {total_orig:,} bytes → {total_tcp} bytes TCP")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(quick_sample_test())
