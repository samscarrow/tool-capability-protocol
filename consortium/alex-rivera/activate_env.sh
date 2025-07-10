#!/bin/bash
# Quick activation script for dr-alex-rivera

# Activate virtual environment
source "/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/dr-alex-rivera/dr-alex-rivera_env/bin/activate"

# Set environment variables
export PROJECT_ROOT="/Users/sam/dev/ai-ml/experiments/tool-capability-protocol"
export RESEARCHER_DIR="/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/dr-alex-rivera"
export PYTHONPATH="/Users/sam/dev/ai-ml/experiments/tool-capability-protocol:${PYTHONPATH:-}"

# Performance optimizations (for all researchers)
export OMP_NUM_THREADS=$(nproc)
export PYTHONOPTIMIZE=2
export PYTHONDONTWRITEBYTECODE=1

# Aliases for common tasks
alias profile='python -m line_profiler'
alias memprofile='python -m memory_profiler'
alias benchmark='python -m pytest --benchmark-only'
alias test='python -m pytest'
alias format='black . && isort .'

echo "✅ dr-alex-rivera environment activated"
echo "📁 Project root: $PROJECT_ROOT"
echo "🐍 Python: $(which python)"
echo "📦 Key tools: profile, memprofile, benchmark, test, format"
