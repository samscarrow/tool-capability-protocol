#!/usr/bin/env python3
"""
Enhanced TCP Command Chaining Demo
Shows how TCP could handle && and other operators with proper analysis
"""

import asyncio
import time
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-server"))

class EnhancedTCPChainAnalyzer:
    """Enhanced TCP that properly handles command chaining"""
    
    def __init__(self):
        # Command risk levels from TCP database
        self.command_risks = {
            'ls': 'CRITICAL',  # Current TCP assessment
            'rm': 'CRITICAL',
            'chmod': 'CRITICAL',
            'mkdir': 'CRITICAL',
            'cat': 'CRITICAL',
            'find': 'CRITICAL',
            'echo': 'SAFE',
            'cd': 'MEDIUM_RISK',
            'test': 'LOW_RISK',
            'grep': 'CRITICAL'
        }
        
        # Operator risk multipliers
        self.operator_risks = {
            '&&': 1.5,  # AND - executes second command if first succeeds
            '||': 1.2,  # OR - executes second command if first fails
            '|': 1.3,   # PIPE - connects commands
            ';': 2.0,   # SEQUENCE - executes all commands regardless
            '&': 1.1    # BACKGROUND - runs in background
        }
        
    def parse_command_chain(self, command_string):
        """Parse command chain into components"""
        # Split on operators while preserving them
        parts = re.split(r'(\s*(?:&&|\|\||[|;&])\s*)', command_string)
        
        commands = []
        operators = []
        
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
                
            if part in ['&&', '||', '|', ';', '&']:
                operators.append(part)
            else:
                # Extract base command (first word)
                base_cmd = part.split()[0] if part.split() else part
                commands.append({
                    'full_command': part,
                    'base_command': base_cmd,
                    'risk_level': self.get_command_risk(base_cmd)
                })
        
        return commands, operators
    
    def get_command_risk(self, command):
        """Get risk level for a command"""
        return self.command_risks.get(command, 'UNKNOWN')
    
    def calculate_chain_risk(self, commands, operators):
        """Calculate overall risk for command chain"""
        if not commands:
            return 'SAFE', 0
        
        # Base risk from most dangerous command
        max_risk = 'SAFE'
        risk_scores = {'SAFE': 0, 'LOW_RISK': 1, 'MEDIUM_RISK': 2, 'HIGH_RISK': 3, 'CRITICAL': 4}
        max_score = 0
        
        for cmd in commands:
            score = risk_scores.get(cmd['risk_level'], 0)
            if score > max_score:
                max_score = score
                max_risk = cmd['risk_level']
        
        # Apply operator multipliers
        for operator in operators:
            multiplier = self.operator_risks.get(operator, 1.0)
            max_score *= multiplier
        
        # Determine final risk level
        if max_score >= 8:
            return 'CRITICAL', max_score
        elif max_score >= 6:
            return 'HIGH_RISK', max_score
        elif max_score >= 4:
            return 'MEDIUM_RISK', max_score
        elif max_score >= 2:
            return 'LOW_RISK', max_score
        else:
            return 'SAFE', max_score
    
    def generate_safe_alternative(self, commands, operators, risk_level):
        """Generate safe alternative for command chain"""
        if risk_level in ['CRITICAL', 'HIGH_RISK']:
            return f"echo 'TCP CHAIN SAFETY: Command chain blocked - contains {len(commands)} commands with {len(operators)} operators - manual review required'"
        elif risk_level == 'MEDIUM_RISK':
            return f"echo 'TCP CHAIN WARNING: Command chain requires approval - {len(commands)} commands detected'"
        else:
            return None
    
    def analyze_command_chain(self, command_string):
        """Analyze complete command chain"""
        start_time = time.perf_counter()
        
        # Parse the command chain
        commands, operators = self.parse_command_chain(command_string)
        
        # Calculate risk
        risk_level, risk_score = self.calculate_chain_risk(commands, operators)
        
        # Generate safe alternative
        safe_alternative = self.generate_safe_alternative(commands, operators, risk_level)
        
        decision_time = (time.perf_counter() - start_time) * 1_000_000
        
        return {
            'command_string': command_string,
            'parsed_commands': commands,
            'operators': operators,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'safe_alternative': safe_alternative,
            'decision_time_us': decision_time,
            'chain_length': len(commands),
            'operator_count': len(operators)
        }

def demonstrate_enhanced_analysis():
    """Demonstrate enhanced command chain analysis"""
    print('🚀 Enhanced TCP Command Chain Analysis')
    print('=' * 70)
    
    analyzer = EnhancedTCPChainAnalyzer()
    
    # Test scenarios with increasing complexity
    test_scenarios = [
        {
            'name': 'Simple Commands',
            'commands': [
                'ls -la',
                'echo "hello"',
                'rm -rf /'
            ]
        },
        {
            'name': 'AND Chaining (&&)',
            'commands': [
                'echo "start" && ls -la',
                'ls -la && echo "done"',
                'ls -la && rm -rf /',
                'mkdir test && cd test && rm -rf /'
            ]
        },
        {
            'name': 'OR Chaining (||)',
            'commands': [
                'ls -la || echo "failed"',
                'test -f file || rm -rf /',
                'echo "safe" || echo "also safe"'
            ]
        },
        {
            'name': 'Pipe Chaining (|)',
            'commands': [
                'ls -la | grep txt',
                'cat /etc/passwd | grep root',
                'echo "safe" | cat'
            ]
        },
        {
            'name': 'Semicolon Chaining (;)',
            'commands': [
                'ls -la; echo "done"',
                'rm -rf /; echo "oops"',
                'cd /tmp; rm -rf *; cd /'
            ]
        },
        {
            'name': 'Complex Mixed Chains',
            'commands': [
                'ls -la && echo "found files" || echo "no files"',
                'mkdir backup && cp * backup/ || rm -rf /',
                'echo "start"; ls -la | grep txt && rm -rf /'
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📁 {scenario['name']}")
        print("-" * 60)
        
        for command in scenario['commands']:
            result = analyzer.analyze_command_chain(command)
            
            risk_emoji = {
                'SAFE': '✅',
                'LOW_RISK': '🟢',
                'MEDIUM_RISK': '🟡',
                'HIGH_RISK': '🟠',
                'CRITICAL': '🔴'
            }.get(result['risk_level'], '❓')
            
            print(f"\n🔍 {command}")
            print(f"   {risk_emoji} Risk: {result['risk_level']} (score: {result['risk_score']:.1f})")
            print(f"   🔗 Chain: {result['chain_length']} commands, {result['operator_count']} operators")
            print(f"   ⚡ Decision: {result['decision_time_us']:.1f} μs")
            
            # Show parsed components
            if result['operators']:
                print(f"   🔧 Operators: {', '.join(result['operators'])}")
            
            cmd_risks = [f"{cmd['base_command']}({cmd['risk_level']})" for cmd in result['parsed_commands']]
            print(f"   📊 Commands: {', '.join(cmd_risks)}")
            
            if result['safe_alternative']:
                alt = result['safe_alternative']
                if len(alt) > 80:
                    alt = alt[:77] + "..."
                print(f"   💡 Safe Alternative: {alt}")

def compare_current_vs_enhanced():
    """Compare current TCP vs enhanced approach"""
    print(f"\n\n🏆 Current TCP vs Enhanced TCP Comparison")
    print("=" * 70)
    
    print("""
CURRENT TCP APPROACH:
• Analyzes base command only (first word)
• 24-byte binary descriptor lookup
• ~2-50 μs decision time
• Ignores command chaining operators
• Example: "ls && rm -rf /" → analyzed as "ls" only

ENHANCED TCP APPROACH:
• Parses complete command chain
• Analyzes each command + operators
• Risk multipliers for operators
• ~50-200 μs decision time
• Example: "ls && rm -rf /" → both commands analyzed

TRADE-OFFS:
Current TCP:
✅ Faster (2-50 μs)
✅ Simpler (24 bytes)
✅ Constant time
❌ Less accurate for chains

Enhanced TCP:
✅ More accurate
✅ Handles complex chains
✅ Better risk assessment
❌ Slower (50-200 μs)
❌ More complex

RECOMMENDATION:
• Use current TCP for simple commands
• Use enhanced TCP for complex chains
• Hybrid approach based on operator detection
""")

if __name__ == '__main__':
    print('🌟 Enhanced TCP Command Chain Analysis Demo')
    print('Showing how TCP could handle && and other operators')
    print('=' * 70)
    
    demonstrate_enhanced_analysis()
    compare_current_vs_enhanced()