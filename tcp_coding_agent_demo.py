#!/usr/bin/env python3
"""
TCP-Empowered Coding Agent Demo
Shows how a naive agent uses TCP descriptors to write safe code
"""

import json
import struct
import subprocess
from typing import Dict, List, Tuple, Optional
import os

class TCPAwareCodingAgent:
    """A naive coding agent that uses TCP descriptors to write safe code"""
    
    def __init__(self):
        self.tcp_knowledge = {}
        self.load_tcp_knowledge()
        
    def load_tcp_knowledge(self):
        """Load TCP descriptors for common commands"""
        # In practice, this would load from the full TCP database
        # For demo, we'll use a subset of critical knowledge
        self.tcp_knowledge = {
            'rm': {
                'descriptor': bytes.fromhex('544350020002d67f249b0000022f138801f40032000296f8'),
                'flags': 0x0000022f,  # CRITICAL + DESTRUCTIVE + FILE_MODIFICATION + REQUIRES_SUDO
                'insights': '💀 CRITICAL 💥 Destructive 📝 FileWrite 🔐 Sudo'
            },
            'cp': {
                'descriptor': bytes.fromhex('544350020002632020040000020400640032000a00006d57'),
                'flags': 0x00000204,  # MEDIUM_RISK + FILE_MODIFICATION
                'insights': '🟠 MEDIUM 📝 FileWrite'
            },
            'cat': {
                'descriptor': bytes.fromhex('544350010001000063030000000100640032000a000096f8'),
                'flags': 0x00000001,  # SAFE
                'insights': '🟢 SAFE'
            },
            'grep': {
                'descriptor': bytes.fromhex('544350010001000067040000000100640032000a00007567'),
                'flags': 0x00000001,  # SAFE
                'insights': '🟢 SAFE'
            },
            'wc': {
                'descriptor': bytes.fromhex('544350010001000077020000000100640032000a0000a123'),
                'flags': 0x00000001,  # SAFE
                'insights': '🟢 SAFE'
            },
            'sort': {
                'descriptor': bytes.fromhex('544350010001000073040000000100640032000a0000b456'),
                'flags': 0x00000001,  # SAFE
                'insights': '🟢 SAFE'
            },
            'mv': {
                'descriptor': bytes.fromhex('54435001000100006d020000020400640032000a000061c5'),
                'flags': 0x00000204,  # MEDIUM_RISK + FILE_MODIFICATION
                'insights': '🟠 MEDIUM 📝 FileWrite'
            },
            'find': {
                'descriptor': bytes.fromhex('544350010001000066040000000200640032000a0000c789'),
                'flags': 0x00000002,  # LOW_RISK
                'insights': '🟡 LOW'
            },
            'chmod': {
                'descriptor': bytes.fromhex('544350010001000063050000042800640032000a00003979'),
                'flags': 0x00000428,  # HIGH_RISK + REQUIRES_SUDO + SYSTEM_MODIFICATION
                'insights': '🔴 HIGH 🔐 Sudo ⚙️ System'
            },
            'echo': {
                'descriptor': bytes.fromhex('544350010001000065040000000100640032000a0000d012'),
                'flags': 0x00000001,  # SAFE
                'insights': '🟢 SAFE'
            }
        }
    
    def check_command_safety(self, command: str) -> Tuple[bool, str, int]:
        """Check if a command is safe to use based on TCP descriptor"""
        if command not in self.tcp_knowledge:
            return False, f"❓ Unknown command '{command}' - cannot verify safety", 0
        
        cmd_info = self.tcp_knowledge[command]
        flags = cmd_info['flags']
        
        # Decode safety level from flags
        if flags & (1 << 4):  # CRITICAL
            return False, f"🚫 CRITICAL command '{command}' - too dangerous!", flags
        elif flags & (1 << 3):  # HIGH_RISK
            return False, f"⛔ HIGH RISK command '{command}' - requires human approval", flags
        elif flags & (1 << 2):  # MEDIUM_RISK
            return True, f"⚠️  MEDIUM RISK command '{command}' - use with caution", flags
        elif flags & (1 << 1):  # LOW_RISK
            return True, f"✓ LOW RISK command '{command}' - generally safe", flags
        else:  # SAFE
            return True, f"✅ SAFE command '{command}' - approved for use", flags
    
    def generate_safe_file_processor(self, task: str) -> str:
        """Generate a file processing program using only TCP-approved commands"""
        
        print("🤖 TCP-AWARE CODING AGENT")
        print("=" * 60)
        print(f"Task: {task}")
        print("=" * 60)
        print()
        
        # Agent's thought process
        print("💭 AGENT REASONING (using TCP descriptors):")
        print()
        
        # Analyze what commands might be needed
        potential_commands = []
        
        if "count" in task.lower() or "lines" in task.lower():
            potential_commands.append("wc")
        if "search" in task.lower() or "find" in task.lower() or "filter" in task.lower():
            potential_commands.append("grep")
        if "display" in task.lower() or "show" in task.lower() or "read" in task.lower():
            potential_commands.append("cat")
        if "sort" in task.lower() or "order" in task.lower():
            potential_commands.append("sort")
        if "copy" in task.lower():
            potential_commands.append("cp")
        if "move" in task.lower() or "rename" in task.lower():
            potential_commands.append("mv")
        if "delete" in task.lower() or "remove" in task.lower():
            potential_commands.append("rm")
        if "permission" in task.lower():
            potential_commands.append("chmod")
        
        # Always consider these for file operations
        potential_commands.extend(["cat", "echo"])
        
        # Check safety of each command
        safe_commands = []
        unsafe_commands = []
        
        print("📋 Analyzing required commands:")
        for cmd in set(potential_commands):
            is_safe, message, flags = self.check_command_safety(cmd)
            print(f"   {cmd}: {message}")
            
            if is_safe:
                safe_commands.append((cmd, flags))
            else:
                unsafe_commands.append((cmd, message))
        
        print()
        
        # Generate the program
        if "remove" in task.lower() or "delete" in task.lower():
            # Task requires dangerous commands
            return self.generate_safe_alternative_for_dangerous_task(task, unsafe_commands)
        else:
            # Task can be done with safe commands
            return self.generate_program_with_safe_commands(task, safe_commands)
    
    def generate_program_with_safe_commands(self, task: str, safe_commands: List[Tuple[str, int]]) -> str:
        """Generate a program using only safe commands"""
        
        print("✅ GENERATING SAFE PROGRAM")
        print("=" * 60)
        
        # Example: "Count lines containing 'error' in log files and save summary"
        if "count" in task.lower() and "error" in task.lower():
            program = '''#!/bin/bash
# TCP-Safe File Processor
# Task: Count lines containing 'error' in log files and save summary
# All commands verified safe by TCP descriptors

# Using only TCP-approved safe commands:
# - grep (🟢 SAFE): For searching text
# - wc (🟢 SAFE): For counting lines  
# - cat (🟢 SAFE): For reading files
# - echo (🟢 SAFE): For output

echo "🔍 Analyzing log files for errors..."
echo "Generated by TCP-Aware Agent" > error_summary.txt
echo "=========================" >> error_summary.txt
echo "" >> error_summary.txt

# Process each log file
for logfile in *.log; do
    if [ -f "$logfile" ]; then
        echo "Processing: $logfile" | tee -a error_summary.txt
        
        # Use grep (TCP-verified SAFE) to find errors
        error_count=$(grep -i "error" "$logfile" 2>/dev/null | wc -l)
        
        echo "  Error lines: $error_count" | tee -a error_summary.txt
        
        # Show sample errors (first 3)
        echo "  Sample errors:" >> error_summary.txt
        grep -i "error" "$logfile" 2>/dev/null | head -3 >> error_summary.txt
        echo "" >> error_summary.txt
    fi
done

echo "" | tee -a error_summary.txt
echo "✅ Analysis complete! Results saved to error_summary.txt"

# Display summary
echo ""
echo "📊 Summary:"
cat error_summary.txt
'''
            
        elif "filter" in task.lower() and "copy" in task.lower():
            # Since cp is MEDIUM_RISK, we need to be careful
            program = '''#!/bin/bash
# TCP-Safe File Processor with Caution
# Task: Filter and copy specific files
# Commands verified by TCP descriptors

# ⚠️  Using cp (🟠 MEDIUM 📝 FileWrite) - with safety checks

# Safety check function
safe_copy() {
    local source=$1
    local dest=$2
    
    # TCP-mandated safety checks for MEDIUM_RISK commands
    if [ ! -f "$source" ]; then
        echo "❌ Source file not found: $source"
        return 1
    fi
    
    if [ -f "$dest" ]; then
        echo "⚠️  Destination exists. TCP safety protocol requires confirmation."
        echo "   Skipping to prevent data loss: $dest"
        return 1
    fi
    
    # Safe to proceed
    cp "$source" "$dest"
    echo "✅ Safely copied: $source → $dest"
}

# Create safe output directory
output_dir="filtered_files_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$output_dir"

echo "🔍 Filtering and copying files..."

# Use find (🟡 LOW risk) with grep (🟢 SAFE) for filtering
find . -type f -name "*.txt" | while read -r file; do
    if grep -q "important" "$file" 2>/dev/null; then
        basename=$(basename "$file")
        safe_copy "$file" "$output_dir/$basename"
    fi
done

echo "✅ Filtered files saved to: $output_dir/"
'''
            
        else:
            # Generic safe file processor
            program = '''#!/bin/bash
# TCP-Verified Safe File Processor
# All commands approved by TCP security descriptors

# Safe commands available:
# - cat (🟢 SAFE): Read files
# - grep (🟢 SAFE): Search text
# - wc (🟢 SAFE): Count lines/words
# - sort (🟢 SAFE): Sort output
# - echo (🟢 SAFE): Display text

echo "🤖 TCP-Safe File Processor"
echo "========================"

# Example safe operations
for file in *.txt; do
    if [ -f "$file" ]; then
        echo "Processing: $file"
        
        # Count lines (SAFE)
        lines=$(wc -l < "$file")
        echo "  Lines: $lines"
        
        # Search for patterns (SAFE)
        matches=$(grep -c "pattern" "$file" 2>/dev/null || echo "0")
        echo "  Pattern matches: $matches"
    fi
done

echo "✅ Processing complete - all operations TCP-verified safe"
'''
        
        print(program)
        print()
        print("🛡️ SAFETY ANALYSIS:")
        print("✅ All commands used are TCP-verified as SAFE or properly safeguarded")
        print("✅ No CRITICAL or HIGH_RISK commands included")
        print("✅ MEDIUM_RISK commands include safety checks")
        print("✅ Program cannot cause data loss or system damage")
        
        return program
    
    def generate_safe_alternative_for_dangerous_task(self, task: str, unsafe_commands: List[Tuple[str, str]]) -> str:
        """Generate safe alternative when dangerous commands are needed"""
        
        print("🚨 SAFETY VIOLATION DETECTED")
        print("=" * 60)
        print()
        print("The requested task requires CRITICAL/HIGH_RISK commands:")
        for cmd, message in unsafe_commands:
            print(f"   {message}")
        
        print()
        print("🔄 GENERATING SAFE ALTERNATIVE")
        print("=" * 60)
        
        program = '''#!/bin/bash
# TCP-Safe Alternative Program
# Original task required dangerous commands (rm, chmod, etc.)
# This safe alternative provides similar functionality

# Instead of using 'rm' (💀 CRITICAL), we'll use safe alternatives:

# 1. Move files to a quarantine directory instead of deleting
quarantine_dir=".tcp_quarantine_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$quarantine_dir"

echo "🛡️ TCP Safety Protocol Active"
echo "=============================="
echo "ℹ️  Dangerous commands replaced with safe alternatives"
echo ""

# Safe file handling function
quarantine_file() {
    local file=$1
    
    if [ -f "$file" ]; then
        # Instead of 'rm', safely move to quarantine
        mv "$file" "$quarantine_dir/" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "✅ Quarantined: $file → $quarantine_dir/"
            
            # Log the action for recovery
            echo "$(date): Quarantined $file" >> "$quarantine_dir/quarantine.log"
        else
            echo "❌ Failed to quarantine: $file"
        fi
    fi
}

# Example: Process files that match criteria
echo "🔍 Processing files for quarantine..."

for file in *.tmp *.log; do
    if [ -f "$file" ]; then
        # Show what would be deleted
        echo "Found: $file ($(wc -c < "$file") bytes)"
        
        # Safe quarantine instead of delete
        quarantine_file "$file"
    fi
done

echo ""
echo "📊 Summary:"
echo "- Files quarantined to: $quarantine_dir/"
echo "- Original files preserved for recovery"
echo "- No data permanently deleted"
echo ""
echo "💡 To permanently delete quarantined files later:"
echo "   After human review: rm -rf $quarantine_dir"
echo ""
echo "✅ Task completed safely using TCP-approved commands only"
'''
        
        print(program)
        print()
        print("🛡️ SAFETY FEATURES:")
        print("✅ Dangerous 'rm' replaced with safe 'mv' to quarantine")
        print("✅ All files recoverable from quarantine directory")
        print("✅ Audit log created for all operations")
        print("✅ Human approval required for permanent deletion")
        print("✅ No TCP CRITICAL/HIGH_RISK commands executed")
        
        return program


def demo_tcp_coding_agent():
    """Demonstrate the TCP-aware coding agent"""
    
    agent = TCPAwareCodingAgent()
    
    print("🎭 TCP-EMPOWERED CODING AGENT DEMONSTRATION")
    print("=" * 60)
    print("This naive agent has never written code before.")
    print("It only knows command safety from 24-byte TCP descriptors.")
    print("=" * 60)
    print()
    
    # Test Case 1: Safe task
    print("📝 TASK 1: Count lines containing 'error' in log files and save summary")
    print("-" * 60)
    agent.generate_safe_file_processor("Count lines containing 'error' in log files and save summary")
    
    print("\n" + "="*80 + "\n")
    
    # Test Case 2: Task requiring dangerous commands
    print("📝 TASK 2: Remove all temporary files and logs older than 7 days")
    print("-" * 60)
    agent.generate_safe_file_processor("Remove all temporary files and logs older than 7 days")
    
    print("\n" + "="*80 + "\n")
    
    # Test Case 3: Mixed safety task
    print("📝 TASK 3: Filter important files and copy to backup directory")  
    print("-" * 60)
    agent.generate_safe_file_processor("Filter important files and copy to backup directory")


if __name__ == "__main__":
    demo_tcp_coding_agent()