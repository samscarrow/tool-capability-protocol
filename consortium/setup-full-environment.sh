#!/bin/bash
# TCP Research Consortium - Complete Environment Setup
# Ensures all researchers have necessary dependencies

set -euo pipefail

echo "🔬 TCP Research Consortium - Full Environment Setup"
echo "=================================================="

# Get absolute path to project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📁 Project root: $PROJECT_ROOT"

# Check if virtual environment exists
if [[ -d "$PROJECT_ROOT/tcp_env" ]]; then
    echo "✅ Found TCP virtual environment"
    
    # Activate the environment
    echo "🔄 Activating virtual environment..."
    source "$PROJECT_ROOT/tcp_env/bin/activate"
    
    # Install all research dependencies
    echo "📦 Installing comprehensive research dependencies..."
    pip install -r "$PROJECT_ROOT/consortium/requirements.txt"
    
    echo "✅ All dependencies installed successfully!"
    
else
    echo "❌ TCP virtual environment not found!"
    echo "🔧 Creating virtual environment..."
    
    cd "$PROJECT_ROOT"
    python -m venv tcp_env
    source tcp_env/bin/activate
    pip install --upgrade pip
    pip install -r consortium/requirements.txt
    
    echo "✅ Virtual environment created with all dependencies"
fi

# Verify key packages for each researcher
echo -e "\n🧪 Verifying researcher-specific packages..."

python -c "
import sys
print(f'✅ Python: {sys.version.split()[0]}')

# Elena's packages (behavioral analysis)
try:
    import numpy, scipy, pandas, sklearn, matplotlib, seaborn
    print('✅ Elena (behavioral): numpy, scipy, pandas, sklearn, matplotlib, seaborn')
except ImportError as e:
    print(f'❌ Elena packages: {e}')

# Marcus's packages (network analysis)
try:
    import networkx, igraph
    print('✅ Marcus (networks): networkx, igraph')
except ImportError as e:
    print(f'❌ Marcus packages: {e}')

# Yuki's packages (performance)
try:
    import numba
    print('✅ Yuki (performance): numba')
except ImportError as e:
    print(f'❌ Yuki packages: {e}')

# Aria's packages (security)
try:
    import cryptography
    print('✅ Aria (security): cryptography')
except ImportError as e:
    print(f'❌ Aria packages: {e}')

# Sam's packages (system)
try:
    import psutil
    print('✅ Sam (system): psutil')
except ImportError as e:
    print(f'❌ Sam packages: {e}')

# TCP modules
try:
    sys.path.append('$PROJECT_ROOT')
    from tcp.core import protocol
    print('✅ TCP modules: accessible')
except ImportError as e:
    print(f'❌ TCP modules: {e}')
"

echo -e "\n🎯 Environment Setup Complete!"
echo "📋 All researchers now have access to their required packages"
echo "💡 Environment variables:"
echo "   export PYTHONPATH=\$PYTHONPATH:$PROJECT_ROOT"
echo "   source $PROJECT_ROOT/tcp_env/bin/activate"

echo -e "\n✅ TCP Research Consortium environment ready for all researchers!"