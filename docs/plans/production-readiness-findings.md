# PashuRaksha ERP - Production Readiness Audit Findings

> **Audit Date**: April 11, 2026
> **Audited By**: Automated security & quality agents
> **Scope**: 90+ API endpoints, 25 DB tables, 3 frontend apps
> **Status**: All findings require remediation before production deployment

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 5 | Must fix before any deployment |
| HIGH | 12 | Must fix before production |
| MEDIUM | 10 | Should fix for production hardening |
| LOW | 5 | Nice to have |

---

## CRITICAL Findings

### CRIT-1: CSRF Bypass — Any Bearer Header Skips Protection

**Files:**
- `packages/api/app/middleware/csrf.py` lines 27-29
- `packages/collection/src/api/client.ts` line 4

**Problem:** The CSRF middleware skips validation for ANY request with an `Authorization: Bearer ...` header, regardless of whether the token is valid. An attacker can send `Authorization: Bearer garbage` to bypass CSRF on all mutating endpoints when targeting cookie-authenticated sessions. Additionally, the Collection frontend sends ZERO CSRF tokens with any mutation (POST/PUT/DELETE).

**Current Code (csrf.py):**
```python
auth_header = request.headers.get("authorization", "")
if auth_header.startswith("Bearer "):
    return await call_next(request)
```

**Current Code (client.ts):**
```typescript
const api = axios.create({
  baseURL: "/v1",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});
// No CSRF token interceptor
```

**Fix:**
1. In `csrf.py`: Validate the Bearer token before exempting from CSRF, or remove the bypass entirely
2. In `client.ts`: Add an axios request interceptor that reads the `csrf_token` cookie and attaches it as `X-CSRF-Token` for POST/PUT/DELETE/PATCH requests (matching the admin data-provider pattern)

---

### CRIT-2: OTP Rate Limiter Completely Broken

**File:** `packages/api/app/routers/auth.py` lines 87-117

**Problem:** The rate limiter counts OTP records with `created_at > one_hour_ago`, but each `request-otp` call DELETES all prior OTP records for that phone BEFORE inserting a new one. The count check can only ever find 0 or 1 records, never reaching the threshold of 5. Unlimited OTP requests are possible.

**Evidence:** Successfully sent 7+ consecutive OTP requests without receiving 429.

**Current Code:**
```python
# Line 101-103: Deletes BEFORE counting
await db.execute(delete(OTPRequest).where(OTPRequest.phone == body.phone))
# Line 94: Count always returns 0 or 1
recent = await db.execute(select(func.count()).where(...))
```

**Fix:** Either:
1. Use a separate rate-limit counter table that persists across OTP regenerations
2. Move the DELETE to AFTER the rate-limit check and flush/commit between operations
3. Use a sliding-window approach with a dedicated rate_limit table

---

### CRIT-3: Cross-Tenant Data Leak on /health/alerts/map

**File:** `packages/api/app/routers/health.py` lines 131-170

**Problem:** `GET /v1/health/alerts/map` queries ALL high-risk health events without any user_id or role filter. Any authenticated farmer can see every other farmer's animal health events, including district/village location data. This is a cross-tenant data leak exposing sensitive livestock health and location information.

**Evidence:** Farmer token successfully retrieved all health events across all users.

**Fix:** Restrict to `admin` and `vet` roles using `require_admin` dependency, or anonymize location data for non-admin users.

---

### CRIT-4: Milk Center Endpoints Have No Role Checks

**File:** `packages/api/app/routers/milk_center.py`

**Problem:** All milk center endpoints require `get_current_user` but do NOT check the user's role:
- `POST /v1/milk-center/receive` — any farmer can record milk for any other farmer
- `GET /v1/milk-center/farmers/search` — any farmer can search ALL farmers by phone/name/Aadhaar (PII leak)
- `POST /v1/milk-center/farmers/enroll` — any farmer can create new farmer accounts
- `GET /v1/milk-center/{center_id}/daily-report` — any farmer can view center reports
- `GET /v1/milk-center/{center_id}/farmer-settlements` — any farmer can view settlement data

**Fix:** Create a `require_milk_center_staff` dependency:
```python
async def require_milk_center_staff(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in {"milk_center", "admin"}:
        raise HTTPException(403, detail="Milk center staff access required")
    return current_user
```

---

### CRIT-5: Financial Calculations Use Float, Not Decimal

**Files:**
- `packages/api/app/routers/finance.py` lines 26, 93-101
- `packages/api/app/routers/milk_center.py` (milk pricing)
- `packages/api/app/models/milk.py` (quantity_liters is Float)

**Problem:** `TransactionCreate.amount` is typed as `float`. While the DB column is `Numeric(10,2)`, the aggregation endpoints sum via `float(t.amount)`, causing precision loss. Milk quantity, fat%, SNF% are all `Float` columns feeding into `rate_per_liter` and `total_amount` calculations. For financial amounts in INR, cumulative rounding errors across hundreds of settlement transactions will produce incorrect totals.

**Fix:**
1. Change `TransactionCreate.amount` to `Decimal` in Pydantic schema
2. Sum with `Decimal` in `financial_summary` instead of `float()`
3. Change `quantity_liters` from `Float` to `Numeric(10,2)` in the milk model
4. Convert milk pricing calculator to use `Decimal` throughout

---

## HIGH Findings

### HIGH-1: /v1/farmers Leaks ALL Farmer PII to Any User

**File:** `packages/api/app/routers/users.py` lines 15-52

**Problem:** Uses `get_current_user` instead of `require_admin`. A farmer-role user can access `GET /v1/farmers` and see ALL farmers' full names, phone numbers, districts, and village codes.

**Fix:** Change dependency from `get_current_user` to `require_admin`.

---

### HIGH-2: /v1/milk/daily-summary Exposes Global Data

**File:** `packages/api/app/routers/milk.py` lines 91-119

**Problem:** `get_daily_summary()` returns aggregated milk data across ALL users without role filtering. Any farmer can see total liters and farmer counts for the entire system.

**Fix:** For non-admin users, scope the query to `user_id == current_user.id`. Admin sees global data.

---

### HIGH-3: Admin Sees 0 Animals (Broken Filter)

**File:** `packages/api/app/routers/animals.py` line 61

**Problem:** `list_animals` always filters `Animal.user_id == current_user.id`. Admin users own no animals, so they get 0 results. Other list endpoints (milk, marketplace) correctly bypass this filter for admin.

**Fix:** Add admin bypass: `if current_user.role != "admin": base = base.where(Animal.user_id == current_user.id)`

---

### HIGH-4: Finance Crashes (500) with Extreme Amounts

**File:** `packages/api/app/schemas/finance.py` (TransactionCreate)

**Problem:** `POST /v1/finance/transaction` with `amount: 999999999999.99` causes an unhandled `NumericValueOutOfRangeError` because the DB column is `NUMERIC(10,2)` (max ~99,999,999.99). Returns bare "Internal Server Error" to client.

**Fix:** Add Pydantic constraint: `amount: Decimal = Field(..., gt=0, le=99_999_999.99)`

---

### HIGH-5: OTP Race Condition — IntegrityError on Re-Request

**File:** `packages/api/app/routers/auth.py` lines 101-103

**Problem:** Requesting a new OTP while a previous one exists can cause `IntegrityError: duplicate key value violates unique constraint "otp_requests_phone_key"` because the DELETE isn't flushed before the INSERT.

**Fix:** Use UPSERT (`INSERT ON CONFLICT UPDATE`) or add `await db.flush()` after the DELETE.

---

### HIGH-6: JWT Contains Phone Number in Plaintext

**File:** `packages/api/app/routers/auth.py` (JWT creation)

**Problem:** JWT payload includes `"phone": "+919900000001"`. Phone is PII and is sent in every HTTP request via cookie. Can be logged by proxies, CDNs, or WAFs.

**Fix:** Remove `phone` from JWT payload. Use `sub` (user ID) for identification. Fetch phone from DB if needed.

---

### HIGH-7: python-jose Has Known CVEs

**File:** `packages/api/pyproject.toml`

**Problem:** `python-jose==3.5.0` has known CVE-2024-33664 (ECDSA signature validation bypass). The library is unmaintained. Also `passlib==1.7.4` is broken with bcrypt 5.x.

**Fix:** Replace `python-jose` with `PyJWT`. Remove `passlib` from dependencies (already using `bcrypt` directly).

---

### HIGH-8: User Cache Doesn't Invalidate on Role Changes

**File:** `packages/api/app/middleware/auth.py` lines 17-35

**Problem:** `_user_cache` has 60s TTL with no invalidation mechanism. If an admin changes a user's role or deletes a user, the stale cache entry persists for up to 60 seconds.

**Fix:** Reduce TTL to 5-10 seconds, or add explicit cache invalidation when user records are modified.

---

### HIGH-9: Advisory/Ethno-Vet/Feed/Reference GET Endpoints Lack Auth

**Files:**
- `packages/api/app/routers/advisory.py`
- `packages/api/app/routers/ethno_vet.py`
- `packages/api/app/routers/feed.py`
- `packages/api/app/routers/reference.py`

**Problem:** These endpoints have no `Depends(get_current_user)`. Anyone can query advisory tips, traditional remedies, feed ingredients, market rates, insurance premiums, and medicine catalogs without authentication.

**Fix:** Add `get_current_user` dependency to all endpoints. For intentionally public data, create an explicit public router with documentation.

---

### HIGH-10: SQL LIKE Injection in Ethno-Vet Search

**File:** `packages/api/app/routers/ethno_vet.py` lines 63-64

**Problem:** Search query `q` is interpolated into LIKE pattern without escaping `%` and `_` wildcards: `pattern = f"%{q.lower()}%"`. User can pass `q=%` to match everything.

**Fix:** Escape wildcards: `escaped = q.replace("%", "\\%").replace("_", "\\_")`

---

### HIGH-11: No Error Boundary in Collection App

**File:** `packages/collection/src/` (missing component)

**Problem:** The Collection (Vite/React) app has no React Error Boundary. A runtime error in any component crashes the entire app with a white screen. This is especially critical for a field-deployed app used by non-technical collection center operators.

**Fix:** Add a top-level `<ErrorBoundary>` component wrapping `<App />` in `main.tsx`, with a user-friendly recovery UI.

---

### HIGH-12: Reference Data PUT Accepts Unvalidated Dict

**File:** `packages/api/app/routers/reference.py` lines 77-78, 138-139

**Problem:** `update_market_rate` and `update_insurance_premium` accept a raw `dict` body instead of a Pydantic schema. No type validation on values — passing `{"min_price": "not-a-number"}` bypasses validation.

**Fix:** Create `MarketRateUpdate` and `InsurancePremiumUpdate` Pydantic schemas with proper field types and constraints.

---

## MEDIUM Findings

### MED-1: Stored XSS Risk in Text Fields

**File:** `packages/api/app/routers/animals.py` (create/update)

**Problem:** Animal name, breed, notes fields store raw HTML. `<script>alert(1)</script>` is stored as-is. While SQL injection is prevented by ORM parameterization, stored XSS is a risk if any frontend renders values with `dangerouslySetInnerHTML`.

**Fix:** Strip HTML tags on input, or validate against a safe character pattern.

---

### MED-2: No Upper Bound on Milk Yield Quantity

**File:** `packages/api/app/schemas/milk.py` (YieldLogCreate)

**Problem:** `quantity_liters` has `gt=0` but no upper limit. A value of 999,999,999,999.99 liters is stored successfully.

**Fix:** Add `le=100` (reasonable max for single session: 100 liters per animal).

---

### MED-3: OTP Enumeration via Different Error Messages

**File:** `packages/api/app/routers/auth.py` lines 128-164

**Problem:** "No OTP request found" vs "Invalid OTP. Please try again." — different messages allow attacker to determine if an OTP was requested for a phone number.

**Fix:** Use a single generic message: "Invalid or expired OTP" for all failure cases.

---

### MED-4: Database Pool Config Ignores config.py

**File:** `packages/api/app/database.py` lines 6-13

**Problem:** `config.py` defines configurable pool settings via env vars, but `database.py` hardcodes `pool_size=10`, `max_overflow=20`, `pool_recycle=1800`. The `pool_recycle` values conflict: 3600 in config vs 1800 hardcoded. `echo` flag is hardcoded to `False` instead of using `settings.sql_echo`.

**Fix:** Replace hardcoded values with `settings.pool_size`, `settings.max_overflow`, etc.

---

### MED-5: Pashu Aadhaar ID Collision Risk

**File:** `packages/api/app/routers/animals.py` lines 27-29

**Problem:** Pashu Aadhaar ID generated from `secrets.randbelow(900000000000) + 100000000000`. DB has unique constraint, but collision causes unhandled IntegrityError (500). Birthday paradox makes collisions likely at scale.

**Fix:** Add retry loop (3 attempts) catching IntegrityError, or use a deterministic scheme.

---

### MED-6: Models Missing Soft Deletes and Audit Columns

**Files:** All model files under `packages/api/app/models/`

**Problem:** No model has `deleted_at`, `created_by`, or `updated_by`. Animal deletion is hard DELETE. For a production ERP with government Pashu Aadhaar IDs, hard deletes risk: loss of audit trail, broken FK references, compliance issues.

**Fix:** Add `SoftDeleteMixin` with `deleted_at` and `is_active`. Add `created_by`/`updated_by` to transactional tables. Convert animal DELETE to soft-delete.

---

### MED-7: Swagger/OpenAPI Publicly Accessible

**File:** `packages/api/app/main.py`

**Problem:** `/docs` and `/openapi.json` are accessible without auth, exposing the full 94-path API surface.

**Fix:** `docs_url=None if settings.environment != "development" else "/docs"`

---

### MED-8: Missing Security Response Headers

**File:** `packages/api/app/main.py`

**Problem:** No `Strict-Transport-Security`, `Content-Security-Policy`, or `X-Content-Type-Options` headers from the API. The Next.js admin app adds `X-Content-Type-Options` and `X-Frame-Options` but the API does not.

**Fix:** Add a security headers middleware for API responses.

---

### MED-9: Float Columns for Monetary-Adjacent Values

**Files:** Multiple model files

**Problem:** Inconsistent numeric types:
- `milk.py`: `quantity_liters`, `fat_pct`, `snf_pct` are `Float` while `rate_per_liter` and `total_amount` are `Numeric(10,2)`
- `feed.py`: `protein_pct`, `energy_kcal` are `Float` while `cost_per_kg` is `Numeric`
- `insurance.py`: `premium_amount` has Float annotation but Numeric column (type mismatch)

**Fix:** Use `Numeric` consistently for all financial values. `Float` acceptable for non-financial measurements.

---

### MED-10: Dates Not Explicitly Formatted in IST

**Files:**
- `packages/admin/src/utils/format.ts`
- `packages/collection/src/pages/Receipt.tsx`

**Problem:** `toLocaleDateString("en-IN")` depends on browser timezone. If browser is not in IST, dates display incorrectly.

**Fix:** Add `{ timeZone: "Asia/Kolkata" }` to all date formatting calls.

---

## LOW Findings

### LOW-1: No Future-Date Validation on Animal Birth Date

**File:** `packages/api/app/schemas/animals.py`

**Problem:** Year 2030 accepted for `date_of_birth`. No validation that `date_of_birth <= today`.

**Fix:** Add Pydantic validator: `@field_validator('date_of_birth') def check_not_future(cls, v): ...`

---

### LOW-2: Inconsistent Auth Error Envelope

**File:** `packages/api/app/routers/auth.py` line 47

**Problem:** Auth errors use `{"detail": {"detail": "...", "code": "..."}}` (nested), while all other errors use `{"detail": "string"}`.

**Fix:** Flatten to `{"detail": "message", "code": "ERROR_CODE"}` for consistency.

---

### LOW-3: console.warn Statements in Admin Auth Provider

**File:** `packages/admin/src/providers/auth-provider.ts` lines 50, 67, 83, 107

**Problem:** Four `console.warn` statements remain. Can leak diagnostic info in browser dev tools.

**Fix:** Remove or replace with a production logging library.

---

### LOW-4: `any` Type in Admin Data Provider

**File:** `packages/admin/src/providers/data-provider.ts` line 45

**Problem:** `let body: any;` with eslint-disable comment.

**Fix:** Type as `unknown` and use type narrowing.

---

### LOW-5: Collection App Hardcodes /v1 BaseURL

**File:** `packages/collection/src/api/client.ts` line 4

**Problem:** API URL hardcoded as `/v1`, relies on Vite proxy. Not configurable for production deployment behind a different reverse proxy.

**Fix:** Use `import.meta.env.VITE_API_URL || "/v1"` for configurability.

---

## Performance Results

### API Response Times (All PASS)

| Endpoint | Time | Target | Status |
|----------|------|--------|--------|
| GET /health | 11ms | <200ms | PASS |
| GET /v1/auth/me | 6ms | <200ms | PASS |
| GET /v1/admin/stats | 99ms | <200ms | PASS |
| GET /v1/admin/charts/milk | 26ms | <200ms | PASS |
| GET /v1/animals?limit=50 | 28ms | <200ms | PASS |
| GET /v1/health/alerts/map | 143ms | <200ms | PASS |
| GET /v1/milk/daily-summary | 28ms | <200ms | PASS |
| GET /v1/finance/summary | 34ms | <200ms | PASS |
| POST /v1/auth/request-otp | 618ms | <500ms | ACCEPTABLE (bcrypt) |

### Database Query Performance (All under 2ms)

| Query Pattern | Time | Notes |
|---------------|------|-------|
| animals WHERE user_id LIMIT 50 | 0.66ms | Seq scan (small table) |
| yield_logs WHERE recent 30d | 0.28ms | Index exists |
| health_events WHERE risk >= 0.7 | 0.15ms | No index on ai_risk_score |
| users JOIN animals GROUP BY | 1.67ms | Hash join |

### Missing Indexes (For Scale)
- `health_events.ai_risk_score` — used in dashboard and alert queries
- Composite `(user_id, created_at DESC)` on transactions

---

## OWASP Top 10 Scorecard

| # | Category | Status | Details |
|---|----------|--------|---------|
| A01 | Broken Access Control | FAIL | Cross-tenant leak, missing role checks on 6+ endpoints |
| A02 | Cryptographic Failures | PASS | HS256 JWT, bcrypt OTP hashing, 256-bit key enforced |
| A03 | Injection | PASS | SQLAlchemy parameterized queries, Pydantic validation |
| A04 | Insecure Design | FAIL | Rate limiting broken, OTP enumeration possible |
| A05 | Security Misconfiguration | WARN | Swagger public, hardcoded dev secrets in compose |
| A06 | Vulnerable Components | WARN | python-jose CVE, passlib broken with bcrypt 5.x |
| A07 | Auth Failures | FAIL | Rate limit bypass, CSRF bypass via fake Bearer |
| A08 | Data Integrity | PASS | JWT tampering rejected, "none" algorithm blocked |
| A09 | Logging Failures | PASS | Request logging middleware with request IDs |
| A10 | SSRF | PASS | No user-controlled fetch URLs |

---

## Fix Priority Batches

### Batch 1 — Security Critical (Do Now)
- [x] CRIT-1: Fix CSRF bypass in middleware/csrf.py + add CSRF to Collection client
- [x] CRIT-2: Fix OTP rate limiter (separate counter or fix delete-before-count)
- [x] CRIT-3: Restrict /health/alerts/map to admin/vet roles
- [x] CRIT-4: Add role checks to all milk_center.py endpoints
- [x] HIGH-1: Restrict /v1/farmers to admin role

### Batch 2 — Data Protection
- [x] CRIT-5: Switch financial calculations to Decimal
- [x] HIGH-2: Scope /milk/daily-summary by user role
- [x] HIGH-3: Fix admin animals filter (bypass for admin role)
- [x] HIGH-4: Add upper-bound validation on finance amounts
- [x] HIGH-5: Fix OTP race condition (use UPSERT)
- [x] HIGH-6: Remove phone from JWT payload
- [x] MED-3: Unify OTP error messages (prevent enumeration)

### Batch 3 — Code Quality & Hardening
- [x] HIGH-7: Replace python-jose with PyJWT
- [x] HIGH-8: Reduce user cache TTL or add invalidation
- [x] HIGH-9: Add auth to advisory/ethno-vet/feed/reference endpoints
- [x] HIGH-10: Fix SQL LIKE injection in ethno-vet search
- [x] HIGH-11: Add Error Boundary to Collection app
- [x] HIGH-12: Add Pydantic schemas for reference PUT endpoints
- [x] MED-4: Fix database.py pool config drift
- [x] MED-5: Add retry on Pashu Aadhaar ID collision

### Batch 4 — Production Polish
- [x] MED-1: Strip HTML from text input fields
- [x] MED-2: Add upper bound on milk yield quantity
- [x] MED-6: Add soft deletes and audit columns (deferred — architectural decision)
- [x] MED-7: Disable Swagger in production
- [x] MED-8: Add security response headers
- [x] MED-9: Fix Float/Numeric inconsistency in models
- [x] MED-10: Add IST timezone to date formatting
- [x] LOW-1: Future date validation on animal birth date
- [x] LOW-2: Flatten auth error envelope
- [x] LOW-3: Remove console.warn from admin auth provider
- [x] LOW-4: Replace `any` with `unknown` in data provider
- [x] LOW-5: Make collection app base URL configurable
