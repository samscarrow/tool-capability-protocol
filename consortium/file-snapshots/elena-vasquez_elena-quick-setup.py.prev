#!/usr/bin/env python3
"""
Dr. Elena Vasquez - Quick Python Environment Setup
Run this from elena-vasquez directory to configure your research environment
"""

import sys
import os
import json
from pathlib import Path

print("🔬 Dr. Elena Vasquez - Python Environment Setup")
print("=" * 50)

# Get current directory and project root
current_dir = Path.cwd()
project_root = current_dir.parent.parent

print(f"📁 Current directory: {current_dir}")
print(f"📁 Project root: {project_root}")

# Add project root to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    print("✅ Added project root to Python path")

# Verify TCP modules are accessible
try:
    from tcp.core import protocol, descriptors
    print("✅ TCP modules accessible")
except ImportError as e:
    print(f"❌ TCP modules error: {e}")

# Check for simulation data
sim_files = list(project_root.glob("tcp_stealth_simulation_results_*.json"))
print(f"\n📊 Found {len(sim_files)} simulation result files:")
for f in sim_files:
    print(f"   • {f.name}")

# Test data loading
if sim_files:
    try:
        with open(sim_files[0], 'r') as f:
            data = json.load(f)
        print(f"✅ Successfully loaded: {sim_files[0].name}")
        print(f"   • Contains: {len(data)} top-level keys")
        if 'analysis' in data:
            print(f"   • Detection metrics available: {list(data['analysis'].keys())}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")

# Check for other key resources
key_files = [
    "tcp_stealth_compromise_simulator.py",
    "performance_benchmark.py", 
    "focused_bcachefs_analysis.py"
]

print(f"\n🔧 Key research files available:")
for file in key_files:
    file_path = project_root / file
    if file_path.exists():
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} (not found)")

print(f"\n🎯 Elena's Research Environment Ready!")
print(f"💡 You can now import and analyze:")
print(f"   import json")
print(f"   with open('../../tcp_stealth_simulation_results_*.json') as f:")
print(f"       data = json.load(f)")
print(f"   from tcp.core import protocol, descriptors")

print(f"\n📈 Start your behavioral analysis!")