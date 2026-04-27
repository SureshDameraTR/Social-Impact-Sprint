# SDLC Agent Suite — Comprehensive Context Audit

**Date**: 2026-04-15
**Scope**: All 35 agents, 8 baselines, 3 slash commands, pipeline orchestration
**Purpose**: First-time deep audit — reference for all future sessions

---

## 1. Agent Inventory (35 total)

### Phase Map

| Phase | Agents | Count |
|-------|--------|-------|
| Design | ux-designer, business-analyst | 2 |
| Architecture | software-architect, code-reviewer | 2 |
| Development | backend-developer, frontend-developer, mobile-developer, database-admin | 4 |
| Functional Testing | qa-lead, unit-tester, integration-tester, e2e-tester, api-tester, browser-ui-tester, contract-tester, i18n-tester | 8 |
| Non-Functional Testing | performance-tester, load-tester, accessibility-tester, visual-regression-tester, chaos-tester, network-resilience-tester, rural-ux-reviewer, data-integrity-tester | 8 |
| Security & Compliance | security-analyst, security-tester, compliance-auditor | 3 |
| Production Readiness | nfr-validator, observability-engineer | 2 |
| Operations | devops-engineer, release-manager, technical-writer | 3 |
| Domain | agritech-domain-expert | 1 |
| Orchestration | pipeline-orchestrator | 1 |
| **Total** | | **34 + 1 orchestrator = 35** |

### Tool Access Matrix

| Tools | Agents |
|-------|--------|
| Read-only (Read, Glob, Grep, Bash, Agent) | code-reviewer, qa-lead, rural-ux-reviewer, i18n-tester, release-manager |
| Read + WebSearch | business-analyst, compliance-auditor, nfr-validator, technical-writer |
| Read + WebSearch + WebFetch | ux-designer, software-architect, security-analyst, performance-tester, accessibility-tester, agritech-domain-expert |
| Read + Edit + Write | backend-developer, frontend-developer, mobile-developer, database-admin, unit-tester, integration-tester, e2e-tester, api-tester, browser-ui-tester, contract-tester, load-tester, visual-regression-tester, chaos-tester, network-resilience-tester, data-integrity-tester, security-tester, observability-engineer, devops-engineer, pipeline-orchestrator |

---

## 2. Per-Agent Context Summaries

### DESIGN PHASE

#### ux-designer
- **Role**: Rural-first UI/UX review across all 4 frontend packages
- **Key checks**: Theme token usage, touch targets (48x48px min), contrast ratios, responsive breakpoints (xs/sm/md/lg/xl), offline states, voice UI affordances
- **Design principles**: Rural-first, Voice-enabled (Sarvam AI), Visual over textual, Forgiving (large targets, confirmations), Progressive disclosure, Cultural context
- **Theme tokens**: Primary #0d6b58, Secondary #1e3a5f, IBM Plex Sans (web), 8px grid, border-radius 12/16/8
- **Artifacts**: None (provides design feedback, no report files)
- **Baselines**: None

#### business-analyst
- **Role**: Requirements mapping, gap analysis, feature completeness against vision
- **Key checks**: 18 business features tracked (API + admin + mobile status), 9 demo scenarios validation, 5 stakeholder needs mapping
- **Business rules embedded**: Milk pricing (FAT%/SNF%), disease triage (55+ ICAR rules, 4 risk levels), feed formulation (NDDB 60/40 roughage/concentrate), insurance (premium/coverage/subsidy), 5 government schemes (PM-KISAN, LISS, PM-KMY, NLM, RKVY)
- **Impact assessment**: Users affected, workflows impacted, schema changes, compliance, localization
- **Artifacts**: `reports/latest/business-analyst.md`, `reports/history/YYYY-MM-DD-business-analyst.md`
- **Baselines**: Reads previous `reports/latest/business-analyst.md` for diff

### ARCHITECTURE PHASE

#### software-architect
- **Role**: System design, API design, data modeling, scalability decisions
- **Key checks**: Architecture review (coupling, cohesion, dependencies), API design (RESTful, pagination, versioning), integration architecture (configurable URLs, circuit breaker, health checks), data architecture (UUID PKs, JSONB, soft delete, NUMERIC not FLOAT), security architecture (STRIDE, CSRF, CORS, Aadhaar protection)
- **9 decisions already made**: Monorepo + pnpm, FastAPI async, SQLAlchemy 2.0 async + asyncpg (pool 10+20), JWT HS256 24h, OTP phone-first, soft delete + audit trail, mock backends separate, disease triage 55+ rules, NDDB feed standards
- **Scalability target**: 10,000 concurrent farmers per district
- **Output format**: ADR (Architecture Decision Records)
- **Artifacts**: None (produces ADRs inline, no report files)
- **Baselines**: None

#### code-reviewer
- **Role**: Code quality enforcement across Python + TypeScript + React Native
- **Checklist (5 categories)**: Correctness (logic, edge cases, error paths, transactions), Security (auth, injection, PII, CORS/CSRF), Performance (N+1, pagination, indexes), Maintainability (functions <50 lines, naming, no dead code), Testing (new code has tests)
- **Standards enforced**: Python (ruff, type hints, async, ORM-only, AuditMixin/SoftDeleteMixin), TypeScript (no any, theme tokens, error boundaries, loading skeletons), React Native (Expo managed, Paper not MUI, i18next, expo-secure-store), General (no console.log, no TODO without beads, no mock data in prod, soft delete only, UUID PKs only)
- **Architecture patterns**: Router -> Service -> Model layering, Refine data providers (admin), Axios interceptors (collection), ApiClient with retry (mobile), Alembic-only migrations, NUMERIC not FLOAT
- **Artifacts**: `reports/latest/code-reviewer.md`, `reports/history/YYYY-MM-DD-code-reviewer.md`
- **Baselines**: Reads previous `reports/latest/code-reviewer.md` for diff

### DEVELOPMENT PHASE

#### backend-developer
- **Role**: FastAPI endpoints, SQLAlchemy models, migrations, services, middleware
- **Critical rules**: Always async, always filter soft-deleted, always add auth, always paginate lists, never raw SQL, never hardcode config, NUMERIC(12,2) for money, UUID PKs, JSONB for flexible data, structured logging only
- **Code patterns**: Router pattern (with Depends, pagination, soft-delete filter), Model pattern (AuditMixin + SoftDeleteMixin + Base), Service pattern (error handling), Migration pattern (alembic commands)
- **Models reference**: 10 key tables documented (User, Animal, HealthEvent, YieldLog, MilkCollectionCenter, MilkCollectionRecord, Transaction, InsurancePolicy, VetConsultation, GovtScheme)
- **Artifacts**: None
- **Baselines**: None

#### frontend-developer
- **Role**: Next.js admin, Vite collection/vet, React components, MUI
- **Critical rules**: No any, no hardcoded colors (use theme.palette.*), loading skeletons, empty states, error boundaries, auth guards, responsive mobile-first, accessibility (ARIA, keyboard, contrast), Leaflet SSR (dynamic import ssr:false), server-side pagination
- **3 apps owned**: Admin (Next.js 14.2 + Refine + MUI, port 3000), Collection (Vite 5.4 + React 18 + MUI + PWA, port 3001), Vet (Vite 5.4 + React 18 + MUI + Leaflet, port 3002)
- **Theme**: Primary #0d6b58, Secondary #1e3a5f, always theme tokens
- **Artifacts**: None
- **Baselines**: None

#### mobile-developer
- **Role**: Expo 52 farmer app, offline-first, voice input, i18n, camera
- **Critical rules**: Expo managed (never eject), React Native Paper (not MUI), all strings via i18next, expo-secure-store for tokens, touch targets 48x48px min, offline handling (cached data + queue writes), voice-first (MicButton), error states, pull-to-refresh, no PII in logs
- **Target user**: Rural Indian farmer — basic smartphone, limited literacy, Kannada primary, 2G/3G, outdoors/sunlight, one-handed
- **26 screens**: tabs (home, milk, health, income, sell), auth, animal CRUD, vaccinations, medicine-log, advisory, weather, feed-calculator, insurance, ethno-vet, smart-farm, pashu-aadhaar, community-alerts, my-consultations, profile, onboarding (4 steps)
- **6 locale files**: en, kn, hi, gu, ta, te (186 keys each)
- **Artifacts**: None
- **Baselines**: None

#### database-admin
- **Role**: Schema design, migrations, query optimization, indexes, integrity, maintenance
- **Migration safety**: Nullable first then backfill, never drop columns, CREATE INDEX CONCURRENTLY, test against prod copy, NUMERIC(12,2), JSONB defaults
- **4 integrity SQL checks**: Orphaned animals, soft-deleted parents with active children, duplicate phones, financial precision
- **5 performance SQL checks**: Table sizes, index usage, missing indexes, active connections, long-running queries
- **25 tables documented**: Full schema with PKs, key columns, relationships
- **10 expected indexes**: users(phone unique, district), animals(owner_id, species, deleted_at), yield_logs(animal_id, recorded_at), health_events(animal_id), milk_collection_records(center_id, collected_at), transactions(user_id, created_at), vet_consultations(status)
- **11 migration versions** (verified clean chain, no duplicates): d22bbd14c60e (initial) -> a1b2c3d4e5f6 (performance_indexes) -> g7h8i9j0k1l2 (gender) -> b7c8d9e0f1a2 (otp_requests) -> c8d9e0f1a2b3 (reference_data) -> e3f4a5b6c7d8 (float_to_numeric) -> f4a5b6c7d8e9 (audit_softdelete) -> b2c3d4e5f6a7 (vet_consultations) -> c0mp051t31dx (composite_indexes) -> d4e5f6a7b8c9 (FK constraints + updated_at + yield_logs unique) -> e5f6a7b8c9d0 (refresh_tokens)
- **Artifacts**: None
- **Baselines**: None

### FUNCTIONAL TESTING PHASE

#### qa-lead
- **Role**: Test strategy, quality gates, coverage tracking, go/no-go decisions
- **Testing pyramid**: ~10 E2E, ~50 integration, ~200 unit
- **4 quality gates**: Pre-commit (ruff), PR (CI green), Pre-release (E2E + security), Post-deploy (health + no errors)
- **3-tier priority**: P1 (patient/financial safety: disease rules, milk pricing, feed, auth), P2 (core workflows: animal CRUD, milk collection, health, insurance, onboarding), P3 (supplementary: advisory, weather, IoT, marketplace, SHG)
- **9 quality metrics**: Unit count (200+), pass rate (100%), integration count (50+), backend coverage (70%+), frontend coverage (60%+), Lighthouse a11y (90+), Lighthouse perf (80+), API P95 (<500ms), vulnerabilities (0 critical)
- **Delegates to**: unit-tester, integration-tester, e2e-tester, performance-tester, accessibility-tester, api-tester, security-tester
- **Artifacts**: `reports/latest/qa-lead.md`, `reports/history/YYYY-MM-DD-qa-lead.md`
- **Baselines**: Reads `reports/baselines/coverage.json`

#### unit-tester
- **Role**: Isolated function/component tests (pytest, Jest, RTL)
- **4 frameworks**: API (pytest + pytest-asyncio), Admin (Jest + RTL), Mobile (Jest + RTL), Collection (Vitest)
- **Coverage targets**: Disease rules 100%, feed calculator 95%, auth middleware 95%, price calculations 95%, UI components 80%, API routers 70%
- **10 principles**: Test behavior not implementation, one assertion, descriptive names (test_func_scenario_expected), AAA pattern, mock externals, edge cases, error paths, no interdependence, fast, no real DB/network
- **Artifacts**: `reports/latest/unit-tester.md`, `reports/history/YYYY-MM-DD-unit-tester.md`
- **Baselines**: Reads `reports/baselines/coverage.json`

#### integration-tester
- **Role**: Cross-component tests hitting real DB and services (not mocks)
- **Requires**: Running Docker stack (db, mock-backends, api)
- **Fixtures**: base_url, farmer_token, admin_token, farmer_user_id, auth_header()
- **9 key workflows**: OTP login -> protected endpoint (Critical), register animal -> health -> triage (Critical), milk collection -> settlement -> finance (Critical), insurance policy -> claim (High), vet consultation -> diagnosis (High), marketplace -> income (High), onboarding -> profile -> animal (Medium), weather -> TTS (Medium), IoT -> readings -> alerts (Medium)
- **8 principles**: Hit real services, test end-to-end data flow, verify side effects, test auth at boundaries, clean up, deterministic, ordered when needed, timeout tolerance
- **Artifacts**: `reports/latest/integration-tester.md`, `reports/history/YYYY-MM-DD-integration-tester.md`
- **Baselines**: Previous report diff only

#### e2e-tester
- **Role**: Full user journey validation across all apps
- **4 apps**: Admin (3000), Collection (3001), Vet (3002), Mobile (8081)
- **5 critical journeys**: Farmer onboarding (mobile, 6 steps), daily milk collection (collection, 7 steps), health alert -> vet response (cross-app, 6 steps), admin dashboard overview (admin, 7 steps), insurance claim (mobile -> admin, 5 steps)
- **9 demo scenarios**: All mapped to business vision
- **Artifacts**: `reports/latest/e2e-tester.md`, `reports/history/YYYY-MM-DD-e2e-tester.md`
- **Baselines**: Previous report diff only

#### api-tester
- **Role**: REST API contracts, edge cases, error handling across 27 routers
- **27 routers documented**: Each with prefix, auth type, key verifications
- **6 test categories**: Contract (response envelope), Auth (401/403), Pagination (skip/limit), Errors (404/422), Edge cases (empty/long/unicode), CRUD lifecycle (create -> soft delete -> verify hidden)
- **Response standards**: Lists return `{data: [], total: int}`, singles return object, errors return `{detail: "..."}`
- **Artifacts**: `reports/latest/api-tester.md`, `reports/history/YYYY-MM-DD-api-tester.md`
- **Baselines**: Previous report diff only

#### browser-ui-tester
- **Role**: Playwright browser automation across admin, collection, vet
- **Current state**: 30+ admin smoke tests exist. Collection and vet have ZERO tests (gap)
- **Page Object Model**: AdminDashboardPage pattern provided
- **5 viewports**: Desktop (1920x1080), Laptop (1366x768), Tablet-L (1024x768), Tablet-P (768x1024), Mobile (375x667)
- **Network interception**: Slow API simulation (2s delay), API failure simulation (500)
- **Accessibility in browser**: axe-core with wcag2a + wcag2aa tags
- **data-testid conventions**: stat-card, milk-chart, alert-map, admin-sidebar, loading-skeleton, error-state
- **Artifacts**: `reports/latest/browser-ui-tester.md`, `reports/history/YYYY-MM-DD-browser-ui-tester.md`
- **Baselines**: Previous report diff only

#### contract-tester
- **Role**: Frontend-backend API shape agreement, OpenAPI compliance
- **Catches**: Field naming mismatches, added required fields, type changes, pagination envelope inconsistency, error format variation
- **3 response standards**: Lists `{data: [], total}`, singles direct object, errors `{detail: "..."}`
- **13 list endpoints tested**: animals, health, milk, marketplace, advisory/tips, alerts/nearby, vaccination/due, medicine, feed/ingredients, ethno-vet/remedies, iot/devices, schemes, map-points/points
- **4 entity required fields**: Animal {id, name, species, created_at}, Health Event {id, animal_id, symptoms, created_at}, Milk Record {id, animal_id, quantity_liters, session}, User Profile {id, phone, role, language}
- **Breaking change detection**: OpenAPI baseline diff
- **Artifacts**: `reports/latest/contract-tester.md`, `reports/history/YYYY-MM-DD-contract-tester.md`
- **Baselines**: Uses `openapi-baseline.json` for breaking change detection

#### i18n-tester
- **Role**: Translation completeness, Indic script rendering, number/date/currency formatting, voice I/O
- **6 languages**: English (full), Kannada (primary, full), Hindi (partial), Gujarati (partial), Tamil (partial), Telugu (partial)
- **186 keys** per locale, all at 100% key coverage (gu/ta/te may be machine-generated stubs)
- **8 test categories**: Translation completeness (Python key diff script), hardcoded string detection (grep), Kannada script rendering (conjuncts, numerals), number/currency formatting (Indian: 1,00,000), voice I/O (Sarvam AI STT/TTS), backend bilingual content (*_en/*_kn fields), text overflow (Kannada 20-40% longer), user language preference persistence
- **13-item checklist**: All strings use t(), 100% key coverage, Kannada rendering, INR formatting, locale dates, voice I/O, text overflow, number input accepts both scripts, language persistence, bilingual backend, error messages in user language, placeholder text
- **Artifacts**: `reports/latest/i18n-tester.md`, `reports/history/YYYY-MM-DD-i18n-tester.md`
- **Baselines**: Reads `reports/baselines/i18n.json`

### NON-FUNCTIONAL TESTING PHASE

#### performance-tester
- **Role**: Response times, query perf, bundle sizes, Lighthouse, memory, connection pool
- **Performance targets**: API P50 <200ms, P95 <500ms, P99 <1000ms, DB query <50ms, Admin FCP <2s, LCP <3s, Mobile cold start <3s, Admin JS bundle <500KB gzip, Collection PWA <300KB gzip, 100+ concurrent users/district
- **7 hotspots**: /v1/admin/stats (high, multi-table), /v1/admin/charts/milk (high, 30-day), /v1/health (medium, JSONB), /v1/map-points (medium, geospatial), /v1/animals?limit=100 (medium, relationships), /v1/weather (high, external HTTP), /v1/iot/readings (medium, time-series)
- **Checks**: SQL echo N+1 detection, missing index detection (pg_indexes), slow query analysis (pg_stat_statements), bundle analysis (next build, vite build), Lighthouse CLI, React performance patterns, database index verification
- **Artifacts**: `reports/latest/performance-tester.md`, `reports/history/YYYY-MM-DD-performance-tester.md`
- **Baselines**: Reads `reports/baselines/performance.json`

#### load-tester
- **Role**: k6 concurrent user simulation, stress/spike/soak tests
- **4 test types**: Baseline (10->50->100 VUs, p95<500), Stress (200->500->1000 VUs, p95<2000), Spike (10->500 in 10s, morning rush), Soak (50 VUs 30min, leak detection)
- **Targets**: 100 concurrent users/district, 500 req/s aggregate, P50 <200ms, P95 <500ms, error rate <0.1%, DB max 30 connections, API memory <512MB
- **Special tests**: Connection pool exhaustion (35 VUs > 30 max), write contention (50 concurrent milk yields), realistic weighted scenarios (30% browse, 20% health, 15% milk write, 10% admin, 10% weather, 15% milk read)
- **Artifacts**: `reports/latest/load-tester.md`, `reports/history/YYYY-MM-DD-load-tester.md`
- **Baselines**: Reads `reports/baselines/load.json`

#### accessibility-tester
- **Role**: WCAG 2.1 Level AA compliance across all frontend packages
- **Automated tools**: Lighthouse a11y, axe-core CLI, pa11y (WCAG2AA)
- **Source code checks**: Missing alt text, empty buttons/links, form labels, role attributes
- **Full WCAG 2.1 AA checklist**: Perceivable (text alternatives, contrast 4.5:1/3:1, adaptable, distinguishable), Operable (keyboard nav, touch 48x48px min + 8px spacing, timing), Understandable (language declared, forms with error messages), Robust (valid HTML, ARIA, status announcements)
- **Theme colors to verify**: Primary #0d6b58 on white, error red on white, warning amber on white, text on colored cards
- **User population**: Age 18-70, low-moderate digital literacy, budget Android 720p, bright sunlight, dirty/wet hands
- **Artifacts**: `reports/latest/accessibility-tester.md`, `reports/history/YYYY-MM-DD-accessibility-tester.md`
- **Baselines**: Reads `reports/baselines/accessibility.json`

#### visual-regression-tester
- **Role**: Playwright screenshot comparison for detecting unintended UI changes
- **Config**: maxDiffPixelRatio 0.01, threshold 0.2, animations disabled, 3 viewports (desktop 1280x720, tablet 768x1024, mobile 375x667), locale en-IN, timezone Asia/Kolkata
- **8 full-page screenshots**: Dashboard, Farmers, Animals, Health, Milk, Map (masked tiles), Schemes, Login
- **Component screenshots**: StatCard variants, Risk badge variants (4 levels), Species chip set
- **Theme verification**: Sidebar must be rgb(13, 107, 88) across 5 pages
- **Dynamic content masking**: .recharts-wrapper, .leaflet-tile-container, [data-testid='timestamp'], [data-testid='count']
- **Anti-flakiness**: Disable animations, network idle, skeleton disappear, mask dynamic, consistent viewport/locale, seed DB
- **Artifacts**: `reports/latest/visual-regression-tester.md`, screenshots in `e2e/visual/visual-regression.spec.ts-snapshots/`
- **Baselines**: Golden screenshots (Playwright snapshots)

#### chaos-tester
- **Role**: Fault injection, service kills, network partitions, cascading failures
- **6 failure categories**: Service kill (docker kill), DB failure (kill mid-request, pool exhaustion, slow via pg_sleep), external service failure (mock down -> 503 not 500, malformed JSON), network degradation (500ms latency via tc netem, 10% packet loss, DNS failure), resource exhaustion (memory 100MB, disk 10K requests, CPU 0.1 cores), concurrent failures (mock down + DB latency)
- **Frontend resilience**: Admin handles API timeout (error not blank), Admin handles 500 (error UI), Collection offline (PWA cache)
- **Recovery checklist**: Auto-restart <30s, no data loss, no orphaned transactions, useful error logs, friendly error messages, full performance <60s
- **Rural context**: Power cuts (restart mid-transaction), network drops (2G/3G), OOM kills, shared hosting contention
- **Artifacts**: `reports/latest/chaos-tester.md`, `reports/history/YYYY-MM-DD-chaos-tester.md`
- **Baselines**: Previous report diff only

#### network-resilience-tester
- **Role**: Offline-first, 2G/3G simulation, retry logic, data sync, PWA offline
- **Network profiles**: 4G (4Mbps/3Mbps/20ms), 3G (200Kbps/100Kbps/300ms), 2G (25Kbps/6Kbps/1000ms), Edge (6Kbps/3Kbps/2000ms), Offline
- **Real-world conditions**: 4G urban (district HQ), 3G semi-urban (taluk), 2G rural (village), Edge/no signal (remote pastures), Intermittent (moving between towers)
- **Tests**: API client retry (3x on 500, no retry on 4xx, 15s timeout, exponential backoff 1s/2s/4s), Playwright throttling (3G <10s, 2G skeleton <3s + load <30s, offline handling, intermittent 5 cycles), API with DB latency (500ms), weather with 5s mock delay
- **Known gaps documented**: No NetInfo listener, no offline queue, no background sync, no PWA offline data, no offline indicator, no retry button, no local cache
- **Artifacts**: `reports/latest/network-resilience-tester.md`, `reports/history/YYYY-MM-DD-network-resilience-tester.md`
- **Baselines**: Previous report diff only

#### rural-ux-reviewer
- **Role**: Farmer-specific UX (distinct from accessibility/WCAG)
- **7 review criteria**: Language & comprehension (no English-only, <10 words/label, icons+text), Visual for outdoors (7:1 contrast AAA, 16px min body, bold for key info, no light-gray-on-white, triple redundancy status), Touch & motor (48dp min, prefer 56dp, 8dp gaps, no double-tap required, full-width buttons), Network & performance (offline flows, skeleton <200ms, lazy images, no auto-video, form data preserved, retries), Voice & audio (TTS for weather/advisory, visible controls, correct language variant), Cultural (local breeds, INR, DD/MM/YYYY, kg/litres/acres, no red/green only), Information architecture (critical info above fold, max 3 taps, consistent nav, no dead ends, confirmation before delete)
- **Device context**: Budget Android 720p, 2-4GB RAM, Android 10-12, 2G-4G, app <30MB
- **Distinction from accessibility-tester**: Rural UX covers literacy/comprehension, sunlight readability, field conditions (wet hands), 2G bandwidth, voice-first, cultural icons. Accessibility covers screen readers, keyboard nav, ARIA, GIGW
- **Artifacts**: `reports/latest/rural-ux-reviewer.md`, `reports/history/YYYY-MM-DD-rural-ux-reviewer.md`
- **Baselines**: Previous report diff only

#### data-integrity-tester
- **Role**: Referential integrity, migration safety, business rule constraints, concurrent writes
- **7 test suites**: Referential integrity (7 orphan checks across animals, health, yields, milk records, insurance claims, vet consultations, medicine administrations), Soft delete consistency (cascade, API filtering, existence, reasonable timestamps), Audit trail (created_at not null, updated_at >= created_at, valid created_by), Business rules (unique phones, unique pashu_aadhaar, valid role/species enums, milk 0-50L, FAT/SNF 0-15%, 2-decimal financial, coverage >= premium), JSONB validation (symptoms array, eligibility non-empty, photo_urls array), Migration safety (backup, count, upgrade, rollback, count diff, integrity, API check), Concurrent writes (50 async POSTs, >=45 success, 0 server errors, correct total)
- **Full audit script**: Combined bash/SQL checking orphans, cascades, duplicates, negatives, future dates, nulls, time paradoxes
- **Artifacts**: `reports/latest/data-integrity-tester.md`, `reports/history/YYYY-MM-DD-data-integrity-tester.md`
- **Baselines**: Previous report diff only

### SECURITY & COMPLIANCE PHASE

#### security-analyst
- **Role**: Static security review — OWASP Top 10, auth/authz, DPDP, input validation, infrastructure, dependencies
- **OWASP coverage**: A01 (broken access), A02 (crypto), A03 (injection), A04 (insecure design), A05 (misconfiguration), A06 (vulnerable components), A07 (auth failures), A08 (data integrity), A09 (logging), A10 (SSRF)
- **Auth audit**: Every endpoint has auth, no privilege escalation, JWT handling, OTP security, IDOR
- **Data protection**: Aadhaar hash+last-4 only, PII in logs, soft delete, consent, minimization
- **Finding format**: Severity, OWASP category, location, finding, impact, remediation with code, verification
- **Artifacts**: `reports/latest/security-analyst.md`, `reports/history/YYYY-MM-DD-security-analyst.md`
- **Baselines**: Reads `reports/baselines/security.json`

#### security-tester
- **Role**: Dynamic penetration testing — writes and executes actual test code
- **7 test suites**: Auth (OTP brute force 15 attempts, JWT tampering alg:none/HS384), SQL injection (5 payloads in query + JSON body), CSRF (no token, mismatched token), Authorization/IDOR (farmer A can't see/modify farmer B), XSS (4 script/event payloads), Security headers (nosniff, DENY, HSTS, referrer), Aadhaar protection (no 12-digit in responses or logs)
- **Test file**: `tests/test_security.py`
- **Dependency scans**: `pip-audit` (Python), `npm audit` (admin, collection, mobile)
- **Artifacts**: `reports/latest/security-tester.md`, `reports/history/YYYY-MM-DD-security-tester.md`
- **Baselines**: Reads `reports/baselines/security.json` (shared with security-analyst)

#### compliance-auditor
- **Role**: Regulatory compliance — DPDP Act 2023, Aadhaar Act, IT Act (legal, not technical)
- **7 audit sections**: A-Data Collection & Consent (privacy notice, consent checkbox, purpose stated), B-Aadhaar (hash+last-4, never log/store/transmit plaintext), C-Data Retention (SoftDeleteMixin, filtered queries, export/deletion endpoints, retention periods), D-Audit Trail (AuditMixin, created/updated/deleted_at/by), E-Access Control (auth guards on all endpoints), F-Data Encryption (DB SSL, expo-secure-store, httpOnly cookies, HTTPS/HSTS), G-Third-Party Sharing (weather/IoT/registry/storage/Sarvam data flows)
- **4 regulatory frameworks**: DPDP Act 2023 (7 principles), Aadhaar Act 2016 (5 rules), IT Act 2000 (Section 43A), ISO 27001
- **Artifacts**: `reports/latest/compliance-auditor.md`, `reports/history/YYYY-MM-DD-compliance-auditor.md`
- **Baselines**: Reads `reports/baselines/compliance.json` (separate from security.json)

### PRODUCTION READINESS PHASE

#### nfr-validator
- **Role**: 10-category scorecard — reliability, availability, scalability, performance, security, observability, maintainability, usability, compliance, operability
- **Production threshold**: 70/100 minimum, no Critical items failing
- **Each scored /10**: Reliability (99.5% uptime, MTBF>72h, MTTR<5min), Availability (health<100ms, restart<30s), Scalability (100 concurrent, 1M+ rows), Performance (P50<200, P95<500, FCP<2s, bundle<500KB), Security (OWASP clean, no secrets, JWT validation, CSRF), Observability (structured JSON logs, request IDs, error context), Maintainability (ruff clean, strict TS, 70% backend coverage), Usability (WCAG AA, a11y>90, touch 48x48, EN+KN), Compliance (DPDP, Aadhaar hash, soft delete, consent), Operability (docker compose up, alembic, env vars, seed, backup)
- **Depends on**: security-analyst, chaos-tester, accessibility-tester, i18n-tester, compliance-auditor, load-tester outputs
- **Artifacts**: `reports/latest/nfr-validator.md`, `reports/history/YYYY-MM-DD-nfr-validator.md`
- **Baselines**: Reads `reports/baselines/nfr-scorecard.json`

#### observability-engineer
- **Role**: Logs, metrics, traces across the three pillars
- **Existing**: JSON structured logging, health checks (/health, /ready), request IDs (X-Request-ID), request timing (duration_ms), Docker health checks
- **Missing/gaps**: Prometheus/StatsD metrics (Critical), distributed tracing/OpenTelemetry (High), error tracking Sentry/Rollbar (Critical), APM (Medium), alert rules (High), Grafana dashboard (Medium), log aggregation (Medium), Web Vitals monitoring (High), mobile crash reporting (High)
- **7 alert rules defined**: API down (critical, /health non-200 >1min), high error rate (critical, 5xx>5% >5min), slow responses (warning, P95>2s >10min), DB pool exhausted (warning, >28 active), disk low (warning, >80%), no milk records (warning, 0 in 2h business), external down (warning, /ready unavailable >5min)
- **PII redaction rules**: Never log full Aadhaar (12-digit), mask phone (****XXXXXX), never log JWT/OTP/passwords
- **Artifacts**: `reports/latest/observability-engineer.md`, `reports/history/YYYY-MM-DD-observability-engineer.md`
- **Baselines**: Previous report diff only

### OPERATIONS PHASE

#### devops-engineer
- **Role**: Docker, CI/CD, monitoring, health checks, infrastructure
- **Docker services**: PostgreSQL 16 (5432), FastAPI API (8000), Mock Backends (8001)
- **CI pipeline**: 3 jobs — api-lint-test (Python 3.12, ruff, pytest), admin-build (Node 20, pnpm, next build), docker-build (API image)
- **Enhancement opportunities**: mobile build, collection build, security scanning, Lighthouse CI, migration testing, E2E with Docker
- **Required env vars**: DATABASE_URL, JWT_SECRET, CORS_ORIGINS, WEATHER_API_URL, IOT_GATEWAY_URL, BHARAT_PASHUDHAN_API_URL, STORAGE_API_URL, ENVIRONMENT, SARVAM_API_KEY
- **Incident response**: 7-step checklist (identify, logs, health, dependencies, restart, verify, root cause)
- **WSL2 notes**: NTFS slow for node_modules, auto-forwards Docker ports, Next.js first load 2-4s, Expo web needs static export
- **Artifacts**: None (operational fixes, not reports)
- **Baselines**: None

#### release-manager
- **Role**: Release planning, version management, go/no-go, deployment
- **Sprint deadline**: April 27, 2026
- **7 release components**: API (docker build), Admin (next build), Collection (vite build), Vet (vite build), Mobile (expo export), Mocks (docker build), Database (alembic upgrade head)
- **Pre-release checklist (6 sections)**: Code quality gates (ruff, pytest, next build, vite build, docker build), Security (pip-audit, npm audit, no secrets), Migration safety (at head, no DROP/destructive), Functional (9 demo scenarios), Performance (health <100ms, FCP <2s, API <500ms), Environment (all healthy, env vars match)
- **7 risks**: DB migration failure (Low/Critical), Docker build failure (Low/High), API regression (Medium/High), frontend build error (Low/Medium), performance degradation (Medium/Medium), security vulnerability (Low/Critical), data loss (Very Low/Critical)
- **Rollback**: Stop containers, restore previous images, alembic downgrade -1, verify health
- **Artifacts**: `reports/latest/release-manager.md`, `reports/history/YYYY-MM-DD-release-manager.md`
- **Baselines**: Previous report diff only

#### technical-writer
- **Role**: API docs, user guides, architecture, README, onboarding
- **15 existing docs**: README, architecture.md, compliance.md, data-flow.md, testing guides, audit reports, vision doc, env template, Swagger
- **7 identified gaps**: API Reference (static, all 25 endpoints), Developer Setup Guide, Mobile User Guide (multilingual), Admin Manual, Deployment Guide, Data Dictionary, Change Log
- **4 audience profiles**: Developers (high tech, English, code-heavy), Farmers (low digital, Kannada/Hindi, visual step-by-step), District admins (medium tech, task-oriented), Vets (medium tech, clinical terminology OK)
- **Artifacts**: Documentation in `docs/` directory (no reports/ output)
- **Baselines**: None

### DOMAIN EXPERTISE

#### agritech-domain-expert
- **Role**: ICAR/NDDB standards, dairy science, govt schemes, rural context
- **Indian dairy structure**: Farmer -> Village Centre -> District Union -> State Federation -> Market, ~80M farmers (1-5 animals), KMF context
- **Milk quality**: FAT% 3.0-8.0 (premium >4.5), SNF% 8.0-9.5 (premium >8.5), temp <10C (<5C premium)
- **5 species groups**: Cattle (Amrit Mahal, Hallikar, Khillari, Malnad Gidda), Buffalo (Murrah, Surti, Pandharpuri), Goat (Osmanabadi, Beetal, Jamunapari), Sheep (Deccani, Bannur), Poultry (Giriraja, Vanaraja)
- **7 critical diseases**: FMD, HS, BQ (Emergency), Brucellosis, Mastitis (High), PPR (Emergency, goat/sheep), Ranikhet (Emergency, poultry)
- **6 government schemes**: PM-KISAN, LISS, PM-KMY, NLM, RKVY, Bharat Pashudhan
- **7 ethnoveterinary remedies**: Bloat (mustard oil+garlic+asafoetida), wounds (turmeric+neem), diarrhea (pomegranate bark), mastitis (neem water), ticks (neem+coconut oil)
- **SHG structure**: Women-led, 10-20 members, Panchsutra 5 principles, ABCD grading, NABARD/NRLM linked
- **6 tech adoption barriers**: Low literacy -> voice/icons/Kannada, poor connectivity -> offline-first, small screens -> progressive disclosure, cost sensitivity -> free tier, trust -> local language/leaders, power -> lightweight app
- **Artifacts**: None (domain validation findings inline)
- **Baselines**: None

### ORCHESTRATION

#### pipeline-orchestrator
- **Role**: Master conductor — routes changes to agents, staged execution, scorecard
- **3 modes**: REQUIREMENT (design+implement+verify), CHANGE (detect->route->stages 3-8), RELEASE (all 34 agents)
- **Impact map**: 19 file patterns x 18 agents activation matrix ([P]=always, [O]=conditional, [-]=skip)
- **8 stages**: Stage 0-2 REQUIREMENT only (understand, design, implement), Stage 3 Fast Checks (<30s, code-reviewer + security-analyst + contract-tester), Stage 4 Build & Lint (<2min, ruff + next build + vite build), Stage 5 Functional Tests (<5min, unit + integration + browser + api + e2e), Stage 6 Quality (<5min, a11y + visual-regression + i18n + performance + data-integrity, WARN only), Stage 7 Security (security-tester + compliance-auditor, BLOCK on critical), Stage 8 Release Gate (release-manager + nfr-validator)
- **Verdicts**: PASS (all stages pass), WARN (quality non-critical), BLOCKED (any critical in security/compliance/functional)
- **Priority order**: Security > Compliance > Accessibility > Functional > Quality > Style
- **Deduplication**: Same file+line -> keep higher severity
- **Conflict resolution**: Security wins over performance, accessibility wins over design, ship if functional (log tech debt), visual changes need human approval
- **Artifacts**: `reports/latest/scorecard.md`, `reports/history/YYYY-MM-DD-scorecard.md`
- **Baselines**: Reads ALL `reports/baselines/*.json`

---

## 3. Slash Commands

| Command | File | Mode | Stages | Purpose |
|---------|------|------|--------|---------|
| `/pipeline` | `commands/pipeline.md` | Auto-detect / REQUIREMENT / CHANGE / RELEASE | 0-8 | Full orchestrator |
| `/verify` | `commands/verify.md` | CHANGE (lightweight) | 3-5 only | Quick check |
| `/review` | `commands/review.md` | File-focused | Parallel agents | Multi-perspective code review |

`/review` dispatches up to 9 agents in parallel based on file type:
- Always: code-reviewer, security-analyst, accessibility-tester (if UI)
- API: + contract-tester, api-tester
- Mobile: + i18n-tester, network-resilience-tester
- UI/frontend: + rural-ux-reviewer
- PII/auth: + compliance-auditor

---

## 4. Baseline Status (8 files)

| Baseline | File | Status | Key Data |
|----------|------|--------|----------|
| Performance | `baselines/performance.json` | **NOT MEASURED** | Targets defined: API P95 <200ms, Admin FLP <3000ms, Lighthouse perf >70 |
| Security | `baselines/security.json` | **PARTIAL** | OWASP: 5 mitigated, 4 partial, 1 unknown. 0 open vulns. No pen test done |
| Accessibility | `baselines/accessibility.json` | **NOT MEASURED** | WCAG 2.1 AA target. Known: StatCard contrast, map marker alt text |
| Coverage | `baselines/coverage.json` | **PARTIAL** | API: 5 test files, no coverage %. Admin: 4 test files + 1 Playwright. Mobile/Collection/Vet: 0 tests |
| Load | `baselines/load.json` | **NOT MEASURED** | Targets: baseline P95 <200ms, stress error <1%, spike recovery <30s, 100 concurrent |
| i18n | `baselines/i18n.json` | **MEASURED** | 186 keys, en/kn/hi 100% complete, gu/ta/te 100% keys but machine-generated stubs |
| NFR Scorecard | `baselines/nfr-scorecard.json` | **NOT ASSESSED** | 10 categories, all null scores. Verdict: NOT_ASSESSED |
| Compliance | `baselines/compliance.json` | **PARTIAL** | DPDP partial (consent/portability/breach missing), Aadhaar partial (not stored), IT Act partial (DB encryption at rest pending) |

**Summary**: Only i18n has actual measurements. Security and compliance have qualitative assessments. Performance, accessibility, load, and NFR are entirely unmeasured.

---

## 5. Workspace Audit Findings Summary

From `reports/latest/workspace-audit-2026.md` — **Last verified**: 2026-04-15

| Severity | Total | Fixed | Open | Key Remaining |
|----------|-------|-------|------|---------------|
| CRITICAL | 18 | **18** | **0** | All resolved |
| HIGH | 38 | **38** | **0** | All resolved |
| MEDIUM | 46 | **42** | **4** | 4 deferred (circuit breaker, offline queue, crash reporting, netinfo) |
| LOW | 37 | **31** | **6** | 6 deferred (React 19, login dedup, expo-updates, rn-screens, mock versioning, k6) |
| **Total** | **139** | **129** | **10** | |

> **Correction**: The original audit contained significant stale data — 10+ CRITICAL and 10+ HIGH
> findings were already fixed before the audit was written. Systematic source-level verification
> corrected the record across two fix sessions.

### All 18 CRITICAL fixes completed:
SEC-01 (auth guards), SEC-02 (.env gitignore), SEC-03 (sessionStorage), SEC-04 (CSP env vars),
SEC-05 (ILIKE escaping), SEC-06 (pure ASGI middleware), DATA-01 (soft delete),
DATA-02 (deleted_at filtering), DATA-03 (VetConsultation mixin), DATA-04 (FK ON DELETE RESTRICT migration),
DATA-05 (Decimal for money), DB-01 (migration chain clean), DB-02 (TTL cache),
MOB-01 (already had api.post), MOB-02 (already had api.post), MOB-05 (fetch timeout)

### 31 of 38 HIGH fixes completed:
PERF-01 (asyncio.gather IoT), PERF-02 (lazy="noload"), PERF-03 (SQL aggregation finance),
PERF-04 (SQL-bounded income), PERF-05 (SQL aggregation milk), PERF-06 (asyncio.gather admin),
PERF-07 (shared httpx.AsyncClient), PERF-08 (tenacity retry), PERF-09 (module-scope recharts),
PERF-10 (server-side pagination), SEC-07 (slowapi rate limiting), SEC-09 (file upload validation),
SEC-10 (127.0.0.1 binding), SEC-12 (cache invalidation on role change), SEC-13 (URL filtering),
SEC-14 (salted Aadhaar hash), DATA-06 (yield_logs unique constraint), DATA-07 (buffalo rules),
DATA-08 (IoT params), DATA-09 (response envelopes), DATA-10 (TimestampMixin + updated_at migration),
DATA-11 (valid dates), DATA-12 (31 Karnataka districts), MOB-03 (catch block fixed),
MOB-04 (confirmation dialog), SVC-01 (storage size limit), SVC-02 (configurable base_url),
SVC-03 (environment-gated OTP logging), TEST-04 (migration chain), FE-02 (no double prefix),
FE-04 (print.css exists)

### All 38 HIGH items resolved — final 7 fixed in session 3:
SEC-08 (RefreshToken model + migration, 30min access/7d refresh, rotation, reuse detection),
SEC-11 (HMAC-signed CSRF tokens bound to user_id + issued_at),
TEST-01 (43 auth router pytest tests), TEST-02 (33 CSRF middleware pytest tests),
TEST-03 (93 mobile Jest/RTL tests across 8 files),
FE-01 (15 loading.tsx + 14 layout.tsx server components, metadata API),
FE-03 (server-side sorting via Refine sorters in 5 admin pages)

---

## 6. Agent Validation Warnings

From `reports/latest/agent-validation.json`:
- All 34 agents passed structural validation
- **Index warnings**: AGENTS.md references 'pipeline', 'review', 'verify' — these are slash commands, not agent files (benign)
- **Impact map warnings**: References 'browser-ui', 'data-integrity', 'visual-regression' with no matching agent file — these are abbreviated names vs full filenames (browser-ui-tester.md, data-integrity-tester.md, visual-regression-tester.md)

---

## 7. Artifact Output Map

| Agent | Writes Latest Report | Writes History | Writes Baseline | Reads Baseline |
|-------|---------------------|----------------|-----------------|----------------|
| pipeline-orchestrator | scorecard.md | YES | NO | ALL baselines |
| business-analyst | YES | YES | NO | previous report |
| code-reviewer | YES | YES | NO | previous report |
| qa-lead | YES | YES | NO | coverage.json |
| unit-tester | YES | YES | NO | coverage.json |
| integration-tester | YES | YES | NO | previous report |
| e2e-tester | YES | YES | NO | previous report |
| api-tester | YES | YES | NO | previous report |
| browser-ui-tester | YES | YES | NO | previous report |
| contract-tester | YES | YES | NO | openapi-baseline.json |
| i18n-tester | YES | YES | NO | i18n.json |
| performance-tester | YES | YES | NO | performance.json |
| load-tester | YES | YES | NO | load.json |
| accessibility-tester | YES | YES | NO | accessibility.json |
| visual-regression-tester | YES | YES | screenshots | screenshots |
| chaos-tester | YES | YES | NO | previous report |
| network-resilience-tester | YES | YES | NO | previous report |
| rural-ux-reviewer | YES | YES | NO | previous report |
| data-integrity-tester | YES | YES | NO | previous report |
| security-analyst | YES | YES | NO | security.json |
| security-tester | YES | YES | NO | security.json |
| compliance-auditor | YES | YES | NO | compliance.json |
| nfr-validator | YES | YES | NO | nfr-scorecard.json |
| observability-engineer | YES | YES | NO | previous report |
| release-manager | YES | YES | NO | previous report |
| ux-designer | NO | NO | NO | NO |
| software-architect | NO | NO | NO | NO |
| backend-developer | NO | NO | NO | NO |
| frontend-developer | NO | NO | NO | NO |
| mobile-developer | NO | NO | NO | NO |
| database-admin | NO | NO | NO | NO |
| devops-engineer | NO | NO | NO | NO |
| technical-writer | NO (writes docs/) | NO | NO | NO |
| agritech-domain-expert | NO | NO | NO | NO |

**25 agents write reports**, **10 agents do not** (design, dev, domain, infra agents produce code/config/ADRs, not reports).

---

## 8. Pipeline Execution Flow

```
REQUIREMENT MODE:
  Stage 0: business-analyst + agritech-domain-expert (sequential)
  Stage 1: software-architect + ux-designer (parallel)
  Stage 2: backend-dev + frontend-dev/mobile-dev + database-admin (parallel)
  -> then falls into CHANGE pipeline stages 3-8

CHANGE MODE:
  git diff -> impact map routing -> agent selection
  Stage 3: Fast Checks (code-reviewer, security-analyst, contract-tester) [<30s, BLOCK on fail]
  Stage 4: Build & Lint (ruff, next build, vite build) [<2min, BLOCK on fail]
  Stage 5: Functional Tests (unit, integration, browser, api, e2e) [<5min, BLOCK on fail]
  Stage 6: Quality (a11y, visual-regression, i18n, performance, data-integrity) [<5min, WARN only]
  Stage 7: Security (security-tester, compliance-auditor) [BLOCK on critical]
  Stage 8: Release Gate (release-manager, nfr-validator) [final verdict]

RELEASE MODE:
  All 34 agents, includes load-tester (soak), chaos-tester (faults), nfr-validator (full scorecard)
```

---

## 9. Known Issues & Gaps (Updated 2026-04-15)

### Agent-Level Gaps
1. **Impact map abbreviations**: 'browser-ui', 'data-integrity', 'visual-regression' don't match filenames — could cause routing misses
2. **No artifact for 10 agents**: Design/dev/domain agents produce no structured reports — their work is only visible in code changes
3. **6 of 8 baselines unmeasured**: Only i18n has actual data; everything else is null/targets-only

### Testing Gaps
4. **Mobile**: 0 test files — primary farmer interface has zero coverage
5. **Collection/Vet**: 0 test files each
6. **Auth router**: 0 tests — OTP/JWT critical path untested
7. **CSRF middleware**: 0 tests
8. **Browser UI**: Collection (3001) and Vet (3002) have 0 Playwright tests

### Infrastructure Gaps
9. **No CI for**: mobile build, collection build, security scanning, Lighthouse, migration testing, E2E
10. **No observability**: No Prometheus metrics, no distributed tracing, no error tracking, no APM, no alerts, no dashboards
11. **No offline support**: Mobile has no NetInfo, no offline queue, no background sync, no local cache
12. **No PWA offline data**: Collection centre service worker not configured for offline data

### Workspace Audit — ALL CRITICAL RESOLVED (18 of 18)
13. ~~8+ endpoints without auth (SEC-01)~~ FIXED — all endpoints have auth
14. ~~Animal hard delete (DATA-01)~~ FIXED — uses soft delete
15. ~~Soft-delete filtering on ALL queries (DATA-02)~~ FIXED — all queries filter deleted_at
16. ~~Migration chain (DB-01)~~ FIXED — chain verified clean, no duplicates
17. ~~Mobile onboarding data (MOB-01, MOB-02)~~ FIXED — already had api.post calls (audit was stale)
18. ~~Vaccination catch block (MOB-03)~~ FIXED + reclassified to HIGH
19. ~~Auth token localStorage (SEC-03)~~ FIXED — changed to sessionStorage
20. ~~FK ON DELETE (DATA-04)~~ FIXED — migration d4e5f6a7b8c9 adds ON DELETE RESTRICT

### No HIGH items remaining — all 38 resolved
