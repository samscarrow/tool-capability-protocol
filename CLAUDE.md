# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Tool Capability Protocol (TCP) is a revolutionary security-aware binary protocol for AI agent safety. It encodes complete command-line tool intelligence into ultra-compact 24-byte binary descriptors, achieving **362:1 compression vs traditional documentation** while maintaining full security context. The project has **proven results** with 100% accuracy validation and analysis of 709 system commands achieving 13,669:1 compression.

## Development Environment Setup & Commands

### Prerequisites
- **Python**: 3.8+ (project supports 3.8-3.12)
- **Poetry**: Required for dependency management
- **Docker**: For containerized analysis and demonstrations

### Install Dependencies
```bash
# Using Poetry (required)
poetry install

# Install with all development dependencies
poetry install --with dev,test,docs

# Activate virtual environment
poetry shell
```

### Docker-Based Development (Recommended)
```bash
# Complete setup and run
make setup          # Build and start containers

# Development workflow
make shell          # Access interactive TCP shell
make demo           # Run security demonstrations
make health         # Check system health

# Quick command analysis
make analyze-rm     # Analyze 'rm' command security
make analyze-sudo   # Analyze 'sudo' command security

# Container management
make logs           # View container logs
make restart        # Restart containers
make clean          # Clean up containers and volumes
```

### Testing Commands
```bash
# Run all tests
poetry run pytest

# Run tests with coverage (90% minimum required)
poetry run pytest --cov=tcp --cov-report=term-missing

# Run by test markers
poetry run pytest -m unit          # Unit tests only
poetry run pytest -m integration   # Integration tests
poetry run pytest -m network       # Network tests
poetry run pytest -m slow          # Performance tests

# Run specific test file/function
poetry run pytest tests/test_protocol.py
poetry run pytest tests/test_protocol.py::test_create_descriptor -v

# Integration tests via Docker
make test-local     # Test local Ollama integration
make test-security  # Test security system
```

### Code Quality Commands
```bash
# Format code (Black with 88-character line length)
poetry run black tcp tests

# Sort imports (isort with Black profile)
poetry run isort tcp tests

# Lint code (flake8)
poetry run flake8 tcp tests

# Type checking (mypy strict mode)
poetry run mypy tcp

# Run all quality checks
poetry run black tcp tests && poetry run isort tcp tests && poetry run flake8 tcp tests && poetry run mypy tcp
```

### CLI Tools
```bash
# Available TCP command-line tools
poetry run tcp --help           # Main CLI entry point
poetry run tcp-wrap --help      # Wrap existing tools
poetry run tcp-query --help     # Query tool capabilities
poetry run tcp-discover --help  # Discover available tools
poetry run tcp-generate --help  # Generate format outputs
```

### Documentation
```bash
# Local documentation server
poetry run mkdocs serve  # http://localhost:8000
poetry run mkdocs build  # Build static site
```

## High-Level Architecture

### Core TCP Protocol Components

#### 1. **Protocol Engine** (`tcp/core/`)
- **`descriptors.py`**: Data models for 24-byte binary descriptors and capability structures
- **`protocol.py`**: Main TCP protocol orchestration and binary encoding/decoding
- **`registry.py`**: Central registry for storing and querying tool capabilities with microsecond lookup
- **`discovery.py`**: Service discovery mechanisms for finding tools by security/capability patterns

#### 2. **Binary Protocol Format** (24 bytes total)
```
TCP Descriptor v2:
├── Magic + Version (6 bytes)     # TCP\x02 + version info
├── Command Hash (4 bytes)        # Unique command identifier  
├── Security Flags (4 bytes)      # 16 security flags + 5-level risk classification
├── Performance Data (6 bytes)    # Execution time + memory + output size
├── Reserved Fields (2 bytes)     # Command length + future expansion
└── CRC16 Checksum (2 bytes)      # Integrity verification
```

#### 3. **Hierarchical Compression** (Second-order encoding)
- **Git Family**: 164 commands compressed 3.4:1 (3936B → 1164B)
- **Multi-tool commands**: Parent descriptor + delta encoding for subcommands
- **Proven scalability**: 709 commands achieving 13,669:1 vs documentation

#### 4. **Security Intelligence**
- **5-Level Risk Classification**: SAFE → LOW_RISK → MEDIUM_RISK → HIGH_RISK → CRITICAL
- **16 Security Flags**: FILE_MODIFICATION, DESTRUCTIVE, NETWORK_ACCESS, REQUIRES_SUDO, etc.
- **Instant Agent Decisions**: Microsecond security evaluation vs minutes for documentation parsing

### Plugin Architecture

#### **Format Generators** (`tcp/generators/`)
- **Plugin System**: Dynamically loaded via Poetry plugins in `pyproject.toml`
- **Binary Generator**: Ultra-compact 24-byte descriptors
- **Standards Support**: JSON Schema, OpenAPI, GraphQL, Protocol Buffers
- **Extensible**: New formats can be added without modifying core

#### **Integration Adapters** (`tcp/adapters/`)
- **CLI Adapter**: Wraps command-line tools to extract capabilities
- **Service Adapters**: REST, gRPC, MCP (Model Context Protocol)
- **Standard Interface**: Consistent adapter pattern for all integrations

### Analysis Pipeline (`tcp/analysis/`)
- **Help Parser**: Extracts capabilities from command help text
- **LLM Extractor**: Uses language models for intelligent capability extraction
- **TCP Generator**: Converts extracted data to binary descriptors
- **Validation**: 100% accuracy proven against expert LLM analysis

### Security Framework (`tcp/security/`)
- **Secure Agent**: AI agent safety wrapper with TCP-guided decisions
- **Sandbox Manager**: Isolated execution environments for dangerous commands
- **Human Approval**: Workflow for high-risk operations
- **Audit Logging**: Complete decision audit trail

## Key Data Models

### Primary Descriptors
- **`CapabilityDescriptor`**: Complete tool capability specification
- **`BinaryCapabilityDescriptor`**: Compact 24-byte binary representation
- **`CommandDescriptor`**: Individual command specifications with security context
- **`ParameterDescriptor`**: Command parameter details with validation rules

### Security Models
- **`SecurityLevel`**: 5-level risk enumeration (SAFE through CRITICAL)
- **`SecurityFlags`**: 16-bit capability flags (destructive, network, sudo, etc.)
- **`PerformanceMetrics`**: Execution time, memory usage, output size predictions

## Research Validation & Results

### Proven Metrics
- **Compression Ratio**: 362:1 vs traditional documentation (13,669:1 on full system)
- **Decision Speed**: <1ms vs 50-500ms for text parsing
- **Accuracy**: 100% agreement with expert LLM analysis (bcachefs case study)
- **Scalability**: Successfully analyzed 709 system commands

### Research Artifacts
- **Interactive Visualizations**: `docs/media/tcp-infographic.html`
- **Case Studies**: `docs/CASE_STUDY_INFOGRAPHIC_FORMATTING.md`
- **Performance Benchmarks**: Validated against real-world command analysis
- **Academic Documentation**: Complete research findings in `RESEARCH_FINDINGS.md`

## Testing Strategy

### Test Organization
- **Unit Tests**: Individual component isolation testing
- **Integration Tests**: Component interaction validation
- **Network Tests**: External service integration (marked `@pytest.mark.network`)
- **Performance Tests**: Compression and speed validation (marked `@pytest.mark.slow`)

### Coverage Requirements
- **Minimum Coverage**: 90% required for all new code
- **Critical Components**: 100% coverage for security and protocol components
- **Regression Testing**: Full test suite runs on all changes

## Code Style & Standards

### Formatting Standards
- **Black**: 88-character line length, Python 3.8+ target
- **isort**: Black profile for import sorting
- **Type Hints**: Required for all functions, enforced by mypy strict mode
- **Docstrings**: Google-style for all public classes and methods

### Development Practices
- **Plugin Registration**: New generators/adapters must be registered in `pyproject.toml`
- **Error Handling**: Use specific exceptions from `tcp.exceptions`
- **Security First**: All command analysis must include security context
- **Binary Compatibility**: Protocol changes require version increment and migration logic

## Advanced Development Tasks

### Adding New Format Generators
1. Create generator class in `tcp/generators/`
2. Implement base generator interface
3. Register in `pyproject.toml` under `[tool.poetry.plugins."tcp.generators"]`
4. Add comprehensive tests in `tests/generators/`

### Extending Security Analysis
1. Update security flags in `descriptors.py`
2. Enhance analysis pipeline in `tcp/analysis/`
3. Validate against known command behaviors
4. Update binary protocol if needed (increment version)

### Performance Optimization
1. Profile with `cProfile` for bottlenecks
2. Optimize binary encoding/decoding in `protocol.py`
3. Validate compression ratios maintain standards
4. Test with large command sets (500+ commands)

## Research Integration

### Consortium Workspace
- **Research Directory**: `consortium/` contains researcher workspaces
- **Behavioral Analysis**: Elena Vasquez's statistical frameworks
- **Network Architecture**: Marcus Chen's distributed systems
- **Performance Optimization**: Yuki Tanaka's real-time systems
- **Security Validation**: Aria Blackwood's adversarial testing

### MCP Server Integration
- **FastMCP Server**: `mcp-server/` provides Claude integration
- **TCP Intelligence**: Exposes command safety analysis to AI agents
- **Real-time Analysis**: Streaming command evaluation for agent decisions

## Docker Development Environment

### Container Architecture
- **Main Container**: `tcp-security` with complete analysis environment
- **Ollama Integration**: Local LLM for capability extraction
- **Persistent Volumes**: Data, cache, logs, and models
- **Health Monitoring**: Automated service health checks

### Development Workflow
1. **Setup**: `make setup` for complete container initialization
2. **Development**: `make shell` for interactive TCP environment
3. **Testing**: `make demo` for security demonstrations
4. **Analysis**: `make analyze-rm` for quick command analysis
5. **Monitoring**: `make health` for system status

## Development Best Practices

### Command Navigation
- Never use `cd ../..` as it breaks relative path assumptions
- Use absolute paths for cross-directory operations
- Maintain working directory context in scripts

### Virtual Environment Management
- Always activate TCP virtual environment: `poetry shell`
- Install dependencies in virtual environment only
- Use `poetry install --with dev,test,docs` for complete development setup

### Research Data Handling
- Simulation results stored in `tcp_stealth_simulation_results_*.json`
- Analysis artifacts in researcher workspaces
- Validation data maintained with version control