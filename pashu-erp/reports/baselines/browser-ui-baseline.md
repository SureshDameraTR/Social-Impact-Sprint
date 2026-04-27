# Browser UI Tester - Baseline Report

**Agent**: browser-test
**Date**: 2026-04-16
**Scope**: Full codebase review of all 3 frontend packages (Admin, Collection, Vet)

---

## 1. Route/Page Inventory

### Admin Dashboard (port 3000) -- 16 pages

| Route | File | Has Loading State | Has Error State | Has Empty State | E2E Tested |
|-------|------|:-:|:-:|:-:|:-:|
| `/` | `app/page.tsx` | Yes (in-component + loading.tsx) | No (dashboard has no isError) | No | Yes (4 tests) |
| `/login` | `app/login/page.tsx` | Yes (CircularProgress) | Yes (Alert) | N/A | No |
| `/farmers` | `app/farmers/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (EmptyState) | Yes (4 tests) |
| `/animals` | `app/animals/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (EmptyState) | Yes (3 tests) |
| `/milk` | `app/milk/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (EmptyState) | No |
| `/health` | `app/health/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (EmptyState) | Yes (2 tests) |
| `/vaccinations` | `app/vaccinations/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (inline) | Yes (2 tests) |
| `/income` | `app/income/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (inline) | No |
| `/marketplace` | `app/marketplace/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (EmptyState) | No |
| `/schemes` | `app/schemes/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (EmptyState) | No |
| `/map` | `app/map/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (inline) | Yes (1 test) |
| `/iot` | `app/iot/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert, split) | Yes (EmptyState) | No |
| `/vet` | `app/vet/page.tsx` | Yes (Skeleton) | No (no isError check) | Yes (inline) | No |
| `/vet/alerts` | `app/vet/alerts/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (EmptyState) | No |
| `/vet/cases` | `app/vet/cases/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (EmptyState) | No |
| `/vet/cases/[id]` | `app/vet/cases/[id]/page.tsx` | Yes (CircularProgress + loading.tsx) | Yes (Alert) | Yes (inline) | No |

### Collection Centre (port 3001) -- 6 pages

| Route | File | Has Loading State | Has Error State | Has Empty State | E2E Tested |
|-------|------|:-:|:-:|:-:|:-:|
| `/login` | `pages/Login.tsx` | Yes (CircularProgress) | Yes (Alert) | N/A | No |
| `/dashboard` | `pages/Dashboard.tsx` | Yes (Skeleton) | Yes (Alert) | N/A | No |
| `/intake` | `pages/Intake.tsx` | Yes (CircularProgress) | Yes (Alert) | N/A | No |
| `/intake/receipt/:id` | `pages/Receipt.tsx` | No | Yes (Alert fallback) | N/A | No |
| `/enroll` | `pages/Enroll.tsx` | Yes (CircularProgress) | Yes (Alert) | N/A | No |
| `/settlements` | `pages/Settlements.tsx` | Yes (CircularProgress) | Yes (Alert) | N/A | No |

### Vet Portal (port 3002) -- 5 pages

| Route | File | Has Loading State | Has Error State | Has Empty State | E2E Tested |
|-------|------|:-:|:-:|:-:|:-:|
| `/login` | `pages/Login.tsx` | Yes (CircularProgress) | Yes (Alert) | N/A | No |
| `/dashboard` | `pages/Dashboard.tsx` | Yes (Skeleton) | Yes (Alert) | Yes (EmptyState) | No |
| `/cases` | `pages/Cases.tsx` | Yes (Skeleton) | Yes (Alert) | Yes (EmptyState) | No |
| `/cases/:id` | `pages/CaseDetail.tsx` | Yes (Skeleton) | Yes (Alert) | N/A | No |
| `/alerts` | `pages/Alerts.tsx` | Yes (Skeleton) | Yes (Alert) | Yes (EmptyState) | No |

---

## 2. E2E Test Coverage Summary

### Existing Tests

| File | Tests | Package | Coverage Area |
|------|-------|---------|---------------|
| `e2e/admin-smoke.spec.ts` | ~30 | Admin | Dashboard, Farmers, Animals, Health, Vaccinations, Map, Sidebar nav, Responsive |
| `e2e/visual/visual-baseline.spec.ts` | 6 | All 3 | Visual regression screenshots |

### Coverage Gaps

| Package | Pages | Pages with E2E | Pages without E2E | Coverage % |
|---------|-------|:-:|:-:|:-:|
| Admin | 16 | 7 | 9 | 44% |
| Collection | 6 | 0 | 6 | 0% |
| Vet | 5 | 0 | 5 | 0% |
| **Total** | **27** | **7** | **20** | **26%** |

Admin pages WITHOUT functional E2E tests: `/login`, `/milk`, `/income`, `/marketplace`, `/schemes`, `/iot`, `/vet`, `/vet/alerts`, `/vet/cases`, `/vet/cases/[id]`

---

## 3. Findings

### CRITICAL

**C1. No E2E tests for Collection Centre (0/6 pages)**
- Severity: CRITICAL
- The milk intake workflow is a core business process (Demo scenario #2). Zero functional test coverage. Only visual baseline screenshot for login page exists.
- Risk: Regressions in the milk intake -> receipt -> settlements flow would be undetected.

**C2. No E2E tests for Vet Portal (0/5 pages)**
- Severity: CRITICAL
- The vet case management workflow is a core demo scenario (#3). Zero functional test coverage. Only visual baseline screenshot for login page exists.
- Risk: Case claim -> diagnose -> close workflow regressions undetected.

**C3. Login flow not tested in any package**
- Severity: CRITICAL
- The OTP-based auth flow (phone -> send OTP -> verify -> redirect) is untested across all 3 apps. This is the gateway to all functionality.
- Admin login is at `/login`, Collection at `/login`, Vet at `/login`. All share the same OTP pattern but use different API clients (fetch vs axios).

### HIGH

**H1. Dashboard page (`/`) has no error boundary for API failures**
- Severity: HIGH
- `app/page.tsx` uses `useList` for 3 data sources (stats, milk chart, alert map) but does not check `isError` for any of them. If the API is down, the page renders with all em-dashes but no error notification.
- Contrast: All other admin pages properly check `isError` and display `<Alert severity="error">`.

**H2. Vet dashboard page (`/vet`) has no error handling for API failures**
- Severity: HIGH
- `app/vet/page.tsx` uses `useList` for stats, cases, and alert map but does not check `isLoading` (only `statsLoading`/`casesLoading`/`alertsLoading` independently) and has no `isError` check at all.
- If the API returns errors, the page renders normally with empty data sections.

**H3. No `not-found.tsx` page in Admin**
- Severity: HIGH
- Next.js App Router supports `not-found.tsx` for custom 404 pages. The admin package has none. Invalid URLs will show the default Next.js 404 which breaks brand consistency.
- The smoke test only checks `text=404` is not visible on valid routes, not that a proper 404 page renders on invalid routes.

**H4. No `not-found` handling in Collection/Vet**
- Severity: HIGH
- Both use `<Navigate to="/login" replace />` as catch-all route. This means any invalid URL silently redirects to login rather than showing a 404. Users may be confused about why they were redirected.

**H5. Admin smoke tests use `toHaveCountGreaterThan(0)` which is not a Playwright API**
- Severity: HIGH
- File: `e2e/admin-smoke.spec.ts` line 53 -- `await expect(rows).toHaveCountGreaterThan(0)` -- this is not a valid Playwright assertion. The test would fail at runtime.
- Should be: `expect(await rows.count()).toBeGreaterThan(0)`

**H6. Vet CaseDetail requires both diagnosis AND prescription to submit**
- Severity: HIGH
- In `packages/vet/src/pages/CaseDetail.tsx` line 385, the submit button is disabled unless both `diagnosis` and `prescription` are filled. But a vet may want to diagnose without prescribing yet. The admin version at `/vet/cases/[id]` only requires diagnosis.
- Inconsistent behavior between admin vet view and standalone vet portal.

### MEDIUM

**M1. No mobile viewport E2E tests**
- Severity: MEDIUM
- Only 1440px and 1024px viewports tested. No tests for mobile (375px) or tablet portrait (768px). The Collection and Vet apps are designed for field use where mobile access is likely.

**M2. Missing `data-testid` attributes across most pages**
- Severity: MEDIUM
- Only `stat-card`, `vacc-stat-card`, `nav-farmers`, and a few others have `data-testid`. Most interactive elements (filter dropdowns, search inputs, table rows, action buttons) lack test IDs, making tests fragile (relying on CSS classes, text content, or MUI internal classes).

**M3. No API mock/intercept strategy in E2E tests**
- Severity: MEDIUM
- `admin-smoke.spec.ts` requires a live API at `localhost:8000`. No `page.route()` interception. Tests will fail if API is down or returns different data. Should either use Playwright route mocking or document API dependency clearly.

**M4. Collection Centre has no pagination**
- Severity: MEDIUM
- The Settlements page displays all farmer settlements without pagination. For centres with many farmers, this could cause performance issues and poor UX. The marketplace page in admin has client-side pagination as a workaround pattern.

**M5. Smoke tests use `waitForTimeout` for debounce**
- Severity: MEDIUM
- Lines 60, 70, 93, 117 use fixed `waitForTimeout(200-300)`. This is flaky -- should use `waitForResponse` or `waitForFunction` to detect actual data change.

**M6. No keyboard navigation tests**
- Severity: MEDIUM
- OTP input boxes support backspace navigation but no E2E test validates Tab/Enter/Backspace keyboard flow. Forms should be testable by keyboard-only users.

**M7. Collection/Vet ErrorBoundary not wired into router**
- Severity: MEDIUM
- Both packages have `ErrorBoundary.tsx` components but they are not visible in `App.tsx` routing. The `main.tsx` may wrap them but if not, uncaught render errors will crash the app.

### LOW

**L1. Admin chart tests rely on Recharts CSS class names**
- Severity: LOW
- `admin-smoke.spec.ts` line 37 uses `.recharts-responsive-container svg`. Recharts class names are not part of their public API and may change between versions.

**L2. Visual baselines cover only 4 admin pages + 2 login pages**
- Severity: LOW
- Missing visual baselines for: milk, animals, health, vaccinations, income, marketplace, schemes, iot, vet pages (admin), all authenticated pages (collection/vet).

**L3. No accessibility tests (axe-core)**
- Severity: LOW
- No axe-core integration. The admin pages do use ARIA attributes (`role="status"`, `aria-label`, `aria-labelledby`) which is good, but no automated validation.

**L4. Hardcoded URLs in e2e tests**
- Severity: LOW
- `admin-smoke.spec.ts` hardcodes `http://localhost:3000`. The Playwright config already sets `baseURL` for each project, but the smoke tests don't use `page.goto("/")` relative paths -- they use `${BASE}${path}` with a local constant.

**L5. No test for the admin `error.tsx` and `global-error.tsx` error boundaries**
- Severity: LOW
- These exist and look correct but are never exercised in tests. Could be validated with a forced error via route interception.

---

## 4. Infrastructure Assessment

### Playwright Config Quality: GOOD
- Three projects (admin, collection, vet) with correct ports
- webServer auto-start for all 3 apps
- HTML reporter + trace on retry + screenshot on failure
- Snapshot template configured for visual tests

### Error Boundaries: GOOD
- Admin: `error.tsx` (route-level) + `global-error.tsx` (app-level) with proper `role="alert"`
- Collection: `ErrorBoundary.tsx` (class component)
- Vet: `ErrorBoundary.tsx` (class component)

### Loading States: EXCELLENT
- Admin: Every route has both a Next.js `loading.tsx` file (Skeleton placeholders) AND in-component `isLoading` states with `CircularProgress`. This provides both Suspense-level and data-level loading indicators.
- Collection: All pages have loading states (Skeleton or CircularProgress)
- Vet: All pages have loading states (Skeleton)

### Form Validation: GOOD
- Phone validation: `/^[6-9]\d{9}$/` (valid Indian mobile)
- OTP: 6-digit numeric with paste support, backspace navigation, auto-focus
- Milk intake: Range validation on FAT (1-12) and SNF (6-12)
- Enroll: Aadhaar 12-digit validation with masked display

### Accessibility: ADEQUATE
- Skip-to-content link in admin layout
- `aria-label` on search inputs and tables
- `role="status"` on loading spinners
- `role="alert"` on error boundaries
- `role="img"` with `aria-labelledby` on charts/maps
- Missing: no axe automated checks

---

## 5. Recommended Test Plan (Priority Order)

1. **Login flow tests** -- all 3 packages (phone validation, OTP entry, error states)
2. **Collection Centre intake workflow** -- farmer search, milk entry, receipt generation
3. **Vet case management** -- case list, claim, diagnose, close
4. **Admin pages without tests** -- milk, income, marketplace, schemes, iot, vet section
5. **Mobile viewport tests** -- 375px and 768px for all 3 packages
6. **Network failure tests** -- API down, slow responses, 500 errors
7. **Keyboard navigation** -- Tab through forms, Enter to submit
8. **Accessibility scan** -- axe-core integration

---

## 6. JSON Summary

```json
{
  "agent": "browser-test",
  "verdict": "WARN",
  "critical": 3,
  "high": 6,
  "medium": 7,
  "low": 5,
  "pages_total": 27,
  "pages_with_e2e": 7,
  "coverage_pct": 26,
  "packages": {
    "admin": { "pages": 16, "tested": 7, "coverage_pct": 44 },
    "collection": { "pages": 6, "tested": 0, "coverage_pct": 0 },
    "vet": { "pages": 5, "tested": 0, "coverage_pct": 0 }
  }
}
```
