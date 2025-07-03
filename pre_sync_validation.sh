#!/bin/bash
# pre_sync_validation.sh
# Validation script to run before synchronizing branches

set -e  # Exit on any error

echo "🔍 Pre-synchronization validation..."

# 1. Ensure main branch is stable
echo "📊 Validating main branch stability..."
git checkout main
# Check if core TCP files exist and are importable
if [[ -f "tcp_analyzer.py" ]]; then
    if ! python -c "import sys; sys.path.append('.'); import tcp_analyzer; print('✅ Core TCP stable')" 2>/dev/null; then
        echo "❌ Main branch unstable - aborting sync"
        exit 1
    fi
elif [[ -f "comprehensive_hierarchical_tcp.py" ]]; then
    if ! python -c "import sys; sys.path.append('.'); import comprehensive_hierarchical_tcp; print('✅ Core TCP stable')" 2>/dev/null; then
        echo "❌ Main branch unstable - aborting sync"
        exit 1
    fi
else
    echo "✅ Main branch appears stable (no core TCP files to validate)"
fi

# 2. Ensure linguistic branch is in good state
echo "🧬 Validating linguistic branch stability..."
git checkout linguistic-evolution
# Check if linguistic files exist and are importable
if [[ -f "tcp_linguistic_node.py" ]]; then
    if ! python -c "import sys; sys.path.append('.'); import tcp_linguistic_node; print('✅ Linguistic node stable')" 2>/dev/null; then
        echo "❌ Linguistic branch unstable - fix before sync"
        exit 1
    fi
else
    echo "✅ Linguistic branch appears stable (linguistic files exist)"
fi

# 3. Check for uncommitted changes
echo "📋 Checking for uncommitted changes..."
if ! git diff --quiet; then
    echo "❌ Uncommitted changes - commit or stash before sync"
    git status --porcelain
    exit 1
fi

# 4. Verify we can access both branches
echo "🔗 Verifying branch access..."
if ! git rev-parse --verify main >/dev/null 2>&1; then
    echo "❌ Cannot access main branch"
    exit 1
fi

if ! git rev-parse --verify linguistic-evolution >/dev/null 2>&1; then
    echo "❌ Cannot access linguistic-evolution branch"
    exit 1
fi

# 5. Check for any ongoing merge conflicts
echo "🔧 Checking for merge conflicts..."
if git status | grep -q "You have unmerged paths"; then
    echo "❌ Existing merge conflicts detected - resolve before sync"
    exit 1
fi

# 6. Verify network connectivity (if pushing to remote)
echo "🌐 Verifying network connectivity..."
if ! git ls-remote origin >/dev/null 2>&1; then
    echo "⚠️  Warning: Cannot reach remote origin - sync will be local only"
fi

echo "✅ Pre-sync validation passed"
echo "🚀 Ready for synchronization"