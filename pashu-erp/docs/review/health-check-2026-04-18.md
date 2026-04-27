# PashuRaksha ERP — Health Check Report

**Date**: 2026-04-18
**Method**: Automated build verification + CDP browser testing + API smoke tests + log analysis
**Agents Used**: build-runner, dependency-auditor, e2e-runner (CDP), security-auditor

---

## Executive Summary

| Layer | Status | Details |
|-------|--------|---------|
| **API Backend** | PASS | Lint clean, 507/507 tests pass, <30ms response times |
| **Database** | PASS | PostgreSQL healthy, connected for 39 hours |
| **Admin Dashboard** | FAIL | Build fails (missing `@mui/icons-material`), no sidebar/nav rendering |
| **Collection Centre** | FAIL | Build fails (same MUI issue), auth flow broken — all pages redirect to login |
| **Vet Platform** | FAIL | Build fails (same MUI issue), auth flow broken — 4/8 pages fail |
| **Mobile (Expo)** | NOT TESTED | Requires device/emulator testing |
| **Docker Stack** | PASS | All 4 containers healthy, 0 errors in logs |
| **Dependencies** | CONCERNS | 3 potential CVEs, Docker images not digest-pinned |

**Overall Verdict: FAIL — 3 frontend apps have build failures and auth flow is broken**

---

## 1. API Backend (FastAPI)

### Lint (ruff)
```
RESULT: PASS — All checks passed
```

### Tests (pytest)
```
507 passed, 24 skipped, 0 failures
Duration: 3m 58s
```

### Endpoint Health
| Endpoint | Status | Response Time |
|----------|--------|---------------|
| GET /health | 200 | 24ms |
| GET /ready | 200 | 621ms |
| GET /docs (Swagger) | 200 | 8ms |
| POST /v1/auth/request-otp | 422 (correct, empty body) | 10ms |
| GET /v1/animals | 401 (correct, no auth) | 12ms |
| GET /v1/admin/stats | 401 (correct) | 41ms |

**Note**: `/ready` is 621ms because it checks all dependencies (database, weather, IoT). All connected.

### Backend Logs
- **Errors**: 0
- **Warnings**: Rate limit warnings only (from E2E test hammering OTP endpoint)
- **Auth issue**: OTP verification returns 403, then rate-limited (429) — this is the root cause of all frontend auth failures

---

## 2. Frontend Builds

### Root Cause: Missing `@mui/icons-material` Package

All 3 frontend apps fail to build due to the same missing dependency:

```
Module not found: Can't resolve '@mui/icons-material/...'
```

**Affected files**:
- Admin: `income/page.tsx`, `login/page.tsx`, `marketplace/page.tsx`, `page.tsx` (5 imports)
- Collection: `components/NavBar.tsx` (`LogoutOutlined`)
- Vet: `components/NavBar.tsx` (`LogoutOutlined`)

**Fix**: `pnpm add @mui/icons-material` in the monorepo root

### Admin Dashboard (Next.js 14, port 3000)
- **Build**: FAIL (5 unresolved MUI icon imports)
- **Dev server**: Running (first load ~15s due to Next.js on-demand compilation, cached loads ~130ms)
- **CDP UI test**: 14 pages tested — 1 PASS (login), 12 WARN, 1 ERROR
- **Issues**:
  - No sidebar/nav detected on ANY page (likely Refine layout not rendering)
  - Very few MUI components on dashboard (<2)
  - 1 JS exception: "message channel closed before response received"
  - `/vet/alerts` page throws an error

### Collection Centre (Vite, port 3001)
- **Build**: FAIL (missing `@mui/icons-material/LogoutOutlined`)
- **Dev server**: Running (200ms response time)
- **CDP E2E**: 7 tests — 1 PASS, 1 FAIL, 4 BLOCKED, 1 WARN
- **Issues**:
  - Auth flow broken — OTP verify returns 403, then rate-limited (429)
  - All authenticated pages redirect to login
  - 1 slow request: POST /v1/auth/request-otp at 2,106ms
  - PWA service worker not registered

### Vet Platform (Vite, port 3002)
- **Build**: FAIL (missing `@mui/icons-material/LogoutOutlined`)
- **Dev server**: Running (143ms response time)
- **CDP E2E**: 8 tests — 2 PASS, 1 PARTIAL, 4 FAIL, 1 SKIP
- **Issues**:
  - Auth completely broken — API auth fails, all pages redirect to login
  - React Router deprecation warnings (v7 migration needed)
  - NavBar navigation non-functional

---

## 3. Docker Infrastructure

```
CONTAINER                    IMAGE                      STATUS              PORTS
pashu-erp-api-1             pashu-erp-api              Up 39h (healthy)    127.0.0.1:8000
pashu-erp-db-1              postgres:16-alpine         Up 39h (healthy)    127.0.0.1:5432
pashu-erp-mock-backends-1   pashu-erp-mock-backends    Up 39h (healthy)    127.0.0.1:8001
pashu-erp-test-db-1         postgres:16-alpine         Up 38h (healthy)    127.0.0.1:5433
```

**Status**: All containers healthy, no errors in logs.

---

## 4. Dependency Security

### Python (API)
- No confirmed CVEs in current locked versions
- python-multipart CVE-2024-53981 (ReDoS) — FIXED in locked version 0.0.24
- starlette 1.0.0 — new major release, monitor for post-1.0 CVE disclosures
- bcrypt 5.0.0 — major version bump from 4.x, verify compatibility

### Node.js
| Package | Concern | Severity |
|---------|---------|----------|
| next ^14.2.35 | CVE-2025-29927 middleware auth bypass | HIGH |
| vite ^5.4.0 | CVE-2024-45812 dev-server XSS | MEDIUM |
| axios ^1.7.0 | CVE-2024-39338 SSRF via proxy bypass | MEDIUM |
| react-native 0.76.3 | Behind current (0.77+) | LOW |
| expo ~52.0.0 | Behind SDK 53 | LOW |

### Docker Images
- `python:3.12-slim` — FLOATING (not pinned to digest)
- `postgres:16-alpine` — FLOATING
- **Recommendation**: Pin to specific patch versions or SHA digests

---

## 5. Critical Bugs Found

### BUG-001: Missing @mui/icons-material dependency [CRITICAL]
- **Impact**: All 3 frontend apps fail production build
- **Root cause**: Package not in dependencies despite being imported
- **Fix**: `pnpm add @mui/icons-material`

### BUG-002: Auth OTP verification returns 403 [CRITICAL]
- **Impact**: No user can log in to any frontend app
- **Symptoms**: POST /v1/auth/verify-otp returns 403, then rate-limited (429)
- **Backend log**: OTP generated correctly (code visible in dev logs), but verification rejects it
- **Possible causes**: OTP expiry too short, bcrypt 5.0 compatibility issue, CSRF middleware blocking, or test is sending wrong OTP format

### BUG-003: Admin layout not rendering [HIGH]
- **Impact**: No sidebar/navigation on any admin page
- **Symptoms**: CDP detects pages render but with no nav/sidebar MUI components
- **Possible cause**: Refine layout provider misconfigured or auth wrapper redirecting before layout renders

### BUG-004: Collection PWA service worker not registered [MEDIUM]
- **Impact**: Offline functionality non-operational
- **Note**: May be expected in dev mode

### BUG-005: React Router v7 deprecation warnings [LOW]
- **Impact**: Vet platform will break on React Router v7 upgrade
- **Fix**: Address `v7_startTransition` and relative route resolution flags

---

## 6. Performance

| Metric | Value | Assessment |
|--------|-------|------------|
| API /health | 24ms | GOOD |
| API /ready | 621ms | OK (checks 3 deps) |
| API general endpoints | 10-41ms | GOOD |
| OTP request | 1,011-2,106ms | SLOW (generates + stores OTP) |
| Admin first load | ~15s | Expected (Next.js dev compilation) |
| Admin cached loads | 130-190ms | GOOD |
| Collection/Vet loads | 140-200ms | GOOD |

---

## 7. Recommended Actions (Priority Order)

1. **[P0] Fix @mui/icons-material** — `pnpm add @mui/icons-material` (unblocks all builds)
2. **[P0] Debug OTP verify 403** — Check auth middleware, OTP expiry, bcrypt compat (unblocks all auth)
3. **[P1] Fix admin layout rendering** — Debug Refine layout provider + auth wrapper
4. **[P1] Pin Docker images** to specific versions for reproducible builds
5. **[P2] Run `pnpm audit` and `pip-audit`** to confirm CVE status
6. **[P2] Address React Router v7 deprecation** in vet platform
7. **[P3] Register PWA service worker** in collection centre production build
8. **[P3] Upgrade expo SDK 52 → 53** and react-native 0.76 → 0.77+

---

*Report generated by autonomous SDLC pipeline health check (build-runner + e2e-runner + dependency-auditor + security-auditor agents)*
