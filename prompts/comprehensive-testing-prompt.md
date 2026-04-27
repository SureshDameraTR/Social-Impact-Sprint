# Comprehensive Testing Prompt for PashuRaksha ERP

> **How to use**: Copy everything below the line and paste it into Claude Code as a single prompt.
> The prompt is self-contained — it references real files, real endpoints, and real agents in this repo.
> Execute from the repo root: `/home/sdamera/workbench/Social-Impact-Sprint`

---

## PROMPT START

You are tasked with comprehensive, end-to-end testing of the PashuRaksha ERP application. This is a livestock management platform running in Docker on WSL. Your job is to verify every layer works correctly — backend APIs, browser UIs, performance, and non-functional requirements.

### CRITICAL RULES (READ BEFORE DOING ANYTHING)

1. **NO HALLUCINATIONS**: Never claim a test passed without actually running it and seeing the output. If a test fails, report the failure honestly. If you can't run something, say so — don't pretend.
2. **NO HALF-TESTING**: Every API endpoint gets 10-12 test cases minimum (positive AND negative). Every UI page gets real browser interaction. No "I tested the login and the rest should work similarly."
3. **DOUBLE VERIFY**: After writing tests, run them. After they pass, run them again. Check the actual HTTP responses and browser screenshots. Don't trust existing docs — verify against the running application.
4. **CONTEXT HANDOVER**: Before your context fills up, create a handover file at `pashu-erp/testing-handover-<phase>.md` with: what's done, what's remaining, exact commands to continue, and any issues found. Then tell me to start a new session with "Continue testing from pashu-erp/testing-handover-<phase>.md".
5. **ASK, DON'T ASSUME**: If Docker isn't running, if a port isn't responding, if Chrome isn't available — ASK ME. Don't skip it or fake it.
6. **REAL BROWSER ONLY FOR UI**: Use Playwright in headed mode (`--headed`) or Chrome CDP. Headless tests miss real rendering issues. If headed mode doesn't work in WSL, tell me and we'll configure it.

---

### PHASE 0: ENVIRONMENT VERIFICATION (Do This First)

Before ANY testing, verify the entire stack is running:

```bash
# 1. Check Docker containers
docker compose ps
# Expected: db, api, mock-backends all "healthy"

# 2. Check API health
curl -s http://localhost:8000/health | jq .
# Expected: {"status": "healthy"}

# 3. Check mock backends
curl -s http://localhost:8001/health | jq .

# 4. Check database connectivity
docker exec pashu-erp-db-1 pg_isready -U postgres

# 5. Test auth flow works (this proves the full stack is connected)
curl -s -X POST http://localhost:8000/v1/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919900000001"}' | jq .
# Then verify OTP
curl -s -X POST http://localhost:8000/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919900000001", "otp": "123456", "client_type": "web"}' | jq .
# Expected: JWT token in response

# 6. Check frontend ports (if testing UI)
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000  # Admin
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001  # Collection
curl -s -o /dev/null -w "%{http_code}" http://localhost:3002  # Vet
```

**If ANY of these fail, STOP and tell me.** Do not proceed with broken infrastructure.

If frontends aren't running, start them:
```bash
cd pashu-erp && docker compose --profile frontend up -d
```

---

### PHASE 1: BACKEND API TESTING (Most Critical)

**Goal**: Test every API endpoint with 10-12 test cases each. This tests the application-to-database layer.

**Approach**: Write pytest integration tests that hit the REAL running API (localhost:8000) with a REAL database. Not mocked tests — real HTTP calls, real database state.

**Test file location**: `pashu-erp/packages/api/tests/comprehensive/`

**Auth setup for tests**: Every test file needs a helper that:
1. Calls `POST /v1/auth/request-otp` with the appropriate test phone
2. Reads the REAL OTP from docker logs: `docker logs pashu-erp-api-1 --tail 10 2>&1 | grep "Code:" | tail -1 | grep -oP '\d{6}'`
3. Calls `POST /v1/auth/verify-otp` with the extracted OTP (NOT "123456" — the OTP is randomly generated via `secrets.randbelow`)
4. Extracts the bearer token for subsequent requests

**WARNING**: The WORKSPACE.md claims dev OTP is "123456" — THIS IS WRONG. The actual code in `auth.py:64` generates random OTPs. The console provider prints them to stderr. You MUST read from docker logs.

**Test accounts** (from seed data):
| Role | Phone | Name |
|------|-------|------|
| admin | +919900000001 | Deepak Kumar |
| farmer | +919900000002 | Lakshmi Devi |
| vet | +919900000005 | Dr. Ramesh |

**For EACH of the 29 routers below, write a test file with 10-12 test cases covering:**

Positive cases (at least 5-6):
- Happy path with valid data
- List endpoint returns correct envelope `{data: [], total: int}`
- Create → Read → verify data matches
- Update → Read → verify changes persisted
- Filter/search with valid parameters
- Pagination (page 1 vs page 2 don't overlap)

Negative cases (at least 5-6):
- 401 Unauthorized (no token)
- 403 Forbidden (wrong role — e.g., farmer can't access admin endpoints)
- 404 Not Found (non-existent UUID)
- 422 Validation Error (missing required fields)
- 422 Validation Error (wrong data types)
- Duplicate/conflict scenarios where applicable
- Boundary values (empty strings, very long strings, negative numbers)

**THE 29 ROUTERS TO TEST:**

| # | Router | Prefix | Key Endpoints | Auth |
|---|--------|--------|---------------|------|
| 1 | auth | /v1/auth | request-otp, verify-otp, refresh, me, logout | None/Any |
| 2 | animals | /v1/animals | CRUD (POST, GET list, GET by id, PATCH, DELETE) | farmer/vet/admin |
| 3 | health | /v1/health | POST log, GET history, GET list, GET alerts/map | farmer/vet |
| 4 | milk | /v1/milk | GET list, GET today, GET history, POST yield, GET daily-summary | farmer |
| 5 | milk_center | /v1/milk-center | GET my-center, POST receive, GET daily-report, GET settlements, POST enroll | milk_center |
| 6 | finance | /v1/finance | POST transaction, GET summary | farmer |
| 7 | shg | /v1/shg | CRUD groups + compliance check | farmer/admin |
| 8 | schemes | /v1/schemes | GET list, GET by id, POST create | farmer/admin |
| 9 | marketplace | /v1/marketplace | GET list, POST sell, GET history, GET rates, GET summary | farmer |
| 10 | income | /v1/income | GET summary, GET breakdown, GET history, GET transactions | farmer/admin |
| 11 | admin | /v1/admin | GET stats, GET charts/milk, GET gis/alerts, PATCH users role | admin |
| 12 | weather | /v1/weather | GET forecast, GET alerts, GET tts | farmer |
| 13 | feed | /v1/feed | GET ingredients, POST calculate-ration | farmer/vet |
| 14 | ethno_vet | /v1/ethno-vet | GET remedies, GET by id, GET search | farmer |
| 15 | bharat_pashudhan | /v1/registry | GET lookup, POST sync | admin |
| 16 | vaccination | /v1/vaccinations | POST create, GET due, GET schedule, GET coverage, PATCH | farmer/vet/admin |
| 17 | insurance | /v1/insurance | GET policies, POST claims, GET premium-estimate | farmer |
| 18 | alerts | /v1/alerts | POST report, GET nearby, PATCH verify | farmer/vet |
| 19 | medicine | /v1/medicines | GET catalog, POST administer, GET withdrawal-status | vet |
| 20 | medicine_log | /v1/medicine-log | GET withdrawals | farmer/vet |
| 21 | advisory | /v1/advisory | GET tips, GET tip by id | farmer |
| 22 | onboarding | /v1/onboarding | POST complete | farmer |
| 23 | iot | /v1/iot | GET devices, GET device-types, GET readings, GET device by id | farmer/admin |
| 24 | map_points | /v1/map | GET points | any |
| 25 | users | /v1/users | GET farmers, GET profile | admin |
| 26 | reference | /v1/reference | GET market-rates, PUT rates, GET premiums, PUT premiums, GET medicines | any/admin |
| 27 | files | /v1/files | POST upload, GET by id, GET list | any |
| 28 | vet | /v1/vet | GET cases, GET case by id, PATCH claim/diagnose/close, GET dashboard | vet |
| 29 | consent | /v1/consent | POST grant, POST withdraw, GET my, DELETE erasure | any |

**Execution approach**: 
- Use the `api-tester` agent for writing and running these tests
- Also use the `integration-tester` agent for cross-router workflow tests
- Write a shared `conftest.py` in the comprehensive test directory with auth helpers
- Run with: `cd pashu-erp/packages/api && uv run pytest tests/comprehensive/ -v --tb=long 2>&1 | tail -100`

**Database seeding**: Before running tests, ensure seed data exists. If the database is empty:
```bash
cd pashu-erp && docker compose exec api python -m app.seed  # or check how seeding works
```
If no seed command exists, the test conftest should create necessary data via API calls (register user, create animal, etc.) as part of test setup.

**OUTPUT REQUIRED**: For each router, report:
- Total tests: X passed, Y failed, Z skipped
- Response times for each endpoint (measure with time)
- Any unexpected behavior or bugs found
- Screenshot of terminal showing test results

---

### PHASE 2: BROWSER UI TESTING (User Acceptance)

**Goal**: Log into each of the 3 web applications as a real user would, test every page, every navigation, every form, every CRUD operation.

**Approach**: Use Playwright in headed mode for real browser testing. Write test specs in `pashu-erp/e2e/comprehensive/`.

**Browser setup for WSL**:
```bash
# Option A: Playwright headed (if WSLg is working)
cd pashu-erp && npx playwright test --headed --project=admin

# Option B: If headed doesn't work, use the playwriter skill for Chrome CDP
# Or launch Chrome on Windows with: chrome.exe --remote-debugging-port=9222
# Then connect from WSL via CDP scripts
```

**If neither option works, ASK ME for help. Do not fall back to headless and pretend it's real browser testing.**

#### 2A. ADMIN DASHBOARD (localhost:3000) — 16 pages

Test as admin user (phone: +919900000001, OTP: 123456):

| Page | Route | What to Test |
|------|-------|-------------|
| Login | /login | Enter phone, submit, enter OTP, verify redirect to dashboard |
| Dashboard | / | Stat cards render with numbers (not 0 or NaN), chart renders, GIS map loads with markers |
| Farmers | /farmers | Table loads with data, search filters work, pagination works, click a farmer row |
| Animals | /animals | Table loads, species filter dropdown works, RiskBadge chips show correct colors |
| Health | /health | Risk level filter works, health events list loads |
| Milk | /milk | Collection data renders, daily summary visible |
| Vaccinations | /vaccinations | Coverage stats render, progress bars show percentages |
| Schemes | /schemes | Government schemes list loads |
| Marketplace | /marketplace | Listings render |
| Income | /income | Income analytics charts render |
| Map | /map | Full-page Leaflet map loads, markers visible, legend renders |
| IoT | /iot | Device list loads, status indicators show |
| Vet Dashboard | /vet | Vet overview stats render |
| Vet Cases | /vet/cases | Case list loads, can click into a case |
| Vet Case Detail | /vet/cases/:id | Case details render, action buttons present |
| Vet Alerts | /vet/alerts | Alert list renders |

**For EACH page, verify:**
- Page loads without console errors (check browser console)
- No "loading..." spinners stuck forever
- No blank white screens
- Data tables have actual data (not empty states when data should exist)
- Navigation sidebar works (click each link, verify URL changes)
- Responsive: test at 1920px, 1366px, 1024px, 768px widths
- Fonts render correctly (no missing characters, especially for Kannada text)
- No overlapping elements or broken layouts
- Take a screenshot of each page for evidence

#### 2B. COLLECTION CENTRE (localhost:3001) — 6 pages

Test as milk_center user (need to verify which phone number):

| Page | Route | What to Test |
|------|-------|-------------|
| Login | /login | Phone + OTP flow |
| Dashboard | /dashboard | Daily intake summary, shift stats |
| Intake | /intake | Search farmer, enter milk qty/FAT/SNF, rate preview calculates, submit |
| Receipt | /intake/receipt/:id | Receipt renders after intake submission, printable layout |
| Enroll | /enroll | Quick farmer enrollment form, submit, verify created |
| Settlements | /settlements | Farmer payment settlement list |

**Critical test for Collection**: The Intake workflow is the core business flow:
1. Login → Dashboard
2. Navigate to Intake
3. Search for a farmer by name
4. Enter milk quantity (e.g., 5.5 liters)
5. Enter FAT (e.g., 4.2) and SNF (e.g., 8.5) values
6. Verify rate preview shows calculated price
7. Submit the intake
8. Verify redirected to receipt page
9. Verify receipt shows correct data

#### 2C. VET DASHBOARD (localhost:3002) — 5 pages

Test as vet user (phone: +919900000005, OTP: 123456):

| Page | Route | What to Test |
|------|-------|-------------|
| Login | /login | Phone + OTP flow |
| Dashboard | /dashboard | Welcome message, stats, pending cases count |
| Cases | /cases | Case list loads, "All Cases" and "My Cases" tabs work |
| Case Detail | /cases/:id | Case info renders, claim/diagnose/close buttons visible |
| Alerts | /alerts | Nearby disease alerts list, map markers if applicable |

**Critical test for Vet**: The case workflow:
1. Login → Dashboard
2. Navigate to Cases
3. View a case
4. Claim the case (PATCH)
5. Add diagnosis
6. Close the case
7. Verify case status updated

**Execution**: Use the `browser-ui-tester` agent and the `e2e-tester` agent. Write Playwright specs.

**OUTPUT REQUIRED**: For each page:
- Screenshot (pass or fail)
- Console errors (if any)
- Load time
- Any visual bugs (overlapping, missing data, broken layout)
- Form submissions: actual API response status

---

### PHASE 3: PERFORMANCE & NFR TESTING

**Goal**: Measure how fast every API responds, identify slow queries, check frontend bundle sizes, and produce a non-functional requirements scorecard.

#### 3A. API Response Time Profiling

For every endpoint tested in Phase 1, capture:
- Response time (ms)
- Response size (bytes)
- Database query count (if observable from logs)

Group by performance tier:
- GREEN: < 200ms
- YELLOW: 200-500ms  
- RED: > 500ms

Report the top 10 slowest endpoints.

#### 3B. Load Testing

Run k6 tests against the running API:
```bash
# Read-path baseline
k6 run pashu-erp/e2e/load/baseline.js

# Write-path load test
k6 run pashu-erp/packages/api/tests/load/k6-write-paths.js
```

If k6 is not installed:
```bash
# Install k6 on WSL
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D68
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6
```

Or use `hey` for quick benchmarks:
```bash
# Install hey
go install github.com/rakyll/hey@latest
# Quick benchmark
hey -n 1000 -c 50 -H "Authorization: Bearer <token>" http://localhost:8000/v1/animals
```

#### 3C. Frontend Performance

For each frontend app, measure:
```bash
# Admin bundle size
cd pashu-erp/packages/admin
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
ANALYZE=true npx next build  # generates bundle analysis

# Collection bundle size
cd pashu-erp/packages/collection && npx vite build

# Vet bundle size  
cd pashu-erp/packages/vet && npx vite build

# Lighthouse scores (if Chrome available)
npx lighthouse http://localhost:3000 --output=json --output-path=./lighthouse-admin.json
npx lighthouse http://localhost:3001 --output=json --output-path=./lighthouse-collection.json
npx lighthouse http://localhost:3002 --output=json --output-path=./lighthouse-vet.json
```

#### 3D. Database Performance

```bash
# Check for missing indexes
docker exec pashu-erp-db-1 psql -U postgres -d pashuraksha -c "
SELECT schemaname, tablename, indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;
"

# Check table sizes
docker exec pashu-erp-db-1 psql -U postgres -d pashuraksha -c "
SELECT relname, n_live_tup, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_stat_user_tables ORDER BY n_live_tup DESC;
"

# Check for slow queries (if pg_stat_statements enabled)
docker exec pashu-erp-db-1 psql -U postgres -d pashuraksha -c "
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 20;
"
```

#### 3E. NFR Scorecard

Use the `nfr-validator` agent to produce a scorecard covering:

| Requirement | Target | How to Measure |
|-------------|--------|---------------|
| API P95 latency | < 500ms | k6 results |
| API P99 latency | < 1000ms | k6 results |
| Error rate under load | < 1% | k6 results |
| Admin FCP | < 2s | Lighthouse |
| Admin LCP | < 3s | Lighthouse |
| JS bundle (Admin) | < 500KB gzipped | next build output |
| JS bundle (Collection) | < 300KB gzipped | vite build output |
| DB connection pool | No exhaustion at 100 VUs | k6 + pg_stat_activity |
| Health endpoint | < 50ms | Direct measurement |
| Concurrent users | 100+ without degradation | k6 stress test |

**OUTPUT REQUIRED**: 
- Complete NFR scorecard with PASS/FAIL per metric
- API endpoint response time table (all 93 endpoints)
- Top 10 slowest endpoints with analysis
- k6 summary output
- Lighthouse scores for all 3 UIs
- Bundle size report

---

### PHASE 4: CONSOLIDATED REPORT

After all phases complete, produce a single report at `pashu-erp/reports/comprehensive-test-report.md`:

```markdown
# PashuRaksha ERP — Comprehensive Test Report
Date: YYYY-MM-DD

## Executive Summary
- Total tests run: X
- Pass rate: X%
- Critical bugs found: X
- Performance grade: A/B/C/D/F

## Phase 1: Backend API Testing
### Per-Router Results
| Router | Tests | Passed | Failed | Avg Response Time |
|--------|-------|--------|--------|-------------------|
(all 29 routers)

### Bugs Found
(list each bug with: endpoint, request, expected vs actual, severity)

## Phase 2: Browser UI Testing  
### Per-App Results
| App | Pages Tested | Pass | Fail | Console Errors |
|-----|-------------|------|------|----------------|

### Screenshots
(reference screenshot files)

### Visual/UX Issues
(list each issue with screenshot reference)

## Phase 3: Performance & NFR
### API Response Times
(table of all endpoints with response times, color-coded)

### Load Test Results
(k6 output summary)

### NFR Scorecard
(pass/fail table)

### Frontend Performance
(Lighthouse scores, bundle sizes)

## Recommendations
(prioritized list of fixes needed before production)
```

---

### AGENT USAGE GUIDE

Use these agents from `.claude/agents/` in this order:

| Phase | Agent | Purpose |
|-------|-------|---------|
| 0 | (manual) | Environment verification |
| 1 | `api-tester` | Write + run API test cases for all 29 routers |
| 1 | `integration-tester` | Cross-router workflow tests against real DB |
| 2 | `browser-ui-tester` | Playwright tests for all 3 web apps |
| 2 | `e2e-tester` | End-to-end user journey tests |
| 3 | `performance-tester` | Response time analysis, bundle sizes, Lighthouse |
| 3 | `load-tester` | k6 load/stress/spike tests |
| 3 | `nfr-validator` | Non-functional requirements scorecard |
| 4 | `qa-lead` | Consolidate results, go/no-go decision |

You can also use the `playwriter` skill for Chrome CDP browser control, and the `performance-testing` skill for k6/Locust guidance.

**Parallelization**: Phases 1 and 3A can run in parallel (API tests + response time measurement). Phase 2 requires Phase 0 frontends running. Phase 4 requires all others complete.

---

### CONTEXT MANAGEMENT

This is a large task. You WILL run out of context. Plan for it:

1. **After Phase 1 completes**: Write `pashu-erp/testing-handover-phase1.md` with results summary and remaining work
2. **After Phase 2 completes**: Write `pashu-erp/testing-handover-phase2.md`  
3. **After Phase 3 completes**: Write `pashu-erp/testing-handover-phase3.md`
4. **If context runs low MID-PHASE**: Immediately write a handover file with:
   - What's done (which routers/pages tested)
   - What's remaining (which routers/pages still need testing)
   - Any issues found so far
   - Exact command to resume
   - Then tell me: "Context is filling up. Continue with: Read pashu-erp/testing-handover-phaseX.md and resume"

**NEVER lose work by running out of context without saving state.**

---

### WHAT SUCCESS LOOKS LIKE

- [ ] All 29 API routers tested with 10-12 cases each (~300+ test cases)
- [ ] All 27 web pages tested in real browser with screenshots
- [ ] All critical user flows tested end-to-end (login, milk intake, vet case, admin dashboard)
- [ ] API response times measured for all 93 endpoints
- [ ] k6 load test completed (baseline + stress + spike)
- [ ] Lighthouse scores for all 3 UIs
- [ ] NFR scorecard with pass/fail per metric
- [ ] Consolidated report with zero hallucinated results
- [ ] Every "PASS" backed by actual test output, every "FAIL" with reproduction steps

## PROMPT END
