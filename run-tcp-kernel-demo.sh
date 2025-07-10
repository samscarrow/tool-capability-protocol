#!/bin/bash
#
# Run TCP Kernel Optimization Demonstration
#

set -e

echo "================================================================"
echo "🚀 TCP KERNEL OPTIMIZATION CONTAINERIZED DEMONSTRATION"
echo "================================================================"
echo ""

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker not found. Please install Docker to run the demonstration."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Create results directory
mkdir -p results

echo "Building TCP kernel development container..."
echo "This may take several minutes on first run..."

# Build and run the container
cd docker
docker-compose build tcp-kernel-builder

echo ""
echo "Starting TCP kernel optimization demonstration..."
echo ""

# Run the quick test first
echo "Running quick validation test..."
docker-compose run --rm tcp-kernel-builder /tcp-kernel-lab/scripts/tcp-kernel-quick-test.sh

echo ""
echo "================================================================"
echo "🎯 QUICK TEST RESULTS"
echo "================================================================"
echo ""
echo "The quick test validates the TCP framework without full compilation."
echo "For a complete demonstration including actual kernel building:"
echo ""
echo "  docker-compose run --rm tcp-kernel-builder"
echo ""
echo "This will:"
echo "  • Download Linux kernel source"
echo "  • Apply TCP optimizations"
echo "  • Build a complete kernel"
echo "  • Test boot in QEMU"
echo "  • Generate viability report"
echo ""
echo "Note: Full build takes 15-30 minutes depending on system performance."
echo "================================================================"