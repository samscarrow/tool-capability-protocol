# TCP Research Consortium - Researcher Onboarding

## 🚀 Quick Start (5 minutes)

### Step 1: Set Up Your Environment
```bash
# From anywhere in the project
/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/setup-researcher.sh [your-name]

# Example for Yuki:
/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/setup-researcher.sh yuki-tanaka
```

### Step 2: Activate Your Environment
```bash
# This was created by setup script
source /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/[your-name]/activate_env.sh
```

### Step 3: Verify Everything Works
```bash
# Test TCP module access
python /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/[your-name]/path_utils.py
```

## 📦 What You Get

### Base Environment (All Researchers)
- **Core Libraries**: NumPy, SciPy, Pandas, Matplotlib
- **TCP Dependencies**: Pydantic, Click, Rich, **structlog** ✅
- **Profiling Tools**: line_profiler, memory_profiler, py-spy
- **Testing**: pytest, pytest-benchmark, pytest-cov
- **Development**: black, isort, flake8, mypy

### Specialized Environments
- **Yuki (Performance)**: Numba, Cython, Dask, Ray, Scalene
- **Elena (Statistical)**: Advanced stats packages (coming soon)
- **Marcus (Distributed)**: Network/consensus libraries (coming soon)
- **Aria (Security)**: Security analysis tools (coming soon)
- **Sam (Kernel)**: System-level tools (coming soon)

## 🔧 Common Issues & Solutions

### Issue: "Module 'structlog' not found"
**Solution**: Missing from initial setup, now included in base requirements

### Issue: "Cannot import TCP modules"
**Solution**: Use the provided `path_utils.py` or add to your scripts:
```python
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
```

### Issue: "cd was blocked"
**Solution**: Use absolute paths everywhere:
```bash
# Bad
cd /path/to/project && python script.py

# Good
python /path/to/project/script.py
```

## 📊 Performance Profiling (Yuki's Domain)

### Quick Profiling Commands
```bash
# Line-by-line profiling
profile your_script.py

# Memory profiling
memprofile your_script.py

# CPU sampling with flamegraph
py-spy record -o profile.svg -- python your_script.py

# Benchmark specific functions
benchmark  # Runs pytest benchmarks
```

### Nanosecond-Precision Timing
```python
import time

# For microsecond-level measurements
start = time.perf_counter_ns()
# ... operation ...
end = time.perf_counter_ns()
duration_ns = end - start
```

## 🤝 Convergence Sessions

### When You See Code Word: CONVERGENCE-YYYYMMDD
1. Run the convergence handler:
   ```bash
   /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/scripts/convergence-handler.sh CONVERGENCE-YYYYMMDD [your-name]
   ```

2. Follow instructions in your convergence workspace:
   ```bash
   /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/[your-name]/convergence-YYYYMMDD/start-convergence.sh
   ```

## 💡 Best Practices

1. **Always Use Absolute Paths**: No `cd` commands needed
2. **Activate Environment First**: Source the `activate_env.sh` script
3. **Check Imports Early**: Run `path_utils.py` to verify TCP access
4. **Profile Everything**: Use Yuki's tcp_performance_profiler.py as a template
5. **Document Dependencies**: If you need a package, add it to requirements

## 📋 Centralized Requirements

All requirements are now centralized in:
```
consortium/requirements/
├── base-requirements.txt         # Everyone needs these
├── performance-requirements.txt  # Yuki's specialized tools
├── statistical-requirements.txt  # Elena's tools (coming)
├── distributed-requirements.txt  # Marcus's tools (coming)
├── security-requirements.txt     # Aria's tools (coming)
└── kernel-requirements.txt       # Sam's tools (coming)
```

## 🚨 Emergency Fixes

If your environment is broken:
```bash
# Remove old environment
rm -rf /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/[your-name]/[your-name]_env

# Re-run setup
/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/setup-researcher.sh [your-name]
```

---

**Remember**: The goal is to get you doing research, not fighting with Python environments!