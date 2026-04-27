# Phase 3: Performance & NFR Testing — Prompt for Claude Code

> **Context**: Phase 1 (Backend API) and Phase 2 (Browser UI) are complete.
> Read `pashu-erp/testing-handover-phase2.md` for Phase 2 results.
> Read `pashu-erp/testing-handover-phase1.md` for Phase 1 results.
>
> **How to use**: Clear context, then paste everything below the line into Claude Code.
> **Working directory**: `/home/sdamera/workbench/Social-Impact-Sprint`

---

## PROMPT START

Read `pashu-erp/testing-handover-phase1.md` and `pashu-erp/testing-handover-phase2.md` first.

You are doing Phase 3: Performance and Non-Functional Requirements testing for PashuRaksha ERP.

### CRITICAL RULES

1. **MEASURE, DON'T GUESS**: Every metric must come from an actual measurement. No "estimated" response times.
2. **CONTEXT HANDOVER**: Write state to `pashu-erp/testing-handover-phase3.md` before context fills up.
3. **ASK IF BLOCKED**: If k6 isn't installed, if Docker stats aren't available, ask me.

### PART A: API Response Time Profiling

Write a Python script that authenticates (extract OTP from docker logs — OTP is randomly generated, NOT "123456") and measures response time for EVERY endpoint. Use the comprehensive test conftest.py pattern for auth.

For each endpoint, capture:
- HTTP method + path
- Response status code
- Response time (ms)
- Response body size (bytes)

Color-code results:
- GREEN: < 200ms
- YELLOW: 200-500ms
- RED: > 500ms

Output a sorted table of all ~93 endpoints.

### PART B: Load Testing with k6

k6 scripts already exist:
- `pashu-erp/e2e/load/baseline.js` — read-path baseline + stress + spike
- `pashu-erp/packages/api/tests/load/k6-write-paths.js` — write-path load test

```bash
# Install k6 if needed
which k6 || (sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D68 && echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list && sudo apt-get update && sudo apt-get install k6 -y)

# Run baseline (10 VUs, 30s + stress ramp + spike)
k6 run pashu-erp/e2e/load/baseline.js

# Run write-path load test
k6 run pashu-erp/packages/api/tests/load/k6-write-paths.js
```

If k6 can't be installed, use `hey` or write a Python concurrent load test with `asyncio` + `httpx`.

Auth for k6: The k6 config at `tests/load/k6-config.js` has auth helpers — but they may use hardcoded OTP "123456" which is WRONG. Fix to use a pre-obtained token instead.

### PART C: Frontend Bundle Sizes

```bash
# Admin (Next.js)
cd pashu-erp/packages/admin
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
ANALYZE=true npx next build 2>&1 | tail -30

# Collection (Vite)
cd pashu-erp/packages/collection && npx vite build 2>&1 | tail -20

# Vet (Vite)
cd pashu-erp/packages/vet && npx vite build 2>&1 | tail -20
```

### PART D: Database Performance Audit

```bash
# Indexes
docker exec pashu-erp-db-1 psql -U pashu -d pashuraksha -c "SELECT schemaname, tablename, indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;"

# Table sizes
docker exec pashu-erp-db-1 psql -U pashu -d pashuraksha -c "SELECT relname, n_live_tup, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_stat_user_tables ORDER BY n_live_tup DESC;"

# Slow queries (if pg_stat_statements available)
docker exec pashu-erp-db-1 psql -U pashu -d pashuraksha -c "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 20;" 2>&1
```

### PART E: NFR Scorecard

Use the `nfr-validator` agent to produce a scorecard:

| Requirement | Target | Status |
|-------------|--------|--------|
| API P95 latency | < 500ms | PASS/FAIL |
| API P99 latency | < 1000ms | PASS/FAIL |
| Error rate under load (50 VUs) | < 1% | PASS/FAIL |
| Admin FCP | < 2s | PASS/FAIL |
| Admin LCP | < 3s | PASS/FAIL |
| Admin JS bundle | < 500KB gzipped | PASS/FAIL |
| Collection JS bundle | < 300KB gzipped | PASS/FAIL |
| DB pool saturation at 100 VUs | No exhaustion | PASS/FAIL |
| Health endpoint | < 50ms | PASS/FAIL |
| Concurrent users without degradation | 100+ | PASS/FAIL |

### AGENTS TO USE

| Agent | Purpose |
|-------|---------|
| `performance-tester` | Response times, bundle sizes, Lighthouse |
| `load-tester` | k6 load/stress/spike tests |
| `nfr-validator` | Non-functional requirements scorecard |

### OUTPUT

Write results to `pashu-erp/testing-handover-phase3.md` with:
- API response time table (all endpoints, sorted by time)
- Top 10 slowest endpoints with analysis
- k6 load test summary
- Bundle size report
- Database audit results
- NFR scorecard with PASS/FAIL

After Phase 3, create the final consolidated report: `pashu-erp/reports/comprehensive-test-report.md` combining Phase 1 + 2 + 3 results. Use the `qa-lead` agent for the go/no-go verdict.

## PROMPT END
