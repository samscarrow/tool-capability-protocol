#!/usr/bin/env python3
"""
Test TCP handling of command chaining operators like &&, ||, |, ;
"""

import asyncio
import json
import time
from pathlib import Path
import sys
import requests

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-server"))

def test_tcp_server(command):
    """Test command against TCP server"""
    try:
        response = requests.post(
            'http://localhost:8081/analyze',
            json={'command': command},
            timeout=1
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        return {'error': str(e)}

def analyze_command_chaining():
    """Analyze how TCP handles command chaining"""
    print('🔗 TCP Command Chaining Analysis')
    print('=' * 60)
    
    # Test various chaining scenarios
    test_scenarios = [
        {
            'category': 'Basic Commands',
            'commands': [
                'ls -la',
                'rm -rf /',
                'chmod 777 /etc'
            ]
        },
        {
            'category': 'AND Chaining (&&)',
            'commands': [
                'ls -la && echo "done"',
                'ls -la && rm -rf /',
                'chmod 777 /etc && rm -rf /',
                'mkdir test && cd test && rm -rf /'
            ]
        },
        {
            'category': 'OR Chaining (||)',
            'commands': [
                'ls -la || echo "failed"',
                'ls -la || rm -rf /',
                'test -f file || rm -rf /'
            ]
        },
        {
            'category': 'Pipe Chaining (|)',
            'commands': [
                'ls -la | grep txt',
                'cat /etc/passwd | grep root',
                'find / -name "*.conf" | xargs rm -f'
            ]
        },
        {
            'category': 'Semicolon Chaining (;)',
            'commands': [
                'ls -la; echo "done"',
                'ls -la; rm -rf /',
                'cd /tmp; rm -rf *; cd /'
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📁 {scenario['category']}")
        print("-" * 50)
        
        for command in scenario['commands']:
            print(f"\n🔍 Testing: {command}")
            
            # Test with TCP server
            result = test_tcp_server(command)
            
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                risk_emoji = {
                    'SAFE': '✅',
                    'LOW_RISK': '🟢',
                    'MEDIUM_RISK': '🟡',
                    'HIGH_RISK': '🟠',
                    'CRITICAL': '🔴'
                }.get(result.get('risk_level', 'UNKNOWN'), '❓')
                
                print(f"   {risk_emoji} Risk: {result.get('risk_level', 'UNKNOWN')}")
                print(f"   ⚡ Decision: {result.get('decision_time_us', 0):.1f} μs")
                print(f"   🗜️  Compression: {result.get('compression_ratio', 0):.0f}:1")
                
                if result.get('capabilities'):
                    print(f"   🔧 Capabilities: {', '.join(result['capabilities'])}")
                    
                if result.get('safe_alternative'):
                    alt = result['safe_alternative']
                    if len(alt) > 80:
                        alt = alt[:77] + "..."
                    print(f"   💡 Safe Alternative: {alt}")

def demonstrate_tcp_chaining_intelligence():
    """Show how TCP's current approach works and limitations"""
    print(f"\n\n🧠 TCP Command Chaining Intelligence")
    print("=" * 60)
    
    print("""
Current TCP Approach:
• Analyzes base command (first word) only
• Uses 24-byte binary descriptor for instant risk assessment
• Doesn't parse command chaining operators
• Treats entire command string as single entity

Why This Approach:
• Microsecond decisions prioritize speed over complexity
• Base command determines primary risk level
• Dangerous base commands are blocked regardless of chaining
• Safe alternatives provided for high-risk commands

Limitations:
• "ls && rm -rf /" shows as "ls" risk level
• Complex chaining logic not analyzed
• Operator-specific risks not captured

Future Enhancements:
• Hierarchical analysis of command chains
• Operator-specific risk multipliers
• Multi-command safety assessment
• Context-aware safe alternatives
""")

if __name__ == '__main__':
    print('🌟 TCP Command Chaining Test')
    print('Testing && and other operators')
    print('=' * 70)
    
    # Test command chaining
    analyze_command_chaining()
    
    # Show intelligence explanation
    demonstrate_tcp_chaining_intelligence()