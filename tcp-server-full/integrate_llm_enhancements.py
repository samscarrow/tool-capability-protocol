#!/usr/bin/env python3
"""
Integrate LLM enhancements into TCP ground truth patterns
"""

import json
from pathlib import Path
from tcp_man_ingestion import ManPageAnalyzer

def integrate_llm_findings():
    """Integrate LLM analysis findings into TCP patterns"""
    
    # Load LLM analysis results
    results_file = "tcp_llm_enhancement_demo_20250709_201633.json"
    
    try:
        with open(results_file, 'r') as f:
            llm_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Results file {results_file} not found")
        return
    
    print("🔗 Integrating LLM Enhancements into TCP Ground Truth")
    print("=" * 55)
    
    analyzer = ManPageAnalyzer()
    
    # Current patterns
    original_keywords = dict(analyzer.safety_keywords)
    original_patterns = dict(analyzer.capability_patterns)
    
    # Extract new patterns from LLM analysis
    new_keywords = {
        'CRITICAL': set(),
        'HIGH_RISK': set(), 
        'MEDIUM_RISK': set(),
        'LOW_RISK': set()
    }
    
    new_capability_patterns = {}
    risk_adjustments = {}
    
    print("📊 Analyzing LLM findings:")
    
    for command, data in llm_data['results'].items():
        current_risk = data['current_tcp']['risk_level']
        llm_risk = data['llm_analysis'].get('risk_level', current_risk)
        
        print(f"\n🔍 {command}:")
        print(f"   Current: {current_risk} → LLM: {llm_risk}")
        
        # Risk level adjustments
        if current_risk != llm_risk:
            risk_adjustments[command] = {
                'from': current_risk,
                'to': llm_risk,
                'reasoning': data['llm_analysis'].get('risk_reasoning', '')
            }
            print(f"   📈 Risk adjustment recommended: {current_risk} → {llm_risk}")
        
        # New dangerous keywords
        llm_keywords = data['llm_analysis'].get('dangerous_keywords', [])
        for keyword in llm_keywords:
            # Add to appropriate risk level based on LLM assessment
            if keyword not in str(original_keywords):
                new_keywords[llm_risk].add(keyword.lower())
                print(f"   ➕ New keyword: '{keyword}' ({llm_risk})")
        
        # New capabilities
        llm_capabilities = data['llm_analysis'].get('capabilities', [])
        for cap in llm_capabilities:
            if cap not in original_patterns:
                # Create pattern based on capability name
                pattern_name = cap
                pattern_regex = f"({cap.lower().replace('_', '|')})"
                new_capability_patterns[pattern_name] = pattern_regex
                print(f"   ➕ New capability: {cap}")
    
    # Generate enhanced patterns
    enhanced_keywords = dict(original_keywords)
    for risk_level, keywords in new_keywords.items():
        if keywords:
            enhanced_keywords[risk_level].extend(list(keywords))
    
    enhanced_patterns = dict(original_patterns)
    enhanced_patterns.update(new_capability_patterns)
    
    # Create enhanced analyzer class
    enhanced_code = f'''#!/usr/bin/env python3
"""
Enhanced TCP Man Page Analyzer with LLM-refined patterns
Generated on: {json.dumps(llm_data["timestamp"])}
Enhancement source: LLM analysis of {len(llm_data["results"])} commands
"""

from tcp_man_ingestion import ManPageAnalyzer as BaseAnalyzer

class EnhancedManPageAnalyzer(BaseAnalyzer):
    """Enhanced analyzer with LLM-refined ground truth patterns"""
    
    def __init__(self):
        super().__init__()
        
        # Enhanced safety keywords (original + LLM findings)
        self.safety_keywords = {json.dumps(enhanced_keywords, indent=12)[:-1]}        }}
        
        # Enhanced capability patterns (original + LLM findings)  
        self.capability_patterns = {json.dumps(enhanced_patterns, indent=12)[:-1]}        }}
        
        # Risk level adjustments based on LLM analysis
        self.risk_adjustments = {json.dumps(risk_adjustments, indent=12)[:-1]}        }}
    
    def analyze_man_page(self, command: str, content: str):
        """Enhanced analysis with LLM refinements"""
        # Run base analysis
        analysis = super().analyze_man_page(command, content)
        
        # Apply LLM-based risk adjustments
        if command in self.risk_adjustments:
            adjustment = self.risk_adjustments[command]
            print(f"🧠 LLM risk adjustment for {{command}}: {{adjustment['from']}} → {{adjustment['to']}}")
            analysis['risk_level'] = adjustment['to']
            analysis['risk_score'] = {{'SAFE': 0, 'LOW_RISK': 1, 'MEDIUM_RISK': 2, 'HIGH_RISK': 3, 'CRITICAL': 4}}.get(adjustment['to'], analysis['risk_score'])
            analysis['llm_reasoning'] = adjustment['reasoning']
        
        return analysis

# Create global instance for testing
enhanced_analyzer = EnhancedManPageAnalyzer()
'''
    
    # Save enhanced analyzer
    output_file = "enhanced_tcp_analyzer.py"
    with open(output_file, 'w') as f:
        f.write(enhanced_code)
    
    print(f"\n✅ Enhanced analyzer saved to: {output_file}")
    
    # Summary
    total_new_keywords = sum(len(keywords) for keywords in new_keywords.values())
    print(f"\n📈 Enhancement Summary:")
    print(f"   New safety keywords: {total_new_keywords}")
    print(f"   New capability patterns: {len(new_capability_patterns)}")
    print(f"   Risk level adjustments: {len(risk_adjustments)}")
    
    if risk_adjustments:
        print(f"\n🎯 Key Risk Adjustments:")
        for cmd, adj in risk_adjustments.items():
            print(f"   {cmd}: {adj['from']} → {adj['to']}")
    
    # Test enhanced analyzer
    print(f"\n🧪 Testing Enhanced Analyzer:")
    from enhanced_tcp_analyzer import enhanced_analyzer
    
    test_result = enhanced_analyzer.analyze_man_page("rm", "test content with remove and delete keywords")
    print(f"   Test analysis: {test_result['risk_level']}")
    
    return enhanced_keywords, enhanced_patterns, risk_adjustments

if __name__ == "__main__":
    integrate_llm_findings()