# PashuRaksha ERP — Workspace Manifest

Single source of truth for all SDLC agents. When files move or new modules appear, update this file — agents reference it instead of hardcoding paths.

Last verified: 2026-04-14

## Packages

| Package | Path | Language | Framework | Port | Purpose |
|---------|------|----------|-----------|------|---------|
| API | `packages/api/` | Python 3.12 | FastAPI 0.115 | 8000 | Backend REST API |
| Admin | `packages/admin/` | TypeScript 5.4 | Next.js 14.2 + Refine + MUI | 3000 | District admin dashboard |
| Mobile | `packages/mobile/` | TypeScript 5.4 | Expo 52 + React Native Paper | 8081 | Farmer mobile app |
| Collection | `packages/collection/` | TypeScript 5.4 | Vite 5.4 + MUI (PWA) | 3001 | Milk collection centre |
| Vet | `packages/vet/` | TypeScript 5.5 | Vite 5.4 + MUI + Leaflet | 3002 | Veterinary field app |
| Mocks | `mocks/` | Python 3.10 | FastAPI | 8001 | Weather/registry/IoT/storage |

## Infrastructure

| Service | Container | Port | Image |
|---------|-----------|------|-------|
| PostgreSQL 16 | `db` | 5432 | postgres:16-alpine |
| FastAPI API | `api` | 8000 | Built from `packages/api/` |
| Mock Backends | `mock-backends` | 8001 | Built from `mocks/` |

Config: `docker-compose.yml`, `.env`, `.env.example`

## API Package — File Registry

### Models (25 ORM models) — `packages/api/app/models/`
| File | Table | Key Relations |
|------|-------|---------------|
| `user.py` | users | has_many: animals, health_events, yield_logs |
| `animal.py` | animals | belongs_to: user; has_many: health_events, yield_logs, vaccinations |
| `health.py` | health_events | belongs_to: animal, user |
| `milk.py` | yield_logs, milk_collection_records, milk_collection_centers | belongs_to: animal/center |
| `finance.py` | transactions | belongs_to: user |
| `marketplace.py` | marketplace_listings | belongs_to: user |
| `schemes.py` | govt_schemes, scheme_applications | application belongs_to: user, scheme |
| `medicine.py` | medicines, medicine_administrations | administration belongs_to: animal, medicine |
| `advisory.py` | advisory_tips | - |
| `ethno_vet.py` | ethno_vet_remedies | - |
| `feed.py` | feed_ingredients, feed_formulations | formulation has_many: ingredients |
| `alerts.py` | health_alerts | belongs_to: user (reporter) |
| `insurance.py` | insurance_policies, insurance_claims | claim belongs_to: policy |
| `reference.py` | reference data (market rates, breeds) | - |
| `shg.py` | self_help_groups, shg_members | member belongs_to: group, user |
| `weather.py` | weather_data | - |
| `vet.py` | vet_consultations | belongs_to: animal, user (vet) |
| `otp.py` | otp_requests | belongs_to: user (by phone) |
| `base.py` | - | Base class: UUID PK, created_at, updated_at, deleted_at |

### Routers (27 endpoints) — `packages/api/app/routers/`
| File | Prefix | Auth | Methods |
|------|--------|------|---------|
| `auth.py` | `/v1/auth` | None | POST send-otp, verify-otp |
| `animals.py` | `/v1/animals` | farmer/vet/admin | CRUD |
| `health.py` | `/v1/health` | farmer/vet | GET list, POST log |
| `milk.py` | `/v1/milk` | farmer | GET history, POST yield |
| `finance.py` | `/v1/finance` | farmer | GET summary, transactions |
| `shg.py` | `/v1/shg` | farmer/admin | CRUD groups, members |
| `schemes.py` | `/v1/schemes` | farmer/admin | GET list, POST apply |
| `marketplace.py` | `/v1/marketplace` | farmer | CRUD listings |
| `income.py` | `/v1/income` | farmer | GET summary |
| `admin.py` | `/v1/admin` | admin | GET stats, dashboard |
| `weather.py` | `/v1/weather` | farmer | GET forecast |
| `feed.py` | `/v1/feed` | farmer/vet | GET ingredients, POST calculate |
| `ethno_vet.py` | `/v1/ethno-vet` | farmer | GET remedies |
| `bharat_pashudhan.py` | `/v1/registry` | admin | GET lookup |
| `vaccination.py` | `/v1/vaccination` | farmer/vet | GET due, POST record |
| `insurance.py` | `/v1/insurance` | farmer | GET products, POST claim |
| `alerts.py` | `/v1/alerts` | farmer/vet | GET nearby, POST report |
| `medicine.py` | `/v1/medicine` | vet | CRUD medicines |
| `medicine_log.py` | `/v1/medicine-log` | farmer/vet | GET logs, POST administer |
| `milk_center.py` | `/v1/milk-center` | milk_center | CRUD records |
| `advisory.py` | `/v1/advisory` | farmer | GET tips |
| `onboarding.py` | `/v1/onboarding` | farmer | POST profile |
| `iot.py` | `/v1/iot` | farmer/admin | GET devices, telemetry |
| `map_points.py` | `/v1/map-points` | any | GET points |
| `users.py` | `/v1/users` | admin | CRUD users |
| `reference.py` | `/v1/reference` | any | GET breeds, rates |
| `files.py` | `/v1/files` | any | POST upload |
| `vet.py` | `/v1/vet` | vet | CRUD consultations |

### Schemas (19 Pydantic models) — `packages/api/app/schemas/`
`animals.py`, `health.py`, `milk.py`, `finance.py`, `marketplace.py`, `schemes.py`, `medicine.py`, `advisory.py`, `ethno_vet.py`, `feed.py`, `alerts.py`, `insurance.py`, `weather.py`, `shg.py`, `admin.py`, `income.py`, `auth.py`

**Gap**: Routers without dedicated schemas: `iot`, `map_points`, `onboarding`, `vaccination`, `milk_center`, `bharat_pashudhan`, `reference`, `files`, `vet`

### Services (13 business logic) — `packages/api/app/services/`
| File | Purpose |
|------|---------|
| `disease_rules.py` | Symptom → disease matching engine (55+ rules) |
| `vaccination_scheduler.py` | Species/age → vaccination schedule |
| `feed_calculator.py` | Nutritional requirements calculator |
| `market_rates.py` | Market rate lookup |
| `milk_pricing.py` | FAT/SNF-based pricing |
| `weather_service.py` | External weather API client |
| `bharat_pashudhan.py` | National registry client |
| `iot_service.py` | IoT gateway client |
| `storage_service.py` | File storage client |
| `errors.py` | Custom exception hierarchy |
| `otp/base.py` | OTP provider interface |
| `otp/sarvam.py` | Sarvam SMS provider |
| `otp/console.py` | Dev console OTP (logs to stdout) |

### Middleware — `packages/api/app/middleware/`
| File | Purpose |
|------|---------|
| `auth.py` | JWT extraction, user cache, role verification |
| `csrf.py` | Double-submit CSRF token validation |
| `request_logging.py` | Request ID injection, timing |

### Migrations — `packages/api/alembic/versions/`
8 versions: initial_schema → performance_indexes → otp_table → reference_data → float_to_numeric → audit_softdelete → gender_column → vet_consultations

### Config
| File | Purpose |
|------|---------|
| `app/main.py` | App factory, router mounting, CORS, security headers |
| `app/config.py` | Pydantic Settings (env vars) |
| `app/database.py` | AsyncSession + engine setup |
| `app/logging_config.py` | Structured JSON logging |
| `pyproject.toml` | Dependencies (18 core, 5 dev) |
| `alembic.ini` | Migration config |

## Admin Package — File Registry

### Pages — `packages/admin/src/app/`
| File | Route | Data Source |
|------|-------|-------------|
| `page.tsx` | `/` | `/v1/admin/stats` |
| `login/page.tsx` | `/login` | `/v1/auth/*` |
| `farmers/page.tsx` | `/farmers` | `/v1/users?role=farmer` |
| `animals/page.tsx` | `/animals` | `/v1/animals` |
| `milk/page.tsx` | `/milk` | `/v1/milk` |
| `vaccinations/page.tsx` | `/vaccinations` | `/v1/vaccination/due` |
| `health/page.tsx` | `/health` | `/v1/health` |
| `income/page.tsx` | `/income` | `/v1/income` |
| `marketplace/page.tsx` | `/marketplace` | `/v1/marketplace` |
| `schemes/page.tsx` | `/schemes` | `/v1/schemes` |
| `map/page.tsx` | `/map` | `/v1/map-points` |
| `iot/page.tsx` | `/iot` | `/v1/iot` |
| `vet/page.tsx` | `/vet` | `/v1/vet` |
| `vet/alerts/page.tsx` | `/vet/alerts` | `/v1/alerts` |
| `vet/cases/page.tsx` | `/vet/cases` | `/v1/vet` |
| `vet/cases/[id]/page.tsx` | `/vet/cases/:id` | `/v1/vet/:id` |

### Components — `packages/admin/src/components/`
`AdminSidebar.tsx`, `SpeciesChip.tsx`, `RiskBadge.tsx`, `StatCard.tsx`, `GISMap.tsx`, `EmptyState.tsx`

### Providers — `packages/admin/src/providers/`
`data-provider.ts` (Refine data binding), `auth-provider.ts` (JWT auth)

### Theme — `packages/admin/src/theme/`
`theme.ts` (MUI theme: primary #0d6b58), `EmotionCache.tsx`

### Tests — `packages/admin/src/__tests__/`
`components/RiskBadge.test.tsx`, `components/SpeciesChip.test.tsx`, `components/StatCard.test.tsx`, `pages/farmers.test.tsx`

## Mobile Package — File Registry

### Screens (26) — `packages/mobile/app/`
| File | Tab | Data Source |
|------|-----|-------------|
| `(tabs)/index.tsx` | Home | `/v1/admin/stats` |
| `(tabs)/milk.tsx` | Milk | `/v1/milk` |
| `(tabs)/health.tsx` | Health | `/v1/health` |
| `(tabs)/income.tsx` | Income | `/v1/income` |
| `(tabs)/sell.tsx` | Sell | `/v1/marketplace` |
| `(auth)/login.tsx` | - | `/v1/auth/*` |
| `animal/add.tsx` | - | POST `/v1/animals` |
| `animal/[id].tsx` | - | `/v1/animals/:id` |
| `vaccinations.tsx` | - | `/v1/vaccination` |
| `medicine-log.tsx` | - | `/v1/medicine-log` |
| `advisory.tsx` | - | `/v1/advisory` |
| `ethno-vet.tsx` | - | `/v1/ethno-vet` |
| `weather.tsx` | - | `/v1/weather` |
| `insurance.tsx` | - | `/v1/insurance` |
| `community-alerts.tsx` | - | `/v1/alerts` |
| `smart-farm.tsx` | - | `/v1/iot` |
| `pashu-aadhaar.tsx` | - | `/v1/registry` |
| `profile.tsx` | - | `/v1/users/me` |
| `my-consultations.tsx` | - | `/v1/vet` |
| `onboarding/*.tsx` | - | `/v1/onboarding` |

### Config — `packages/mobile/src/config/`
`api.ts` — Axios client (15s timeout, 3 retries, exponential backoff)

### i18n — `packages/mobile/src/i18n/`
`en.json`, `kn.json` (Kannada — primary), `hi.json` (Hindi — partial)

## Collection Package — File Registry

### Pages — `packages/collection/src/pages/`
`Login.tsx`, `Dashboard.tsx`, `Intake.tsx`, `Receipt.tsx`, `Enroll.tsx`, `Settlements.tsx`

### Components — `packages/collection/src/components/`
`NavBar.tsx`, `FarmerSearch.tsx`, `ShiftSelector.tsx`, `RatePreview.tsx`, `AuthGuard.tsx`, `ErrorBoundary.tsx`

### API Client — `packages/collection/src/api/`
`client.ts`, `auth.ts`, `milk.ts`

## Vet Package — File Registry

### Pages — `packages/vet/src/pages/`
`Login.tsx`, `Dashboard.tsx`, `Cases.tsx`, `CaseDetail.tsx`, `Alerts.tsx`

### Components — `packages/vet/src/components/`
`NavBar.tsx`, `StatCard.tsx`, `SpeciesChip.tsx`, `EmptyState.tsx`, `AuthGuard.tsx`, `ErrorBoundary.tsx`

### API Client — `packages/vet/src/api/`
`client.ts`, `auth.ts`, `vet.ts`

## Mock Backends — File Registry

### Routers — `mocks/routers/`
| File | Prefix | Purpose |
|------|--------|---------|
| `weather.py` | `/weather` | IMD weather forecast mock |
| `registry.py` | `/registry` | Bharat Pashudhan registry mock |
| `iot.py` | `/iot` | IoT device telemetry mock |
| `storage.py` | `/storage` | File upload/download mock |

### Data — `mocks/data/`
`karnataka_districts.json`, `breeds.json`, `sample_devices.json`

## Testing Infrastructure

| Layer | Tool | Location | Scope |
|-------|------|----------|-------|
| Unit (Python) | pytest | `packages/api/tests/` | Models, services, routers |
| Unit (JS) | Jest | `packages/admin/src/__tests__/` | Components, utils |
| Integration | pytest | `packages/api/tests/test_integration_e2e.py` | API workflows |
| E2E | Playwright | `e2e/admin-smoke.spec.ts` | Admin UI flows |
| Demo scenarios | pytest | `packages/api/tests/test_demo_scenarios.py` | 9 demo flows |

## Documentation

| File | Purpose |
|------|---------|
| `TESTING.md` | Testing strategy |
| `TESTING_PLAN.md` | Detailed test plan |
| `PERFORMANCE-AUDIT.md` | Performance analysis |
| `ACCESSIBILITY-AUDIT.md` | WCAG compliance |
| `PRODUCTION-READINESS-REVIEW.md` | Production checklist |
| `UI-AUDIT-REPORT.md` | UI/UX audit |
| `docs/plans/*.md` | Design documents |
| `demo/demo-script.md` | Demo walkthrough |

## Auth & Roles

| Role | Login | Capabilities |
|------|-------|-------------|
| farmer | OTP phone (+919900000001) | Animals, milk, health, income, marketplace |
| admin | OTP phone (+919900000002) | Dashboard, all data, user management |
| vet | OTP phone (+919900000003) | Cases, alerts, medicine, consultations |
| milk_center | OTP phone (+919900000004) | Collection records, settlements |

Dev OTP: `123456` (console provider, all environments)

## 9 Demo Scenarios

1. Farmer registers animal via Pashu Aadhaar
2. Daily milk recording + income tracking
3. Disease detection via symptom logging
4. Vaccination schedule + reminders
5. Government scheme discovery + application
6. Marketplace listing (buy/sell livestock)
7. Insurance claim with photo proof
8. Community health alert reporting
9. Admin dashboard overview
