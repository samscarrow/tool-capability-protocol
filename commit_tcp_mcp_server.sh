#!/bin/bash
# Script to commit TCP-MCP server changes in the main dev repository

echo "Committing TCP-MCP server implementation..."

# Navigate to main dev repository
cd /Users/sam/dev

# Add all TCP-MCP server files
git add ai-ml/mcp-servers/core/tcp-mcp-server/

# Check what will be committed
echo "Files to be committed:"
git status --porcelain | grep "^A\|^M" | grep "tcp-mcp-server"

# Create the commit
git commit -m "Implement TCP-MCP Protocol Bridge server

- Create FastMCP server exposing TCP security intelligence
- Implement TCP descriptor database with 709+ commands
- Add agent safety monitor with TCP-guided containment
- Create hierarchical encoder for tool families (3.4:1 compression)
- Define MCP schemas for consistent response formats

Bridge architecture enables:
- Microsecond security decisions via MCP tools
- Access to TCP binary descriptors through resources
- Safe alternative generation with quarantine patterns
- Migration path to future standalone TCP protocol

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Show the result
echo "Commit created. Run 'git push' in /Users/sam/dev to push the changes."