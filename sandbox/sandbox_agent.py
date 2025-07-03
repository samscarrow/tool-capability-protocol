#!/usr/bin/env python3
"""
Enhanced Naive Agent with Self-Discovery Capabilities

This agent discovers its own capabilities by analyzing binary TCP descriptors
and generates natural language memos describing what it can do.
"""

import sys
import json
import struct
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tcp.analysis.pipeline import TCPGenerationPipeline


@dataclass
class ToolProfile:
    """Structured analysis of a tool's capabilities."""
    name: str
    binary_hex: str
    magic_signature: str
    version: str
    capability_flags: int
    memory_mb: int
    cpu_percent: int
    throughput: int
    categories: List[str]
    key_capabilities: List[str]
    efficiency_score: float
    confidence: float


class SandboxAgent:
    """
    Enhanced naive agent that discovers its own capabilities through
    binary TCP descriptor analysis and generates natural language memos.
    """
    
    def __init__(self, registry_path: str = None):
        """Initialize the sandbox agent."""
        self.registry_path = registry_path or str(Path(__file__).parent / "tool_registry.json")
        self.tool_profiles = {}
        self.capability_matrix = defaultdict(list)
        self.discovery_report = {}
        
        # Load tool registry
        self._load_tool_registry()
        
    def _load_tool_registry(self) -> None:
        """Load and analyze tool registry."""
        print("🤖 Agent initializing: Loading tool registry...")
        
        try:
            with open(self.registry_path, 'r') as f:
                registry_data = json.load(f)
            
            print(f"   📂 Found {len(registry_data['tools'])} tools in registry")
            
            # Analyze each tool
            for tool_name, tool_data in registry_data['tools'].items():
                profile = self._analyze_tool_binary(tool_name, tool_data)
                self.tool_profiles[tool_name] = profile
                
                # Build capability matrix
                for capability in profile.key_capabilities:
                    self.capability_matrix[capability].append(tool_name)
            
            print(f"   ✅ Analyzed {len(self.tool_profiles)} tool profiles")
            print(f"   🔍 Discovered {len(self.capability_matrix)} unique capabilities")
            
        except Exception as e:
            print(f"   ❌ Failed to load registry: {e}")
            
    def _analyze_tool_binary(self, tool_name: str, tool_data: Dict) -> ToolProfile:
        """Analyze a tool's binary descriptor to extract capabilities."""
        binary_hex = tool_data['binary_hex']
        binary_bytes = bytes.fromhex(binary_hex)
        
        if len(binary_bytes) != 20:
            raise ValueError(f"Invalid binary descriptor length: {len(binary_bytes)}")
        
        # Parse binary format: Magic(4) + Version(2) + Capabilities(4) + Performance(8) + CRC(2)
        magic = binary_bytes[:4]
        version_bytes = binary_bytes[4:6]
        cap_bytes = binary_bytes[6:10]
        perf_bytes = binary_bytes[10:18]
        crc_bytes = binary_bytes[18:20]
        
        # Decode components
        magic_signature = magic.hex()
        version = struct.unpack('>H', version_bytes)[0]
        version_str = f"{version // 100}.{version % 100}" if version > 0 else "unknown"
        cap_flags = struct.unpack('>I', cap_bytes)[0]
        
        # Performance metrics (simplified decoding)
        try:
            memory_mb, cpu_percent, throughput = struct.unpack('>HBH', perf_bytes[:5])
        except:
            memory_mb, cpu_percent, throughput = 0, 0, 0
        
        # Analyze capabilities from flags
        capabilities = self._decode_capability_flags(cap_flags)
        categories = self._categorize_tool(tool_name, capabilities)
        efficiency = self._calculate_efficiency(memory_mb, cpu_percent)
        
        return ToolProfile(
            name=tool_name,
            binary_hex=binary_hex,
            magic_signature=magic_signature,
            version=version_str,
            capability_flags=cap_flags,
            memory_mb=memory_mb,
            cpu_percent=cpu_percent,
            throughput=throughput,
            categories=categories,
            key_capabilities=capabilities,
            efficiency_score=efficiency,
            confidence=tool_data.get('confidence', 0.5)
        )
    
    def _decode_capability_flags(self, flags: int) -> List[str]:
        """Decode capability flags into human-readable capabilities."""
        capabilities = []
        
        # Define flag positions and meanings
        flag_meanings = {
            0: "text_processing",
            1: "json_handling", 
            2: "file_operations",
            3: "stdin_support",
            4: "recursive_operations",
            5: "parallel_processing",
            6: "streaming_support",
            7: "pattern_matching",
            8: "case_handling",
            9: "word_boundaries",
            10: "line_numbering",
            11: "context_aware",
            12: "binary_support",
            13: "compression",
            14: "network_operations",
            15: "real_time_processing"
        }
        
        for bit_pos, capability in flag_meanings.items():
            if flags & (1 << bit_pos):
                capabilities.append(capability)
        
        return capabilities
    
    def _categorize_tool(self, tool_name: str, capabilities: List[str]) -> List[str]:
        """Categorize tool based on name and capabilities."""
        categories = []
        
        # File I/O tools
        if any(cap in capabilities for cap in ["file_operations", "stdin_support"]):
            categories.append("file_io")
        
        # Text processing tools
        if any(cap in capabilities for cap in ["text_processing", "pattern_matching"]):
            categories.append("text_processing")
        
        # System utilities
        if tool_name in ["cat", "tee", "wc", "cut", "uniq"]:
            categories.append("text_utilities")
        
        # Search tools
        if tool_name in ["grep", "find"] or "pattern_matching" in capabilities:
            categories.append("search_tools")
        
        # Data tools
        if tool_name in ["sort", "cut", "uniq", "wc"]:
            categories.append("data_manipulation")
        
        # Network tools
        if "network_operations" in capabilities or tool_name == "curl":
            categories.append("network_tools")
        
        # Performance-based categories
        if "parallel_processing" in capabilities:
            categories.append("scalable_tools")
        
        if "streaming_support" in capabilities:
            categories.append("stream_processors")
        
        return categories or ["general_utility"]
    
    def _calculate_efficiency(self, memory_mb: int, cpu_percent: int) -> float:
        """Calculate efficiency score based on resource usage."""
        if memory_mb == 0 and cpu_percent == 0:
            return 0.5  # Default for unknown
        
        # Lower resource usage = higher efficiency
        memory_score = max(0, (1000 - memory_mb) / 1000)
        cpu_score = max(0, (100 - cpu_percent) / 100)
        return (memory_score + cpu_score) / 2
    
    def discover_capabilities(self) -> Dict:
        """Perform self-discovery analysis of available capabilities."""
        print("🔍 Agent performing self-discovery analysis...")
        print("=" * 60)
        
        discovery = {
            "timestamp": datetime.now().isoformat(),
            "total_tools": len(self.tool_profiles),
            "capability_summary": {},
            "tool_categories": defaultdict(list),
            "performance_analysis": {},
            "capability_matrix": dict(self.capability_matrix),
            "insights": []
        }
        
        # Analyze capabilities
        print("📊 Analyzing capability distribution...")
        all_capabilities = set()
        for profile in self.tool_profiles.values():
            all_capabilities.update(profile.key_capabilities)
            for category in profile.categories:
                discovery["tool_categories"][category].append(profile.name)
        
        # Capability frequency analysis
        cap_frequency = defaultdict(int)
        for profile in self.tool_profiles.values():
            for cap in profile.key_capabilities:
                cap_frequency[cap] += 1
        
        discovery["capability_summary"] = {
            "total_unique_capabilities": len(all_capabilities),
            "most_common_capabilities": sorted(cap_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "rare_capabilities": [cap for cap, count in cap_frequency.items() if count == 1]
        }
        
        # Performance analysis
        print("⚡ Analyzing performance characteristics...")
        efficiencies = [p.efficiency_score for p in self.tool_profiles.values()]
        memory_usage = [p.memory_mb for p in self.tool_profiles.values() if p.memory_mb > 0]
        cpu_usage = [p.cpu_percent for p in self.tool_profiles.values() if p.cpu_percent > 0]
        
        discovery["performance_analysis"] = {
            "average_efficiency": sum(efficiencies) / len(efficiencies) if efficiencies else 0,
            "most_efficient_tool": max(self.tool_profiles.values(), key=lambda p: p.efficiency_score).name,
            "average_memory_mb": sum(memory_usage) / len(memory_usage) if memory_usage else 0,
            "average_cpu_percent": sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
            "lightweight_tools": [p.name for p in self.tool_profiles.values() if p.efficiency_score > 0.7],
            "heavyweight_tools": [p.name for p in self.tool_profiles.values() if p.efficiency_score < 0.3]
        }
        
        # Generate insights
        print("💡 Generating insights...")
        insights = []
        
        # Tool coverage insights
        if len(discovery["tool_categories"]["text_utilities"]) >= 3:
            insights.append("Strong text processing capabilities with multiple specialized utilities")
        
        if "search_tools" in discovery["tool_categories"]:
            insights.append("Advanced search capabilities for both content and files")
        
        if discovery["performance_analysis"]["average_efficiency"] > 0.6:
            insights.append("Generally efficient tool collection with low resource requirements")
        
        # Capability gap analysis
        expected_capabilities = ["file_operations", "text_processing", "pattern_matching"]
        missing_caps = [cap for cap in expected_capabilities if cap not in all_capabilities]
        if missing_caps:
            insights.append(f"Potential capability gaps: {', '.join(missing_caps)}")
        
        # Specialization analysis
        if len(discovery["capability_summary"]["rare_capabilities"]) > 3:
            insights.append("High tool specialization with unique capabilities per tool")
        
        discovery["insights"] = insights
        self.discovery_report = discovery
        
        print(f"✅ Discovery complete: {len(all_capabilities)} capabilities across {len(discovery['tool_categories'])} categories")
        return discovery
    
    def generate_memo(self) -> str:
        """Generate natural language memo about discovered capabilities."""
        if not self.discovery_report:
            self.discover_capabilities()
        
        report = self.discovery_report
        memo_lines = []
        
        # Header
        memo_lines.extend([
            "🤖 SANDBOX AGENT CAPABILITY DISCOVERY MEMO",
            "=" * 60,
            f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Agent Status: Operational",
            f"Discovery Method: Binary TCP Descriptor Analysis",
            "",
            "EXECUTIVE SUMMARY:",
            "-" * 30
        ])
        
        # Summary statistics
        memo_lines.extend([
            f"• Total Tools Analyzed: {report['total_tools']}",
            f"• Unique Capabilities Discovered: {report['capability_summary']['total_unique_capabilities']}",
            f"• Tool Categories Identified: {len(report['tool_categories'])}",
            f"• Average Efficiency Rating: {report['performance_analysis']['average_efficiency']:.2f}/1.0",
            ""
        ])
        
        # Capability overview
        memo_lines.extend([
            "CAPABILITY INVENTORY:",
            "-" * 30
        ])
        
        # Most common capabilities
        memo_lines.append("Core Capabilities (most common):")
        for cap, count in report['capability_summary']['most_common_capabilities']:
            percentage = (count / report['total_tools']) * 100
            memo_lines.append(f"  • {cap.replace('_', ' ').title()}: {count}/{report['total_tools']} tools ({percentage:.0f}%)")
        
        memo_lines.append("")
        
        # Tool categories
        memo_lines.extend([
            "FUNCTIONAL CATEGORIES:",
            "-" * 30
        ])
        
        for category, tools in report['tool_categories'].items():
            category_name = category.replace('_', ' ').title()
            memo_lines.append(f"• {category_name}: {', '.join(tools)} ({len(tools)} tools)")
        
        memo_lines.append("")
        
        # Performance analysis
        memo_lines.extend([
            "PERFORMANCE PROFILE:",
            "-" * 30,
            f"• Most Efficient Tool: {report['performance_analysis']['most_efficient_tool']}",
            f"• Lightweight Tools: {', '.join(report['performance_analysis']['lightweight_tools'])}",
        ])
        
        if report['performance_analysis']['heavyweight_tools']:
            memo_lines.append(f"• Resource-Intensive Tools: {', '.join(report['performance_analysis']['heavyweight_tools'])}")
        
        avg_mem = report['performance_analysis']['average_memory_mb']
        avg_cpu = report['performance_analysis']['average_cpu_percent']
        if avg_mem > 0:
            memo_lines.append(f"• Average Memory Usage: {avg_mem:.0f} MB")
        if avg_cpu > 0:
            memo_lines.append(f"• Average CPU Usage: {avg_cpu:.0f}%")
        
        memo_lines.append("")
        
        # Key insights
        memo_lines.extend([
            "KEY INSIGHTS:",
            "-" * 30
        ])
        
        for insight in report['insights']:
            memo_lines.append(f"• {insight}")
        
        memo_lines.append("")
        
        # Capability matrix highlights
        memo_lines.extend([
            "CAPABILITY COMBINATIONS:",
            "-" * 30
        ])
        
        # Find tools with multiple capabilities
        multi_cap_tools = [(name, len(profile.key_capabilities)) 
                          for name, profile in self.tool_profiles.items() 
                          if len(profile.key_capabilities) > 2]
        multi_cap_tools.sort(key=lambda x: x[1], reverse=True)
        
        if multi_cap_tools:
            memo_lines.append("Most Versatile Tools:")
            for tool_name, cap_count in multi_cap_tools[:3]:
                profile = self.tool_profiles[tool_name]
                caps = ', '.join(profile.key_capabilities[:3])
                if len(profile.key_capabilities) > 3:
                    caps += "..."
                memo_lines.append(f"  • {tool_name}: {cap_count} capabilities ({caps})")
        
        memo_lines.append("")
        
        # Recommendations
        memo_lines.extend([
            "OPERATIONAL RECOMMENDATIONS:",
            "-" * 30,
            "• Leverage text processing tools for content analysis workflows",
            "• Use search tools (grep, find) for efficient data discovery", 
            "• Combine lightweight tools for complex processing pipelines",
            "• Utilize file I/O tools for data transformation tasks",
            ""
        ])
        
        # Technical details
        memo_lines.extend([
            "TECHNICAL IMPLEMENTATION:",
            "-" * 30,
            "• Binary Descriptor Format: 20-byte TCP standard",
            "• Analysis Method: Bitwise capability flag decoding",
            "• Performance Metrics: Memory, CPU, and throughput analysis",
            "• Confidence Scoring: Automated extraction validation",
            f"• Total Binary Data: {report['total_tools'] * 20} bytes for complete capability profile",
            ""
        ])
        
        # Footer
        memo_lines.extend([
            "=" * 60,
            "🎯 CONCLUSION: Agent has successfully identified comprehensive",
            "   tool capabilities through binary analysis. Ready for",
            "   intelligent tool selection and workflow automation.",
            "",
            "Generated by: Sandbox Agent v1.0",
            "Data Source: TCP Binary Descriptors",
            f"Analysis Confidence: {sum(p.confidence for p in self.tool_profiles.values()) / len(self.tool_profiles):.2f}/1.0"
        ])
        
        return "\n".join(memo_lines)
    
    def save_memo(self, output_path: str = None) -> str:
        """Save the capability memo to a file."""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(Path(__file__).parent / f"capability_memo_{timestamp}.txt")
        
        memo_content = self.generate_memo()
        
        with open(output_path, 'w') as f:
            f.write(memo_content)
        
        print(f"📄 Memo saved to: {output_path}")
        return output_path
    
    def interactive_query(self) -> None:
        """Interactive mode for querying agent capabilities."""
        print("\n🤖 INTERACTIVE AGENT QUERY MODE")
        print("=" * 50)
        print("Ask me about my capabilities! Type 'help' for commands or 'quit' to exit.")
        print()
        
        while True:
            try:
                query = input("Agent> ").strip().lower()
                
                if query in ['quit', 'exit', 'q']:
                    print("👋 Agent shutting down...")
                    break
                
                elif query == 'help':
                    print("Available commands:")
                    print("  tools          - List all available tools")
                    print("  capabilities   - Show unique capabilities")
                    print("  categories     - Show tool categories") 
                    print("  best <task>    - Find best tool for task")
                    print("  analyze <tool> - Analyze specific tool")
                    print("  memo           - Generate full capability memo")
                    print("  help           - Show this help")
                    print("  quit           - Exit interactive mode")
                
                elif query == 'tools':
                    tools = list(self.tool_profiles.keys())
                    print(f"Available tools ({len(tools)}): {', '.join(sorted(tools))}")
                
                elif query == 'capabilities':
                    all_caps = set()
                    for profile in self.tool_profiles.values():
                        all_caps.update(profile.key_capabilities)
                    print(f"Discovered capabilities ({len(all_caps)}):")
                    for cap in sorted(all_caps):
                        tools_with_cap = self.capability_matrix.get(cap, [])
                        print(f"  • {cap.replace('_', ' ').title()}: {len(tools_with_cap)} tools")
                
                elif query == 'categories':
                    if not self.discovery_report:
                        self.discover_capabilities()
                    for category, tools in self.discovery_report['tool_categories'].items():
                        print(f"• {category.replace('_', ' ').title()}: {', '.join(tools)}")
                
                elif query.startswith('best '):
                    task = query[5:]
                    suggestion = self._suggest_tool_for_task(task)
                    print(f"Best tool for '{task}': {suggestion}")
                
                elif query.startswith('analyze '):
                    tool_name = query[8:]
                    if tool_name in self.tool_profiles:
                        self._show_tool_analysis(tool_name)
                    else:
                        print(f"Tool '{tool_name}' not found. Available tools: {', '.join(self.tool_profiles.keys())}")
                
                elif query == 'memo':
                    print("\nGenerating capability memo...\n")
                    print(self.generate_memo())
                
                else:
                    print("Unknown command. Type 'help' for available commands.")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Agent interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _suggest_tool_for_task(self, task: str) -> str:
        """Suggest best tool for a given task description."""
        task_lower = task.lower()
        
        # Simple keyword matching
        if any(word in task_lower for word in ['search', 'find', 'grep', 'pattern']):
            if 'file' in task_lower:
                return "find (file search)"
            else:
                return "grep (text search)"
        
        elif any(word in task_lower for word in ['count', 'lines', 'words']):
            return "wc (word count)"
        
        elif any(word in task_lower for word in ['sort', 'order', 'arrange']):
            return "sort (text sorting)"
        
        elif any(word in task_lower for word in ['unique', 'duplicate', 'uniq']):
            return "uniq (remove duplicates)"
        
        elif any(word in task_lower for word in ['cut', 'extract', 'column']):
            return "cut (extract fields)"
        
        elif any(word in task_lower for word in ['download', 'fetch', 'http', 'url']):
            return "curl (network transfer)"
        
        elif any(word in task_lower for word in ['display', 'show', 'read']):
            return "cat (display files)"
        
        elif any(word in task_lower for word in ['write', 'save', 'output']):
            return "tee (write to file and stdout)"
        
        else:
            # Find most versatile tool
            most_versatile = max(self.tool_profiles.values(), 
                               key=lambda p: len(p.key_capabilities))
            return f"{most_versatile.name} (most versatile: {len(most_versatile.key_capabilities)} capabilities)"
    
    def _show_tool_analysis(self, tool_name: str) -> None:
        """Show detailed analysis of a specific tool."""
        profile = self.tool_profiles[tool_name]
        
        print(f"\n🔧 ANALYSIS: {tool_name.upper()}")
        print("-" * 40)
        print(f"Binary Signature: {profile.magic_signature}")
        print(f"Version: {profile.version}")
        print(f"Categories: {', '.join(profile.categories)}")
        print(f"Efficiency Score: {profile.efficiency_score:.2f}/1.0")
        print(f"Confidence: {profile.confidence:.2f}")
        
        if profile.memory_mb > 0 or profile.cpu_percent > 0:
            print(f"Resource Usage: {profile.memory_mb}MB memory, {profile.cpu_percent}% CPU")
        
        print(f"Capabilities ({len(profile.key_capabilities)}):")
        for cap in profile.key_capabilities:
            print(f"  • {cap.replace('_', ' ').title()}")
        
        # Show similar tools
        similar_tools = []
        for other_name, other_profile in self.tool_profiles.items():
            if other_name != tool_name:
                shared_caps = set(profile.key_capabilities) & set(other_profile.key_capabilities)
                if len(shared_caps) >= 2:
                    similar_tools.append((other_name, len(shared_caps)))
        
        if similar_tools:
            similar_tools.sort(key=lambda x: x[1], reverse=True)
            print(f"Similar tools: {', '.join(tool + f'({shared})' for tool, shared in similar_tools[:3])}")


def main():
    """Main function to demonstrate sandbox agent capabilities."""
    print("🚀 SANDBOX AGENT DEMONSTRATION")
    print("=" * 60)
    print("Creating enhanced naive agent with self-discovery capabilities...")
    print()
    
    # Initialize agent
    agent = SandboxAgent()
    
    # Perform self-discovery
    discovery = agent.discover_capabilities()
    print()
    
    # Generate and save memo
    print("📝 Generating capability memo...")
    memo_path = agent.save_memo()
    print()
    
    # Show summary
    print("📊 DISCOVERY SUMMARY:")
    print("-" * 40)
    print(f"Tools analyzed: {discovery['total_tools']}")
    print(f"Capabilities found: {discovery['capability_summary']['total_unique_capabilities']}")
    print(f"Categories identified: {len(discovery['tool_categories'])}")
    print(f"Insights generated: {len(discovery['insights'])}")
    print()
    
    # Quick demo of key capabilities
    print("🔑 KEY FINDINGS:")
    print("-" * 40)
    for insight in discovery['insights'][:3]:
        print(f"• {insight}")
    print()
    
    # Show most capable tools
    print("🏆 MOST CAPABLE TOOLS:")
    print("-" * 40)
    versatile_tools = sorted(agent.tool_profiles.values(), 
                           key=lambda p: len(p.key_capabilities), reverse=True)
    for i, profile in enumerate(versatile_tools[:3], 1):
        caps = ', '.join(profile.key_capabilities[:3])
        if len(profile.key_capabilities) > 3:
            caps += f" (+{len(profile.key_capabilities)-3} more)"
        print(f"{i}. {profile.name}: {caps}")
    print()
    
    # Offer interactive mode
    response = input("🤖 Enter interactive query mode? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        agent.interactive_query()
    
    print("\n🎉 Sandbox agent demonstration complete!")
    print(f"📄 Full memo saved to: {memo_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()