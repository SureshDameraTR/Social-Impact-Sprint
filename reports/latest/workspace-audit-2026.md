# PashuRaksha ERP — Workspace Audit Report (2026 Standards)

**Date**: 2026-04-15
**Auditors**: 7 parallel code review agents
**Scope**: ~200+ source files across 6 packages
**Standards**: OWASP 2025, FastAPI 0.115+, SQLAlchemy 2.x, Pydantic v2, React 19, Expo 52+

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 26 | Production blockers — must fix before any deployment |
| HIGH | 38 | Must fix before production |
| MEDIUM | 46 | Should fix |
| LOW | 37 | Nice to have |
| **Total** | **147** | |

---

## CRITICAL FINDINGS (26) — Production Blockers

### SEC-01: Authentication Gaps — 8+ Endpoints Unprotected
**Files**: `routers/weather.py`, `routers/bharat_pashudhan.py`, `routers/insurance.py:92`, `routers/vaccination.py:176,214`, `routers/medicine.py:21`, `routers/alerts.py:52`
**Issue**: 8+ endpoints have no `Depends(get_current_user)`.
**Violation**: Project CLAUDE.md mandates "every router endpoint requires Depends(get_current_user) — no exceptions"
**Impact**: Unauthenticated access to weather, registry, insurance estimates, vaccination schedules, medicines, and disease outbreak GPS coordinates.
**Fix**: Add `current_user: User = Depends(get_current_user)` to each endpoint signature.

### SEC-02: .env Files with Real Secrets in Working Tree
**Files**: `pashu-erp/.env`, `packages/api/.env`
**Issue**: Real `JWT_SECRET` and `POSTGRES_PASSWORD` in working tree. Risk of accidental `git add -A`.
**Fix**: Verify `.gitignore` coverage at all levels; rotate secrets if ever committed.

### SEC-03: Auth Token in localStorage on Web (XSS-Readable)
**File**: `packages/mobile/src/config/storage.ts:13-16`
**Issue**: On web platform, JWT stored in `localStorage` — readable by any XSS attack.
**Fix**: Use `sessionStorage` or httpOnly cookie flow for web auth.

### SEC-04: CSP Hardcoded to localhost — Breaks All Non-Dev Deployments
**File**: `packages/admin/next.config.js:18-25`
**Issue**: `connect-src 'self' http://localhost:8000 http://localhost:8001` blocks all API calls outside dev. Also blocks Google Fonts (`font-src`), Leaflet tiles (`img-src`), and CDN CSS (`style-src`).
**Fix**: Make CSP configurable via environment variables.

### SEC-05: ILIKE with Unsanitized Wildcards (Logic Bypass)
**File**: `routers/schemes.py:71`
**Issue**: `stmt.where(GovtScheme.ministry.ilike(f"%{ministry}%"))` — `%` and `_` not escaped.
**Fix**: Escape wildcards: `ministry.replace("%", "\\%").replace("_", "\\_")`

### SEC-06: BaseHTTPMiddleware Anti-Pattern on All 3 Middleware Classes
**Files**: `main.py:53-75`, `middleware/csrf.py`, `middleware/request_logging.py`
**Issue**: Known anti-pattern causing request body streaming issues, `BackgroundTask` execution order bugs, and memory leaks under load.
**Fix**: Replace with pure ASGI middleware classes.

### DATA-01: Animal DELETE Performs HARD Delete
**File**: `routers/animals.py:157-175`
**Issue**: `await db.delete(animal)` instead of `animal.deleted_at = datetime.now(timezone.utc)`.
**Impact**: Permanent data loss. Orphaned rows in health_events, vaccinations, yield_logs, insurance, vet_consultations.
**Fix**: Set `deleted_at` instead of calling `db.delete()`.

### DATA-02: No Soft-Delete Filtering on ANY Query
**Files**: All 28 routers
**Issue**: Despite 18 of 20 models having `SoftDeleteMixin`, ZERO `SELECT` statements filter `.where(deleted_at.is_(None))`.
**Impact**: The entire soft-delete architecture is decorative. Deleted records appear everywhere.
**Fix**: Add `.where(Model.deleted_at.is_(None))` to every query.

### DATA-03: VetConsultation Model Missing SoftDeleteMixin
**File**: `models/vet.py:30`
**Issue**: `VetConsultation(AuditMixin, Base)` — no `SoftDeleteMixin`.
**Fix**: Add `SoftDeleteMixin` to class inheritance.

### DATA-04: No ON DELETE Clause on Any Foreign Key
**Files**: All model files
**Issue**: Every `ForeignKey("table.id")` has no `ondelete` clause.
**Fix**: Add `ondelete="RESTRICT"` for soft-delete architecture.

### DATA-05: Float Used for Money in Pydantic Schemas
**Files**: `schemas/finance.py:22`, `schemas/marketplace.py`, `schemas/milk.py`, `schemas/insurance.py`, `schemas/shg.py`, `schemas/feed.py`
**Issue**: `float` for all financial fields. DB uses `NUMERIC(10,2)` but float round-trip introduces IEEE 754 errors.
**Impact**: Rs 3333.33 becomes 3333.329999... Cumulative errors in settlements.
**Fix**: Replace `float` with `Decimal` with `max_digits=10, decimal_places=2`.

### DB-01: Migration Chain Non-Executable
**Files**: `alembic/versions/add_performance_indexes.py`, `alembic/versions/a1b2c3d4e5f6_add_gender_column_to_users.py`
**Issue**: Two migrations share revision ID `a1b2c3d4e5f6`. OTP migration depends on duplicate. `health_events` composite index references non-existent `user_id` column. OTP model `request_count` missing from migration.
**Impact**: `alembic upgrade head` FAILS on fresh database.
**Fix**: Rename duplicate revision IDs. Fix column references.

### DB-02: In-Process User Cache Unbounded and Not Process-Safe
**File**: `middleware/auth.py:19-36`
**Issue**: Module-level `_user_cache: dict` caches ORM User objects. No size limit (grows to 1001). Cached detached ORM objects cause `DetachedInstanceError`. Per-worker in multi-worker mode.
**Fix**: Use `cachetools.TTLCache(maxsize=100, ttl=10)` with non-ORM value types, or remove cache.

### MOB-01: Onboarding Profile Data Never Persisted
**File**: `packages/mobile/app/onboarding/profile.tsx:100-108`
**Issue**: "Save & Continue" navigates but never saves name, district, village to API or storage.
**Impact**: Complete data loss — users think their data is saved.
**Fix**: Add `api.post('/users/profile', { name, district, village })` before navigation.

### MOB-02: Onboarding First-Animal Data Never Persisted
**File**: `packages/mobile/app/onboarding/first-animal.tsx:98-107`
**Issue**: "Add Animal" navigates but never sends species, breed, name to API.
**Fix**: Add `api.post('/animals', { species, breed, name })` before navigation.

### MOB-03: Vaccination markDone Catch Block Applies Same Optimistic Update
**File**: `packages/mobile/app/vaccinations.tsx:47-58`
**Issue**: On API failure, the catch block applies the same state update as success → false vaccination records.
**Impact**: Health-critical: false positive records can lead to skipped real vaccinations.
**Fix**: Remove optimistic update from catch block; show error snackbar instead.

### MOB-04: Animal Delete Has No Confirmation Dialog
**File**: `packages/mobile/app/animal/[id].tsx:152-158`
**Issue**: Single tap permanently deletes animal record with no confirmation.
**Fix**: Add `Alert.alert()` confirmation before executing delete.

### MOB-05: Login Uses Raw fetch() Instead of API Client
**File**: `packages/mobile/app/(auth)/login.tsx:44-94`
**Issue**: Both `handleSendOtp` and `handleVerifyOtp` use raw `fetch()` — no timeout, no retry, no abort.
**Impact**: Hangs indefinitely on slow rural networks.
**Fix**: Use `api.post()` from `src/config/api.ts` or add AbortController.

---

## HIGH FINDINGS (38) — Must Fix Before Production

### PERF-01: N+1 in IoT Readings — Up to 50 Sequential HTTP Calls
**File**: `routers/iot.py:86-96`
**Fix**: Use `asyncio.gather()` with semaphore.

### PERF-02: Animal Model Eager Loading — 4 selectin Relationships
**File**: `models/animal.py:55-58`
**Fix**: Change to `lazy="noload"`, use explicit `.options(selectinload(...))` per endpoint.

### PERF-03: Financial Summary Loads All Rows Into Python
**File**: `routers/finance.py:87-110`
**Fix**: Use SQL `SUM(...) GROUP BY type, category`.

### PERF-04: Income History Loads All Records Then Paginates in Python
**File**: `routers/income.py:126-187`
**Fix**: Use SQL UNION ALL with ORDER BY and LIMIT/OFFSET.

### PERF-05: Milk Center Daily Report In-Memory Aggregation
**File**: `routers/milk_center.py:108-157`
**Fix**: Use SQL `func.sum`, `func.count`, `func.avg` per shift.

### PERF-06: Admin Dashboard 9 Sequential DB Queries
**File**: `routers/admin.py:28-135`
**Fix**: Use `asyncio.gather()` to run all 9 concurrently.

### PERF-07: No Connection Pooling on HTTP Service Clients
**Files**: `services/weather_service.py`, `services/bharat_pashudhan.py`, `services/iot_service.py`, `services/storage_service.py`
**Fix**: Create shared `httpx.AsyncClient` in lifespan with connection pooling.

### PERF-08: No Retry Logic on Any External Service Call
**Files**: All 4 service clients + `services/otp/sarvam.py`
**Fix**: Add `tenacity` retry with exponential backoff.

### PERF-09: recharts Imported Inside Render Function
**Files**: `admin/src/app/page.tsx:38`, `milk/page.tsx:45`, `income/page.tsx:37`, `marketplace/page.tsx:52`
**Fix**: Move `require("recharts")` to module scope.

### PERF-10: Animals Page Fetches ALL Data Then Paginates in Memory
**File**: `admin/src/app/animals/page.tsx:59`
**Fix**: Add `pagination: { current: page + 1, pageSize: rowsPerPage }` to useList.

### SEC-07: No Global Rate Limiting
**File**: `config.py:19`
**Issue**: `rate_limit_per_minute=10` defined but never used on any endpoint.
**Fix**: Add `slowapi` middleware.

### SEC-08: JWT 24h/7d Expiry, No Refresh, No Revocation
**Files**: `config.py:8`, `routers/auth.py:31-32`
**Fix**: Implement short-lived access tokens + refresh tokens + revocation table.

### SEC-09: File Upload No Size/Type Validation
**File**: `routers/files.py:19-42`
**Fix**: Add max size (10MB), allowed types, content-type verification.

### SEC-10: Mock Backends Port Exposed to 0.0.0.0
**File**: `docker-compose.yml:26`
**Fix**: Change to `"127.0.0.1:8001:8001"`.

### SEC-11: CSRF Token Not Bound to Session
**File**: `routers/auth.py:224`
**Fix**: Use HMAC-signed token derived from JWT.

### SEC-12: User Cache No Invalidation on Role Change
**File**: `middleware/auth.py:19-37`
**Fix**: Call `invalidate_user_cache()` after role changes; use Redis for multi-worker.

### SEC-13: Unvalidated External URLs as img src/href
**Files**: `admin/src/app/vet/cases/[id]/page.tsx:519-530`, `vet/src/pages/CaseDetail.tsx:253,275`
**Fix**: Validate URLs against https-only allowlist.

### SEC-14: Aadhaar Unsalted SHA-256
**File**: `routers/milk_center.py:272`
**Fix**: Use salted hash: `sha256((aadhaar + salt).encode())`.

### DATA-06: No Unique Constraint on yield_logs → Duplicate Milk Recording
**File**: `models/milk.py`
**Fix**: Add `UniqueConstraint('animal_id', 'session', 'recording_date')`.

### DATA-07: No Buffalo Species in Disease Rules
**File**: `services/disease_rules.py`
**Impact**: Disease triage non-functional for buffaloes — a major Karnataka livestock.
**Fix**: Add `"buffalo"` key with cattle-similar rules.

### DATA-08: IoT Service Wrong Parameter Names
**File**: `services/iot_service.py:30,71-73`
**Issue**: Sends `device_type` (mock expects `type`), `from`/`to` (mock expects `from_ts`/`to_ts`).
**Fix**: Align parameter names with mock API contract.

### DATA-09: 6 List Endpoints Return Raw Lists Instead of Envelope
**Files**: `routers/shg.py:97`, `routers/schemes.py:60`, `routers/feed.py:19`, `routers/ethno_vet.py:18,58`, `routers/advisory.py:18`, `routers/insurance.py:25`
**Fix**: Return `{"data": [...], "total": int}`.

### DATA-10: Missing updated_at on Most Models
**Files**: 15+ model files
**Fix**: Add `updated_at` to `AuditMixin` or `TimestampMixin`.

### DATA-11: Registry Mock Returns Invalid Date (2027-02-30)
**File**: `mocks/routers/registry.py:139`
**Fix**: Use `calendar.monthrange()` for last day.

### DATA-12: Only 12 of 31 Karnataka Districts
**File**: `mocks/data/karnataka_districts.json`
**Fix**: Add all 31 districts with accurate elevation/coordinates.

### TEST-01: Auth Router Has Zero Tests
**Impact**: OTP rate limiting, JWT issuance, role checks — all untested.

### TEST-02: CSRF Middleware Has Zero Tests
**Impact**: CSRF protection regressions invisible.

### TEST-03: Mobile Package Has Zero Tests
**Impact**: 26 screens, primary farmer interface — zero coverage.

### TEST-04: Migration Chain Has Duplicate Revision IDs
**Issue**: `alembic upgrade head` fails on fresh database. (Overlaps DB-01)

### FE-01: All Admin Pages are "use client" — Zero Server Components
**Files**: Every `packages/admin/src/app/*/page.tsx`
**Fix**: Separate data fetching into Server Components.

### FE-02: Double API URL Prefix in Collection CentreProvider
**File**: `packages/collection/src/hooks/useCentre.tsx:36`
**Issue**: `/v1/` prefix in code + `/v1` fallback baseURL → `/v1/v1/` double prefix.
**Fix**: Remove `/v1/` from api.get call.

### FE-03: Client-Side Sorting After Server-Side Pagination
**File**: `admin/src/app/farmers/page.tsx:88-108`
**Fix**: Pass sort parameters to server or do everything client-side.

### FE-04: Receipt Page Missing print.css Import
**File**: `packages/collection/src/pages/Receipt.tsx:12`
**Fix**: Create missing file or remove import.

### SVC-01: Storage Mock No File Size Limit — DoS Risk
**File**: `mocks/routers/storage.py:41`
**Fix**: Add max-size guard before `file.read()`.

### SVC-02: Sarvam OTP Hardcoded Base URL
**File**: `services/otp/sarvam.py:9`
**Fix**: Accept `base_url` as constructor parameter.

### SVC-03: Console OTP Logs Full OTP with No Environment Guard
**File**: `services/otp/console.py:15-24`
**Fix**: Add environment check; mask phone number.

---

## MEDIUM FINDINGS (46) — Should Fix

### Code Quality (9)
- No pre-commit hook configuration
- No mypy/pyright type checking configured
- Minimal ruff rules (no S, B, PT, I rules)
- Admin tsconfig excludes test files from type checking
- No ESLint in admin package
- Inline Pydantic schemas in routers duplicate schemas/ versions
- Duplicated constants, enums, validators across files
- `console.error` left in mobile production paths
- `datetime.utcnow()` deprecated in Python 3.12+

### Architecture (9)
- In-memory reference cache unbounded (`routers/reference.py:31-52`)
- No circuit breaker on any external service
- No request body size limit on API
- No database SSL configuration
- Admin/vet role can't access individual animals (403) (`routers/animals.py:107-174`)
- Missing Permissions-Policy, COEP, COOP headers
- `typing.Optional` used instead of `X | None` (Python 3.10+)
- Missing `__init__.py` exports in schemas package
- `get_db` return type annotation wrong (AsyncSession vs AsyncGenerator)

### Mobile (11)
- No SafeAreaView — content obscured on notched phones
- No react-native-screens — all screens kept in memory
- Audio.Sound memory leak on weather screen unmount
- No crash reporting (ErrorBoundary catches but doesn't report)
- 14+ hardcoded English strings not through `t()`
- No offline data persistence or mutation queue
- Insurance claim form clears on error — data loss
- Missing `@react-native-community/netinfo`
- `patch`/`delete` methods lack retry logic
- `sell.tsx` product key `goat_products` doesn't match i18n key `sell.goatProducts`
- `require('react-native')` runtime import in income.tsx

### Frontend (8)
- Raw hex colors instead of MUI theme tokens (12+ instances)
- `useEffect` for document.title instead of Next.js metadata API
- `localStorage.getItem` during SSR/hydration in CentreProvider
- `Math.random()` as React key fallback in map page
- Vet Cases page bypasses Refine data provider
- React 18 not 19 across all packages
- `@ts-expect-error` in data-provider.ts
- Unused imports (CircularProgress in dashboard)

### Accessibility (9)
- Missing `aria-label` on search inputs across all admin pages
- Tables lack `aria-label` or `aria-labelledby`
- Loading spinners have no accessible text
- No `accessibilityLabel` on mobile interactive elements (species picker, device cards, radio buttons)
- Missing GIGW compliance for government app
- Vaccine schedule table uses array index as key
- Array index keys in OTP input fields
- Error boundary uses `console.error` in production
- Error.tsx does not log/report errors

---

## LOW FINDINGS (37) — Nice to Have

- Inconsistent import styles (mixed `from datetime import` vs `import datetime`)
- Mixed pagination parameter naming (`offset`/`limit` vs `skip`/`limit`)
- Duplicated login page code across 3 packages (~150 lines each)
- `TouchableOpacity` instead of `Pressable` in 3 mobile files
- `X-XSS-Protection: 1; mode=block` header deprecated
- Hardcoded theme colors instead of tokens in mobile (12+ instances)
- Missing RTL support configuration in mobile `app.json`
- Invalid `setupFilesAfterFramework` key in mobile `jest.config.js`
- No `expo-updates` for OTA updates
- `Dimensions.get('window')` at module level (stale on rotation)
- `toLocaleString('en-IN')` hardcoded instead of i18n-aware
- Missing `__all__` exports in services `__init__.py`
- Duplicate `_strip_html` function across 4 schema files
- `VetCaseListResponse` missing `total` field
- Hardcoded magic numbers in health router (should use settings)
- Both weather.py and alerts.py define `AlertSeverity` with different values
- No OpenAPI response_model on most list endpoints
- `VetCaseRead` uses `str` for all fields including enums/dates
- `md5` used in weather mock (should use sha256 for consistency)
- Mock CORS allows all methods/headers
- Import order inconsistency in mocks/main.py
- Weather mock TTS returns silence instead of speech
- Mock Dockerfile `pip install` without version pinning
- Registry mock uses `Random` generating fake Aadhaar fragments
- No API versioning on mock endpoints
- OTP base class doesn't define `verify_otp` method
- Inconsistent test class naming conventions
- Mock factories duplicated across test files
- Disease rules tests use `next()` without default
- Visual regression tests lack tolerance documentation
- k6 load test covers only GET endpoints
- `validate_agents.py` doesn't validate test coverage
- pnpm-workspace.yaml doesn't include API package
- `Mapped[str]` used for UUID columns instead of `Mapped[UUID]`
- No `CHECK` constraints on numeric columns (amounts, percentages)
- GPS coordinates use `Float` instead of PostGIS geography types
- Vet dashboard alerts endpoint hardcodes `.limit(50)` with no pagination

---

## PRIORITY ACTION PLAN

### Phase 1: STOP THE BLEEDING (Week 1) — 7 tasks
1. Add `Depends(get_current_user)` to 8+ unprotected endpoints
2. Replace `db.delete(animal)` with soft delete
3. Add `.where(deleted_at.is_(None))` to all queries
4. Fix migration chain: rename duplicate revision IDs
5. Ensure `.env` in `.gitignore`; rotate secrets
6. Fix mobile onboarding data persistence
7. Fix vaccination markDone catch block

### Phase 2: HARDEN (Week 2) — 9 tasks
8. Replace `float` with `Decimal` in all financial schemas
9. Add file upload size/type validation
10. Fix CSP to be environment-aware
11. Bind mock-backends to `127.0.0.1`
12. Add connection pooling (shared `httpx.AsyncClient`)
13. Add retry logic on all service clients
14. Fix IoT parameter name mismatches
15. Add buffalo disease rules
16. Add confirmation dialog to mobile animal delete

### Phase 3: OPTIMIZE (Week 3) — 8 tasks
17. Replace `BaseHTTPMiddleware` with pure ASGI middleware
18. Move financial aggregation to SQL
19. Change Animal relationships to `lazy="noload"`
20. Implement server-side pagination
21. Add global rate limiting middleware
22. Add unique constraint on yield_logs
23. Convert admin pages to Server Components
24. Add auth/CSRF/mobile test coverage

### Phase 4: POLISH (Week 4) — 8 tasks
25. Add pre-commit hooks (ruff, mypy, .env blocking)
26. Implement short-lived access + refresh tokens
27. Add circuit breaker pattern
28. Add offline support to mobile
29. Fix all i18n gaps
30. Add accessibility labels
31. Complete Karnataka district data
32. Consolidate duplicated schemas/enums/validators
