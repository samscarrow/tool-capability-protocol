"""LLM-based extraction for enhanced help text analysis."""

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Union

try:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.prompts import PromptTemplate
    from langchain_ollama import OllamaLLM
    from langchain_openai import ChatOpenAI

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

    # Create dummy classes to prevent import errors
    class PromptTemplate:
        def __init__(self, *args, **kwargs):
            pass

    class JsonOutputParser:
        def __init__(self, *args, **kwargs):
            pass

    class ChatOpenAI:
        def __init__(self, *args, **kwargs):
            pass

    class ChatAnthropic:
        def __init__(self, *args, **kwargs):
            pass

    class OllamaLLM:
        def __init__(self, *args, **kwargs):
            pass


try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from .help_parser import HelpTextAnalysis, RawCommand, RawOption


@dataclass
class EnhancedOption:
    """Enhanced option with LLM-extracted metadata."""

    short_flag: Optional[str] = None
    long_flag: Optional[str] = None
    description: str = ""
    parameter_type: str = "boolean"  # boolean, string, integer, float, enum, path, url
    is_required: bool = False
    default_value: Optional[str] = None
    enum_values: List[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    examples: List[str] = None
    conflicts_with: List[str] = None
    requires: List[str] = None
    category: str = "general"  # input, output, behavior, performance, debug
    stability: str = "stable"  # stable, experimental, deprecated


@dataclass
class EnhancedCommand:
    """Enhanced command with LLM-extracted metadata."""

    name: str
    description: str = ""
    category: str = "action"
    options: List[EnhancedOption] = None
    input_formats: List[str] = None
    output_formats: List[str] = None
    examples: List[str] = None
    performance_hints: Dict[str, Any] = None
    error_codes: Dict[int, str] = None
    side_effects: List[str] = None


@dataclass
class ToolCapabilities:
    """Enhanced tool capabilities extracted by LLM."""

    tool_name: str
    version: Optional[str] = None
    description: str = ""
    vendor: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None

    # Core capabilities
    commands: List[EnhancedCommand] = None
    global_options: List[EnhancedOption] = None

    # Processing capabilities
    supports_stdin: bool = False
    supports_files: bool = False
    supports_directories: bool = False
    supports_recursion: bool = False
    supports_parallel: bool = False
    supports_streaming: bool = False

    # Format capabilities
    input_formats: List[str] = None
    output_formats: List[str] = None

    # Performance characteristics
    memory_usage: str = "low"  # low, medium, high
    cpu_usage: str = "low"
    disk_usage: str = "none"  # none, temporary, persistent
    network_usage: str = "none"

    # Quality metrics
    confidence_score: float = 0.0
    extraction_method: str = "unknown"


class LLMExtractor(ABC):
    """Abstract base class for LLM-based help text extraction."""

    @abstractmethod
    def extract_capabilities(self, analysis: HelpTextAnalysis) -> ToolCapabilities:
        """Extract enhanced capabilities from help text analysis."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this extractor is available."""
        pass


class LangChainExtractor(LLMExtractor):
    """LangChain-based extraction using various LLM providers."""

    def __init__(self, provider: str = "openai", model: str = None, **kwargs):
        """Initialize LangChain extractor."""
        self.provider = provider
        self.model = model
        self.kwargs = kwargs
        self.logger = logging.getLogger(__name__)

        if not LANGCHAIN_AVAILABLE:
            self.llm = None
            self.logger.warning(
                "LangChain not available. Install with: pip install langchain"
            )
        else:
            self.llm = self._create_llm()

    def _create_llm(self):
        """Create LLM instance based on provider."""
        if self.provider == "openai":
            return ChatOpenAI(
                model=self.model or "gpt-4o-mini", temperature=0.1, **self.kwargs
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                model=self.model or "claude-3-haiku-20240307",
                temperature=0.1,
                **self.kwargs,
            )
        elif self.provider == "ollama":
            return OllamaLLM(
                model=self.model or "llama3.1", temperature=0.1, **self.kwargs
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def is_available(self) -> bool:
        """Check if LangChain and provider are available."""
        if not LANGCHAIN_AVAILABLE or self.llm is None:
            return False
        try:
            # Try a simple call to test availability
            self.llm.invoke("test")
            return True
        except Exception:
            return False

    def extract_capabilities(self, analysis: HelpTextAnalysis) -> ToolCapabilities:
        """Extract capabilities using LangChain."""
        prompt = self._create_extraction_prompt()
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser

        try:
            # Prepare input data
            input_data = {
                "tool_name": analysis.tool_name,
                "version": analysis.version or "unknown",
                "description": analysis.description,
                "usage_patterns": analysis.usage_patterns,
                "options": [asdict(opt) for opt in analysis.global_options],
                "examples": analysis.examples,
            }

            # Extract capabilities
            result = chain.invoke({"analysis": json.dumps(input_data, indent=2)})

            # Convert to ToolCapabilities
            capabilities = self._parse_llm_result(result, analysis)
            capabilities.extraction_method = f"langchain_{self.provider}"

            return capabilities

        except Exception as e:
            self.logger.error(f"LangChain extraction failed: {e}")
            # Fallback to basic conversion
            return self._fallback_extraction(analysis)

    def _create_extraction_prompt(self) -> PromptTemplate:
        """Create prompt template for capability extraction."""
        template = """
Analyze the following command-line tool help text analysis and extract comprehensive capabilities in JSON format.

Tool Analysis:
{analysis}

Extract the following information and return as valid JSON:

{{
  "tool_name": "string",
  "version": "string or null",
  "description": "string", 
  "vendor": "string or null",
  "homepage": "string or null",
  "commands": [
    {{
      "name": "string",
      "description": "string",
      "category": "action|query|config|utility",
      "options": [
        {{
          "short_flag": "string or null",
          "long_flag": "string or null", 
          "description": "string",
          "parameter_type": "boolean|string|integer|float|enum|path|url",
          "is_required": boolean,
          "default_value": "string or null",
          "enum_values": ["array of strings or null"],
          "category": "input|output|behavior|performance|debug|general",
          "examples": ["array of strings or null"]
        }}
      ],
      "input_formats": ["array of strings or null"],
      "output_formats": ["array of strings or null"],
      "examples": ["array of strings or null"]
    }}
  ],
  "supports_stdin": boolean,
  "supports_files": boolean,
  "supports_directories": boolean,
  "supports_recursion": boolean,
  "supports_parallel": boolean,
  "supports_streaming": boolean,
  "input_formats": ["array of strings"],
  "output_formats": ["array of strings"],
  "memory_usage": "low|medium|high",
  "cpu_usage": "low|medium|high",
  "confidence_score": float_between_0_and_1
}}

Guidelines:
1. Infer parameter types from descriptions (look for file paths, numbers, etc.)
2. Categorize options logically (input/output/behavior/etc.)
3. Detect format support from descriptions and examples
4. Infer processing capabilities from option names and descriptions
5. Estimate resource usage based on tool type and capabilities
6. Be conservative with confidence scores
7. Return ONLY valid JSON, no additional text

JSON Output:"""

        return PromptTemplate(input_variables=["analysis"], template=template)

    def _parse_llm_result(
        self, result: Dict[str, Any], original: HelpTextAnalysis
    ) -> ToolCapabilities:
        """Parse LLM result into ToolCapabilities."""
        capabilities = ToolCapabilities(
            tool_name=result.get("tool_name", original.tool_name),
            version=result.get("version") or original.version,
            description=result.get("description", original.description),
            vendor=result.get("vendor"),
            homepage=result.get("homepage"),
            confidence_score=result.get("confidence_score", 0.7),
        )

        # Parse commands
        if result.get("commands"):
            capabilities.commands = []
            for cmd_data in result["commands"]:
                cmd = EnhancedCommand(
                    name=cmd_data.get("name", "default"),
                    description=cmd_data.get("description", ""),
                    category=cmd_data.get("category", "action"),
                    input_formats=cmd_data.get("input_formats", []),
                    output_formats=cmd_data.get("output_formats", []),
                    examples=cmd_data.get("examples", []),
                )

                # Parse options
                if cmd_data.get("options"):
                    cmd.options = []
                    for opt_data in cmd_data["options"]:
                        option = EnhancedOption(
                            short_flag=opt_data.get("short_flag"),
                            long_flag=opt_data.get("long_flag"),
                            description=opt_data.get("description", ""),
                            parameter_type=opt_data.get("parameter_type", "boolean"),
                            is_required=opt_data.get("is_required", False),
                            default_value=opt_data.get("default_value"),
                            enum_values=opt_data.get("enum_values"),
                            category=opt_data.get("category", "general"),
                            examples=opt_data.get("examples"),
                        )
                        cmd.options.append(option)

                capabilities.commands.append(cmd)

        # Set processing capabilities
        capabilities.supports_stdin = result.get("supports_stdin", False)
        capabilities.supports_files = result.get("supports_files", False)
        capabilities.supports_directories = result.get("supports_directories", False)
        capabilities.supports_recursion = result.get("supports_recursion", False)
        capabilities.supports_parallel = result.get("supports_parallel", False)
        capabilities.supports_streaming = result.get("supports_streaming", False)

        # Set formats
        capabilities.input_formats = result.get("input_formats", [])
        capabilities.output_formats = result.get("output_formats", [])

        # Set resource usage
        capabilities.memory_usage = result.get("memory_usage", "low")
        capabilities.cpu_usage = result.get("cpu_usage", "low")

        return capabilities

    def _fallback_extraction(self, analysis: HelpTextAnalysis) -> ToolCapabilities:
        """Fallback extraction without LLM."""
        capabilities = ToolCapabilities(
            tool_name=analysis.tool_name,
            version=analysis.version,
            description=analysis.description,
            confidence_score=0.3,
            extraction_method="fallback",
        )

        # Convert commands
        capabilities.commands = []
        for raw_cmd in analysis.commands:
            cmd = EnhancedCommand(
                name=raw_cmd.name, description=raw_cmd.description, options=[]
            )

            # Convert options
            for raw_opt in raw_cmd.options:
                option = EnhancedOption(
                    short_flag=raw_opt.short_flag,
                    long_flag=raw_opt.long_flag,
                    description=raw_opt.description,
                    parameter_type="string" if raw_opt.takes_value else "boolean",
                    is_required=raw_opt.is_required,
                )
                cmd.options.append(option)

            capabilities.commands.append(cmd)

        return capabilities


class LocalLLMExtractor(LLMExtractor):
    """Local LLM extraction using Ollama or direct HTTP APIs."""

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "llama3.1"
    ):
        """Initialize local LLM extractor."""
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "Requests not available. Install with: pip install requests"
            )

        self.base_url = base_url.rstrip("/")
        self.model = model
        self.logger = logging.getLogger(__name__)

    def is_available(self) -> bool:
        """Check if local LLM is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def extract_capabilities(self, analysis: HelpTextAnalysis) -> ToolCapabilities:
        """Extract capabilities using local LLM."""
        prompt = self._create_extraction_prompt(analysis)

        try:
            response = self._call_local_llm(prompt)
            result = self._parse_response(response)

            capabilities = self._parse_llm_result(result, analysis)
            capabilities.extraction_method = f"local_llm_{self.model}"

            return capabilities

        except Exception as e:
            self.logger.error(f"Local LLM extraction failed: {e}")
            return self._fallback_extraction(analysis)

    def _call_local_llm(self, prompt: str) -> str:
        """Call local LLM API."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "top_p": 0.9},
        }

        response = requests.post(
            f"{self.base_url}/api/generate", json=payload, timeout=60
        )
        response.raise_for_status()

        return response.json()["response"]

    def _create_extraction_prompt(self, analysis: HelpTextAnalysis) -> str:
        """Create extraction prompt for local LLM."""
        input_data = {
            "tool_name": analysis.tool_name,
            "version": analysis.version or "unknown",
            "description": analysis.description,
            "usage_patterns": analysis.usage_patterns,
            "options": [
                {
                    "short_flag": opt.short_flag,
                    "long_flag": opt.long_flag,
                    "description": opt.description,
                    "takes_value": opt.takes_value,
                }
                for opt in analysis.global_options
            ],
            "examples": analysis.examples,
        }

        return f"""
Analyze this command-line tool and extract capabilities as JSON.

Tool Analysis:
{json.dumps(input_data, indent=2)}

Extract and return ONLY a valid JSON object with these fields:
- tool_name, version, description
- supports_stdin, supports_files, supports_directories (boolean)
- supports_recursion, supports_parallel, supports_streaming (boolean)  
- input_formats, output_formats (arrays of strings)
- memory_usage, cpu_usage ("low"/"medium"/"high")
- commands array with name, description, options
- Each option has: short_flag, long_flag, description, parameter_type, is_required

JSON:"""

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract JSON."""
        # Try to find JSON in response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Fallback: try to parse entire response
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            raise ValueError("Could not parse JSON from LLM response")

    def _parse_llm_result(
        self, result: Dict[str, Any], original: HelpTextAnalysis
    ) -> ToolCapabilities:
        """Parse LLM result into ToolCapabilities (same as LangChain version)."""
        capabilities = ToolCapabilities(
            tool_name=result.get("tool_name", original.tool_name),
            version=result.get("version") or original.version,
            description=result.get("description", original.description),
            confidence_score=result.get("confidence_score", 0.6),
        )

        # Parse processing capabilities
        capabilities.supports_stdin = result.get("supports_stdin", False)
        capabilities.supports_files = result.get("supports_files", False)
        capabilities.supports_directories = result.get("supports_directories", False)
        capabilities.supports_recursion = result.get("supports_recursion", False)
        capabilities.supports_parallel = result.get("supports_parallel", False)
        capabilities.supports_streaming = result.get("supports_streaming", False)

        # Parse formats
        capabilities.input_formats = result.get("input_formats", [])
        capabilities.output_formats = result.get("output_formats", [])

        # Parse resource usage
        capabilities.memory_usage = result.get("memory_usage", "low")
        capabilities.cpu_usage = result.get("cpu_usage", "low")

        # Parse commands (simplified for local LLM)
        capabilities.commands = []
        for cmd_data in result.get("commands", []):
            cmd = EnhancedCommand(
                name=cmd_data.get("name", "default"),
                description=cmd_data.get("description", ""),
                options=[],
            )

            for opt_data in cmd_data.get("options", []):
                option = EnhancedOption(
                    short_flag=opt_data.get("short_flag"),
                    long_flag=opt_data.get("long_flag"),
                    description=opt_data.get("description", ""),
                    parameter_type=opt_data.get("parameter_type", "boolean"),
                    is_required=opt_data.get("is_required", False),
                )
                cmd.options.append(option)

            capabilities.commands.append(cmd)

        return capabilities

    def _fallback_extraction(self, analysis: HelpTextAnalysis) -> ToolCapabilities:
        """Fallback extraction without LLM (same as LangChain version)."""
        capabilities = ToolCapabilities(
            tool_name=analysis.tool_name,
            version=analysis.version,
            description=analysis.description,
            confidence_score=0.3,
            extraction_method="fallback",
        )

        capabilities.commands = []
        for raw_cmd in analysis.commands:
            cmd = EnhancedCommand(
                name=raw_cmd.name, description=raw_cmd.description, options=[]
            )

            for raw_opt in raw_cmd.options:
                option = EnhancedOption(
                    short_flag=raw_opt.short_flag,
                    long_flag=raw_opt.long_flag,
                    description=raw_opt.description,
                    parameter_type="string" if raw_opt.takes_value else "boolean",
                    is_required=raw_opt.is_required,
                )
                cmd.options.append(option)

            capabilities.commands.append(cmd)

        return capabilities
