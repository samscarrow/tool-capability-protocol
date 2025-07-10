#!/usr/bin/env python3
"""
LLM Ground Truth Enhancement for TCP Protocol
One-time refinement of rule-based patterns using expert LLM analysis
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from tcp_man_ingestion import ManPageAnalyzer, TCPManIngestionServer
import anthropic

class TCPGroundTruthEnhancer:
    """
    Enhance TCP's rule-based ground truth using one-time LLM analysis
    """
    
    def __init__(self, use_anthropic=True):
        self.analyzer = ManPageAnalyzer()
        self.use_anthropic = use_anthropic
        
        # Initialize Anthropic client
        if use_anthropic:
            self.anthropic_client = anthropic.Anthropic(
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
            
        self.enhancement_results = {
            'enhanced_commands': {},
            'new_safety_keywords': set(),
            'new_capability_patterns': {},
            'risk_level_corrections': {},
            'semantic_patterns': []
        }
    
    async def enhance_ground_truth(self, commands_to_analyze: List[str] = None):
        """
        Main enhancement pipeline: analyze commands with LLM for ground truth refinement
        """
        
        if not commands_to_analyze:
            # Use existing TCP database commands
            server = TCPManIngestionServer()
            await server.ingest_system_commands()
            commands_to_analyze = list(server.ingested_commands.keys())[:20]  # Sample
        
        print(f"🧠 LLM Ground Truth Enhancement")
        print(f"Analyzing {len(commands_to_analyze)} commands for pattern refinement")
        print("=" * 60)
        
        for i, command in enumerate(commands_to_analyze, 1):
            print(f"[{i}/{len(commands_to_analyze)}] Enhancing {command}...")
            
            # Get man page
            man_content = self.analyzer.get_man_page(command)
            if not man_content:
                continue
                
            # Get current TCP analysis
            current_analysis = self.analyzer.analyze_man_page(command, man_content)
            
            # Get LLM expert analysis
            llm_analysis = await self.get_llm_analysis(command, man_content)
            
            # Compare and extract improvements
            improvements = self.compare_analyses(command, current_analysis, llm_analysis)
            
            if improvements:
                self.enhancement_results['enhanced_commands'][command] = improvements
                print(f"  ✅ Found {len(improvements)} improvements")
            else:
                print(f"  ➡️  No improvements needed")
    
    async def get_llm_analysis(self, command: str, man_content: str) -> Dict:
        """
        Get expert LLM analysis of command safety and capabilities
        """
        
        # Truncate very long man pages for LLM context limits
        if len(man_content) > 50000:
            man_content = man_content[:50000] + "... [TRUNCATED]"
        
        system_prompt = """You are a cybersecurity expert analyzing Unix/Linux commands for AI agent safety.
        
Your task: Analyze this command's man page and provide detailed security intelligence.

Focus on:
1. Risk Level: SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL
2. Security Capabilities: What can this command do that's security-relevant?
3. Dangerous Patterns: Keywords/phrases that indicate risk
4. Context Sensitivity: How arguments/options change risk
5. Subtle Risks: Non-obvious security implications

Be precise and security-focused. Consider AI agent safety scenarios."""

        user_prompt = f"""Command: {command}

Man Page Content:
{man_content}

Provide analysis in this JSON format:
{{
  "risk_level": "CRITICAL|HIGH_RISK|MEDIUM_RISK|LOW_RISK|SAFE",
  "risk_reasoning": "Why this risk level?",
  "capabilities": ["DESTRUCTIVE", "NETWORK_ACCESS", etc.],
  "dangerous_keywords": ["keyword1", "keyword2"],
  "dangerous_options": ["-rf", "--force"],
  "context_risks": {{"option": "risk description"}},
  "ai_agent_concerns": ["concern1", "concern2"],
  "suggested_patterns": {{"pattern_name": "regex_pattern"}}
}}"""

        try:
            if self.use_anthropic:
                response = await self._call_anthropic(system_prompt, user_prompt)
            else:
                return {}
                
            # Parse JSON response
            return json.loads(response)
            
        except Exception as e:
            print(f"    ❌ LLM analysis failed: {e}")
            return {}
    
    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        """Call Anthropic API"""
        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=2000,
            temperature=0.1
        )
        return response.content[0].text
    
    def compare_analyses(self, command: str, current: Dict, llm: Dict) -> List[Dict]:
        """
        Compare current TCP analysis with LLM analysis to find improvements
        """
        improvements = []
        
        if not llm:
            return improvements
        
        # Risk level comparison
        if current['risk_level'] != llm.get('risk_level'):
            improvements.append({
                'type': 'risk_level_correction',
                'current': current['risk_level'],
                'suggested': llm.get('risk_level'),
                'reasoning': llm.get('risk_reasoning', '')
            })
        
        # New dangerous keywords
        current_keywords = set()
        for keywords in self.analyzer.safety_keywords.values():
            current_keywords.update(keywords)
            
        llm_keywords = set(llm.get('dangerous_keywords', []))
        new_keywords = llm_keywords - current_keywords
        
        if new_keywords:
            improvements.append({
                'type': 'new_safety_keywords',
                'keywords': list(new_keywords),
                'command_context': command
            })
        
        # New capability patterns
        llm_patterns = llm.get('suggested_patterns', {})
        for pattern_name, pattern_regex in llm_patterns.items():
            if pattern_name not in self.analyzer.capability_patterns:
                improvements.append({
                    'type': 'new_capability_pattern',
                    'name': pattern_name,
                    'pattern': pattern_regex,
                    'source_command': command
                })
        
        # Context-sensitive risks
        context_risks = llm.get('context_risks', {})
        if context_risks:
            improvements.append({
                'type': 'context_sensitivity',
                'risks': context_risks,
                'command': command
            })
        
        return improvements
    
    def generate_enhanced_patterns(self) -> Dict:
        """
        Generate enhanced pattern dictionaries from LLM analysis
        """
        enhanced_safety_keywords = dict(self.analyzer.safety_keywords)
        enhanced_capability_patterns = dict(self.analyzer.capability_patterns)
        
        # Aggregate new keywords by risk level
        for command_data in self.enhancement_results['enhanced_commands'].values():
            for improvement in command_data:
                if improvement['type'] == 'new_safety_keywords':
                    # Need to categorize these keywords by risk level
                    # This would require additional LLM analysis or heuristics
                    pass
                elif improvement['type'] == 'new_capability_pattern':
                    enhanced_capability_patterns[improvement['name']] = improvement['pattern']
        
        return {
            'enhanced_safety_keywords': enhanced_safety_keywords,
            'enhanced_capability_patterns': enhanced_capability_patterns,
            'risk_corrections': self.enhancement_results['risk_level_corrections']
        }
    
    def save_enhancement_results(self, output_file: str = "tcp_llm_enhancements.json"):
        """Save enhancement results for manual review and integration"""
        
        with open(output_file, 'w') as f:
            json.dump({
                'enhancement_metadata': {
                    'timestamp': str(datetime.now()),
                    'commands_analyzed': len(self.enhancement_results['enhanced_commands']),
                    'total_improvements': sum(len(improvements) for improvements in 
                                            self.enhancement_results['enhanced_commands'].values())
                },
                'results': self.enhancement_results,
                'proposed_patterns': self.generate_enhanced_patterns()
            }, f, indent=2, default=str)
        
        print(f"🎯 Enhancement results saved to {output_file}")
        print(f"📊 Analysis complete:")
        print(f"   Commands analyzed: {len(self.enhancement_results['enhanced_commands'])}")
        print(f"   Improvements found: {sum(len(improvements) for improvements in self.enhancement_results['enhanced_commands'].values())}")

async def main():
    """Run TCP ground truth enhancement"""
    
    # Check for API keys
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ No Anthropic API key found. Set ANTHROPIC_API_KEY")
        return
    
    enhancer = TCPGroundTruthEnhancer(use_anthropic=True)
    
    # High-value commands for enhancement
    priority_commands = [
        'rm', 'dd', 'sudo', 'chmod', 'chown',  # Dangerous basics
        'git', 'docker', 'kubectl', 'ssh',     # Complex tools
        'curl', 'wget', 'nc', 'nmap',          # Network tools
        'find', 'grep', 'awk', 'sed'           # Text processing
    ]
    
    await enhancer.enhance_ground_truth(priority_commands)
    enhancer.save_enhancement_results()

if __name__ == "__main__":
    asyncio.run(main())