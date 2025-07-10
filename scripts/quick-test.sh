#!/bin/bash
echo "🧪 Quick TCP Test"
echo "================"

# Test Python imports
echo "Testing Python imports..."
python3 -c "
import sys
sys.path.insert(0, '/tcp-security')
try:
    from tcp.enrichment.manpage_enricher import ManPageEnricher
    print('✅ TCP imports working')
except Exception as e:
    print(f'❌ Import error: {e}')
"

# Test man pages
echo "Testing man pages..."
if man ls > /dev/null 2>&1; then
    echo "✅ Man pages available"
else
    echo "❌ Man pages not found"
fi

# Test command analysis
echo "Testing command analysis..."
python3 -c "
import sys
sys.path.insert(0, '/tcp-security')
try:
    from tcp.enrichment.manpage_enricher import ManPageEnricher
    enricher = ManPageEnricher()
    result = enricher.enrich_command('ls')
    if result:
        print(f'✅ Analysis working: {result.security_level.value}')
    else:
        print('⚠️  Analysis returned no results')
except Exception as e:
    print(f'❌ Analysis error: {e}')
"

echo ""
echo "🏁 Quick test complete!"