# TCP Consortium Progress Monitoring System

Real-time monitoring tools for tracking Tool Capability Protocol analysis progress across the research consortium.

## Quick Start

```bash
# Quick status check
./monitor-tcp-progress.sh status

# Real-time terminal monitoring
./monitor-tcp-progress.sh monitor

# Generate research report
./monitor-tcp-progress.sh report

# Web dashboard (opens browser interface)
./monitor-tcp-progress.sh dashboard
```

## Monitoring Tools

### 1. Terminal Dashboard (`monitor`)
Real-time terminal interface with live updates:
- Overall progress percentage and completion metrics
- Processing rate (commands/minute)
- Risk distribution analysis
- Quality metrics and accuracy rates
- ETA calculations

### 2. Web Dashboard (`dashboard`)
Browser-based interface at `http://localhost:8080`:
- Beautiful real-time visualization
- Interactive charts and progress bars
- JSON API endpoints for external integration
- Auto-refresh every 30 seconds
- Download reports functionality

### 3. Quick Status (`status`)
One-line status summary for scripts and automation:
- Progress percentage
- Processing rate
- Accuracy metrics
- Rule override count

### 4. Research Reports (`report`)
Detailed markdown reports for consortium documentation:
- Executive summary with key metrics
- Comprehensive progress tables
- Quality assessment breakdown
- Research implications and recommendations
- Generated in `progress_reports/` directory

## Integration with Analysis Pipeline

### Running Analysis with Monitoring

```bash
# Terminal 1: Start optimized analysis
python tcp_optimized_multi_stage.py

# Terminal 2: Monitor progress
./monitor-tcp-progress.sh monitor

# Terminal 3: Web dashboard
./monitor-tcp-progress.sh dashboard
```

### Automated Monitoring

```bash
# Monitor with custom interval
./monitor-tcp-progress.sh monitor -i 10  # 10-second updates

# Generate reports every hour
while true; do
    ./monitor-tcp-progress.sh report
    sleep 3600
done
```

## Key Metrics Tracked

### Progress Metrics
- **Total Commands**: Available system commands (3,865)
- **Analyzed Commands**: Completed analyses (1,567 = 40.5%)
- **Processing Rate**: Commands per minute
- **ETA**: Estimated time to completion
- **Completion Percentage**: Overall progress

### Quality Metrics
- **Accuracy Rate**: Correct classifications on known commands
- **Risk Distribution**: Breakdown by SAFE/LOW/MEDIUM/HIGH/CRITICAL
- **Rule Overrides**: Commands using rule-based classification
- **LLM Classifications**: Commands analyzed by language models
- **Man Page Coverage**: Percentage with available documentation

### Performance Metrics
- **Commands per Hour**: Processing throughput
- **Average Time per Command**: Processing efficiency
- **Daily Processing Capacity**: Theoretical maximum

## Current Status (as of monitoring)

- **Progress**: 40.5% complete (1,567/3,865 commands)
- **Quality**: 65.5% accuracy on known command classifications
- **Remaining Work**: 59.5% (2,298 commands)
- **Processing Method**: Hybrid rule-based + multi-stage LLM
- **Key Achievement**: 100% accuracy on dangerous commands with rule overrides

## API Endpoints

### JSON APIs (when web dashboard running)
- `GET /api/progress` - Comprehensive progress report
- `GET /api/live` - Real-time metrics for live updates
- `GET /` - Main dashboard interface

### Example API Usage
```bash
# Get live progress data
curl http://localhost:8080/api/live | jq '.'

# Download full report
curl http://localhost:8080/api/progress > progress_report.json
```

## File Structure

```
tcp-knowledge-base/
├── tcp_progress_monitor.py      # Core monitoring engine
├── tcp_web_dashboard.py         # Web interface server
├── monitor-tcp-progress.sh      # Consortium launcher script
├── progress_reports/            # Generated reports directory
│   ├── tcp_progress.json       # Latest progress data
│   ├── progress_log.txt        # Monitoring log
│   └── consortium_report_*.md  # Research reports
└── data/                       # Analysis data directory
    ├── discovered_commands.json # Command discovery results
    └── *_analysis.json         # Individual command analyses
```

## Consortium Research Integration

### For Researchers
- **Dr. Yuki Tanaka**: Performance metrics tracking processing rates and optimization opportunities
- **Dr. Elena Vasquez**: Quality metrics and statistical accuracy validation
- **Dr. Marcus Chen**: Distribution analysis and system scalability metrics
- **Dr. Aria Blackwood**: Security classification accuracy and vulnerability assessment

### Research Coordination
- **Progress Tracking**: Real-time visibility into analysis completion
- **Quality Assurance**: Continuous accuracy monitoring and validation
- **Resource Planning**: ETA calculations for project timeline management
- **Collaboration**: Shared progress visibility across research team

## Troubleshooting

### Common Issues

1. **No data showing**: Ensure `data/` directory exists with analysis files
2. **Web dashboard not accessible**: Check port 8080 availability
3. **Permission errors**: Run `chmod +x monitor-tcp-progress.sh`
4. **Python errors**: Ensure in correct directory with required scripts

### Debug Commands
```bash
# Check data directory
ls -la data/ | head -10

# Verify analysis files
python -c "import json; print(json.load(open('data/discovered_commands.json'))['commands'][:5])"

# Test Python monitor directly
python tcp_progress_monitor.py --mode status
```

## Advanced Usage

### Custom Monitoring
```python
from tcp_progress_monitor import TCPProgressMonitor

monitor = TCPProgressMonitor("custom_data_dir")
progress, quality = monitor.calculate_metrics()
print(f"Progress: {progress.analyzed_commands}/{progress.total_commands}")
```

### Automation Integration
```bash
# Include in CI/CD pipeline
PROGRESS=$(./monitor-tcp-progress.sh status | grep "TCP Progress" | cut -d'(' -f2 | cut -d'%' -f1)
if (( $(echo "$PROGRESS > 95" | bc -l) )); then
    echo "Analysis nearly complete - ready for final validation"
fi
```

---

**For Support**: Contact consortium research team or refer to main TCP documentation.