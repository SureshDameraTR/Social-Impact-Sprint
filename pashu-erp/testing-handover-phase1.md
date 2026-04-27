# Phase 1 Handover: Backend API Testing — COMPLETE

**Date**: 2026-04-20  
**Working directory**: `/home/sdamera/workbench/Social-Impact-Sprint/pashu-erp/packages/api`  
**Branch**: `main` (uncommitted changes)

---

## What Was Accomplished

Comprehensive backend API integration testing of ALL 29 routers in the PashuRaksha ERP application. Tests hit the **real running API at localhost:8000** with a **real PostgreSQL database** — no mocking.

**Final result**: `387 passed, 4 skipped, 0 failed` in 11.28 seconds.

---

## Files Created

### Test Infrastructure
| File | Purpose |
|------|---------|
| `tests/comprehensive/__init__.py` | Package marker |
| `tests/comprehensive/conftest.py` | Shared fixtures: auth helpers (OTP extraction from docker logs), session-scoped tokens for 4 roles (admin, farmer, farmer2, vet), rate-limit retry with 61s backoff, API reachability check |

### Test Files (29 files, 391 test functions)

| File | Router | Tests |
|------|--------|-------|
| `test_auth_comprehensive.py` | /v1/auth | 12 |
| `test_animals_comprehensive.py` | /v1/animals | 12 |
| `test_health_comprehensive.py` | /v1/health | 12 |
| `test_milk_comprehensive.py` | /v1/milk | 19 |
| `test_milk_center_comprehensive.py` | /v1/milk-center | 18 |
| `test_finance_comprehensive.py` | /v1/finance | 19 |
| `test_income_comprehensive.py` | /v1/income | 20 |
| `test_marketplace_comprehensive.py` | /v1/marketplace | 22 |
| `test_shg_comprehensive.py` | /v1/shg | 12 |
| `test_schemes_comprehensive.py` | /v1/schemes | 12 |
| `test_vet_comprehensive.py` | /v1/vet | 12 |
| `test_vaccination_comprehensive.py` | /v1/vaccinations | 12 |
| `test_medicine_comprehensive.py` | /v1/medicines | 12 |
| `test_medicine_log_comprehensive.py` | /v1/medicine-log | 10 |
| `test_alerts_comprehensive.py` | /v1/alerts | 12 |
| `test_weather_comprehensive.py` | /v1/weather | 13 |
| `test_iot_comprehensive.py` | /v1/iot | 13 |
| `test_registry_comprehensive.py` | /v1/registry | 11 |
| `test_insurance_comprehensive.py` | /v1/insurance | 12 |
| `test_feed_comprehensive.py` | /v1/feed | 14 |
| `test_ethno_vet_comprehensive.py` | /v1/ethno-vet | 14 |
| `test_advisory_comprehensive.py` | /v1/advisory | 14 |
| `test_admin_comprehensive.py` | /v1/admin | 12 |
| `test_users_comprehensive.py` | /v1/users | 12 |
| `test_reference_comprehensive.py` | /v1/reference | 12 |
| `test_files_comprehensive.py` | /v1/files | 12 |
| `test_map_points_comprehensive.py` | /v1/map | 12 |
| `test_onboarding_comprehensive.py` | /v1/onboarding | 12 |
| `test_consent_comprehensive.py` | /v1/consent | 12 |

### Other Files Created
| File | Purpose |
|------|---------|
| `prompts/comprehensive-testing-prompt.md` | Master prompt for all 4 testing phases |

---

## Application Bugs Found and Fixed

The fixer agent modified application source code to fix bugs discovered during testing. **46 app files were touched** (all routers, services, docker-compose, mocks). The critical bug fixes were:

| # | Sev | File | Bug | Fix Applied |
|---|-----|------|-----|-------------|
| 1 | CRITICAL | `routers/onboarding.py` | Detached SQLAlchemy instance — auth middleware cached User from session A, onboarding used session B → 500 on every call | Re-load user from current db session |
| 2 | CRITICAL | `routers/vet.py` | `my_cases()` returned raw ORM objects to typed `VetCaseRead` response_model → 500 serialization error | Used existing `_serialize_case()` helper |
| 3 | HIGH | `routers/alerts.py` | Haversine math crashed on PostgreSQL `Decimal` GPS coordinates — `math.radians(Decimal)` → TypeError | Cast to `float()` before calculation |
| 4 | HIGH | `services/feed_calculator.py` | `Decimal * float` TypeError in ration calculation | Cast `weight_kg` to `float()` |
| 5 | HIGH | `docker-compose.yml` | Mock service URLs had `/api/v1/` but mocks served at `/api/` → weather, IoT, registry, files ALL broken | Corrected URL prefixes |
| 6 | HIGH | DB schema | `market_rates`, `insurance_premiums`, `medicine_catalog` tables missing despite migration recorded | Created tables + seeded data |
| 7 | MEDIUM | `routers/schemes.py` | Non-deterministic pagination — ordered by `name` only, duplicates caused page overlap | Added secondary sort by `id` |

**IMPORTANT**: These app changes are **uncommitted** on the `main` branch. They need review before committing. The fixer agent's scope was broad — it modified all 29 routers and 13 services. Some changes may be bug fixes, others may be incidental. You should review with `git diff -- pashu-erp/packages/api/app/` before committing.

---

## Application State

### Docker containers running
```
pashu-erp-api-1          (healthy, port 8000)
pashu-erp-db-1           (healthy, port 5432)
pashu-erp-mock-backends-1 (healthy, port 8001)
```
Frontends are NOT running (need `--profile frontend`).

### Database seed data
9 users (1 admin, 6 farmers, 1 vet, 1 milk_center), 8 animals, 300 yield_logs, 24 tables with data.

### Auth mechanism
OTP is **randomly generated** (NOT fixed "123456" as docs claim). Must extract from docker logs:
```bash
docker logs pashu-erp-api-1 --tail 15 2>&1 | grep "Code:" | tail -1
```
Rate limits: 5/minute per IP (slowapi in-memory), 5/hour per phone (DB). Reset with:
```bash
docker exec pashu-erp-db-1 psql -U pashu -d pashuraksha -c "UPDATE otp_requests SET request_count = 0, attempts = 0;"
docker restart pashu-erp-api-1  # clears in-memory slowapi state
```

### Test run command
```bash
cd pashu-erp/packages/api
docker exec pashu-erp-db-1 psql -U pashu -d pashuraksha -c "UPDATE otp_requests SET request_count = 0, attempts = 0;"
uv run pytest tests/comprehensive/ -v --tb=short
```

---

## What Remains: Phases 2, 3, 4

### Phase 2: Browser UI Testing
- Start frontends: `cd pashu-erp && docker compose --profile frontend up -d`
- Install Playwright: `npx playwright install chromium`
- Test all 27 web pages across 3 apps (Admin:3000, Collection:3001, Vet:3002)
- Login flows, navigation, CRUD operations, responsive testing, screenshots
- Use `browser-ui-tester` and `e2e-tester` agents
- Full spec in `prompts/comprehensive-testing-prompt.md` → PHASE 2 section

### Phase 3: Performance & NFR Testing
- API response time profiling for all 93 endpoints
- k6 load tests (scripts exist at `e2e/load/baseline.js` and `tests/load/k6-write-paths.js`)
- Frontend bundle sizes and Lighthouse scores
- Database index audit, slow query analysis
- NFR scorecard (P95 < 500ms, FCP < 2s, etc.)
- Use `performance-tester`, `load-tester`, `nfr-validator` agents

### Phase 4: Consolidated Report
- Merge all results into `reports/comprehensive-test-report.md`
- Use `qa-lead` agent for go/no-go decision

---

## Key Learnings for Next Session

1. **OTP is random** — never hardcode "123456". Always extract from docker logs.
2. **CSRF fires before auth** — unauthenticated POST/PATCH/DELETE gets 403 (CSRF), not 401 (JWT). Tests should accept both.
3. **Rate limits are aggressive** — 5 OTP requests/minute/IP. Space token acquisition, reset DB + restart API between runs.
4. **The fixer agent modified app code** — review `git diff` carefully before committing. Not all changes may be desired.
5. **Session-scoped fixtures work well** — 4 tokens obtained once, reused across all 391 tests. Total overhead ~4s.
