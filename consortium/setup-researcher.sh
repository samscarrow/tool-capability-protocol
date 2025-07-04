#!/bin/bash
# TCP Research Consortium - Universal Researcher Setup
# One script to properly set up ANY researcher's environment

set -euo pipefail

echo "🚀 TCP Research Consortium - Researcher Setup"
echo "============================================="

# Get researcher name from argument
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <researcher-name>"
    echo "Example: $0 elena-vasquez"
    echo "Available researchers:"
    echo "  - elena-vasquez"
    echo "  - marcus-chen"
    echo "  - yuki-tanaka"
    echo "  - aria-blackwood"
    echo "  - sam-mitchell"
    exit 1
fi

RESEARCHER="$1"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESEARCHER_DIR="$PROJECT_ROOT/consortium/$RESEARCHER"
REQUIREMENTS_DIR="$PROJECT_ROOT/consortium/requirements"

# Validate researcher exists
if [[ ! -d "$RESEARCHER_DIR" ]]; then
    echo "❌ Researcher directory not found: $RESEARCHER_DIR"
    exit 1
fi

echo "📁 Setting up environment for: $RESEARCHER"
echo "📍 Project root: $PROJECT_ROOT"
echo "📍 Researcher directory: $RESEARCHER_DIR"

# Create virtual environment
VENV_DIR="$RESEARCHER_DIR/${RESEARCHER}_env"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created: $VENV_DIR"
else
    echo "✅ Virtual environment exists: $VENV_DIR"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install base requirements
echo "📦 Installing base requirements..."
pip install -r "$REQUIREMENTS_DIR/base-requirements.txt"

# Install researcher-specific requirements
case "$RESEARCHER" in
    "yuki-tanaka")
        echo "⚡ Installing performance-specific requirements for Yuki..."
        pip install -r "$REQUIREMENTS_DIR/performance-requirements.txt"
        ;;
    "elena-vasquez")
        echo "🧠 Installing statistical analysis requirements for Elena..."
        pip install -r "$REQUIREMENTS_DIR/statistical-requirements.txt" 2>/dev/null || echo "⚠️  No statistical-specific requirements yet"
        ;;
    "marcus-chen")
        echo "🌐 Installing distributed systems requirements for Marcus..."
        pip install -r "$REQUIREMENTS_DIR/distributed-requirements.txt" 2>/dev/null || echo "⚠️  No distributed-specific requirements yet"
        ;;
    "aria-blackwood")
        echo "🔒 Installing security analysis requirements for Aria..."
        pip install -r "$REQUIREMENTS_DIR/security-requirements.txt" 2>/dev/null || echo "⚠️  No security-specific requirements yet"
        ;;
    "sam-mitchell")
        echo "🖥️  Installing kernel development requirements for Sam..."
        pip install -r "$REQUIREMENTS_DIR/kernel-requirements.txt" 2>/dev/null || echo "⚠️  No kernel-specific requirements yet"
        ;;
esac

# Create activation script with paths
ACTIVATE_SCRIPT="$RESEARCHER_DIR/activate_env.sh"
cat > "$ACTIVATE_SCRIPT" << EOF
#!/bin/bash
# Quick activation script for $RESEARCHER

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Set environment variables
export PROJECT_ROOT="$PROJECT_ROOT"
export RESEARCHER_DIR="$RESEARCHER_DIR"
export PYTHONPATH="$PROJECT_ROOT:\${PYTHONPATH:-}"

# Performance optimizations (for all researchers)
export OMP_NUM_THREADS=\$(nproc)
export PYTHONOPTIMIZE=2
export PYTHONDONTWRITEBYTECODE=1

# Aliases for common tasks
alias profile='python -m line_profiler'
alias memprofile='python -m memory_profiler'
alias benchmark='python -m pytest --benchmark-only'
alias test='python -m pytest'
alias format='black . && isort .'

echo "✅ $RESEARCHER environment activated"
echo "📁 Project root: \$PROJECT_ROOT"
echo "🐍 Python: \$(which python)"
echo "📦 Key tools: profile, memprofile, benchmark, test, format"
EOF

chmod +x "$ACTIVATE_SCRIPT"

# Create path utilities
PATH_UTILS="$RESEARCHER_DIR/path_utils.py"
cat > "$PATH_UTILS" << 'EOF'
"""Path utilities for TCP Research Consortium"""
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Common paths
CONSORTIUM_DIR = PROJECT_ROOT / "consortium"
RESEARCHER_DIR = Path(__file__).parent
CONVERGENCE_DIR = CONSORTIUM_DIR / f"convergence-{RESEARCHER_DIR.name}"

# TCP modules should now be importable
try:
    from tcp.core import protocol
    print("✅ TCP modules accessible")
except ImportError:
    print("❌ TCP modules not accessible - check PROJECT_ROOT")
EOF

# Test the setup
echo -e "\n🔬 Testing environment setup..."
python -c "
import sys
print(f'✅ Python: {sys.version.split()[0]}')

try:
    import numpy as np
    print(f'✅ NumPy: {np.__version__}')
except ImportError:
    print('❌ NumPy not installed')

try:
    import structlog
    print('✅ structlog: installed')
except ImportError:
    print('❌ structlog not installed - THIS IS REQUIRED!')

sys.path.insert(0, '$PROJECT_ROOT')
try:
    from tcp.core import protocol
    print('✅ TCP modules: accessible')
except ImportError:
    print('❌ TCP modules: not accessible')
"

echo -e "\n✅ Setup complete for $RESEARCHER!"
echo "===================================="
echo ""
echo "📋 Quick Start:"
echo "   source $ACTIVATE_SCRIPT"
echo ""
echo "🚀 Key Commands:"
echo "   profile script.py         # Line-by-line profiling"
echo "   memprofile script.py      # Memory profiling"
echo "   benchmark                 # Run performance tests"
echo "   python path_utils.py      # Test TCP imports"
echo ""
echo "📁 Your workspace: $RESEARCHER_DIR"
echo "📁 Project root: $PROJECT_ROOT"