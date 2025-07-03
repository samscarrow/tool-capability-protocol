#!/usr/bin/env python3
"""
TCP Descriptor Database: Bridge between native TCP protocol and MCP

Loads and manages TCP binary descriptors from breakthrough research,
designed for future migration to standalone TCP protocol.
"""

import json
import struct
import hashlib
import zlib
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import structlog

logger = structlog.get_logger(__name__)

class TCPDescriptorDatabase:
    """
    TCP Binary Descriptor Database with MCP Bridge Compatibility
    
    Manages 709+ command descriptors from proven TCP research,
    designed for future standalone TCP protocol adoption.
    """
    
    def __init__(self):
        self.descriptors: Dict[str, bytes] = {}
        self.system_stats: Dict[str, Any] = {}
        self.command_families: Dict[str, List[str]] = {}
        self.data_dir = Path(__file__).parent / "data"
        
        # TCP Protocol Configuration (for future standalone mode)
        self.tcp_config = {
            "protocol_version": "2.0",
            "descriptor_size": 24,
            "compression_target": "362:1",
            "bridge_mode": True,  # Will be False in standalone TCP
            "mcp_compatibility": True
        }
    
    async def load_system_commands(self):
        """Load TCP descriptors from research data"""
        logger.info("Loading TCP descriptor database...")
        
        try:
            # Load from existing TCP research if available
            await self._load_from_tcp_research()
            
            # Generate missing descriptors
            await self._generate_missing_descriptors()
            
            # Calculate system statistics
            await self._calculate_system_stats()
            
            logger.info("TCP database loaded", 
                       commands=len(self.descriptors),
                       families=len(self.command_families))
            
        except Exception as e:
            logger.error("Failed to load TCP database", error=str(e))
            # Fallback to basic descriptor generation
            await self._generate_basic_descriptors()
    
    async def _load_from_tcp_research(self):
        """Load descriptors from TCP research breakthrough"""
        research_path = Path(__file__).parent.parent.parent.parent / "experiments" / "tool-capability-protocol"
        
        # Load from comprehensive analysis if available
        analysis_files = list(research_path.glob("comprehensive_tcp_analysis_*.json"))
        if analysis_files:
            latest_analysis = max(analysis_files, key=lambda p: p.stat().st_mtime)
            logger.info("Loading from TCP research", file=latest_analysis.name)
            
            with open(latest_analysis) as f:
                research_data = json.load(f)
            
            # Extract TCP descriptors from research
            families = research_data.get("families", {})
            for family_name, family_data in families.items():
                commands = family_data.get("commands", {})
                self.command_families[family_name] = list(commands.keys())
                
                for command, hex_descriptor in commands.items():
                    try:
                        self.descriptors[command] = bytes.fromhex(hex_descriptor)
                    except ValueError:
                        logger.warning("Invalid hex descriptor", command=command)
            
            logger.info("Loaded TCP research data", 
                       commands_loaded=len(self.descriptors))
        else:
            logger.info("No TCP research data found, will generate descriptors")
    
    async def _generate_missing_descriptors(self):
        """Generate TCP descriptors for common system commands"""
        common_commands = [
            # Critical commands
            "rm", "dd", "shred", "wipefs", "mkfs", "fdisk", "parted", 
            "format", "blkdiscard",
            
            # High-risk commands  
            "sudo", "su", "passwd", "chmod", "chown", "chgrp", "mount", 
            "umount", "kill", "killall", "pkill",
            
            # Medium-risk commands
            "cp", "mv", "curl", "wget", "tar", "zip", "ssh", "scp",
            
            # Low-risk commands
            "ps", "top", "ls", "find", "grep", "cat", "head", "tail",
            
            # Safe commands
            "echo", "printf", "date", "whoami", "id", "uname", "which"
        ]
        
        for command in common_commands:
            if command not in self.descriptors:
                descriptor = self._generate_tcp_descriptor(command)
                self.descriptors[command] = descriptor
                
                # Add to appropriate family
                if command not in self.command_families.get("system", []):
                    if "system" not in self.command_families:
                        self.command_families["system"] = []
                    self.command_families["system"].append(command)
    
    def _generate_tcp_descriptor(self, command: str) -> bytes:
        """Generate 24-byte TCP descriptor for command"""
        
        # Analyze command security characteristics
        risk_level, security_flags = self._analyze_command_security(command)
        
        # Estimate performance characteristics  
        exec_time, memory_mb, output_kb = self._estimate_performance(command)
        
        # Build TCP descriptor according to v2 specification
        magic = b'TCP\x02'
        version = struct.pack('>H', 2)
        cmd_hash = hashlib.md5(command.encode()).digest()[:4]
        security_data = struct.pack('>I', security_flags)
        performance = struct.pack('>IHH', exec_time, memory_mb, output_kb)
        
        # Build descriptor (22 bytes so far)
        data = magic + version + cmd_hash + security_data + performance
        
        # Add CRC16 checksum (2 bytes)
        crc = struct.pack('>H', zlib.crc32(data) & 0xFFFF)
        
        return data + crc
    
    def _analyze_command_security(self, command: str) -> Tuple[str, int]:
        """Analyze command security using TCP research patterns"""
        
        security_flags = 0
        
        # Critical commands - can destroy data permanently
        if command in ['rm', 'dd', 'shred', 'wipefs', 'mkfs', 'fdisk', 'parted', 'format']:
            security_flags |= (1 << 4)  # CRITICAL
            security_flags |= (1 << 7)  # DESTRUCTIVE
            security_flags |= (1 << 10) # SYSTEM_MODIFICATION
            security_flags |= (1 << 9)  # FILE_MODIFICATION
            security_flags |= (1 << 6)  # REQUIRES_ROOT
            risk_level = "CRITICAL"
            
        # High-risk commands - system modifications
        elif command in ['sudo', 'su', 'passwd', 'chmod', 'chown', 'mount', 'umount', 'kill']:
            security_flags |= (1 << 3)  # HIGH_RISK
            security_flags |= (1 << 6)  # REQUIRES_ROOT
            security_flags |= (1 << 10) # SYSTEM_MODIFICATION
            if command in ['kill', 'killall', 'pkill']:
                security_flags |= (1 << 7)  # DESTRUCTIVE
            risk_level = "HIGH_RISK"
            
        # Medium-risk commands - file operations
        elif command in ['cp', 'mv', 'tar', 'zip', 'ssh', 'scp']:
            security_flags |= (1 << 2)  # MEDIUM_RISK  
            security_flags |= (1 << 9)  # FILE_MODIFICATION
            if command in ['ssh', 'scp', 'curl', 'wget']:
                security_flags |= (1 << 8)  # NETWORK_ACCESS
            risk_level = "MEDIUM_RISK"
            
        # Low-risk commands - information gathering
        elif command in ['ps', 'top', 'find', 'grep']:
            security_flags |= (1 << 1)  # LOW_RISK
            risk_level = "LOW_RISK"
            
        # Safe commands - read-only operations
        else:
            security_flags |= (1 << 0)  # SAFE
            risk_level = "SAFE"
        
        return risk_level, security_flags
    
    def _estimate_performance(self, command: str) -> Tuple[int, int, int]:
        """Estimate performance characteristics"""
        
        # Performance estimates based on command type (milliseconds, MB, KB)
        if command in ['dd', 'shred', 'mkfs']:
            return 10000, 1000, 100  # 10s, 1GB, 100KB
        elif command in ['find', 'grep', 'tar']:
            return 2000, 200, 50     # 2s, 200MB, 50KB  
        elif command in ['cp', 'mv', 'ssh']:
            return 1000, 100, 20     # 1s, 100MB, 20KB
        elif command in ['ps', 'top', 'ls']:
            return 500, 50, 10       # 500ms, 50MB, 10KB
        else:
            return 100, 10, 1        # 100ms, 10MB, 1KB
    
    async def _generate_basic_descriptors(self):
        """Fallback: generate basic descriptors for common commands"""
        basic_commands = ["ls", "cat", "echo", "rm", "cp", "mv", "grep", "find"]
        
        for command in basic_commands:
            self.descriptors[command] = self._generate_tcp_descriptor(command)
        
        self.command_families["basic"] = basic_commands
        logger.info("Generated basic TCP descriptors", count=len(basic_commands))
    
    async def _calculate_system_stats(self):
        """Calculate system-wide TCP statistics"""
        total_commands = len(self.descriptors)
        tcp_size = total_commands * 24  # 24 bytes per descriptor
        
        # Estimate traditional documentation size (conservative 125KB per command)
        docs_size_estimate = total_commands * 125 * 1024  # 125KB per command
        
        compression_ratio = docs_size_estimate / tcp_size if tcp_size > 0 else 1
        
        # Analyze risk distribution
        risk_distribution = {"SAFE": 0, "LOW_RISK": 0, "MEDIUM_RISK": 0, "HIGH_RISK": 0, "CRITICAL": 0}
        capabilities = set()
        
        for command, descriptor in self.descriptors.items():
            try:
                analysis = self._decode_descriptor_quick(descriptor)
                risk_distribution[analysis["risk_level"]] += 1
                capabilities.update(analysis["capabilities"])
            except:
                continue
        
        self.system_stats = {
            "command_count": total_commands,
            "tcp_size": tcp_size,
            "docs_size_estimate": docs_size_estimate // 1024,  # KB
            "compression_ratio": int(compression_ratio),
            "risk_distribution": risk_distribution,
            "capabilities": list(capabilities),
            "families": len(self.command_families)
        }
    
    def _decode_descriptor_quick(self, descriptor: bytes) -> Dict[str, Any]:
        """Quick decode of TCP descriptor for statistics"""
        if len(descriptor) != 24:
            return {"risk_level": "UNKNOWN", "capabilities": []}
        
        security_flags = struct.unpack('>I', descriptor[10:14])[0]
        
        # Decode risk level
        if security_flags & (1 << 4):
            risk_level = "CRITICAL"
        elif security_flags & (1 << 3):
            risk_level = "HIGH_RISK"
        elif security_flags & (1 << 2):
            risk_level = "MEDIUM_RISK"
        elif security_flags & (1 << 1):
            risk_level = "LOW_RISK"
        else:
            risk_level = "SAFE"
        
        # Decode capabilities
        capabilities = []
        if security_flags & (1 << 6):
            capabilities.append("REQUIRES_ROOT")
        if security_flags & (1 << 7):
            capabilities.append("DESTRUCTIVE")
        if security_flags & (1 << 8):
            capabilities.append("NETWORK_ACCESS")
        if security_flags & (1 << 9):
            capabilities.append("FILE_MODIFICATION")
        if security_flags & (1 << 10):
            capabilities.append("SYSTEM_MODIFICATION")
        
        return {"risk_level": risk_level, "capabilities": capabilities}
    
    async def get_descriptor(self, command: str) -> bytes:
        """Get TCP descriptor for command"""
        # Clean command (handle arguments)
        base_command = command.split()[0] if ' ' in command else command
        
        if base_command in self.descriptors:
            return self.descriptors[base_command]
        
        # Generate on-demand for unknown commands
        logger.info("Generating TCP descriptor on-demand", command=base_command)
        descriptor = self._generate_tcp_descriptor(base_command)
        self.descriptors[base_command] = descriptor
        
        return descriptor
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide TCP statistics"""
        return self.system_stats.copy()
    
    @property
    def command_count(self) -> int:
        """Number of commands in database"""
        return len(self.descriptors)
    
    def list_commands(self) -> List[str]:
        """List all commands in database"""
        return list(self.descriptors.keys())
    
    def list_families(self) -> List[str]:
        """List all command families"""
        return list(self.command_families.keys())
    
    def get_family_commands(self, family: str) -> List[str]:
        """Get commands in specific family"""
        return self.command_families.get(family, [])
    
    # TCP Protocol Bridge Methods (for future standalone TCP)
    async def tcp_query(self, command: str) -> bytes:
        """Native TCP protocol query (future standalone mode)"""
        return await self.get_descriptor(command)
    
    async def tcp_batch_query(self, commands: List[str]) -> Dict[str, bytes]:
        """Batch TCP queries (future optimization)"""
        results = {}
        for command in commands:
            results[command] = await self.get_descriptor(command)
        return results
    
    def get_tcp_config(self) -> Dict[str, Any]:
        """Get TCP protocol configuration"""
        return self.tcp_config.copy()