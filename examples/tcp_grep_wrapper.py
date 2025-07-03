#!/usr/bin/env python3
"""
TCP wrapper for grep - makes grep capabilities machine-readable.

Usage:
    tcp-grep --tcp-capabilities          # Output capabilities in TCP format
    tcp-grep --tcp-binary               # Output binary descriptor
    tcp-grep --tcp-json                 # Output JSON schema
    tcp-grep --tcp-openapi              # Output OpenAPI spec
    tcp-grep [grep arguments]           # Pass through to actual grep
"""

import sys
import os
import json
import base64
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tcp.adapters.grep import GrepAdapter
from tcp.core.protocol import ToolCapabilityProtocol
from tcp.generators.json import JSONGenerator
from tcp.generators.openapi import OpenAPIGenerator


def main():
    """Main entry point for TCP grep wrapper."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    # Check for TCP-specific flags
    if sys.argv[1].startswith("--tcp-"):
        adapter = GrepAdapter()
        descriptor = adapter.create_descriptor()
        tcp = ToolCapabilityProtocol()
        
        if sys.argv[1] == "--tcp-capabilities":
            # Human-readable capability summary
            print(f"Tool: {descriptor.name} v{descriptor.version}")
            print(f"Description: {descriptor.description}")
            print("\nCapabilities:")
            for cap, enabled in descriptor.capabilities.items():
                status = "✓" if enabled else "✗"
                print(f"  {status} {cap}")
            print("\nPerformance:")
            for metric, value in descriptor.performance_metrics.items():
                print(f"  {metric}: {value}")
            
        elif sys.argv[1] == "--tcp-binary":
            # Output binary descriptor
            binary = tcp.generate_binary(descriptor)
            if sys.stdout.isatty():
                # Terminal output - show base64
                print(base64.b64encode(binary).decode())
            else:
                # Pipe output - raw binary
                sys.stdout.buffer.write(binary)
            
        elif sys.argv[1] == "--tcp-json":
            # Output JSON schema
            json_gen = JSONGenerator()
            schema = json_gen.generate(descriptor)
            print(json.dumps(schema, indent=2))
            
        elif sys.argv[1] == "--tcp-openapi":
            # Output OpenAPI specification
            openapi_gen = OpenAPIGenerator()
            spec = openapi_gen.generate(descriptor)
            print(json.dumps(spec, indent=2))
            
        elif sys.argv[1] == "--tcp-query":
            # Query specific capability
            if len(sys.argv) < 3:
                print("Usage: tcp-grep --tcp-query <capability>")
                sys.exit(1)
            capability = sys.argv[2]
            if capability in descriptor.capabilities:
                # Exit code 0 for true, 1 for false
                sys.exit(0 if descriptor.capabilities[capability] else 1)
            else:
                print(f"Unknown capability: {capability}")
                sys.exit(2)
        
    else:
        # Pass through to actual grep
        grep_cmd = ["grep"] + sys.argv[1:]
        result = subprocess.run(grep_cmd)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()