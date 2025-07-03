#!/usr/bin/env python3
"""
Enhanced Naive Agent Demo with Improved Capability Detection

This shows how the agent can make sophisticated tool selection decisions
based on enhanced binary TCP descriptors with better capability encoding.
"""

import sys
import struct
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tcp.analysis.pipeline import TCPGenerationPipeline


class EnhancedTCPEncoder:
    """Enhanced TCP binary encoder with better capability detection."""
    
    @staticmethod
    def encode_enhanced_binary(tool_name: str, capabilities: Dict, performance: Dict) -> bytes:
        """
        Create enhanced 20-byte binary descriptor with richer capability encoding.
        
        Format: Magic(4) + Version(2) + Capabilities(6) + Performance(6) + CRC(2)
        """
        # Magic bytes from tool name
        magic = hashlib.md5(tool_name.encode()).digest()[:4]
        
        # Version (simplified to 1.0)
        version = struct.pack('>H', 100)  # 1.0
        
        # Enhanced capability encoding (6 bytes = 48 bits)
        cap_flags = 0
        
        # Input capabilities (bits 0-7)
        if any(fmt in str(capabilities.get('input_formats', [])) for fmt in ['text', 'txt']):
            cap_flags |= (1 << 0)  # TEXT_INPUT
        if any(fmt in str(capabilities.get('input_formats', [])) for fmt in ['json']):
            cap_flags |= (1 << 1)  # JSON_INPUT
        if any(fmt in str(capabilities.get('input_formats', [])) for fmt in ['file', 'document']):
            cap_flags |= (1 << 2)  # FILE_INPUT
        if capabilities.get('supports_stdin', False):
            cap_flags |= (1 << 3)  # STDIN_INPUT
        if any(word in tool_name.lower() for word in ['find', 'search', 'grep', 'locate']):
            cap_flags |= (1 << 4)  # SEARCH_CAPABILITY
        if any(word in tool_name.lower() for word in ['sort', 'order', 'arrange']):
            cap_flags |= (1 << 5)  # SORT_CAPABILITY
        if any(word in tool_name.lower() for word in ['tar', 'zip', 'compress', 'archive']):
            cap_flags |= (1 << 6)  # ARCHIVE_CAPABILITY
        if any(word in tool_name.lower() for word in ['curl', 'wget', 'download', 'http']):
            cap_flags |= (1 << 7)  # NETWORK_CAPABILITY
        
        # Processing capabilities (bits 8-15)
        if capabilities.get('supports_recursion', False) or '-r' in tool_name or 'recursive' in str(capabilities):
            cap_flags |= (1 << 8)   # RECURSIVE_PROCESSING
        if capabilities.get('supports_parallel', False) or any(word in tool_name.lower() for word in ['parallel', 'thread']):
            cap_flags |= (1 << 9)   # PARALLEL_PROCESSING
        if capabilities.get('supports_streaming', False):
            cap_flags |= (1 << 10)  # STREAMING_PROCESSING
        if capabilities.get('supports_files', False) or any(fmt in str(capabilities.get('input_formats', [])) for fmt in ['file']):
            cap_flags |= (1 << 11)  # FILE_PROCESSING
        if any(word in tool_name.lower() for word in ['filter', 'transform', 'convert']):
            cap_flags |= (1 << 12)  # TRANSFORM_CAPABILITY
        if any(word in tool_name.lower() for word in ['analyze', 'parse', 'extract']):
            cap_flags |= (1 << 13)  # ANALYSIS_CAPABILITY
        if tool_name.lower() in ['find', 'locate', 'which', 'whereis']:
            cap_flags |= (1 << 14)  # DISCOVERY_CAPABILITY
        if capabilities.get('memory_usage', 'medium') == 'low':
            cap_flags |= (1 << 15)  # LIGHTWEIGHT
        
        # Output capabilities (bits 16-23)
        if any(fmt in str(capabilities.get('output_formats', [])) for fmt in ['text']):
            cap_flags |= (1 << 16)  # TEXT_OUTPUT
        if any(fmt in str(capabilities.get('output_formats', [])) for fmt in ['json']):
            cap_flags |= (1 << 17)  # JSON_OUTPUT
        if any(fmt in str(capabilities.get('output_formats', [])) for fmt in ['binary']):
            cap_flags |= (1 << 18)  # BINARY_OUTPUT
        if tool_name.lower() in ['tar', 'zip', 'gzip']:
            cap_flags |= (1 << 19)  # COMPRESSED_OUTPUT
        
        # Pack capability flags (6 bytes)
        cap_bytes = struct.pack('>Q', cap_flags)[:6]  # Take first 6 bytes of 8-byte int
        
        # Enhanced performance encoding (6 bytes)
        memory_mb = min(performance.get('memory_usage_mb', 100), 65535)
        cpu_percent = min(performance.get('cpu_usage_percent', 10), 255)
        
        # Infer additional metrics from tool type
        if tool_name.lower() in ['grep', 'find', 'search']:
            throughput = 1000  # High throughput for search tools
        elif tool_name.lower() in ['sort', 'uniq']:
            throughput = 500   # Medium throughput for processing
        elif tool_name.lower() in ['tar', 'gzip']:
            throughput = 200   # Lower throughput for compression
        else:
            throughput = 300   # Default
        
        startup_ms = 50 if cap_flags & (1 << 15) else 200  # Lightweight tools start faster
        
        perf_bytes = struct.pack('>HHBB',
            memory_mb,     # Memory usage (2 bytes)
            throughput,    # Throughput ops/sec (2 bytes) 
            cpu_percent,   # CPU usage (1 byte)
            startup_ms     # Startup time ms (1 byte)
        )
        
        # Calculate CRC16
        data = magic + version + cap_bytes + perf_bytes
        crc = struct.pack('>H', EnhancedTCPEncoder._calculate_crc16(data))
        
        return data + crc
    
    @staticmethod
    def _calculate_crc16(data: bytes) -> int:
        """Calculate CRC16 checksum."""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc & 0xFFFF


class SmartAgent:
    """Enhanced agent with better capability understanding."""
    
    def __init__(self):
        self.tool_registry = {}
        self.capability_names = {
            # Input capabilities
            0: 'text_input', 1: 'json_input', 2: 'file_input', 3: 'stdin_input',
            4: 'search_tool', 5: 'sort_tool', 6: 'archive_tool', 7: 'network_tool',
            # Processing capabilities  
            8: 'recursive', 9: 'parallel', 10: 'streaming', 11: 'file_processing',
            12: 'transform', 13: 'analysis', 14: 'discovery', 15: 'lightweight',
            # Output capabilities
            16: 'text_output', 17: 'json_output', 18: 'binary_output', 19: 'compressed_output'
        }
    
    def register_tool_enhanced(self, tool_name: str, capabilities: Dict, performance: Dict):
        """Register tool with enhanced binary encoding."""
        binary_desc = EnhancedTCPEncoder.encode_enhanced_binary(tool_name, capabilities, performance)
        self.tool_registry[tool_name] = binary_desc
        print(f"🤖 Enhanced agent learned '{tool_name}' capabilities")
    
    def decode_enhanced_capabilities(self, binary_desc: bytes) -> Dict:
        """Decode enhanced 20-byte binary descriptor."""
        if len(binary_desc) != 20:
            raise ValueError(f"Invalid descriptor length: {len(binary_desc)}")
        
        # Parse format: Magic(4) + Version(2) + Capabilities(6) + Performance(6) + CRC(2)
        magic = binary_desc[:4]
        version = struct.unpack('>H', binary_desc[4:6])[0]
        cap_bytes = binary_desc[6:12]
        perf_bytes = binary_desc[12:18]
        crc = struct.unpack('>H', binary_desc[18:20])[0]
        
        # Decode capability flags (6 bytes = 48 bits)
        cap_flags = struct.unpack('>Q', b'\x00\x00' + cap_bytes)[0]
        
        # Extract individual capabilities
        capabilities = {}
        for bit_pos, cap_name in self.capability_names.items():
            capabilities[cap_name] = bool(cap_flags & (1 << bit_pos))
        
        # Decode performance metrics
        memory_mb, throughput, cpu_percent, startup_ms = struct.unpack('>HHBB', perf_bytes)
        
        return {
            'magic': magic.hex(),
            'version': f"{version // 100}.{version % 100}",
            'capabilities': capabilities,
            'performance': {
                'memory_mb': memory_mb,
                'throughput_ops_sec': throughput,
                'cpu_percent': cpu_percent,
                'startup_ms': startup_ms
            },
            'raw_flags': cap_flags
        }
    
    def analyze_task_requirements(self, task_description: str) -> List[str]:
        """Analyze task to determine required capabilities."""
        requirements = []
        task_lower = task_description.lower()
        
        # Input requirements
        if any(word in task_lower for word in ['file', 'files', 'document']):
            requirements.append('file_input')
        if any(word in task_lower for word in ['text', 'string', 'content']):
            requirements.append('text_input')
        if any(word in task_lower for word in ['json', 'structured']):
            requirements.append('json_input')
        
        # Functional requirements
        if any(word in task_lower for word in ['search', 'find', 'look', 'grep', 'locate']):
            requirements.append('search_tool')
        if any(word in task_lower for word in ['sort', 'order', 'arrange', 'rank']):
            requirements.append('sort_tool')
        if any(word in task_lower for word in ['archive', 'compress', 'pack', 'bundle']):
            requirements.append('archive_tool')
        if any(word in task_lower for word in ['download', 'fetch', 'http', 'url', 'web']):
            requirements.append('network_tool')
        
        # Processing requirements
        if any(word in task_lower for word in ['recursive', 'deep', 'all', 'subdirectory']):
            requirements.append('recursive')
        if any(word in task_lower for word in ['parallel', 'fast', 'concurrent', 'multiple']):
            requirements.append('parallel')
        if any(word in task_lower for word in ['stream', 'pipe', 'flow', 'continuous']):
            requirements.append('streaming')
        if any(word in task_lower for word in ['transform', 'convert', 'modify', 'change']):
            requirements.append('transform')
        if any(word in task_lower for word in ['analyze', 'parse', 'extract', 'examine']):
            requirements.append('analysis')
        
        # Performance requirements
        if any(word in task_lower for word in ['quick', 'fast', 'efficient', 'lightweight']):
            requirements.append('lightweight')
        
        return requirements
    
    def smart_tool_selection(self, task_description: str) -> Optional[Tuple[str, Dict, str]]:
        """Make intelligent tool selection with reasoning."""
        print(f"\n🧠 Smart Agent analyzing: '{task_description}'")
        
        requirements = self.analyze_task_requirements(task_description)
        print(f"   📋 Detected requirements: {requirements}")
        
        # Score each tool
        tool_scores = []
        
        for tool_name, binary_desc in self.tool_registry.items():
            caps_data = self.decode_enhanced_capabilities(binary_desc)
            capabilities = caps_data['capabilities']
            performance = caps_data['performance']
            
            score = 0
            reasoning = []
            
            # Score based on required capabilities
            for req in requirements:
                if capabilities.get(req, False):
                    score += 10
                    reasoning.append(f"✅ {req}")
                else:
                    reasoning.append(f"❌ {req}")
            
            # Bonus for performance characteristics
            if performance['memory_mb'] < 100:
                score += 2
                reasoning.append("💾 Low memory")
            if performance['startup_ms'] < 100:
                score += 2  
                reasoning.append("⚡ Fast startup")
            if performance['throughput_ops_sec'] > 500:
                score += 3
                reasoning.append("🚀 High throughput")
            
            tool_scores.append((tool_name, score, reasoning, caps_data))
        
        # Sort by score
        tool_scores.sort(key=lambda x: x[1], reverse=True)
        
        if tool_scores and tool_scores[0][1] > 0:
            best_tool, best_score, reasoning, caps_data = tool_scores[0]
            
            print(f"   🏆 Selected: {best_tool} (score: {best_score})")
            print(f"   💡 Reasoning: {' | '.join(reasoning[:5])}")
            
            return best_tool, caps_data, ' | '.join(reasoning)
        
        print("   ❌ No suitable tool found")
        return None
    
    def explain_tool_understanding(self, tool_name: str):
        """Explain agent's understanding of a tool."""
        if tool_name not in self.tool_registry:
            print(f"❌ Tool '{tool_name}' not known")
            return
        
        binary_desc = self.tool_registry[tool_name]
        caps_data = self.decode_enhanced_capabilities(binary_desc)
        
        print(f"\n🔍 Smart Agent's understanding of '{tool_name}':")
        print("=" * 55)
        
        print(f"📦 Binary: {binary_desc.hex()}")
        print(f"🏷️  Version: {caps_data['version']}")
        print(f"🔢 Capability flags: 0x{caps_data['raw_flags']:012x}")
        
        # Categorize capabilities
        input_caps = {k: v for k, v in caps_data['capabilities'].items() if k.endswith('_input') and v}
        tool_caps = {k: v for k, v in caps_data['capabilities'].items() if k.endswith('_tool') and v}
        process_caps = {k: v for k, v in caps_data['capabilities'].items() 
                       if k in ['recursive', 'parallel', 'streaming', 'lightweight'] and v}
        output_caps = {k: v for k, v in caps_data['capabilities'].items() if k.endswith('_output') and v}
        
        print(f"\n📥 Input Capabilities: {list(input_caps.keys()) if input_caps else ['None detected']}")
        print(f"🛠️  Tool Type: {list(tool_caps.keys()) if tool_caps else ['Generic']}")
        print(f"⚙️  Processing: {list(process_caps.keys()) if process_caps else ['Basic']}")
        print(f"📤 Output: {list(output_caps.keys()) if output_caps else ['Standard']}")
        
        perf = caps_data['performance']
        print(f"\n📊 Performance Profile:")
        print(f"   💾 Memory: {perf['memory_mb']} MB")
        print(f"   🖥️  CPU: {perf['cpu_percent']}%")
        print(f"   ⚡ Startup: {perf['startup_ms']} ms")
        print(f"   🚀 Throughput: {perf['throughput_ops_sec']} ops/sec")


def demonstrate_smart_agent():
    """Demonstrate the enhanced smart agent."""
    print("🧠 Smart Agent Enhanced TCP Binary Demo")
    print("=" * 60)
    print("Agent understands richer tool capabilities from enhanced 20-byte descriptors!")
    print()
    
    # Initialize
    pipeline = TCPGenerationPipeline(llm_provider="basic")
    agent = SmartAgent()
    
    # Learn about tools with enhanced encoding
    tools_info = [
        ("grep", "Text search and pattern matching tool"),
        ("find", "File and directory discovery tool"),
        ("sort", "Data sorting and organization tool"),
        ("tar", "Archive creation and extraction tool"),
        ("curl", "Network data transfer tool")
    ]
    
    print("📚 Teaching smart agent with enhanced descriptors...")
    print("-" * 60)
    
    for tool_name, description in tools_info:
        try:
            result = pipeline.process_command(tool_name, output_formats=["json"])
            if result["success"]:
                capabilities = result["capabilities"]
                performance = {
                    'memory_usage_mb': 50 if tool_name in ['sort', 'grep'] else 100,
                    'cpu_usage_percent': 20 if tool_name in ['find', 'curl'] else 30
                }
                
                agent.register_tool_enhanced(tool_name, capabilities, performance)
                print(f"   ✅ {tool_name}: {description}")
            
        except Exception as e:
            print(f"   ❌ {tool_name}: Error - {e}")
    
    print(f"\n🧠 Smart agent learned about {len(agent.tool_registry)} tools")
    
    # Demonstrate understanding
    print("\n🔍 ENHANCED CAPABILITY UNDERSTANDING")
    print("=" * 60)
    
    if "grep" in agent.tool_registry:
        agent.explain_tool_understanding("grep")
    
    # Demonstrate smart task analysis
    print("\n🎯 INTELLIGENT TASK MATCHING")
    print("=" * 60)
    
    test_tasks = [
        "Search for error patterns in log files",
        "Find all Python files in subdirectories recursively", 
        "Sort a large dataset efficiently with minimal memory",
        "Archive project files for backup with compression",
        "Download configuration files from a web server"
    ]
    
    for task in test_tasks:
        result = agent.smart_tool_selection(task)
        if result:
            tool_name, caps_data, reasoning = result
            perf = caps_data['performance']
            print(f"   ⚡ Performance: {perf['memory_mb']}MB, {perf['startup_ms']}ms startup")
        print()
    
    # Show capability matrix
    print("📊 TOOL CAPABILITY MATRIX")
    print("=" * 60)
    
    print(f"{'Tool':<8} {'Search':<7} {'Archive':<8} {'Network':<8} {'Recursive':<10} {'Lightweight':<12}")
    print("-" * 60)
    
    for tool_name in agent.tool_registry:
        caps_data = agent.decode_enhanced_capabilities(agent.tool_registry[tool_name])
        caps = caps_data['capabilities']
        
        search = "✅" if caps.get('search_tool') else "❌"
        archive = "✅" if caps.get('archive_tool') else "❌"
        network = "✅" if caps.get('network_tool') else "❌"
        recursive = "✅" if caps.get('recursive') else "❌"
        lightweight = "✅" if caps.get('lightweight') else "❌"
        
        print(f"{tool_name:<8} {search:<7} {archive:<8} {network:<8} {recursive:<10} {lightweight:<12}")
    
    print("\n" + "=" * 60)
    print("🎉 SMART AGENT DEMONSTRATION COMPLETE")
    print("=" * 60)
    print()
    print("🚀 KEY IMPROVEMENTS:")
    print("• 48-bit capability flags vs 32-bit (50% more capability data)")
    print("• Tool-type detection from name analysis")
    print("• Enhanced performance metrics (memory, CPU, throughput, startup)")
    print("• Semantic capability matching vs bit-pattern matching")
    print("• Scoring-based tool selection with reasoning")
    print()
    print("💡 AGENT INTELLIGENCE:")
    print("• Understands tool purposes from binary signatures")
    print("• Makes reasoned decisions based on multiple factors")
    print("• Provides explainable tool selection rationale")
    print("• Adapts to performance vs functionality trade-offs")


if __name__ == "__main__":
    try:
        demonstrate_smart_agent()
        
        print("\n🔮 FUTURE POSSIBILITIES:")
        print("• ML-trained capability detection from usage patterns")
        print("• Dynamic performance profiling and binary updates")
        print("• Tool recommendation systems based on TCP similarity")
        print("• Automated tool composition for complex workflows")
        
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()