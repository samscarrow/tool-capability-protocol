Create a new Git worktree for researcher $ARGUMENTS. This sets up an isolated development environment for parallel Claude Code sessions.

Usage: /worktree-setup <researcher> <gate> [feature]

Examples:
- /worktree-setup aria-blackwood 3
- /worktree-setup yuki-tanaka 4 performance-opt

This will:
1. Create a new worktree at ~/tcp-worktrees/{researcher}-gate{gate}
2. Set up a new branch gate{gate}-{researcher}[-{feature}]
3. Copy researcher-specific configurations
4. Install dependencies with Poetry
5. Prepare for Claude Code session

Available researchers:
- aria-blackwood (Security Authority)
- elena-vasquez (Statistical/Behavioral Authority)
- marcus-chen (Distributed Systems Authority)
- yuki-tanaka (Performance Authority)
- sam-mitchell (Infrastructure Authority)
- alex-rivera (Quality Authority)
- claude-sonnet (Managing Director)