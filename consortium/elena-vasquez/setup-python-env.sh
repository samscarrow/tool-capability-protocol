#!/bin/bash
# Dr. Elena Vasquez - Python Environment Setup
# Quick fix for Python imports and environment

echo "🐍 Elena's Python Environment Setup"
echo "===================================="

# Get absolute path to project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "📁 Project root: $PROJECT_ROOT"

# Check if virtual environment exists
if [[ -d "$PROJECT_ROOT/tcp_env" ]]; then
    echo "✅ Found TCP virtual environment"
    
    # Activate the environment
    echo "🔄 Activating virtual environment..."
    source "$PROJECT_ROOT/tcp_env/bin/activate"
    
    # Add project to Python path
    export PYTHONPATH="$PYTHONPATH:$PROJECT_ROOT"
    echo "✅ Added project to Python path: $PROJECT_ROOT"
    
    # Verify key packages
    echo -e "\n📦 Checking available packages..."
    python -c "
import sys
print(f'✅ Python: {sys.version.split()[0]}')

try:
    import numpy as np
    print(f'✅ NumPy: {np.__version__}')
except ImportError:
    print('❌ NumPy not available')

try:
    import matplotlib
    print(f'✅ Matplotlib: {matplotlib.__version__}')
except ImportError:
    print('❌ Matplotlib not available')

try:
    import json
    print('✅ JSON: built-in module')
except ImportError:
    print('❌ JSON not available')

try:
    from tcp.core import protocol
    print('✅ TCP modules: accessible')
except ImportError as e:
    print(f'❌ TCP modules: {e}')
"
    
    echo -e "\n🎯 Ready for Elena's Research!"
    echo "Environment activated and configured."
    echo ""
    echo "💡 To use in your Python session:"
    echo "   import sys"
    echo "   sys.path.append('$PROJECT_ROOT')"
    echo "   import numpy as np"
    echo "   import json"
    echo "   from tcp.core import protocol, descriptors"
    echo ""
    echo "📊 Elena can now access all TCP research data and tools!"
    echo "📁 Stay in current directory: $(pwd)"
    
else
    echo "❌ TCP virtual environment not found!"
    echo "🔧 Creating virtual environment..."
    
    python -m venv tcp_env
    source tcp_env/bin/activate
    pip install numpy matplotlib seaborn
    
    echo "✅ Virtual environment created and configured"
    cd consortium/elena-vasquez/
fi