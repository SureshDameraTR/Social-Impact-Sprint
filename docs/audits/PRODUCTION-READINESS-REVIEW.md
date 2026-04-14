# PashuRaksha ERP — Production-Readiness Review

**Date**: 2026-04-08
**Reviewer**: Principal Software Architect (AI-Assisted)
**Scope**: Full monorepo — API, Admin Dashboard, Mobile App, DevOps/Infrastructure

---

## Table of Contents

- [Phase 1: Repository Map](#phase-1-repository-map)
- [Phase 2: Consolidated Findings Summary](#phase-2-consolidated-findings-summary)
- [Phase 3: Critical Findings (16)](#phase-3-critical-findings-16--ship-blockers)
- [Phase 4: High Findings (29)](#phase-4-high-findings-29--fix-before-next-release)
- [Phase 5: Medium Findings (37)](#phase-5-medium-findings-37--tech-debt)
- [Phase 6: Low Findings (21)](#phase-6-low-findings-21--nice-to-have)
- [Top 10 Actions Before Production](#top-10-actions-before-production)

---

## Phase 1: Repository Map

### Package Overview

| Package | Runtime | Framework | Language | Purpose |
|---------|---------|-----------|----------|---------|
| `packages/api` | Python 3.12 | FastAPI + SQLAlchemy 2 | Python | REST API, 21 routers, Alembic migrations |
| `packages/admin` | Node.js | Next.js + Refine + MUI | TypeScript | District admin dashboard, 11 pages |
| `packages/mobile` | React Native | Expo Router + Paper | TypeScript | Farmer mobile app, 25+ screens |
| Root | — | pnpm workspaces | — | Docker Compose, justfile orchestration |

### Key Directories

```
pashu-erp/
├── docker-compose.yml          # Orchestration (Postgres + API)
├── justfile                    # Task runner (dev, seed, reset-db, migrate)
├── pnpm-workspace.yaml         # Monorepo workspace config
├── .env.example                # Environment template
├── demo/                       # Demo scripts (verify-setup.sh, warmup.sh)
├── packages/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py         # App entry, CORS, router registration
│   │   │   ├── config.py       # Pydantic settings
│   │   │   ├── database.py     # SQLAlchemy async engine + session
│   │   │   ├── middleware/     # Auth middleware
│   │   │   ├── models/         # 14 SQLAlchemy models
│   │   │   ├── routers/        # 21 API routers
│   │   │   ├── schemas/        # 15 Pydantic schemas
│   │   │   ├── services/       # 7 business logic services
│   │   │   └── seed/           # Demo data seeder
│   │   ├── alembic/            # DB migrations
│   │   ├── tests/              # 1 test file (demo scenarios)
│   │   ├── Dockerfile          # Single-stage Python image
│   │   └── pyproject.toml      # Python deps (uv)
│   ├── admin/                  # Next.js admin dashboard
│   │   ├── src/app/            # 11 page routes
│   │   ├── src/components/     # 5 shared components
│   │   ├── src/providers/      # Auth + data providers
│   │   ├── src/theme/          # MUI theme
│   │   ├── src/utils/          # Formatters
│   │   └── next.config.js      # Next.js config
│   └── mobile/                 # Expo React Native app
│       ├── app/                # 25+ screens (file-based routing)
│       ├── src/components/     # 9 shared components
│       ├── src/config/         # API client + theme
│       ├── src/i18n/           # English + Kannada translations
│       └── src/services/       # Voice + Kannada parser
```

### Shared Code Strategy

**None.** Zero shared packages between mobile and admin. Data types, enums, API contracts, and theme tokens are fully duplicated across packages.

### Build/Test/Lint Commands

| Package | Build | Test | Lint |
|---------|-------|------|------|
| API | `uvicorn app.main:app` | `pytest` (against live server) | `ruff` (in dev deps) |
| Admin | `next build` | None configured | None configured |
| Mobile | `expo export` | `console.assert` tests (no framework) | None configured |

---

## Phase 2: Consolidated Findings Summary

| Severity | API | Admin | Mobile | DevOps | **Total** |
|----------|-----|-------|--------|--------|-----------|
| **Critical** | 4 | 3 | 4 | 5 | **16** |
| **High** | 7 | 8 | 7 | 7 | **29** |
| **Medium** | 9 | 10 | 10 | 8 | **37** |
| **Low** | 4 | 5 | 7 | 5 | **21** |
| **Total** | **24** | **26** | **28** | **25** | **93** |

---

## Phase 3: Critical Findings (16) — Ship Blockers

### C1. Hardcoded Mock OTP Bypasses All Authentication

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: OWASP A07:2021 — Identification and Authentication Failures
- **File(s)**: `packages/api/app/routers/auth.py:15`
- **Current state**: `MOCK_OTP = "123456"` is hardcoded and is the ONLY OTP validation. There is no real OTP generation or delivery. Any attacker can authenticate as any phone number by sending `"otp": "123456"`.
- **Recommended fix**: Implement a real OTP provider (e.g., Sarvam SMS, Twilio) with time-limited server-stored codes. Keep mock mode gated behind `settings.environment == "development"`.
- **Why it matters**: Complete authentication bypass. Any user account can be hijacked by knowing their phone number.

### C2. Admin Auto-Authenticates on Network Error

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: OWASP A07:2021 — Identification and Authentication Failures
- **File(s)**: `packages/admin/src/providers/auth-provider.ts:34-48`
- **Current state**: The `catch` block in `login()` catches ALL fetch errors (network failure, CORS, DNS) and responds by silently auto-logging the user in with a hardcoded `"demo-jwt-token"` and a hardcoded admin identity. Any network issue grants unrestricted access.
- **Recommended fix**: Remove the demo fallback entirely. Return `{ success: false }` from the catch block. Gate demo mode behind an explicit env flag (`NEXT_PUBLIC_DEMO_MODE`).
- **Why it matters**: Any user can gain district-admin access by simply disconnecting from the network or pointing at a dead API URL. Full authentication bypass.

### C3. Mobile Has No Auth Guard

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: OWASP A07:2021 — Identification and Authentication Failures
- **File(s)**: `packages/mobile/app/_layout.tsx:7-36`
- **Current state**: The root layout renders `(auth)` and `(tabs)` stacks but has no logic to check whether a user is authenticated. Any user can navigate directly to `/(tabs)` without logging in.
- **Recommended fix**: Add an auth context provider that reads `auth_token` from SecureStore on mount and conditionally renders auth vs tabs stacks (or uses `Redirect`).
- **Why it matters**: All app data and functionality is accessible without authentication. In a livestock management app handling financial data, this is a data privacy violation.

### C4. Mobile Stores Hardcoded Mock JWT Token

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: OWASP A07:2021 — Identification and Authentication Failures
- **File(s)**: `packages/mobile/app/(auth)/login.tsx:29`
- **Current state**: `await SecureStore.setItemAsync('auth_token', 'mock-jwt-token')` — the login flow stores a static mock token with no real OTP verification. No feature flag prevents this from shipping.
- **Recommended fix**: Gate mock auth behind `__DEV__` or `EXPO_PUBLIC_MOCK_AUTH` env var. Implement real OTP verification against the API before production.
- **Why it matters**: Anyone can "authenticate" — the app has zero actual security.

### C5. CORS Allows All Origins with Credentials

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: OWASP A05:2021 — Security Misconfiguration
- **File(s)**: `packages/api/app/main.py:37-43`
- **Current state**: `allow_origins=["*"]` combined with `allow_credentials=True`. Even without credentials, `*` origin allows any website to call the API.
- **Recommended fix**: Set `allow_origins` to an explicit list from a config variable (e.g., `settings.cors_origins`). Remove `allow_credentials=True` unless specifically needed.
- **Why it matters**: Cross-site request forgery vector. Any malicious website can make authenticated API calls.

### C6. Weak JWT Secret Committed to Repository

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: CWE-798 — Use of Hard-coded Credentials
- **File(s)**: `packages/api/app/config.py:6`, `packages/api/.env:2`
- **Current state**: `jwt_secret: str = "dev-secret-change-in-production"` as the default, and `.env` contains the same value. Both are committed to git.
- **Recommended fix**: Remove the default value (make it required with no default). Use a strong random secret (32+ bytes) injected via environment variable in production. Add `.env` to `.gitignore`.
- **Why it matters**: JWT tokens can be forged by anyone with repo access, granting arbitrary admin access.

### C7. Database Credentials in Source Code and .env

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: CWE-798 — Use of Hard-coded Credentials
- **File(s)**: `packages/api/app/config.py:5`, `packages/api/.env:1`, `docker-compose.yml:7-8`
- **Current state**: `database_url` has a hardcoded default with password `pashu_dev_2026`. The `.env` file is tracked in git with the same credentials.
- **Recommended fix**: Remove default DB URL. Inject via environment variable only. `git rm --cached packages/api/.env`. Rotate all exposed credentials.
- **Why it matters**: Database credentials exposed to anyone with repo access. Permanent in git history.

### C8. Hardcoded Credentials in alembic.ini

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: CWE-798 — Use of Hard-coded Credentials
- **File(s)**: `packages/api/alembic.ini:3`
- **Current state**: `sqlalchemy.url = postgresql+asyncpg://pashu:pashu_dev_2026@localhost:5432/pashuraksha` hardcoded. Although `alembic/env.py` overrides this at runtime, the INI file contains credentials in version control.
- **Recommended fix**: Set `sqlalchemy.url = ` (empty) in alembic.ini since env.py already overrides it.
- **Why it matters**: Credential leak in source control.

### C9. Admin Token Stored in localStorage (XSS-Vulnerable)

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: OWASP A07:2021 — Identification and Authentication Failures
- **File(s)**: `packages/admin/src/providers/auth-provider.ts:19`, `packages/admin/src/providers/data-provider.ts:6`
- **Current state**: JWT token and user identity stored via `localStorage.setItem("token", ...)`. The data provider reads it back and attaches it as a Bearer token.
- **Recommended fix**: Use httpOnly, Secure, SameSite cookies for token storage. This removes the token from JS reach entirely.
- **Why it matters**: Any XSS vulnerability (including from third-party libraries like Leaflet tiles, Recharts tooltips, or the CDN-loaded Leaflet CSS) can exfiltrate the auth token.

### C10. Hardcoded OTP Bypass in Demo Scripts

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: CWE-798 — Use of Hard-coded Credentials
- **File(s)**: `demo/verify-setup.sh:63`, `demo/warmup.sh:19,31`
- **Current state**: OTP `123456` is hardcoded and always accepted. No evidence of a separate production auth flow.
- **Recommended fix**: Ensure the hardcoded OTP is only accepted when `ENVIRONMENT=development`. Add a startup check that blocks `123456` OTP acceptance in production.
- **Why it matters**: If this code reaches production, any account can be taken over.

### C11. Hardcoded Database Credentials in docker-compose.yml

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: CWE-798 — Use of Hard-coded Credentials
- **File(s)**: `docker-compose.yml:7-8, 23-24`
- **Current state**: `POSTGRES_PASSWORD: pashu_dev_2026` and `JWT_SECRET: dev-secret-change-in-production` hardcoded in compose file committed to git.
- **Recommended fix**: Use `${POSTGRES_PASSWORD}` variable interpolation referencing a `.env` file. Never commit credentials.
- **Why it matters**: Anyone with repo access gets DB credentials and can forge JWTs.

### C12. `packages/api/.env` Tracked in Git

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: CWE-540 — Inclusion of Sensitive Information in Source Code
- **File(s)**: `packages/api/.env`
- **Current state**: Contains `DATABASE_URL` with password and `JWT_SECRET`. Git status shows this file as tracked (modified `M`).
- **Recommended fix**: `git rm --cached packages/api/.env`, add to `.gitignore`, rotate all exposed credentials.
- **Why it matters**: Secrets in git history are permanent unless force-pushed.

### C13. No Phone Number Validation on Mobile Login

- **Category**: Security / Input Validation
- **Severity**: Critical
- **Standard Violated**: OWASP A03:2021 — Injection
- **File(s)**: `packages/mobile/app/(auth)/login.tsx:17-23`
- **Current state**: Phone number has `maxLength={10}` but no regex validation. `handleSendOtp` sends the OTP regardless of input content (letters, special characters, etc.).
- **Recommended fix**: Add regex validation `/^[6-9]\d{9}$/` for Indian mobile numbers. Disable "Send OTP" until valid.
- **Why it matters**: Wasted API calls to SMS gateway; potential abuse of OTP sending endpoint (SMS bombing).

### C14. No React Error Boundary in Admin

- **Category**: Error Handling
- **Severity**: Critical
- **Standard Violated**: React Best Practices — Error Boundaries
- **File(s)**: `packages/admin/src/app/layout.tsx`
- **Current state**: No `ErrorBoundary` component wrapping route children. A single runtime error crashes the entire app to a white screen.
- **Recommended fix**: Add `global-error.tsx` and per-route `error.tsx` files (Next.js App Router convention). Wrap chart/map components in local error boundaries.
- **Why it matters**: A single map tile failure or malformed data point takes down the entire dashboard.

### C15. No Error Boundary in Mobile App

- **Category**: Error Handling
- **Severity**: Critical
- **Standard Violated**: React Best Practices — Error Boundaries
- **File(s)**: `packages/mobile/app/_layout.tsx:7-36`
- **Current state**: No React error boundary wraps the app. An unhandled exception crashes the entire app with a white screen.
- **Recommended fix**: Add an `ErrorBoundary` component wrapping `<PaperProvider>` that shows a friendly "Something went wrong" screen with a reload button.
- **Why it matters**: Rural users with limited tech literacy see a blank white screen and assume the app is broken permanently. High uninstall rate.

### C16. Hardcoded Admin Credentials in auth-provider.ts

- **Category**: Security
- **Severity**: Critical
- **Standard Violated**: CWE-798 — Use of Hard-coded Credentials
- **File(s)**: `packages/admin/src/providers/auth-provider.ts:7-8,19,36`
- **Current state**: `"demo-jwt-token"` stored in localStorage. Login defaults to `phone: "+919999900000"` and `otp: "123456"`.
- **Recommended fix**: Remove all hardcoded tokens and default credentials. Require real auth input.
- **Why it matters**: Predictable token values and default credentials enable trivial auth bypass.

---

## Phase 4: High Findings (29) — Fix Before Next Release

### API Backend (7)

#### H1. N+1 Query in Admin GIS Alert Markers

- **Category**: Database / Performance
- **Severity**: High
- **Standard Violated**: ORM Best Practices — Eager Loading
- **File(s)**: `packages/api/app/routers/admin.py:132-142`
- **Current state**: For each of up to 100 health events, two additional queries are made (one for Animal, one for User) inside a Python loop. 1 + 100 + 100 = 201 queries per call.
- **Recommended fix**: Use `select(HealthEvent).options(joinedload(HealthEvent.animal).joinedload(Animal.owner))`.
- **Why it matters**: Admin GIS endpoint will be extremely slow under load, potentially timing out.

#### H2. Admin Milk Chart Issues 30 Sequential Queries

- **Category**: Database / Performance
- **Severity**: High
- **Standard Violated**: SQL Best Practices — Batch Queries
- **File(s)**: `packages/api/app/routers/admin.py:91-105`
- **Current state**: `for i in range(30)` loop issues one SQL query per day. 30 sequential DB round-trips per API call.
- **Recommended fix**: Single query with `GROUP BY DATE(recorded_at)` and fill missing days in Python.
- **Why it matters**: Slow dashboard load. Under concurrent admin usage, this hammers the database.

#### H3. N+1 Query in Vaccination Due Endpoint

- **Category**: Database / Performance
- **Severity**: High
- **Standard Violated**: ORM Best Practices — Eager Loading
- **File(s)**: `packages/api/app/routers/vaccination.py:43-50`
- **Current state**: For each animal, a separate query fetches vaccinations. 50 animals = 51 queries.
- **Recommended fix**: Fetch all vaccinations for the user's animals in a single query using `IN` clause.
- **Why it matters**: Performance degrades linearly with herd size.

#### H4. No Authentication on Vaccination Endpoints

- **Category**: Security
- **Severity**: High
- **Standard Violated**: OWASP A01:2021 — Broken Access Control
- **File(s)**: `packages/api/app/routers/vaccination.py:27-33`
- **Current state**: `GET /v1/vaccinations/due/{user_id}` and `GET /v1/vaccinations/coverage/{village_code}` have no `Depends(get_current_user)`. Any unauthenticated caller can query any user's vaccination data.
- **Recommended fix**: Add `current_user: User = Depends(get_current_user)` and verify `user_id == current_user.id` or admin role.
- **Why it matters**: IDOR vulnerability. Any user's vaccination records can be enumerated.

#### H5. No Pagination on Any List Endpoint

- **Category**: API Design
- **Severity**: High
- **Standard Violated**: REST Best Practices — Pagination
- **File(s)**: `packages/api/app/routers/animals.py:52`, `health.py:65`, `milk.py:48`, `marketplace.py:84`, `income.py:120`
- **Current state**: All list endpoints return unbounded result sets.
- **Recommended fix**: Add `limit: int = Query(50, le=200)` and `offset: int = Query(0, ge=0)` parameters. Return total count.
- **Why it matters**: Memory exhaustion, slow responses, potential OOM kills for users with large datasets.

#### H6. Route Ordering Bug — `/vaccinations/due` Unreachable

- **Category**: API Design
- **Severity**: High
- **Standard Violated**: FastAPI Route Ordering
- **File(s)**: `packages/api/app/routers/health.py:121-143`
- **Current state**: `GET /vaccinations/{animal_id}` registered before `GET /vaccinations/due`. FastAPI matches in order, so `/vaccinations/due` is captured by `/{animal_id}` where `animal_id="due"`, failing UUID parsing.
- **Recommended fix**: Move `/vaccinations/due` route before `/{animal_id}`, or rename to `/vaccinations/upcoming`.
- **Why it matters**: The "due vaccinations" feature is broken — always returns 422 validation error.

#### H7. Onboarding Endpoint Silently Discards Data

- **Category**: Code Quality
- **Severity**: High
- **Standard Violated**: Data Integrity
- **File(s)**: `packages/api/app/routers/onboarding.py:30-57`
- **Current state**: `complete_onboarding` builds a preferences dict but never writes it to the database. User's preferences, location, and language are never persisted.
- **Recommended fix**: Set `current_user.preferences = preferences`, `current_user.location_district = body.district`, etc., then `await db.commit()`.
- **Why it matters**: Onboarding data is silently lost. Users must re-onboard every session.

### Admin Dashboard (8)

#### H8. Entire App is `"use client"` — No SSR/SSG

- **Category**: Architecture / Performance
- **Severity**: High
- **Standard Violated**: Next.js Best Practices — Server Components
- **File(s)**: `packages/admin/src/app/layout.tsx:1`
- **Current state**: `RootLayout` marked `"use client"`, forcing entire Next.js app into client-side rendering. Defeats Next.js core value proposition.
- **Recommended fix**: Move `Refine` provider setup into a separate `Providers` client component. Keep `RootLayout` as a server component.
- **Why it matters**: No SEO, no streaming HTML, slower first contentful paint, larger JS bundle.

#### H9. No Loading/Error UI for API Calls

- **Category**: Error Handling
- **Severity**: High
- **Standard Violated**: UX Best Practices — Loading States
- **File(s)**: All admin page files (`animals/page.tsx`, `farmers/page.tsx`, `health/page.tsx`, `milk/page.tsx`, `marketplace/page.tsx`, `schemes/page.tsx`)
- **Current state**: `useList()` is called but `isLoading` is only destructured in `farmers/page.tsx` (never used in JSX). `isError`/`error` never destructured in any page. All pages silently fall back to mock data.
- **Recommended fix**: Show skeleton/spinner for `isLoading`, error banner for `isError`, empty-state for zero results.
- **Why it matters**: Users cannot tell if they are seeing real data or stale mock data. Failed API calls are invisible.

#### H10. All Admin Data is Hardcoded Mock Arrays

- **Category**: Architecture
- **Severity**: High
- **Standard Violated**: Separation of Concerns
- **File(s)**: All admin page files
- **Current state**: Every page defines large inline mock data arrays (`mockAnimals`, `mockFarmers`, `mockAlerts`, etc.) used as fallbacks. Dashboard page uses ONLY mock data with no API call.
- **Recommended fix**: Extract mock data to `__mocks__/` or `fixtures/`. Gate behind `NEXT_PUBLIC_DEMO_MODE`. Dashboard should use `useList()`.
- **Why it matters**: Mock data bundled into production JS. Dashboard always shows fake numbers.

#### H11. Leaflet CSS Loaded from unpkg CDN

- **Category**: Performance / Security
- **Severity**: High
- **Standard Violated**: Supply Chain Security
- **File(s)**: `packages/admin/src/app/layout.tsx:29-32`
- **Current state**: `<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />` loaded on every page, even 9 of 11 that don't use maps.
- **Recommended fix**: Import Leaflet CSS inside GISMap component from npm package (`import 'leaflet/dist/leaflet.css'`).
- **Why it matters**: CDN outage/compromise breaks entire app layout. Unnecessary download on non-map pages. Supply chain risk.

#### H12. Hardcoded API URL

- **Category**: Architecture
- **Severity**: High
- **Standard Violated**: 12-Factor App — Config
- **File(s)**: `packages/admin/src/providers/auth-provider.ts:3`, `data-provider.ts:3`
- **Current state**: `const API_URL = "http://localhost:8000/v1"` hardcoded in both files.
- **Recommended fix**: Use `process.env.NEXT_PUBLIC_API_URL` with a fallback.
- **Why it matters**: Deploying to any non-local environment requires source code changes.

#### H13. No ARIA Landmarks or Skip Navigation

- **Category**: Accessibility
- **Severity**: High
- **Standard Violated**: WCAG 2.1 Level A — 1.3.1 Info and Relationships, 2.4.1 Bypass Blocks
- **File(s)**: `packages/admin/src/app/layout.tsx`, `src/components/AdminSidebar.tsx`
- **Current state**: No `<nav>` landmark on sidebar, no `role="main"` on content area, no skip-to-content link, no `aria-label` on search fields.
- **Recommended fix**: Wrap sidebar in `<nav aria-label="Main navigation">`. Add skip link. Add `aria-label` to all `<TextField>`.
- **Why it matters**: Screen reader users cannot navigate the dashboard.

#### H14. `require()` Inside React Component (GISMap)

- **Category**: Code Quality
- **Severity**: High
- **Standard Violated**: ESM Best Practices
- **File(s)**: `packages/admin/src/components/GISMap.tsx:43-50`
- **Current state**: `const { MapContainer, TileLayer, ... } = require("react-leaflet")` called inside render function. Runs on every render, bypasses TypeScript checking.
- **Recommended fix**: Use ESM dynamic imports at top of file or within `dynamic()` wrapper's factory function.
- **Why it matters**: No TypeScript checking on map components. Module resolution on every render cycle.

#### H15. No Content Security Policy Headers

- **Category**: Security
- **Severity**: High
- **Standard Violated**: OWASP A05:2021 — Security Misconfiguration
- **File(s)**: `packages/admin/next.config.js`
- **Current state**: No CSP headers configured. App loads from unpkg CDN and OpenStreetMap.
- **Recommended fix**: Add `headers()` in `next.config.js` with CSP whitelisting required domains.
- **Why it matters**: No defense against injected scripts. Compounds localStorage token storage risk.

### Mobile App (7)

#### H16. No Offline Support / Data Persistence

- **Category**: Architecture
- **Severity**: High
- **Standard Violated**: Mobile Best Practices — Offline-First
- **File(s)**: All mobile screen files, `src/config/api.ts`
- **Current state**: All data is hardcoded mock data in component files. No local database (SQLite/MMKV/AsyncStorage), no offline queue, no sync mechanism.
- **Recommended fix**: Implement offline-first architecture with MMKV or WatermelonDB. Queue mutations for sync.
- **Why it matters**: App is unusable without internet. Target users (rural Indian farmers) frequently have poor connectivity.

#### H17. API Client Has No Retry, Timeout, or Offline Detection

- **Category**: Error Handling
- **Severity**: High
- **Standard Violated**: Mobile Best Practices — Network Resilience
- **File(s)**: `packages/mobile/src/config/api.ts:20-54`
- **Current state**: Raw `fetch()` calls with no timeout, no retry logic, no network status check.
- **Recommended fix**: Add 15s timeout, exponential retry (3 attempts), network reachability check via `@react-native-community/netinfo`.
- **Why it matters**: API calls hang indefinitely on poor connections. Users see no feedback.

#### H18. Sarvam API Key Exposed in Client Bundle

- **Category**: Security
- **Severity**: High
- **Standard Violated**: OWASP A07:2021 — Identification and Authentication Failures
- **File(s)**: `packages/mobile/src/services/voice.ts:56`
- **Current state**: `process.env.EXPO_PUBLIC_SARVAM_API_KEY!` embedded in client-side bundle. Extractable from APK/IPA.
- **Recommended fix**: Proxy Sarvam API calls through your backend. Never embed third-party API keys in mobile bundles.
- **Why it matters**: API key can be extracted and abused for unlimited STT calls — financial liability.

#### H19. No Input Bounds on Sell/Milk Quantities

- **Category**: Security / Code Quality
- **Severity**: High
- **Standard Violated**: Input Validation Best Practices
- **File(s)**: `packages/mobile/app/(tabs)/milk.tsx:43-50`, `app/(tabs)/sell.tsx:33`
- **Current state**: Quantity input allows arbitrary decimal strings. `parseFloat()` used directly with no bounds checking. Negative and extremely large values accepted.
- **Recommended fix**: Clamp values (0.1-999), reject negative, limit decimal places, validate before submission.
- **Why it matters**: Corrupted data records. Potential financial reporting errors.

#### H20. Triage Messages Hardcoded in English

- **Category**: i18n
- **Severity**: High
- **Standard Violated**: Localization Best Practices
- **File(s)**: `packages/mobile/app/(tabs)/health.tsx:28-42`
- **Current state**: `getTriageResult()` returns hardcoded English strings like `'Possible FMD infection. Immediate vet attention needed.'`. Never passed through `t()`.
- **Recommended fix**: Use i18n keys: `t('health.triageFMD')`, etc.
- **Why it matters**: Kannada-speaking farmers receive critical health advice in English they may not understand.

#### H21. Emergency Vet Call Button is a No-Op

- **Category**: UX / Error Handling
- **Severity**: High
- **Standard Violated**: Functional Requirements
- **File(s)**: `packages/mobile/app/(tabs)/health.tsx:175-188`
- **Current state**: Emergency card has `onCallVet={() => {}}` (no-op). No `Linking.openURL('tel:...')` call.
- **Recommended fix**: Implement `Linking.openURL('tel:1962')` (India's animal helpline) or configurable vet phone number.
- **Why it matters**: In a livestock health emergency, the most prominent UI element does nothing. Animals could die.

#### H22. Missing `ios` Configuration in app.json

- **Category**: Architecture
- **Severity**: High
- **Standard Violated**: Expo/iOS Requirements
- **File(s)**: `packages/mobile/app.json`
- **Current state**: No `ios` block with `bundleIdentifier`, `supportsTablet`, etc. Only Android configuration exists.
- **Recommended fix**: Add `ios: { bundleIdentifier: "org.rdo.pashuraksha", supportsTablet: true }`.
- **Why it matters**: iOS builds will fail or use defaults. App Store submission requires explicit bundle ID.

### DevOps & Infrastructure (7)

#### H23. Zero CI/CD Pipeline

- **Category**: CI/CD
- **Severity**: High
- **Standard Violated**: DevOps Best Practices — Continuous Integration
- **File(s)**: N/A (`.github/workflows/` directory does not exist)
- **Current state**: No automated pipeline. No GitHub Actions, no GitLab CI, nothing.
- **Recommended fix**: Add at minimum: lint, test, build-docker, migration-check stages.
- **Why it matters**: Every merge to main is untested. Broken code ships silently.

#### H24. Docker Container Runs as Root

- **Category**: Security
- **Severity**: High
- **Standard Violated**: CIS Docker Benchmark 4.1
- **File(s)**: `packages/api/Dockerfile:1-13`
- **Current state**: No `USER` directive. Container runs as root.
- **Recommended fix**: Add `RUN adduser --disabled-password --gecos '' appuser` and `USER appuser` before CMD.
- **Why it matters**: Container escape vulnerability gives attacker root on host.

#### H25. No `.dockerignore` File

- **Category**: Security
- **Severity**: High
- **Standard Violated**: Docker Best Practices
- **File(s)**: `packages/api/.dockerignore` (missing)
- **Current state**: `COPY . .` copies everything including `.env`, `.git`, `__pycache__`, test files.
- **Recommended fix**: Create `.dockerignore` with `.env`, `.git`, `__pycache__`, `.venv`, `tests/`.
- **Why it matters**: Secrets baked into Docker image layers.

#### H26. No API Container Healthcheck

- **Category**: Monitoring
- **Severity**: High
- **Standard Violated**: Docker Best Practices — Health Checks
- **File(s)**: `docker-compose.yml:18-31`
- **Current state**: `db` service has healthcheck but `api` has none.
- **Recommended fix**: Add `healthcheck: test: ["CMD", "curl", "-f", "http://localhost:8000/health"]`.
- **Why it matters**: Docker/orchestrator cannot detect API crashes.

#### H27. Incomplete `.gitignore`

- **Category**: Configuration
- **Severity**: High
- **Standard Violated**: Git Best Practices
- **File(s)**: `.gitignore`
- **Current state**: Only covers `.dolt/`, `.db`, `.beads-credential-key`, `.env`. Missing: `node_modules/`, `.next/`, `.venv/`, `__pycache__/`, `.expo/`, `dist/`, `build/`.
- **Recommended fix**: Add standard ignores for Python, Node.js, Next.js, Expo.
- **Why it matters**: Git status shows `.next/` as untracked. Risk of committing large binary directories.

#### H28. Database Port Exposed to Host Network

- **Category**: Security
- **Severity**: High
- **Standard Violated**: Principle of Least Privilege
- **File(s)**: `docker-compose.yml:9`
- **Current state**: `ports: - "5432:5432"` exposes Postgres to host (and potentially LAN).
- **Recommended fix**: Bind to localhost: `"127.0.0.1:5432:5432"`. Remove entirely for production.
- **Why it matters**: Database accessible from any machine on the network. Combined with known credentials, this is direct DB access.

#### H29. No Multi-Stage Docker Build

- **Category**: Docker
- **Severity**: High
- **Standard Violated**: Docker Best Practices — Minimal Images
- **File(s)**: `packages/api/Dockerfile:1-13`
- **Current state**: Single-stage build includes `uv`, pip, dev dependencies, and build tools in final image.
- **Recommended fix**: Use multi-stage build: builder installs deps, final stage copies only venv/app. Pin base image digest.
- **Why it matters**: Larger attack surface, 2-3x image size, slower deployments.

---

## Phase 5: Medium Findings (37) — Tech Debt

### API Backend (9)

| # | Finding | File(s) | Standard |
|---|---------|---------|----------|
| M1 | No connection pool size configuration — uses SQLAlchemy defaults (pool_size=5) | `app/database.py:5-9` | Database Best Practices |
| M2 | Random ID generation uses non-crypto `random` module, no collision check | `app/routers/animals.py:28-29` | CWE-330 Insufficient Randomness |
| M3 | `product_type` accepts arbitrary strings, ignoring `ProductType` enum | `app/routers/marketplace.py:26` | Input Validation |
| M4 | SQL echo enabled in dev mode — logs query params to stdout | `app/database.py:7` | Data Privacy |
| M5 | No rate limiting on auth endpoints | `app/routers/auth.py:18-24` | OWASP A07 |
| M6 | Dockerfile installs dev dependencies in production image | `Dockerfile:6` | Docker Best Practices |
| M7 | Healthcheck returns healthy without verifying DB connectivity | `app/main.py:70-72` | Monitoring Best Practices |
| M8 | Financial amounts use `float` in some places, `Numeric` in others | `app/models/milk.py:80-83`, `app/routers/income.py:49-50` | IEEE 754 / Financial Computing |
| M9 | Missing database indexes on FK columns (`animal_id`, `user_id`) | `app/models/animal.py:37-39`, `health.py:27`, `milk.py:24-28`, `finance.py:31-32` | PostgreSQL Best Practices |

### Admin Dashboard (10)

| # | Finding | File(s) | Standard |
|---|---------|---------|----------|
| M10 | `theme.ts` has unnecessary `"use client"` directive — only exports constants | `src/theme/theme.ts:1` | Next.js Best Practices |
| M11 | Mock data regenerated with `Math.random()` — chart changes on every refresh | `src/app/page.tsx:25-33` | UX Consistency |
| M12 | God components: vaccinations (347 lines), iot (279 lines), marketplace (217 lines) | `vaccinations/page.tsx`, `iot/page.tsx`, `marketplace/page.tsx` | Single Responsibility Principle |
| M13 | Double pagination bug — FarmersPage sends pagination to API AND re-slices locally | `farmers/page.tsx:73-74` | DRY / Correctness |
| M14 | Duplicate icon definitions in layout.tsx AND AdminSidebar.tsx | `layout.tsx`, `AdminSidebar.tsx` | DRY Principle |
| M15 | Magic strings for resource names, risk levels, species throughout | Multiple pages | Constants / Enums |
| M16 | No Content Security Policy headers configured | `next.config.js` | OWASP A05 |
| M17 | Hardcoded date `"2026-04-08"` for "today's" milk total | `src/app/milk/page.tsx:84-86` | Temporal Coupling |
| M18 | No `React.memo` on StatCard, SpeciesChip, RiskBadge (rendered in table rows) | `StatCard.tsx`, `SpeciesChip.tsx`, `RiskBadge.tsx` | React Performance |
| M19 | Empty `experimental` block in next.config.js | `next.config.js:4-6` | Dead Code |

### Mobile App (10)

| # | Finding | File(s) | Standard |
|---|---------|---------|----------|
| M20 | Hardcoded colors bypass theme — two different greens used (`#1B6B4A` vs `#2E7D32`) | Almost every screen file | Design System Consistency |
| M21 | 13+ untranslated string sets (emergency line, profile, smart farm, credit card, etc.) | `health.tsx`, `income.tsx`, `profile.tsx`, `smart-farm.tsx`, `advisory.tsx` | i18n Best Practices |
| M22 | Duplicate `titleEn` property in advisory mock data | `app/advisory.tsx:44,48` | JavaScript Object Correctness |
| M23 | No loading/error states on data screens (only home has skeleton) | `health.tsx`, `income.tsx`, `sell.tsx`, `milk.tsx`, `vaccinations.tsx` | UX Best Practices |
| M24 | `ScrollView` + `.map()` used for long lists instead of `FlatList` | `income.tsx`, `sell.tsx`, `ethno-vet.tsx`, `vaccinations.tsx`, `community-alerts.tsx` | React Native Performance |
| M25 | No `accessibilityLabel` on most interactive elements | All screen files | WCAG / Mobile Accessibility |
| M26 | Missing `react-native-safe-area-context` — hardcoded `paddingTop` instead | `package.json` | iOS/Android Device Safety |
| M27 | No test framework configured — tests use `console.assert()` | `src/services/__tests__/kannada-parser.test.ts` | Testing Best Practices |
| M28 | `profile.tsx` name collision with `onboarding/profile.tsx` — both export `ProfileScreen` | `app/profile.tsx`, `app/onboarding/profile.tsx` | Naming Conventions |
| M29 | Feed calculator silently defaults to 300kg on invalid input — no validation error | `app/feed-calculator.tsx:61` | Input Validation |

### DevOps & Infrastructure (8)

| # | Finding | File(s) | Standard |
|---|---------|---------|----------|
| M30 | Source code volume-mounted into container (`./packages/api:/app`) | `docker-compose.yml:29-30` | Immutable Deployments |
| M31 | `--reload` flag on uvicorn in docker-compose (dev-only) | `docker-compose.yml:31` | Production Configuration |
| M32 | No rollback strategy for migrations — no backup-before-migrate | `alembic/versions/d22bbd14c60e_initial_schema.py:306-329` | Database Best Practices |
| M33 | Migration downgrade doesn't drop custom ENUM types | `alembic/versions/d22bbd14c60e_initial_schema.py:306-329` | PostgreSQL Migrations |
| M34 | No environment-specific config separation (single .env.example, no docker-compose.prod.yml) | `.env.example`, `docker-compose.yml` | 12-Factor App |
| M35 | No logging/monitoring configuration (no structured logging, no APM, no Sentry) | `docker-compose.yml`, `Dockerfile` | Observability Best Practices |
| M36 | No resource limits on containers (no mem_limit, no cpus) | `docker-compose.yml` | Container Best Practices |
| M37 | No Kubernetes/Helm configuration — Docker Compose only | N/A | Scalability |

---

## Phase 6: Low Findings (21) — Nice-to-Have

### API Backend (4)

| # | Finding | File(s) |
|---|---------|---------|
| L1 | Duplicate vaccination router registration in `health.py` and `vaccination.py` (overlapping `/v1/vaccinations` prefix) | `app/routers/health.py`, `vaccination.py` |
| L2 | Tests run against live server, not test database — not repeatable in CI | `tests/conftest.py:6`, `test_demo_scenarios.py:14` |
| L3 | Milk pricing service has dead code — first rate calculation immediately overwritten | `app/services/milk_pricing.py:54-62` |
| L4 | No graceful shutdown / lifespan management — no `engine.dispose()` on shutdown | `app/main.py` |

### Admin Dashboard (5)

| # | Finding | File(s) |
|---|---------|---------|
| L5 | Color-only status indicators — potential WCAG AA contrast failures (white on amber) | `RiskBadge.tsx`, `SpeciesChip.tsx`, `vaccinations/page.tsx` |
| L6 | Unused `useState` import in vaccinations page | `vaccinations/page.tsx:3` |
| L7 | `fmtDate` utility may return "Invalid Date" on null/malformed input | `src/utils/format.ts:9` |
| L8 | AdminSidebar hardcodes "Dr. Rajesh Kumar" instead of using `useGetIdentity()` | `AdminSidebar.tsx:232-258` |
| L9 | Array index used as React `key` in vaccination schedule table | `vaccinations/page.tsx:307` |

### Mobile App (7)

| # | Finding | File(s) |
|---|---------|---------|
| L10 | `react-native-gifted-charts` in dependencies but never imported | `package.json:23` |
| L11 | `@types/react` in dependencies instead of devDependencies | `package.json:13` |
| L12 | Animation memory leak in MicButton — `Animated.loop()` not fully cleaned up | `src/components/MicButton.tsx:27-46` |
| L13 | Mixed `TouchableOpacity` and `Pressable` across screens | `advisory.tsx`, `ethno-vet.tsx`, `onboarding/first-animal.tsx` |
| L14 | Kannada parser cannot handle compound numbers (e.g., "twenty-five") | `src/services/kannada-parser.ts:70-85` |
| L15 | No RTL layout support (fine for Kannada/English, blocks Hindi/Urdu/Arabic) | App-wide |
| L16 | Unused `SegmentedButtons` import in income screen | `app/(tabs)/income.tsx:3` |

### DevOps (5)

| # | Finding | File(s) |
|---|---------|---------|
| L17 | Base image `python:3.12-slim` not pinned to digest — not reproducible | `Dockerfile:1` |
| L18 | `pip install uv` not version-pinned | `Dockerfile:5` |
| L19 | Dev dependencies (pytest, ruff) installed in production image | `Dockerfile:8` |
| L20 | `sleep 3` in justfile for Postgres readiness instead of `pg_isready` loop | `justfile:36` |
| L21 | Postgres data volume not backed up — `docker compose down -v` destroys all data | `docker-compose.yml:33-34` |

---

## Top 10 Actions Before Production

| Priority | Action | Blast Radius | Effort |
|----------|--------|--------------|--------|
| **1** | **Implement real OTP** (Sarvam SMS or Twilio). Gate `123456` behind `ENV=development` only. | All 3 apps | Medium |
| **2** | **Rotate and externalize ALL secrets.** `git rm --cached` `.env` files. Use env vars / secrets manager. Never commit credentials. | API + DevOps | Low |
| **3** | **Fix CORS** to explicit origin list. Move admin tokens to httpOnly cookies. Add CSP headers. | API + Admin | Low |
| **4** | **Add auth guards** to mobile app route layout and unauthenticated API endpoints (vaccination, etc.). | Mobile + API | Low |
| **5** | **Add error boundaries** to both React apps (global-error.tsx for admin, ErrorBoundary wrapper for mobile). | Admin + Mobile | Low |
| **6** | **Fix N+1 queries** (admin GIS, milk chart, vaccination due) and **add pagination** to all list endpoints. | API | Medium |
| **7** | **Add DB indexes** on all FK columns (`animal_id`, `user_id` in yield_logs, health_events, transactions, sell_records). | API | Low |
| **8** | **Create CI/CD pipeline** — at minimum: lint + test + build-docker + migration-check. | DevOps | Medium |
| **9** | **Harden Dockerfile** — multi-stage build, non-root user, `.dockerignore`, pinned base image. | DevOps | Low |
| **10** | **Translate health triage messages** to Kannada. Wire up emergency vet call (`tel:1962`). Add offline data persistence. | Mobile | Medium |

---

## Architecture Observations

### Missing Patterns

| Pattern | Where Needed | Current State |
|---------|-------------|---------------|
| **Repository Pattern** | Data access across all API routers | Routers directly call SQLAlchemy. Business logic mixed with DB queries. |
| **Dependency Injection** | External services (weather, Sarvam, Bharat Pashudhan) | Services import config directly. Not testable without live APIs. |
| **Shared Types Package** | Between admin + mobile + API | Zero shared code. Species enums, product types, API contracts duplicated 3x. |
| **Error Handling Strategy** | All three packages | No consistent error type, no error reporting, no crash analytics. |
| **Offline-First / CQRS** | Mobile app | No local persistence, no mutation queue, no sync. |

### Dependency Direction Violations

- Admin `data-provider.ts` hardcodes API URL (presentation → infra coupling)
- Mobile screens contain mock data arrays (UI → data coupling)
- API routers contain business logic and DB queries (controller → model coupling)

---

*End of Production-Readiness Review*
