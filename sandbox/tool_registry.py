#!/usr/bin/env python3
"""
Tool Registry for Sandbox Environment

This module processes system utilities through the TCP pipeline and maintains
a registry of binary descriptors for the naive agent to discover.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tcp.analysis.pipeline import TCPGenerationPipeline


class SandboxToolRegistry:
    """Registry for managing TCP binary descriptors in the sandbox."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self.pipeline = TCPGenerationPipeline(llm_provider="basic")
        self.tool_descriptors = {}  # tool_name -> {binary, json, metadata}
        self.binary_registry = {}  # binary_hex -> tool_name
        
    def process_tool(self, tool_name: str, description: str = "") -> bool:
        """Process a tool and add it to the registry."""
        print(f"🔧 Processing '{tool_name}' through TCP pipeline...")
        
        try:
            result = self.pipeline.process_command(
                tool_name,
                output_formats=["tcp", "json", "binary"]
            )
            
            if result["success"]:
                # Extract binary descriptor
                binary_data = result["outputs"]["binary"]["data"]
                binary_bytes = bytes.fromhex(binary_data)
                
                # Store in registry
                self.tool_descriptors[tool_name] = {
                    "binary_hex": binary_data,
                    "binary_bytes": binary_bytes,
                    "json_descriptor": result["outputs"]["json"],
                    "tcp_descriptor": result["outputs"]["tcp"],
                    "capabilities": result["capabilities"],
                    "description": description,
                    "analysis_confidence": result["capabilities"]["confidence_score"]
                }
                
                # Add to binary lookup
                self.binary_registry[binary_data] = tool_name
                
                print(f"   ✅ Success: {len(binary_bytes)} bytes, confidence {result['capabilities']['confidence_score']:.2f}")
                return True
                
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def populate_with_system_utilities(self) -> None:
        """Populate registry with system utilities."""
        print("🏗️  Populating sandbox with system utilities...")
        print("=" * 60)
        
        # System utilities to process
        utilities = [
            # File writing/reading tools
            ("cat", "Concatenate and display file contents"),
            ("tee", "Write output to both file and stdout"), 
            
            # Text processing utilities
            ("wc", "Count words, lines, and characters"),
            ("cut", "Extract columns or fields from text"),
            ("uniq", "Remove or report duplicate lines"),
            
            # Previously processed tools for comparison
            ("grep", "Search text patterns"),
            ("find", "Search for files and directories"),
            ("sort", "Sort lines of text"),
            ("curl", "Transfer data from servers"),
        ]
        
        successful = 0
        for tool_name, description in utilities:
            if self.process_tool(tool_name, description):
                successful += 1
            print()
        
        print(f"📊 Registry populated: {successful}/{len(utilities)} tools processed")
        print(f"🤖 Binary descriptors ready for naive agent discovery")
        
    def get_binary_descriptors(self) -> Dict[str, bytes]:
        """Get all binary descriptors for agent discovery."""
        return {
            name: data["binary_bytes"] 
            for name, data in self.tool_descriptors.items()
        }
    
    def get_tool_metadata(self, tool_name: str) -> Dict:
        """Get metadata for a specific tool (for validation)."""
        return self.tool_descriptors.get(tool_name, {})
    
    def list_available_tools(self) -> List[str]:
        """List all tools in the registry."""
        return list(self.tool_descriptors.keys())
    
    def save_registry(self, filepath: str) -> None:
        """Save registry to file for persistence."""
        registry_data = {
            "tools": {},
            "binary_lookup": self.binary_registry,
            "metadata": {
                "total_tools": len(self.tool_descriptors),
                "generation_method": "TCP Basic Pipeline"
            }
        }
        
        # Serialize tool data (excluding binary bytes)
        for tool_name, data in self.tool_descriptors.items():
            registry_data["tools"][tool_name] = {
                "binary_hex": data["binary_hex"],
                "capabilities": data["capabilities"],
                "description": data["description"],
                "confidence": data["analysis_confidence"]
            }
        
        with open(filepath, 'w') as f:
            json.dump(registry_data, f, indent=2, default=str)
        
        print(f"💾 Registry saved to {filepath}")
    
    def load_registry(self, filepath: str) -> None:
        """Load registry from file."""
        with open(filepath, 'r') as f:
            registry_data = json.load(f)
        
        self.binary_registry = registry_data["binary_lookup"]
        
        for tool_name, data in registry_data["tools"].items():
            binary_bytes = bytes.fromhex(data["binary_hex"])
            self.tool_descriptors[tool_name] = {
                "binary_hex": data["binary_hex"],
                "binary_bytes": binary_bytes,
                "capabilities": data["capabilities"],
                "description": data["description"],
                "analysis_confidence": data["confidence"]
            }
        
        print(f"📂 Registry loaded: {len(self.tool_descriptors)} tools")


def main():
    """Main function to populate the registry."""
    registry = SandboxToolRegistry()
    
    print("🚀 TCP Sandbox Tool Registry")
    print("=" * 60)
    print("Processing system utilities to create binary descriptors")
    print("for naive agent discovery...")
    print()
    
    # Populate with utilities
    registry.populate_with_system_utilities()
    
    # Save registry
    registry_path = Path(__file__).parent / "tool_registry.json"
    registry.save_registry(str(registry_path))
    
    # Show summary
    print("\n📋 REGISTRY SUMMARY:")
    print("-" * 40)
    for tool_name in registry.list_available_tools():
        metadata = registry.get_tool_metadata(tool_name)
        binary_size = len(metadata["binary_bytes"])
        confidence = metadata["analysis_confidence"]
        print(f"{tool_name:8} | {binary_size:2d} bytes | {confidence:.2f} confidence")
    
    print(f"\n🎯 Ready for naive agent discovery!")
    print(f"   Total tools: {len(registry.list_available_tools())}")
    print(f"   Binary descriptors: {sum(len(data['binary_bytes']) for data in registry.tool_descriptors.values())} total bytes")


if __name__ == "__main__":
    main()