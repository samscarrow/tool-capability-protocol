#!/bin/bash

echo "🔐 TCP Security Interactive Shell"
echo "================================="
echo ""
echo "This is a secure TCP environment with:"
echo "  • Local Ollama LLM for security analysis"
echo "  • Enhanced TCP descriptors with embedded security"
echo "  • Human-controlled sandbox for tool execution"
echo "  • Complete privacy - all processing local"
echo ""
echo "Quick commands:"
echo "  tcp-demo     - Run demonstration menu"
echo "  tcp-health   - Check system health"
echo "  tcp-ollama   - Interact with Ollama directly"
echo "  tcp-analyze  - Analyze a command's security"
echo ""

# Add custom aliases
alias tcp-demo='/tcp-security/run-demo.sh'
alias tcp-health='/tcp-security/health-check.sh'
alias tcp-ollama='ollama'

# Function to analyze a command
tcp-analyze() {
    if [ -z "$1" ]; then
        echo "Usage: tcp-analyze <command>"
        echo "Example: tcp-analyze rm"
        return 1
    fi
    
    echo "🔍 Analyzing command: $1"
    python3 -c "
from tcp.enrichment.manpage_enricher import ManPageEnricher
from tcp.enrichment.tcp_encoder import EnrichedTCPEncoder
from tcp.enrichment.risk_assessment_auditor import TransparentRiskAssessor

enricher = ManPageEnricher()
encoder = EnrichedTCPEncoder(enricher)
assessor = TransparentRiskAssessor()

command = '$1'
print(f'📋 Processing: {command}')

# Get man page data
man_data = enricher.enrich_command(command)
if man_data:
    print(f'✅ Security Level: {man_data.security_level.value}')
    print(f'✅ Privileges: {man_data.privilege_requirements.value}')
    
    # Generate TCP descriptor
    descriptor = encoder.encode_enhanced_tcp(command)
    binary_data = encoder.to_binary(descriptor)
    
    print(f'✅ Binary Size: {len(binary_data)} bytes')
    print(f'✅ Security Flags: 0x{descriptor.security_flags:08x}')
    
    # Risk assessment
    audit = assessor.assess_command_risk(command, man_data)
    print(f'✅ Risk Score: {audit.security_score:.3f}')
    print(f'✅ Evidence Pieces: {len(audit.risk_evidence)}')
else:
    print('❌ Failed to analyze command')
"
}

export -f tcp-analyze

echo "🚀 TCP Security Shell ready! Try 'tcp-demo' to get started."
bash