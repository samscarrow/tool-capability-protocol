#!/bin/bash
"""
Helper script to configure 1Password secrets for TCP deployment
"""

echo "🔐 TCP 1Password Secrets Configuration"
echo "====================================="

# Check for op CLI
if ! command -v op &> /dev/null; then
    echo "❌ 1Password CLI not found. Install with: brew install 1password-cli"
    exit 1
fi

# Check authentication
if ! op account list &> /dev/null; then
    echo "❌ 1Password not authenticated. Run: op signin"
    exit 1
fi

echo "🔍 Available 1Password items:"
op item list --format=table

echo ""
echo "📋 TCP requires these secrets:"
echo "   1. Anthropic API key (for LLM analysis)"
echo "   2. DigitalOcean API token (for droplet management)"
echo ""

# Helper for finding items
echo "🔍 Finding Anthropic items:"
op item list | grep -i anthropic || echo "   No Anthropic items found"

echo ""
echo "🔍 Finding DigitalOcean items:"
op item list | grep -i "digital\|ocean\|do" || echo "   No DigitalOcean items found"

echo ""
echo "📝 Configuration needed in ~/.config/op-secrets.sh:"
echo ""
echo "# Anthropic API Key"
echo "export ANTHROPIC_OP_VAULT=\"Personal\""
echo "export ANTHROPIC_OP_UUID=\"your_anthropic_uuid_here\""
echo "export ANTHROPIC_OP_FIELD=\"credential\""
echo ""
echo "# DigitalOcean API Token"  
echo "export DIGITALOCEAN_OP_VAULT=\"Personal\""
echo "export DIGITALOCEAN_OP_UUID=\"your_do_uuid_here\""
echo "export DIGITALOCEAN_OP_FIELD=\"credential\""
echo ""
echo "💡 Use 'op item get <uuid>' to verify your items"

