# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Tool Capability Protocol (TCP) is a universal protocol for machine-readable tool capability description and discovery. It enables efficient LLM-to-tool communication without parsing help text or documentation, providing standardized formats that are orders of magnitude more efficient than natural language parsing.

## Development Environment Setup & Commands

### Install Dependencies
```bash
# Using Poetry (required)
poetry install

# Install with development dependencies
poetry install --with dev,test,docs
```

### Run Tests
```bash
# Run all tests
poetry run pytest

# Run unit tests only
poetry run pytest -m unit

# Run integration tests
poetry run pytest -m integration

# Run tests with coverage
poetry run pytest --cov=tcp --cov-report=term-missing

# Run a specific test file
poetry run pytest tests/test_protocol.py

# Run a specific test function
poetry run pytest tests/test_protocol.py::test_create_descriptor -v
```

### Code Quality Commands
```bash
# Format code with Black
poetry run black tcp tests

# Sort imports
poetry run isort tcp tests

# Lint with flake8
poetry run flake8 tcp tests

# Type check with mypy
poetry run mypy tcp

# Run all quality checks
poetry run black tcp tests && poetry run isort tcp tests && poetry run flake8 tcp tests && poetry run mypy tcp
```

### Development Workflow
```bash
# Start Python REPL with project context
poetry shell
python

# Run CLI tools
poetry run tcp --help
poetry run tcp-wrap --help
poetry run tcp-query --help
poetry run tcp-discover --help
poetry run tcp-generate --help

# Build documentation
poetry run mkdocs serve  # Local preview at http://localhost:8000
poetry run mkdocs build  # Build static site
```

## Architecture Overview

### Core Components

1. **Protocol Engine** (`tcp/core/`)
   - `protocol.py`: Main TCP protocol implementation, orchestrates all operations
   - `descriptors.py`: Data models for capability descriptors (CapabilityDescriptor, BinaryCapabilityDescriptor, etc.)
   - `registry.py`: Central registry for storing and querying tool capabilities
   - `discovery.py`: Service discovery mechanisms for finding tools by capabilities

2. **Format Generators** (`tcp/generators/`)
   - `json.py`: Generates JSON Schema representations
   - `openapi.py`: Creates OpenAPI/Swagger specifications
   - `protobuf.py`: Generates Protocol Buffer definitions
   - `graphql.py`: Creates GraphQL schemas
   - `binary.py`: Generates ultra-compact 20-byte binary descriptors

3. **Integration Adapters** (`tcp/adapters/`)
   - `cli.py`: Wraps CLI tools to extract capabilities
   - `rest.py`: REST API adapter for HTTP services
   - `grpc.py`: gRPC service adapter
   - `mcp.py`: Model Context Protocol server adapter

4. **Command-Line Tools** (`tcp/tools/`)
   - `wrapper.py`: Wraps existing tools with TCP capabilities
   - `query.py`: Query tool capabilities
   - `discovery.py`: Discover available tools
   - `cli.py`: Main CLI entry point

### Key Design Patterns

1. **Plugin Architecture**: Generators and adapters are dynamically loaded via Poetry plugin system
   - Defined in `pyproject.toml` under `[tool.poetry.plugins]`
   - New formats/adapters can be added without modifying core

2. **Binary Protocol Format** (20 bytes):
   ```
   Magic(4) + Version(2) + Flags(3) + Commands(1) + Performance(8) + CRC(2)
   ```

3. **Capability Matching**: Efficient binary operations for checking tool support
   - Uses bitwise operations for fast capability queries
   - <1ms query time vs 50ms+ for text parsing

## Key Data Models

- **CapabilityDescriptor**: Main descriptor containing all tool capabilities
- **BinaryCapabilityDescriptor**: Compact 20-byte representation
- **CommandDescriptor**: Individual command specifications
- **ParameterDescriptor**: Command parameter details
- **FormatDescriptor**: Input/output format specifications
- **PerformanceMetrics**: Speed, memory, concurrency information

## Testing Strategy

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Network Tests**: Test external service integrations (marked with `@pytest.mark.network`)
- **Slow Tests**: Performance and stress tests (marked with `@pytest.mark.slow`)

## Code Style Guidelines

- **Formatting**: Black with 88-character line length
- **Import Sorting**: isort with Black profile
- **Type Hints**: Required for all functions (enforced by mypy strict mode)
- **Docstrings**: Google-style for classes and public methods
- **Error Handling**: Use specific exceptions from `tcp.exceptions`

## Common Development Tasks

### Adding a New Format Generator
1. Create new file in `tcp/generators/`
2. Implement generator class inheriting from base
3. Register in `pyproject.toml` under `[tool.poetry.plugins."tcp.generators"]`
4. Add tests in `tests/generators/`

### Adding a New Adapter
1. Create new file in `tcp/adapters/`
2. Implement adapter class with standard interface
3. Register in `pyproject.toml` under `[tool.poetry.plugins."tcp.adapters"]`
4. Add integration tests

### Modifying Binary Protocol
1. Update `BinaryCapabilityDescriptor` in `descriptors.py`
2. Update encoding/decoding logic in `protocol.py`
3. Increment protocol version
4. Add migration logic for backward compatibility