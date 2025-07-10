#!/usr/bin/env python3
"""Quick LLM enhancement demo for TCP ground truth"""

import os
import json
from datetime import datetime
from tcp_man_ingestion import ManPageAnalyzer
import anthropic


def analyze_command_with_llm(command: str, man_content: str) -> dict:
    """Analyze a single command with LLM"""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Truncate for context limits
    if len(man_content) > 30000:
        man_content = man_content[:30000] + "... [TRUNCATED]"

    system_prompt = """You are a cybersecurity expert analyzing Unix commands for AI agent safety.

Analyze this command's man page and provide security intelligence in JSON format.

Focus on:
1. Risk Level: SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL  
2. Dangerous keywords that indicate security risk
3. Command capabilities that could be misused
4. Context-sensitive risks based on options/arguments

Respond with valid JSON only."""

    user_prompt = f"""Command: {command}

Man Page Content:
{man_content[:10000]}...

Provide analysis in this exact JSON format:
{{
  "risk_level": "CRITICAL",
  "risk_reasoning": "Brief explanation why",
  "dangerous_keywords": ["keyword1", "keyword2"],
  "capabilities": ["DESTRUCTIVE", "NETWORK_ACCESS"],
  "dangerous_options": ["-rf", "--force"],
  "ai_agent_concerns": ["concern1", "concern2"]
}}"""

    try:
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=1000,
            temperature=0.1,
        )

        response_text = response.content[0].text
        # Clean up JSON if wrapped in markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        return json.loads(response_text.strip())

    except Exception as e:
        print(f"    ❌ LLM analysis failed: {e}")
        return {}


def main():
    """Quick LLM enhancement demo"""

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ No Anthropic API key found")
        return

    analyzer = ManPageAnalyzer()

    # High-priority dangerous commands
    test_commands = ["rm", "dd", "sudo", "chmod"]

    print("🧠 TCP LLM Ground Truth Enhancement Demo")
    print("=" * 50)

    results = {}

    for i, command in enumerate(test_commands, 1):
        print(f"\n[{i}/{len(test_commands)}] Analyzing {command} with LLM...")

        # Get man page
        man_content = analyzer.get_man_page(command)
        if not man_content:
            print(f"  ❌ No man page for {command}")
            continue

        # Get current TCP analysis
        current = analyzer.analyze_man_page(command, man_content)
        print(f"  📊 Current TCP: {current['risk_level']}")

        # Get LLM analysis
        print(f"  🧠 Analyzing with Claude...", end=" ")
        llm_analysis = analyze_command_with_llm(command, man_content)

        if llm_analysis:
            print(f"✅ {llm_analysis.get('risk_level', 'UNKNOWN')}")
            print(
                f"     LLM reasoning: {llm_analysis.get('risk_reasoning', 'N/A')[:60]}..."
            )
            print(
                f"     New keywords: {llm_analysis.get('dangerous_keywords', [])[:3]}"
            )
            print(f"     Capabilities: {llm_analysis.get('capabilities', [])[:3]}")

            results[command] = {
                "current_tcp": current,
                "llm_analysis": llm_analysis,
                "agreement": current["risk_level"] == llm_analysis.get("risk_level"),
                "man_page_size": len(man_content),
            }
        else:
            print("❌ Failed")

    # Summary
    print(f"\n📊 Enhancement Summary:")
    print(f"   Commands analyzed: {len(results)}")

    agreements = sum(1 for r in results.values() if r["agreement"])
    print(
        f"   Risk level agreement: {agreements}/{len(results)} ({100*agreements/len(results):.0f}%)"
    )

    # Save results
    output_file = (
        f"tcp_llm_enhancement_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(output_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "commands_analyzed": len(results),
                    "agreement_rate": agreements / len(results) if results else 0,
                },
                "results": results,
            },
            f,
            indent=2,
            default=str,
        )

    print(f"   Results saved: {output_file}")

    # Show key insights
    for cmd, data in results.items():
        if not data["agreement"]:
            print(f"\n🔍 Disagreement on {cmd}:")
            print(f"   TCP: {data['current_tcp']['risk_level']}")
            print(f"   LLM: {data['llm_analysis'].get('risk_level', 'UNKNOWN')}")
            print(
                f"   LLM reasoning: {data['llm_analysis'].get('risk_reasoning', 'N/A')}"
            )


if __name__ == "__main__":
    main()
