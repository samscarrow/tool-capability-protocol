#!/bin/bash
#
# Quick TCP kernel optimization test without full build
# Demonstrates TCP framework without long compilation times
#

set -e

echo "========================================================"
echo "🚀 TCP KERNEL QUICK TEST"
echo "========================================================"
echo "Testing TCP framework without full kernel compilation"
echo ""

# Test TCP kernel optimizer
echo "1. Testing TCP kernel configuration optimizer..."
cd /tcp-kernel-lab

if python3 tcp_kernel_optimizer.py; then
    echo "✅ TCP optimizer working correctly"
else
    echo "❌ TCP optimizer test failed"
    exit 1
fi

echo ""

# Test kernel source preparation
echo "2. Testing kernel source validation..."
if [ -f "$KERNEL_SOURCE/Makefile" ]; then
    KERNEL_VERSION=$(cd "$KERNEL_SOURCE" && make kernelversion 2>/dev/null || echo "unknown")
    echo "✅ Kernel source available: Linux $KERNEL_VERSION"
else
    echo "❌ Kernel source not properly prepared"
    exit 1
fi

echo ""

# Test configuration generation
echo "3. Testing TCP configuration generation..."
BUILD_DIR="/tmp/tcp-test-build"
mkdir -p "$BUILD_DIR"

# Generate minimal defconfig
if make -C "$KERNEL_SOURCE" O="$BUILD_DIR" defconfig >/dev/null 2>&1; then
    echo "✅ Base kernel configuration generated"
    
    # Count configuration options
    CONFIG_COUNT=$(grep -c "^CONFIG_" "$BUILD_DIR/.config" || echo "0")
    echo "   Configuration options: $CONFIG_COUNT"
else
    echo "❌ Failed to generate base configuration"
    exit 1
fi

echo ""

# Test TCP optimization logic
echo "4. Testing TCP optimization application..."

# Create a simple test to verify TCP logic
python3 << 'EOF'
import sys
sys.path.append('/tcp-kernel-lab')

from tcp_kernel_optimizer import TCPKernelOptimizer

# Test hardware specification
hardware_spec = {
    'cpu_cores': 2,
    'memory_gb': 4,
    'architecture': 'x86_64',
    'type': 'virtual'
}

requirements = {
    'security_level': 1,
    'performance_priority': 'balanced'
}

try:
    optimizer = TCPKernelOptimizer()
    config = optimizer.optimize_kernel(hardware_spec, requirements)
    
    print(f"✅ TCP optimization successful:")
    print(f"   Features optimized: {len(config['config'])}")
    print(f"   Performance impact: {config['performance_impact']}")
    print(f"   Security level: {config['security_level']}")
    print(f"   Hardware class: {config['hardware_class']}")
    
except Exception as e:
    print(f"❌ TCP optimization failed: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo "✅ TCP optimization logic validated"
else
    echo "❌ TCP optimization logic failed"
    exit 1
fi

echo ""

# Test binary descriptor functionality
echo "5. Testing TCP binary descriptor framework..."

python3 << 'EOF'
import sys
sys.path.append('/tcp-kernel-lab')

from tcp_kernel_optimizer import TCPKernelDescriptor, TCPKernelFlags

# Test binary descriptor creation and validation
try:
    # Create test descriptor
    descriptor = TCPKernelDescriptor(
        feature_hash=0x1234567890ABCDEF,
        flags=TCPKernelFlags.SAFE | TCPKernelFlags.PERFORMANCE_CRITICAL,
        hardware_mask=0xFF,
        dependency_hash=0x12345678,
        performance_impact=1000,
        security_level=1,
        arch_mask=0x01,
        validation_crc=0
    )
    
    # Test binary serialization
    binary_data = descriptor.to_binary()
    
    if len(binary_data) == 24:
        print(f"✅ TCP binary descriptor: {len(binary_data)} bytes")
    else:
        print(f"❌ TCP descriptor wrong size: {len(binary_data)} bytes")
        sys.exit(1)
    
    # Test deserialization
    restored = TCPKernelDescriptor.from_binary(binary_data)
    
    if restored.feature_hash == descriptor.feature_hash:
        print("✅ TCP descriptor serialization working")
    else:
        print("❌ TCP descriptor serialization failed")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ TCP binary framework failed: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo "✅ TCP binary descriptor framework validated"
else
    echo "❌ TCP binary descriptor framework failed"
    exit 1
fi

echo ""

# Cleanup
rm -rf "$BUILD_DIR"

echo "========================================================"
echo "🎉 TCP KERNEL QUICK TEST COMPLETE"
echo "========================================================"
echo ""
echo "✅ All TCP framework components working correctly"
echo "✅ Ready for full kernel build demonstration"
echo "✅ TCP binary descriptors validated"
echo "✅ Optimization logic functional"
echo ""
echo "TCP kernel optimization system is viable!"
echo "========================================================"