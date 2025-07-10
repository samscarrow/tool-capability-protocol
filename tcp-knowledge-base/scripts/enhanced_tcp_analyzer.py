#!/usr/bin/env python3
"""
Enhanced TCP Man Page Analyzer with LLM-refined patterns
Generated on: "2025-07-09T20:16:33.965910"
Enhancement source: LLM analysis of 4 commands
"""

from tcp_man_ingestion import ManPageAnalyzer as BaseAnalyzer

class EnhancedManPageAnalyzer(BaseAnalyzer):
    """Enhanced analyzer with LLM-refined ground truth patterns"""
    
    def __init__(self):
        super().__init__()
        
        # Enhanced safety keywords (original + LLM findings)
        self.safety_keywords = {
            "CRITICAL": [
                        "destroy",
                        "erase",
                        "wipe",
                        "format",
                        "delete permanently",
                        "irreversible",
                        "data loss",
                        "cannot be undone",
                        "destructive",
                        "overwrite",
                        "unrecoverable",
                        "obliterate",
                        "execute",
                        "security policy",
                        "authentication",
                        "superuser",
                        "password"
            ],
            "HIGH_RISK": [
                        "delete",
                        "remove",
                        "modify",
                        "change",
                        "alter",
                        "permission",
                        "root",
                        "sudo",
                        "privilege",
                        "system",
                        "configuration",
                        "conv",
                        "noerror",
                        "setgid",
                        "recursive",
                        "unlink",
                        "notrunc",
                        "fsync",
                        "force",
                        "sync",
                        "setuid",
                        "sticky bit"
            ],
            "MEDIUM_RISK": [
                        "write",
                        "create",
                        "update",
                        "edit",
                        "move",
                        "rename",
                        "network",
                        "connect",
                        "download",
                        "upload"
            ],
            "LOW_RISK": [
                        "read",
                        "list",
                        "display",
                        "show",
                        "view",
                        "check",
                        "status",
                        "info",
                        "query"
            ]
        }
        
        # Enhanced capability patterns (original + LLM findings)  
        self.capability_patterns = {
            "REQUIRES_ROOT": "(requires?\\s+root|must\\s+be\\s+root|superuser|sudo)",
            "DESTRUCTIVE": "(destroy|delete|remove|erase|wipe|format)",
            "NETWORK_ACCESS": "(network|internet|download|upload|remote|ssh|http)",
            "FILE_MODIFICATION": "(write|modify|create|delete|change.*file)",
            "SYSTEM_MODIFICATION": "(system|kernel|boot|service|daemon)",
            "PRIVILEGE_ESCALATION": "(setuid|privilege|escalat|sudo|root)",
            "FILE_SYSTEM_ACCESS": "(file|system|access)",
            "EXECUTE_COMMANDS": "(execute|commands)",
            "ACCESS_CONTROL": "(access|control)",
            "FILE_SYSTEM_CHANGES": "(file|system|changes)"
        }
        
        # Risk level adjustments based on LLM analysis
        self.risk_adjustments = {
            "rm": {
                        "from": "CRITICAL",
                        "to": "HIGH_RISK",
                        "reasoning": "The rm command can permanently delete files and directories, which could lead to data loss if used improperly."
            },
            "dd": {
                        "from": "CRITICAL",
                        "to": "HIGH_RISK",
                        "reasoning": "The dd command can be used to overwrite and corrupt data on disks and files, potentially causing data loss or system instability if misused."
            },
            "chmod": {
                        "from": "CRITICAL",
                        "to": "HIGH_RISK",
                        "reasoning": "The chmod command can grant or revoke permissions on files and directories, potentially allowing unauthorized access or unintended changes."
            }
        }
    
    def analyze_man_page(self, command: str, content: str):
        """Enhanced analysis with LLM refinements"""
        # Run base analysis
        analysis = super().analyze_man_page(command, content)
        
        # Apply LLM-based risk adjustments
        if command in self.risk_adjustments:
            adjustment = self.risk_adjustments[command]
            print(f"🧠 LLM risk adjustment for {command}: {adjustment['from']} → {adjustment['to']}")
            analysis['risk_level'] = adjustment['to']
            analysis['risk_score'] = {'SAFE': 0, 'LOW_RISK': 1, 'MEDIUM_RISK': 2, 'HIGH_RISK': 3, 'CRITICAL': 4}.get(adjustment['to'], analysis['risk_score'])
            analysis['llm_reasoning'] = adjustment['reasoning']
        
        return analysis

# Create global instance for testing
enhanced_analyzer = EnhancedManPageAnalyzer()
