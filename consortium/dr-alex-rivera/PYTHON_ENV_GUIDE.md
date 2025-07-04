# Python Environment Guide for Dr. Alex Rivera

## Quick Start

Your Python environment is now set up with all quality and testing tools!

### 1. Activate Your Environment
```bash
source /Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/dr-alex-rivera/dr-alex-rivera_env/bin/activate
```

### 2. Verify Installation
```bash
# Check Python and key tools
python --version  # Should be 3.11+
pytest --version
flake8 --version
mypy --version
prospector --version
```

### 3. Key Quality Tools Available

#### Testing & Coverage
- **pytest**: Core testing framework
- **pytest-cov**: Coverage analysis (target: 95%)
- **pytest-mock**: Mocking capabilities
- **pytest-xdist**: Parallel test execution
- **hypothesis**: Property-based testing

#### Code Quality
- **flake8**: Style guide enforcement
- **black**: Code formatting (88 char lines)
- **isort**: Import sorting
- **mypy**: Static type checking
- **prospector**: Comprehensive analysis
- **radon**: Complexity metrics
- **bandit**: Security scanning

#### Documentation
- **sphinx**: Documentation generation
- **pydocstyle**: Docstring conventions

#### CI/CD
- **pre-commit**: Git hooks
- **tox**: Multi-environment testing
- **safety**: Dependency vulnerability scanning

## Your First Quality Analysis

### 1. Run Coverage Analysis
```bash
# From project root
cd /Users/sam/dev/ai-ml/experiments/tool-capability-protocol
pytest --cov=tcp --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html
```

### 2. Code Quality Check
```bash
# Comprehensive quality analysis
prospector tcp --strictness veryhigh

# Individual tools
flake8 tcp --statistics
mypy tcp --strict
bandit -r tcp
```

### 3. Check Researcher Code
```bash
# Elena's behavioral analysis
pytest consortium/elena-vasquez/behavioral_analysis_toolkit.py --cov

# Marcus's distributed systems
prospector consortium/marcus-chen/research-session-*/

# Yuki's performance code
mypy consortium/yuki-tanaka/tcp_performance_profiler.py --strict
```

## Key Quality Metrics to Track

### Current Gaps (from your start-here.md)
- Missing `structlog` dependency ✅ FIXED in base-requirements.txt
- No standardized performance benchmarking
- Elena's O(n²) complexity without scale tests
- Marcus's 3,247 lines with unknown coverage
- Yuki's optimizations without correctness tests

### Your Quality Dashboard Commands
```bash
# Generate quality report
python -c "
import subprocess
import json

results = {
    'tcp_coverage': subprocess.getoutput('pytest --cov=tcp --cov-report=json --cov-report-file=/dev/stdout | tail -1'),
    'code_quality': subprocess.getoutput('flake8 tcp --count --quiet'),
    'type_coverage': subprocess.getoutput('mypy tcp --strict 2>&1 | grep \"Success:\" || echo \"Errors found\"'),
    'security_issues': subprocess.getoutput('bandit -r tcp -f json 2>/dev/null | grep \"issue_severity\" | wc -l')
}
print(json.dumps(results, indent=2))
"
```

## Integration Testing Setup

### Create Your First Integration Test
```python
# consortium/dr-alex-rivera/integration_tests/test_elena_marcus.py
import pytest
from tcp.core import protocol
from consortium.elena_vasquez.behavioral_analysis_toolkit import BehavioralAnalyzer
from consortium.marcus_chen.consensus_free_detection import ConsensusDetector

def test_behavioral_detection_scales():
    """Ensure Elena's detection works with Marcus's network"""
    analyzer = BehavioralAnalyzer()
    detector = ConsensusDetector()
    
    # Test scaling from 10 to 1000 agents
    for agent_count in [10, 100, 1000]:
        behavioral_scores = analyzer.analyze_agents(agent_count)
        consensus = detector.process_scores(behavioral_scores)
        assert consensus.is_valid()
```

## Your Environment Variables
```bash
# Already set when environment is activated
export PROJECT_ROOT="/Users/sam/dev/ai-ml/experiments/tool-capability-protocol"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Quality-specific settings
export PYTEST_OPTS="--strict-markers --tb=short"
export MYPY_OPTS="--strict --show-error-codes"
```

## Common Quality Commands

```bash
# Format all code
black tcp consortium --line-length 88
isort tcp consortium

# Run all quality checks
./scripts/quality-check.sh  # You should create this!

# Generate documentation
sphinx-build -b html docs docs/_build

# Security scan with details
bandit -r tcp -ll -f txt
```

## Next Steps

1. **Baseline Assessment**: Run coverage on entire TCP codebase
2. **Create Quality Scripts**: Automate common quality checks
3. **Setup CI/CD**: GitHub Actions for automated quality gates
4. **Integration Tests**: Test researcher code interactions
5. **Performance Benchmarks**: Validate Yuki's optimizations

Remember: Your role is to ensure every line of code is production-ready. The researchers create breakthroughs - you make them bulletproof!

---
*Environment Location*: `/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium/dr-alex-rivera/dr-alex-rivera_env/`
*Python Version*: 3.11
*Key Focus*: 95% coverage, zero security issues, microsecond performance validation