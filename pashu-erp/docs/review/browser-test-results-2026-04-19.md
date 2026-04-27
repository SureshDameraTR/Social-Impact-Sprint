# PashuRaksha ERP — Browser Test Results

**Date**: 2026-04-19
**Method**: Playwright Python (headless Chromium) + OTP auth + screenshot capture + console/network monitoring
**Tester**: Automated (Claude Code + Playwright sync_api)

---

## Executive Summary

| App | Pages Tested | Pass | Fail | Warn | Issues |
|-----|:---:|:---:|:---:|:---:|--------|
| **Admin Dashboard** | 13 | 0 | 6 | 7 | Slow loads (5-19s), CORS blocking stats API, 6 pages stuck/blank |
| **Collection Centre** | 4 | 3 | 1 | 0 | Settlements page crashes (JS error) |
| **Vet Platform** | 3 | 2 | 0 | 1 | Dashboard slow (5.3s), otherwise healthy |
| **Mobile (Web)** | 4 | 4 | 0 | 0 | Login screen only — Expo web routing ignores cookie auth |

**Overall Verdict: PARTIAL PASS — Vet and Collection mostly functional; Admin has critical performance and data-loading issues; Mobile web untestable via cookie injection**

---

## 1. Admin Dashboard (localhost:3000)

### Per-Page Results

| Page | Status | Load (ms) | Rendered | Nav | Rows | Notes |
|------|:---:|---:|:---:|:---:|---:|-------|
| `/` (Dashboard) | WARN | 11,527 | Yes | Yes | 20 | Cards show "—" (no stats data), charts/map render |
| `/farmers` | WARN | 5,571 | Yes | Yes | 7 | Table with 6 farmers, search bar, pagination — **fully functional** |
| `/animals` | FAIL | timeout | No | No | 0 | Page.goto timed out at 15s |
| `/milk` | FAIL | 11,491 | No* | No* | 0 | Spinner visible; screenshot shows sidebar + table rendered (timing) |
| `/health` | WARN | 5,770 | Yes | Yes | 2 | Health alerts table rendered |
| `/vaccinations` | FAIL | 1,700 | No | No* | 0 | Stuck spinner; screenshot confirms sidebar but no content |
| `/schemes` | WARN | 11,564 | Yes | Yes | 6 | Government schemes table rendered |
| `/marketplace` | FAIL | 8,965 | No | No* | 0 | Spinner visible; content area blank |
| `/income` | WARN | 7,318 | Yes | Yes | 6 | Income analytics table rendered |
| `/map` | WARN | 15,163 | Yes | Yes | 0 | Leaflet map renders; CSP blocks layer images |
| `/iot` | FAIL | 13,847 | No | No* | 0 | Spinner visible; stuck loading |
| `/vet/cases` | FAIL | 4,461 | No* | No* | 0 | Screenshot shows table with 1 case (timing issue) |
| `/vet/alerts` | WARN | 19,261 | Yes | Yes | 2 | Alerts table rendered but very slow |

*\*Pages marked "No\*" appear to have content in screenshots but were in a loading state when the automated check ran (hydration/SSR delay).*

**Key observations from screenshots:**
- **Sidebar now renders on ALL pages** — major improvement vs. April 18 health check
- Dashboard cards show "—" instead of numbers because CORS blocks `GET /v1/admin/stats`
- Milk Collection page actually has full sidebar + table with date filters and milk records
- Vet Cases page shows 1 pending case (Lakshmi Devi, cattle, Emergency)
- Vaccinations and IoT genuinely stuck on spinners — likely API endpoint issues

### CRUD Tests

| Action | Result | Notes |
|--------|:---:|-------|
| Create Farmer | SKIP | No "Create" or "Add" button found on /farmers |
| Create Animal | SKIP | /animals page timed out before button search |

### Responsive Tests

| Viewport | Width | Hamburger Menu | Sidebar Collapsed |
|----------|:---:|:---:|:---:|
| Tablet | 768px | Yes | Yes (hidden) |
| Mobile | 375px | Yes | Yes (hidden) |

Responsive layout works correctly — hamburger menu appears, sidebar collapses, cards stack vertically.

### Console Errors (Admin)

| Error | Frequency | Severity |
|-------|:---:|---------|
| CORS: `Access-Control` blocking `localhost:8000/v1/admin/stats` from `:3000` | Every page | **CRITICAL** — Dashboard stats blank |
| Refine telemetry image blocked (CSP/network) | Every page | Low (cosmetic) |
| Leaflet layer images blocked by CSP | /map only | Medium — map missing layer toggle |
| `net::ERR_FAILED` on first load | / only | Low |

### Network Errors (Admin)

- `GET /v1/admin/stats` — CORS blocked (causes blank dashboard cards)
- `GET /v1/iot/device-types` — `net::ERR_ABORTED` on /vet/cases page
- Refine telemetry pings blocked across all pages (harmless)

---

## 2. Collection Centre (localhost:3001)

### Per-Page Results

| Page | Status | Load (ms) | Rendered | Nav | Rows | Notes |
|------|:---:|---:|:---:|:---:|---:|-------|
| `/dashboard` | FAIL | 3,013 | No | No | 0 | Screenshot shows full dashboard with KPI cards (0.0L, ₹0, 0 Farmers, 0.0% Fat, Morning/Evening shifts) — false negative from timing |
| `/intake` | PASS | 1,418 | Yes | No | 2 | Milk intake form loads correctly |
| `/settlements` | PASS* | 891 | Yes | No | 0 | **ErrorBoundary caught**: `s.total_liters.toFixed is not a function` — shows "Something went wrong" |
| `/enroll` | PASS | 802 | Yes | No | 2 | Farmer enrollment form loads |

*\*Settlements marked PASS by automated check (text rendered) but shows error boundary crash visually.*

**Key observations from screenshots:**
- Dashboard actually renders correctly with KPI cards and shift breakdown — the automated check ran before hydration completed
- Settlements page shows "Something went wrong. An unexpected error occurred." with Reload button
- Nav bar at top with Intake, Dashboard, Settlements tabs — working
- User identity shows "Manjunath Reddy" with logout icon

### CRUD Tests

| Action | Result | Inputs Found |
|--------|:---:|:---:|
| Enroll Farmer | PASS | 2+ form fields |
| Record Intake | PASS | 2+ form fields |

### Console Errors (Collection)

| Error | Page | Severity |
|-------|------|---------|
| `s.total_liters.toFixed is not a function` | /settlements | **HIGH** — page crashes |
| CSP `frame-ancestors` via `<meta>` ignored | All pages | Low (warning only) |

---

## 3. Vet Platform (localhost:3002)

### Per-Page Results

| Page | Status | Load (ms) | Rendered | Nav | Rows | Notes |
|------|:---:|---:|:---:|:---:|---:|-------|
| `/dashboard` | WARN | 5,287 | Yes | No | 10 | Welcome message, KPI cards (1 Pending, 0 Diagnosed, 5 Animals, 1 Alert), pending cases list |
| `/cases` | PASS | 1,158 | Yes | No | 3 | Cases table with tabs (Pending/In Review/Diagnosed/Closed) |
| `/alerts` | PASS | 1,469 | Yes | No | 2 | Alerts table rendered |

**Key observations from screenshots:**
- Dashboard shows "Welcome, Dr. Ramesh" with Mysore District context
- 1 pending case (cattle — Gowri, emergency, Lakshmi Devi) visible
- Top nav bar: Dashboard, Cases, Alerts — all functional
- User identity: "Dr. Ramesh" with logout icon

### CRUD Tests

| Action | Result | Notes |
|--------|:---:|-------|
| Create Case | SKIP | No "Create"/"Add"/"New" button found on /cases |

### Console Errors (Vet)

| Error | Page | Severity |
|-------|------|---------|
| MUI Tooltip on disabled button | /cases | Low (accessibility warning) |
| CSP `frame-ancestors` via `<meta>` | All pages | Low |

---

## 4. Mobile App — Web (localhost:8081)

### Per-Page Results

| Page | Status | Load (ms) | Rendered | Notes |
|------|:---:|---:|:---:|-------|
| `/` (Login) | PASS | 1,754 | Yes | Login screen with PashuRaksha branding, phone input, Send OTP button |
| `/animals` | PASS* | 540 | Yes | HTTP 404 — Expo web serves login fallback |
| `/health` | PASS* | 547 | Yes | HTTP 404 — same fallback |
| `/profile` | PASS* | 533 | Yes | HTTP 404 — same fallback |

*\*These routes return 404 because Expo web routing doesn't support direct URL navigation to authenticated screens. The token cookie injection doesn't trigger Expo's auth state — Expo uses in-memory/AsyncStorage auth, not cookies.*

**Key observation:** Mobile web cannot be tested via headless browser + cookie injection. It requires either:
1. Programmatic login through the login form (fill phone, submit, enter OTP)
2. Native device/emulator testing

---

## 5. Backend Errors (During Testing)

```
CRITICAL: SQLAlchemy concurrent session errors
```

| Error | Count | Severity |
|-------|:---:|---------|
| `InvalidRequestError: session provisioning new connection; concurrent ops not permitted` | 2 | **CRITICAL** |
| `IllegalStateChangeError: close() can't be called during _connection_for_bind()` | 2 | **CRITICAL** |
| `GC cleaning up non-checked-in connection` (connection pool leak) | 4 | **HIGH** |

**Root cause**: The API has a SQLAlchemy async session management bug — concurrent requests cause the session to attempt simultaneous operations, leading to connection pool leaks. The garbage collector is cleaning up leaked connections, which confirms the connection pool leak identified in the April 18 health check.

---

## 6. Comparison with April 18 Health Check

| Issue (April 18) | Status Now | Change |
|-------------------|-----------|--------|
| **BUG-001**: Missing `@mui/icons-material` | **Still present** (builds still fail, but dev servers work) | No change |
| **BUG-002**: Auth OTP returns 403 | **FIXED** — OTP works for all roles (web + mobile client_type) | IMPROVED |
| **BUG-003**: Admin sidebar not rendering | **FIXED** — sidebar renders on ALL pages with full navigation | IMPROVED |
| **BUG-004**: Collection auth broken (redirect to login) | **FIXED** — all pages accessible, nav working | IMPROVED |
| **BUG-005**: Vet auth broken (redirect to login) | **FIXED** — all pages accessible, data loading | IMPROVED |
| SQLAlchemy connection pool leak | **Still present** — GC warnings in backend logs | No change |
| Admin slow loads (15s first load) | **Still present** — 5-19s on most pages (Next.js dev mode) | No change |

**New issues found this session:**

| Bug | Severity | Description |
|-----|---------|-------------|
| **BUG-006**: CORS blocking `/v1/admin/stats` | CRITICAL | Dashboard KPI cards show "—" instead of numbers |
| **BUG-007**: Settlements JS crash | HIGH | `s.total_liters.toFixed is not a function` — page shows error boundary |
| **BUG-008**: Vaccinations page stuck spinner | HIGH | Never finishes loading — API endpoint may be hanging |
| **BUG-009**: IoT page stuck spinner | HIGH | Same pattern as Vaccinations |
| **BUG-010**: Animals page timeout | HIGH | Page.goto exceeds 15s timeout |
| **BUG-011**: Marketplace page blank | MEDIUM | Spinner visible but no content loads |
| **BUG-012**: Mobile web routes 404 | LOW | Expected — Expo web doesn't support direct URL routing |

---

## 7. Screenshots

All saved to `e2e/screenshots/`:

| File | Description |
|------|-------------|
| `admin_.png` | Dashboard — sidebar, cards (no stats), charts, disease map |
| `admin_farmers.png` | Farmers table — 6 rows, search, pagination |
| `admin_milk.png` | Milk collection — date filters, intake records table |
| `admin_health.png` | Health alerts table |
| `admin_schemes.png` | Government schemes table |
| `admin_income.png` | Income analytics table |
| `admin_map.png` | Leaflet map of Karnataka |
| `admin_vaccinations.png` | Stuck spinner |
| `admin_iot.png` | Stuck spinner |
| `admin_vet_cases.png` | Vet cases table (1 pending case) |
| `admin_vet_alerts.png` | Vet alerts table |
| `admin_responsive_tablet.png` | 768px — hamburger menu, cards 2-col |
| `admin_responsive_mobile.png` | 375px — hamburger menu, cards stacked |
| `collection_dashboard.png` | KPI cards, shift summary |
| `collection_intake.png` | Milk intake form |
| `collection_settlements.png` | Error boundary crash |
| `collection_enroll.png` | Farmer enrollment form |
| `collection_crud_enroll.png` | Enrollment form (CRUD test) |
| `collection_crud_intake.png` | Intake form (CRUD test) |
| `vet_dashboard.png` | Welcome, KPI cards, pending cases |
| `mobile_.png` | Login screen with OTP |

---

## 8. Recommended Actions (Priority Order)

1. **[P0] Fix CORS for `/v1/admin/stats`** — Admin dashboard stats are completely blank
2. **[P0] Fix Settlements `total_liters.toFixed`** — Page crashes; likely API returns string instead of number
3. **[P0] Fix SQLAlchemy session management** — Concurrent request handling causes connection pool leaks
4. **[P1] Debug Vaccinations endpoint** — Page never finishes loading (stuck spinner)
5. **[P1] Debug IoT page** — Same stuck spinner pattern
6. **[P1] Debug Animals page timeout** — 15s+ load time causes complete failure
7. **[P1] Debug Marketplace loading** — Spinner but no data
8. **[P2] Add `@mui/icons-material`** — Production builds still fail
9. **[P2] Optimize admin page load times** — Most pages >5s (Next.js dev mode JIT compilation)
10. **[P3] Add CRUD buttons** — Admin Farmers/Animals have no visible Create/Add buttons
11. **[P3] Add CRUD button to Vet Cases** — No way to create a new case from the UI

---

*Report generated by Playwright Python headless browser testing session, April 19, 2026*
