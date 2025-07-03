#!/usr/bin/env python3
"""
Demonstration of Tool Capability Protocol (TCP) applied to grep.

This example shows how TCP provides machine-readable capability descriptions
that are orders of magnitude more efficient than parsing help text.
"""

import json
import time
import base64
from typing import Dict, Any
import struct

# Simulate TCP imports (in real usage, these would come from the tcp package)
from dataclasses import dataclass, field
from enum import IntEnum, auto


class CommandFlag(IntEnum):
    """Binary flags for grep command capabilities."""
    BASIC_MATCH = 1 << 0        # Basic pattern matching
    REGEX = 1 << 1              # Regular expression support
    CASE_INSENSITIVE = 1 << 2   # -i flag
    INVERT_MATCH = 1 << 3       # -v flag
    WORD_MATCH = 1 << 4         # -w flag
    LINE_MATCH = 1 << 5         # -x flag
    COUNT_ONLY = 1 << 6         # -c flag
    FILES_WITH_MATCH = 1 << 7   # -l flag
    LINE_NUMBERS = 1 << 8       # -n flag
    RECURSIVE = 1 << 9          # -r flag
    QUIET = 1 << 10             # -q flag
    BINARY_FILES = 1 << 11      # Binary file handling
    CONTEXT = 1 << 12           # -A/-B/-C context lines
    COLOR = 1 << 13             # --color output
    PERL_REGEX = 1 << 14        # -P perl regex
    EXTENDED_REGEX = 1 << 15    # -E extended regex


@dataclass
class GrepCapabilityDescriptor:
    """Complete capability descriptor for grep."""
    name: str = "grep"
    version: str = "3.11"
    description: str = "Search for patterns in files"
    
    # Input/Output capabilities
    input_formats: list = field(default_factory=lambda: ["text", "stdin", "file", "directory"])
    output_formats: list = field(default_factory=lambda: ["text", "json", "null"])
    
    # Processing modes
    supports_streaming: bool = True
    supports_parallel: bool = True
    max_pattern_length: int = 2048
    max_file_size: str = "unlimited"
    
    # Command capabilities (as binary flags)
    command_flags: int = (
        CommandFlag.BASIC_MATCH |
        CommandFlag.REGEX |
        CommandFlag.CASE_INSENSITIVE |
        CommandFlag.INVERT_MATCH |
        CommandFlag.WORD_MATCH |
        CommandFlag.LINE_MATCH |
        CommandFlag.COUNT_ONLY |
        CommandFlag.FILES_WITH_MATCH |
        CommandFlag.LINE_NUMBERS |
        CommandFlag.RECURSIVE |
        CommandFlag.QUIET |
        CommandFlag.BINARY_FILES |
        CommandFlag.CONTEXT |
        CommandFlag.COLOR |
        CommandFlag.PERL_REGEX |
        CommandFlag.EXTENDED_REGEX
    )
    
    # Performance characteristics
    performance: dict = field(default_factory=lambda: {
        "avg_mb_per_sec": 500,
        "memory_overhead_mb": 10,
        "startup_time_ms": 5,
        "regex_engine": "PCRE2",
        "multithread_capable": True
    })


class GrepTCP:
    """TCP implementation for grep."""
    
    def __init__(self):
        self.descriptor = GrepCapabilityDescriptor()
    
    def generate_binary_descriptor(self) -> bytes:
        """
        Generate ultra-compact 20-byte binary descriptor.
        
        Format: Magic(4) + Version(2) + Flags(3) + Commands(1) + Performance(8) + CRC(2)
        """
        magic = b'GREP'  # 4 bytes
        version = struct.pack('>H', 311)  # 2 bytes (3.11 -> 311)
        
        # Pack capability flags into 3 bytes
        flags = struct.pack('>I', self.descriptor.command_flags)[:3]  # 3 bytes
        
        # Commands byte (simplified: bit per major mode)
        commands = struct.pack('B', 0xFF)  # 1 byte (all commands supported)
        
        # Performance metrics (8 bytes)
        # Speed (2 bytes), Memory (2 bytes), Features (4 bytes)
        perf = struct.pack('>HHBBBB', 
            min(self.descriptor.performance['avg_mb_per_sec'], 65535),  # Speed MB/s
            self.descriptor.performance['memory_overhead_mb'],          # Memory MB
            1 if self.descriptor.supports_streaming else 0,             # Streaming
            1 if self.descriptor.supports_parallel else 0,              # Parallel
            1,  # PCRE2 support
            0   # Reserved
        )
        
        # Calculate simple CRC16
        data = magic + version + flags + commands + perf
        crc = struct.pack('>H', sum(data) % 65536)  # 2 bytes
        
        return data + crc
    
    def generate_json_schema(self) -> Dict[str, Any]:
        """Generate JSON Schema representation."""
        return {
            "tool": self.descriptor.name,
            "version": self.descriptor.version,
            "description": self.descriptor.description,
            "capabilities": {
                "input_formats": self.descriptor.input_formats,
                "output_formats": self.descriptor.output_formats,
                "streaming": self.descriptor.supports_streaming,
                "parallel": self.descriptor.supports_parallel,
                "commands": {
                    "search": {
                        "description": "Search for pattern in files",
                        "parameters": {
                            "pattern": {
                                "type": "string",
                                "description": "Search pattern (regex or literal)",
                                "required": True,
                                "max_length": self.descriptor.max_pattern_length
                            },
                            "files": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Files to search (optional, defaults to stdin)"
                            },
                            "case_insensitive": {
                                "type": "boolean",
                                "description": "Case insensitive search (-i)"
                            },
                            "invert_match": {
                                "type": "boolean", 
                                "description": "Select non-matching lines (-v)"
                            },
                            "word_regexp": {
                                "type": "boolean",
                                "description": "Match whole words only (-w)"
                            },
                            "line_regexp": {
                                "type": "boolean",
                                "description": "Match whole lines only (-x)"
                            },
                            "count": {
                                "type": "boolean",
                                "description": "Only output count of matches (-c)"
                            },
                            "files_with_matches": {
                                "type": "boolean",
                                "description": "Only output filenames with matches (-l)"
                            },
                            "line_number": {
                                "type": "boolean",
                                "description": "Show line numbers (-n)"
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Recursive directory search (-r)"
                            },
                            "perl_regexp": {
                                "type": "boolean",
                                "description": "Use Perl regex engine (-P)"
                            },
                            "extended_regexp": {
                                "type": "boolean",
                                "description": "Use extended regex (-E)"
                            },
                            "context_before": {
                                "type": "integer",
                                "description": "Lines of context before match (-B)"
                            },
                            "context_after": {
                                "type": "integer",
                                "description": "Lines of context after match (-A)"
                            }
                        },
                        "returns": {
                            "type": "object",
                            "properties": {
                                "matches": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "file": {"type": "string"},
                                            "line_number": {"type": "integer"},
                                            "line": {"type": "string"},
                                            "match": {"type": "string"}
                                        }
                                    }
                                },
                                "count": {"type": "integer"},
                                "files": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    }
                },
                "performance": self.descriptor.performance,
                "limits": {
                    "max_pattern_length": self.descriptor.max_pattern_length,
                    "max_file_size": self.descriptor.max_file_size
                }
            }
        }
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI specification for grep-as-a-service."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Grep Service API",
                "version": self.descriptor.version,
                "description": "RESTful API for grep functionality"
            },
            "paths": {
                "/search": {
                    "post": {
                        "summary": "Search for patterns",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/SearchRequest"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Search results",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/SearchResponse"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/capabilities": {
                    "get": {
                        "summary": "Get grep capabilities",
                        "responses": {
                            "200": {
                                "description": "Capability descriptor",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/Capabilities"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "SearchRequest": {
                        "type": "object",
                        "required": ["pattern"],
                        "properties": {
                            "pattern": {"type": "string"},
                            "files": {"type": "array", "items": {"type": "string"}},
                            "options": {
                                "type": "object",
                                "properties": {
                                    "case_insensitive": {"type": "boolean"},
                                    "invert_match": {"type": "boolean"},
                                    "line_numbers": {"type": "boolean"},
                                    "recursive": {"type": "boolean"}
                                }
                            }
                        }
                    },
                    "SearchResponse": {
                        "type": "object",
                        "properties": {
                            "matches": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/Match"
                                }
                            },
                            "total_count": {"type": "integer"},
                            "search_time_ms": {"type": "number"}
                        }
                    },
                    "Match": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string"},
                            "line_number": {"type": "integer"},
                            "line": {"type": "string"},
                            "highlights": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "start": {"type": "integer"},
                                        "end": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "Capabilities": {
                        "type": "object",
                        "properties": {
                            "version": {"type": "string"},
                            "features": {"type": "array", "items": {"type": "string"}},
                            "performance": {"type": "object"},
                            "limits": {"type": "object"}
                        }
                    }
                }
            }
        }
    
    def check_capability(self, binary_descriptor: bytes, capability: str) -> bool:
        """
        Ultra-fast capability checking using binary descriptor.
        
        This is where TCP shines - checking capabilities in microseconds
        instead of parsing help text.
        """
        # Skip magic and version, get flags
        flags = struct.unpack('>I', b'\x00' + binary_descriptor[6:9])[0]
        
        capability_map = {
            "case_insensitive": CommandFlag.CASE_INSENSITIVE,
            "regex": CommandFlag.REGEX,
            "perl_regex": CommandFlag.PERL_REGEX,
            "recursive": CommandFlag.RECURSIVE,
            "context": CommandFlag.CONTEXT,
            "count": CommandFlag.COUNT_ONLY,
            "invert": CommandFlag.INVERT_MATCH,
            "line_numbers": CommandFlag.LINE_NUMBERS,
            "word_match": CommandFlag.WORD_MATCH,
            "files_only": CommandFlag.FILES_WITH_MATCH
        }
        
        if capability in capability_map:
            return bool(flags & capability_map[capability])
        return False


def compare_efficiency():
    """Compare TCP efficiency vs traditional help text parsing."""
    tcp = GrepTCP()
    
    print("=== Grep Tool Capability Protocol Demo ===\n")
    
    # Generate binary descriptor
    print("1. Binary Descriptor (20 bytes):")
    binary = tcp.generate_binary_descriptor()
    print(f"   Raw: {binary.hex()}")
    print(f"   Base64: {base64.b64encode(binary).decode()}")
    print(f"   Size: {len(binary)} bytes\n")
    
    # Test capability checking speed
    print("2. Capability Checking Performance:")
    
    # Binary descriptor checking
    start = time.perf_counter()
    for _ in range(10000):
        tcp.check_capability(binary, "perl_regex")
    binary_time = (time.perf_counter() - start) * 1000
    print(f"   Binary descriptor: {binary_time/10000:.3f}ms per check")
    
    # Simulate help text parsing
    help_text = """grep [OPTION]... PATTERN [FILE]...
    -E, --extended-regexp     PATTERN is an extended regular expression
    -P, --perl-regexp         PATTERN is a Perl regular expression
    -i, --ignore-case         ignore case distinctions
    -v, --invert-match        select non-matching lines
    -w, --word-regexp         force PATTERN to match only whole words
    -x, --line-regexp         force PATTERN to match only whole lines
    -c, --count               print only a count of matching lines per FILE
    """
    
    start = time.perf_counter()
    for _ in range(10000):
        "perl-regexp" in help_text or "-P" in help_text
    text_time = (time.perf_counter() - start) * 1000
    print(f"   Help text parsing: {text_time/10000:.3f}ms per check")
    print(f"   Speedup: {text_time/binary_time:.1f}x faster\n")
    
    # Show JSON schema
    print("3. JSON Schema (for structured queries):")
    json_schema = tcp.generate_json_schema()
    print(json.dumps(json_schema, indent=2)[:500] + "...\n")
    
    # Show size comparison
    print("4. Size Comparison:")
    print(f"   Help text: ~{len(help_text)} bytes")
    print(f"   TCP Binary: {len(binary)} bytes ({len(help_text)/len(binary):.1f}x smaller)")
    print(f"   TCP JSON: ~{len(json.dumps(json_schema))} bytes")
    
    # Example LLM usage
    print("\n5. Example LLM Usage:")
    print("   # Instead of parsing help text:")
    print("   # llm.parse('grep --help | grep perl')")
    print("   ")
    print("   # Use TCP binary descriptor:")
    print("   if tcp.check_capability(descriptor, 'perl_regex'):")
    print("       run_grep_with_perl_regex(pattern)")
    
    # Show OpenAPI snippet
    print("\n6. OpenAPI Specification (snippet):")
    openapi = tcp.generate_openapi_spec()
    print(json.dumps(openapi["paths"], indent=2)[:400] + "...")


def demonstrate_llm_integration():
    """Show how an LLM would use TCP to work with grep."""
    tcp = GrepTCP()
    binary = tcp.generate_binary_descriptor()
    
    print("\n\n=== LLM Integration Example ===\n")
    
    class LLMToolSelector:
        """Simulated LLM tool selection using TCP."""
        
        def __init__(self):
            self.tools = {
                "grep": binary,
                # Other tools would have their own descriptors
            }
        
        def find_tools_for_task(self, task: str) -> list:
            """Find tools that can handle a specific task."""
            results = []
            
            if "search" in task.lower() or "find" in task.lower():
                if "perl" in task and tcp.check_capability(self.tools["grep"], "perl_regex"):
                    results.append(("grep", "perl_regex", 0.95))
                elif "case" in task and tcp.check_capability(self.tools["grep"], "case_insensitive"):
                    results.append(("grep", "case_insensitive", 0.90))
                elif tcp.check_capability(self.tools["grep"], "regex"):
                    results.append(("grep", "regex", 0.85))
            
            return results
        
        def generate_command(self, tool: str, task: str, options: dict) -> str:
            """Generate the actual command based on capabilities."""
            if tool == "grep":
                cmd = ["grep"]
                
                if options.get("perl_regex"):
                    cmd.append("-P")
                if options.get("case_insensitive"):
                    cmd.append("-i")
                if options.get("recursive"):
                    cmd.append("-r")
                if options.get("line_numbers"):
                    cmd.append("-n")
                
                cmd.append(options.get("pattern", ""))
                if options.get("files"):
                    cmd.extend(options["files"])
                
                return " ".join(cmd)
            return ""
    
    # Demonstrate LLM usage
    llm = LLMToolSelector()
    
    # Task 1: Find Perl regex capable tool
    print("Task: 'Find all email addresses using perl regex patterns'")
    tools = llm.find_tools_for_task("Find all email addresses using perl regex patterns")
    for tool, capability, confidence in tools:
        print(f"  Found: {tool} with {capability} (confidence: {confidence})")
        cmd = llm.generate_command(tool, "email search", {
            "perl_regex": True,
            "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "files": ["*.txt"]
        })
        print(f"  Command: {cmd}")
    
    # Task 2: Case insensitive search
    print("\nTask: 'Search for ERROR ignoring case'")
    tools = llm.find_tools_for_task("Search for ERROR ignoring case in logs")
    for tool, capability, confidence in tools:
        print(f"  Found: {tool} with {capability} (confidence: {confidence})")
        cmd = llm.generate_command(tool, "error search", {
            "case_insensitive": True,
            "pattern": "ERROR",
            "files": ["/var/log/*.log"],
            "recursive": True
        })
        print(f"  Command: {cmd}")
    
    # Show performance metrics
    print("\n7. Performance Metrics from Binary Descriptor:")
    perf_data = binary[10:18]  # Performance section
    speed, memory = struct.unpack('>HH', perf_data[:4])
    print(f"   Processing speed: {speed} MB/s")
    print(f"   Memory overhead: {memory} MB")
    print(f"   Supports streaming: {'Yes' if perf_data[4] else 'No'}")
    print(f"   Supports parallel: {'Yes' if perf_data[5] else 'No'}")


if __name__ == "__main__":
    compare_efficiency()
    demonstrate_llm_integration()