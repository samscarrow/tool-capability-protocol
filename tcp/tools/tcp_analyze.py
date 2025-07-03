#!/usr/bin/env python3
"""
TCP Analysis Tool - Convert arbitrary command help text to TCP descriptors.

This tool can analyze any command-line tool and generate TCP descriptors using
LLM-powered extraction or basic parsing.
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tcp.analysis.pipeline import TCPGenerationPipeline


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze command-line tools and generate TCP descriptors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze grep with OpenAI
  tcp-analyze grep --llm langchain_openai --output-format json tcp

  # Analyze find with local LLM (Ollama)
  tcp-analyze find --llm local_llm --model llama3.1

  # Batch analyze multiple commands
  tcp-analyze grep find ls --batch --output-dir ./tcp_descriptors

  # Use pre-extracted help text
  tcp-analyze "my-tool" --help-text "$(my-tool --help)" --llm basic

  # Auto-detect best LLM provider
  tcp-analyze docker --llm auto --output-format json binary openapi

Available LLM providers:
  - auto: Auto-detect best available provider
  - langchain_openai: OpenAI via LangChain (requires OPENAI_API_KEY)
  - langchain_anthropic: Anthropic via LangChain (requires ANTHROPIC_API_KEY)  
  - langchain_ollama: Ollama via LangChain (requires Ollama server)
  - local_llm: Direct Ollama API (requires Ollama server)
  - basic: No LLM, basic parsing only
        """
    )
    
    # Command arguments
    parser.add_argument(
        "commands",
        nargs="+",
        help="Commands to analyze (e.g., 'grep', 'find', 'docker ps')"
    )
    
    # LLM configuration
    parser.add_argument(
        "--llm",
        choices=["auto", "langchain_openai", "langchain_anthropic", "langchain_ollama", "local_llm", "basic"],
        default="auto",
        help="LLM provider to use for analysis (default: auto)"
    )
    
    parser.add_argument(
        "--model",
        help="Model name (provider-specific, e.g., 'gpt-4', 'claude-3-haiku', 'llama3.1')"
    )
    
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama server URL (default: http://localhost:11434)"
    )
    
    # Input options
    parser.add_argument(
        "--help-text",
        help="Pre-extracted help text (skip automatic extraction)"
    )
    
    parser.add_argument(
        "--help-flags",
        nargs="+",
        default=["--help", "-h"],
        help="Help flags to try (default: --help -h)"
    )
    
    # Output options
    parser.add_argument(
        "--output-format",
        nargs="+",
        choices=["tcp", "json", "binary", "openapi"],
        default=["json"],
        help="Output formats to generate (default: json)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for results (default: stdout)"
    )
    
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Output file for single command (default: stdout)"
    )
    
    # Processing options
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process commands in batch mode"
    )
    
    parser.add_argument(
        "--fallback",
        action="store_true",
        default=True,
        help="Fallback to basic parsing if LLM fails (default: true)"
    )
    
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.3,
        help="Minimum confidence threshold (default: 0.3)"
    )
    
    # Display options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress non-error output"
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: true)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if not args.quiet:
        setup_logging(args.verbose)
    
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize pipeline
        llm_kwargs = {}
        if args.llm == "local_llm":
            llm_kwargs["base_url"] = args.ollama_url
        
        pipeline = TCPGenerationPipeline(
            llm_provider=args.llm,
            model=args.model,
            fallback_to_basic=args.fallback,
            **llm_kwargs
        )
        
        # Process commands
        if args.batch or len(args.commands) > 1:
            # Batch processing
            logger.info(f"Batch processing {len(args.commands)} commands")
            
            results = pipeline.batch_process_commands(
                commands=args.commands,
                output_dir=str(args.output_dir) if args.output_dir else None
            )
            
            # Output batch results
            output_data = results
            
        else:
            # Single command processing
            command = args.commands[0]
            logger.info(f"Processing single command: {command}")
            
            results = pipeline.process_command(
                command=command,
                help_text=args.help_text,
                output_formats=args.output_format
            )
            
            # Check confidence threshold
            if results.get("capabilities"):
                confidence = results["capabilities"].get("confidence_score", 0)
                if confidence < args.confidence_threshold:
                    logger.warning(f"Low confidence score: {confidence} < {args.confidence_threshold}")
            
            output_data = results
        
        # Output results
        if args.output_file:
            # Single file output
            with open(args.output_file, 'w') as f:
                json.dump(output_data, f, indent=2 if args.pretty else None, default=str)
            logger.info(f"Results written to {args.output_file}")
            
        elif args.output_dir:
            # Directory output (batch mode)
            args.output_dir.mkdir(parents=True, exist_ok=True)
            
            summary_file = args.output_dir / "batch_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(output_data, f, indent=2 if args.pretty else None, default=str)
            logger.info(f"Batch summary written to {summary_file}")
            
        else:
            # Stdout output
            if not args.quiet:
                json.dump(output_data, sys.stdout, indent=2 if args.pretty else None, default=str)
                print()  # Add newline
        
        # Exit with appropriate code
        if args.batch:
            success_rate = output_data["summary"]["success_rate"]
            if success_rate < 0.5:
                sys.exit(1)  # More failures than successes
        else:
            if not output_data.get("success"):
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        if args.verbose:
            logger.exception("Pipeline failed")
        else:
            logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


def demo():
    """Demo function showing pipeline capabilities."""
    print("=== TCP Analysis Pipeline Demo ===\n")
    
    # Test commands with different characteristics
    test_commands = [
        "grep",      # Text processing with many options
        "find",      # File system traversal
        "docker",    # Complex subcommand structure
        "curl",      # Network tool with many options
        "jq",        # JSON processing
    ]
    
    print("Testing pipeline with different LLM providers:\n")
    
    for provider in ["basic", "local_llm", "langchain_openai"]:
        print(f"Provider: {provider}")
        print("-" * 40)
        
        try:
            pipeline = TCPGenerationPipeline(llm_provider=provider)
            
            if not pipeline.llm_extractor or not pipeline.llm_extractor.is_available():
                print(f"  ❌ {provider} not available")
                continue
            
            # Test with grep
            result = pipeline.process_command("grep", output_formats=["json"])
            
            if result["success"]:
                confidence = result.get("capabilities", {}).get("confidence_score", 0)
                print(f"  ✅ Success (confidence: {confidence:.2f})")
                
                # Show some extracted capabilities
                caps = result.get("capabilities", {})
                print(f"     Supports stdin: {caps.get('supports_stdin', False)}")
                print(f"     Supports files: {caps.get('supports_files', False)}")
                print(f"     Supports recursion: {caps.get('supports_recursion', False)}")
                
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()


if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "demo"):
        demo()
    else:
        main()