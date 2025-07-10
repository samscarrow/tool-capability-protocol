#!/bin/bash
# TCP Knowledge Growth Monitor

echo "🔍 TCP Knowledge Growth Monitor"
echo "================================"

ssh -i /Users/sam/.ssh/tcp_deployment_key root@167.99.149.241 << 'EOF'
echo "📊 Current Statistics:"
echo -n "  • Commands discovered: "
grep -o '"[^"]*"' /opt/tcp-knowledge-system/data/discovered_commands.json 2>/dev/null | grep -v commands | grep -v last_updated | wc -l
echo -n "  • Last update: "
grep last_updated /opt/tcp-knowledge-system/data/discovered_commands.json | cut -d'"' -f4
echo "  • Analysis files: $(ls -1 /opt/tcp-knowledge-system/data/*_analysis.json 2>/dev/null | wc -l)"
echo ""
echo "📈 Growth Rate:"
echo "  • Analyzing 2 commands every minute"
echo "  • ~120 commands per hour"
echo "  • ~2,880 commands per day"
echo ""
echo "🔧 Service Status:"
systemctl is-active tcp-knowledge-growth >/dev/null 2>&1 && echo "  • Service: ✅ Running" || echo "  • Service: ❌ Stopped"
echo -n "  • Memory usage: "
ps aux | grep minimal_tcp_deployment.py | grep -v grep | awk '{print $6/1024 "MB"}'
echo ""
echo "📝 Recent Commands Analyzed:"
ls -t /opt/tcp-knowledge-system/data/*_analysis.json 2>/dev/null | head -5 | while read f; do
    basename "$f" | sed 's/_analysis.json//' | sed 's/^/  • /'
done
EOF