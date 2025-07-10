#!/usr/bin/env python3
"""
TCP Man Page Refinery - Use man pages as ground truth with local Ollama
Refines TCP descriptors by analyzing actual man page documentation
"""

import subprocess
import json
import time
import re
import os
from typing import Dict, List, Tuple, Optional
import hashlib
import struct


class TCPManPageRefinery:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.man_cache = {}
        self.refined_descriptors = {}
        self.refinement_stats = {
            "total_processed": 0,
            "man_pages_found": 0,
            "successfully_refined": 0,
            "failed": 0,
        }

    def get_man_page(self, command: str) -> Optional[str]:
        """Extract man page content for a command"""
        if command in self.man_cache:
            return self.man_cache[command]

        try:
            # Try to get the man page
            result = subprocess.run(
                ["man", command],
                capture_output=True,
                text=True,
                env={**os.environ, "MANPAGER": "cat", "MANWIDTH": "80"},
            )

            if result.returncode == 0 and result.stdout:
                # Clean up the man page text
                man_text = result.stdout
                # Remove backspace sequences
                man_text = re.sub(r".\x08", "", man_text)
                # Limit to first 2000 chars for LLM processing
                man_text = man_text[:2000]

                self.man_cache[command] = man_text
                return man_text

        except Exception as e:
            print(f"   ⚠️ Error getting man page for {command}: {e}")

        return None

    def extract_key_sections(self, man_page: str) -> Dict[str, str]:
        """Extract key sections from man page"""
        sections = {
            "synopsis": "",
            "description": "",
            "options": "",
            "warnings": "",
            "see_also": "",
        }

        # Simple section extraction
        current_section = None
        lines = man_page.split("\n")

        for line in lines:
            line_upper = line.strip().upper()

            # Detect section headers
            if line_upper in [
                "SYNOPSIS",
                "DESCRIPTION",
                "OPTIONS",
                "FLAGS",
                "WARNINGS",
                "CAUTION",
                "BUGS",
                "SEE ALSO",
            ]:
                if "SYNOPSIS" in line_upper:
                    current_section = "synopsis"
                elif "DESCRIPTION" in line_upper:
                    current_section = "description"
                elif any(opt in line_upper for opt in ["OPTIONS", "FLAGS"]):
                    current_section = "options"
                elif any(warn in line_upper for warn in ["WARNING", "CAUTION", "BUGS"]):
                    current_section = "warnings"
                elif "SEE ALSO" in line_upper:
                    current_section = "see_also"
                continue

            # Collect section content
            if current_section and line.strip():
                sections[current_section] += line + "\n"
                # Limit section size
                if len(sections[current_section]) > 500:
                    sections[current_section] = sections[current_section][:500] + "..."

        return sections

    def analyze_with_ollama(
        self,
        command: str,
        man_sections: Dict[str, str],
        model: str = "tinyllama:latest",
    ) -> Dict:
        """Analyze command using man page ground truth with Ollama"""

        # Build focused prompt with man page context
        prompt = f"""Analyze the Unix command '{command}' based on its official man page documentation.

SYNOPSIS:
{man_sections['synopsis'][:200]}

DESCRIPTION:
{man_sections['description'][:300]}

{f"WARNINGS/CAUTIONS:{chr(10)}{man_sections['warnings'][:200]}" if man_sections['warnings'] else ""}

Based on this official documentation, provide:
1. Risk level: SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, or CRITICAL
2. Primary capabilities (what it can do)
3. Security concerns from the man page
4. Whether it requires sudo/root

Be precise and base your assessment on the man page content. Keep under 150 words."""

        try:
            # Make request to Ollama
            cmd = [
                "curl",
                "-s",
                "-X",
                "POST",
                f"{self.ollama_url}/api/generate",
                "-d",
                json.dumps(
                    {
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistency
                            "num_predict": 200,
                            "seed": 42,
                        },
                    }
                ),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                response = json.loads(result.stdout)
                analysis = response.get("response", "")

                # Extract risk level
                risk = self.extract_risk_level(analysis)

                # Extract capabilities
                capabilities = self.extract_capabilities(analysis, man_sections)

                return {
                    "command": command,
                    "risk": risk,
                    "capabilities": capabilities,
                    "analysis": analysis,
                    "man_page_used": True,
                    "model": model,
                }

        except Exception as e:
            print(f"   ❌ Ollama error for {command}: {e}")

        return None

    def extract_risk_level(self, analysis: str) -> str:
        """Extract risk level from analysis"""
        analysis_upper = analysis.upper()

        # Check for explicit risk mentions
        if "CRITICAL" in analysis_upper:
            return "CRITICAL"
        elif "HIGH RISK" in analysis_upper or "HIGH_RISK" in analysis_upper:
            return "HIGH_RISK"
        elif "MEDIUM RISK" in analysis_upper or "MEDIUM_RISK" in analysis_upper:
            return "MEDIUM_RISK"
        elif "LOW RISK" in analysis_upper or "LOW_RISK" in analysis_upper:
            return "LOW_RISK"
        elif "SAFE" in analysis_upper:
            return "SAFE"

        # Infer from content
        danger_words = [
            "destroy",
            "delete",
            "remove",
            "format",
            "wipe",
            "erase",
            "kill",
        ]
        if any(word in analysis_upper for word in danger_words):
            return "HIGH_RISK"

        return "MEDIUM_RISK"  # Default

    def extract_capabilities(
        self, analysis: str, man_sections: Dict[str, str]
    ) -> List[str]:
        """Extract capabilities from analysis and man page"""
        capabilities = []

        combined_text = (analysis + " " + man_sections.get("description", "")).lower()

        # File operations
        if any(
            word in combined_text
            for word in ["file", "directory", "filesystem", "read", "write"]
        ):
            capabilities.append("FILE_OPS")

        # Network operations
        if any(
            word in combined_text
            for word in ["network", "socket", "port", "tcp", "udp", "http"]
        ):
            capabilities.append("NETWORK")

        # Process control
        if any(
            word in combined_text
            for word in ["process", "pid", "signal", "kill", "terminate"]
        ):
            capabilities.append("PROCESS")

        # System modification
        if any(
            word in combined_text
            for word in ["system", "kernel", "module", "service", "daemon"]
        ):
            capabilities.append("SYSTEM")

        # Destructive operations
        if any(
            word in combined_text
            for word in ["delete", "remove", "destroy", "format", "wipe"]
        ):
            capabilities.append("DESTRUCTIVE")

        # Requires privileges
        if any(
            word in combined_text
            for word in ["root", "sudo", "privilege", "permission"]
        ):
            capabilities.append("SUDO")

        return list(set(capabilities))  # Remove duplicates

    def create_refined_descriptor(self, command: str, analysis: Dict) -> bytes:
        """Create refined TCP binary descriptor"""
        # Risk level mapping
        risk_flags = {
            "SAFE": 0x01,
            "LOW_RISK": 0x02,
            "MEDIUM_RISK": 0x04,
            "HIGH_RISK": 0x08,
            "CRITICAL": 0x10,
        }

        # Capability flags
        cap_flags = 0
        cap_mapping = {
            "FILE_OPS": 0x0100,
            "NETWORK": 0x0200,
            "SUDO": 0x0400,
            "DESTRUCTIVE": 0x0800,
            "SYSTEM": 0x1000,
            "PROCESS": 0x2000,
        }

        for cap in analysis.get("capabilities", []):
            if cap in cap_mapping:
                cap_flags |= cap_mapping[cap]

        # Build descriptor
        magic = b"TCP\x02"
        version = struct.pack(">H", 2)
        cmd_hash = hashlib.md5(command.encode()).digest()[:4]
        security_flags = struct.pack(
            ">I", risk_flags.get(analysis["risk"], 0) | cap_flags
        )

        # Performance placeholders
        exec_time = struct.pack(">I", 100)
        memory = struct.pack(">H", 10)
        output = struct.pack(">H", 1)

        # Calculate CRC
        data = magic + version + cmd_hash + security_flags + exec_time + memory + output
        crc = struct.pack(">H", sum(data) & 0xFFFF)

        return data + crc

    def refine_command(
        self, command: str, existing_analysis: Optional[Dict] = None
    ) -> Dict:
        """Refine a single command using man page ground truth"""
        print(f"\n🔧 Refining: {command}")

        self.refinement_stats["total_processed"] += 1

        # Get man page
        man_page = self.get_man_page(command)
        if not man_page:
            print(f"   ❌ No man page found")
            self.refinement_stats["failed"] += 1
            return None

        self.refinement_stats["man_pages_found"] += 1
        print(f"   ✓ Man page found ({len(man_page)} chars)")

        # Extract key sections
        sections = self.extract_key_sections(man_page)

        # Analyze with Ollama using man page
        refined_analysis = self.analyze_with_ollama(command, sections)

        if refined_analysis:
            # Create binary descriptor
            descriptor = self.create_refined_descriptor(command, refined_analysis)

            # Store refined result
            self.refined_descriptors[command] = {
                "original": existing_analysis,
                "refined": refined_analysis,
                "descriptor": descriptor.hex(),
                "man_sections": sections,
            }

            self.refinement_stats["successfully_refined"] += 1

            print(
                f"   ✅ Refined: [{refined_analysis['risk']}] {', '.join(refined_analysis['capabilities'])}"
            )

            return refined_analysis
        else:
            self.refinement_stats["failed"] += 1
            return None

    def batch_refine(self, commands: List[str], limit: Optional[int] = None):
        """Refine multiple commands in batch"""
        print("🏭 TCP Man Page Refinery - Batch Processing")
        print("=" * 60)

        # Load existing analyses if available
        existing_analyses = {}
        if os.path.exists("data/discovered_commands.json"):
            with open("data/discovered_commands.json", "r") as f:
                data = json.load(f)
                # Map commands to existing analyses
                for cmd in data.get("commands", []):
                    analysis_file = f"data/{cmd}_analysis.json"
                    if os.path.exists(analysis_file):
                        with open(analysis_file, "r") as af:
                            existing_analyses[cmd] = json.load(af)

        # Process commands
        commands_to_process = commands[:limit] if limit else commands
        start_time = time.time()

        for i, command in enumerate(commands_to_process, 1):
            existing = existing_analyses.get(command)
            self.refine_command(command, existing)

            # Progress update
            if i % 10 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                print(
                    f"\n📊 Progress: {i}/{len(commands_to_process)} "
                    f"({rate:.1f} cmd/min)"
                )

        # Final report
        self.generate_refinement_report()

    def generate_refinement_report(self):
        """Generate refinement statistics and comparison report"""
        print("\n" + "=" * 60)
        print("📊 Refinement Report")
        print("=" * 60)

        print(f"Total processed: {self.refinement_stats['total_processed']}")
        print(f"Man pages found: {self.refinement_stats['man_pages_found']}")
        print(f"Successfully refined: {self.refinement_stats['successfully_refined']}")
        print(f"Failed: {self.refinement_stats['failed']}")

        # Risk distribution
        risk_dist = {}
        for cmd, data in self.refined_descriptors.items():
            risk = data["refined"]["risk"]
            risk_dist[risk] = risk_dist.get(risk, 0) + 1

        print("\n🎯 Risk Distribution (Refined):")
        for risk, count in sorted(risk_dist.items()):
            print(f"  {risk:<15} {count:>3}")

        # Save results
        output_file = "refined_tcp_descriptors.json"
        with open(output_file, "w") as f:
            json.dump(
                {
                    "metadata": {
                        "total_refined": len(self.refined_descriptors),
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "method": "man_page_ground_truth",
                        "stats": self.refinement_stats,
                    },
                    "descriptors": self.refined_descriptors,
                },
                f,
                indent=2,
            )

        print(f"\n💾 Saved refined descriptors to: {output_file}")

    def demo(self):
        """Run demo with sample commands"""
        print("🔬 TCP Man Page Refinery Demo")
        print("Using man pages as ground truth with local Ollama")
        print("=" * 60)

        # Sample commands to refine
        sample_commands = [
            # Safe commands
            "ls",
            "cat",
            "echo",
            "pwd",
            "date",
            # File operations
            "cp",
            "mv",
            "rm",
            "mkdir",
            "touch",
            # System tools
            "ps",
            "top",
            "kill",
            "chmod",
            "chown",
            # Network tools
            "ping",
            "curl",
            "ssh",
            "nc",
            "wget",
            # Dangerous commands
            "dd",
            "mkfs",
            "fdisk",
            "shred",
            "sudo",
        ]

        print(f"\n📋 Refining {len(sample_commands)} commands using man pages...")

        self.batch_refine(sample_commands)

        # Show comparison example
        if "rm" in self.refined_descriptors:
            print("\n🔍 Example Refinement: 'rm' command")
            rm_data = self.refined_descriptors["rm"]
            print(f"   Risk: {rm_data['refined']['risk']}")
            print(f"   Capabilities: {', '.join(rm_data['refined']['capabilities'])}")
            print(f"   Binary descriptor: {rm_data['descriptor'][:32]}...")
            print(f"   Analysis snippet: {rm_data['refined']['analysis'][:100]}...")


if __name__ == "__main__":
    refinery = TCPManPageRefinery()
    refinery.demo()
