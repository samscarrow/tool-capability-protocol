#!/usr/bin/env python3
"""
DigitalOcean TCP Knowledge Growth System
Continuous enhancement of TCP ground truth via scheduled LLM analysis
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import schedule
import time
import logging
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/tcp-knowledge-growth.log'),
        logging.StreamHandler()
    ]
)

class TCPKnowledgeGrowthSystem:
    """Continuous TCP knowledge enhancement system for DigitalOcean"""
    
    def __init__(self):
        self.base_dir = Path("/opt/tcp-knowledge-system")
        self.data_dir = self.base_dir / "data"
        self.patterns_dir = self.base_dir / "patterns"
        self.logs_dir = self.base_dir / "logs"
        
        # Create directories
        for dir_path in [self.data_dir, self.patterns_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.enhancement_history = self.data_dir / "enhancement_history.json"
        self.current_patterns = self.patterns_dir / "current_tcp_patterns.json"
        self.command_queue = self.data_dir / "command_discovery_queue.json"
        
        # Performance tracking
        self.metrics = {
            'commands_analyzed': 0,
            'patterns_enhanced': 0,
            'accuracy_improvements': 0,
            'last_enhancement': None,
            'system_uptime': datetime.now(),
            'api_costs': 0.0
        }
        
        logging.info("🚀 TCP Knowledge Growth System initialized")
    
    def discover_new_commands(self) -> List[str]:
        """Discover new commands available on the system"""
        import subprocess
        
        try:
            # Get available man pages
            result = subprocess.run(
                ['apropos', '.'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                commands = []
                for line in result.stdout.split('\n')[:1000]:  # Limit to 1000
                    if line.strip():
                        cmd = line.split('(')[0].strip()
                        if len(cmd) > 1 and cmd.isalnum():
                            commands.append(cmd)
                
                # Filter out already analyzed commands
                existing_commands = self.load_analyzed_commands()
                new_commands = [cmd for cmd in commands if cmd not in existing_commands]
                
                logging.info(f"📊 Discovered {len(new_commands)} new commands")
                return new_commands[:50]  # Process 50 at a time
                
        except Exception as e:
            logging.error(f"❌ Command discovery failed: {e}")
        
        return []
    
    def load_analyzed_commands(self) -> set:
        """Load list of previously analyzed commands"""
        try:
            if self.enhancement_history.exists():
                with open(self.enhancement_history, 'r') as f:
                    history = json.load(f)
                return set(history.get('analyzed_commands', []))
        except Exception as e:
            logging.error(f"❌ Failed to load command history: {e}")
        
        return set()
    
    def analyze_command_batch(self, commands: List[str]) -> Dict:
        """Analyze a batch of commands with LLM"""
        from enhanced_tcp_analyzer import enhanced_analyzer
        import anthropic
        
        if not os.getenv('ANTHROPIC_API_KEY'):
            logging.error("❌ No Anthropic API key found")
            return {}
        
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        batch_results = {}
        api_cost = 0.0
        
        for i, command in enumerate(commands, 1):
            logging.info(f"[{i}/{len(commands)}] Analyzing {command}...")
            
            try:
                # Get man page
                man_content = self.get_man_page(command)
                if not man_content:
                    continue
                
                # Current TCP analysis
                current_analysis = enhanced_analyzer.analyze_man_page(command, man_content)
                
                # LLM analysis
                llm_analysis = self.get_llm_analysis(client, command, man_content)
                
                if llm_analysis:
                    batch_results[command] = {
                        'current': current_analysis,
                        'llm': llm_analysis,
                        'timestamp': datetime.now().isoformat(),
                        'man_page_size': len(man_content)
                    }
                    
                    # Estimate API cost (rough: $0.01 per analysis)
                    api_cost += 0.01
                    
                    logging.info(f"✅ {command}: {current_analysis['risk_level']} → {llm_analysis.get('risk_level', 'UNKNOWN')}")
                
            except Exception as e:
                logging.error(f"❌ Failed to analyze {command}: {e}")
        
        self.metrics['api_costs'] += api_cost
        return batch_results
    
    def get_man_page(self, command: str) -> str:
        """Get man page content for command"""
        import subprocess
        
        try:
            result = subprocess.run(
                ['man', command],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, 'MANPAGER': 'cat', 'PAGER': 'cat'}
            )
            
            if result.returncode == 0:
                return result.stdout
                
        except Exception as e:
            logging.error(f"❌ Failed to get man page for {command}: {e}")
        
        return ""
    
    def get_llm_analysis(self, client, command: str, man_content: str) -> Dict:
        """Get LLM analysis for command"""
        
        # Truncate for context limits
        if len(man_content) > 20000:
            man_content = man_content[:20000] + "... [TRUNCATED]"
        
        system_prompt = """You are a cybersecurity expert analyzing Unix commands for AI agent safety.
        
Provide concise security analysis in JSON format only. Focus on:
1. Risk level assessment
2. Key security capabilities
3. Dangerous patterns or options

Be precise and security-focused."""

        user_prompt = f"""Command: {command}

Man Page: {man_content[:5000]}...

Respond with JSON only:
{{
  "risk_level": "SAFE|LOW_RISK|MEDIUM_RISK|HIGH_RISK|CRITICAL",
  "capabilities": ["CAPABILITY1", "CAPABILITY2"],
  "dangerous_keywords": ["keyword1", "keyword2"],
  "security_notes": "Brief security assessment"
}}"""

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Use latest model
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            response_text = response.content[0].text
            
            # Extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            return json.loads(response_text.strip())
            
        except Exception as e:
            logging.error(f"❌ LLM analysis failed for {command}: {e}")
            return {}
    
    def integrate_batch_enhancements(self, batch_results: Dict):
        """Integrate batch analysis results into patterns"""
        
        if not batch_results:
            return
        
        # Load current patterns
        current_patterns = self.load_current_patterns()
        
        # Extract improvements
        new_keywords = set()
        new_capabilities = set()
        risk_corrections = {}
        
        for command, data in batch_results.items():
            current = data['current']
            llm = data['llm']
            
            # Risk corrections
            if current['risk_level'] != llm.get('risk_level'):
                risk_corrections[command] = {
                    'from': current['risk_level'],
                    'to': llm.get('risk_level'),
                    'confidence': 'llm_suggested'
                }
            
            # New keywords
            for keyword in llm.get('dangerous_keywords', []):
                if keyword.lower() not in str(current_patterns.get('safety_keywords', {})).lower():
                    new_keywords.add(keyword.lower())
            
            # New capabilities
            for cap in llm.get('capabilities', []):
                if cap not in current_patterns.get('capability_patterns', {}):
                    new_capabilities.add(cap)
        
        # Update patterns
        if new_keywords or new_capabilities or risk_corrections:
            enhanced_patterns = dict(current_patterns)
            
            # Add new keywords to appropriate risk levels
            for keyword in new_keywords:
                enhanced_patterns.setdefault('new_keywords', []).append(keyword)
            
            # Add new capabilities
            for cap in new_capabilities:
                pattern = f"({cap.lower().replace('_', '|')})"
                enhanced_patterns.setdefault('new_capability_patterns', {})[cap] = pattern
            
            # Save enhanced patterns
            enhanced_patterns['last_updated'] = datetime.now().isoformat()
            enhanced_patterns['batch_enhancements'] = len(batch_results)
            
            self.save_current_patterns(enhanced_patterns)
            
            self.metrics['patterns_enhanced'] += len(new_keywords) + len(new_capabilities)
            self.metrics['accuracy_improvements'] += len(risk_corrections)
            
            logging.info(f"✅ Integrated enhancements: {len(new_keywords)} keywords, {len(new_capabilities)} capabilities")
    
    def load_current_patterns(self) -> Dict:
        """Load current TCP patterns"""
        try:
            if self.current_patterns.exists():
                with open(self.current_patterns, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"❌ Failed to load patterns: {e}")
        
        return {'safety_keywords': {}, 'capability_patterns': {}}
    
    def save_current_patterns(self, patterns: Dict):
        """Save enhanced patterns"""
        try:
            with open(self.current_patterns, 'w') as f:
                json.dump(patterns, f, indent=2)
            logging.info(f"💾 Patterns saved to {self.current_patterns}")
        except Exception as e:
            logging.error(f"❌ Failed to save patterns: {e}")
    
    def save_enhancement_history(self, batch_results: Dict):
        """Save enhancement history for tracking"""
        try:
            history = {'analyzed_commands': [], 'enhancements': []}
            
            if self.enhancement_history.exists():
                with open(self.enhancement_history, 'r') as f:
                    history = json.load(f)
            
            # Add new commands
            history['analyzed_commands'].extend(batch_results.keys())
            
            # Add enhancement record
            history['enhancements'].append({
                'timestamp': datetime.now().isoformat(),
                'commands_count': len(batch_results),
                'api_cost': self.metrics['api_costs'],
                'improvements': self.metrics['accuracy_improvements']
            })
            
            with open(self.enhancement_history, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logging.error(f"❌ Failed to save history: {e}")
    
    def run_enhancement_cycle(self):
        """Run a single enhancement cycle"""
        logging.info("🔄 Starting enhancement cycle...")
        
        try:
            # Discover new commands
            new_commands = self.discover_new_commands()
            
            if not new_commands:
                logging.info("ℹ️  No new commands to analyze")
                return
            
            # Analyze batch
            batch_results = self.analyze_command_batch(new_commands)
            
            if batch_results:
                # Integrate enhancements
                self.integrate_batch_enhancements(batch_results)
                
                # Save history
                self.save_enhancement_history(batch_results)
                
                # Update metrics
                self.metrics['commands_analyzed'] += len(batch_results)
                self.metrics['last_enhancement'] = datetime.now().isoformat()
                
                logging.info(f"✅ Enhancement cycle complete: {len(batch_results)} commands processed")
            else:
                logging.warning("⚠️  No successful analyses in this cycle")
                
        except Exception as e:
            logging.error(f"❌ Enhancement cycle failed: {e}")
    
    def generate_status_report(self) -> Dict:
        """Generate system status report"""
        uptime = datetime.now() - self.metrics['system_uptime']
        
        return {
            'system_status': 'running',
            'uptime_hours': uptime.total_seconds() / 3600,
            'metrics': self.metrics,
            'last_enhancement': self.metrics.get('last_enhancement'),
            'storage_usage': {
                'patterns_file_size': self.current_patterns.stat().st_size if self.current_patterns.exists() else 0,
                'history_file_size': self.enhancement_history.stat().st_size if self.enhancement_history.exists() else 0
            }
        }
    
    def start_continuous_growth(self):
        """Start continuous knowledge growth system"""
        logging.info("🚀 Starting TCP continuous knowledge growth...")
        
        # Schedule enhancement cycles
        schedule.every(6).hours.do(self.run_enhancement_cycle)  # Every 6 hours
        schedule.every().day.at("02:00").do(self.run_enhancement_cycle)  # Daily at 2 AM
        
        # Status reports
        schedule.every().hour.do(lambda: logging.info(f"📊 Status: {self.generate_status_report()}"))
        
        # Initial cycle
        self.run_enhancement_cycle()
        
        # Main loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main entry point for DigitalOcean deployment"""
    system = TCPKnowledgeGrowthSystem()
    
    try:
        system.start_continuous_growth()
    except KeyboardInterrupt:
        logging.info("🛑 System shutdown requested")
    except Exception as e:
        logging.error(f"❌ System error: {e}")

if __name__ == "__main__":
    main()