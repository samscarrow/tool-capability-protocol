#!/usr/bin/env python3
"""
TCP Controlled Uncertainty Demonstration
Shows how TCP maintains high safety even with uncertain/ambiguous commands
"""

import asyncio
import random
import time
import json
import hashlib
import struct
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-server"))
from tcp_database import TCPDescriptorDatabase
from safety_patterns import AgentSafetyMonitor


class UncertaintySimulator:
    """Simulates real-world uncertainty in command analysis"""
    
    def __init__(self):
        self.ambiguous_patterns = {
            'variable_expansion': [
                'rm -rf $HOME/*',
                'chmod 777 ${CONFIG_DIR}',
                'dd if=$SOURCE of=$TARGET',
                'curl $URL | bash'
            ],
            'wildcards': [
                'rm -rf /tmp/test*',
                'chmod 644 *.conf',
                'find / -name "*.log" -delete',
                'docker rm $(docker ps -aq)'
            ],
            'piped_commands': [
                'cat /etc/passwd | grep root',
                'ps aux | kill -9',
                'find . -type f | xargs rm',
                'curl https://example.com | sudo bash'
            ],
            'conditional_execution': [
                'test -f /tmp/lock && rm -rf /',
                '[ -z "$USER" ] || chmod 777 /',
                'sudo -u $USER command',
                'if [ -f config ]; then rm -rf *; fi'
            ],
            'obfuscated': [
                'r""m -r""f /',
                'ch`mod` 777 /',
                'eval "rm -rf /"',
                'base64 -d <<< "cm0gLXJmIC8="'
            ]
        }
        
        # Uncertainty factors that affect risk assessment
        self.uncertainty_factors = {
            'environment_unknown': 0.2,      # Don't know environment variables
            'user_privileges_unknown': 0.3,  # Don't know if user is root
            'filesystem_state_unknown': 0.2, # Don't know what files exist
            'network_state_unknown': 0.1,    # Don't know network accessibility
            'time_based_risk': 0.1          # Risk changes based on time/context
        }
        
    def inject_uncertainty(self, command: str) -> Dict:
        """Analyze command uncertainty factors"""
        uncertainty_score = 0.0
        uncertainty_reasons = []
        
        # Check for variable expansion
        if '$' in command or '${' in command:
            uncertainty_score += self.uncertainty_factors['environment_unknown']
            uncertainty_reasons.append("Contains environment variables")
            
        # Check for wildcards
        if any(wild in command for wild in ['*', '?', '[', ']']):
            uncertainty_score += self.uncertainty_factors['filesystem_state_unknown']
            uncertainty_reasons.append("Contains wildcards")
            
        # Check for command substitution
        if '$(' in command or '`' in command:
            uncertainty_score += 0.4
            uncertainty_reasons.append("Contains command substitution")
            
        # Check for piped commands
        if '|' in command:
            uncertainty_score += 0.3
            uncertainty_reasons.append("Contains piped commands")
            
        # Check for conditional execution
        if any(cond in command for cond in ['&&', '||', 'if', 'then']):
            uncertainty_score += 0.25
            uncertainty_reasons.append("Contains conditional execution")
            
        # Check for privilege escalation
        if any(priv in command for priv in ['sudo', 'su', 'doas']):
            uncertainty_score += self.uncertainty_factors['user_privileges_unknown']
            uncertainty_reasons.append("Requires privilege escalation")
            
        # Check for network operations
        if any(net in command for net in ['curl', 'wget', 'ssh', 'nc']):
            uncertainty_score += self.uncertainty_factors['network_state_unknown']
            uncertainty_reasons.append("Involves network operations")
            
        # Time-based uncertainty (e.g., cron jobs, scheduled tasks)
        if any(time_cmd in command for time_cmd in ['cron', 'at', 'sleep']):
            uncertainty_score += self.uncertainty_factors['time_based_risk']
            uncertainty_reasons.append("Time-dependent execution")
            
        return {
            'uncertainty_score': min(uncertainty_score, 1.0),
            'uncertainty_reasons': uncertainty_reasons,
            'confidence': 1.0 - min(uncertainty_score, 1.0)
        }


class TCPUncertaintyHandler:
    """TCP system that handles uncertainty with high safety"""
    
    def __init__(self):
        self.tcp_db = TCPDescriptorDatabase()
        self.safety_monitor = AgentSafetyMonitor()
        self.uncertainty_sim = UncertaintySimulator()
        self.safety_threshold = 0.7  # Confidence threshold for auto-approval
        
        # TCP uncertainty resolution strategies
        self.resolution_strategies = {
            'isolate': "Execute in isolated sandbox environment",
            'dry_run': "Perform dry-run analysis first",
            'human_review': "Require human approval",
            'decompose': "Break into safer sub-commands",
            'monitor': "Execute with real-time monitoring",
            'reject': "Reject due to high uncertainty"
        }
        
    async def analyze_with_uncertainty(self, command: str) -> Dict:
        """Analyze command considering uncertainty"""
        start_time = time.perf_counter()
        
        # Get base TCP analysis
        base_cmd = command.split()[0]
        tcp_descriptor = await self.tcp_db.get_descriptor(base_cmd)
        
        # Base risk assessment from TCP
        if tcp_descriptor:
            risk_info = self._decode_tcp_risk(tcp_descriptor)
        else:
            risk_info = {'risk_level': 'UNKNOWN', 'risk_score': 5}
            
        # Add uncertainty analysis
        uncertainty = self.uncertainty_sim.inject_uncertainty(command)
        
        # Calculate combined safety score
        base_safety = 1.0 - (risk_info['risk_score'] / 5.0)
        safety_score = base_safety * uncertainty['confidence']
        
        # Determine action based on safety score
        if safety_score >= self.safety_threshold:
            action = 'APPROVE'
            strategy = None
        elif safety_score >= 0.5:
            action = 'CONDITIONAL_APPROVE'
            strategy = self._select_strategy(command, uncertainty)
        elif safety_score >= 0.3:
            action = 'REQUIRE_REVIEW'
            strategy = 'human_review'
        else:
            action = 'REJECT'
            strategy = 'reject'
            
        # Generate safe alternative if needed
        safe_alternative = None
        if action in ['REQUIRE_REVIEW', 'REJECT']:
            safe_alternative = self.safety_monitor.generate_safe_alternative(command)
            
        decision_time = (time.perf_counter() - start_time) * 1_000_000
        
        return {
            'command': command,
            'risk_level': risk_info['risk_level'],
            'uncertainty': uncertainty,
            'safety_score': safety_score,
            'action': action,
            'strategy': strategy,
            'safe_alternative': safe_alternative,
            'decision_time_us': decision_time,
            'reasoning': self._generate_reasoning(risk_info, uncertainty, safety_score)
        }
        
    def _decode_tcp_risk(self, descriptor: bytes) -> Dict:
        """Decode risk from TCP descriptor"""
        if len(descriptor) != 24:
            return {'risk_level': 'UNKNOWN', 'risk_score': 5}
            
        security_flags = struct.unpack('>I', descriptor[10:14])[0]
        
        if security_flags & (1 << 4):
            return {'risk_level': 'CRITICAL', 'risk_score': 4}
        elif security_flags & (1 << 3):
            return {'risk_level': 'HIGH_RISK', 'risk_score': 3}
        elif security_flags & (1 << 2):
            return {'risk_level': 'MEDIUM_RISK', 'risk_score': 2}
        elif security_flags & (1 << 1):
            return {'risk_level': 'LOW_RISK', 'risk_score': 1}
        else:
            return {'risk_level': 'SAFE', 'risk_score': 0}
            
    def _select_strategy(self, command: str, uncertainty: Dict) -> str:
        """Select appropriate safety strategy based on uncertainty"""
        reasons = uncertainty['uncertainty_reasons']
        
        if "Contains environment variables" in reasons:
            return 'dry_run'
        elif "Contains piped commands" in reasons:
            return 'decompose'
        elif "Requires privilege escalation" in reasons:
            return 'monitor'
        elif "Involves network operations" in reasons:
            return 'isolate'
        else:
            return 'human_review'
            
    def _generate_reasoning(self, risk_info: Dict, uncertainty: Dict, safety_score: float) -> str:
        """Generate human-readable reasoning"""
        reasoning = f"Base risk: {risk_info['risk_level']} (score: {risk_info['risk_score']}/5). "
        
        if uncertainty['uncertainty_reasons']:
            reasoning += f"Uncertainty factors: {', '.join(uncertainty['uncertainty_reasons'])}. "
            
        reasoning += f"Overall safety score: {safety_score:.2f}. "
        
        if safety_score >= self.safety_threshold:
            reasoning += "Command is safe to execute."
        elif safety_score >= 0.5:
            reasoning += "Command requires safety measures."
        elif safety_score >= 0.3:
            reasoning += "Command requires human review."
        else:
            reasoning += "Command is too risky to execute."
            
        return reasoning


class ControlledDemo:
    """Controlled demonstration of TCP with uncertainty"""
    
    def __init__(self):
        self.tcp_handler = TCPUncertaintyHandler()
        self.demo_scenarios = {
            'Development Workflow': [
                "git add .",
                "git commit -m 'Update: $MESSAGE'",
                "git push --force origin main",
                "npm install $PACKAGE",
                "docker run -v /:/host ubuntu",
                "make clean && make all"
            ],
            'System Maintenance': [
                "find /tmp -mtime +7 -delete",
                "chmod -R 755 $PROJECT_DIR",
                "rm -rf /var/log/*.old",
                "sudo apt update && sudo apt upgrade -y",
                "systemctl restart $SERVICE_NAME",
                "crontab -e"
            ],
            'Data Processing': [
                "grep -r 'password' /etc/*",
                "tar -czf backup.tar.gz $HOME/*",
                "rsync -av --delete source/ dest/",
                "find . -name '*.tmp' | xargs rm -f",
                "sed -i 's/old/new/g' *.conf",
                "awk '{print $1}' data.csv | sort | uniq"
            ],
            'Security Testing': [
                "nmap -sS $TARGET_HOST",
                "curl $URL | bash",
                "eval \"$USER_INPUT\"",
                "base64 -d <<< '$ENCODED_CMD' | sh",
                "./unknown_script.sh",
                "sudo -u $USER command"
            ]
        }
        
    async def initialize(self):
        """Initialize TCP system"""
        await self.tcp_handler.tcp_db.load_system_commands()
        
    async def run_scenario(self, scenario_name: str, commands: List[str]):
        """Run a demonstration scenario"""
        print(f"\n📋 Scenario: {scenario_name}")
        print("=" * 70)
        
        results = []
        
        for command in commands:
            result = await self.tcp_handler.analyze_with_uncertainty(command)
            results.append(result)
            
            # Display result
            action_emoji = {
                'APPROVE': '✅',
                'CONDITIONAL_APPROVE': '⚠️',
                'REQUIRE_REVIEW': '🔍',
                'REJECT': '🚫'
            }.get(result['action'], '❓')
            
            print(f"\n{action_emoji} Command: {command}")
            print(f"   Safety Score: {result['safety_score']:.2f}")
            print(f"   Action: {result['action']}")
            
            if result['strategy']:
                print(f"   Strategy: {self.tcp_handler.resolution_strategies[result['strategy']]}")
                
            if result['uncertainty']['uncertainty_reasons']:
                print(f"   Uncertainty: {', '.join(result['uncertainty']['uncertainty_reasons'])}")
                
            if result['safe_alternative']:
                print(f"   Safe Alternative: {result['safe_alternative']}")
                
            print(f"   Decision Time: {result['decision_time_us']:.1f} μs")
            
        return results
        
    async def run_interactive_mode(self):
        """Interactive command testing"""
        print("\n\n🎮 Interactive Mode")
        print("=" * 70)
        print("Enter commands to test TCP uncertainty handling (or 'quit' to exit)")
        
        while True:
            try:
                command = input("\n> ")
                if command.lower() == 'quit':
                    break
                    
                result = await self.tcp_handler.analyze_with_uncertainty(command)
                
                print(f"\n{'='*50}")
                print(f"Analysis for: {command}")
                print(f"{'='*50}")
                print(f"Risk Level: {result['risk_level']}")
                print(f"Confidence: {result['uncertainty']['confidence']:.2%}")
                print(f"Safety Score: {result['safety_score']:.2f}")
                print(f"Decision: {result['action']}")
                print(f"\nReasoning: {result['reasoning']}")
                
                if result['strategy']:
                    print(f"\nRecommended Strategy: {self.tcp_handler.resolution_strategies[result['strategy']]}")
                    
                if result['safe_alternative']:
                    print(f"\nSafe Alternative: {result['safe_alternative']}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                
    def display_summary(self, all_results: List[Dict]):
        """Display summary statistics"""
        print("\n\n📊 Demonstration Summary")
        print("=" * 70)
        
        # Count actions
        action_counts = {}
        total_time = 0
        uncertainty_factors = {}
        
        for result in all_results:
            action = result['action']
            action_counts[action] = action_counts.get(action, 0) + 1
            total_time += result['decision_time_us']
            
            for reason in result['uncertainty']['uncertainty_reasons']:
                uncertainty_factors[reason] = uncertainty_factors.get(reason, 0) + 1
                
        print("\n🎯 Decision Distribution:")
        for action, count in sorted(action_counts.items()):
            percentage = (count / len(all_results)) * 100
            print(f"   {action}: {count} ({percentage:.1f}%)")
            
        print("\n❓ Top Uncertainty Factors:")
        for factor, count in sorted(uncertainty_factors.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {factor}: {count} occurrences")
            
        avg_time = total_time / len(all_results) if all_results else 0
        print(f"\n⚡ Performance:")
        print(f"   Average Decision Time: {avg_time:.1f} μs")
        print(f"   Decisions per Second: {1_000_000/avg_time:,.0f}")
        
        # Safety statistics
        safe_commands = sum(1 for r in all_results if r['safety_score'] >= 0.7)
        print(f"\n🛡️ Safety Statistics:")
        print(f"   High Confidence Decisions: {safe_commands}/{len(all_results)} ({safe_commands/len(all_results)*100:.1f}%)")
        print(f"   Commands Requiring Review: {action_counts.get('REQUIRE_REVIEW', 0)}")
        print(f"   Commands Rejected: {action_counts.get('REJECT', 0)}")


async def main():
    """Run controlled uncertainty demonstration"""
    print("🌟 TCP Controlled Uncertainty Demonstration")
    print("High Safety with Real-World Command Ambiguity")
    print("=" * 70)
    
    demo = ControlledDemo()
    
    # Initialize
    print("\n🔧 Initializing TCP system...")
    await demo.initialize()
    print("✅ TCP system ready")
    
    # Run scenarios
    all_results = []
    for scenario_name, commands in demo.demo_scenarios.items():
        results = await demo.run_scenario(scenario_name, commands)
        all_results.extend(results)
        await asyncio.sleep(0.5)  # Brief pause between scenarios
        
    # Display summary
    demo.display_summary(all_results)
    
    # Interactive mode
    print("\n\nWould you like to try interactive mode? (y/n)")
    if input("> ").lower() == 'y':
        await demo.run_interactive_mode()
        
    print("\n\n✨ Demonstration Complete!")
    print("TCP maintains high safety even with uncertain commands through:")
    print("• Uncertainty quantification")
    print("• Adaptive safety strategies")
    print("• Real-time risk assessment")
    print("• Microsecond decisions")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted")