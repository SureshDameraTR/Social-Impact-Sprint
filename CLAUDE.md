# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->


## SDLC Agent Suite

This project has **34 specialized agents** in `.claude/agents/` covering the full software development lifecycle. Read `AGENTS.md` for the complete index.

### Pipeline Commands

| Command | Purpose |
|---------|---------|
| `/pipeline` | Full orchestrator — auto-detects mode (REQUIREMENT / CHANGE / RELEASE) |
| `/pipeline requirement <text>` | Design + implement + verify a new feature end-to-end |
| `/pipeline change` | Verify current uncommitted changes through all 8 stages |
| `/pipeline release` | Full pre-release sweep — all 34 agents |
| `/verify` | Quick check — stages 3-5 only (fast checks, build, tests) |
| `/review` | Multi-agent code review of current diff |

### How the Pipeline Works

1. Detects changed files via `git diff`
2. Routes to relevant agents via impact map (file pattern → agent matrix in `pipeline-orchestrator.md`)
3. Executes in staged parallel: Fast Checks → Build → Functional Tests → Quality → Security → Release Gate
4. Each stage gates — BLOCK stops, WARN continues
5. Produces an ASCII scorecard with per-stage pass/fail and VERDICT

### Agent Phases

- **Design**: ux-designer, business-analyst
- **Architecture**: software-architect, code-reviewer
- **Development**: backend-developer, frontend-developer, mobile-developer, database-admin
- **Functional Testing** (8): qa-lead, unit, integration, e2e, api, browser-ui, contract, i18n
- **Non-Functional Testing** (7): performance, load, accessibility, visual-regression, chaos, network-resilience, data-integrity
- **Security**: security-analyst, security-tester, compliance-auditor
- **Production Readiness**: nfr-validator, observability-engineer
- **Operations**: devops-engineer, release-manager, technical-writer
- **Domain**: agritech-domain-expert
- **Orchestration**: pipeline-orchestrator

## Build & Test

```bash
# API (FastAPI + PostgreSQL)
cd pashu-erp/packages/api
uv run ruff check app/                    # Lint
uv run pytest tests/ -v                   # Unit + integration tests

# Admin (Next.js 14 + Refine + MUI)
cd pashu-erp/packages/admin
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
pnpm install && npx next build            # Build check
npx playwright test                       # Browser tests (e2e/)

# Collection Centre (Vite + MUI PWA)
cd pashu-erp/packages/collection
pnpm install && npx vite build

# Docker (full stack)
cd pashu-erp
docker compose up -d                      # API(8000) + PostgreSQL(5432) + Mocks(8001)
```

## Workspace Navigation

- **Workspace manifest**: `pashu-erp/WORKSPACE.md` — complete file registry for all packages (the single source of truth for agents)
- **Agent index**: `AGENTS.md` — all 34 agents with phase grouping + RACI matrix
- **Package-level instructions**: Each package has its own `CLAUDE.md` (auto-loaded when working there)

## Architecture Overview

**PashuRaksha ERP** — Livestock management platform for rural Indian farmers.

| Package | Stack | Port | CLAUDE.md |
|---------|-------|------|-----------|
| API | FastAPI / SQLAlchemy / PostgreSQL | 8000 | `packages/api/CLAUDE.md` |
| Admin | Next.js 14 / Refine / MUI | 3000 | `packages/admin/CLAUDE.md` |
| Mobile | Expo 52 / React Native Paper | 8081 | `packages/mobile/CLAUDE.md` |
| Collection | Vite / MUI / PWA | 3001 | `packages/collection/CLAUDE.md` |
| Vet | Vite / MUI / Leaflet | 3002 | `packages/vet/CLAUDE.md` |
| Mocks | FastAPI | 8001 | `mocks/CLAUDE.md` |

## Workspace Manifest — MANDATORY Sync Rule

**`pashu-erp/WORKSPACE.md`** is the single source of truth for all 34 agents. It MUST stay in sync with the codebase.

**After ANY structural change, you MUST update WORKSPACE.md.** Structural changes include:
- Adding/removing/renaming a **model**, **router**, **schema**, or **service** in the API package
- Adding/removing/renaming a **page**, **component**, or **provider** in any frontend package
- Adding/removing/renaming a **screen** in the mobile package
- Adding/removing a **migration** in Alembic
- Changing **ports**, **auth roles**, or **API prefixes**
- Adding/removing a **mock router** or **mock data file**
- Adding/removing a **package** to the monorepo

**How to update**: Edit the relevant section in `pashu-erp/WORKSPACE.md` to reflect the change. Keep entries in the same format (table rows with file, route, data source columns).

**This is not optional.** If you create a new router but don't add it to WORKSPACE.md, every agent that reads the manifest will be unaware it exists. The pipeline orchestrator's impact map will miss it. Tests won't cover it.

## Conventions & Patterns

- **Python**: async everywhere, `ruff` for linting, type hints on public APIs
- **TypeScript**: strict mode, no `any`, MUI theme tokens (not raw colors)
- **API responses**: List endpoints return `{data: [], total: int}`, single items return object directly
- **Auth**: Every router endpoint requires `Depends(get_current_user)` — no exceptions
- **Database**: UUID primary keys, soft delete (`deleted_at`), audit trail (`created_at`, `updated_at`)
- **No cross-package imports** — each package will become its own repo
- **No mocking in production code** — mock backends are separate services behind configurable URLs
- **NVM required**: All npm/node commands need `nvm use 22` first
