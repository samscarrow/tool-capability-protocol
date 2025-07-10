# Makefile for TCP Kernel Integration Module
#
# This Makefile builds the TCP kernel module for Linux systems.
# It includes both debug and release configurations.

# Module name
MODULE_NAME := tcp_kernel

# Object files
obj-m += $(MODULE_NAME).o
$(MODULE_NAME)-objs := tcp_kernel_module.o

# Kernel build directory (auto-detect current kernel)
KERNEL_DIR ?= /lib/modules/$(shell uname -r)/build

# Current directory
PWD := $(shell pwd)

# Compiler flags
EXTRA_CFLAGS += -DDEBUG
EXTRA_CFLAGS += -Wall -Wextra
EXTRA_CFLAGS += -std=gnu99

# Default target
all: module

# Build the kernel module
module:
	@echo "Building TCP Kernel Integration Module..."
	@echo "Kernel Directory: $(KERNEL_DIR)"
	@echo "Module Name: $(MODULE_NAME)"
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules

# Clean build artifacts
clean:
	@echo "Cleaning TCP kernel module build artifacts..."
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) clean
	rm -f *.order *.symvers *.mod.c

# Install the module (requires root)
install: module
	@echo "Installing TCP kernel module..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "ERROR: Installation requires root privileges"; \
		echo "Run: sudo make install"; \
		exit 1; \
	fi
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules_install
	depmod -a
	@echo "Module installed successfully"
	@echo "Load with: sudo modprobe $(MODULE_NAME)"

# Load the module
load: module
	@echo "Loading TCP kernel module..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "ERROR: Loading requires root privileges"; \
		echo "Run: sudo make load"; \
		exit 1; \
	fi
	@if lsmod | grep -q "^$(MODULE_NAME)"; then \
		echo "Module already loaded, reloading..."; \
		rmmod $(MODULE_NAME) || true; \
	fi
	insmod $(MODULE_NAME).ko
	@echo "Module loaded successfully"
	@echo "Check status: cat /proc/tcp_kernel"

# Unload the module
unload:
	@echo "Unloading TCP kernel module..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "ERROR: Unloading requires root privileges"; \
		echo "Run: sudo make unload"; \
		exit 1; \
	fi
	@if lsmod | grep -q "^$(MODULE_NAME)"; then \
		rmmod $(MODULE_NAME); \
		echo "Module unloaded successfully"; \
	else \
		echo "Module not currently loaded"; \
	fi

# Show module information
info: module
	@echo "TCP Kernel Module Information:"
	@echo "============================="
	modinfo $(MODULE_NAME).ko

# Test the module (build, load, show status, unload)
test: module
	@echo "Testing TCP kernel module..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "ERROR: Testing requires root privileges"; \
		echo "Run: sudo make test"; \
		exit 1; \
	fi
	@echo "1. Loading module..."
	$(MAKE) load
	@echo "2. Waiting for initialization..."
	sleep 2
	@echo "3. Checking module status..."
	cat /proc/tcp_kernel
	@echo "4. Checking kernel messages..."
	dmesg | tail -10 | grep TCP || true
	@echo "5. Testing complete. Module remains loaded."
	@echo "   To unload: sudo make unload"

# Development target - build and show any errors
dev: clean
	@echo "Development build with verbose output..."
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules V=1

# Check kernel compatibility
check:
	@echo "Checking kernel compatibility..."
	@echo "Current kernel: $(shell uname -r)"
	@echo "Kernel headers: $(KERNEL_DIR)"
	@if [ ! -d "$(KERNEL_DIR)" ]; then \
		echo "ERROR: Kernel headers not found"; \
		echo "Install with: sudo apt-get install linux-headers-$(shell uname -r)"; \
		exit 1; \
	fi
	@echo "Kernel version check:"
	@cat $(KERNEL_DIR)/include/generated/utsrelease.h 2>/dev/null || \
		echo "WARNING: Could not read kernel version"
	@echo "Compatibility check passed"

# Performance test
perf-test: load
	@echo "Running performance test..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "ERROR: Performance test requires root privileges"; \
		exit 1; \
	fi
	@echo "Baseline syscall performance..."
	time ls /dev > /dev/null
	@echo "TCP kernel module statistics:"
	cat /proc/tcp_kernel | grep -A 10 "Statistics:"

# Security test
security-test: load
	@echo "Running security tests..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "ERROR: Security test requires root privileges"; \
		exit 1; \
	fi
	@echo "Testing file operations..."
	touch /tmp/tcp_test_file
	rm /tmp/tcp_test_file
	@echo "Testing process operations..."
	/bin/true
	@echo "Checking security events:"
	cat /proc/tcp_kernel | grep "Security Events:"
	dmesg | tail -20 | grep TCP || echo "No TCP security events in recent dmesg"

# Help target
help:
	@echo "TCP Kernel Integration Module - Makefile Help"
	@echo "============================================"
	@echo ""
	@echo "Targets:"
	@echo "  all         - Build the kernel module (default)"
	@echo "  module      - Build the kernel module"
	@echo "  clean       - Clean build artifacts"
	@echo "  install     - Install module to system (requires root)"
	@echo "  load        - Load module into kernel (requires root)"
	@echo "  unload      - Unload module from kernel (requires root)"
	@echo "  test        - Full test: build, load, status, keep loaded (requires root)"
	@echo "  perf-test   - Performance testing (requires root)"
	@echo "  security-test - Security functionality testing (requires root)"
	@echo "  info        - Show module information"
	@echo "  check       - Check kernel compatibility"
	@echo "  dev         - Development build with verbose output"
	@echo "  help        - Show this help message"
	@echo ""
	@echo "Usage examples:"
	@echo "  make                    # Build module"
	@echo "  sudo make test          # Full test cycle"
	@echo "  sudo make load          # Load module"
	@echo "  cat /proc/tcp_kernel    # Check status"
	@echo "  sudo make unload        # Unload module"
	@echo ""
	@echo "Requirements:"
	@echo "  - Linux kernel headers for current kernel"
	@echo "  - GCC compiler"
	@echo "  - Root privileges for load/unload operations"

.PHONY: all module clean install load unload info test dev check perf-test security-test help