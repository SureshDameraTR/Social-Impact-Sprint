# Agent Instructions

## Beads Task Tracking (MANDATORY)

This project uses Beads (`bd`) for task tracking. Follow these rules strictly:

1. **Always check beads first**: Run `bd ready --json` before starting any work
2. **Claim before working**: Run `bd update <id> --claim` before touching code
3. **Close when done**: Run `bd close <id> --reason "Done: <summary>"` after completing
4. **Never use TodoWrite for tracked work** — Beads is the single source of truth
5. **Never invent tasks** — only work on what exists in beads
6. **Always use --json flag** for parsing: `bd ready --json`, `bd show <id> --json`

## Session Start Ritual

When starting a session:
1. Read this file (AGENTS.md)
2. Run `bd ready --json` to see available tasks
3. Report back what tasks are available before starting work

## Project Context

- **Monorepo**: `pashu-erp/` with 3 packages (api, admin, mobile)
- **Blueprints**: `docs/architecture.md`, `docs/compliance.md`, `docs/data-flow.md`
- **OpenSpec**: `openspec/` for change management
- **Future**: Each package will become its own repo — no cross-package imports

## NVM Required

All npm/node commands require NVM:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
```
