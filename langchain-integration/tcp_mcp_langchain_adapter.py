"""
TCP-MCP-LangChain Adapter: Direct integration with existing TCP MCP server.

This adapter bridges the TCP MCP server with LangChain agents using langchain-mcp-adapters,
providing real-time safety monitoring for autonomous agents.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import dependencies with graceful fallbacks
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.tools import convert_mcp_tool_to_langchain_tool
    MCP_ADAPTERS_AVAILABLE = True
except ImportError:
    MCP_ADAPTERS_AVAILABLE = False
    logger.warning("langchain-mcp-adapters not available. Install with: pip install langchain-mcp-adapters")

try:
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain_core.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain.tools.base import BaseTool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available. Install with: pip install langchain langchain-openai")


class TCPMCPLangChainAdapter:
    """
    Adapter that connects TCP MCP server with LangChain agents.
    
    This adapter leverages your existing TCP MCP server infrastructure to provide
    real-time safety monitoring for LangChain agents using the proven 362:1 compression
    and microsecond decision capabilities.
    """
    
    def __init__(self, tcp_server_path: str = None):
        """
        Initialize TCP-MCP-LangChain adapter.
        
        Args:
            tcp_server_path: Path to TCP MCP server script
        """
        self.tcp_server_path = tcp_server_path or self._find_tcp_server()
        self.mcp_client = None
        self.tcp_tools = []
        self.safety_stats = {
            "commands_analyzed": 0,
            "safety_blocks": 0,
            "safe_alternatives_used": 0,
            "total_decision_time": 0.0
        }
        
        logger.info(f"TCP-MCP-LangChain adapter initialized with server: {self.tcp_server_path}")
    
    def _find_tcp_server(self) -> str:
        """Find TCP MCP server script in common locations."""
        possible_paths = [
            "/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/mcp-server/tcp_mcp_server.py",
            "../mcp-server/tcp_mcp_server.py",
            "./tcp_mcp_server.py",
            "tcp_mcp_server.py"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return str(Path(path).resolve())
        
        raise FileNotFoundError(
            "TCP MCP server not found. Please ensure tcp_mcp_server.py is available or specify tcp_server_path."
        )
    
    async def initialize_mcp_client(self) -> None:
        """Initialize MCP client connection to TCP server."""
        if not MCP_ADAPTERS_AVAILABLE:
            raise ImportError("langchain-mcp-adapters is required for MCP client functionality")
        
        try:
            # Create MCP client configuration
            mcp_config = {
                "tcp_safety": {
                    "command": "python",
                    "args": [self.tcp_server_path],
                    "transport": "stdio"
                }
            }
            
            # Initialize MCP client
            self.mcp_client = MultiServerMCPClient(mcp_config)
            
            # Load TCP tools
            self.tcp_tools = await self.mcp_client.get_tools()
            
            logger.info(f"TCP MCP client initialized with {len(self.tcp_tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            raise
    
    async def get_tcp_langchain_tools(self) -> List['BaseTool']:
        """
        Get TCP-enhanced LangChain tools.
        
        Returns:
            List of LangChain tools with TCP safety integration
        """
        if not self.mcp_client:
            await self.initialize_mcp_client()
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is required for tool conversion")
        
        langchain_tools = []
        
        for mcp_tool in self.tcp_tools:
            try:
                # Convert MCP tool to LangChain tool
                langchain_tool = convert_mcp_tool_to_langchain_tool(mcp_tool)
                
                # Wrap with TCP safety monitoring
                tcp_safe_tool = TCPSafetyWrapper(langchain_tool, self)
                langchain_tools.append(tcp_safe_tool)
                
            except Exception as e:
                logger.warning(f"Failed to convert tool {mcp_tool.name}: {e}")
        
        logger.info(f"Created {len(langchain_tools)} TCP-enhanced LangChain tools")
        return langchain_tools
    
    async def assess_command_safety(self, command: str, tool_name: str = None) -> Dict[str, Any]:
        """
        Assess command safety using TCP MCP server.
        
        Args:
            command: Command to assess
            tool_name: Name of the tool being used
            
        Returns:
            Safety assessment result
        """
        if not self.mcp_client:
            await self.initialize_mcp_client()
        
        try:
            # Find TCP safety assessment tool
            safety_tool = None
            for tool in self.tcp_tools:
                if "assess" in tool.name.lower() or "safety" in tool.name.lower():
                    safety_tool = tool
                    break
            
            if not safety_tool:
                logger.warning("No TCP safety assessment tool found")
                return {
                    "risk_level": "UNKNOWN",
                    "decision": "CAUTION",
                    "explanation": "TCP safety assessment unavailable"
                }
            
            # Call TCP safety assessment
            result = await safety_tool.ainvoke({
                "command": command,
                "context": {"tool_name": tool_name}
            })
            
            # Update statistics
            self.safety_stats["commands_analyzed"] += 1
            
            # Parse result
            if isinstance(result, str):
                try:
                    safety_result = json.loads(result)
                except json.JSONDecodeError:
                    safety_result = {"explanation": result, "risk_level": "UNKNOWN"}
            else:
                safety_result = result
            
            # Log high-risk commands
            if safety_result.get("risk_level") in ["HIGH_RISK", "CRITICAL"]:
                self.safety_stats["safety_blocks"] += 1
                logger.warning(f"TCP Safety Alert: {command} - {safety_result.get('risk_level')}")
            
            return safety_result
            
        except Exception as e:
            logger.error(f"TCP safety assessment failed: {e}")
            return {
                "risk_level": "ERROR",
                "decision": "REQUIRE_APPROVAL",
                "explanation": f"Safety assessment error: {str(e)}"
            }
    
    def get_safety_statistics(self) -> Dict[str, Any]:
        """Get TCP safety monitoring statistics."""
        return {
            **self.safety_stats,
            "safety_block_rate": (
                self.safety_stats["safety_blocks"] / max(self.safety_stats["commands_analyzed"], 1)
            ),
            "tools_available": len(self.tcp_tools),
            "tcp_server_path": self.tcp_server_path
        }


class TCPSafetyWrapper:  # Will inherit from BaseTool when available
    """
    LangChain tool wrapper with TCP safety monitoring.
    """
    
    def __init__(self, wrapped_tool: 'BaseTool', tcp_adapter: TCPMCPLangChainAdapter):
        """
        Initialize TCP safety wrapper.
        
        Args:
            wrapped_tool: Original LangChain tool
            tcp_adapter: TCP-MCP adapter instance
        """
        self.wrapped_tool = wrapped_tool
        self.tcp_adapter = tcp_adapter
        
        # Copy tool properties
        self.name = f"tcp_safe_{wrapped_tool.name}"
        self.description = f"TCP-enhanced {wrapped_tool.description}"
        self.args_schema = wrapped_tool.args_schema
    
    def _run(self, query: str, **kwargs) -> str:
        """
        Synchronous run with TCP safety monitoring.
        
        Args:
            query: Tool query
            **kwargs: Additional arguments
            
        Returns:
            Tool result with safety monitoring
        """
        # Run async safety check in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(self._arun(query, **kwargs))
        finally:
            loop.close()
    
    async def _arun(self, query: str, **kwargs) -> str:
        """
        Asynchronous run with TCP safety monitoring.
        
        Args:
            query: Tool query
            **kwargs: Additional arguments
            
        Returns:
            Tool result with safety monitoring
        """
        # Assess command safety using TCP
        safety_result = await self.tcp_adapter.assess_command_safety(query, self.wrapped_tool.name)
        
        # Apply safety decision
        decision = safety_result.get("decision", "UNKNOWN")
        risk_level = safety_result.get("risk_level", "UNKNOWN")
        
        if decision == "REJECT" or risk_level == "CRITICAL":
            return f"🚫 Command rejected by TCP safety monitor: {safety_result.get('explanation', 'High risk operation')}"
        
        elif decision == "REQUIRE_APPROVAL":
            return f"⚠️ Command requires approval: {safety_result.get('explanation', 'Review needed')}"
        
        elif "safe_alternative" in safety_result:
            safe_alt = safety_result["safe_alternative"]
            self.tcp_adapter.safety_stats["safe_alternatives_used"] += 1
            logger.info(f"Using TCP safe alternative: {safe_alt}")
            
            # Execute safe alternative
            if hasattr(self.wrapped_tool, '_arun'):
                return await self.wrapped_tool._arun(safe_alt, **kwargs)
            else:
                return self.wrapped_tool._run(safe_alt, **kwargs)
        
        else:
            # Execute original command with TCP monitoring
            logger.info(f"TCP approved: {query} (Risk: {risk_level})")
            
            if hasattr(self.wrapped_tool, '_arun'):
                return await self.wrapped_tool._arun(query, **kwargs)
            else:
                return self.wrapped_tool._run(query, **kwargs)


class TCPEnhancedAgent:
    """
    LangChain agent enhanced with TCP safety monitoring.
    """
    
    def __init__(self, 
                 llm: Optional[Any] = None,
                 tcp_server_path: Optional[str] = None):
        """
        Initialize TCP-enhanced agent.
        
        Args:
            llm: LangChain LLM instance
            tcp_server_path: Path to TCP MCP server
        """
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available for full functionality")
            self.llm = llm
        else:
            self.llm = llm or ChatOpenAI(model="gpt-4", temperature=0)
        self.tcp_adapter = TCPMCPLangChainAdapter(tcp_server_path)
        self.agent_executor = None
        
    async def create_agent(self, additional_tools: List['BaseTool'] = None) -> 'AgentExecutor':
        """
        Create TCP-enhanced LangChain agent.
        
        Args:
            additional_tools: Additional tools to include
            
        Returns:
            Agent executor with TCP safety monitoring
        """
        # Get TCP-enhanced tools
        tcp_tools = await self.tcp_adapter.get_tcp_langchain_tools()
        
        # Combine with additional tools
        all_tools = tcp_tools + (additional_tools or [])
        
        # Create safety-enhanced prompt
        prompt = PromptTemplate.from_template("""
You are an AI assistant enhanced with the Tool Capability Protocol (TCP) for real-time safety monitoring.

TCP provides microsecond safety decisions using binary intelligence from 709+ commands with 362:1 compression.

Safety Guidelines:
- Commands are automatically assessed for risk level (SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL)
- High-risk commands may be blocked or require approval
- Safe alternatives are automatically suggested when available
- All decisions are logged for audit compliance

Available tools: {tools}

Question: {input}
{agent_scratchpad}
""")
        
        # Create ReAct agent with TCP safety
        agent = create_react_agent(
            llm=self.llm,
            tools=all_tools,
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=all_tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )
        
        return self.agent_executor
    
    def get_safety_report(self) -> Dict[str, Any]:
        """Get comprehensive TCP safety report."""
        return self.tcp_adapter.get_safety_statistics()


# Example usage and demo
async def demo_tcp_enhanced_agent():
    """Demonstrate TCP-enhanced LangChain agent."""
    print("🔐 TCP-Enhanced LangChain Agent Demo")
    print("=" * 50)
    
    try:
        # Create TCP-enhanced agent
        agent = TCPEnhancedAgent()
        
        # Create agent executor
        executor = await agent.create_agent()
        
        # Test queries with different risk levels
        test_queries = [
            "What is the current working directory?",
            "List files in the current directory",
            "Create a test file with hello world",
            "Show system processes",
            "Delete temporary files safely"
        ]
        
        print(f"Testing {len(test_queries)} queries with TCP safety monitoring...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            print("-" * 40)
            
            try:
                result = await executor.ainvoke({"input": query})
                print(f"✅ Result: {result['output']}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                logger.error(f"Query failed: {query} - {e}")
        
        # Display safety report
        print("\n📊 TCP Safety Report:")
        print("-" * 30)
        report = agent.get_safety_report()
        
        for key, value in report.items():
            print(f"{key}: {value}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")


if __name__ == "__main__":
    print("TCP-MCP-LangChain Adapter")
    print("Integrating Tool Capability Protocol with LangChain agents")
    print("=" * 60)
    
    if MCP_ADAPTERS_AVAILABLE and LANGCHAIN_AVAILABLE:
        asyncio.run(demo_tcp_enhanced_agent())
    else:
        print("Missing dependencies:")
        if not MCP_ADAPTERS_AVAILABLE:
            print("- langchain-mcp-adapters: pip install langchain-mcp-adapters")
        if not LANGCHAIN_AVAILABLE:
            print("- langchain: pip install langchain langchain-openai")
        print("\nInstall dependencies and run again.")