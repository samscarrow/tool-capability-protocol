"""Test Yuki's performance environment setup"""
import time
import numpy as np
from numba import jit
import multiprocessing

print("⚡ Testing Yuki's Performance Environment")
print("=" * 50)

# Test NumPy with threading
print(f"✅ NumPy version: {np.__version__}")
print(f"✅ CPU cores available: {multiprocessing.cpu_count()}")

# Test Numba JIT compilation
@jit(nopython=True)
def fast_computation(n):
    result = 0.0
    for i in range(n):
        result += i ** 2
    return result

# Warm up JIT
fast_computation(10)

# Benchmark
start = time.perf_counter_ns()
result = fast_computation(1_000_000)
end = time.perf_counter_ns()

print(f"✅ Numba JIT test: {(end - start) / 1000:.2f} microseconds")
print(f"✅ All performance libraries loaded successfully!")

# Test TCP imports
try:
    import sys
    sys.path.insert(0, '/Users/sam/dev/ai-ml/experiments/tool-capability-protocol')
    from tcp.core import protocol
    print("✅ TCP modules accessible")
except ImportError:
    print("⚠️  TCP modules not yet accessible - run from PROJECT_ROOT")