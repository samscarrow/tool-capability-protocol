#!/bin/bash
# TCP Progress Monitor - Quick launcher for consortium researchers
# Usage: ./monitor-tcp-progress.sh [mode] [options]

set -euo pipefail

# Default values
MODE="monitor"
INTERVAL=30
DATA_DIR="data"
OUTPUT_DIR="progress_reports"

# Help function
show_help() {
    cat << EOF
🔬 TCP Progress Monitor - Consortium Research Tool

USAGE:
    ./monitor-tcp-progress.sh [MODE] [OPTIONS]

MODES:
    monitor     Real-time dashboard (default)
    report      Generate consortium report
    status      Quick status check
    dashboard   Open web dashboard (if available)

OPTIONS:
    -i, --interval SECONDS    Update interval (default: 30)
    -d, --data-dir DIR        Analysis data directory (default: data)
    -o, --output-dir DIR      Reports output directory (default: progress_reports)
    -h, --help               Show this help

EXAMPLES:
    ./monitor-tcp-progress.sh                    # Start real-time monitor
    ./monitor-tcp-progress.sh status            # Quick status check
    ./monitor-tcp-progress.sh report            # Generate detailed report
    ./monitor-tcp-progress.sh monitor -i 10     # Monitor with 10s updates

CONSORTIUM USAGE:
    # Terminal 1: Run analysis
    python tcp_optimized_multi_stage.py
    
    # Terminal 2: Monitor progress
    ./monitor-tcp-progress.sh monitor
    
    # Terminal 3: Quick checks
    ./monitor-tcp-progress.sh status

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        monitor|report|status|dashboard)
            MODE="$1"
            shift
            ;;
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -d|--data-dir)
            DATA_DIR="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Ensure Python script exists
if [[ ! -f "tcp_progress_monitor.py" ]]; then
    echo "❌ Error: tcp_progress_monitor.py not found in current directory"
    echo "   Make sure you're in the tcp-knowledge-base directory"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Execute based on mode
case $MODE in
    monitor)
        echo "🔬 Starting TCP Progress Monitor..."
        echo "📊 Data: $DATA_DIR | Reports: $OUTPUT_DIR | Interval: ${INTERVAL}s"
        echo "🔄 Press Ctrl+C to stop"
        echo ""
        python tcp_progress_monitor.py --mode monitor --interval "$INTERVAL" --data-dir "$DATA_DIR" --output-dir "$OUTPUT_DIR"
        ;;
    
    report)
        echo "📊 Generating Consortium Research Report..."
        python tcp_progress_monitor.py --mode report --data-dir "$DATA_DIR" --output-dir "$OUTPUT_DIR"
        echo ""
        echo "📁 Reports available in: $OUTPUT_DIR"
        ls -la "$OUTPUT_DIR"/*.md 2>/dev/null || echo "   (No markdown reports found)"
        ;;
    
    status)
        echo "⚡ TCP Quick Status Check:"
        python tcp_progress_monitor.py --mode status --data-dir "$DATA_DIR" --output-dir "$OUTPUT_DIR"
        ;;
    
    dashboard)
        echo "🌐 Web Dashboard Mode"
        if [[ -f "tcp_web_dashboard.py" ]]; then
            echo "   Starting web server on http://localhost:8080"
            python tcp_web_dashboard.py --port 8080 --data-dir "$DATA_DIR"
        else
            echo "   Web dashboard not available - using terminal monitor instead"
            python tcp_progress_monitor.py --mode monitor --interval "$INTERVAL" --data-dir "$DATA_DIR" --output-dir "$OUTPUT_DIR"
        fi
        ;;
esac