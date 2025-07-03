# TCP-MCP Response Schemas

JSON Schema definitions for consistent TCP intelligence responses through Model Context Protocol.

## 📋 Schema Files

### Tool Response Schemas
- **`tcp_analysis.json`** - Command security analysis with risk classification and agent decisions
- **`safe_alternative.json`** - TCP-guided safe command alternatives with validation
- **`hierarchical_family.json`** - Tool family analysis with compression metrics

### Resource Response Schemas  
- **`tcp_descriptor.json`** - 24-byte binary TCP descriptors with metadata
- **`system_analysis.json`** - Complete system PATH intelligence analysis
- **`family_encoding.json`** - Hierarchical family encoding with parent/delta structure

## 🔧 Usage

These schemas define the structure of responses from TCP-MCP server tools and resources, ensuring consistent data formats for Claude's consumption.

### Tool Responses
```python
# analyze_command_safety tool returns data matching tcp_analysis.json
# get_safe_alternative tool returns data matching safe_alternative.json  
# check_hierarchical_family tool returns data matching hierarchical_family.json
```

### Resource Responses
```python
# tcp://command/{name} returns data matching tcp_descriptor.json
# tcp://system/path returns data matching system_analysis.json
# tcp://family/{name} returns data matching family_encoding.json
```

## 📊 Schema Validation

Schemas follow JSON Schema Draft 07 specification and include:
- **Required fields** for essential TCP intelligence
- **Type validation** for data integrity
- **Enum constraints** for standardized values
- **Pattern matching** for hex descriptors and flags
- **Error handling** for failed operations

## 🎯 Benefits

- **Consistent Responses**: Standardized data structures across all TCP operations
- **Type Safety**: Schema validation ensures correct data types
- **Documentation**: Self-documenting API through schema descriptions
- **Client Validation**: Enable client-side response validation
- **Evolution Support**: Schema versioning for future TCP protocol updates

---

**Protocol**: Model Context Protocol (MCP) v1.0  
**TCP Version**: Tool Capability Protocol v2.0 with Hierarchical v3.0 Encoding