#!/usr/bin/env python3
"""
Yuki's Quick Setup - Handles all the environment complexity
"""
import subprocess
import sys
import os

def setup_yuki_environment():
    """One command to rule them all"""
    
    print("⚡ Yuki's Quick Environment Setup")
    print("=" * 50)
    
    # Absolute paths
    YUKI_WORKSPACE = "/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/yuki-tanaka"
    PROJECT_ROOT = "/Users/sam/dev/ai-ml/experiments/tool-capability-protocol"
    
    # Check if we're in the virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("❌ Not in virtual environment!")
        print(f"🔧 Run: source {YUKI_WORKSPACE}/yuki_env/bin/activate")
        return False
    
    # Add project root to Python path
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    
    # Install missing dependencies that the main project needs
    missing_deps = []
    
    # Check for commonly missing dependencies
    try:
        import structlog
    except ImportError:
        missing_deps.append("structlog")
    
    try:
        import pytest_benchmark
    except ImportError:
        missing_deps.append("pytest-benchmark")
        
    if missing_deps:
        print(f"📦 Installing missing dependencies: {', '.join(missing_deps)}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_deps)
    
    # Create a wrapper script for the main performance benchmark
    wrapper_content = f"""#!/usr/bin/env python3
'''Wrapper for main performance benchmark with proper paths'''
import sys
sys.path.insert(0, '{PROJECT_ROOT}')

# Now run the original script
with open('{PROJECT_ROOT}/performance_benchmark.py') as f:
    code = compile(f.read(), 'performance_benchmark.py', 'exec')
    exec(code)
"""
    
    wrapper_path = f"{YUKI_WORKSPACE}/run_performance_benchmark.py"
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_content)
    
    print(f"✅ Created wrapper: {wrapper_path}")
    print(f"✅ Project root added to PYTHONPATH")
    print(f"✅ All dependencies checked")
    
    print("\n🚀 You can now run:")
    print(f"   python {wrapper_path}")
    print("\n⚡ Or for direct profiling:")
    print(f"   pyspy {wrapper_path}")
    
    return True

if __name__ == "__main__":
    setup_yuki_environment()