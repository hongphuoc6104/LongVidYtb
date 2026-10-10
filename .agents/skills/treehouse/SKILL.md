---
name: treehouse
description: Git worktree manager for parallel AI agent workflows with file locking in .worktrees/ to prevent file conflicts.
---

# Treehouse — Worktree & Multi-Agent Isolation

This skill guides the agent in using `treehouse` for isolating changes, managing Git worktrees, and preventing conflicts across concurrent tasks.

## Key Invariants
- Worktrees are created in `.worktrees/` per `treehouse.json`.
- `.worktrees/` is excluded from Git tracking via `.gitignore`.
- Always lock a worktree when starting active development and unlock/complete upon finish.

## Common Commands
- `treehouse status`: View active worktrees and their current branch.
- `treehouse create <name> [branch]`: Create a clean, isolated worktree.
- `treehouse lock <name> --agent <agent-id> --message <reason>`: Lock worktree to prevent conflicts.
- `treehouse complete <name> --merge`: Complete the task and merge back into base branch.
- `treehouse unlock <name>`: Release lock on worktree.
- `treehouse remove <name>`: Clean up completed worktree.
