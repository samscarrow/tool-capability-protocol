#!/bin/bash
#
# Simple TCP Kernel Demo without Docker Compose
#

set -e

echo "================================================================"
echo "🚀 TCP KERNEL OPTIMIZATION DEMONSTRATION"
echo "================================================================"

# Build the container
echo "Building TCP kernel development container..."
docker build -t tcp-kernel-builder -f Dockerfile.tcp-kernel-builder ..

echo ""
echo "Running TCP kernel optimization quick test..."

# Run the quick test
docker run --rm --privileged \
    -e KERNEL_SOURCE=/tcp-kernel-lab/kernel-source/linux \
    -e BUILD_OUTPUT=/tcp-kernel-lab/build-output \
    -e TCP_CONFIG_DIR=/tcp-kernel-lab/tcp-configs \
    tcp-kernel-builder \
    /tcp-kernel-lab/scripts/tcp-kernel-quick-test.sh

echo ""
echo "================================================================"
echo "Quick test complete! For full kernel build demonstration, run:"
echo "docker run -it --privileged tcp-kernel-builder"
echo "================================================================"