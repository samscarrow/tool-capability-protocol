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
