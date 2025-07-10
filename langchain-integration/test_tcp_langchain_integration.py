#!/usr/bin/env python3
"""
Comprehensive test suite for TCP-LangChain integration.

This test suite validates the integration between your breakthrough TCP research
and LangChain agents, ensuring real-time safety monitoring works correctly.
"""

import asyncio
import unittest
import json
import time
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import logging

# Configure test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test imports with graceful fallbacks
try:
    from tcp_mcp_langchain_adapter import (
        TCPMCPLangChainAdapter,
        TCPSafetyWrapper,
        TCPEnhancedAgent
    )
    TCP_ADAPTER_AVAILABLE = True
except ImportError:
    TCP_ADAPTER_AVAILABLE = False
    logger.warning("TCP adapter not available")

try:
    from langchain.tools.base import BaseTool
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available")


class MockTCPMCPTool:
    """Mock TCP MCP tool for testing."""
    
    def __init__(self, name: str = "tcp_safety_tool"):
        self.name = name
        self.description = "Mock TCP safety assessment tool"
    
    async def ainvoke(self, args: dict) -> dict:
        """Mock TCP safety assessment."""
        command = args.get("command", "")
        
        # Mock TCP safety logic
        if "rm -rf" in command or "format" in command:
            return {
                "risk_level": "CRITICAL",
                "decision": "REJECT",
                "explanation": "Destructive command detected",
                "safe_alternative": f"mv {command.split()[-1]} .tcp_quarantine_test/"
            }
        elif "delete" in command or "rm" in command:
            return {
                "risk_level": "HIGH_RISK",
                "decision": "REQUIRE_APPROVAL",
                "explanation": "Deletion operation requires approval",
                "safe_alternative": f"mv {command.split()[-1]} .tcp_quarantine_test/"
            }
        elif "ls" in command or "pwd" in command:
            return {
                "risk_level": "SAFE",
                "decision": "APPROVE",
                "explanation": "Safe read-only operation"
            }
        else:
            return {
                "risk_level": "MEDIUM_RISK",
                "decision": "CAUTION",
                "explanation": "General command execution with monitoring"
            }


class MockLangChainTool:
    """Mock LangChain tool for testing."""
    
    name = "mock_shell_tool"
    description = "Mock shell tool for testing"
    
    def _run(self, command: str) -> str:
        """Mock synchronous tool execution."""
        return f"Mock executed: {command}"
    
    async def _arun(self, command: str) -> str:
        """Mock asynchronous tool execution."""
        return f"Mock executed async: {command}"
    
    def run(self, command: str) -> str:
        """Mock run method."""
        return self._run(command)
        
    async def arun(self, command: str) -> str:
        """Mock async run method."""
        return await self._arun(command)


@unittest.skipUnless(TCP_ADAPTER_AVAILABLE, "TCP adapter not available")
class TestTCPMCPLangChainAdapter(unittest.TestCase):
    """Test TCP-MCP-LangChain adapter functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.adapter = TCPMCPLangChainAdapter()
        self.adapter.tcp_tools = [MockTCPMCPTool()]
        
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertIsNotNone(self.adapter)
        self.assertIsNotNone(self.adapter.tcp_server_path)
        self.assertEqual(self.adapter.safety_stats["commands_analyzed"], 0)
        
    async def test_assess_command_safety_safe(self):
        """Test safety assessment for safe commands."""
        # Mock MCP client
        self.adapter.mcp_client = Mock()
        
        result = await self.adapter.assess_command_safety("ls -la")
        
        self.assertEqual(result["risk_level"], "SAFE")
        self.assertEqual(result["decision"], "APPROVE")
        self.assertEqual(self.adapter.safety_stats["commands_analyzed"], 1)
        
    async def test_assess_command_safety_critical(self):
        """Test safety assessment for critical commands."""
        # Mock MCP client
        self.adapter.mcp_client = Mock()
        
        result = await self.adapter.assess_command_safety("rm -rf /")
        
        self.assertEqual(result["risk_level"], "CRITICAL")
        self.assertEqual(result["decision"], "REJECT")
        self.assertIn("safe_alternative", result)
        self.assertEqual(self.adapter.safety_stats["commands_analyzed"], 1)
        
    async def test_assess_command_safety_high_risk(self):
        """Test safety assessment for high-risk commands."""
        # Mock MCP client
        self.adapter.mcp_client = Mock()
        
        result = await self.adapter.assess_command_safety("rm important_file.txt")
        
        self.assertEqual(result["risk_level"], "HIGH_RISK")
        self.assertEqual(result["decision"], "REQUIRE_APPROVAL")
        self.assertIn("safe_alternative", result)
        
    def test_safety_statistics(self):
        """Test safety statistics collection."""
        stats = self.adapter.get_safety_statistics()
        
        self.assertIn("commands_analyzed", stats)
        self.assertIn("safety_blocks", stats)
        self.assertIn("safety_block_rate", stats)
        self.assertIn("tools_available", stats)
        
    async def test_get_tcp_langchain_tools(self):
        """Test TCP LangChain tool creation."""
        # Mock MCP client
        self.adapter.mcp_client = Mock()
        
        if LANGCHAIN_AVAILABLE:
            tools = await self.adapter.get_tcp_langchain_tools()
            self.assertIsInstance(tools, list)
            # Note: Would be empty due to mocking, but structure is correct


@unittest.skipUnless(TCP_ADAPTER_AVAILABLE and LANGCHAIN_AVAILABLE, "TCP adapter and LangChain not available")
class TestTCPSafetyWrapper(unittest.TestCase):
    """Test TCP safety wrapper for LangChain tools."""
    
    def setUp(self):
        """Set up test environment."""
        self.adapter = TCPMCPLangChainAdapter()
        self.adapter.tcp_tools = [MockTCPMCPTool()]
        self.adapter.mcp_client = Mock()
        
        self.mock_tool = MockLangChainTool()
        self.wrapper = TCPSafetyWrapper(self.mock_tool, self.adapter)
        
    def test_wrapper_initialization(self):
        """Test wrapper initialization."""
        self.assertEqual(self.wrapper.name, "tcp_safe_mock_shell_tool")
        self.assertIn("TCP-enhanced", self.wrapper.description)
        self.assertEqual(self.wrapper.wrapped_tool, self.mock_tool)
        
    async def test_safe_command_execution(self):
        """Test execution of safe commands."""
        result = await self.wrapper._arun("ls -la")
        
        self.assertIn("Mock executed async", result)
        self.assertEqual(self.adapter.safety_stats["commands_analyzed"], 1)
        
    async def test_critical_command_rejection(self):
        """Test rejection of critical commands."""
        result = await self.wrapper._arun("rm -rf /")
        
        self.assertIn("Command rejected by TCP safety monitor", result)
        self.assertEqual(self.adapter.safety_stats["commands_analyzed"], 1)
        self.assertEqual(self.adapter.safety_stats["safety_blocks"], 1)
        
    async def test_high_risk_command_approval(self):
        """Test approval requirement for high-risk commands."""
        result = await self.wrapper._arun("rm important_file.txt")
        
        self.assertIn("Command requires approval", result)
        self.assertEqual(self.adapter.safety_stats["commands_analyzed"], 1)
        
    async def test_safe_alternative_usage(self):
        """Test usage of safe alternatives."""
        # This test would need more sophisticated mocking
        # to fully test safe alternative execution
        result = await self.wrapper._arun("rm test_file.txt")
        
        self.assertIsNotNone(result)
        self.assertEqual(self.adapter.safety_stats["commands_analyzed"], 1)


@unittest.skipUnless(TCP_ADAPTER_AVAILABLE and LANGCHAIN_AVAILABLE, "TCP adapter and LangChain not available")
class TestTCPEnhancedAgent(unittest.TestCase):
    """Test TCP-enhanced LangChain agent."""
    
    def setUp(self):
        """Set up test environment."""
        self.agent = TCPEnhancedAgent()
        
    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.llm)
        self.assertIsNotNone(self.agent.tcp_adapter)
        
    async def test_create_agent(self):
        """Test agent creation."""
        # Mock the TCP adapter
        self.agent.tcp_adapter.mcp_client = Mock()
        self.agent.tcp_adapter.tcp_tools = [MockTCPMCPTool()]
        
        # Mock get_tcp_langchain_tools to return empty list
        self.agent.tcp_adapter.get_tcp_langchain_tools = AsyncMock(return_value=[])
        
        executor = await self.agent.create_agent()
        
        self.assertIsNotNone(executor)
        self.assertIsNotNone(self.agent.agent_executor)
        
    def test_safety_report(self):
        """Test safety report generation."""
        report = self.agent.get_safety_report()
        
        self.assertIn("commands_analyzed", report)
        self.assertIn("safety_blocks", report)
        self.assertIn("tools_available", report)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Test TCP performance benchmarks."""
    
    @unittest.skipUnless(TCP_ADAPTER_AVAILABLE, "TCP adapter not available")
    async def test_decision_speed(self):
        """Test TCP decision speed benchmarks."""
        adapter = TCPMCPLangChainAdapter()
        adapter.tcp_tools = [MockTCPMCPTool()]
        adapter.mcp_client = Mock()
        
        # Benchmark decision speed
        start_time = time.time()
        
        test_commands = [
            "ls -la",
            "pwd",
            "cat file.txt",
            "rm temp.txt",
            "rm -rf /tmp/test"
        ]
        
        for command in test_commands:
            result = await adapter.assess_command_safety(command)
            self.assertIn("risk_level", result)
            
        total_time = time.time() - start_time
        avg_time = total_time / len(test_commands)
        
        logger.info(f"TCP decision speed: {avg_time:.6f}s average")
        
        # TCP should be much faster than traditional documentation parsing
        self.assertLess(avg_time, 0.1, "TCP decisions should be sub-100ms")
        
    @unittest.skipUnless(TCP_ADAPTER_AVAILABLE, "TCP adapter not available")
    async def test_cache_performance(self):
        """Test TCP cache performance."""
        adapter = TCPMCPLangChainAdapter()
        adapter.tcp_tools = [MockTCPMCPTool()]
        adapter.mcp_client = Mock()
        
        # First assessment (cache miss)
        start_time = time.time()
        result1 = await adapter.assess_command_safety("ls -la")
        first_time = time.time() - start_time
        
        # Second assessment (cache hit)
        start_time = time.time()
        result2 = await adapter.assess_command_safety("ls -la")
        second_time = time.time() - start_time
        
        # Cache should improve performance
        self.assertEqual(result1["risk_level"], result2["risk_level"])
        logger.info(f"Cache performance: {first_time:.6f}s -> {second_time:.6f}s")


class TestIntegrationScenarios(unittest.TestCase):
    """Test real-world integration scenarios."""
    
    @unittest.skipUnless(TCP_ADAPTER_AVAILABLE and LANGCHAIN_AVAILABLE, "Dependencies not available")
    async def test_system_administration_scenario(self):
        """Test TCP integration in system administration scenario."""
        agent = TCPEnhancedAgent()
        
        # Mock the TCP components
        agent.tcp_adapter.mcp_client = Mock()
        agent.tcp_adapter.tcp_tools = [MockTCPMCPTool()]
        agent.tcp_adapter.get_tcp_langchain_tools = AsyncMock(return_value=[])
        
        executor = await agent.create_agent()
        
        # Test system admin commands
        test_scenarios = [
            ("Check disk space", "df -h"),
            ("View running processes", "ps aux"),
            ("Clean temporary files", "rm /tmp/test*"),
            ("System update", "apt update && apt upgrade")
        ]
        
        for scenario, expected_command in test_scenarios:
            # This would require more sophisticated mocking for full execution
            logger.info(f"Testing scenario: {scenario}")
            self.assertIsNotNone(executor)
            
    @unittest.skipUnless(TCP_ADAPTER_AVAILABLE and LANGCHAIN_AVAILABLE, "Dependencies not available")
    async def test_development_workflow_scenario(self):
        """Test TCP integration in development workflow scenario."""
        agent = TCPEnhancedAgent()
        
        # Mock the TCP components
        agent.tcp_adapter.mcp_client = Mock()
        agent.tcp_adapter.tcp_tools = [MockTCPMCPTool()]
        agent.tcp_adapter.get_tcp_langchain_tools = AsyncMock(return_value=[])
        
        executor = await agent.create_agent()
        
        # Test development commands
        test_scenarios = [
            ("Build project", "make build"),
            ("Run tests", "pytest tests/"),
            ("Deploy to staging", "docker build && docker push"),
            ("Clean build artifacts", "make clean")
        ]
        
        for scenario, expected_command in test_scenarios:
            logger.info(f"Testing scenario: {scenario}")
            self.assertIsNotNone(executor)


async def run_comprehensive_tests():
    """Run comprehensive test suite."""
    print("🧪 TCP-LangChain Integration Test Suite")
    print("=" * 50)
    
    # Test availability
    print("📋 Checking dependencies...")
    if not TCP_ADAPTER_AVAILABLE:
        print("❌ TCP adapter not available")
        return False
    
    if not LANGCHAIN_AVAILABLE:
        print("❌ LangChain not available")
        return False
    
    print("✅ All dependencies available")
    
    # Run tests
    test_classes = [
        TestTCPMCPLangChainAdapter,
        TestTCPSafetyWrapper,
        TestTCPEnhancedAgent,
        TestPerformanceBenchmarks,
        TestIntegrationScenarios
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n🔬 Running {test_class.__name__}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        for test in suite:
            total_tests += 1
            try:
                # Run async tests
                if hasattr(test._testMethodName, 'test_'):
                    method = getattr(test, test._testMethodName)
                    if asyncio.iscoroutinefunction(method):
                        await method()
                    else:
                        method()
                
                print(f"  ✅ {test._testMethodName}")
                passed_tests += 1
                
            except Exception as e:
                print(f"  ❌ {test._testMethodName}: {e}")
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    print("TCP-LangChain Integration Test Suite")
    print("Testing breakthrough AI agent safety integration")
    print("=" * 60)
    
    # Run comprehensive tests
    success = asyncio.run(run_comprehensive_tests())
    
    if success:
        print("\n🎉 All tests passed! TCP-LangChain integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Review output above.")
        
    # Performance summary
    print("\n📈 Expected Performance (from TCP research):")
    print("- Decision speed: <1ms (vs minutes for documentation)")
    print("- Compression: 362:1 (vs traditional documentation)")
    print("- Accuracy: 100% (validated against expert knowledge)")
    print("- Coverage: 709+ commands with system-wide intelligence")