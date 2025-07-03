#!/usr/bin/env python3
"""
Comprehensive Hierarchical TCP Encoding
Process git + all previous commands with first and second-order encoding
"""

import os
import subprocess
import json
import struct
import hashlib
import zlib
import time
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime

class ComprehensiveTCPEncoder:
    """Complete TCP encoding system with hierarchical compression"""
    
    def __init__(self):
        self.first_order_cache = {}
        self.hierarchical_cache = {}
        self.tool_families = {}
        
    def discover_git_commands(self) -> List[Tuple[str, str]]:
        """Discover all git commands and subcommands"""
        commands = []
        
        # Get main git command
        if os.path.exists('/usr/bin/git'):
            commands.append(('git', '/usr/bin/git'))
        
        # Get git subcommands
        try:
            # Get list of git commands
            result = subprocess.run(['git', 'help', '-a'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                in_main_commands = False
                in_ancillary_commands = False
                
                for line in lines:
                    line = line.strip()
                    
                    if 'Main porcelain commands' in line:
                        in_main_commands = True
                        continue
                    elif 'Ancillary Commands' in line:
                        in_ancillary_commands = True
                        in_main_commands = False
                        continue
                    elif line.startswith('Low-level commands') or line.startswith('External commands'):
                        break
                    
                    if (in_main_commands or in_ancillary_commands) and line:
                        # Parse command lines like "  add        Add file contents to the index"
                        if line.startswith('  ') and not line.startswith('   '):
                            parts = line.split()
                            if parts and len(parts[0]) > 1:
                                cmd_name = parts[0]
                                # Skip obvious non-commands
                                if not any(skip in cmd_name for skip in ['--', 'help', 'version']):
                                    commands.append((f'git {cmd_name}', 'git'))
            
            # Also try git --list-cmds
            result2 = subprocess.run(['git', '--list-cmds=main'], 
                                   capture_output=True, text=True, timeout=3)
            if result2.returncode == 0:
                for line in result2.stdout.strip().split('\n'):
                    cmd = line.strip()
                    if cmd and cmd not in [c[0].split(' ', 1)[1] for c in commands if ' ' in c[0]]:
                        commands.append((f'git {cmd}', 'git'))
                        
        except Exception as e:
            print(f"Warning: Could not discover git commands: {e}")
        
        return sorted(set(commands))
    
    def analyze_command_security(self, command: str, path: str) -> Tuple[str, int, str]:
        """Analyze command security with enhanced git knowledge"""
        
        # Enhanced git command analysis
        git_security_db = {
            # CRITICAL - Can destroy data permanently
            'critical': {
                'commands': {
                    'git reset --hard', 'git clean -fd', 'git clean -fdx', 
                    'git filter-branch', 'git rebase -i', 'git push --force',
                    'git rm --cached', 'git rm -rf', 'git branch -D',
                    'git tag -d', 'git reflog expire', 'git gc --prune=now',
                    'git push --delete', 'git reset --hard HEAD~'
                },
                'patterns': ['reset.*--hard', 'clean.*-f', 'push.*--force', 'filter-branch', 'rm.*-rf'],
                'flags': 0x000006d0  # CRITICAL + DESTRUCTIVE + ROOT + SYSTEM + FILE
            },
            
            # HIGH RISK - Can modify repository state significantly
            'high_risk': {
                'commands': {
                    'git rebase', 'git merge', 'git cherry-pick', 'git revert',
                    'git commit --amend', 'git reset', 'git stash drop',
                    'git branch -m', 'git remote set-url', 'git submodule',
                    'git worktree', 'git bisect', 'git archive', 'git bundle'
                },
                'patterns': ['rebase', 'merge', 'reset', 'commit.*--amend', 'stash.*drop'],
                'flags': 0x00000648  # HIGH + ROOT + SYSTEM + FILE
            },
            
            # MEDIUM RISK - Modify working directory or index
            'medium_risk': {
                'commands': {
                    'git add', 'git commit', 'git checkout', 'git switch',
                    'git rm', 'git mv', 'git restore', 'git stash',
                    'git apply', 'git am', 'git format-patch', 'git send-email',
                    'git clone', 'git fetch', 'git pull', 'git push'
                },
                'patterns': ['add', 'commit', 'checkout', 'clone', 'push', 'pull'],
                'flags': 0x00000244  # MEDIUM + FILE
            },
            
            # LOW RISK - Information gathering, might reveal sensitive data
            'low_risk': {
                'commands': {
                    'git log', 'git show', 'git diff', 'git blame', 'git annotate',
                    'git grep', 'git ls-files', 'git ls-tree', 'git cat-file',
                    'git rev-list', 'git describe', 'git name-rev'
                },
                'patterns': ['log', 'show', 'diff', 'blame', 'grep', 'ls-'],
                'flags': 0x00000002  # LOW
            },
            
            # SAFE - Pure information display
            'safe': {
                'commands': {
                    'git status', 'git branch', 'git tag', 'git remote',
                    'git config --list', 'git version', 'git help',
                    'git rev-parse', 'git symbolic-ref', 'git for-each-ref'
                },
                'patterns': ['status', 'branch', 'help', 'version', 'config.*--list'],
                'flags': 0x00000001  # SAFE
            }
        }
        
        # Non-git command analysis (from previous system)
        general_security_db = {
            'critical': {
                'commands': {'rm', 'dd', 'shred', 'wipefs', 'mkfs', 'fdisk', 'parted',
                           'format', 'blkdiscard', 'badblocks', 'mdadm', 'lvm'},
                'flags': 0x000006d0
            },
            'high_risk': {
                'commands': {'sudo', 'su', 'passwd', 'chmod', 'chown', 'chgrp', 
                           'mount', 'umount', 'kill', 'killall', 'pkill'},
                'flags': 0x00000648
            },
            'medium_risk': {
                'commands': {'cp', 'mv', 'curl', 'wget', 'tar', 'zip', 'ssh', 'scp'},
                'flags': 0x00000244
            },
            'low_risk': {
                'commands': {'ps', 'top', 'ls', 'find', 'grep', 'cat', 'head', 'tail'},
                'flags': 0x00000002
            },
            'safe': {
                'commands': {'echo', 'printf', 'date', 'whoami', 'id', 'uname'},
                'flags': 0x00000001
            }
        }
        
        # Determine which database to use
        if command.startswith('git '):
            security_db = git_security_db
            base_cmd = command
        else:
            security_db = general_security_db
            base_cmd = command.split()[0]
        
        # Check against security database
        for level, data in security_db.items():
            # Direct command match
            if base_cmd in data['commands']:
                return level, data['flags'], f"Direct match: {level}"
            
            # Pattern match for git commands
            if 'patterns' in data:
                for pattern in data['patterns']:
                    if pattern in command.lower():
                        return level, data['flags'], f"Pattern match: {pattern}"
        
        # Default for unknown commands
        if 'git' in command:
            return 'medium_risk', 0x00000244, "Unknown git command - default medium risk"
        else:
            return 'low_risk', 0x00000002, "Unknown command - default low risk"
    
    def create_first_order_tcp(self, command: str, path: str) -> bytes:
        """Create standard 24-byte TCP descriptor"""
        
        risk_level, security_flags, reason = self.analyze_command_security(command, path)
        
        # Get file size if possible
        try:
            file_size = os.path.getsize(path) if path != 'git' else 50000000  # Git is ~50MB
        except:
            file_size = 1000000  # 1MB default
        
        # Performance estimates based on risk and command type
        if risk_level == 'critical':
            exec_time, memory_mb = 10000, 1000  # 10s, 1GB
        elif risk_level == 'high_risk':
            exec_time, memory_mb = 5000, 500    # 5s, 500MB
        elif risk_level == 'medium_risk':
            exec_time, memory_mb = 2000, 200    # 2s, 200MB
        elif risk_level == 'low_risk':
            exec_time, memory_mb = 500, 50      # 500ms, 50MB
        else:  # safe
            exec_time, memory_mb = 100, 10      # 100ms, 10MB
        
        # Build TCP descriptor
        magic = b'TCP\x02'
        version = struct.pack('>H', 2)
        cmd_hash = hashlib.md5(command.encode()).digest()[:4]
        security_data = struct.pack('>I', security_flags)
        performance = struct.pack('>HHH', exec_time, memory_mb, min(file_size//1024, 65535))
        reserved = struct.pack('>H', len(command))
        
        data = magic + version + cmd_hash + security_data + performance + reserved
        crc = struct.pack('>H', zlib.crc32(data) & 0xFFFF)
        
        return data + crc
    
    def group_commands_by_family(self, commands: List[Tuple[str, str]]) -> Dict[str, List[Tuple[str, str]]]:
        """Group commands by tool family"""
        families = defaultdict(list)
        
        for command, path in commands:
            if ' ' in command:
                # Multi-word command like "git add"
                parent = command.split(' ')[0]
                families[parent].append((command, path))
            else:
                # Single command
                families[command].append((command, path))
        
        return dict(families)
    
    def create_hierarchical_encoding(self, family_name: str, commands: List[Tuple[str, str]]) -> Dict:
        """Create hierarchical encoding for a command family"""
        
        if len(commands) <= 1:
            # Single command - no benefit from hierarchical encoding
            if commands:
                cmd, path = commands[0]
                tcp_desc = self.create_first_order_tcp(cmd, path)
                return {
                    'family_name': family_name,
                    'encoding_type': 'single_command',
                    'commands': {cmd: tcp_desc.hex()},
                    'original_size': 24,
                    'compressed_size': 24,
                    'compression_ratio': 1.0,
                    'parent_descriptor': None,
                    'delta_descriptors': {}
                }
            return {}
        
        # Multi-command family - use hierarchical encoding
        
        # Generate first-order TCP for all commands
        tcp_descriptors = {}
        for cmd, path in commands:
            tcp_descriptors[cmd] = self.create_first_order_tcp(cmd, path)
        
        # Analyze common properties
        all_flags = []
        risk_levels = []
        
        for tcp_desc in tcp_descriptors.values():
            flags = struct.unpack('>I', tcp_desc[10:14])[0]
            all_flags.append(flags)
            
            # Determine risk level from flags
            if flags & (1 << 4):
                risk_levels.append(4)  # CRITICAL
            elif flags & (1 << 3):
                risk_levels.append(3)  # HIGH
            elif flags & (1 << 2):
                risk_levels.append(2)  # MEDIUM
            elif flags & (1 << 1):
                risk_levels.append(1)  # LOW
            else:
                risk_levels.append(0)  # SAFE
        
        # Create parent descriptor (16 bytes)
        magic = b'TCP\x03'  # Hierarchical version
        family_hash = hashlib.md5(family_name.encode()).digest()[:4]
        
        # Common flags analysis
        common_flags = 0
        if all(flags & (1 << 6) for flags in all_flags):  # All require root
            common_flags |= (1 << 0)
        if len(commands) > 10:
            common_flags |= (1 << 1)  # Large family
        if any(flags & (1 << 7) for flags in all_flags):  # Has destructive
            common_flags |= (1 << 2)
        if any(flags & (1 << 0) for flags in all_flags):  # Has safe
            common_flags |= (1 << 3)
        
        # Determine tool family type
        family_props = 0
        if family_name in ['git', 'svn', 'hg']:
            family_props |= (1 << 0)  # Version control
        elif family_name in ['bcachefs', 'mkfs', 'mount']:
            family_props |= (1 << 1)  # Filesystem
        elif family_name in ['docker', 'kubectl', 'systemctl']:
            family_props |= (1 << 2)  # System management
        
        risk_floor = min(risk_levels) if risk_levels else 0
        
        parent_data = (magic + family_hash + 
                      struct.pack('>H', common_flags) +
                      struct.pack('B', min(len(commands), 255)) +
                      struct.pack('B', risk_floor) +
                      struct.pack('>H', family_props))
        
        parent_crc = struct.pack('>H', zlib.crc32(parent_data) & 0xFFFF)
        parent_descriptor = parent_data + parent_crc
        
        # Create delta descriptors
        delta_descriptors = {}
        
        for cmd, tcp_desc in tcp_descriptors.items():
            # Extract subcommand (everything after first space)
            if ' ' in cmd:
                subcmd = cmd.split(' ', 1)[1]
            else:
                subcmd = cmd
            
            # Create delta (8 bytes for complex commands)
            subcmd_hash = hash(subcmd) & 0xFF
            
            flags = struct.unpack('>I', tcp_desc[10:14])[0]
            exec_time = struct.unpack('>H', tcp_desc[14:16])[0]
            memory_mb = struct.unpack('>H', tcp_desc[16:18])[0]
            
            # Risk level
            if flags & (1 << 4):
                risk_level = 4
            elif flags & (1 << 3):
                risk_level = 3
            elif flags & (1 << 2):
                risk_level = 2
            elif flags & (1 << 1):
                risk_level = 1
            else:
                risk_level = 0
            
            risk_delta = max(0, risk_level - risk_floor)
            
            # Capability flags (compress to 16 bits)
            cap_flags = 0
            if flags & (1 << 7):   # DESTRUCTIVE
                cap_flags |= (1 << 0)
            if flags & (1 << 9):   # FILE_MODIFICATION
                cap_flags |= (1 << 1)
            if flags & (1 << 10):  # SYSTEM_MODIFICATION
                cap_flags |= (1 << 2)
            if flags & (1 << 8):   # NETWORK_ACCESS
                cap_flags |= (1 << 3)
            if flags & (1 << 11):  # PRIVILEGE_ESCALATION
                cap_flags |= (1 << 4)
            
            # Logarithmic encoding for performance
            import math
            exec_log = min(15, max(0, int(math.log2(max(1, exec_time // 100)))))
            mem_log = min(15, max(0, int(math.log2(max(1, memory_mb // 10)))))
            perf_byte = (exec_log << 4) | mem_log
            
            # Build delta (8 bytes)
            delta = struct.pack('BBHBBB',
                              subcmd_hash,
                              risk_delta,
                              cap_flags,
                              perf_byte,
                              len(subcmd),
                              len(cmd))  # Full command length
            
            delta_descriptors[cmd] = delta
        
        # Calculate compression stats
        original_size = len(commands) * 24
        compressed_size = 16 + sum(len(delta) for delta in delta_descriptors.values())
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        
        return {
            'family_name': family_name,
            'encoding_type': 'hierarchical',
            'command_count': len(commands),
            'commands': {cmd: tcp_desc.hex() for cmd, tcp_desc in tcp_descriptors.items()},
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'space_saved': original_size - compressed_size,
            'parent_descriptor': parent_descriptor.hex(),
            'parent_size': len(parent_descriptor),
            'delta_descriptors': {cmd: delta.hex() for cmd, delta in delta_descriptors.items()},
            'delta_sizes': {cmd: len(delta) for cmd, delta in delta_descriptors.items()}
        }
    
    def process_all_commands(self):
        """Process all commands with comprehensive TCP encoding"""
        
        print("🌍 COMPREHENSIVE TCP ENCODING - FIRST & SECOND ORDER")
        print("=" * 80)
        print("Processing all system commands with hierarchical compression")
        print("Special focus: Git command family analysis")
        print("=" * 80)
        print()
        
        # Discover all available commands
        print("🔍 DISCOVERING COMMANDS...")
        
        # Get git commands
        print("  • Git commands...")
        git_commands = self.discover_git_commands()
        print(f"    Found {len(git_commands)} git commands")
        
        # Get critical system commands from previous analysis
        print("  • System commands...")
        system_commands = [
            ('rm', '/usr/bin/rm'),
            ('dd', '/usr/bin/dd'),
            ('cp', '/usr/bin/cp'),
            ('mv', '/usr/bin/mv'),
            ('cat', '/usr/bin/cat'),
            ('grep', '/usr/bin/grep'),
            ('find', '/usr/bin/find'),
            ('chmod', '/usr/bin/chmod'),
            ('chown', '/usr/bin/chown'),
            ('sudo', '/usr/bin/sudo'),
            ('mount', '/usr/bin/mount'),
            ('umount', '/usr/bin/umount')
        ]
        
        # Add bcachefs commands
        print("  • Bcachefs commands...")
        bcachefs_commands = [
            ('bcachefs format', 'bcachefs'),
            ('bcachefs fsck', 'bcachefs'),
            ('bcachefs device add', 'bcachefs'),
            ('bcachefs device remove', 'bcachefs'),
            ('bcachefs migrate', 'bcachefs'),
            ('bcachefs show-super', 'bcachefs'),
            ('bcachefs list', 'bcachefs'),
            ('bcachefs fs usage', 'bcachefs')
        ]
        
        all_commands = git_commands + system_commands + bcachefs_commands
        print(f"  📊 Total commands: {len(all_commands)}")
        print()
        
        # Group by families
        print("👨‍👩‍👧‍👦 GROUPING INTO FAMILIES...")
        families = self.group_commands_by_family(all_commands)
        
        for family, cmds in families.items():
            print(f"  {family}: {len(cmds)} commands")
        print()
        
        # Process each family
        print("⚙️ PROCESSING FAMILIES...")
        results = {}
        total_original = 0
        total_compressed = 0
        
        for family_name, commands in families.items():
            print(f"\n[{family_name}] Processing {len(commands)} commands...")
            
            result = self.create_hierarchical_encoding(family_name, commands)
            if result:
                results[family_name] = result
                total_original += result['original_size']
                total_compressed += result['compressed_size']
                
                if result['encoding_type'] == 'hierarchical':
                    ratio = result['compression_ratio']
                    saved = result['space_saved']
                    print(f"  ✅ {result['original_size']}B → {result['compressed_size']}B ({ratio:.1f}:1, saved {saved}B)")
                else:
                    print(f"  ➡️  Single command: {result['original_size']}B (no compression)")
        
        # Generate comprehensive report
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE ANALYSIS RESULTS")
        print("=" * 80)
        
        print(f"\nTool Families Processed: {len(results)}")
        print(f"Total Commands: {sum(r['command_count'] if 'command_count' in r else 1 for r in results.values())}")
        print(f"Overall Compression: {total_original}B → {total_compressed}B ({total_original/total_compressed:.1f}:1)")
        print(f"Total Space Saved: {total_original - total_compressed}B")
        
        # Detailed family analysis
        print("\n🔍 FAMILY-BY-FAMILY BREAKDOWN:")
        print("-" * 60)
        
        for family_name, result in sorted(results.items(), key=lambda x: x[1].get('compression_ratio', 1), reverse=True):
            if result['encoding_type'] == 'hierarchical':
                print(f"{family_name:15} | {result['command_count']:3d} cmds | "
                      f"{result['original_size']:4d}B → {result['compressed_size']:3d}B | "
                      f"{result['compression_ratio']:4.1f}:1")
            else:
                print(f"{family_name:15} | {1:3d} cmd  | "
                      f"{result['original_size']:4d}B → {result['compressed_size']:3d}B | "
                      f"{'1.0':>4s}:1")
        
        # Git-specific analysis
        if 'git' in results:
            git_result = results['git']
            print(f"\n🔬 GIT DETAILED ANALYSIS:")
            print(f"Commands: {git_result['command_count']}")
            print(f"Compression: {git_result['compression_ratio']:.1f}:1")
            print(f"Parent descriptor: {git_result['parent_size']} bytes")
            print(f"Average delta size: {sum(git_result['delta_sizes'].values()) / len(git_result['delta_sizes']):.1f} bytes")
            
            # Show sample git commands by risk level
            print("\nSample Git Commands by Risk Level:")
            git_samples = {
                'Critical': ['git reset --hard', 'git clean -fd', 'git push --force'],
                'High': ['git rebase', 'git merge', 'git reset'],
                'Medium': ['git add', 'git commit', 'git push'],
                'Safe': ['git status', 'git log', 'git help']
            }
            
            for level, samples in git_samples.items():
                available = [cmd for cmd in samples if cmd in git_result['commands']]
                if available:
                    print(f"  {level:8}: {', '.join(available[:3])}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'comprehensive_tcp_analysis_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump({
                'analysis_timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_families': len(results),
                    'total_commands': sum(r.get('command_count', 1) for r in results.values()),
                    'original_size': total_original,
                    'compressed_size': total_compressed,
                    'overall_compression_ratio': total_original / total_compressed if total_compressed > 0 else 1.0,
                    'space_saved': total_original - total_compressed
                },
                'families': results
            }, f, indent=2)
        
        print(f"\n💾 Complete analysis saved to: {filename}")
        
        # Final insights
        print(f"\n🎯 KEY INSIGHTS:")
        print(f"• Git family achieved {results.get('git', {}).get('compression_ratio', 1):.1f}:1 compression")
        print(f"• Hierarchical encoding scales with family size")
        print(f"• Total system intelligence: {total_compressed} bytes")
        print(f"• Traditional approach would require: ~{total_original * 125} bytes of documentation")
        print(f"• TCP achieves ~{(total_original * 125) // total_compressed}:1 overall compression vs docs")
        
        return results


def main():
    """Run comprehensive TCP encoding analysis"""
    encoder = ComprehensiveTCPEncoder()
    encoder.process_all_commands()


if __name__ == "__main__":
    main()