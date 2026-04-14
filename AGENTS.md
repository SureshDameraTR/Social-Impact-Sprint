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

- **Monorepo**: `pashu-erp/` with 5 packages (api, admin, mobile, collection, vet)
- **Workspace manifest**: `pashu-erp/WORKSPACE.md` — complete file registry (single source of truth)
- **Package instructions**: Each package has its own `CLAUDE.md` that auto-loads per directory
- **Future**: Each package will become its own repo — no cross-package imports

## NVM Required

All npm/node commands require NVM:
```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
```

## SDLC Agent Suite

34 specialized agents covering the full software development lifecycle. Located in `.claude/agents/`.

### Design Phase
| Agent | File | Purpose |
|-------|------|---------|
| UX Designer | `ux-designer.md` | UI/UX review, accessibility, responsive design for rural farmers |
| Business Analyst | `business-analyst.md` | Requirements mapping, gap analysis, stakeholder needs |

### Architecture Phase
| Agent | File | Purpose |
|-------|------|---------|
| Software Architect | `software-architect.md` | System design, API design, data modeling, scalability |
| Code Reviewer | `code-reviewer.md` | Code quality, pattern adherence, best practices |

### Development Phase
| Agent | File | Purpose |
|-------|------|---------|
| Backend Developer | `backend-developer.md` | FastAPI, SQLAlchemy, async Python, REST APIs |
| Frontend Developer | `frontend-developer.md` | Next.js admin, Vite collection/vet, MUI, React |
| Mobile Developer | `mobile-developer.md` | Expo, React Native, i18n, offline-first, voice |
| Database Admin | `database-admin.md` | Schema design, migrations, query optimization, indexes |

### Testing Phase — Functional (8 testers)
| Agent | File | Purpose |
|-------|------|---------|
| QA Lead | `qa-lead.md` | Test strategy, quality gates, coverage tracking |
| Unit Tester | `unit-tester.md` | Isolated function/component tests (pytest, Jest) |
| Integration Tester | `integration-tester.md` | Cross-component tests, API + DB workflows |
| E2E Tester | `e2e-tester.md` | Full user journey validation, 9 demo scenarios |
| API Tester | `api-tester.md` | REST API contracts, edge cases, error handling |
| Browser UI Tester | `browser-ui-tester.md` | Playwright browser automation, form testing, navigation |
| Contract Tester | `contract-tester.md` | Frontend-backend API shape agreement, OpenAPI validation |
| i18n Tester | `i18n-tester.md` | Kannada/Hindi translation, number formatting, voice |

### Testing Phase — Non-Functional (7 testers)
| Agent | File | Purpose |
|-------|------|---------|
| Performance Tester | `performance-tester.md` | Response times, query optimization, bundle analysis |
| Load Tester | `load-tester.md` | k6 concurrent user simulation, stress/spike/soak tests |
| Accessibility Tester | `accessibility-tester.md` | WCAG 2.1, screen readers, touch targets |
| Visual Regression Tester | `visual-regression-tester.md` | Screenshot comparison, theme consistency, UI drift |
| Chaos Tester | `chaos-tester.md` | Fault injection, service kills, network partitions, cascading failures |
| Network Resilience Tester | `network-resilience-tester.md` | 2G/3G simulation, offline mode, PWA caching, rural connectivity |
| Rural UX Reviewer | `rural-ux-reviewer.md` | Farmer literacy, sunlight readability, touch targets, voice UI |
| Data Integrity Tester | `data-integrity-tester.md` | Referential integrity, migration safety, concurrent writes |

### Security & Compliance Phase
| Agent | File | Purpose |
|-------|------|---------|
| Security Analyst | `security-analyst.md` | OWASP Top 10 review, threat modeling, static analysis |
| Security Tester | `security-tester.md` | Penetration testing, auth bypass, injection testing |
| Compliance Auditor | `compliance-auditor.md` | DPDP Act 2023, Aadhaar Act, data retention, consent |

### Production Readiness Phase
| Agent | File | Purpose |
|-------|------|---------|
| NFR Validator | `nfr-validator.md` | 10-category scorecard: reliability, scalability, security, etc. |
| Observability Engineer | `observability-engineer.md` | Logging, metrics, tracing, alerting, dashboards |

### Operations & Maintenance Phase
| Agent | File | Purpose |
|-------|------|---------|
| DevOps Engineer | `devops-engineer.md` | Docker, CI/CD, monitoring, health checks |
| Release Manager | `release-manager.md` | Release planning, version management, go/no-go |
| Technical Writer | `technical-writer.md` | API docs, user guides, architecture documentation |

### Domain Expertise
| Agent | File | Purpose |
|-------|------|---------|
| Agritech Domain Expert | `agritech-domain-expert.md` | ICAR/NDDB standards, dairy science, govt schemes |

### Orchestration
| Agent | File | Purpose |
|-------|------|---------|
| Pipeline Orchestrator | `pipeline-orchestrator.md` | Master conductor: routes changes to agents, staged execution, scorecard |

## Slash Commands

These commands invoke the agent pipeline from any Claude Code session:

| Command | File | Purpose |
|---------|------|---------|
| `/pipeline` | `commands/pipeline.md` | Full pipeline: requirement, change, or release mode |
| `/verify` | `commands/verify.md` | Quick verify: fast checks + build + tests on current diff |
| `/review` | `commands/review.md` | Agent-powered code review from multiple perspectives |

### Usage Examples

```bash
/pipeline                          # Auto-detect mode from git state
/pipeline requirement Add SMS alerts for disease outbreaks
/pipeline change                   # Verify current uncommitted changes
/pipeline release                  # Full pre-release sweep
/verify                            # Quick check — stages 3-5 only
/review                            # Multi-agent code review of current diff
/review packages/api/app/routers/health.py  # Review a specific file
```

## Testing RACI Matrix

Resolves scope overlaps — each testing domain has one **Responsible** owner.

```
Legend: R = Responsible (owns it)  A = Accountable (reviews)  C = Consulted  I = Informed

                          qa   unit intg  e2e  api  brw  ctr  i18n perf load a11y vis  cha  net  rux  data sec  sec  com
                          lead tst  tst   tst  tst  tst  tst  tst  tst  tst  tst  tst  tst  tst  rev  tst  anl  pen  aud
                          ─────────────────────────────────────────────────────────────────────────────────────────────────
Unit tests (functions)     A    R    ·     ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·
Unit tests (components)    A    R    ·     ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·
API contract shapes        A    ·    ·     ·    C    ·    R    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·
API runtime behavior       A    ·    C     ·    R    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·
Cross-router workflows     A    ·    R     C    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·
Browser UI interaction     A    ·    ·     C    ·    R    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·
Visual consistency         A    ·    ·     ·    ·    C    ·    ·    ·    ·    ·    R    ·    ·    C    ·    ·    ·    ·
Full user journeys         A    ·    ·     R    ·    C    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·
Translation completeness   A    ·    ·     ·    ·    ·    ·    R    ·    ·    ·    ·    ·    ·    C    ·    ·    ·    ·
WCAG accessibility         A    ·    ·     ·    ·    C    ·    ·    ·    ·    R    ·    ·    ·    C    ·    ·    ·    ·
Rural farmer UX            A    ·    ·     ·    ·    ·    ·    C    ·    ·    C    ·    ·    C    R    ·    ·    ·    ·
API response times         A    ·    ·     ·    ·    ·    ·    ·    R    C    ·    ·    ·    ·    ·    ·    ·    ·    ·
Concurrent load            A    ·    ·     ·    ·    ·    ·    ·    C    R    ·    ·    ·    ·    ·    ·    ·    ·    ·
Service failure recovery   A    ·    ·     ·    ·    ·    ·    ·    ·    ·    ·    ·    R    ·    ·    ·    ·    ·    ·
Offline / slow network     A    ·    ·     ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    R    C    ·    ·    ·    ·
DB referential integrity   A    ·    ·     ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    R    ·    ·    ·
Static security analysis   A    ·    ·     ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    R    C    ·
Dynamic pen testing        A    ·    ·     ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    C    R    ·
Regulatory compliance      A    ·    ·     ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    ·    C    ·    R
```

**Conflict resolution**: When two agents find the same issue, the **R** agent's finding takes precedence.
Pipeline-orchestrator deduplicates by file+line — keeps the higher-severity finding.
