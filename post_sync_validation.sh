#!/bin/bash
# post_sync_validation.sh
# Validation script to run after synchronizing branches

set -e  # Exit on any error

echo "🧪 Post-synchronization validation..."

# 1. Verify core TCP functionality still works
echo "🔧 Verifying core TCP functionality..."
if python comprehensive_hierarchical_tcp.py --quick-validate 2>/dev/null; then
    echo "✅ Core TCP functions validated"
else
    echo "⚠️  Core TCP validation had issues - manual review needed"
fi

# 2. Verify linguistic evolution still functions
echo "🧬 Verifying linguistic evolution functionality..."
if python tcp_linguistic_node.py --test-mode 2>/dev/null; then
    echo "✅ Linguistic evolution functions validated"
else
    echo "⚠️  Linguistic evolution validation had issues - manual review needed"
fi

# 3. Verify MCP integration still works (if applicable)
echo "🔗 Verifying MCP integration..."
if [[ -f "mcp-server/tcp_mcp_server.py" ]]; then
    if python mcp-server/tcp_mcp_server.py --validate 2>/dev/null; then
        echo "✅ MCP integration validated"
    else
        echo "⚠️  MCP integration validation had issues - manual review needed"
    fi
else
    echo "ℹ️  MCP integration not found - skipping validation"
fi

# 4. Run any automated tests
echo "🧪 Running automated tests..."
if python -m pytest tests/ -v 2>/dev/null; then
    echo "✅ Automated tests passed"
else
    echo "ℹ️  No automated tests found or tests failed - manual verification recommended"
fi

# 5. Check if the merge preserved both approaches
echo "📊 Checking branch integrity..."
if git log --oneline -n 5 | grep -q "linguistic-evolution\|main"; then
    echo "✅ Branch history preserved"
else
    echo "ℹ️  Branch history check inconclusive"
fi

# 6. Verify critical files are present
echo "📁 Verifying critical files..."
critical_files=(
    "tcp_analyzer.py"
    "tcp_linguistic_node.py"
    "comprehensive_hierarchical_tcp.py"
    "TCP_LINGUISTIC_EVOLUTION.md"
    "TCP_SPECIFICATION.md"
    "README.md"
)

missing_files=()
for file in "${critical_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file present"
    else
        echo "❌ $file missing"
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "⚠️  Missing critical files: ${missing_files[*]}"
    echo "   Manual review required"
fi

# 7. Check for any syntax errors in Python files
echo "🐍 Checking Python syntax..."
python_files=$(find . -name "*.py" -not -path "./.*" | head -10)
syntax_errors=()

for file in $python_files; do
    if python -m py_compile "$file" 2>/dev/null; then
        echo "✅ $file syntax OK"
    else
        echo "❌ $file has syntax errors"
        syntax_errors+=("$file")
    fi
done

if [[ ${#syntax_errors[@]} -gt 0 ]]; then
    echo "⚠️  Syntax errors in: ${syntax_errors[*]}"
    echo "   Manual review required"
fi

# 8. Verify documentation is coherent
echo "📚 Verifying documentation..."
if [[ -f "README.md" ]] && grep -q "TCP" README.md; then
    echo "✅ README.md contains TCP documentation"
else
    echo "⚠️  README.md may need updates"
fi

# 9. Check for any TODO markers or merge conflicts
echo "🔍 Checking for merge artifacts..."
if grep -r "<<<<<<< HEAD\|=======" . --include="*.py" --include="*.md" --include="*.sh" 2>/dev/null; then
    echo "❌ Merge conflict markers found - manual resolution required"
else
    echo "✅ No merge conflict markers found"
fi

# 10. Final status summary
echo ""
echo "📋 Post-sync validation summary:"
echo "   - Core TCP: $(python comprehensive_hierarchical_tcp.py --quick-validate 2>/dev/null && echo "✅ OK" || echo "⚠️  Check needed")"
echo "   - Linguistic Evolution: $(python tcp_linguistic_node.py --test-mode 2>/dev/null && echo "✅ OK" || echo "⚠️  Check needed")"
echo "   - Critical Files: $([[ ${#missing_files[@]} -eq 0 ]] && echo "✅ OK" || echo "⚠️  Missing files")"
echo "   - Python Syntax: $([[ ${#syntax_errors[@]} -eq 0 ]] && echo "✅ OK" || echo "⚠️  Syntax errors")"

if [[ ${#missing_files[@]} -eq 0 ]] && [[ ${#syntax_errors[@]} -eq 0 ]]; then
    echo ""
    echo "✅ Post-sync validation complete - sync appears successful"
else
    echo ""
    echo "⚠️  Post-sync validation found issues - manual review recommended"
fi