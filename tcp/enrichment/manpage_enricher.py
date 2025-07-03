#!/usr/bin/env python3
"""
Man Page Enrichment System for TCP

This system enriches TCP descriptors with comprehensive man page data,
enabling intelligent security classification and risk assessment.
"""

import re
import subprocess
import json

# Optional web requests (fallback gracefully if not available)
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from urllib.parse import quote
import time


class SecurityLevel(Enum):
    """Security risk levels for commands."""
    SAFE = "safe"              # No security risks
    LOW_RISK = "low_risk"      # Minor risks, user-level operations
    MEDIUM_RISK = "medium_risk"  # Can affect user data/environment
    HIGH_RISK = "high_risk"    # System-level operations, potential damage
    CRITICAL = "critical"      # Can destroy system, requires root


class PrivilegeLevel(Enum):
    """Privilege requirements for commands."""
    USER = "user"              # Regular user privileges
    SUDO = "sudo"              # Requires sudo/elevated privileges
    ROOT = "root"              # Must run as root
    SYSTEM = "system"          # System service level


@dataclass
class ManPageData:
    """Structured man page information."""
    command: str
    section: int
    synopsis: str
    description: str
    options: List[Dict[str, str]]
    examples: List[str]
    see_also: List[str]
    security_notes: List[str]
    privilege_requirements: PrivilegeLevel
    security_level: SecurityLevel
    destructive_operations: List[str]
    network_operations: List[str]
    file_operations: List[str]
    system_operations: List[str]


class ManPageEnricher:
    """
    Enriches TCP descriptors with comprehensive man page data and security analysis.
    
    Sources:
    1. Local man pages (primary)
    2. Web-based man page repositories (fallback)
    3. Security databases and CVE information
    4. Known dangerous command patterns
    """
    
    def __init__(self, cache_dir: str = None):
        """Initialize man page enricher."""
        self.cache_dir = Path(cache_dir or Path.cwd() / "manpage_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("manpage_enricher")
        self._setup_logging()
        
        # Initialize security knowledge bases
        self._init_security_databases()
        
        # Web sources for man pages
        self.web_sources = [
            "https://man7.org/linux/man-pages/man1/{command}.1.html",
            "https://www.freebsd.org/cgi/man.cgi?query={command}&sektion=1",
            "https://linux.die.net/man/1/{command}",
            "https://manpages.ubuntu.com/manpages/jammy/man1/{command}.1.html"
        ]
    
    def _setup_logging(self) -> None:
        """Set up logging for enrichment process."""
        log_file = self.cache_dir / "enrichment.log"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] ENRICHER: %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _init_security_databases(self) -> None:
        """Initialize security knowledge databases."""
        
        # Commands that require elevated privileges
        self.privilege_commands = {
            PrivilegeLevel.ROOT: {
                'mount', 'umount', 'fdisk', 'mkfs', 'fsck', 'modprobe', 'rmmod',
                'iptables', 'systemctl', 'service', 'chroot', 'sysctl'
            },
            PrivilegeLevel.SUDO: {
                'sudo', 'su', 'passwd', 'chown', 'chmod', 'kill', 'killall',
                'useradd', 'userdel', 'usermod', 'groupadd', 'groupdel'
            }
        }
        
        # Commands with critical security implications
        self.critical_commands = {
            'rm', 'dd', 'shred', 'wipefs', 'mkfs', 'fdisk', 'parted',
            'format', 'deltree', 'rmdir', 'unlink'
        }
        
        # Commands with high security risk
        self.high_risk_commands = {
            'chmod', 'chown', 'chgrp', 'setuid', 'setgid', 'mount', 'umount',
            'kill', 'killall', 'pkill', 'su', 'sudo', 'passwd', 'crontab'
        }
        
        # Commands with medium security risk
        self.medium_risk_commands = {
            'mv', 'cp', 'tar', 'zip', 'unzip', 'gzip', 'gunzip', 'ssh',
            'scp', 'rsync', 'curl', 'wget', 'nc', 'telnet', 'ftp'
        }
        
        # Destructive operation patterns
        self.destructive_patterns = {
            r'rm\s+.*-[rf]': 'Recursive/force file removal',
            r'dd\s+.*of=': 'Direct disk write operation',
            r'mkfs': 'Filesystem creation (destroys data)',
            r'format': 'Disk formatting operation',
            r'shred': 'Secure file deletion',
            r'wipefs': 'Filesystem signature removal',
            r'>\s*/dev/': 'Direct device write'
        }
        
        # Network operation indicators
        self.network_indicators = {
            'tcp', 'udp', 'http', 'https', 'ftp', 'ssh', 'telnet', 'smtp',
            'connect', 'bind', 'listen', 'socket', 'port', 'host', 'url'
        }
        
        # File operation types
        self.file_operations = {
            'read': ['cat', 'head', 'tail', 'less', 'more', 'grep', 'find'],
            'write': ['cp', 'mv', 'touch', 'echo', 'tee', 'dd'],
            'modify': ['sed', 'awk', 'chmod', 'chown', 'chgrp'],
            'delete': ['rm', 'rmdir', 'unlink', 'shred']
        }
    
    def get_local_manpage(self, command: str) -> Optional[str]:
        """Get man page from local system."""
        try:
            result = subprocess.run(
                ['man', command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"Retrieved local man page for {command}")
                return result.stdout
            else:
                self.logger.warning(f"No local man page found for {command}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout retrieving man page for {command}")
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving local man page for {command}: {e}")
            return None
    
    def get_web_manpage(self, command: str) -> Optional[str]:
        """Get man page from web sources."""
        if not HAS_REQUESTS:
            self.logger.warning("requests module not available, skipping web sources")
            return None
            
        for source_template in self.web_sources:
            try:
                url = source_template.format(command=quote(command))
                self.logger.info(f"Fetching man page from: {url}")
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.logger.info(f"Retrieved web man page for {command} from {url}")
                    return response.text
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                self.logger.warning(f"Failed to fetch from {url}: {e}")
                continue
        
        self.logger.error(f"No web man page found for {command}")
        return None
    
    def parse_manpage_content(self, content: str, command: str) -> ManPageData:
        """Parse man page content into structured data."""
        
        # Extract sections using regex patterns
        synopsis_match = re.search(r'SYNOPSIS\s*\n(.*?)(?=\n[A-Z])', content, re.DOTALL | re.IGNORECASE)
        synopsis = synopsis_match.group(1).strip() if synopsis_match else ""
        
        description_match = re.search(r'DESCRIPTION\s*\n(.*?)(?=\n[A-Z])', content, re.DOTALL | re.IGNORECASE)
        description = description_match.group(1).strip() if description_match else ""
        
        # Extract options
        options = self._parse_options(content)
        
        # Extract examples
        examples = self._parse_examples(content)
        
        # Extract see also
        see_also = self._parse_see_also(content)
        
        # Extract security notes
        security_notes = self._extract_security_notes(content, command)
        
        # Perform security analysis
        privilege_level = self._analyze_privilege_requirements(command, content)
        security_level = self._analyze_security_level(command, content)
        
        # Analyze operation types
        destructive_ops = self._analyze_destructive_operations(command, content)
        network_ops = self._analyze_network_operations(command, content)
        file_ops = self._analyze_file_operations(command, content)
        system_ops = self._analyze_system_operations(command, content)
        
        return ManPageData(
            command=command,
            section=1,  # Default to section 1
            synopsis=synopsis,
            description=description,
            options=options,
            examples=examples,
            see_also=see_also,
            security_notes=security_notes,
            privilege_requirements=privilege_level,
            security_level=security_level,
            destructive_operations=destructive_ops,
            network_operations=network_ops,
            file_operations=file_ops,
            system_operations=system_ops
        )
    
    def _parse_options(self, content: str) -> List[Dict[str, str]]:
        """Parse command options from man page."""
        options = []
        
        # Look for OPTIONS section
        options_match = re.search(r'OPTIONS\s*\n(.*?)(?=\n[A-Z])', content, re.DOTALL | re.IGNORECASE)
        if not options_match:
            return options
        
        options_text = options_match.group(1)
        
        # Parse individual options (simplified pattern)
        option_pattern = r'^\s*(-[a-zA-Z]|--[a-zA-Z-]+)(?:\s+([^-\n]*?))?(?=^\s*-|\Z)'
        
        for match in re.finditer(option_pattern, options_text, re.MULTILINE):
            flag = match.group(1)
            description = match.group(2).strip() if match.group(2) else ""
            
            options.append({
                'flag': flag,
                'description': description
            })
        
        return options
    
    def _parse_examples(self, content: str) -> List[str]:
        """Parse examples from man page."""
        examples = []
        
        # Look for EXAMPLES section
        examples_match = re.search(r'EXAMPLES?\s*\n(.*?)(?=\n[A-Z])', content, re.DOTALL | re.IGNORECASE)
        if examples_match:
            examples_text = examples_match.group(1)
            
            # Extract command lines that start with $ or contain the command
            example_lines = re.findall(r'^\s*\$?\s*([^\n]+)$', examples_text, re.MULTILINE)
            examples.extend(example_lines)
        
        return examples
    
    def _parse_see_also(self, content: str) -> List[str]:
        """Parse 'see also' references."""
        see_also = []
        
        see_also_match = re.search(r'SEE ALSO\s*\n(.*?)(?=\n[A-Z]|\Z)', content, re.DOTALL | re.IGNORECASE)
        if see_also_match:
            see_also_text = see_also_match.group(1)
            
            # Extract command references
            commands = re.findall(r'\b([a-z]+)\([0-9]\)', see_also_text)
            see_also.extend(commands)
        
        return see_also
    
    def _extract_security_notes(self, content: str, command: str) -> List[str]:
        """Extract security-related notes from man page."""
        security_notes = []
        
        # Look for security-related sections
        security_sections = [
            r'SECURITY\s*\n(.*?)(?=\n[A-Z])',
            r'WARNING\s*\n(.*?)(?=\n[A-Z])',
            r'CAUTION\s*\n(.*?)(?=\n[A-Z])',
            r'BUGS?\s*\n(.*?)(?=\n[A-Z])'
        ]
        
        for pattern in security_sections:
            matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                security_notes.append(match.group(1).strip())
        
        # Look for security keywords in description
        security_keywords = [
            'privilege', 'root', 'sudo', 'dangerous', 'caution', 'warning',
            'security', 'risk', 'careful', 'destroy', 'delete', 'remove'
        ]
        
        for keyword in security_keywords:
            if keyword.lower() in content.lower():
                # Extract sentences containing security keywords
                sentences = re.split(r'[.!?]+', content)
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        security_notes.append(sentence.strip())
        
        return list(set(security_notes))  # Remove duplicates
    
    def _analyze_privilege_requirements(self, command: str, content: str) -> PrivilegeLevel:
        """Analyze privilege requirements for command."""
        
        # Check against known privilege databases
        if command in self.privilege_commands[PrivilegeLevel.ROOT]:
            return PrivilegeLevel.ROOT
        
        if command in self.privilege_commands[PrivilegeLevel.SUDO]:
            return PrivilegeLevel.SUDO
        
        # Analyze content for privilege indicators
        privilege_indicators = {
            PrivilegeLevel.ROOT: [
                'must be run as root', 'requires root', 'superuser only',
                'root privileges', 'run as root'
            ],
            PrivilegeLevel.SUDO: [
                'requires sudo', 'administrative privileges', 'elevated privileges',
                'superuser privileges', 'requires administrator'
            ]
        }
        
        content_lower = content.lower()
        
        for level, indicators in privilege_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                return level
        
        return PrivilegeLevel.USER
    
    def _analyze_security_level(self, command: str, content: str) -> SecurityLevel:
        """Analyze security risk level of command."""
        
        # Check against known risk databases
        if command in self.critical_commands:
            return SecurityLevel.CRITICAL
        
        if command in self.high_risk_commands:
            return SecurityLevel.HIGH_RISK
        
        if command in self.medium_risk_commands:
            return SecurityLevel.MEDIUM_RISK
        
        # Analyze content for risk indicators
        content_lower = content.lower()
        
        # Critical risk indicators
        critical_indicators = [
            'destroy', 'format', 'wipe', 'erase', 'delete permanently',
            'irreversible', 'cannot be undone', 'permanent removal'
        ]
        
        if any(indicator in content_lower for indicator in critical_indicators):
            return SecurityLevel.CRITICAL
        
        # High risk indicators
        high_risk_indicators = [
            'system files', 'modify permissions', 'change ownership',
            'kill processes', 'mount filesystem', 'network access'
        ]
        
        if any(indicator in content_lower for indicator in high_risk_indicators):
            return SecurityLevel.HIGH_RISK
        
        # Medium risk indicators
        medium_risk_indicators = [
            'modify files', 'copy files', 'move files', 'download',
            'upload', 'network connection', 'remote access'
        ]
        
        if any(indicator in content_lower for indicator in medium_risk_indicators):
            return SecurityLevel.MEDIUM_RISK
        
        # Default to safe for read-only operations
        safe_indicators = [
            'display', 'show', 'list', 'view', 'read', 'search', 'find'
        ]
        
        if any(indicator in content_lower for indicator in safe_indicators):
            return SecurityLevel.SAFE
        
        return SecurityLevel.LOW_RISK
    
    def _analyze_destructive_operations(self, command: str, content: str) -> List[str]:
        """Analyze potential destructive operations."""
        destructive_ops = []
        
        # Check destructive patterns
        for pattern, description in self.destructive_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                destructive_ops.append(description)
        
        # Check for destructive keywords
        destructive_keywords = [
            'delete', 'remove', 'destroy', 'wipe', 'format', 'erase',
            'overwrite', 'truncate', 'clear', 'purge'
        ]
        
        content_lower = content.lower()
        for keyword in destructive_keywords:
            if keyword in content_lower:
                destructive_ops.append(f"Can {keyword} data")
        
        return list(set(destructive_ops))
    
    def _analyze_network_operations(self, command: str, content: str) -> List[str]:
        """Analyze network operation capabilities."""
        network_ops = []
        
        content_lower = content.lower()
        
        # Check for network indicators
        for indicator in self.network_indicators:
            if indicator in content_lower:
                network_ops.append(f"Supports {indicator}")
        
        # Specific network operation patterns
        network_patterns = {
            r'connect to': 'Can establish connections',
            r'download': 'Can download files',
            r'upload': 'Can upload files',
            r'transfer': 'Can transfer data',
            r'remote': 'Can access remote systems'
        }
        
        for pattern, description in network_patterns.items():
            if re.search(pattern, content_lower):
                network_ops.append(description)
        
        return list(set(network_ops))
    
    def _analyze_file_operations(self, command: str, content: str) -> List[str]:
        """Analyze file operation capabilities."""
        file_ops = []
        
        # Check against known file operations
        for op_type, commands in self.file_operations.items():
            if command in commands:
                file_ops.append(f"Can {op_type} files")
        
        # Analyze content for file operations
        file_patterns = {
            r'read.*file': 'Can read files',
            r'write.*file': 'Can write files',
            r'create.*file': 'Can create files',
            r'copy.*file': 'Can copy files',
            r'move.*file': 'Can move files',
            r'delete.*file': 'Can delete files'
        }
        
        content_lower = content.lower()
        for pattern, description in file_patterns.items():
            if re.search(pattern, content_lower):
                file_ops.append(description)
        
        return list(set(file_ops))
    
    def _analyze_system_operations(self, command: str, content: str) -> List[str]:
        """Analyze system-level operations."""
        system_ops = []
        
        system_patterns = {
            r'process': 'Can manipulate processes',
            r'service': 'Can control services',
            r'mount': 'Can mount filesystems',
            r'kernel': 'Can interact with kernel',
            r'system.*call': 'Can make system calls',
            r'device': 'Can access devices'
        }
        
        content_lower = content.lower()
        for pattern, description in system_patterns.items():
            if re.search(pattern, content_lower):
                system_ops.append(description)
        
        return list(set(system_ops))
    
    def enrich_command(self, command: str) -> Optional[ManPageData]:
        """Enrich a command with comprehensive man page data."""
        self.logger.info(f"Enriching command: {command}")
        
        # Check cache first
        cache_file = self.cache_dir / f"{command}_manpage.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    
                    # Convert string enums back to enum objects
                    if 'security_level' in cached_data:
                        if isinstance(cached_data['security_level'], str):
                            # Handle both "SecurityLevel.CRITICAL" and "critical" formats
                            level_str = cached_data['security_level']
                            if level_str.startswith('SecurityLevel.'):
                                level_str = level_str.split('.')[1].lower()
                            cached_data['security_level'] = SecurityLevel(level_str)
                    
                    if 'privilege_requirements' in cached_data:
                        if isinstance(cached_data['privilege_requirements'], str):
                            # Handle both "PrivilegeLevel.USER" and "user" formats
                            priv_str = cached_data['privilege_requirements']
                            if priv_str.startswith('PrivilegeLevel.'):
                                priv_str = priv_str.split('.')[1].lower()
                            cached_data['privilege_requirements'] = PrivilegeLevel(priv_str)
                    
                    return ManPageData(**cached_data)
            except Exception as e:
                self.logger.warning(f"Failed to load cached data for {command}: {e}")
        
        # Try local man page first
        content = self.get_local_manpage(command)
        
        # Fallback to web sources
        if not content:
            content = self.get_web_manpage(command)
        
        if not content:
            self.logger.error(f"No man page content found for {command}")
            return None
        
        # Parse content
        manpage_data = self.parse_manpage_content(content, command)
        
        # Cache the result
        try:
            with open(cache_file, 'w') as f:
                json.dump(asdict(manpage_data), f, indent=2, default=str)
            self.logger.info(f"Cached enriched data for {command}")
        except Exception as e:
            self.logger.warning(f"Failed to cache data for {command}: {e}")
        
        return manpage_data
    
    def batch_enrich_commands(self, commands: List[str]) -> Dict[str, ManPageData]:
        """Enrich multiple commands in batch."""
        self.logger.info(f"Batch enriching {len(commands)} commands")
        
        enriched_data = {}
        
        for i, command in enumerate(commands, 1):
            self.logger.info(f"Processing {i}/{len(commands)}: {command}")
            
            try:
                data = self.enrich_command(command)
                if data:
                    enriched_data[command] = data
                    self.logger.info(f"Successfully enriched {command}")
                else:
                    self.logger.warning(f"Failed to enrich {command}")
                    
            except Exception as e:
                self.logger.error(f"Error enriching {command}: {e}")
            
            # Rate limiting for web requests
            if i % 10 == 0:
                time.sleep(1)
        
        self.logger.info(f"Batch enrichment complete: {len(enriched_data)}/{len(commands)} successful")
        return enriched_data


def main():
    """Demonstrate man page enrichment system."""
    print("📚 MAN PAGE ENRICHMENT SYSTEM")
    print("=" * 60)
    print("Enriching TCP descriptors with comprehensive man page data")
    print("and intelligent security classification...")
    print()
    
    # Initialize enricher
    enricher = ManPageEnricher()
    
    # Test commands with varying security levels
    test_commands = [
        'cat',      # Safe
        'grep',     # Safe  
        'cp',       # Medium risk
        'chmod',    # High risk
        'rm',       # Critical
        'sudo',     # Critical
        'curl',     # Medium risk (network)
        'find',     # Low risk
    ]
    
    print("🔍 Enriching test commands...")
    print("-" * 40)
    
    for command in test_commands:
        print(f"\n📖 Enriching: {command}")
        
        data = enricher.enrich_command(command)
        
        if data:
            print(f"   Security Level: {data.security_level.value}")
            print(f"   Privilege Required: {data.privilege_requirements.value}")
            print(f"   File Operations: {len(data.file_operations)}")
            print(f"   Network Operations: {len(data.network_operations)}")
            print(f"   Destructive Operations: {len(data.destructive_operations)}")
            print(f"   Security Notes: {len(data.security_notes)}")
            
            if data.destructive_operations:
                print(f"   ⚠️  Destructive: {', '.join(data.destructive_operations[:2])}")
                
        else:
            print("   ❌ Failed to enrich")
    
    print(f"\n📊 ENRICHMENT SUMMARY:")
    print("-" * 40)
    print("✅ Man page data extracted and parsed")
    print("✅ Security levels automatically classified")
    print("✅ Privilege requirements determined")
    print("✅ Operation types analyzed")
    print("✅ Risk factors identified")
    print()
    print("🧠 NAIVE AGENT BENEFITS:")
    print("• Can inherently understand security risks")
    print("• Knows which commands need special privileges") 
    print("• Identifies potentially destructive operations")
    print("• Understands network and file operation capabilities")
    print("• Makes informed security decisions automatically")


if __name__ == "__main__":
    main()