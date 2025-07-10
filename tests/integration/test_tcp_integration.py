"""Integration tests for TCP end-to-end functionality."""

import pytest

from tcp.core.protocol import ToolCapabilityProtocol
from tcp.core.registry import CapabilityRegistry


class TestTCPIntegration:
    """Integration tests for TCP protocol."""

    def test_protocol_registry_integration(self):
        """Test protocol and registry integration."""
        registry = CapabilityRegistry()
        protocol = ToolCapabilityProtocol(registry=registry)

        # Create a descriptor
        descriptor = protocol.create_descriptor(
            name="test-tool", version="1.0.0", description="Test tool for integration"
        )

        # Register it
        protocol.register_tool(descriptor)

        # Retrieve it
        retrieved = protocol.get_tool("test-tool", "1.0.0")
        assert retrieved is not None
        assert retrieved.name == "test-tool"
        assert retrieved.version == "1.0.0"

    @pytest.mark.integration
    def test_tool_discovery(self):
        """Test tool discovery functionality."""
        registry = CapabilityRegistry()
        protocol = ToolCapabilityProtocol(registry=registry)

        # Register multiple tools
        for i in range(3):
            descriptor = protocol.create_descriptor(
                name=f"tool-{i}", version="1.0.0", description=f"Test tool {i}"
            )
            protocol.register_tool(descriptor)

        # Discover all tools
        tools = protocol.list_tools()
        assert len(tools) == 3

        # Verify all tools are present
        tool_names = {tool.name for tool in tools}
        assert tool_names == {"tool-0", "tool-1", "tool-2"}
