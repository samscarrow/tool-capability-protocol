#!/usr/bin/env python3
"""
Simple TCP Knowledge Growth Deployment
Creates a local continuous learning system that can be deployed to any server
"""

import os
import json
import schedule
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from tcp_man_ingestion import ManPageAnalyzer
import anthropic

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("tcp_knowledge_growth.log"), logging.StreamHandler()],
)


class SimpleTCPKnowledgeGrowth:
    """Simple TCP knowledge growth system"""

    def __init__(self):
        self.data_dir = Path("tcp_data")
        self.data_dir.mkdir(exist_ok=True)

        # Get API key from 1Password
        try:
            result = subprocess.run(
                [
                    "op",
                    "item",
                    "get",
                    "neposatk4gkawjw52mlhm6jvcu",
                    "--fields",
                    "credential",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self.anthropic_key = result.stdout.strip()
                logging.info("✅ Anthropic API key loaded from 1Password")
            else:
                logging.error("❌ Failed to get Anthropic API key from 1Password")
                self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        except:
            self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.anthropic_key:
            raise ValueError("❌ No Anthropic API key available")

        self.client = anthropic.Anthropic(api_key=self.anthropic_key)
        self.analyzer = ManPageAnalyzer()

        # Initialize tracking
        self.analyzed_commands = set()
        self.enhancement_history = []
        self.load_state()

        logging.info("🚀 TCP Knowledge Growth System initialized")

    def load_state(self):
        """Load previous state"""
        state_file = self.data_dir / "state.json"
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    state = json.load(f)
                self.analyzed_commands = set(state.get("analyzed_commands", []))
                self.enhancement_history = state.get("enhancement_history", [])
                logging.info(
                    f"📊 Loaded state: {len(self.analyzed_commands)} analyzed commands"
                )
            except Exception as e:
                logging.error(f"❌ Failed to load state: {e}")

    def save_state(self):
        """Save current state"""
        state_file = self.data_dir / "state.json"
        try:
            state = {
                "analyzed_commands": list(self.analyzed_commands),
                "enhancement_history": self.enhancement_history,
                "last_updated": datetime.now().isoformat(),
            }
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)
            logging.info("💾 State saved")
        except Exception as e:
            logging.error(f"❌ Failed to save state: {e}")

    def discover_new_commands(self, limit=10):
        """Discover new commands to analyze"""
        try:
            # Get available commands
            result = subprocess.run(
                ["apropos", "."], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                all_commands = []
                for line in result.stdout.split("\n")[:500]:  # Limit scope
                    if line.strip():
                        cmd = line.split("(")[0].strip()
                        if (
                            len(cmd) > 1
                            and cmd.isalnum()
                            and cmd not in self.analyzed_commands
                        ):
                            all_commands.append(cmd)

                # Return new commands up to limit
                new_commands = list(set(all_commands))[:limit]
                logging.info(
                    f"🔍 Discovered {len(new_commands)} new commands to analyze"
                )
                return new_commands

        except Exception as e:
            logging.error(f"❌ Command discovery failed: {e}")

        return []

    def analyze_command_with_llm(self, command):
        """Analyze a command with LLM"""
        try:
            # Get man page
            man_content = self.analyzer.get_man_page(command)
            if not man_content:
                return None

            # Truncate for API limits
            if len(man_content) > 15000:
                man_content = man_content[:15000] + "... [TRUNCATED]"

            # Get current analysis
            current = self.analyzer.analyze_man_page(command, man_content)

            # LLM analysis
            system_prompt = """You are a cybersecurity expert. Analyze this Unix command for AI agent safety.

Provide JSON with:
- risk_level: SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL
- capabilities: list of security-relevant capabilities
- dangerous_keywords: keywords indicating security risk"""

            user_prompt = f"""Command: {command}

Man page: {man_content[:8000]}...

Respond with JSON only."""

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                max_tokens=300,
                temperature=0.1,
            )

            response_text = response.content[0].text
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]

            llm_analysis = json.loads(response_text.strip())

            result = {
                "command": command,
                "current_tcp": current,
                "llm_analysis": llm_analysis,
                "man_page_size": len(man_content),
                "timestamp": datetime.now().isoformat(),
            }

            logging.info(
                f"✅ {command}: {current['risk_level']} → {llm_analysis.get('risk_level', 'UNKNOWN')}"
            )
            return result

        except Exception as e:
            logging.error(f"❌ Failed to analyze {command}: {e}")
            return None

    def run_enhancement_cycle(self):
        """Run a single enhancement cycle"""
        logging.info("🔄 Starting enhancement cycle...")

        # Discover new commands
        new_commands = self.discover_new_commands(limit=5)  # Small batches

        if not new_commands:
            logging.info("ℹ️  No new commands to analyze")
            return

        # Analyze commands
        results = []
        for command in new_commands:
            result = self.analyze_command_with_llm(command)
            if result:
                results.append(result)
                self.analyzed_commands.add(command)

        if results:
            # Save enhancement data
            enhancement = {
                "timestamp": datetime.now().isoformat(),
                "commands_analyzed": len(results),
                "results": results,
            }

            self.enhancement_history.append(enhancement)

            # Save results to file
            results_file = (
                self.data_dir
                / f"enhancement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(results_file, "w") as f:
                json.dump(enhancement, f, indent=2)

            self.save_state()

            logging.info(f"✅ Cycle complete: {len(results)} commands analyzed")

            # Log interesting findings
            for result in results:
                current_risk = result["current_tcp"]["risk_level"]
                llm_risk = result["llm_analysis"].get("risk_level", "UNKNOWN")
                if current_risk != llm_risk:
                    logging.info(
                        f"🔍 Risk disagreement on {result['command']}: {current_risk} vs {llm_risk}"
                    )

        else:
            logging.warning("⚠️  No successful analyses in this cycle")

    def get_stats(self):
        """Get system statistics"""
        return {
            "commands_analyzed": len(self.analyzed_commands),
            "enhancement_cycles": len(self.enhancement_history),
            "last_cycle": self.enhancement_history[-1]["timestamp"]
            if self.enhancement_history
            else None,
            "data_files": len(list(self.data_dir.glob("enhancement_*.json"))),
        }

    def start_continuous_growth(self):
        """Start continuous learning"""
        logging.info("🌱 Starting TCP continuous knowledge growth...")

        # Schedule cycles
        schedule.every(2).hours.do(self.run_enhancement_cycle)  # Every 2 hours

        # Initial cycle
        self.run_enhancement_cycle()

        # Main loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

                # Log stats every hour
                if datetime.now().minute == 0:
                    stats = self.get_stats()
                    logging.info(f"📊 Stats: {stats}")

        except KeyboardInterrupt:
            logging.info("🛑 Shutdown requested")
            self.save_state()


def main():
    """Main entry point"""
    try:
        system = SimpleTCPKnowledgeGrowth()

        # Show initial stats
        stats = system.get_stats()
        logging.info(f"📊 Initial stats: {stats}")

        # Option to run single cycle or continuous
        import sys

        if len(sys.argv) > 1 and sys.argv[1] == "once":
            logging.info("🔄 Running single enhancement cycle...")
            system.run_enhancement_cycle()
            final_stats = system.get_stats()
            logging.info(f"📊 Final stats: {final_stats}")
        else:
            system.start_continuous_growth()

    except Exception as e:
        logging.error(f"❌ System error: {e}")


if __name__ == "__main__":
    main()
