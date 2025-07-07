#!/bin/bash
# Start TCP File Conflict Monitor in background
# Dr. Claude Sonnet, Managing Director

CONSORTIUM_ROOT="/Users/sam/dev/ai-ml/experiments/tool-capability-protocol/consortium"
LOG_FILE="$CONSORTIUM_ROOT/infrastructure/conflict_monitor.log"

echo "🚀 Starting TCP File Conflict Monitor..."
echo "   Consortium Root: $CONSORTIUM_ROOT"
echo "   Log File: $LOG_FILE"

# Start monitor in background
nohup python3 "$CONSORTIUM_ROOT/infrastructure/tcp_file_conflict_monitor.py" "$CONSORTIUM_ROOT" > "$LOG_FILE" 2>&1 &

# Save PID
echo $! > "$CONSORTIUM_ROOT/infrastructure/conflict_monitor.pid"

echo "✅ Monitor started with PID: $!"
echo "📊 Dashboard will be updated at: $CONSORTIUM_ROOT/infrastructure/CONFLICT_MONITOR_DASHBOARD.md"
echo "📝 Logs available at: $LOG_FILE"