#!/bin/bash
# sync_linguistic_branch.sh
# Main synchronization script for TCP linguistic evolution branch

set -e  # Exit on any error

echo "🔄 Starting TCP branch synchronization..."

# Ensure we're on main and up to date
git checkout main
git pull origin main

# Switch to linguistic branch
git checkout linguistic-evolution
git pull origin linguistic-evolution

# Merge main into linguistic-evolution
echo "📥 Merging main branch changes..."
git merge main --no-ff -m "Sync: Integrate latest TCP research from main branch

$(git log --oneline main ^linguistic-evolution | head -5)

This merge brings proven TCP advances into the linguistic evolution
experimental framework for continued research and validation."

# Push the synchronized branch
git push origin linguistic-evolution

echo "✅ Linguistic evolution branch synchronized with main"
echo "🧬 Ready for continued experimental development"