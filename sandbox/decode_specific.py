#!/usr/bin/env python3
"""
Decode specific tools to show different binary patterns
"""

import sys
import struct
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sandbox_agent import SandboxAgent


def decode_all_tools():
    """Decode all tools in the registry to show different patterns."""
    print("🔍 DECODING ALL TOOLS IN REGISTRY")
    print("=" * 70)
    
    agent = SandboxAgent()
    
    print(f"Found {len(agent.tool_profiles)} tools in registry")
    print()
    
    for tool_name, profile in agent.tool_profiles.items():
        binary_hex = profile.binary_hex
        binary_bytes = bytes.fromhex(binary_hex)
        
        # Parse the binary
        magic = binary_bytes[:4]
        version_bytes = binary_bytes[4:6]
        cap_bytes = binary_bytes[6:10]
        perf_bytes = binary_bytes[10:18]
        crc_bytes = binary_bytes[18:20]
        
        # Decode components
        version = struct.unpack('>H', version_bytes)[0]
        cap_flags = struct.unpack('>I', cap_bytes)[0]
        
        try:
            memory_mb, cpu_percent, throughput = struct.unpack('>HBH', perf_bytes[:5])
        except:
            memory_mb, cpu_percent, throughput = 0, 0, 0
        
        print(f"🔧 {tool_name.upper()} ANALYSIS:")
        print("-" * 50)
        print(f"Binary: {binary_hex}")
        print(f"Magic:  {magic.hex()} (tool identity)")
        print(f"Version: v{version // 100}.{version % 100}" if version > 0 else "Version: unknown")
        print(f"Capabilities: 0x{cap_flags:08x} ({cap_flags:032b})")
        print(f"Performance: {memory_mb}MB, {cpu_percent}% CPU, {throughput} ops/sec")
        print(f"Categories: {', '.join(profile.categories)}")
        print(f"Agent-detected capabilities: {', '.join(profile.key_capabilities)}")
        
        # Show which bits are set
        if cap_flags > 0:
            print("Active capability bits:")
            for bit_pos in range(32):
                if cap_flags & (1 << bit_pos):
                    print(f"  Bit {bit_pos}: ON")
        else:
            print("No capability bits set in binary")
        
        print(f"Efficiency: {profile.efficiency_score:.2f}/1.0")
        print()
    
    # Show the most interesting pattern differences
    print("🎯 PATTERN ANALYSIS:")
    print("-" * 50)
    
    # Group by capability patterns
    cap_patterns = {}
    for tool_name, profile in agent.tool_profiles.items():
        cap_key = tuple(sorted(profile.key_capabilities))
        if cap_key not in cap_patterns:
            cap_patterns[cap_key] = []
        cap_patterns[cap_key].append(tool_name)
    
    print("Tools grouped by capability patterns:")
    for i, (cap_pattern, tools) in enumerate(cap_patterns.items(), 1):
        pattern_desc = ', '.join(cap_pattern) if cap_pattern else "No capabilities"
        print(f"{i}. Pattern: [{pattern_desc}]")
        print(f"   Tools: {', '.join(tools)}")
        print()
    
    # Show binary diversity
    unique_binaries = set(profile.binary_hex for profile in agent.tool_profiles.values())
    print(f"📊 Binary diversity: {len(unique_binaries)}/{len(agent.tool_profiles)} unique descriptors")
    
    # Show version distribution
    versions = [profile.version for profile in agent.tool_profiles.values()]
    version_counts = {}
    for v in versions:
        version_counts[v] = version_counts.get(v, 0) + 1
    
    print("Version distribution:")
    for version, count in sorted(version_counts.items()):
        print(f"  v{version}: {count} tools")
    
    return agent


def demonstrate_interactive_decoding():
    """Let user pick specific tools to decode in detail."""
    agent = decode_all_tools()
    
    print("\n" + "=" * 70)
    print("🤖 INTERACTIVE BINARY DECODER")
    print("=" * 70)
    print("Available tools:", ', '.join(sorted(agent.tool_profiles.keys())))
    print("Enter tool name to decode in detail, or 'quit' to exit")
    print()
    
    while True:
        try:
            tool_choice = input("Decode tool> ").strip().lower()
            
            if tool_choice in ['quit', 'exit', 'q']:
                print("👋 Decoder exiting...")
                break
            
            if tool_choice in agent.tool_profiles:
                profile = agent.tool_profiles[tool_choice]
                
                print(f"\n🔍 DETAILED DECODE: {tool_choice.upper()}")
                print("-" * 60)
                
                # Show complete binary breakdown
                binary_bytes = bytes.fromhex(profile.binary_hex)
                
                print("Byte-by-byte breakdown:")
                for i, byte_val in enumerate(binary_bytes):
                    section = ""
                    if i < 4:
                        section = "Magic"
                    elif i < 6:
                        section = "Version"
                    elif i < 10:
                        section = "Capabilities"
                    elif i < 18:
                        section = "Performance"
                    else:
                        section = "CRC"
                    
                    print(f"  Byte {i:2d}: 0x{byte_val:02x} ({byte_val:3d}) [{section}]")
                
                print(f"\nAgent interpretation:")
                print(f"  Categories: {', '.join(profile.categories)}")
                print(f"  Key capabilities: {', '.join(profile.key_capabilities)}")
                print(f"  Efficiency score: {profile.efficiency_score:.2f}")
                print(f"  Resource usage: {profile.memory_mb}MB, {profile.cpu_percent}% CPU")
                
                # Show what tasks this tool would be good for
                print(f"\nRecommended for tasks involving:")
                if 'search_tools' in profile.categories:
                    print("  • Pattern searching and text matching")
                if 'text_utilities' in profile.categories:
                    print("  • Text processing and manipulation")
                if 'data_manipulation' in profile.categories:
                    print("  • Data transformation and analysis")
                if 'network_tools' in profile.categories:
                    print("  • Network operations and data transfer")
                if profile.efficiency_score > 0.8:
                    print("  • High-efficiency processing workflows")
                
                print()
                
            else:
                print(f"Tool '{tool_choice}' not found. Available: {', '.join(agent.tool_profiles.keys())}")
                
        except KeyboardInterrupt:
            print("\n👋 Decoder interrupted. Goodbye!")
            break
        except EOFError:
            print("\n👋 Input ended. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    try:
        # First show all tools, then go interactive if possible
        print("This will show binary decoding for all tools, then offer interactive mode...")
        print()
        
        # Just run the analysis without interactive mode for now
        agent = decode_all_tools()
        
        print("\n💡 DECODING INSIGHTS:")
        print("-" * 50)
        print("• Each tool has a unique 20-byte binary fingerprint")
        print("• Magic signatures provide instant tool identification")
        print("• Version info enables compatibility checking")
        print("• Capability flags encode functional abilities")
        print("• Performance metrics guide resource planning")
        print("• Agent can categorize and reason about tools from binary alone")
        print()
        print("🎉 This demonstrates the power of structured binary descriptors")
        print("   for instant tool capability understanding!")
        
    except Exception as e:
        print(f"❌ Decoding failed: {e}")
        import traceback
        traceback.print_exc()