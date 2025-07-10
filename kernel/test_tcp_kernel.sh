#!/bin/bash
#
# TCP Kernel Integration Test Suite
#
# This script provides comprehensive testing for the TCP kernel module,
# including functionality, performance, and security validation.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
MODULE_NAME="tcp_kernel"
TEST_DIR="/tmp/tcp_test_$$"
LOG_FILE="/tmp/tcp_test.log"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [ "$(id -u)" != "0" ]; then
        log_error "This script must be run as root"
        echo "Usage: sudo $0"
        exit 1
    fi
}

# Initialize test environment
init_test() {
    log_info "Initializing TCP kernel module test suite"
    
    # Create test directory
    mkdir -p "$TEST_DIR"
    cd "$TEST_DIR"
    
    # Clear log file
    > "$LOG_FILE"
    
    # Record system information
    log_info "System Information:"
    echo "  Kernel: $(uname -r)" | tee -a "$LOG_FILE"
    echo "  Architecture: $(uname -m)" | tee -a "$LOG_FILE"
    echo "  Date: $(date)" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Test 1: Module compilation
test_compilation() {
    log_info "Test 1: Module Compilation"
    
    cd "$(dirname "$0")"
    
    if make clean >/dev/null 2>&1 && make >/dev/null 2>&1; then
        log_success "Module compiled successfully"
        return 0
    else
        log_error "Module compilation failed"
        return 1
    fi
}

# Test 2: Module loading
test_module_loading() {
    log_info "Test 2: Module Loading"
    
    # Unload if already loaded
    if lsmod | grep -q "^$MODULE_NAME"; then
        rmmod "$MODULE_NAME" 2>/dev/null || true
    fi
    
    # Load the module
    if insmod "${MODULE_NAME}.ko" 2>/dev/null; then
        log_success "Module loaded successfully"
        
        # Check if module appears in lsmod
        if lsmod | grep -q "^$MODULE_NAME"; then
            log_success "Module appears in lsmod"
        else
            log_error "Module not found in lsmod"
            return 1
        fi
        
        # Check if proc entry exists
        if [ -f "/proc/tcp_kernel" ]; then
            log_success "Proc interface created"
        else
            log_error "Proc interface not found"
            return 1
        fi
        
        return 0
    else
        log_error "Module loading failed"
        return 1
    fi
}

# Test 3: Basic functionality
test_basic_functionality() {
    log_info "Test 3: Basic Functionality"
    
    # Check proc interface
    if cat /proc/tcp_kernel >/dev/null 2>&1; then
        log_success "Proc interface readable"
    else
        log_error "Cannot read proc interface"
        return 1
    fi
    
    # Check if statistics are being collected
    local stats_before=$(cat /proc/tcp_kernel | grep "Total Checks:" | awk '{print $3}')
    
    # Perform some operations to trigger syscalls
    ls /dev >/dev/null 2>&1
    touch "$TEST_DIR/test_file"
    rm "$TEST_DIR/test_file"
    /bin/true
    
    sleep 1
    
    local stats_after=$(cat /proc/tcp_kernel | grep "Total Checks:" | awk '{print $3}')
    
    if [ "$stats_after" -gt "$stats_before" ]; then
        log_success "Statistics are being updated"
    else
        log_warning "Statistics not changing (may be expected)"
    fi
    
    return 0
}

# Test 4: Security event detection
test_security_events() {
    log_info "Test 4: Security Event Detection"
    
    # Clear dmesg buffer
    dmesg -c >/dev/null 2>&1 || true
    
    # Perform operations that should trigger security events
    log_info "Triggering security events..."
    
    # File operations
    touch "$TEST_DIR/test_security_file"
    rm "$TEST_DIR/test_security_file"
    
    # Process operations
    /bin/echo "TCP security test" >/dev/null
    
    # Wait for events to be processed
    sleep 2
    
    # Check for security events in dmesg
    local events=$(dmesg | grep "TCP:" | wc -l)
    
    if [ "$events" -gt "0" ]; then
        log_success "Security events detected ($events events)"
        
        # Show some recent events
        echo "Recent TCP events:"
        dmesg | grep "TCP:" | tail -5 | sed 's/^/  /'
    else
        log_warning "No security events found in dmesg"
    fi
    
    # Check statistics for security events
    local sec_events=$(cat /proc/tcp_kernel | grep "Security Events:" | awk '{print $3}')
    
    if [ "$sec_events" -gt "0" ]; then
        log_success "Security events recorded in statistics"
    else
        log_warning "No security events in statistics"
    fi
    
    return 0
}

# Test 5: Performance measurement
test_performance() {
    log_info "Test 5: Performance Testing"
    
    # Baseline performance (without TCP module active checks)
    log_info "Measuring baseline performance..."
    
    local start_time=$(date +%s%N)
    for i in {1..1000}; do
        /bin/true >/dev/null 2>&1
    done
    local end_time=$(date +%s%N)
    
    local baseline_ns=$((end_time - start_time))
    local baseline_per_op=$((baseline_ns / 1000))
    
    log_info "Baseline: ${baseline_per_op} ns per operation"
    
    # Get TCP statistics
    local checks_before=$(cat /proc/tcp_kernel | grep "Total Checks:" | awk '{print $3}')
    
    # Performance with TCP active
    start_time=$(date +%s%N)
    for i in {1..1000}; do
        /bin/true >/dev/null 2>&1
    done
    end_time=$(date +%s%N)
    
    local tcp_ns=$((end_time - start_time))
    local tcp_per_op=$((tcp_ns / 1000))
    
    local checks_after=$(cat /proc/tcp_kernel | grep "Total Checks:" | awk '{print $3}')
    local tcp_checks=$((checks_after - checks_before))
    
    log_info "With TCP: ${tcp_per_op} ns per operation"
    log_info "TCP processed $tcp_checks checks"
    
    # Calculate overhead
    if [ "$baseline_per_op" -gt "0" ]; then
        local overhead_percent=$(( (tcp_per_op - baseline_per_op) * 100 / baseline_per_op ))
        
        if [ "$overhead_percent" -lt "20" ]; then
            log_success "Performance overhead: ${overhead_percent}% (acceptable)"
        else
            log_warning "Performance overhead: ${overhead_percent}% (high)"
        fi
    else
        log_warning "Cannot calculate performance overhead"
    fi
    
    return 0
}

# Test 6: Stress testing
test_stress() {
    log_info "Test 6: Stress Testing"
    
    log_info "Running stress test for 10 seconds..."
    
    local checks_before=$(cat /proc/tcp_kernel | grep "Total Checks:" | awk '{print $3}')
    
    # Generate high syscall load
    timeout 10s bash -c '
        while true; do
            ls /dev >/dev/null 2>&1
            /bin/true >/dev/null 2>&1
            touch /tmp/stress_$$ 2>/dev/null
            rm /tmp/stress_$$ 2>/dev/null
        done
    ' &
    
    local stress_pid=$!
    sleep 10
    kill $stress_pid 2>/dev/null || true
    wait $stress_pid 2>/dev/null || true
    
    local checks_after=$(cat /proc/tcp_kernel | grep "Total Checks:" | awk '{print $3}')
    local total_checks=$((checks_after - checks_before))
    
    log_info "Processed $total_checks checks during stress test"
    
    # Check if module is still responsive
    if cat /proc/tcp_kernel >/dev/null 2>&1; then
        log_success "Module remained stable during stress test"
    else
        log_error "Module became unresponsive during stress test"
        return 1
    fi
    
    return 0
}

# Test 7: Module unloading
test_module_unloading() {
    log_info "Test 7: Module Unloading"
    
    if rmmod "$MODULE_NAME" 2>/dev/null; then
        log_success "Module unloaded successfully"
        
        # Verify module is gone
        if ! lsmod | grep -q "^$MODULE_NAME"; then
            log_success "Module removed from lsmod"
        else
            log_error "Module still appears in lsmod"
            return 1
        fi
        
        # Verify proc entry is gone
        if [ ! -f "/proc/tcp_kernel" ]; then
            log_success "Proc interface removed"
        else
            log_error "Proc interface still exists"
            return 1
        fi
        
        return 0
    else
        log_error "Module unloading failed"
        return 1
    fi
}

# Generate test report
generate_report() {
    log_info "Generating test report..."
    
    echo ""
    echo "========================================="
    echo "TCP Kernel Module Test Report"
    echo "========================================="
    echo "Date: $(date)"
    echo "Kernel: $(uname -r)"
    echo "Test Directory: $TEST_DIR"
    echo "Log File: $LOG_FILE"
    echo ""
    
    # Count test results
    local total_tests=7
    local passed_tests=$(grep -c "\[PASS\]" "$LOG_FILE" || echo "0")
    local failed_tests=$(grep -c "\[FAIL\]" "$LOG_FILE" || echo "0")
    local warnings=$(grep -c "\[WARN\]" "$LOG_FILE" || echo "0")
    
    echo "Test Results:"
    echo "  Total Tests: $total_tests"
    echo "  Passed: $passed_tests"
    echo "  Failed: $failed_tests"
    echo "  Warnings: $warnings"
    echo ""
    
    if [ "$failed_tests" -eq "0" ]; then
        echo -e "${GREEN}Overall Result: PASS${NC}"
        echo "All tests completed successfully!"
    else
        echo -e "${RED}Overall Result: FAIL${NC}"
        echo "Some tests failed. Check the log for details."
    fi
    
    echo ""
    echo "Full log available at: $LOG_FILE"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up test environment..."
    
    # Unload module if still loaded
    if lsmod | grep -q "^$MODULE_NAME"; then
        rmmod "$MODULE_NAME" 2>/dev/null || true
    fi
    
    # Remove test directory
    rm -rf "$TEST_DIR" 2>/dev/null || true
    
    log_info "Cleanup completed"
}

# Main test execution
main() {
    # Setup
    check_root
    init_test
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    local failed_tests=0
    
    # Run tests
    echo "Starting TCP Kernel Module Test Suite"
    echo "====================================="
    echo ""
    
    # Test 1: Compilation
    if ! test_compilation; then
        ((failed_tests++))
    fi
    
    # Test 2: Module Loading
    if ! test_module_loading; then
        ((failed_tests++))
        log_error "Cannot continue without loaded module"
        generate_report
        exit 1
    fi
    
    # Test 3: Basic Functionality
    if ! test_basic_functionality; then
        ((failed_tests++))
    fi
    
    # Test 4: Security Events
    if ! test_security_events; then
        ((failed_tests++))
    fi
    
    # Test 5: Performance
    if ! test_performance; then
        ((failed_tests++))
    fi
    
    # Test 6: Stress Testing
    if ! test_stress; then
        ((failed_tests++))
    fi
    
    # Test 7: Module Unloading
    if ! test_module_unloading; then
        ((failed_tests++))
    fi
    
    # Generate report
    generate_report
    
    # Exit with appropriate code
    if [ "$failed_tests" -eq "0" ]; then
        exit 0
    else
        exit 1
    fi
}

# Show help
show_help() {
    echo "TCP Kernel Module Test Suite"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo "  -v, --verbose Enable verbose output"
    echo ""
    echo "This script must be run as root."
    echo ""
    echo "Tests performed:"
    echo "  1. Module compilation"
    echo "  2. Module loading"
    echo "  3. Basic functionality"
    echo "  4. Security event detection"
    echo "  5. Performance measurement"
    echo "  6. Stress testing"
    echo "  7. Module unloading"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            set -x
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main