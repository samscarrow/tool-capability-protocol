#!/usr/bin/env python3
"""
Test Suite for Statistical Performance Optimization
Elena Vasquez & Yuki Tanaka Collaboration

Comprehensive test suite validating mathematical correctness and performance improvements.
Establishes baselines and measures optimization effectiveness with statistical rigor.
"""

import math
import random
import time
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Import components under test
from tcp.analysis.statistical_performance_engine import (
    OptimizationBackend,
    PerformanceStatistics,
    RingBuffer,
    RunningStatistics,
    StatisticalPerformanceEngine,
)
from tcp.core.descriptors import (
    CapabilityDescriptor,
    CapabilityFlags,
    CommandDescriptor,
    PerformanceMetrics,
)
from tcp.core.optimized_protocol import (
    HighPerformanceCache,
    OptimizationMetrics,
    OptimizedToolCapabilityProtocol,
)


class TestStatisticalValidation:
    """Test statistical correctness of performance measurements."""

    def test_running_statistics_accuracy(self):
        """Test mathematical accuracy of running statistics."""
        # Test data with known statistical properties
        test_data = [1.0, 2.0, 3.0, 4.0, 5.0]
        expected_mean = 3.0
        expected_variance = 2.5  # Sample variance
        expected_std = math.sqrt(2.5)

        stats = RunningStatistics()
        for value in test_data:
            stats.update(value)

        # Validate mathematical correctness
        assert (
            abs(stats.mean - expected_mean) < 1e-10
        ), f"Mean calculation error: {stats.mean} != {expected_mean}"
        assert (
            abs(stats.variance - expected_variance) < 1e-10
        ), f"Variance calculation error: {stats.variance} != {expected_variance}"
        assert (
            abs(stats.std_dev - expected_std) < 1e-10
        ), f"StdDev calculation error: {stats.std_dev} != {expected_std}"
        assert stats.count == 5, f"Count error: {stats.count} != 5"
        assert stats.min_value == 1.0, f"Min error: {stats.min_value} != 1.0"
        assert stats.max_value == 5.0, f"Max error: {stats.max_value} != 5.0"

    def test_confidence_intervals(self):
        """Test confidence interval calculations."""
        # Normal distribution test data
        np.random.seed(42)
        test_data = np.random.normal(100, 15, 1000).tolist()

        stats = RunningStatistics()
        for value in test_data:
            stats.update(value)

        # Test 95% confidence interval
        ci_95 = stats.confidence_interval(0.95)
        margin_95 = ci_95[1] - ci_95[0]

        # Test 99% confidence interval (should be wider)
        ci_99 = stats.confidence_interval(0.99)
        margin_99 = ci_99[1] - ci_99[0]

        assert margin_99 > margin_95, "99% CI should be wider than 95% CI"
        assert (
            ci_95[0] < stats.mean < ci_95[1]
        ), "Mean should be within confidence interval"

        # Validate approximate correctness for large sample
        expected_margin_95 = 1.96 * stats.standard_error
        assert (
            abs(margin_95 - 2 * expected_margin_95) < 0.5
        ), f"CI margin calculation error"

    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        stats = RunningStatistics()

        # Large values
        large_values = [1e10, 1e10 + 1, 1e10 + 2, 1e10 + 3]
        for value in large_values:
            stats.update(value)

        # Should not overflow or lose precision
        assert not math.isnan(stats.mean), "Mean calculation produced NaN"
        assert not math.isinf(stats.variance), "Variance calculation produced inf"
        assert stats.std_dev > 0, "Standard deviation should be positive"

        # Small values near machine epsilon
        stats.reset()
        small_values = [1e-15, 2e-15, 3e-15, 4e-15]
        for value in small_values:
            stats.update(value)

        assert stats.mean > 0, "Mean should be positive for positive values"
        assert not math.isnan(
            stats.variance
        ), "Variance calculation produced NaN for small values"

    def test_welford_algorithm_equivalence(self):
        """Test that Welford's algorithm produces same results as batch calculation."""
        np.random.seed(123)
        test_data = np.random.normal(50, 10, 500).tolist()

        # Welford's algorithm (our implementation)
        welford_stats = RunningStatistics()
        for value in test_data:
            welford_stats.update(value)

        # Batch calculation
        batch_mean = np.mean(test_data)
        batch_var = np.var(test_data, ddof=1)  # Sample variance
        batch_std = np.std(test_data, ddof=1)

        # Compare results
        assert (
            abs(welford_stats.mean - batch_mean) < 1e-10
        ), "Mean mismatch between algorithms"
        assert (
            abs(welford_stats.variance - batch_var) < 1e-10
        ), "Variance mismatch between algorithms"
        assert (
            abs(welford_stats.std_dev - batch_std) < 1e-10
        ), "StdDev mismatch between algorithms"


class TestPerformanceEngine:
    """Test statistical performance engine functionality."""

    @pytest.fixture
    def engine(self):
        """Create test engine instance."""
        return StatisticalPerformanceEngine(
            window_size=1000,
            backend=OptimizationBackend.CPU_BASIC,
            confidence_level=0.95,
        )

    def test_measurement_recording(self, engine):
        """Test measurement recording and analysis."""
        # Record some measurements
        measurements = [10.5, 12.3, 9.8, 11.2, 10.9]
        results = []

        for i, value in enumerate(measurements):
            result = engine.record_measurement(
                operation_id="test_operation", value=value, metadata={"iteration": i}
            )
            results.append(result)

        # Validate structure
        assert len(results) == 5
        final_result = results[-1]

        required_keys = [
            "operation_id",
            "measurement",
            "timestamp",
            "statistics",
            "anomaly_detection",
            "baseline_comparison",
            "performance",
        ]
        for key in required_keys:
            assert key in final_result, f"Missing required key: {key}"

        # Validate statistics
        stats = final_result["statistics"]
        assert stats["count"] == 5
        assert abs(stats["mean"] - np.mean(measurements)) < 1e-10
        assert stats["std_dev"] > 0

        # Validate anomaly detection
        anomaly = final_result["anomaly_detection"]
        assert "z_score" in anomaly
        assert "is_anomaly" in anomaly
        assert anomaly["threshold"] == 3.0

    def test_baseline_establishment(self, engine):
        """Test baseline establishment and comparison."""
        # Establish baseline
        baseline_data = [100.0, 105.0, 95.0, 110.0, 90.0, 108.0, 102.0]
        baseline_stats = engine.establish_baseline("test_op", baseline_data)

        # Validate baseline statistics
        assert baseline_stats.count == len(baseline_data)
        assert abs(baseline_stats.mean - np.mean(baseline_data)) < 1e-10
        assert baseline_stats.std_dev > 0
        assert len(baseline_stats.confidence_interval) == 2
        assert baseline_stats.latency_percentiles[50] > 0  # Median

        # Test new measurement against baseline
        result = engine.record_measurement("test_op", 120.0)  # Higher than baseline

        # Should detect difference from baseline
        baseline_comparison = result["baseline_comparison"]
        assert baseline_comparison["p_value"] is not None
        assert baseline_comparison["effect_size"] is not None

    def test_batch_analysis(self, engine):
        """Test batch statistical analysis."""
        # Generate test data for multiple operations
        np.random.seed(456)
        operation_data = {
            "fast_operation": np.random.normal(5, 1, 1000).tolist(),
            "slow_operation": np.random.normal(50, 10, 1000).tolist(),
            "variable_operation": np.random.gamma(2, 5, 1000).tolist(),
        }

        # Perform batch analysis
        results = engine.batch_statistical_analysis(operation_data)

        # Validate results
        assert len(results) == 3
        for op_name, stats in results.items():
            assert isinstance(stats, PerformanceStatistics)
            assert stats.count == 1000
            assert stats.mean > 0
            assert stats.std_dev > 0
            assert len(stats.confidence_interval) == 2
            assert 50 in stats.latency_percentiles

    def test_performance_engine_overhead(self, engine):
        """Test that statistical analysis overhead is minimal."""
        # Measure overhead of statistical analysis itself
        num_measurements = 1000

        start_time = time.perf_counter()
        for i in range(num_measurements):
            engine.record_measurement("overhead_test", random.uniform(1, 10))
        end_time = time.perf_counter()

        total_time_ms = (end_time - start_time) * 1000
        avg_time_per_measurement = total_time_ms / num_measurements

        # Analysis overhead should be < 0.1ms per measurement
        assert (
            avg_time_per_measurement < 0.1
        ), f"Statistical analysis overhead too high: {avg_time_per_measurement:.3f}ms"


class TestHighPerformanceCache:
    """Test high-performance cache implementation."""

    def test_basic_cache_operations(self):
        """Test basic cache get/put operations."""
        cache = HighPerformanceCache(max_size=100, default_ttl=1.0)

        # Test put/get
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

        # Test miss
        assert cache.get("nonexistent") is None

        # Test hit rate calculation
        cache.get("key1")  # Another hit
        cache.get("key1")  # Another hit
        cache.get("missing")  # Miss

        hit_rate = cache.get_hit_rate()
        assert hit_rate == 3 / 4  # 3 hits, 1 miss

    def test_cache_expiration(self):
        """Test cache TTL functionality."""
        cache = HighPerformanceCache(max_size=100, default_ttl=0.1)  # 100ms TTL

        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(0.15)

        # Should be expired
        assert cache.get("key1") is None

    def test_cache_eviction(self):
        """Test LRU eviction policy."""
        cache = HighPerformanceCache(max_size=3, default_ttl=10.0)

        # Fill cache
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")

        # Access key1 to make it recently used
        cache.get("key1")

        # Add key4, should evict key2 (least recently used)
        cache.put("key4", "value4")

        assert cache.get("key1") == "value1"  # Should still exist
        assert cache.get("key2") is None  # Should be evicted
        assert cache.get("key3") == "value3"  # Should still exist
        assert cache.get("key4") == "value4"  # Should exist


class TestOptimizedProtocol:
    """Test optimized TCP protocol implementation."""

    @pytest.fixture
    def optimized_protocol(self):
        """Create optimized protocol instance."""
        return OptimizedToolCapabilityProtocol(
            enable_optimization=True,
            optimization_backend=OptimizationBackend.CPU_BASIC,
            cache_size=1000,
        )

    @pytest.fixture
    def sample_descriptors(self):
        """Create sample capability descriptors for testing."""
        descriptors = []
        for i in range(10):
            perf_metrics = PerformanceMetrics(
                avg_processing_time_ms=random.randint(100, 1000),
                memory_usage_mb=random.randint(10, 100),
                max_file_size_mb=random.randint(1, 1000),
            )

            desc = CapabilityDescriptor(
                name=f"test_tool_{i}",
                version="1.0.0",
                description=f"Test tool {i}",
                performance=perf_metrics,
            )
            descriptors.append(desc)

        return descriptors

    def test_optimized_tool_selection(self, optimized_protocol, sample_descriptors):
        """Test optimized tool selection with caching."""
        # First selection (cache miss)
        start_time = time.perf_counter()
        result1 = optimized_protocol.select_optimal_tool(sample_descriptors, "speed")
        first_time = time.perf_counter() - start_time

        # Second selection (cache hit)
        start_time = time.perf_counter()
        result2 = optimized_protocol.select_optimal_tool(sample_descriptors, "speed")
        second_time = time.perf_counter() - start_time

        # Results should be identical
        assert result1.name == result2.name

        # Second call should be faster (cache hit)
        assert (
            second_time < first_time
        ), f"Cache hit not faster: {second_time:.6f}s vs {first_time:.6f}s"

        # Validate selection correctness
        assert result1 is not None
        fastest_tool = min(
            sample_descriptors, key=lambda t: t.performance.avg_processing_time_ms
        )
        assert result1.name == fastest_tool.name

    def test_batch_binary_generation(self, optimized_protocol, sample_descriptors):
        """Test batch binary generation with caching."""
        # Generate binaries
        binaries = optimized_protocol.batch_generate_binary(sample_descriptors)

        # Validate results
        assert len(binaries) == len(sample_descriptors)
        for binary_data in binaries:
            assert isinstance(binary_data, bytes)
            assert len(binary_data) > 0

        # Test caching - second call should be faster
        start_time = time.perf_counter()
        binaries2 = optimized_protocol.batch_generate_binary(sample_descriptors)
        cached_time = time.perf_counter() - start_time

        # Results should be identical
        assert binaries == binaries2

        # Should be very fast due to caching
        assert (
            cached_time < 0.01
        ), f"Cached binary generation too slow: {cached_time:.6f}s"

    def test_capability_query_optimization(
        self, optimized_protocol, sample_descriptors
    ):
        """Test optimized capability queries."""
        # Define test capabilities
        capabilities = [
            "flag:SUPPORTS_FILES",
            "flag:BATCH_PROCESSING",
            "format:json",
            "command:execute",
        ]

        # Perform batch capability query
        results = optimized_protocol.optimized_capability_query(
            sample_descriptors, capabilities
        )

        # Validate results structure
        assert len(results) == len(sample_descriptors)
        for tool_name, tool_results in results.items():
            assert len(tool_results) == len(capabilities)
            for capability in capabilities:
                assert capability in tool_results
                assert isinstance(tool_results[capability], bool)

    def test_performance_monitoring(self, optimized_protocol, sample_descriptors):
        """Test performance monitoring and reporting."""
        # Perform various operations to generate metrics
        for _ in range(5):
            optimized_protocol.select_optimal_tool(sample_descriptors, "speed")
            optimized_protocol.batch_generate_binary(sample_descriptors[:3])

        # Get optimization report
        report = optimized_protocol.get_optimization_report()

        # Validate report structure
        assert report["optimization_enabled"] is True
        assert "statistical_engine" in report
        assert "cache_performance" in report

        # Validate cache performance
        cache_perf = report["cache_performance"]
        assert "hit_rate" in cache_perf
        assert "hit_count" in cache_perf
        assert cache_perf["hit_rate"] >= 0.0
        assert cache_perf["hit_count"] > 0  # Should have some cache hits


class TestMathematicalCorrectness:
    """Test mathematical correctness of statistical operations."""

    def test_effect_size_calculation(self):
        """Test Cohen's d effect size calculation."""
        engine = StatisticalPerformanceEngine()

        # Create two groups with known effect size
        group1_data = [10, 12, 14, 16, 18]  # Mean = 14
        group2_data = [20, 22, 24, 26, 28]  # Mean = 24, diff = 10

        # Standard deviation for both groups ≈ 3.16
        # Expected Cohen's d ≈ 10 / 3.16 ≈ 3.16 (large effect)

        stats1 = RunningStatistics()
        stats2 = RunningStatistics()

        for val in group1_data:
            stats1.update(val)
        for val in group2_data:
            stats2.update(val)

        effect_size = engine._cohens_d(stats1, stats2)

        # Should indicate large effect (> 0.8)
        assert effect_size > 2.0, f"Effect size calculation error: {effect_size}"
        assert effect_size < 4.0, f"Effect size too large: {effect_size}"

    def test_statistical_significance(self):
        """Test statistical significance testing."""
        engine = StatisticalPerformanceEngine()

        # Create baseline
        baseline_data = [100] * 100  # Constant baseline
        engine.establish_baseline("test_significance", baseline_data)

        # Test significantly different value
        result = engine.record_measurement("test_significance", 150.0)

        # Should detect significant difference
        p_value = result["baseline_comparison"]["p_value"]
        assert p_value is not None
        assert p_value < 0.05, f"Should detect significant difference: p={p_value}"

    def test_confidence_interval_coverage(self):
        """Test confidence interval coverage probability."""
        # Generate multiple samples and check CI coverage
        true_mean = 100.0
        true_std = 15.0
        confidence_level = 0.95

        coverage_count = 0
        num_trials = 1000

        np.random.seed(789)

        for _ in range(num_trials):
            # Generate sample
            sample = np.random.normal(true_mean, true_std, 30)

            # Calculate CI
            stats = RunningStatistics()
            for value in sample:
                stats.update(value)

            ci = stats.confidence_interval(confidence_level)

            # Check if true mean is in CI
            if ci[0] <= true_mean <= ci[1]:
                coverage_count += 1

        coverage_rate = coverage_count / num_trials

        # Should be close to confidence level (within reasonable margin)
        expected_rate = confidence_level
        margin = 0.05  # Allow 5% deviation

        assert (
            abs(coverage_rate - expected_rate) < margin
        ), f"CI coverage rate {coverage_rate:.3f} not close to expected {expected_rate:.3f}"


class TestPerformanceBenchmarks:
    """Benchmark tests to establish performance baselines."""

    def test_statistical_analysis_performance(self):
        """Benchmark statistical analysis performance."""
        engine = StatisticalPerformanceEngine()

        # Benchmark single measurements
        num_measurements = 10000
        measurement_times = []

        for i in range(num_measurements):
            start = time.perf_counter()
            engine.record_measurement("benchmark", random.uniform(1, 100))
            end = time.perf_counter()
            measurement_times.append((end - start) * 1000)  # Convert to ms

        avg_time = np.mean(measurement_times)
        p99_time = np.percentile(measurement_times, 99)

        # Performance targets
        assert avg_time < 0.1, f"Average measurement time too high: {avg_time:.3f}ms"
        assert p99_time < 0.5, f"99th percentile time too high: {p99_time:.3f}ms"

        print(f"Statistical analysis performance:")
        print(f"  Average time: {avg_time:.3f}ms")
        print(f"  99th percentile: {p99_time:.3f}ms")
        print(f"  Throughput: {1000/avg_time:.0f} measurements/second")

    def test_cache_performance(self):
        """Benchmark cache performance."""
        cache = HighPerformanceCache(max_size=10000)

        # Benchmark cache operations
        num_ops = 100000

        # Fill cache
        start = time.perf_counter()
        for i in range(10000):
            cache.put(f"key_{i}", f"value_{i}")
        put_time = time.perf_counter() - start

        # Benchmark gets (mix of hits and misses)
        start = time.perf_counter()
        for i in range(num_ops):
            key = f"key_{i % 15000}"  # Mix of hits (0-9999) and misses (10000-14999)
            cache.get(key)
        get_time = time.perf_counter() - start

        avg_put_time = (put_time / 10000) * 1000000  # microseconds
        avg_get_time = (get_time / num_ops) * 1000000  # microseconds

        # Performance targets
        assert avg_put_time < 10, f"Cache put too slow: {avg_put_time:.2f}μs"
        assert avg_get_time < 5, f"Cache get too slow: {avg_get_time:.2f}μs"

        print(f"Cache performance:")
        print(f"  Average put time: {avg_put_time:.2f}μs")
        print(f"  Average get time: {avg_get_time:.2f}μs")
        print(f"  Hit rate: {cache.get_hit_rate():.3f}")


if __name__ == "__main__":
    # Run performance benchmarks
    print("🔬 Running Statistical Performance Optimization Tests")
    print("=" * 60)

    benchmark_tests = TestPerformanceBenchmarks()

    print("\n📊 Statistical Analysis Performance:")
    benchmark_tests.test_statistical_analysis_performance()

    print("\n💾 Cache Performance:")
    benchmark_tests.test_cache_performance()

    print("\n✅ All benchmarks completed successfully!")
    print("\n🎯 Ready for Yuki's hardware acceleration integration!")
