# PashuRaksha ERP - Production Readiness & Comprehensive Testing Prompt

> **Project**: PashuRaksha ERP (Livestock Management Platform for Rural India)
> **Stack**: FastAPI + PostgreSQL (backend), Next.js (admin), Vite+React (milk collection), Expo/RN (mobile)
> **Monorepo**: pnpm workspaces, Docker Compose, `just` task runner

---

## PHASE 0: ENVIRONMENT SETUP & INFRASTRUCTURE

### 0.1 Start All Backend Services via Docker

```bash
cd pashu-erp

# Build and start all containers (Postgres 16, Mock backends, API)
docker compose up -d --build

# Verify all 3 services are healthy
docker compose ps   # STATUS must show "healthy" for db, mock-backends, api

# Run database migrations
docker compose exec api alembic upgrade head

# Seed demo data (idempotent - safe to re-run)
docker compose exec api python -m app.seed.demo_data

# Verify API responds
curl http://localhost:8000/health     # {"status": "ok"}
curl http://localhost:8000/ready      # {"status": "ready"}
curl http://localhost:8001/health     # Mock backends health
```

### 0.2 Start Frontend Applications

```bash
# Admin Dashboard (Next.js on port 3000)
cd packages/admin && pnpm install && pnpm dev

# Milk Collection Center (Vite on port 5173)
cd packages/collection && pnpm install && pnpm dev
```

### 0.3 Demo Credentials

| Role | Phone | OTP | Purpose |
|------|-------|-----|---------|
| Admin | +919900000001 | 123456 | Admin dashboard, full access |
| Farmer (Lakshmi) | +919900000002 | 123456 | Farmer with cattle, milk logs |
| Farmer (Annapurna) | +919900000003 | 123456 | Farmer with goats |
| Farmer (Savitri) | +919900000004 | 123456 | Farmer with sheep |

---

## PHASE 1: BACKEND - API CORRECTNESS & SECURITY AUDIT

### 1.1 Authentication Flow (Critical Path)

Test each step through browser/curl against `http://localhost:8000`:

1. **OTP Request**: `POST /v1/auth/request-otp` with `{"phone": "+919900000002"}`
   - Verify: 200 response, OTP created in DB
   - Verify: Rate limit - send 6 requests rapidly, 6th should be 429
   - Verify: Invalid phone format rejected (missing +91, too short, too long)
   - Verify: Non-Indian numbers rejected

2. **OTP Verification**: `POST /v1/auth/verify-otp` with `{"phone": "+919900000002", "otp": "123456"}`
   - Verify: JWT returned in httponly cookie
   - Verify: CSRF token returned
   - Verify: Wrong OTP returns 401 (not 400 - check for info leakage)
   - Verify: Expired OTP (wait 5+ min) returns appropriate error
   - Verify: Max 3 attempts before lockout
   - Verify: Same error message for "no OTP found" vs "wrong OTP" (prevent enumeration)

3. **Session**: `GET /v1/auth/me`
   - Verify: Returns user profile with valid JWT
   - Verify: 401 without cookie/token
   - Verify: 401 with expired/malformed JWT
   - Verify: CSRF token required for state-changing requests

4. **Logout**: `POST /v1/auth/logout`
   - Verify: Clears auth cookies
   - Verify: Subsequent /me returns 401

### 1.2 Authorization & Access Control (RBAC)

For each endpoint, test with admin, farmer, and unauthenticated requests:

| Endpoint | Admin | Farmer (own) | Farmer (other's) | Unauth |
|----------|-------|-------------|-------------------|--------|
| GET /v1/admin/stats | 200 | 403 | 403 | 401 |
| GET /v1/admin/charts/milk | 200 | 403 | 403 | 401 |
| GET /v1/admin/gis/alerts | 200 | 403 | 403 | 401 |
| GET /v1/animals | 200 (all) | 200 (own only) | N/A | 401 |
| POST /v1/animals | 200 | 200 | N/A | 401 |
| PATCH /v1/animals/{id} | 200 | 200 (own) | 403 | 401 |
| DELETE /v1/animals/{id} | 200 | 200 (own) | 403 | 401 |
| GET /v1/health/history/{animal_id} | 200 | 200 (own animal) | 403 | 401 |
| GET /v1/health/alerts/map | 200 | **CHECK** | **CHECK** | 401 |
| GET /v1/finance/summary | 200 | 200 (own) | N/A | 401 |
| POST /v1/finance/transaction | 200 | 200 | N/A | 401 |
| GET /v1/milk/daily-summary | 200 | **CHECK** | **CHECK** | 401 |
| POST /v1/milk-center/receive | 200 | **CHECK role=milk_center** | 403 | 401 |
| GET /v1/milk-center/farmers/search | 200 | **CHECK** | **CHECK** | 401 |
| POST /v1/milk-center/farmers/enroll | 200 | **CHECK** | **CHECK** | 401 |

**Flag any endpoint that returns data across user boundaries without admin role.**

### 1.3 Input Validation & Injection Testing

Test each endpoint with malicious/edge-case inputs:

**Animals CRUD:**
- Create animal with empty name, XSS in name (`<script>alert(1)</script>`), SQL in name (`'; DROP TABLE animals; --`)
- Species value not in enum: `"species": "dragon"`
- Negative weight: `"weight_kg": -50`
- Future birth date: `"date_of_birth": "2030-01-01"`
- Pashu Aadhaar ID collision (duplicate)
- UUID injection in animal_id path param

**Health Events:**
- Log health event for animal belonging to different user
- Empty symptoms list
- Symptoms with HTML/script tags
- Invalid event_type not in enum
- Future event_date
- risk_score outside 0-100 range

**Milk Collection:**
- Negative quantity: `"quantity_liters": -5`
- Zero quantity: `"quantity_liters": 0`
- Extreme quantity: `"quantity_liters": 99999`
- Fat % outside range: `"fat_pct": 99.9` or `"fat_pct": -1`
- SNF % outside range: `"snf_pct": 0` or `"snf_pct": 100`
- Invalid session: `"session": "midnight"`

**Finance:**
- Negative amount: `"amount": -1000`
- Extremely large amount: `"amount": 999999999999.99`
- Invalid transaction type
- Category with special characters
- Decimal precision: `"amount": 10.999` (should round or reject)

**Marketplace:**
- Sell record for animal not owned by user
- Price of 0 or negative
- Missing required fields
- buyer_phone with invalid format

### 1.4 API Response Consistency

Verify across ALL endpoints:
- Consistent error envelope: `{"detail": "message"}` for errors
- Correct HTTP status codes (201 for create, 200 for update, 204 for delete)
- Pagination format consistency: `{"data": [...], "total": N}` where applicable
- Date formats: ISO 8601 with timezone
- Decimal precision: financial amounts have exactly 2 decimal places
- Empty list returns `[]` not `null`
- No stack traces in error responses (ENVIRONMENT=production)

### 1.5 Database Integrity

```sql
-- Connect to Postgres and verify:
docker compose exec db psql -U pashu -d pashuraksha

-- Check all foreign keys have ON DELETE behavior defined
SELECT tc.table_name, kcu.column_name, rc.delete_rule
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.referential_constraints rc ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- Check for orphaned records
SELECT a.id FROM animals a LEFT JOIN users u ON a.user_id = u.id WHERE u.id IS NULL;
SELECT h.id FROM health_events h LEFT JOIN animals a ON h.animal_id = a.id WHERE a.id IS NULL;
SELECT y.id FROM yield_logs y LEFT JOIN animals a ON y.animal_id = a.id WHERE a.id IS NULL;

-- Check indexes exist on commonly queried columns
SELECT tablename, indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;

-- Verify no null UUIDs in primary keys
SELECT 'users' AS tbl, COUNT(*) FROM users WHERE id IS NULL
UNION ALL SELECT 'animals', COUNT(*) FROM animals WHERE id IS NULL;

-- Check unique constraints
SELECT constraint_name, table_name FROM information_schema.table_constraints
WHERE constraint_type = 'UNIQUE';
```

---

## PHASE 2: FRONTEND UI - END-TO-END TESTING

### 2.1 Admin Dashboard (http://localhost:3000)

Open in Chrome via Claude Code browser automation.

**Login Flow:**
1. Navigate to http://localhost:3000
2. Verify redirect to /login if not authenticated
3. Enter phone: 9900000001, verify +91 prefix handling
4. Enter wrong OTP (000000) - verify error message displayed
5. Enter correct OTP (123456) - verify redirect to dashboard
6. Verify sidebar shows all navigation items: Dashboard, Farmers, Animals, Health, Income, Milk, Marketplace, Vaccinations, Schemes, IoT, Map
7. Verify user name "Deepak Kumar" visible in header/sidebar

**Dashboard Page:**
1. Verify 4 stat cards load with numeric values (not "---" or NaN)
2. Verify milk collection chart renders with 30-day data
3. Verify GIS map loads with alert markers
4. Verify all stat cards have correct labels (Total Farmers, Total Animals, Active Alerts, Milk Today)
5. Check responsive layout - resize window to 768px, verify cards stack

**Farmers Page:**
1. Navigate to /farmers
2. Verify farmer table loads with demo data (Lakshmi, Annapurna, Savitri)
3. Verify district filter dropdown works
4. Verify search/filter by name works
5. Verify stat cards show correct counts
6. Verify table pagination if > 10 records
7. Click on a farmer row - verify detail view or navigation

**Animals Page:**
1. Navigate to /animals
2. Verify animal list loads with species icons (cow, goat, sheep)
3. Verify species filter chips work
4. Verify animal cards show: name, species, breed, age, owner
5. Verify empty state if no animals match filter

**Milk Page:**
1. Navigate to /milk
2. Verify daily collection table loads
3. Verify date picker/range selector works
4. Verify totals row calculates correctly
5. Cross-check: milk data here should match dashboard stat card

**Health Page:**
1. Navigate to /health
2. Verify health event list loads
3. Verify risk badges show correct colors (green/yellow/red)
4. Verify filter by severity works

**Income Page:**
1. Navigate to /income
2. Verify income summary loads
3. Verify breakdown by category chart

**Marketplace Page:**
1. Navigate to /marketplace
2. Verify sell records display
3. Verify product type filters

**Map Page:**
1. Navigate to /map
2. Verify Leaflet map renders
3. Verify alert markers are clickable with popups
4. Verify zoom controls work

### 2.2 Milk Collection Center (http://localhost:5173)

**Login Flow:**
1. Navigate to http://localhost:5173
2. Login with admin credentials (or milk_center role user)
3. Verify dashboard loads with shift selector

**Cross-App Data Flow (CRITICAL):**
This tests data entered in Collection Center appearing in Admin Dashboard.

1. **In Collection Center** - Record a new milk collection:
   - Select morning shift
   - Search for farmer "Lakshmi" by phone
   - Enter: Quantity=5.5L, Fat%=4.2, SNF%=8.5
   - Submit the record
   - Verify success message and receipt generation

2. **In Admin Dashboard** - Verify the record appears:
   - Navigate to /milk page
   - Verify the new 5.5L record from Lakshmi appears
   - Navigate to dashboard
   - Verify "Milk Today" stat card updated
   - Verify milk chart shows today's data point

3. **In Collection Center** - Enroll a new farmer:
   - Navigate to Enroll page
   - Enter: Name="Test Farmer", Phone="+919900000099", District="Mysore"
   - Aadhaar: Enter masked format (XXXX-XXXX-1234)
   - Submit enrollment

4. **In Admin Dashboard** - Verify new farmer:
   - Navigate to /farmers
   - Search for "Test Farmer"
   - Verify the farmer appears with correct district

**Intake Page Validation:**
1. Try submitting without selecting farmer - verify error
2. Try quantity = 0 - verify error
3. Try fat% = 15 (above max 12) - verify error
4. Try SNF% = 3 (below min 6) - verify error
5. Try submitting with all valid data - verify success

**Receipt Page:**
1. After successful collection, verify receipt shows:
   - Farmer name, date, shift
   - Quantity, fat%, SNF%, calculated rate
   - Total payment amount
2. Verify print button works (opens print dialog)

**Settlement Page:**
1. Navigate to settlements
2. Verify farmer settlement list loads
3. Verify payment calculations match collection records

### 2.3 Cross-Console Verification Matrix

This is the **most critical test** - data consistency across all frontends:

| Action in Source | Verify in Target | What to Check |
|-----------------|-----------------|---------------|
| Add milk record in Collection | Admin /milk page | Record appears with correct values |
| Enroll farmer in Collection | Admin /farmers page | Farmer appears with all fields |
| Add animal via API (curl) | Admin /animals page | Animal appears with correct species |
| Log health event via API | Admin /health page | Event shows with risk badge |
| Record sale via API | Admin /marketplace | Sale record with correct amount |
| Add transaction via API | Admin /income | Transaction in summary |
| Create collection center via API | Collection login | Center available for selection |

### 2.4 UI Quality Checks

For EVERY page in both Admin and Collection:

**Visual:**
- [ ] No broken images or missing icons
- [ ] No text overflow/truncation without tooltip
- [ ] Tables have horizontal scroll on overflow
- [ ] Cards have consistent spacing and alignment
- [ ] Colors match Material UI theme consistently
- [ ] No console errors (open Chrome DevTools > Console)
- [ ] No console warnings about React keys, deprecated props

**Interaction:**
- [ ] All clickable elements have hover state (cursor: pointer)
- [ ] All buttons have loading state during API calls
- [ ] All forms clear after successful submission
- [ ] Back/forward browser navigation works correctly
- [ ] Deep linking works (paste URL directly, should load correct page)
- [ ] Refresh on any page maintains state (doesn't redirect to home)

**Empty States:**
- [ ] Filter that returns 0 results shows "No data" message, not blank
- [ ] New user with no animals sees proper onboarding/empty state
- [ ] Search with no matches shows helpful message

**Accessibility:**
- [ ] Tab through all interactive elements on each page
- [ ] Enter/Space activates buttons
- [ ] Form labels are associated with inputs (click label focuses input)
- [ ] Screen reader can navigate sidebar (check ARIA roles)
- [ ] Color contrast passes WCAG AA (use Chrome Lighthouse audit)

---

## PHASE 3: PERFORMANCE TESTING

### 3.1 API Response Times

Measure with curl timing for each endpoint (target: < 200ms for reads, < 500ms for writes):

```bash
# Authenticate first and capture token
TOKEN=$(curl -s -X POST http://localhost:8000/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919900000001","otp":"123456"}' \
  -c cookies.txt | jq -r '.access_token // empty')

# Time critical endpoints
curl -w "\n%{time_total}s\n" -b cookies.txt http://localhost:8000/v1/admin/stats
curl -w "\n%{time_total}s\n" -b cookies.txt http://localhost:8000/v1/admin/charts/milk
curl -w "\n%{time_total}s\n" -b cookies.txt http://localhost:8000/v1/animals?limit=50
curl -w "\n%{time_total}s\n" -b cookies.txt http://localhost:8000/v1/health/alerts/map
curl -w "\n%{time_total}s\n" -b cookies.txt http://localhost:8000/v1/milk/daily-summary
curl -w "\n%{time_total}s\n" -b cookies.txt http://localhost:8000/v1/finance/summary
```

### 3.2 Database Query Performance

```sql
-- Enable query timing
\timing on

-- Check slow queries (simulate with EXPLAIN ANALYZE)
EXPLAIN ANALYZE SELECT * FROM animals WHERE user_id = '<farmer_uuid>' ORDER BY created_at DESC LIMIT 50;
EXPLAIN ANALYZE SELECT * FROM yield_logs WHERE animal_id = '<animal_uuid>' AND created_at > NOW() - INTERVAL '30 days';
EXPLAIN ANALYZE SELECT * FROM health_events WHERE risk_score >= 7 ORDER BY event_date DESC;
EXPLAIN ANALYZE SELECT u.id, u.name, COUNT(a.id) FROM users u LEFT JOIN animals a ON u.id = a.user_id GROUP BY u.id;

-- Check for missing indexes
SELECT relname AS table, seq_scan, idx_scan, seq_scan - idx_scan AS too_many_seq_scans
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan AND seq_scan > 100
ORDER BY too_many_seq_scans DESC;

-- Check table sizes
SELECT relname AS table, pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC;
```

### 3.3 N+1 Query Detection

With Docker logs or SQL echo enabled, perform these actions and count queries:

1. Load Admin Dashboard (should be < 5 queries)
2. Load Farmers page with 50 farmers (should be 1-2 queries, NOT 50+)
3. Load Animals with breed/species filter (should be 1 query)
4. Load Health alerts map (should be 1-2 queries)

```bash
# Enable SQL echo temporarily
docker compose exec api env SQL_ECHO=true uvicorn app.main:app --host 0.0.0.0 --port 8000
# Then check logs:
docker compose logs api --tail 100
```

### 3.4 Frontend Performance

Run Chrome Lighthouse on each page:

1. **Admin Dashboard**: Target scores - Performance > 80, Accessibility > 90, Best Practices > 90
2. **Milk Collection Intake**: Target scores - Performance > 85 (must be snappy for field use)
3. **Admin Farmers List**: Check bundle size, verify code splitting works

Check in Chrome DevTools:
- **Network tab**: No requests > 1MB, total page load < 3MB
- **Performance tab**: No layout shifts (CLS < 0.1)
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s

### 3.5 Concurrent Load Test

```bash
# Install Apache Bench or use curl
# Simulate 50 concurrent reads on dashboard stats
ab -n 200 -c 50 -H "Cookie: auth_token=<jwt>" http://localhost:8000/v1/admin/stats

# Simulate 20 concurrent milk record submissions
# (Use a script that sends valid POST requests)

# Check: No 500 errors, response time < 500ms at p95
# Check: Database connections don't exhaust (pool_size=10, max_overflow=20)
```

---

## PHASE 4: SECURITY AUDIT

### 4.1 OWASP Top 10 Checklist

| # | Vulnerability | Test | Expected |
|---|---------------|------|----------|
| A01 | Broken Access Control | Farmer accesses other farmer's animals via direct ID | 403 Forbidden |
| A02 | Cryptographic Failures | Check JWT secret length, bcrypt rounds | Secret >= 64 chars, bcrypt cost 12 |
| A03 | Injection | SQL in search fields, XSS in names | Sanitized/rejected |
| A04 | Insecure Design | Rate limit on OTP, max attempts | 5/hour, 3 attempts |
| A05 | Security Misconfiguration | CORS allows *, debug mode in prod | Origins whitelisted, debug off |
| A06 | Vulnerable Components | Check dependency CVEs | No critical CVEs |
| A07 | Auth Failures | Brute force OTP, session fixation | Rate limited, new session on login |
| A08 | Data Integrity | Tampered JWT accepted? | Rejected with 401 |
| A09 | Logging Failures | Failed logins logged? | Yes, with IP/timestamp |
| A10 | SSRF | Internal URLs in file upload/fetch | Rejected |

### 4.2 Specific Security Tests

**JWT Security:**
```bash
# Test with tampered JWT (change payload, keep signature)
# Test with JWT signed with different secret
# Test with expired JWT
# Test with "none" algorithm attack
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0..." http://localhost:8000/v1/auth/me
```

**CSRF Protection:**
```bash
# State-changing request WITHOUT CSRF token should be rejected
curl -X POST http://localhost:8000/v1/animals -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}' 
# Expected: 403 (CSRF validation failed)

# CRITICAL: Verify Bearer token doesn't bypass CSRF check
# (Known gap in middleware/csrf.py - any Bearer header skips CSRF)
```

**CORS Configuration:**
```bash
# Request from disallowed origin
curl -H "Origin: https://evil.com" -I http://localhost:8000/v1/animals
# Should NOT have Access-Control-Allow-Origin: https://evil.com
```

**Information Disclosure:**
```bash
# Check error responses don't leak stack traces
curl http://localhost:8000/v1/nonexistent
# Should be generic 404, no Python traceback

# Check different error messages for user enumeration
# "OTP not found" vs "OTP expired" vs "wrong OTP" should be SAME message
```

**Sensitive Data Exposure:**
- Verify Aadhaar numbers are masked in API responses (only last 4 digits)
- Verify phone numbers aren't exposed in farmer search without auth
- Verify JWT doesn't contain sensitive data in payload (decode and check)
- Verify no PII in URL parameters
- Verify no secrets in docker-compose.yml committed to git

### 4.3 Dependency Vulnerability Scan

```bash
# Python dependencies
cd packages/api && pip-audit  # or: safety check

# Node dependencies
cd packages/admin && pnpm audit
cd packages/collection && pnpm audit

# Docker image scan
docker scout cves pashuraksha-api:latest
```

### 4.4 DPDP Act 2023 Compliance (India Data Protection)

Since this handles farmer PII (Aadhaar, phone, location):
- [ ] Aadhaar stored as hash, not plaintext
- [ ] Phone numbers encrypted at rest (or justified why not)
- [ ] Data retention policy defined (how long are records kept?)
- [ ] Consent mechanism for data collection exists
- [ ] Data export capability for farmer (Right to Access)
- [ ] Data deletion capability (Right to Erasure)
- [ ] Audit trail for who accessed what PII

---

## PHASE 5: CODE QUALITY & STANDARDS

### 5.1 Backend Code Review Checklist

**File-by-File Audit:**

| File | Check | Issue |
|------|-------|-------|
| `config.py` | Secrets not hardcoded | .env has JWT_SECRET in repo |
| `database.py` | Pool config matches config.py | Hardcoded values override config |
| `middleware/csrf.py` | Bearer bypass is validated | Any Bearer token skips CSRF |
| `middleware/auth.py` | User cache invalidation | Stale permissions possible |
| `routers/auth.py` | OTP enumeration prevention | Different errors for different failures |
| `routers/milk_center.py` | Authorization on all endpoints | Missing role checks |
| `routers/health.py` | /alerts/map authorization | Public access to location data |
| `routers/finance.py` | Decimal precision | Float-to-Decimal conversion |
| `routers/animals.py` | Collision on Pashu Aadhaar | No retry on random ID collision |
| `models/*.py` | Soft deletes | No deleted_at column |
| `models/*.py` | Audit columns | No created_by/updated_by |

**Pattern Compliance:**
- [ ] All routers use dependency injection for auth
- [ ] All write endpoints validate input with Pydantic schemas
- [ ] All list endpoints have pagination (limit/offset)
- [ ] All queries scoped to current user (unless admin)
- [ ] All financial calculations use Decimal, not float
- [ ] No raw SQL queries (all through SQLAlchemy ORM)
- [ ] Consistent response models across endpoints
- [ ] Proper HTTP status codes (201 for create, 204 for delete)

### 5.2 Frontend Code Review Checklist

**Admin (Next.js):**
- [ ] Error boundary on all route segments
- [ ] Loading.tsx for route transitions
- [ ] No `any` types in TypeScript
- [ ] All API URLs from environment variables
- [ ] No hardcoded district/category lists (should come from API)
- [ ] Memoization on expensive components (React.memo, useMemo)
- [ ] Images optimized with next/image
- [ ] Metadata/SEO tags on pages

**Collection (Vite/React):**
- [ ] Error boundary exists (MISSING - needs adding)
- [ ] AuthGuard on all protected routes
- [ ] Form validation before submit
- [ ] Loading states on all async operations
- [ ] No console.log in production code
- [ ] Environment variables properly prefixed (VITE_)

**Common:**
- [ ] No API keys in frontend code
- [ ] CSRF token sent with mutations
- [ ] 401 responses trigger re-authentication
- [ ] Dates displayed in user's locale (IST for India)
- [ ] Numbers formatted with Indian numbering (lakhs/crores)
- [ ] Currency displayed as INR with proper symbol

### 5.3 Run Existing Test Suites

```bash
# Backend tests
cd packages/api && uv run pytest -v --tb=short

# Admin unit tests
cd packages/admin && pnpm test -- --watchAll=false

# E2E tests (requires running services)
cd e2e && npx playwright test

# Linting
cd packages/api && uv run ruff check . && uv run ruff format --check .
```

### 5.4 Missing Tests to Write

**Backend (Priority Order):**
1. Auth security: brute force, token tampering, session management
2. Authorization: every endpoint tested with wrong role/wrong user
3. Input validation: boundary values, injection payloads
4. Financial calculations: decimal precision, rounding
5. Milk collection: fat/SNF validation, rate calculation
6. Health triage: risk score calculation against disease_rules.py
7. Concurrent operations: two users editing same animal

**Frontend:**
1. Login flow: success, failure, OTP expiry, retry
2. Dashboard: data rendering, empty states, error states
3. Forms: validation, submission, error display
4. Navigation: sidebar, deep linking, back/forward
5. Cross-app: data created in Collection appears in Admin

---

## PHASE 6: PRODUCTION HARDENING FIXES

### 6.1 Critical Fixes (Must Do)

1. **Remove .env from git** - Add to .gitignore, rotate JWT_SECRET
2. **Add authorization to milk_center routes** - Verify user.role == "milk_center" or "admin"
3. **Add authorization to /health/alerts/map** - Require admin role
4. **Add authorization to /milk/daily-summary** - Require admin or milk_center role
5. **Fix CSRF bypass** - Validate Bearer token before exempting from CSRF
6. **Implement rate limiting middleware** - Currently configured but not enforced
7. **Add error boundary to Collection app** - App will white-screen on unhandled error
8. **Unify error messages in auth** - Same message for all OTP failures (prevent enumeration)

### 6.2 Important Fixes

9. **Add soft delete to animals, health_events, transactions** - `deleted_at` column
10. **Add audit columns** - `created_by`, `updated_by` on transactional tables
11. **Fix database.py pool config** - Use values from config.py, not hardcoded
12. **Add Decimal type for quantity_liters** - Currently Float, should be Numeric(10,2)
13. **Add structured audit logging** - Log auth failures, data access, mutations
14. **Add HSTS header** - `Strict-Transport-Security` in production
15. **Implement connection retry on API startup** - Handle DB not ready
16. **Add health check that verifies migration version** - /ready should check alembic

### 6.3 Nice-to-Have

17. Feature flags infrastructure
18. API versioning headers
19. Request/response compression (gzip)
20. Redis caching for dashboard stats
21. Database connection pooling with PgBouncer
22. Sentry/error tracking integration
23. OpenTelemetry tracing

---

## PHASE 7: DOCKER PRODUCTION CONFIGURATION

### 7.1 Docker Hardening

Verify/fix in docker-compose.yml:
- [ ] No default passwords in production compose
- [ ] Non-root user in Dockerfiles
- [ ] Multi-stage builds to minimize image size
- [ ] Health checks have appropriate intervals
- [ ] Resource limits are production-appropriate
- [ ] Logging driver configured (not just stdout)
- [ ] Restart policies set (`restart: unless-stopped`)
- [ ] Secrets via Docker secrets or env file (not inline)
- [ ] Network isolation (API can reach DB, frontends cannot)

### 7.2 Production Docker Compose Additions Needed

```yaml
# Items to add:
- Nginx reverse proxy with SSL termination
- Redis for caching and rate limiting
- Log aggregation (Loki or similar)
- Backup service for PostgreSQL
- Network segmentation (frontend, backend, database networks)
- Volume backup strategy
```

---

## PHASE 8: FINAL VERIFICATION CHECKLIST

### Smoke Test (Run After All Fixes)

1. [ ] `docker compose up -d` starts all services healthy
2. [ ] Admin login works, dashboard loads with data
3. [ ] Collection Center login works, can record milk
4. [ ] Milk recorded in Collection appears in Admin within 5 seconds
5. [ ] Farmer enrolled in Collection appears in Admin
6. [ ] All admin sidebar pages load without error
7. [ ] API /health and /ready return 200
8. [ ] No 500 errors in docker logs
9. [ ] No console errors in browser
10. [ ] Lighthouse Performance > 80 on all pages
11. [ ] `pnpm audit` shows no critical vulnerabilities
12. [ ] `ruff check .` passes with no errors
13. [ ] All existing tests pass
14. [ ] CORS rejects unauthorized origins
15. [ ] Rate limiting blocks excessive OTP requests

### Sign-Off Criteria

| Category | Pass Criteria |
|----------|--------------|
| **Functionality** | All CRUD operations work, cross-app data flows verified |
| **Security** | No OWASP Top 10 violations, auth/authz complete |
| **Performance** | API < 200ms p95, Frontend LCP < 2.5s |
| **Code Quality** | Linting passes, no any types, consistent patterns |
| **Data Integrity** | No orphaned records, FK constraints enforced |
| **Error Handling** | No white screens, all errors user-friendly |
| **Accessibility** | WCAG AA on all pages, keyboard navigation works |
| **Docker** | All services healthy, resource limits set, no default passwords |

---

## EXECUTION ORDER

```
Phase 0  -> Setup environment, start services
Phase 1  -> Backend API audit (can run in parallel with Phase 2)
Phase 2  -> Frontend UI E2E testing with Chrome
Phase 3  -> Performance benchmarks
Phase 4  -> Security audit
Phase 5  -> Code quality review and test gaps
Phase 6  -> Fix all findings from Phases 1-5
Phase 7  -> Docker production hardening
Phase 8  -> Final verification (re-run all checks post-fix)
```

Total estimated effort: This is a thorough production readiness audit covering 27 API endpoints, 3 frontend apps, 15+ pages, and ~45 database tables.
