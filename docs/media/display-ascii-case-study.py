#!/usr/bin/env python3
"""
TCP Case Study ASCII Art Display
Displays the TCP meta-analysis case study with color coding and optional animation
"""

import os
import sys
import time
import argparse
from typing import List

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Standard colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'

def colorize_line(line: str) -> str:
    """Apply color coding to different elements"""
    # Headers and borders
    if line.startswith('╔') or line.startswith('╚') or '═══' in line:
        return f"{Colors.BRIGHT_BLUE}{Colors.BOLD}{line}{Colors.RESET}"
    
    # Section headers
    if line.startswith('┌─') and ('─' * 10) in line:
        return f"{Colors.CYAN}{Colors.BOLD}{line}{Colors.RESET}"
    
    # Performance metrics - positive (TCP)
    if any(keyword in line for keyword in ['TCP Approach', '100%', '<100ms', '✅', 'CORRECT']):
        return f"{Colors.BRIGHT_GREEN}{line}{Colors.RESET}"
    
    # Performance metrics - negative (Text Parsing)  
    if any(keyword in line for keyword in ['Text Parsing', 'FALSE POSITIVE', '❌', '30+ seconds']):
        return f"{Colors.BRIGHT_RED}{line}{Colors.RESET}"
    
    # Commands and code
    if line.strip().startswith('│ $ ') or '```' in line or 'scanner =' in line:
        return f"{Colors.YELLOW}{line}{Colors.RESET}"
    
    # Time indicators
    if '⏱️' in line:
        return f"{Colors.MAGENTA}{line}{Colors.RESET}"
    
    # Success indicators
    if any(symbol in line for symbol in ['✅', '🤖', '⚡']):
        return f"{Colors.GREEN}{line}{Colors.RESET}"
    
    # Warning indicators  
    if any(symbol in line for symbol in ['⚠️', '🐌', '❌']):
        return f"{Colors.RED}{line}{Colors.RESET}"
    
    # Box characters and structure
    if any(char in line for char in ['┌', '┐', '└', '┘', '├', '┤', '│', '─', '╭', '╮', '╯', '╰']):
        return f"{Colors.DIM}{line}{Colors.RESET}"
    
    return line

def display_with_animation(lines: List[str], delay: float = 0.1) -> None:
    """Display lines with animation effect"""
    for line in lines:
        colored_line = colorize_line(line)
        print(colored_line)
        if delay > 0:
            time.sleep(delay)

def display_static(lines: List[str]) -> None:
    """Display all lines at once"""
    for line in lines:
        colored_line = colorize_line(line)
        print(colored_line)

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    parser = argparse.ArgumentParser(description='Display TCP Case Study ASCII Art')
    parser.add_argument('--animate', action='store_true', help='Display with animation')
    parser.add_argument('--delay', type=float, default=0.05, help='Animation delay (seconds)')
    parser.add_argument('--clear', action='store_true', help='Clear screen before display')
    parser.add_argument('--no-color', action='store_true', help='Disable color output')
    
    args = parser.parse_args()
    
    # Get the path to the ASCII file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ascii_file = os.path.join(script_dir, 'tcp-case-study-ascii.txt')
    
    if not os.path.exists(ascii_file):
        print(f"Error: ASCII file not found at {ascii_file}")
        sys.exit(1)
    
    # Read the ASCII content
    try:
        with open(ascii_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remove trailing newlines but preserve structure
        lines = [line.rstrip() for line in lines]
        
    except Exception as e:
        print(f"Error reading ASCII file: {e}")
        sys.exit(1)
    
    # Disable colors if requested or if not in a TTY
    if args.no_color or not sys.stdout.isatty():
        # Reset all color codes
        for attr_name in dir(Colors):
            if not attr_name.startswith('_'):
                setattr(Colors, attr_name, '')
    
    # Clear screen if requested
    if args.clear:
        clear_screen()
    
    # Display the content
    try:
        if args.animate:
            print(f"{Colors.BRIGHT_CYAN}🚀 TCP Case Study Meta-Analysis{Colors.RESET}")
            print(f"{Colors.DIM}Press Ctrl+C to stop animation{Colors.RESET}\n")
            time.sleep(1)
            display_with_animation(lines, args.delay)
        else:
            display_static(lines)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Animation stopped by user{Colors.RESET}")
        sys.exit(0)
    
    # Footer message
    print(f"\n{Colors.BRIGHT_BLUE}💡 Tip: Use --animate for animated display, --help for options{Colors.RESET}")

if __name__ == '__main__':
    main()