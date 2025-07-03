#!/usr/bin/env python3
"""
TCP Performance Benchmark Runner

Execute comprehensive performance comparison between native TCP and current models.
Generates publication-ready results with statistical analysis.
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Optional

import structlog
import click
import yaml

from performance_benchmark import TCPPerformanceBenchmark, BenchmarkConfig

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

def load_config(config_file: Optional[str] = None) -> BenchmarkConfig:
    """Load benchmark configuration from YAML file"""
    if config_file:
        config_path = Path(config_file)
    else:
        config_path = Path(__file__).parent / "benchmark_config.yaml"
    
    if not config_path.exists():
        logger.warning("Config file not found, using defaults", path=str(config_path))
        return BenchmarkConfig()
    
    try:
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        
        # Extract test config
        test_config = config_data.get("test_config", {})
        
        return BenchmarkConfig(
            command_sample_size=test_config.get("command_sample_size", 1000),
            repetitions_per_test=test_config.get("repetitions_per_test", 10),
            confidence_level=test_config.get("confidence_level", 0.95),
            timeout_seconds=test_config.get("timeout_seconds", 30),
            openai_model=config_data.get("models", {}).get("openai", {}).get("model", "gpt-4"),
            anthropic_model=config_data.get("models", {}).get("anthropic", {}).get("model", "claude-3-sonnet-20240229"),
            tcp_descriptor_size=config_data.get("models", {}).get("tcp", {}).get("descriptor_size", 24),
            tcp_analysis_target_ms=config_data.get("models", {}).get("tcp", {}).get("target_latency_ms", 1.0),
            results_dir=config_data.get("output", {}).get("results_directory", "benchmark_results"),
            generate_visualizations=True,
            generate_report=True
        )
        
    except Exception as e:
        logger.error("Failed to load config file", path=str(config_path), error=str(e))
        return BenchmarkConfig()

@click.command()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--sample-size', '-s', type=int, help='Number of commands to test')
@click.option('--models', '-m', multiple=True, 
              type=click.Choice(['tcp', 'gpt4', 'claude', 'all']),
              default=['all'], help='Models to benchmark')
@click.option('--quick', '-q', is_flag=True, help='Quick test with smaller dataset')
@click.option('--output-dir', '-o', help='Output directory for results')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(config: Optional[str], sample_size: Optional[int], models: tuple, 
         quick: bool, output_dir: Optional[str], verbose: bool):
    """
    Run comprehensive TCP vs LLM performance benchmark
    
    This benchmark scientifically compares TCP binary analysis with current
    LLM-based approaches across multiple performance dimensions.
    """
    
    # Set up logging level
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    logger.info("Starting TCP Performance Benchmark")
    
    # Load configuration
    benchmark_config = load_config(config)
    
    # Override config with command line options
    if sample_size:
        benchmark_config.command_sample_size = sample_size
    
    if quick:
        benchmark_config.command_sample_size = 50
        benchmark_config.repetitions_per_test = 3
        logger.info("Quick mode enabled", sample_size=50)
    
    if output_dir:
        benchmark_config.results_dir = output_dir
    
    # Determine which models to test
    test_models = set(models)
    if 'all' in test_models:
        test_models = {'tcp', 'gpt4', 'claude'}
    
    logger.info("Benchmark configuration loaded", 
                sample_size=benchmark_config.command_sample_size,
                models=list(test_models),
                output_dir=benchmark_config.results_dir)
    
    # Run benchmark
    try:
        asyncio.run(run_benchmark_async(benchmark_config, test_models))
    except KeyboardInterrupt:
        logger.info("Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Benchmark failed", error=str(e))
        sys.exit(1)

async def run_benchmark_async(config: BenchmarkConfig, test_models: set):
    """Run the asynchronous benchmark"""
    
    benchmark = TCPPerformanceBenchmark(config)
    
    try:
        # Pre-flight checks
        logger.info("Performing pre-flight checks...")
        await benchmark.initialize_tcp_system()
        
        # Check API credentials if needed
        if 'gpt4' in test_models:
            try:
                import openai
                client = openai.OpenAI()
                # Quick test call
                await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: client.models.list()
                )
                logger.info("OpenAI API access verified")
            except Exception as e:
                logger.warning("OpenAI API not available", error=str(e))
                test_models.discard('gpt4')
        
        if 'claude' in test_models:
            try:
                import anthropic
                client = anthropic.Anthropic()
                # The client will validate API key on first use
                logger.info("Anthropic API configured")
            except Exception as e:
                logger.warning("Anthropic API not available", error=str(e))
                test_models.discard('claude')
        
        logger.info("Pre-flight checks complete", active_models=list(test_models))
        
        # Run full benchmark
        results = await benchmark.run_comprehensive_benchmark()
        
        # Display summary results
        print("\n" + "="*60)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*60)
        
        for method, metrics in results.items():
            print(f"\n{method.upper()}:")
            print(f"  Commands Analyzed: {metrics.total_commands}")
            print(f"  Accuracy:         {metrics.accuracy_score:.1%}")
            print(f"  Consistency:      {metrics.consistency_score:.1%}")
            print(f"  Error Rate:       {metrics.error_rate:.1%}")
            
            if metrics.latency_stats:
                stats = metrics.latency_stats
                print(f"  Mean Latency:     {stats['mean']:.2f}ms")
                print(f"  Median Latency:   {stats['median']:.2f}ms")
                print(f"  P95 Latency:      {stats['p95']:.2f}ms")
                print(f"  P99 Latency:      {stats['p99']:.2f}ms")
        
        # Performance comparison
        if 'TCP' in results and len(results) > 1:
            tcp_metrics = results['TCP']
            tcp_latency = tcp_metrics.latency_stats.get('mean', 0)
            
            print(f"\nPERFORMANCE COMPARISON:")
            
            for method, metrics in results.items():
                if method == 'TCP':
                    continue
                
                if metrics.latency_stats:
                    other_latency = metrics.latency_stats.get('mean', float('inf'))
                    if other_latency > 0:
                        speedup = other_latency / tcp_latency
                        print(f"  TCP vs {method}: {speedup:.1f}x faster")
                
                accuracy_diff = tcp_metrics.accuracy_score - metrics.accuracy_score
                consistency_diff = tcp_metrics.consistency_score - metrics.consistency_score
                
                print(f"  TCP vs {method}: {accuracy_diff:+.1%} accuracy, {consistency_diff:+.1%} consistency")
        
        print(f"\nDetailed results saved to: {config.results_dir}")
        print("="*60)
        
        logger.info("Benchmark completed successfully", 
                   results_dir=config.results_dir,
                   models_tested=list(results.keys()))
        
    except Exception as e:
        logger.error("Benchmark execution failed", error=str(e))
        raise

if __name__ == "__main__":
    main()