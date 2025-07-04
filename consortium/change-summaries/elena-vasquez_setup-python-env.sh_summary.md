# setup-python-env.sh - elena-vasquez

**Last Modified**: /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/elena-vasquez/setup-python-env.sh 100000f0000001a ? 1a 4096 4096 242829865 10175072 10175072 414174643 407002880
Unknown
**Size**: 77 lines
**Location**: /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/elena-vasquez/setup-python-env.sh

## Recent Activity
- File updated at /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/elena-vasquez/setup-python-env.sh 100000f0000001a ? 1a 4096 4096 242829865 10175072 10175072 414174643 407002880
Unknown
- Current size: 77 lines

## File Preview (first 20 lines)
```
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
```

## File Preview (last 10 lines)
```
    echo "❌ TCP virtual environment not found!"
    echo "🔧 Creating virtual environment..."
    
    python -m venv tcp_env
    source tcp_env/bin/activate
    pip install numpy matplotlib seaborn
    
    echo "✅ Virtual environment created and configured"
    cd consortium/elena-vasquez/
fi
```
