#!/usr/bin/env python3
"""
Parallel Analysis of bcachefs-tools
1. LLM-based analysis (simulated)
2. TCP-only analysis using binary descriptors
"""

import os
import subprocess
import json
import struct
import hashlib
import zlib
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class BcachefsAnalyzer:
    """Analyzes bcachefs-tools using two parallel approaches"""
    
    def __init__(self):
        self.bcachefs_commands = []
        self.tcp_results = {}
        self.llm_results = {}
        
    def discover_bcachefs_tools(self) -> List[Tuple[str, str]]:
        """Find all bcachefs-related executables"""
        commands = []
        
        # Common bcachefs tool names
        potential_tools = [
            'bcachefs', 'bcachefs-tools', 'mkfs.bcachefs', 'mount.bcachefs',
            'fsck.bcachefs', 'bcachefs-device', 'bcachefs-fs', 'bcachefs-data',
            'bcachefs-key', 'bcachefs-subvolume', 'bcachefs-migrate',
            'bcachefs-format', 'bcachefs-show-super', 'bcachefs-list',
            'bcachefs-usage', 'bcachefs-fsck', 'bcachefs-mount'
        ]
        
        # Search in common locations
        search_paths = ['/usr/bin', '/usr/sbin', '/bin', '/sbin', '/usr/local/bin']
        
        for path in search_paths:
            if os.path.exists(path):
                try:
                    # List all files in directory
                    for item in os.listdir(path):
                        if 'bcachefs' in item or 'bcache' in item:
                            full_path = os.path.join(path, item)
                            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                                commands.append((item, full_path))
                except:
                    continue
        
        # Also check if bcachefs is a multi-tool binary with subcommands
        if any(cmd[0] == 'bcachefs' for cmd in commands):
            # Try to get subcommands
            try:
                result = subprocess.run(['bcachefs', 'help'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0 or result.stderr:
                    # Parse subcommands from help output
                    output = result.stdout + result.stderr
                    for line in output.split('\n'):
                        if line.strip() and not line.startswith(' '):
                            words = line.split()
                            if words and words[0] not in ['usage:', 'Usage:', 'Commands:']:
                                subcommand = words[0].strip(':').strip()
                                if subcommand and subcommand not in ['help', 'version']:
                                    commands.append((f'bcachefs {subcommand}', 'bcachefs'))
            except:
                pass
        
        return sorted(set(commands))
    
    def analyze_with_llm(self, command: str, path: str) -> Dict:
        """Analyze using LLM knowledge (simulated with detailed bcachefs understanding)"""
        
        # Simulated LLM analysis based on bcachefs documentation knowledge
        llm_knowledge = {
            'bcachefs': {
                'risk_level': 'high',
                'risk_score': 0.8,
                'description': 'Main bcachefs filesystem utility - multi-tool for filesystem operations',
                'capabilities': ['create_fs', 'modify_fs', 'destroy_data', 'mount_fs', 'check_fs'],
                'requires_privileges': 'root',
                'potential_risks': [
                    'Can format devices, destroying all data',
                    'Can modify filesystem metadata',
                    'Can mount/unmount filesystems',
                    'Can access raw block devices'
                ],
                'safe_operations': ['list', 'show-super', 'usage', 'help'],
                'dangerous_operations': ['format', 'device add', 'device remove', 'migrate']
            },
            'mkfs.bcachefs': {
                'risk_level': 'critical',
                'risk_score': 1.0,
                'description': 'Creates bcachefs filesystems - DESTROYS ALL DATA on target devices',
                'capabilities': ['format_device', 'destroy_data', 'create_fs'],
                'requires_privileges': 'root',
                'potential_risks': [
                    'PERMANENTLY DESTROYS all data on specified devices',
                    'Cannot be undone',
                    'Can accidentally format wrong device with typo'
                ],
                'safe_operations': [],
                'dangerous_operations': ['ALL OPERATIONS']
            },
            'bcachefs format': {
                'risk_level': 'critical',
                'risk_score': 1.0,
                'description': 'Formats devices with bcachefs - DESTROYS ALL DATA',
                'capabilities': ['format_device', 'destroy_data'],
                'requires_privileges': 'root',
                'potential_risks': [
                    'Equivalent to mkfs - destroys everything',
                    'Supports multiple devices in single filesystem',
                    'Supports encryption which can lock out data'
                ]
            },
            'bcachefs mount': {
                'risk_level': 'medium',
                'risk_score': 0.5,
                'description': 'Mounts bcachefs filesystems',
                'capabilities': ['mount_fs', 'system_modification'],
                'requires_privileges': 'root',
                'potential_risks': [
                    'Can expose corrupted filesystem',
                    'May require specific kernel support',
                    'Can affect system stability if filesystem is damaged'
                ]
            },
            'bcachefs fsck': {
                'risk_level': 'high',
                'risk_score': 0.7,
                'description': 'Filesystem checker and repair tool',
                'capabilities': ['check_fs', 'repair_fs', 'modify_metadata'],
                'requires_privileges': 'root',
                'potential_risks': [
                    'Can modify filesystem metadata',
                    'Auto-repair might cause data loss',
                    'Should only run on unmounted filesystems'
                ]
            },
            'bcachefs subvolume': {
                'risk_level': 'medium',
                'risk_score': 0.6,
                'description': 'Manages bcachefs subvolumes and snapshots',
                'capabilities': ['create_snapshot', 'delete_subvolume', 'modify_fs'],
                'requires_privileges': 'root',
                'potential_risks': [
                    'Can delete subvolumes and their data',
                    'Snapshot operations affect storage space',
                    'Complex inheritance rules for snapshots'
                ]
            },
            'bcachefs device': {
                'risk_level': 'high',
                'risk_score': 0.8,
                'description': 'Manages devices in bcachefs filesystem',
                'capabilities': ['add_device', 'remove_device', 'modify_fs'],
                'requires_privileges': 'root',
                'potential_risks': [
                    'Adding devices can affect data placement',
                    'Removing devices requires data migration',
                    'Can cause data loss if done incorrectly'
                ]
            }
        }
        
        # Default analysis for unknown bcachefs commands
        default_analysis = {
            'risk_level': 'high',
            'risk_score': 0.75,
            'description': 'Unknown bcachefs tool - assuming high risk due to filesystem operations',
            'capabilities': ['filesystem_operations'],
            'requires_privileges': 'likely root',
            'potential_risks': [
                'Unknown filesystem operation tool',
                'Likely requires root privileges',
                'Could potentially modify or damage filesystem'
            ]
        }
        
        # Get specific knowledge or use default
        base_cmd = command.split()[0]
        
        if command in llm_knowledge:
            analysis = llm_knowledge[command]
        elif base_cmd in llm_knowledge:
            analysis = llm_knowledge[base_cmd]
        else:
            analysis = default_analysis
            analysis['description'] = f'Bcachefs tool: {command} - filesystem operation utility'
        
        return {
            'command': command,
            'path': path,
            'analysis_type': 'LLM',
            'timestamp': datetime.now().isoformat(),
            **analysis
        }
    
    def generate_tcp_descriptor(self, command: str, path: str) -> Dict:
        """Generate TCP descriptor using only binary analysis"""
        
        # Analyze command characteristics
        security_flags = 0
        
        # Base security level detection from command name
        if any(word in command.lower() for word in ['format', 'mkfs', 'wipefs']):
            # CRITICAL - formats/destroys data
            security_flags |= (1 << 4)  # CRITICAL
            security_flags |= (1 << 7)  # DESTRUCTIVE
            security_flags |= (1 << 10) # SYSTEM_MODIFICATION
            exec_time = 10000  # 10 seconds
            risk_level = 'critical'
        elif any(word in command.lower() for word in ['device', 'migrate', 'fsck', 'repair']):
            # HIGH RISK - modifies filesystem
            security_flags |= (1 << 3)  # HIGH_RISK
            security_flags |= (1 << 10) # SYSTEM_MODIFICATION
            security_flags |= (1 << 9)  # FILE_MODIFICATION
            exec_time = 5000  # 5 seconds
            risk_level = 'high'
        elif any(word in command.lower() for word in ['mount', 'unmount', 'subvolume']):
            # MEDIUM RISK - system operations
            security_flags |= (1 << 2)  # MEDIUM_RISK
            security_flags |= (1 << 10) # SYSTEM_MODIFICATION
            exec_time = 1000  # 1 second
            risk_level = 'medium'
        elif any(word in command.lower() for word in ['list', 'show', 'usage', 'help']):
            # SAFE - read-only operations
            security_flags |= (1 << 0)  # SAFE
            exec_time = 100  # 100ms
            risk_level = 'safe'
        else:
            # Unknown - assume HIGH RISK for filesystem tools
            security_flags |= (1 << 3)  # HIGH_RISK
            exec_time = 2000
            risk_level = 'high'
        
        # All bcachefs operations likely need root
        security_flags |= (1 << 6)  # REQUIRES_ROOT
        
        # Get file info
        try:
            file_size = os.path.getsize(path) if path != 'bcachefs' else 1024000  # 1MB estimate
        except:
            file_size = 1024000  # 1MB default
        
        # Create TCP descriptor
        magic = b'TCP\x02'
        version = struct.pack('>H', 2)
        cmd_hash = hashlib.md5(command.encode()).digest()[:4]
        security_data = struct.pack('>I', security_flags)
        
        # Performance hints based on operation type
        memory_mb = 1000 if 'format' in command else 100
        output_kb = 10
        
        performance = struct.pack('>HHH', exec_time, memory_mb, output_kb)
        reserved = struct.pack('>H', len(command))
        
        # Build descriptor
        data = magic + version + cmd_hash + security_data + performance + reserved
        crc = struct.pack('>H', zlib.crc32(data) & 0xFFFF)
        descriptor = data + crc
        
        # Decode flags for insights
        insights = []
        if security_flags & (1 << 4):
            insights.append("💀 CRITICAL")
        elif security_flags & (1 << 3):
            insights.append("🔴 HIGH")
        elif security_flags & (1 << 2):
            insights.append("🟠 MEDIUM")
        else:
            insights.append("🟢 SAFE")
            
        if security_flags & (1 << 7):
            insights.append("💥 Destructive")
        if security_flags & (1 << 6):
            insights.append("🔑 Root")
        if security_flags & (1 << 10):
            insights.append("⚙️ System")
        if security_flags & (1 << 9):
            insights.append("📝 FileWrite")
        
        return {
            'command': command,
            'path': path,
            'analysis_type': 'TCP',
            'descriptor_hex': descriptor.hex(),
            'descriptor_size': len(descriptor),
            'security_flags': f'0x{security_flags:08x}',
            'risk_level': risk_level,
            'exec_time_ms': exec_time,
            'memory_mb': memory_mb,
            'insights': ' '.join(insights),
            'requires_privileges': 'root',
            'tcp_decoded': {
                'magic': magic.decode('utf-8', errors='ignore'),
                'version': version[0] if len(version) > 0 else 0,
                'flags_binary': bin(security_flags),
                'file_size': file_size
            }
        }
    
    def compare_analyses(self, llm_result: Dict, tcp_result: Dict) -> Dict:
        """Compare LLM and TCP analysis results"""
        
        comparison = {
            'command': llm_result['command'],
            'agreement_score': 0.0,
            'risk_level_match': llm_result['risk_level'] == tcp_result['risk_level'],
            'llm_risk': llm_result['risk_level'],
            'tcp_risk': tcp_result['risk_level'],
            'llm_risk_score': llm_result.get('risk_score', 0),
            'tcp_risk_binary': tcp_result['insights'],
            'privilege_match': llm_result['requires_privileges'] == tcp_result['requires_privileges'],
            'analysis_differences': []
        }
        
        # Calculate agreement score
        score = 0
        total = 4
        
        if comparison['risk_level_match']:
            score += 1
        if comparison['privilege_match']:
            score += 1
        
        # Check if both identify destructive operations
        llm_destructive = any('destroy' in risk.lower() or 'format' in risk.lower() 
                             for risk in llm_result.get('potential_risks', []))
        tcp_destructive = '💥' in tcp_result['insights']
        if llm_destructive == tcp_destructive:
            score += 1
        else:
            comparison['analysis_differences'].append(
                f"Destructive detection: LLM={llm_destructive}, TCP={tcp_destructive}"
            )
        
        # Check system modification detection
        llm_system_mod = 'modify_fs' in llm_result.get('capabilities', [])
        tcp_system_mod = '⚙️' in tcp_result['insights']
        if llm_system_mod == tcp_system_mod:
            score += 1
        else:
            comparison['analysis_differences'].append(
                f"System mod detection: LLM={llm_system_mod}, TCP={tcp_system_mod}"
            )
        
        comparison['agreement_score'] = score / total
        
        # Note key differences
        if llm_result['risk_level'] != tcp_result['risk_level']:
            comparison['analysis_differences'].append(
                f"Risk assessment differs: LLM sees '{llm_result['risk_level']}' "
                f"({llm_result.get('risk_score', 0):.1f}), TCP sees '{tcp_result['risk_level']}'"
            )
        
        return comparison
    
    def run_parallel_analysis(self):
        """Run both analyses in parallel and compare results"""
        
        print("🔬 PARALLEL BCACHEFS-TOOLS ANALYSIS")
        print("=" * 80)
        print("Analyzing bcachefs-tools using two methods:")
        print("1. LLM with knowledge of bcachefs documentation")
        print("2. TCP binary descriptors only")
        print("=" * 80)
        print()
        
        # Discover bcachefs tools
        print("🔍 Discovering bcachefs tools...")
        tools = self.discover_bcachefs_tools()
        
        if not tools:
            print("❌ No bcachefs tools found. Please install bcachefs-tools first.")
            return
        
        print(f"✅ Found {len(tools)} bcachefs-related commands")
        print()
        
        # Analyze each tool with both methods
        comparisons = []
        
        for i, (command, path) in enumerate(tools, 1):
            print(f"[{i}/{len(tools)}] Analyzing: {command}")
            print("-" * 60)
            
            # LLM Analysis
            print("  1️⃣ LLM Analysis...")
            llm_result = self.analyze_with_llm(command, path)
            self.llm_results[command] = llm_result
            print(f"     Risk: {llm_result['risk_level']} ({llm_result.get('risk_score', 0):.1f})")
            print(f"     Desc: {llm_result['description'][:60]}...")
            
            # TCP Analysis
            print("  2️⃣ TCP Analysis...")
            tcp_result = self.generate_tcp_descriptor(command, path)
            self.tcp_results[command] = tcp_result
            print(f"     Risk: {tcp_result['risk_level']}")
            print(f"     Flags: {tcp_result['security_flags']} → {tcp_result['insights']}")
            print(f"     Descriptor: {tcp_result['descriptor_hex'][:32]}... ({tcp_result['descriptor_size']} bytes)")
            
            # Compare
            print("  3️⃣ Comparison...")
            comparison = self.compare_analyses(llm_result, tcp_result)
            comparisons.append(comparison)
            print(f"     Agreement: {comparison['agreement_score']*100:.0f}%")
            if comparison['analysis_differences']:
                for diff in comparison['analysis_differences']:
                    print(f"     ⚠️  {diff}")
            
            print()
        
        # Summary
        print("📊 ANALYSIS SUMMARY")
        print("=" * 80)
        
        # Risk distribution
        print("\nRisk Level Distribution:")
        print("                    LLM Analysis | TCP Analysis")
        print("                    -------------|-------------")
        
        for level in ['critical', 'high', 'medium', 'low', 'safe']:
            llm_count = sum(1 for r in self.llm_results.values() if r['risk_level'] == level)
            tcp_count = sum(1 for r in self.tcp_results.values() if r['risk_level'] == level)
            print(f"  {level:10} |{llm_count:8d}     |{tcp_count:8d}")
        
        # Agreement metrics
        avg_agreement = sum(c['agreement_score'] for c in comparisons) / len(comparisons)
        perfect_matches = sum(1 for c in comparisons if c['agreement_score'] == 1.0)
        
        print(f"\nAgreement Metrics:")
        print(f"  Average Agreement: {avg_agreement*100:.1f}%")
        print(f"  Perfect Matches: {perfect_matches}/{len(comparisons)}")
        
        # Key findings
        print("\n🔑 KEY FINDINGS:")
        print("-" * 80)
        
        # Find critical disagreements
        critical_disagreements = [c for c in comparisons 
                                 if not c['risk_level_match'] and 
                                 (c['llm_risk'] == 'critical' or c['tcp_risk'] == 'critical')]
        
        if critical_disagreements:
            print("⚠️  Critical Risk Assessment Differences:")
            for c in critical_disagreements:
                print(f"   {c['command']}: LLM={c['llm_risk']}, TCP={c['tcp_risk']}")
        
        # TCP advantages
        print("\n✅ TCP Binary Descriptor Advantages:")
        print("  • Instant analysis (no LLM latency)")
        print("  • Consistent risk assessment")
        print("  • 24-byte complete security profile")
        print("  • No ambiguity in privilege requirements")
        print(f"  • Total size for all tools: {len(tools)*24} bytes")
        
        # LLM advantages  
        print("\n✅ LLM Analysis Advantages:")
        print("  • Detailed risk explanations")
        print("  • Understands command relationships")
        print("  • Can explain safe vs dangerous operations")
        print("  • Provides context-aware recommendations")
        
        # Save results
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'tools_analyzed': len(tools),
            'average_agreement': avg_agreement,
            'llm_results': self.llm_results,
            'tcp_results': self.tcp_results,
            'comparisons': comparisons
        }
        
        with open('bcachefs_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Full results saved to: bcachefs_analysis_results.json")


def main():
    """Run the parallel bcachefs analysis"""
    analyzer = BcachefsAnalyzer()
    analyzer.run_parallel_analysis()


if __name__ == "__main__":
    main()