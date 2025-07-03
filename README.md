# Tool Capability Protocol (TCP)

A universal protocol for machine-readable tool capability description and discovery, designed to enable efficient LLM-to-tool communication without parsing help text or documentation.

## 🎯 Problem Statement

Current LLM systems waste significant tokens and processing time parsing unstructured help text to understand tool capabilities. This project provides standardized, machine-readable formats that are orders of magnitude more efficient than natural language parsing.

## 🚀 Key Features

- **Multiple Format Support**: JSON, Binary, Protocol Buffers, GraphQL, OpenAPI
- **Ultra-Compact Binary Protocol**: 20-byte capability descriptors
- **Type-Safe Schema Generation**: Auto-generate clients in any language
- **Extensible Architecture**: Plugin system for custom capability types
- **Performance Optimized**: <1ms capability queries vs 50ms+ help text parsing

## 📊 Efficiency Comparison

| Method | Size | Parse Time | Type Safety | Completeness |
|--------|------|------------|-------------|--------------|
| **Help Text** | ~5KB | ~50ms | ❌ | ⭐⭐⭐ |
| **TCP Binary** | 20 bytes | ~0.1ms | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **TCP JSON** | ~2KB | ~3ms | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **TCP Protobuf** | ~1KB | ~1ms | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🏗️ Architecture

```
Tool Capability Protocol (TCP)
├── Core Protocol Engine
│   ├── Binary Descriptors (20-byte capability fingerprints)
│   ├── Schema Registry (versioned capability schemas)
│   └── Discovery Service (capability announcement/query)
├── Format Generators
│   ├── JSON Schema Generator
│   ├── OpenAPI/Swagger Generator
│   ├── GraphQL Schema Generator
│   ├── Protocol Buffer Generator
│   └── Binary Protocol Generator
├── Client Libraries
│   ├── Python SDK
│   ├── TypeScript SDK
│   ├── Go SDK
│   └── Rust SDK
└── Integration Adapters
    ├── CLI Tool Wrapper
    ├── REST API Adapter
    ├── gRPC Service Adapter
    └── MCP Server Adapter
```

## 🔧 Quick Start

### Installation

```bash
pip install tool-capability-protocol
```

### Basic Usage

```python
from tcp import ToolCapabilityProtocol, CapabilityDescriptor

# Create capability descriptor for your tool
tcp = ToolCapabilityProtocol()
descriptor = tcp.create_descriptor(
    name="my-tool",
    version="1.0.0",
    commands=["extract", "process", "analyze"],
    input_formats=["pdf", "docx", "txt"],
    output_formats=["json", "xml"]
)

# Generate machine-readable formats
json_schema = tcp.generate_json_schema(descriptor)
binary_caps = tcp.generate_binary(descriptor)  # 20 bytes
protobuf_schema = tcp.generate_protobuf(descriptor)

# Query capabilities efficiently
if tcp.supports_format(binary_caps, "pdf"):
    # Process PDF input
    pass
```

### CLI Integration

```bash
# Wrap existing CLI tools
tcp-wrap my-existing-tool --analyze-help --generate-all

# Generate capabilities for your tool
my-tool --tcp-capabilities-binary | tcp-decode

# Query tool capabilities
tcp-query my-tool supports pdf
tcp-query my-tool commands extract --parameters
```

## 📋 Supported Capability Types

### Input/Output Capabilities
- **Formats**: File types, data formats, encodings
- **Protocols**: HTTP, gRPC, WebSocket, stdin/stdout
- **Authentication**: API keys, OAuth, certificates

### Processing Capabilities
- **Modes**: Sync/async, batch, streaming
- **Performance**: Speed, memory usage, GPU requirements
- **Concurrency**: Max parallel operations, rate limits

### Command Specifications
- **Parameters**: Required/optional, types, constraints
- **Outputs**: Return types, error codes, metadata
- **Examples**: Sample inputs/outputs, usage patterns

## 🎨 Format Examples

### Binary Protocol (20 bytes)
```
Magic(4) + Version(2) + Flags(3) + Commands(1) + Performance(8) + CRC(2)
```

### JSON Schema
```json
{
  "tool": "docextract",
  "version": "1.0.0",
  "capabilities": {
    "input_formats": ["pdf", "docx", "eml", "base64"],
    "commands": {
      "extract": {
        "parameters": {"format": "enum", "output": "string"},
        "returns": "ExtractionResult"
      }
    }
  }
}
```

### Protocol Buffers
```protobuf
service ToolService {
  rpc GetCapabilities(Empty) returns (Capabilities);
  rpc Execute(CommandRequest) returns (CommandResponse);
}
```

## 🔌 Integration Patterns

### LLM Function Calling
```python
# Instead of parsing help text
tools = tcp.discover_tools()
pdf_tools = tcp.filter_by_capability(tools, supports="pdf")
best_tool = tcp.select_optimal(pdf_tools, criteria="speed")
```

### API Gateway Integration
```yaml
# Auto-generate API routes from TCP descriptors
routes:
  - path: /tools/{tool}/extract
    tcp_command: extract
    auto_validate: true
```

### Container Orchestration
```dockerfile
# Include TCP descriptor in container labels
LABEL tcp.capabilities="base64:CAPABILITY_DESCRIPTOR"
LABEL tcp.version="1.0"
```

## 🛠️ Development

### Project Structure
```
tool-capability-protocol/
├── tcp/                    # Core protocol implementation
│   ├── core/              # Binary protocol, schema registry
│   ├── generators/        # Format generators
│   ├── adapters/          # Integration adapters
│   └── utils/             # Utilities and helpers
├── schemas/               # Schema definitions
├── examples/              # Example implementations
├── tests/                 # Test suite
├── docs/                  # Documentation
└── tools/                 # Development tools
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📚 Use Cases

### For Tool Developers
- **Standardized Capability Advertising**: Consistent way to describe tool features
- **Auto-Generated Documentation**: API docs, CLI help, integration guides
- **Type-Safe Client Generation**: SDKs for multiple languages
- **Performance Optimization**: Efficient capability queries

### For LLM Systems
- **Efficient Tool Discovery**: Query capabilities without parsing documentation
- **Smart Tool Selection**: Choose optimal tools based on requirements
- **Reduced Token Usage**: Compact capability descriptions
- **Type-Safe Execution**: Validated parameters and return types

### For Integration Platforms
- **API Gateway**: Auto-route requests based on capabilities
- **Container Orchestration**: Service discovery via capability matching
- **Workflow Engines**: Dynamic tool chaining based on capabilities
- **Monitoring Systems**: Track tool usage and performance

## 🔄 Version History

- **v1.0.0**: Initial release with binary protocol and JSON schema
- **v0.9.0**: Beta release with protocol buffer support
- **v0.8.0**: Alpha release with basic capability descriptors

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📞 Support

- **Documentation**: [https://tcp.dev/docs](https://tcp.dev/docs)
- **Issues**: [GitHub Issues](https://github.com/tcp/tool-capability-protocol/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tcp/tool-capability-protocol/discussions)
- **Discord**: [TCP Community](https://discord.gg/tcp-community)