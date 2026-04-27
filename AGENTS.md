# Agent Team Instructions

## Agent Teams Architecture

This project uses **Claude Code Agent Teams** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) for a fully automated SDLC pipeline.

### Team Structure

- **Team Name**: `pashuraksha-sdlc`
- **Team Lead**: `team-lead` (orchestrator — decomposes, delegates, reviews, decides)
- **Teammates**: 34 specialists (below)
- **Entry Points**: `/pipeline`, `/review`, `/verify` slash commands

### How It Works

1. User triggers work via `/pipeline requirement <text>`, `/pipeline change`, `/pipeline release`, or `/review`
2. The slash command creates the team (`TeamCreate`) and spawns the Team Lead
3. Team Lead decomposes work into tasks (`TaskCreate`)
4. Team Lead spawns ONLY the relevant teammates (`Agent` with `team_name`)
5. Teammates work in parallel where possible, report back via `SendMessage`
6. Team Lead enforces quality gates, produces scorecard
7. Team Lead shuts down teammates when done

---

## Beads Task Tracking (MANDATORY)

This project uses Beads (`bd`) for persistent issue tracking across sessions:

1. **Always check beads first**: Run `bd ready --json` before starting any work
2. **Claim before working**: Run `bd update <id> --claim` before touching code
3. **Close when done**: Run `bd close <id> --reason "Done: <summary>"` after completing
4. **Never use TodoWrite for tracked work** — Beads is the single source of truth
5. **Never invent tasks** — only work on what exists in beads

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

---

## Team Lead

| Agent | File | Short Name | Purpose |
|-------|------|-----------|---------|
| Team Lead | `team-lead.md` | `team-lead` | Orchestrator: decompose, delegate, gate, decide, report |

## Teammates by Phase

### Design Phase
| Agent | File | Short Name | Purpose |
|-------|------|-----------|---------|
| UX Designer | `ux-designer.md` | `ux` | UI/UX review, accessibility, responsive design for rural farmers |
| Business Analyst | `business-analyst.md` | `ba` | Requirements mapping, gap analysis, stakeholder needs |

### Architecture Phase
| Agent | File | Short Name | Purpose |
|-------|------|-----------|---------|
| Software Architect | `software-architect.md` | `architect` | System design, API design, data modeling, scalability |
| Code Reviewer | `code-reviewer.md` | `reviewer` | Code quality, pattern adherence, best practices |

### Development Phase
| Agent | File | Short Name | Purpose |
|-------|------|-----------|---------|
| Backend Developer | `backend-developer.md` | `backend` | FastAPI, SQLAlchemy, async Python, REST APIs |
| Frontend Developer | `frontend-developer.md` | `frontend` | Next.js admin, Vite collection/vet, MUI, React |
| Mobile Developer | `mobile-developer.md` | `mobile` | Expo, React Native, i18n, offline-first, voice |
| Database Admin | `database-admin.md` | `dba` | Schema design, migrations, query optimization, indexes |

### Testing Phase — Functional (8 testers)
| Agent | File | Short Name | Purpose |
|-------|------|-----------|---------|
| QA Lead | `qa-lead.md` | `qa` | Test strategy, quality gates, coverage tracking |
| Unit Tester | `unit-tester.md` | `unit-test` | Isolated function/component tests (pytest, Jest) |
| Integration Tester | `integration-tester.md` | `integ-test` | Cross-component tests, API + DB workflows |
| E2E Tester | `e2e-tester.md` | `e2e` | Full user journey validation, 9 demo scenarios |
| API Tester | `api-tester.md` | `api-test` | REST API contracts, edge cases, error handling |
| Browser UI Tester | `browser-ui-tester.md` | `browser-test` | Playwright browser automation, form testing, navigation |
| Contract Tester | `contract-tester.md` | `contract` | Frontend-backend API shape agreement, OpenAPI validation |
| i18n Tester | `i18n-tester.md` | `i18n` | Kannada/Hindi translation, number formatting, voice |

### Testing Phase — Non-Functional (7 testers)
| Agent | File | Short Name | Purpose |
|-------|------|-----------|---------|
| Performance Tester | `performance-tester.md` | `perf` | Response times, query optimization, bundle analysis |
| Load Tester | `load-tester.md` | `load` | k6 concurrent user simulation, stress/spike/soak tests |
| Accessibility Tester | `accessibility-tester.md` | `a11y` | WCAG 2.1, screen readers, touch targets |
| Visual Regression Tester | `visual-regression-tester.md` | `vis-regress` | Screenshot comparison, theme consistency, UI drift |
| Chaos Tester | `chaos-tester.md` | `chaos` | Fault injection, service kills, network partitions |
| Network Resilience Tester | `network-resilience-tester.md` | `net-resil` | 2G/3G simulation, offline mode, PWA caching |
| Data Integrity Tester | `data-integrity-tester.md` | `data-integ` | Referential integrity, migration safety, concurrent writes |

### Security & Compliance Phase
| Agent | File | Short Name | Purpose |
|-------|------|-----------|---------|
| Security Analyst | `security-analyst.md` | `sec-analyst` | OWASP Top 10 review, threat modeling, static analysis |
| Security Tester | `security-tester.md` | `sec-tester` | Penetration testing, auth bypass, injection testing |
| Compliance Auditor | `compliance-auditor.md` | `compliance` | DPDP Act 2023, Aadhaar Act, data retention, consent |

### Production Readiness Phase
| Agent | File | Short Name | Purpose |
|-------|------|-----------|---------|
| NFR Validator | `nfr-validator.md` | `nfr` | 10-category scorecard: reliability, scalability, security, etc. |
| Observability Engineer | `observability-engineer.md` | `observ` | Logging, metrics, tracing, alerting, dashboards |

### Operations & Maintenance Phase
| Agent | File | Short Name | Purpose |
|-------|------|-----------|---------|
| DevOps Engineer | `devops-engineer.md` | `devops` | Docker, CI/CD, monitoring, health checks |
| Release Manager | `release-manager.md` | `release` | Release planning, version management, go/no-go |
| Technical Writer | `technical-writer.md` | `tech-writer` | API docs, user guides, architecture documentation |

### Domain Expertise
| Agent | File | Short Name | Purpose |
|-------|------|-----------|---------|
| Agritech Domain Expert | `agritech-domain-expert.md` | `domain` | ICAR/NDDB standards, dairy science, govt schemes |
| Rural UX Reviewer | `rural-ux-reviewer.md` | `rural-ux` | Farmer literacy, sunlight readability, touch targets |

---

## Slash Commands

| Command | File | Purpose |
|---------|------|---------|
| `/pipeline` | `commands/pipeline.md` | Full team pipeline: requirement, change, bug, or release mode |
| `/verify` | `commands/verify.md` | Quick verify: fast checks + build + tests on current diff |
| `/review` | `commands/review.md` | Agent-team-powered code review from multiple perspectives |

### Usage Examples

```bash
/pipeline                          # Auto-detect mode from git state
/pipeline requirement Add SMS alerts for disease outbreaks
/pipeline change                   # Verify current uncommitted changes
/pipeline release                  # Full pre-release sweep
/pipeline bug Login OTP not validating on first attempt
/verify                            # Quick check — stages 3-5 only
/review                            # Multi-agent code review of current diff
/review packages/api/app/routers/health.py  # Review a specific file
```

---

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
Team Lead deduplicates by file+line — keeps the higher-severity finding.
