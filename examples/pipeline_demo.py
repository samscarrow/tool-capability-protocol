#!/usr/bin/env python3
"""
Complete demonstration of the TCP analysis pipeline.

This script shows how to use the pipeline to analyze various commands
and generate TCP descriptors using different LLM providers.
"""

import sys
import json
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tcp.analysis.pipeline import TCPGenerationPipeline


def demo_basic_usage():
    """Demonstrate basic pipeline usage."""
    print("=== Basic Pipeline Usage Demo ===\n")
    
    # Initialize pipeline with basic parsing (no LLM required)
    pipeline = TCPGenerationPipeline(llm_provider="basic")
    
    # Analyze a simple command
    print("1. Analyzing 'grep' with basic parsing:")
    print("-" * 50)
    
    result = pipeline.process_command("grep", output_formats=["json", "binary"])
    
    if result["success"]:
        print(f"✅ Success!")
        print(f"Tool: {result['capabilities']['tool_name']}")
        print(f"Version: {result['capabilities']['version']}")
        print(f"Description: {result['capabilities']['description']}")
        print(f"Confidence: {result['capabilities']['confidence_score']:.2f}")
        print(f"Extraction method: {result['capabilities']['extraction_method']}")
        
        # Show some capabilities
        caps = result['capabilities']
        print("\nDetected capabilities:")
        print(f"  📁 Supports files: {caps['supports_files']}")
        print(f"  📂 Supports directories: {caps['supports_directories']}")
        print(f"  🔄 Supports recursion: {caps['supports_recursion']}")
        print(f"  ⚡ Supports parallel: {caps['supports_parallel']}")
        
        # Show binary descriptor
        if "binary" in result["outputs"]:
            binary_info = result["outputs"]["binary"]
            print(f"\n📦 Binary descriptor: {binary_info['size_bytes']} bytes")
            print(f"   Hex: {binary_info['data'][:32]}...")
        
    else:
        print(f"❌ Failed: {result['error']}")
    
    print("\n" + "="*60 + "\n")


def demo_llm_comparison():
    """Compare different LLM providers."""
    print("=== LLM Provider Comparison Demo ===\n")
    
    providers = [
        ("basic", "Basic parsing only"),
        ("local_llm", "Local Ollama LLM"),
        ("langchain_openai", "OpenAI via LangChain"),
    ]
    
    command = "find"
    
    for provider, description in providers:
        print(f"Testing: {provider} ({description})")
        print("-" * 50)
        
        try:
            start_time = time.time()
            pipeline = TCPGenerationPipeline(llm_provider=provider)
            
            # Check availability
            if provider != "basic" and (not pipeline.llm_extractor or not pipeline.llm_extractor.is_available()):
                print(f"  ⚠️  Provider not available (skipping)\n")
                continue
            
            # Process command
            result = pipeline.process_command(command, output_formats=["json"])
            processing_time = time.time() - start_time
            
            if result["success"]:
                caps = result["capabilities"]
                print(f"  ✅ Success ({processing_time:.2f}s)")
                print(f"     Confidence: {caps['confidence_score']:.2f}")
                print(f"     Supports recursion: {caps['supports_recursion']}")
                print(f"     Supports parallel: {caps['supports_parallel']}")
                print(f"     Memory usage: {caps['memory_usage']}")
                print(f"     CPU usage: {caps['cpu_usage']}")
                
                # Count detected options
                commands = caps.get('commands', [])
                if commands:
                    options_count = sum(len(cmd.get('options', [])) for cmd in commands)
                    print(f"     Detected options: {options_count}")
                
            else:
                print(f"  ❌ Failed: {result['error']}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    print("="*60 + "\n")


def demo_batch_processing():
    """Demonstrate batch processing of multiple commands."""
    print("=== Batch Processing Demo ===\n")
    
    # Commands with different characteristics
    commands = [
        "ls",        # Simple file listing
        "grep",      # Text processing
        "find",      # File system traversal
        "curl",      # Network tool
        "tar",       # Archive tool
    ]
    
    print(f"Batch processing {len(commands)} commands:")
    print("-" * 50)
    
    pipeline = TCPGenerationPipeline(llm_provider="basic")  # Use basic for speed
    
    start_time = time.time()
    batch_result = pipeline.batch_process_commands(commands)
    total_time = time.time() - start_time
    
    print(f"Completed in {total_time:.2f}s")
    print(f"Success rate: {batch_result['summary']['success_rate']:.1%}")
    print(f"Successful: {batch_result['successful']}")
    print(f"Failed: {batch_result['failed']}")
    print(f"Average confidence: {batch_result['summary']['avg_confidence']:.2f}")
    
    # Show individual results
    print("\nIndividual results:")
    for command, result in batch_result["results"].items():
        status = "✅" if result["success"] else "❌"
        confidence = "N/A"
        if result.get("capabilities"):
            confidence = f"{result['capabilities']['confidence_score']:.2f}"
        print(f"  {status} {command:8} (confidence: {confidence})")
    
    # Show common errors
    if batch_result['summary']['most_common_errors']:
        print("\nMost common errors:")
        for error, count in batch_result['summary']['most_common_errors'][:3]:
            print(f"  • {error}: {count} occurrences")
    
    print("\n" + "="*60 + "\n")


def demo_output_formats():
    """Demonstrate different output formats."""
    print("=== Output Formats Demo ===\n")
    
    pipeline = TCPGenerationPipeline(llm_provider="basic")
    
    print("Analyzing 'sort' command with all output formats:")
    print("-" * 50)
    
    result = pipeline.process_command(
        "sort", 
        output_formats=["tcp", "json", "binary", "openapi"]
    )
    
    if result["success"]:
        print("✅ Analysis successful\n")
        
        # Show each output format
        for format_name, format_data in result["outputs"].items():
            print(f"📋 {format_name.upper()} Format:")
            
            if format_name == "binary":
                print(f"   Size: {format_data['size_bytes']} bytes")
                print(f"   Hex: {format_data['data']}")
            elif format_name == "tcp":
                print(f"   Tool: {format_data['name']}")
                print(f"   Version: {format_data['version']}")
                print(f"   Commands: {len(format_data.get('commands', []))}")
            elif format_name == "json":
                print(f"   Tool: {format_data['tool']}")
                print(f"   Commands: {len(format_data.get('commands', {}))}")
                if 'capabilities' in format_data:
                    processing = format_data['capabilities']['processing']
                    print(f"   Supports stdin: {processing['supports_stdin']}")
            elif format_name == "openapi":
                print(f"   API Title: {format_data['info']['title']}")
                print(f"   Paths: {len(format_data['paths'])}")
                print(f"   Schemas: {len(format_data['components']['schemas'])}")
            
            print()
    
    else:
        print(f"❌ Failed: {result['error']}")
    
    print("="*60 + "\n")


def demo_custom_help_text():
    """Demonstrate using custom help text."""
    print("=== Custom Help Text Demo ===\n")
    
    # Simulate a custom tool's help text
    custom_help = """
my-custom-tool - A demonstration tool for TCP analysis

USAGE:
    my-custom-tool [OPTIONS] <input-file>

OPTIONS:
    -f, --format <FORMAT>     Output format (json, xml, csv)
    -o, --output <FILE>       Output file path
    -v, --verbose             Enable verbose output
    -q, --quiet               Suppress output
    --parallel <N>            Number of parallel threads
    --recursive               Process directories recursively
    --include <PATTERN>       Include files matching pattern
    --exclude <PATTERN>       Exclude files matching pattern

EXAMPLES:
    my-custom-tool input.txt
    my-custom-tool -f json -o output.json input.txt
    my-custom-tool --recursive --include "*.txt" /path/to/dir
    """
    
    pipeline = TCPGenerationPipeline(llm_provider="basic")
    
    print("Analyzing custom tool with provided help text:")
    print("-" * 50)
    
    result = pipeline.process_command(
        "my-custom-tool",
        help_text=custom_help,
        output_formats=["json"]
    )
    
    if result["success"]:
        caps = result["capabilities"]
        print(f"✅ Successfully analyzed custom tool")
        print(f"   Confidence: {caps['confidence_score']:.2f}")
        print(f"   Detected capabilities:")
        print(f"     • Supports files: {caps['supports_files']}")
        print(f"     • Supports recursion: {caps['supports_recursion']}")
        print(f"     • Supports parallel: {caps['supports_parallel']}")
        
        # Show detected options
        commands = caps.get('commands', [])
        if commands and commands[0].get('options'):
            options = commands[0]['options']
            print(f"     • Detected {len(options)} options:")
            for opt in options[:5]:  # Show first 5
                flag = opt.get('long_flag') or opt.get('short_flag', '')
                print(f"       - {flag}: {opt.get('description', '')[:40]}...")
        
        # Show JSON output snippet
        json_output = result["outputs"]["json"]
        print(f"\n📄 JSON Schema (snippet):")
        print(f"   Tool: {json_output['tool']}")
        print(f"   Commands: {list(json_output['commands'].keys())}")
        
    else:
        print(f"❌ Failed: {result['error']}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Run all demos."""
    print("🚀 TCP Analysis Pipeline Comprehensive Demo\n")
    print("This demo shows how to convert arbitrary command help text")
    print("into structured TCP descriptors using various LLM providers.\n")
    
    demos = [
        demo_basic_usage,
        demo_llm_comparison,
        demo_batch_processing,
        demo_output_formats,
        demo_custom_help_text,
    ]
    
    for i, demo_func in enumerate(demos, 1):
        print(f"Demo {i}/{len(demos)}: {demo_func.__doc__.split('.')[0]}")
        try:
            demo_func()
        except KeyboardInterrupt:
            print("\n⚠️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"❌ Demo failed: {e}\n")
            continue
    
    print("🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Try: python tcp/tools/tcp_analyze.py grep --llm basic")
    print("2. Try: python tcp/tools/tcp_analyze.py --help")
    print("3. Install Ollama and try local LLM: tcp-analyze find --llm local_llm")
    print("4. Set up OpenAI API key and try: tcp-analyze docker --llm langchain_openai")


if __name__ == "__main__":
    main()