#!/bin/bash
# Dr. Yuki Tanaka - Python Environment Setup
# High-performance Python environment with optimization libraries

set -euo pipefail

echo "⚡ Setting up Yuki's High-Performance Python Environment"
echo "======================================================"

# Get absolute paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
YUKI_WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create virtual environment if it doesn't exist
if [[ ! -d "$YUKI_WORKSPACE/yuki_env" ]]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$YUKI_WORKSPACE/yuki_env"
    echo "✅ Virtual environment created at: $YUKI_WORKSPACE/yuki_env"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source "$YUKI_WORKSPACE/yuki_env/bin/activate"
echo "✅ Virtual environment activated"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install performance-focused dependencies
echo "📦 Installing high-performance Python libraries..."
cat > "$YUKI_WORKSPACE/requirements-performance.txt" << EOF
# Core Scientific Computing (Performance Optimized)
numpy>=1.24.0  # Vectorized operations
scipy>=1.10.0  # Scientific algorithms
numba>=0.57.0  # JIT compilation for Python
cython>=3.0.0  # C-extensions for Python

# Profiling and Performance Analysis
line_profiler>=4.0.0  # Line-by-line profiling
memory_profiler>=0.60.0  # Memory usage profiling
py-spy>=0.3.14  # Sampling profiler
scalene>=1.5.0  # High-performance CPU+GPU+memory profiler

# Parallel Processing
multiprocessing-logging>=0.3.4
joblib>=1.3.0  # Parallel computing
dask>=2023.5.0  # Parallel computing with task scheduling
ray>=2.5.0  # Distributed computing

# Data Science (Elena's tools)
pandas>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0

# TCP Project Dependencies
pydantic>=2.0.0
click>=8.1.0
rich>=13.0.0
httpx>=0.24.0

# Testing and Benchmarking
pytest>=7.3.0
pytest-benchmark>=4.0.0  # Benchmarking plugin
asv>=0.6.0  # Airspeed Velocity for benchmarks
EOF

pip install -r "$YUKI_WORKSPACE/requirements-performance.txt"

# Set up environment variables for performance
cat > "$YUKI_WORKSPACE/yuki_env_vars.sh" << EOF
#!/bin/bash
# Yuki's Performance Environment Variables

# Enable NumPy optimizations
export OMP_NUM_THREADS=\$(nproc)
export OPENBLAS_NUM_THREADS=\$(nproc)
export MKL_NUM_THREADS=\$(nproc)
export VECLIB_MAXIMUM_THREADS=\$(nproc)
export NUMEXPR_NUM_THREADS=\$(nproc)

# Python optimizations
export PYTHONOPTIMIZE=2  # Remove assertions and __debug__ code
export PYTHONDONTWRITEBYTECODE=1  # Don't create .pyc files

# Project paths
export PROJECT_ROOT="$PROJECT_ROOT"
export YUKI_WORKSPACE="$YUKI_WORKSPACE"
export PYTHONPATH="\$PROJECT_ROOT:\$PYTHONPATH"

# Performance tools
alias profile='python -m line_profiler'
alias memprofile='python -m memory_profiler'
alias benchmark='python -m pytest --benchmark-only'
alias pyspy='py-spy record -o profile.svg -- python'

echo "⚡ Yuki's performance environment loaded"
echo "   • NumPy threads: \$OMP_NUM_THREADS"
echo "   • Python optimizations: ENABLED"
echo "   • Profiling tools: profile, memprofile, benchmark, pyspy"
EOF

# Source the environment variables
source "$YUKI_WORKSPACE/yuki_env_vars.sh"

# Create quick test script
cat > "$YUKI_WORKSPACE/test_performance_env.py" << 'EOF'
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
    sys.path.insert(0, PROJECT_ROOT)
    from tcp.core import protocol
    print("✅ TCP modules accessible")
except ImportError:
    print("⚠️  TCP modules not yet accessible - run from PROJECT_ROOT")
EOF

# Replace PROJECT_ROOT in test script
sed -i "" "s|PROJECT_ROOT|'$PROJECT_ROOT'|g" "$YUKI_WORKSPACE/test_performance_env.py"

echo -e "\n🚀 Yuki's Performance Environment Setup Complete!"
echo "===================================================="
echo ""
echo "📋 Quick Start Commands:"
echo "   1. source $YUKI_WORKSPACE/yuki_env/bin/activate"
echo "   2. source $YUKI_WORKSPACE/yuki_env_vars.sh"
echo "   3. python $YUKI_WORKSPACE/test_performance_env.py"
echo ""
echo "🔧 Performance Tools Available:"
echo "   • profile script.py - Line-by-line profiling"
echo "   • memprofile script.py - Memory profiling"
echo "   • pyspy script.py - Sampling profiler with flamegraphs"
echo "   • benchmark - Run performance benchmarks"
echo ""
echo "⚡ Remember: Speed is security at internet scale!"