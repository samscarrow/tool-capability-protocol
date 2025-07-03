#!/usr/bin/env python3
"""
Focused Bcachefs Analysis: LLM vs TCP-Only
Compares detailed analysis of key bcachefs commands
"""

import struct
import hashlib
import zlib
from datetime import datetime

def analyze_with_llm_knowledge(command: str) -> dict:
    """My LLM analysis based on bcachefs documentation knowledge"""
    
    analyses = {
        'bcachefs format': {
            'risk_level': 'critical',
            'risk_score': 1.0,
            'destructive': True,
            'requires_root': True,
            'description': 'Formats devices with bcachefs filesystem, permanently destroying all existing data. Creates superblocks, allocates initial structures.',
            'specific_risks': [
                'Permanently destroys ALL data on target devices',
                'Cannot be undone - no recovery possible',
                'Can accidentally format wrong device with parameter typo',
                'Supports multi-device arrays - can destroy multiple disks at once',
                'Creates encrypted filesystems that can lock out data forever'
            ],
            'capabilities': ['format_device', 'destroy_data', 'create_fs', 'multi_device'],
            'safe_usage': 'Never safe - always destructive',
            'prerequisites': 'Unmounted devices, backup verification, double-check device paths'
        },
        
        'bcachefs fsck': {
            'risk_level': 'high', 
            'risk_score': 0.8,
            'destructive': False,
            'requires_root': True,
            'description': 'Filesystem checker and repair tool. Can modify metadata to fix corruption but may cause data loss during aggressive repairs.',
            'specific_risks': [
                'Auto-repair mode can delete corrupted files',
                'May modify filesystem metadata unexpectedly',
                'Can mark files as unrecoverable during repair',
                'Should only run on unmounted filesystems',
                'May take hours on large filesystems'
            ],
            'capabilities': ['check_fs', 'repair_fs', 'modify_metadata'],
            'safe_usage': 'Read-only check mode (-n flag)',
            'prerequisites': 'Filesystem must be unmounted, recent backup recommended'
        },
        
        'bcachefs device add': {
            'risk_level': 'high',
            'risk_score': 0.7,
            'destructive': False,
            'requires_root': True,
            'description': 'Adds new device to existing bcachefs filesystem. Changes filesystem topology and data placement.',
            'specific_risks': [
                'Changes data distribution across devices',
                'New device becomes integral to filesystem - cannot remove without migration',
                'Can affect performance characteristics',
                'May trigger rebalancing operations that take time',
                'Wrong device type can impact durability'
            ],
            'capabilities': ['modify_fs', 'add_device', 'change_topology'],
            'safe_usage': 'Only with proper planning and testing',
            'prerequisites': 'Filesystem mounted, compatible device, sufficient space'
        },
        
        'bcachefs device remove': {
            'risk_level': 'high',
            'risk_score': 0.8,
            'destructive': True,
            'requires_root': True,
            'description': 'Removes device from bcachefs filesystem. Must migrate all data off device first.',
            'specific_risks': [
                'Data loss if evacuation fails',
                'Can make filesystem unmountable if done incorrectly',
                'May trigger lengthy data migration',
                'Cannot remove last device of a durability tier',
                'Interrupted removal can corrupt filesystem'
            ],
            'capabilities': ['modify_fs', 'remove_device', 'migrate_data'],
            'safe_usage': 'Only with verified successful evacuation',
            'prerequisites': 'Mounted filesystem, successful data evacuation, no errors'
        },
        
        'bcachefs migrate': {
            'risk_level': 'critical',
            'risk_score': 0.9,
            'destructive': True,
            'requires_root': True,
            'description': 'Migrates existing ext4/xfs filesystem to bcachefs in-place. Extremely dangerous operation.',
            'specific_risks': [
                'Can destroy entire filesystem if interrupted',
                'No rollback possible once started',
                'Source filesystem must be perfect - any corruption causes failure',
                'Extremely complex operation with many failure modes',
                'Power loss during migration = complete data loss'
            ],
            'capabilities': ['convert_fs', 'destroy_data', 'modify_fs'],
            'safe_usage': 'Never without complete offline backup',
            'prerequisites': 'Perfect source filesystem, complete backup, UPS, extensive testing'
        },
        
        'bcachefs show-super': {
            'risk_level': 'safe',
            'risk_score': 0.1,
            'destructive': False,
            'requires_root': False,
            'description': 'Displays superblock information. Read-only operation that analyzes filesystem metadata.',
            'specific_risks': [
                'Can reveal sensitive filesystem details',
                'May fail on corrupted superblocks'
            ],
            'capabilities': ['read_metadata', 'display_info'],
            'safe_usage': 'Always safe for information gathering',
            'prerequisites': 'None - can run on any bcachefs device'
        },
        
        'bcachefs list': {
            'risk_level': 'safe',
            'risk_score': 0.1,
            'destructive': False,
            'requires_root': False,
            'description': 'Lists bcachefs filesystems and their components. Read-only discovery operation.',
            'specific_risks': [
                'Minimal risk - only reads filesystem information'
            ],
            'capabilities': ['list_fs', 'read_metadata'],
            'safe_usage': 'Always safe',
            'prerequisites': 'None'
        },
        
        'bcachefs fs usage': {
            'risk_level': 'safe',
            'risk_score': 0.1,
            'destructive': False,
            'requires_root': False,
            'description': 'Shows filesystem usage statistics. Read-only operation.',
            'specific_risks': [
                'No risks - purely informational'
            ],
            'capabilities': ['read_stats', 'display_usage'],
            'safe_usage': 'Always safe',
            'prerequisites': 'Mounted filesystem'
        }
    }
    
    return analyses.get(command, {
        'risk_level': 'unknown',
        'risk_score': 0.5,
        'description': f'Unknown bcachefs command: {command}',
        'specific_risks': ['Unknown operation - assume moderate risk'],
        'capabilities': ['unknown'],
        'safe_usage': 'Unknown',
        'prerequisites': 'Unknown'
    })

def analyze_with_tcp_only(command: str) -> dict:
    """Generate TCP descriptor using only command name pattern analysis"""
    
    security_flags = 0
    
    # Pattern-based risk assessment
    if any(word in command.lower() for word in ['format', 'mkfs']):
        security_flags |= (1 << 4)  # CRITICAL
        security_flags |= (1 << 7)  # DESTRUCTIVE
        security_flags |= (1 << 10) # SYSTEM_MODIFICATION
        security_flags |= (1 << 9)  # FILE_MODIFICATION
        risk_level = 'critical'
        exec_time = 30000  # 30 seconds
        memory_mb = 1000
        
    elif any(word in command.lower() for word in ['migrate', 'convert']):
        security_flags |= (1 << 4)  # CRITICAL
        security_flags |= (1 << 7)  # DESTRUCTIVE
        security_flags |= (1 << 10) # SYSTEM_MODIFICATION
        risk_level = 'critical'
        exec_time = 60000  # 60 seconds
        memory_mb = 2000
        
    elif any(word in command.lower() for word in ['remove', 'delete', 'destroy']):
        security_flags |= (1 << 3)  # HIGH_RISK
        security_flags |= (1 << 7)  # DESTRUCTIVE
        security_flags |= (1 << 10) # SYSTEM_MODIFICATION
        risk_level = 'high'
        exec_time = 10000  # 10 seconds
        memory_mb = 500
        
    elif any(word in command.lower() for word in ['fsck', 'repair', 'check']):
        security_flags |= (1 << 3)  # HIGH_RISK
        security_flags |= (1 << 10) # SYSTEM_MODIFICATION
        security_flags |= (1 << 9)  # FILE_MODIFICATION
        risk_level = 'high'
        exec_time = 15000  # 15 seconds
        memory_mb = 300
        
    elif any(word in command.lower() for word in ['add', 'device']):
        security_flags |= (1 << 3)  # HIGH_RISK
        security_flags |= (1 << 10) # SYSTEM_MODIFICATION
        risk_level = 'high'
        exec_time = 5000  # 5 seconds
        memory_mb = 200
        
    elif any(word in command.lower() for word in ['mount', 'unmount']):
        security_flags |= (1 << 2)  # MEDIUM_RISK
        security_flags |= (1 << 10) # SYSTEM_MODIFICATION
        risk_level = 'medium'
        exec_time = 2000  # 2 seconds
        memory_mb = 100
        
    elif any(word in command.lower() for word in ['show', 'list', 'usage', 'info', 'version']):
        security_flags |= (1 << 0)  # SAFE
        risk_level = 'safe'
        exec_time = 100  # 100ms
        memory_mb = 10
        
    else:
        # Unknown bcachefs operation - assume high risk
        security_flags |= (1 << 3)  # HIGH_RISK
        risk_level = 'high'
        exec_time = 2000
        memory_mb = 100
    
    # All bcachefs operations likely need root
    security_flags |= (1 << 6)  # REQUIRES_ROOT
    
    # Generate binary descriptor
    magic = b'TCP\x02'
    version = struct.pack('>H', 2)
    cmd_hash = hashlib.md5(command.encode()).digest()[:4]
    security_data = struct.pack('>I', security_flags)
    performance = struct.pack('>HHH', exec_time, memory_mb, 50)  # 50KB output
    reserved = struct.pack('>H', len(command))
    
    data = magic + version + cmd_hash + security_data + performance + reserved
    crc = struct.pack('>H', zlib.crc32(data) & 0xFFFF)
    descriptor = data + crc
    
    # Decode insights
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
        'risk_level': risk_level,
        'security_flags': f'0x{security_flags:08x}',
        'descriptor_hex': descriptor.hex(),
        'descriptor_size': len(descriptor),
        'exec_time_ms': exec_time,
        'memory_mb': memory_mb,
        'insights': ' '.join(insights),
        'analysis_method': 'tcp_pattern_only'
    }

def compare_analysis_methods():
    """Compare LLM knowledge vs TCP-only analysis for key bcachefs commands"""
    
    test_commands = [
        'bcachefs format',
        'bcachefs fsck', 
        'bcachefs device add',
        'bcachefs device remove',
        'bcachefs migrate',
        'bcachefs show-super',
        'bcachefs list',
        'bcachefs fs usage'
    ]
    
    print("🔬 FOCUSED BCACHEFS ANALYSIS: LLM vs TCP-ONLY")
    print("=" * 80)
    print("Comparing detailed command analysis using two approaches:")
    print("1. LLM: Deep knowledge of bcachefs documentation and behavior")
    print("2. TCP: Pattern-only analysis from command names (no external knowledge)")
    print("=" * 80)
    print()
    
    results = []
    
    for i, command in enumerate(test_commands, 1):
        print(f"[{i}/{len(test_commands)}] ANALYZING: {command}")
        print("-" * 60)
        
        # LLM Analysis
        print("🧠 LLM ANALYSIS (with bcachefs knowledge):")
        llm_result = analyze_with_llm_knowledge(command)
        print(f"   Risk Level: {llm_result['risk_level']} (score: {llm_result.get('risk_score', 0):.1f})")
        print(f"   Destructive: {llm_result.get('destructive', 'unknown')}")
        print(f"   Description: {llm_result['description'][:80]}...")
        print(f"   Key Risks: {len(llm_result.get('specific_risks', []))} specific risks identified")
        if llm_result.get('specific_risks'):
            print(f"   Top Risk: {llm_result['specific_risks'][0][:60]}...")
        print()
        
        # TCP Analysis
        print("🔀 TCP ANALYSIS (pattern-only, no external knowledge):")
        tcp_result = analyze_with_tcp_only(command)
        print(f"   Risk Level: {tcp_result['risk_level']}")
        print(f"   Security Flags: {tcp_result['security_flags']}")
        print(f"   Agent Insights: {tcp_result['insights']}")
        print(f"   Descriptor: {tcp_result['descriptor_hex'][:32]}... ({tcp_result['descriptor_size']} bytes)")
        print(f"   Runtime Estimate: {tcp_result['exec_time_ms']}ms")
        print()
        
        # Comparison
        print("⚖️  COMPARISON:")
        risk_match = llm_result['risk_level'] == tcp_result['risk_level']
        print(f"   Risk Level Match: {'✅' if risk_match else '❌'} LLM={llm_result['risk_level']}, TCP={tcp_result['risk_level']}")
        
        llm_destructive = llm_result.get('destructive', False)
        tcp_destructive = '💥' in tcp_result['insights']
        destructive_match = llm_destructive == tcp_destructive
        print(f"   Destructive Match: {'✅' if destructive_match else '❌'} LLM={llm_destructive}, TCP={tcp_destructive}")
        
        # Agreement score
        agreement = (risk_match + destructive_match) / 2
        print(f"   Agreement Score: {agreement*100:.0f}%")
        
        if not risk_match:
            print(f"   ⚠️  Risk assessment differs: This could lead to different safety decisions")
        
        results.append({
            'command': command,
            'llm': llm_result,
            'tcp': tcp_result,
            'agreement': agreement,
            'risk_match': risk_match,
            'destructive_match': destructive_match
        })
        
        print("\n" + "="*80 + "\n")
    
    # Summary Analysis
    print("📊 COMPARATIVE ANALYSIS SUMMARY")
    print("=" * 80)
    
    avg_agreement = sum(r['agreement'] for r in results) / len(results)
    perfect_matches = sum(1 for r in results if r['agreement'] == 1.0)
    risk_matches = sum(1 for r in results if r['risk_match'])
    
    print(f"Commands Analyzed: {len(results)}")
    print(f"Average Agreement: {avg_agreement*100:.1f}%")
    print(f"Perfect Matches: {perfect_matches}/{len(results)}")
    print(f"Risk Level Matches: {risk_matches}/{len(results)}")
    print()
    
    # Critical disagreements
    critical_disagreements = []
    for result in results:
        llm_critical = result['llm']['risk_level'] == 'critical'
        tcp_critical = result['tcp']['risk_level'] == 'critical'
        if llm_critical != tcp_critical:
            critical_disagreements.append(result)
    
    if critical_disagreements:
        print("🚨 CRITICAL RISK ASSESSMENT DISAGREEMENTS:")
        for result in critical_disagreements:
            cmd = result['command']
            llm_risk = result['llm']['risk_level']
            tcp_risk = result['tcp']['risk_level']
            print(f"   {cmd}: LLM={llm_risk}, TCP={tcp_risk}")
        print()
    
    # Specific insights
    print("🔍 KEY INSIGHTS:")
    print()
    
    print("💡 TCP Binary Descriptor Advantages:")
    print("   ✅ Instant analysis (no external knowledge required)")
    print("   ✅ Consistent pattern-based classification")
    print("   ✅ Works for unknown commands")
    print(f"   ✅ Complete analysis in {len(results)*24} bytes total")
    print("   ✅ No dependency on documentation or training")
    print()
    
    print("💡 LLM Analysis Advantages:")
    print("   ✅ Deep understanding of actual command behavior")
    print("   ✅ Context-aware risk assessment")
    print("   ✅ Specific risk identification (interruption, power loss, etc.)")
    print("   ✅ Usage prerequisites and safety recommendations")
    print("   ✅ Understanding of complex interactions (multi-device, encryption)")
    print()
    
    print("⚠️  Critical Differences:")
    print("   • TCP might miss nuanced risks (e.g., 'bcachefs show-super' is safe)")
    print("   • LLM provides actionable safety advice TCP cannot")
    print("   • TCP provides consistent binary flags for agent decision-making")
    print("   • LLM offers detailed explanations humans need")
    print()
    
    print("🎯 Conclusion:")
    print(f"TCP achieved {avg_agreement*100:.0f}% agreement with expert LLM analysis using only")
    print("command name patterns. This demonstrates that:")
    print("• Binary descriptors can capture essential security intelligence")
    print("• Pattern-based analysis scales to unknown tools") 
    print("• 24-byte descriptors enable instant agent safety decisions")
    print("• LLM analysis remains valuable for human understanding and edge cases")

if __name__ == "__main__":
    compare_analysis_methods()