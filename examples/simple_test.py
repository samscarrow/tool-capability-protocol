#!/usr/bin/env python3
"""Simple test of the TCP analysis pipeline."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tcp.analysis.pipeline import TCPGenerationPipeline


def main():
    """Run a simple test of the pipeline."""
    print("🔧 TCP Analysis Pipeline - Simple Test\n")
    
    try:
        # Test basic parsing (no LLM required)
        print("1. Testing basic parsing with 'ls' command...")
        
        pipeline = TCPGenerationPipeline(llm_provider="basic")
        result = pipeline.process_command("ls", output_formats=["json", "binary"])
        
        if result["success"]:
            print("   ✅ Success!")
            caps = result["capabilities"]
            print(f"   Tool: {caps['tool_name']}")
            print(f"   Confidence: {caps['confidence_score']:.2f}")
            print(f"   Extraction method: {caps['extraction_method']}")
            
            # Show binary output
            if "binary" in result["outputs"]:
                binary_info = result["outputs"]["binary"]
                print(f"   Binary descriptor: {binary_info['size_bytes']} bytes")
            
            # Show JSON structure
            if "json" in result["outputs"]:
                json_output = result["outputs"]["json"]
                print(f"   JSON commands: {len(json_output.get('commands', {}))}")
            
        else:
            print(f"   ❌ Failed: {result['error']}")
            return 1
        
        print("\n2. Testing custom help text...")
        
        custom_help = """
test-tool - A test utility

Usage: test-tool [OPTIONS] FILE...

Options:
  -v, --verbose     Enable verbose output
  -o, --output DIR  Output directory
  -f, --format FMT  Output format (json, xml)
  --recursive       Process directories recursively
  --parallel N      Use N parallel threads
"""
        
        result2 = pipeline.process_command(
            "test-tool",
            help_text=custom_help,
            output_formats=["json"]
        )
        
        if result2["success"]:
            print("   ✅ Success!")
            caps2 = result2["capabilities"]
            print(f"   Detected recursion support: {caps2['supports_recursion']}")
            print(f"   Detected parallel support: {caps2['supports_parallel']}")
            print(f"   Detected files support: {caps2['supports_files']}")
            
        else:
            print(f"   ❌ Failed: {result2['error']}")
            return 1
        
        print("\n🎉 All tests passed!")
        print("\nNext steps:")
        print("- Try: python tcp/tools/tcp_analyze.py grep")
        print("- Try: python examples/pipeline_demo.py")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())