#!/bin/bash
# Setup local LLMs on MacBook and Gentoo

echo "🚀 Setting up Local LLMs for TCP Burst Analysis"
echo "=============================================="

# Check if Ollama is installed locally
if command -v ollama &> /dev/null; then
    echo "✓ Ollama found locally"
    # Start Ollama if not running
    if ! pgrep -x "ollama" > /dev/null; then
        echo "Starting local Ollama..."
        ollama serve &
        sleep 5
    fi
    
    # Pull lightweight models if not present
    echo "Ensuring lightweight models are available..."
    ollama pull phi:2.7b 2>/dev/null || true
    ollama pull tinyllama 2>/dev/null || true
else
    echo "❌ Ollama not found locally. Install with: brew install ollama"
fi

# Setup MacBookPro Ollama
echo ""
echo "Setting up MacBookPro LLM..."
ssh sam@192.168.1.229 << 'EOF' 2>/dev/null || echo "Could not connect to MacBookPro"
if command -v ollama &> /dev/null; then
    echo "✓ Ollama found on MacBookPro"
    # Start Ollama if not running
    if ! pgrep -x "ollama" > /dev/null; then
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        sleep 5
    fi
    # Pull models
    ollama pull llama2:7b 2>/dev/null || true
    ollama pull mistral 2>/dev/null || true
else
    echo "Installing Ollama on MacBookPro..."
    brew install ollama
fi
EOF

# Setup Gentoo Ollama
echo ""
echo "Setting up Gentoo LLM..."
ssh sam@gentoo.local << 'EOF' 2>/dev/null || echo "Could not connect to Gentoo"
if command -v ollama &> /dev/null; then
    echo "✓ Ollama found on Gentoo"
    if ! pgrep -x "ollama" > /dev/null; then
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        sleep 5
    fi
    ollama pull codellama:7b 2>/dev/null || true
else
    echo "Ollama not found on Gentoo. Install manually."
fi
EOF

# Test endpoints
echo ""
echo "Testing LLM endpoints..."
echo "----------------------"

# Test local
curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && echo "✓ Local Ollama: Active" || echo "✗ Local Ollama: Inactive"

# Test MacBookPro
curl -s http://192.168.1.229:11434/api/tags > /dev/null 2>&1 && echo "✓ MacBookPro Ollama: Active" || echo "✗ MacBookPro Ollama: Inactive"

# Test Gentoo
curl -s http://gentoo.local:11434/api/tags > /dev/null 2>&1 && echo "✓ Gentoo Ollama: Active" || echo "✗ Gentoo Ollama: Inactive"

echo ""
echo "Ready for distributed TCP analysis!"