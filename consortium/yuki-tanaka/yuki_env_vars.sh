#!/bin/bash
# Yuki's Performance Environment Variables

# Enable NumPy optimizations
export OMP_NUM_THREADS=$(nproc)
export OPENBLAS_NUM_THREADS=$(nproc)
export MKL_NUM_THREADS=$(nproc)
export VECLIB_MAXIMUM_THREADS=$(nproc)
export NUMEXPR_NUM_THREADS=$(nproc)

# Python optimizations
export PYTHONOPTIMIZE=2  # Remove assertions and __debug__ code
export PYTHONDONTWRITEBYTECODE=1  # Don't create .pyc files

# Project paths
export PROJECT_ROOT="/Users/sam/dev/ai-ml/experiments/tool-capability-protocol"
export YUKI_WORKSPACE="/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/yuki-tanaka"
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH:-}"

# Performance tools
alias profile='python -m line_profiler'
alias memprofile='python -m memory_profiler'
alias benchmark='python -m pytest --benchmark-only'
alias pyspy='py-spy record -o profile.svg -- python'

echo "⚡ Yuki's performance environment loaded"
echo "   • NumPy threads: $OMP_NUM_THREADS"
echo "   • Python optimizations: ENABLED"
echo "   • Profiling tools: profile, memprofile, benchmark, pyspy"
