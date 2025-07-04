#!/bin/bash
#
# Prepare kernel source for TCP optimization demonstration
#

set -e

KERNEL_VERSION="6.1.87"
DOWNLOAD_URL="https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${KERNEL_VERSION}.tar.xz"
SOURCE_DIR="/tcp-kernel-lab/kernel-source"

echo "Preparing Linux kernel source for TCP demonstration..."

# Create source directory
mkdir -p "$SOURCE_DIR"
cd "$SOURCE_DIR"

# Check if already downloaded
if [ -d "linux" ]; then
    echo "Kernel source already available"
    exit 0
fi

echo "Downloading Linux kernel $KERNEL_VERSION..."
wget -q --show-progress "$DOWNLOAD_URL"

echo "Extracting kernel source..."
tar -xf "linux-${KERNEL_VERSION}.tar.xz"
mv "linux-${KERNEL_VERSION}" linux
rm "linux-${KERNEL_VERSION}.tar.xz"

echo "Kernel source prepared successfully"
ls -la linux/