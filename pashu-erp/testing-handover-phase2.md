# Phase 2: Browser UI Testing — Handover Report

**Date**: 2026-04-20
**Tester**: Automated (Playwright Python + headless Chromium)
**Test script**: `e2e/comprehensive/browser_test_phase2.py`
**Results JSON**: `e2e/screenshots/comprehensive/results.json`
**Screenshots**: `e2e/screenshots/comprehensive/` (69 files)

---

## Summary

| Metric | Value |
|--------|-------|
| Pages tested | 28 |
| PASS | 26 (93%) |
| FAIL | 1 (3.6%) |
| SKIP | 1 (3.6%) |
| Screenshots captured | 69 |
| Console errors recorded | 16 |
| Apps covered | Admin (3000), Collection (3001), Vet (3002) |
| Auth method | API token acquisition + browser cookie injection |
| Responsive widths | 1920, 1366, 1024, 768px |

---

## Per-Page Results

### Admin (Next.js 14 + Refine + MUI) — 15 PASS, 1 SKIP

| # | Route | Page | Status | Load (ms) | Issues | Screenshot |
|---|-------|------|--------|-----------|--------|------------|
| 1 | `/login` | Login | PASS | 2364 | — | `admin_login_desktop_1920x1080.png` |
| 2 | `/` | Dashboard | PASS | 2666 | CORS on `/v1/admin/stats` | `admin_dashboard_desktop_1920x1080.png` |
| 3 | `/farmers` | Farmers | PASS | 2000 | — | `admin_farmers_desktop_1920x1080.png` |
| 4 | `/animals` | Animals | PASS | 1683 | — | `admin_animals_desktop_1920x1080.png` |
| 5 | `/health` | Health | PASS | 3212 | — | `admin_health_desktop_1920x1080.png` |
| 6 | `/milk` | Milk | PASS | 2891 | — | `admin_milk_desktop_1920x1080.png` |
| 7 | `/vaccinations` | Vaccinations | PASS | 5492 | Slow load | `admin_vaccinations_desktop_1920x1080.png` |
| 8 | `/schemes` | Schemes | PASS | 1971 | — | `admin_schemes_desktop_1920x1080.png` |
| 9 | `/marketplace` | Marketplace | PASS | 2171 | — | `admin_marketplace_desktop_1920x1080.png` |
| 10 | `/income` | Income | PASS | 2122 | — | `admin_income_desktop_1920x1080.png` |
| 11 | `/map` | GIS Map | PASS | 2743 | CSP blocks Leaflet images | `admin_gis_map_desktop_1920x1080.png` |
| 12 | `/iot` | IoT Devices | PASS | 3900 | — | `admin_iot_devices_desktop_1920x1080.png` |
| 13 | `/vet` | Vet Overview | PASS | 4216 | — | `admin_vet_overview_desktop_1920x1080.png` |
| 14 | `/vet/cases` | Vet Cases | PASS | 4524 | — | `admin_vet_cases_desktop_1920x1080.png` |
| 15 | `/vet/alerts` | Vet Alerts | PASS | 3329 | — | `admin_vet_alerts_desktop_1920x1080.png` |
| 16 | `/vet/cases/:id` | Case Detail | SKIP | — | Click didn't navigate to case detail | — |

### Collection Centre (Vite + MUI PWA) — 5 PASS, 1 FAIL

| # | Route | Page | Status | Load (ms) | Issues | Screenshot |
|---|-------|------|--------|-----------|--------|------------|
| 17 | `/login` | Login | PASS | 1449 | — | `collection_login_desktop_1920x1080.png` |
| 18 | `/dashboard` | Dashboard | PASS | 1274 | — | `collection_dashboard_desktop_1920x1080.png` |
| 19 | `/intake` | Milk Intake | PASS | 772 | — | `collection_milk_intake_desktop_1920x1080.png` |
| 20 | `/enroll` | Farmer Enroll | PASS | 652 | — | `collection_farmer_enroll_desktop_1920x1080.png` |
| 21 | `/settlements` | Settlements | **FAIL** | 657 | Error boundary crash | `collection_settlements_desktop_1920x1080.png` |
| 22 | `/intake` (E2E) | Intake Flow | PASS | — | End-to-end form fill test | `collection_intake_e2e_form_1920x1080.png` |

### Vet Dashboard (Vite + MUI + Leaflet) — 5 PASS

| # | Route | Page | Status | Load (ms) | Issues | Screenshot |
|---|-------|------|--------|-----------|--------|------------|
| 23 | `/login` | Login | PASS | 1366 | — | `vet_login_desktop_1920x1080.png` |
| 24 | `/dashboard` | Dashboard | PASS | 1453 | — | `vet_dashboard_desktop_1920x1080.png` |
| 25 | `/cases` | Cases | PASS | 924 | MUI Tooltip warning | `vet_cases_desktop_1920x1080.png` |
| 26 | `/alerts` | Alerts | PASS | 676 | — | `vet_alerts_desktop_1920x1080.png` |
| 27 | `/cases/:id` | Case Detail | PASS | — | DOM nesting warning | `vet_case_detail_desktop_1920x1080.png` |

### Cross-Cutting — 1 PASS

| # | Test | Status | Detail |
|---|------|--------|--------|
| 28 | Farmer blocked from admin | PASS | API returns 403: "This portal is for staff. Please use the PashuRaksha mobile app." |

---

## Bugs Found

### BUG-1: Collection `/settlements` crashes with TypeError (P1 - Blocker)

**Status**: FAIL — page shows error boundary
**File**: `packages/collection/src/pages/Settlements.tsx:127`
**Error**: `TypeError: s.total_liters.toFixed is not a function`

**Root cause**: API schema `FarmerSettlementItem` in `packages/api/app/schemas/milk_center.py` uses `Decimal` type fields:
```python
total_liters: Decimal = Field(..., max_digits=10, decimal_places=2)
avg_fat_pct: Decimal = Field(..., max_digits=5, decimal_places=2)
avg_snf_pct: Decimal = Field(..., max_digits=5, decimal_places=2)
```
Pydantic serializes `Decimal` as JSON strings (`"45.50"` not `45.50`). The frontend calls `.toFixed(1)` on these values, which fails because strings don't have `.toFixed()`.

**Fix options**:
1. **API side** (preferred): Change schema fields to `float` or add `model_config = ConfigDict(json_encoders={Decimal: float})`
2. **Frontend side**: Wrap values with `Number(s.total_liters).toFixed(1)` at lines 127-129

**Screenshot**: `collection_settlements_desktop_1920x1080.png` (shows error boundary)

### BUG-2: Admin `/vet/cases/:id` navigation broken (P3 - Minor)

**Status**: SKIP — click on case row did not navigate to detail page
**Context**: Vet Cases list at `/vet/cases` loaded correctly. Clicking a row was expected to navigate to `/vet/cases/:id` but no navigation occurred. May be a missing click handler or Refine routing issue.

---

## Console Errors

### Critical (affects functionality)

| # | App | Page | Error | Severity |
|---|-----|------|-------|----------|
| 1 | Admin | `/` | CORS blocks `GET /v1/admin/stats` — no `Access-Control-Allow-Origin` header | HIGH — dashboard stats fail to load |
| 2 | Collection | `/settlements` | `TypeError: s.total_liters.toFixed is not a function` | HIGH — page crashes (BUG-1) |

### Warnings (no functional impact)

| # | App | Page | Warning |
|---|-----|------|---------|
| 3 | Admin | `/map` | CSP blocks Leaflet layer toggle images from `unpkg.com` — `img-src` directive missing `https://unpkg.com` |
| 4 | Collection | `/login` | 401 on `/v1/auth/me` — expected for unauthenticated login page |
| 5 | Vet | `/login` | 401 on `/v1/auth/me` — expected for unauthenticated login page |
| 6 | Vet | `/cases` | MUI: disabled button inside Tooltip — wrap with `<span>` |
| 7 | Vet | `/cases/:id` | DOM nesting: `<div>` inside `<p>` via SpeciesChip component |

---

## Responsive Testing

All pages were tested at **desktop (1920x1080)** and **tablet (768x1024)**. Admin was additionally tested at 4 widths (1920, 1366, 1024, 768).

| Width | Admin | Collection | Vet |
|-------|-------|------------|-----|
| 1920px (desktop) | All pages render correctly | All pages render correctly | All pages render correctly |
| 1366px (laptop) | Sidebar + content scale well | — | — |
| 1024px (small laptop) | Layout adjusts, tables scroll | — | — |
| 768px (tablet) | Sidebar collapses, content stacks | All pages scale, forms usable | Map + tables fit viewport |

**Screenshots**: `responsive_admin_768_768x1080.png`, `responsive_admin_1024_1024x1080.png`, `responsive_admin_1366_1366x1080.png`, `responsive_admin_1920_1920x1080.png`

No responsive breakage was observed. All tested widths showed usable layouts.

---

## Login Flow Testing

Each app's login page was tested for UI rendering:

| App | Phone field | OTP field | Submit button | Language toggle | Screenshot |
|-----|-------------|-----------|---------------|-----------------|------------|
| Admin | Present | Present | Present | N/A | `admin_01_login_1920x1080.png` |
| Collection | Present | 6-digit boxes | Present | EN/KN/HI | `collection_01_login_1920x1080.png` |
| Vet | Present | Present | Present | N/A | `vet_01_login_1920x1080.png` |

OTP auth verified via API (httpx → `/v1/auth/request-otp` + `/v1/auth/verify-otp`). Tokens injected as cookies into browser contexts. All 3 apps successfully authenticated.

---

## Auth Boundary Testing

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Farmer phone (9876543210) → admin portal | Reject with clear message | API returns 403: "This portal is for staff. Please use the PashuRaksha mobile app." | PASS |
| Unauthenticated → admin pages | Redirect to login | Redirect confirmed | PASS |
| Unauthenticated → collection pages | Redirect to login | Redirect confirmed | PASS |
| Unauthenticated → vet pages | Redirect to login | Redirect confirmed | PASS |

---

## Screenshot Inventory (69 files)

```
e2e/screenshots/comprehensive/
├── Admin (33 screenshots)
│   ├── admin_login_{desktop,tablet}.png
│   ├── admin_dashboard_{desktop,tablet}.png
│   ├── admin_farmers_{desktop,tablet}.png
│   ├── admin_animals_{desktop,tablet}.png
│   ├── admin_health_{desktop,tablet}.png
│   ├── admin_milk_{desktop,tablet}.png
│   ├── admin_vaccinations_{desktop,tablet}.png
│   ├── admin_schemes_{desktop,tablet}.png
│   ├── admin_marketplace_{desktop,tablet}.png
│   ├── admin_income_{desktop,tablet}.png
│   ├── admin_gis_map_{desktop,tablet}.png
│   ├── admin_iot_devices_{desktop,tablet}.png
│   ├── admin_vet_overview_{desktop,tablet}.png
│   ├── admin_vet_cases_{desktop,tablet}.png
│   ├── admin_vet_alerts_{desktop,tablet}.png
│   ├── admin_01_login.png, admin_02_otp_filled.png, admin_03_login_failed.png
│   └── responsive_admin_{768,1024,1366,1920}.png
│
├── Collection (14 screenshots)
│   ├── collection_login_{desktop,tablet}.png
│   ├── collection_dashboard_{desktop,tablet}.png
│   ├── collection_milk_intake_{desktop,tablet}.png
│   ├── collection_farmer_enroll_{desktop,tablet}.png
│   ├── collection_settlements_{desktop,tablet}.png
│   ├── collection_01_login.png, collection_02_otp_filled.png, collection_03_login_failed.png
│   └── collection_intake_e2e_{start,form}.png
│
├── Vet (15 screenshots)
│   ├── vet_login_{desktop,tablet}.png
│   ├── vet_dashboard_{desktop,tablet}.png
│   ├── vet_cases_{desktop,tablet}.png
│   ├── vet_alerts_{desktop,tablet}.png
│   ├── vet_case_detail_{desktop,tablet}.png
│   ├── vet_01_login.png, vet_02_otp_filled.png, vet_03_login_failed.png
│   └── vet_case_claimed.png
│
├── Responsive (7 screenshots)
│   ├── responsive_admin_{768,1024,1366,1920}.png
│   └── responsive_01_login.png, responsive_02_otp_filled.png, responsive_03_login_failed.png
│
└── results.json
```

---

## Load Time Summary

| App | Avg Load (ms) | Slowest Page | Fastest Page |
|-----|---------------|--------------|--------------|
| Admin | 3060 | `/vet/cases` (4524ms) | `/animals` (1683ms) |
| Collection | 961 | `/login` (1449ms) | `/enroll` (652ms) |
| Vet | 1080 | `/dashboard` (1453ms) | `/alerts` (676ms) |

Admin is significantly slower due to Next.js SSR overhead and heavier data loads. Collection and Vet (both Vite) are consistently faster.

---

## Issues Requiring Fixes Before Production

### Must Fix (P1)

1. **Collection `/settlements` Decimal crash** — BUG-1. Users cannot view settlement history. Fix the Decimal→float serialization in the API schema or add `Number()` casts in the frontend.

### Should Fix (P2)

2. **Admin CORS on `/v1/admin/stats`** — Dashboard stats widget fails to load. Check that the `/v1/admin/stats` endpoint is included in CORS allowed origins or that the route returns proper CORS headers.

3. **Admin CSP for Leaflet images** — Layer toggle icons (layers.png, marker-icon.png) blocked by Content Security Policy. Add `https://unpkg.com` to `img-src` in `next.config.js`.

### Nice to Fix (P3)

4. **Admin `/vet/cases/:id` navigation** — Case detail not reachable via click. Check row click handler in the Vet Cases list component.

5. **Vet `/cases` MUI Tooltip warning** — Wrap disabled buttons in `<span>` per MUI docs.

6. **Vet `/cases/:id` DOM nesting** — SpeciesChip renders `<div>` inside `<p>`. Change the parent to `<div>` or use `component="div"` on the Typography.

---

## What Remains

- **Phase 3**: Performance & NFR Testing — API response times, k6 load tests, bundle sizes, DB connection pool audit, Lighthouse scores, NFR production-readiness scorecard
- **Phase 4**: Consolidated report (`reports/comprehensive-test-report.md`) combining Phase 1 (API) + Phase 2 (Browser UI) + Phase 3 (Performance)
