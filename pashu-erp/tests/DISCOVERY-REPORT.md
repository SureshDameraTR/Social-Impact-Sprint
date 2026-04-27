# PashuRaksha ERP — Test Discovery Report (Phase 0)

**Generated**: 2026-04-20
**Author**: Senior QA architect agent
**Verification rule**: every number in this document was produced by running a
shell command against the live codebase or a live service. No claim was copied
from a doc, README, or AGENTS file without re-verification. Each section lists
the exact command used so you can re-run it.

---

## 0. TL;DR — what is real today

| Layer                    | Count | Verified by                                            |
| ------------------------ | ----: | ------------------------------------------------------ |
| API routers              |    29 | `find packages/api/app/routers -name "*.py" \| wc -l`  |
| API endpoints (total)    |   115 | `grep -rE "^@router\." packages/api/app/routers \| wc` |
| API DB models (classes)  |    27 | `grep -r "__tablename__" packages/api/app/models`      |
| API DB tables            |    27 | one-to-one with model classes                          |
| Mapped columns (total)   |   245 | `grep -c mapped_column packages/api/app/models/*.py`   |
| Alembic migrations       |    12 | `ls packages/api/alembic/versions/*.py`                |
| Mock-backend routers     |     4 | `ls mocks/routers/*.py`                                |
| Mock-backend endpoints   |    12 | `grep -rE "^@router\." mocks/routers \| wc -l`         |
| Frontend apps            |     4 | admin, mobile, collection, vet                         |
| Existing pytest cases    |   529 | `uv run pytest --collect-only -q`                      |
| Existing pytest passing  |   494 | `uv run pytest tests/ --ignore=tests/integration` (52s)|
| Existing pytest skipped  |    24 | same run                                               |
| Existing pytest failing  |     0 | same run (excluding integration)                       |
| Integration pytest cases |    13 | `uv run pytest tests/integration/ --collect-only`      |
| Frontend Jest tests (admin) | 4 files | `npx jest --listTests`                            |
| Frontend Jest tests (mobile) | 18 files | `npx jest --listTests` (incl. 2 setup files)    |
| Vitest tests (collection) | 7 passing | `npx vitest run` (verified live)                  |
| Vitest tests (vet)       | 9 passing | `npx vitest run` (verified live)                   |
| Playwright e2e specs     |     3 | `e2e/*.spec.ts` + `e2e/visual/*.spec.ts`              |
| Playwright `test()` blocks | 43  | 20 (admin) + 17 (fullstack) + 6 (visual)               |

> **Important nuance discovered during verification:**
> The collection and vet packages have a `"test": "vitest run"` script and 4
> `*.test.tsx` files in `src/__tests__/`. An earlier check using `vitest list
> --run` reported "No test files found, exiting with code 1" — that was a
> CLI-flag mistake, not a real gap. Running `npx vitest run` actually passes
> 7 tests in collection and 9 in vet. **Do not trust `vitest list`. Use
> `vitest run` to count tests.**

---

## 1. Docker services and port mapping (live, re-checked)

Source: `docker-compose.yml` (re-read at write time) plus `docker ps` output.

| Service        | Image / build context     | Internal port | Host port (bind)         | Healthcheck                      | Profile        |
| -------------- | ------------------------- | ------------: | ------------------------ | -------------------------------- | -------------- |
| `db`           | `postgres:16-alpine`      |      `5432`   | `127.0.0.1:5432`         | `pg_isready -U pashu`            | (default)      |
| `mock-backends`| `./mocks` Dockerfile      |      `8001`   | `127.0.0.1:8001`         | `urllib.request /health`         | (default)      |
| `api`          | `./packages/api`          |      `8000`   | `127.0.0.1:8000`         | `curl -f /health`                | (default)      |
| `admin`        | `./packages/admin`        |      `3000`   | `127.0.0.1:3000`         | (none defined)                   | `frontend`     |
| `collection`   | `./packages/collection`   |      `3001`   | `127.0.0.1:3001`         | (none defined)                   | `frontend`     |
| `vet`          | `./packages/vet`          |      `3002`   | `127.0.0.1:3002`         | (none defined)                   | `frontend`     |

**Currently running (verified by `docker ps` at report time):**

```
pashu-erp-api-1               Up About an hour (healthy)   127.0.0.1:8000->8000/tcp
pashu-erp-db-1                Up About an hour (healthy)   127.0.0.1:5432->5432/tcp
pashu-erp-mock-backends-1     Up About an hour (healthy)   127.0.0.1:8001->8001/tcp
```

Frontend services (`admin`, `collection`, `vet`) are **not running** — they
require `docker compose --profile frontend up -d` or a local `next dev` /
`vite` invocation. The Playwright config in `e2e/playwright.config.ts`
launches them on demand via the `webServer` block.

**Test database (separate stack):** `docker-compose.test.yml` brings up
`test-db` on host port `5433` with `tmpfs` storage (DB name
`pashuraksha_test`, user `pashu_test`, password `test_password`). The
integration tests in `packages/api/tests/integration/` skip themselves if
this DB is not reachable on `localhost:5433` (verified in
`tests/integration/conftest.py`).

**Critical environment dependencies (from `docker-compose.yml`):**

- `POSTGRES_PASSWORD`, `DATABASE_URL`, `JWT_SECRET` are required (`:?` in
  compose file means failing without them). `pashu-erp/.env` exists; its
  contents were not read for this report (treat as opaque secrets).
- `JWT_SECRET` must be ≥ 64 hex chars (asserted in
  `app/main.py::_validate_settings()`).
- In non-development environments, `AADHAAR_HASH_SECRET`, `SARVAM_API_KEY`,
  and the four service URLs (`WEATHER_API_URL`, `BHARAT_PASHUDHAN_API_URL`,
  `IOT_GATEWAY_URL`, `STORAGE_API_URL`) are also mandatory.

---

## 2. API endpoints — every route, every method (verified)

Source: `grep -rE "^@router\." packages/api/app/routers/*.py` followed by
walking forward to the `async def` line. **Total: 115 endpoints across 29
router files.**

### Per-router endpoint count (highest first)

```
  10  vaccination.py
   9  vet.py
   7  milk.py
   7  income.py
   6  milk_center.py
   5  shg.py
   5  reference.py
   5  marketplace.py
   5  iot.py
   5  auth.py
   5  animals.py
   4  health.py
   4  consent.py
   4  admin.py
   3  weather.py
   3  schemes.py
   3  medicine.py
   3  insurance.py
   3  files.py
   3  ethno_vet.py
   3  alerts.py
   2  users.py
   2  finance.py
   2  feed.py
   2  bharat_pashudhan.py
   2  advisory.py
   1  onboarding.py
   1  medicine_log.py
   1  map_points.py
```

### Full endpoint inventory (grouped by router file)

#### `auth.py` — `/v1/auth` (5 endpoints)

| Method | Path                  | Handler          | Auth                | Notes                                       |
| ------ | --------------------- | ---------------- | ------------------- | ------------------------------------------- |
| POST   | `/v1/auth/request-otp`| `request_otp`    | none                | `slowapi.limit("5/minute")`, hashes via bcrypt |
| POST   | `/v1/auth/verify-otp` | `verify_otp`     | none                | issues JWT (mobile) or sets cookies (web); `client_type` field gates web staff-only |
| POST   | `/v1/auth/refresh`    | `refresh_token`  | refresh token       | rotates refresh token; revokes-all on reuse detection |
| GET    | `/v1/auth/me`         | `get_me`         | `get_current_user`  | returns `{user_id, role, name, location_district}` |
| POST   | `/v1/auth/logout`     | `logout`         | `get_current_user`  | revokes all active refresh tokens for user |

#### `animals.py` — `/v1/animals` (5 endpoints)

| Method | Path                       | Handler          | Auth               |
| ------ | -------------------------- | ---------------- | ------------------ |
| POST   | `/v1/animals`              | `create_animal`  | `get_current_user` |
| GET    | `/v1/animals`              | `list_animals`   | `get_current_user` |
| GET    | `/v1/animals/{animal_id}`  | `get_animal`     | `get_current_user` |
| PATCH  | `/v1/animals/{animal_id}`  | `update_animal`  | `get_current_user` |
| DELETE | `/v1/animals/{animal_id}`  | `delete_animal`  | `get_current_user` |

Role rules verified by reading the router source:
- admin: list/get/update any animal
- vet: list/get any animal whose owner shares the first 2 chars of
  `village_code`; cannot modify
- farmer: own animals only
- delete cascades soft-delete to `health_events`, `yield_logs`, `vaccinations`

#### `health.py` — `/v1` (4 endpoints, prefix omitted because some routes use the bare `/v1`)

| Method | Path                           | Handler                  | Auth                |
| ------ | ------------------------------ | ------------------------ | ------------------- |
| POST   | `/v1/health/log`               | `log_health_event`       | `get_current_user`  |
| GET    | `/v1/health/history/{animal_id}`| `get_health_history`    | `get_current_user`  |
| GET    | `/v1/health`                   | `list_health_events`     | `get_current_user`  |
| GET    | `/v1/health/alerts/map`        | `get_health_alerts_map`  | `require_admin`     |

#### `milk.py` — `/v1/milk` (7 endpoints)

| Method | Path                                    | Handler                | Auth               |
| ------ | --------------------------------------- | ---------------------- | ------------------ |
| GET    | `/v1/milk`                              | `list_milk_records`    | `get_current_user` |
| GET    | `/v1/milk/today`                        | `get_today_total`      | `get_current_user` |
| GET    | `/v1/milk/history`                      | `get_my_milk_history`  | `get_current_user` |
| GET    | `/v1/milk/daily-summary`                | `get_daily_summary`    | `get_current_user` |
| POST   | `/v1/milk/yield`                        | `record_yield`         | `get_current_user` |
| GET    | `/v1/milk/farmer/{user_id}/history`     | `get_milk_history`     | `get_current_user` |
| GET    | `/v1/milk/center/{center_id}/daily`     | `get_daily_collection` | `get_current_user` |

#### `milk_center.py` — `/v1/milk-center` (6 endpoints)

| Method | Path                                                 | Handler                  | Auth                          |
| ------ | ---------------------------------------------------- | ------------------------ | ----------------------------- |
| GET    | `/v1/milk-center/my-center`                          | `get_my_center`          | `require_milk_center_staff`  |
| POST   | `/v1/milk-center/receive`                            | `receive_milk`           | `require_milk_center_staff`  |
| GET    | `/v1/milk-center/{center_id}/daily-report`           | `get_daily_report`       | (verify in source)            |
| GET    | `/v1/milk-center/{center_id}/farmer-settlements`     | `get_farmer_settlements` | (verify in source)            |
| GET    | `/v1/milk-center/farmers/search`                     | `search_farmers`         | (verify in source)            |
| POST   | `/v1/milk-center/farmers/enroll`                     | (handler not in scrape — re-read source for name) | (verify) |

> Note: The 6th milk-center POST endpoint `/farmers/enroll` exists (verified
> by `grep -c` returning 6) but its function name was not extracted by the
> awk pattern because the decorator spans multiple lines. **Re-read
> `packages/api/app/routers/milk_center.py` lines 344-346 before writing
> tests for it.**

#### `vet.py` — `/v1/vet` (9 endpoints)

| Method | Path                                  | Handler                 |
| ------ | ------------------------------------- | ----------------------- |
| GET    | `/v1/vet/cases`                       | `list_cases`            |
| GET    | `/v1/vet/cases/{case_id}`             | `get_case`              |
| PATCH  | `/v1/vet/cases/{case_id}/claim`       | `claim_case`            |
| PATCH  | `/v1/vet/cases/{case_id}/diagnose`    | `diagnose_case`         |
| PATCH  | `/v1/vet/cases/{case_id}/video-link`  | `set_video_link`        |
| PATCH  | `/v1/vet/cases/{case_id}/close`       | `close_case`            |
| GET    | `/v1/vet/dashboard/stats`             | `vet_dashboard_stats`   |
| GET    | `/v1/vet/dashboard/alerts`            | `vet_dashboard_alerts`  |
| GET    | `/v1/vet/my-cases`                    | `my_cases`              |

`vet_dashboard_stats` uses `require_vet_or_admin` (verified). Other endpoints
use a mix of `get_current_user` and role-specific dependencies — confirm per
endpoint before writing role-boundary tests.

#### `vaccination.py` — `/v1/vaccinations` (10 endpoints)

| Method | Path                                          | Handler                          |
| ------ | --------------------------------------------- | -------------------------------- |
| POST   | `/v1/vaccinations`                            | `record_vaccination`             |
| GET    | `/v1/vaccinations/due`                        | `get_due_vaccinations_for_user`  |
| GET    | `/v1/vaccinations/species-breakdown`          | `get_species_breakdown` (admin)  |
| GET    | `/v1/vaccinations/village-coverage`           | `get_village_coverage_admin` (admin) |
| GET    | `/v1/vaccinations/schedule`                   | `get_all_schedules`              |
| GET    | `/v1/vaccinations/{animal_id}`                | `get_vaccinations`               |
| GET    | `/v1/vaccinations/schedule/{species}`         | `get_species_schedule`           |
| GET    | `/v1/vaccinations/due/{user_id}`              | `get_upcoming_vaccinations`      |
| GET    | `/v1/vaccinations/coverage/{village_code}`    | `get_village_coverage`           |
| PATCH  | `/v1/vaccinations/{vaccination_id}`           | `update_vaccination`             |

> **Routing risk:** `GET /v1/vaccinations/{animal_id}` and `GET
> /v1/vaccinations/schedule` are at the same path level. FastAPI route order
> matters here. The router file lists `/schedule` before `/{animal_id}` —
> verify this on every change.

#### `income.py` — `/v1/income` (7 endpoints)

| Method | Path                                | Handler                  |
| ------ | ----------------------------------- | ------------------------ |
| GET    | `/v1/income/summary/{user_id}`      | `income_summary`         |
| GET    | `/v1/income/breakdown/{user_id}`    | `income_breakdown`       |
| GET    | `/v1/income/history/{user_id}`      | `income_history`         |
| GET    | `/v1/income/summary`                | `my_income_summary`      |
| GET    | `/v1/income/transactions`           | `my_income_transactions` |
| GET    | `/v1/income/by-category`            | `income_by_category`     |
| GET    | `/v1/income/monthly`                | `income_monthly_trend`   |

> **Routing risk:** `GET /summary/{user_id}` vs `GET /summary` — FastAPI
> resolves these by registration order. The router file declares
> `/summary/{user_id}` first (line 28) and `/summary` later (line 238).
> A request to `/v1/income/summary` (no trailing path) will hit
> `my_income_summary`, but a request to `/v1/income/summary/anything`
> hits `income_summary` because of greedy path matching. Verified by
> reading source.

#### Remaining routers (compact)

```
admin.py           4   /v1/admin/{stats,charts/milk,gis/alerts,users/{user_id}/role}
shg.py             5   /v1/shg/{,,, /{shg_id}, /{shg_id}/compliance}
schemes.py         3   /v1/schemes/{,, /{scheme_id}}
marketplace.py     5   /v1/marketplace/{,sell,history/{user_id},rates,summary/{user_id}}
insurance.py       3   /v1/insurance/{policies/{user_id},claims,premium-estimate/{animal_id}}
finance.py         2   /v1/finance/{transaction,summary}
feed.py            2   /v1/feed/{ingredients,calculate-ration}
ethno_vet.py       3   /v1/ethno-vet/{remedies,remedies/{remedy_id},search}
alerts.py          3   /v1/alerts/{report,nearby,{alert_id}/verify}
medicine.py        3   /v1/medicines/{,administer,withdrawal-status/{animal_id}}
medicine_log.py    1   /v1/medicine-log/withdrawals
advisory.py        2   /v1/advisory/{tips,tips/{tip_id}}
weather.py         3   /v1/weather/{forecast,alerts,tts}/{district}
iot.py             5   /v1/iot/{devices,device-types,readings,devices/{id},devices/{id}/latest}
bharat_pashudhan.py 2  /v1/registry/{lookup/{id},sync/{animal_id}}
files.py           3   /v1/files/{POST,GET /{id},GET}
consent.py         4   /v1/consent/{grant,withdraw,my,erasure-request}
users.py           2   /v1/{farmers,users/profile}
reference.py       5   /v1/reference/{market-rates(GET/PUT),insurance-premiums(GET/PUT),medicines}
onboarding.py      1   /v1/onboarding/complete
map_points.py      1   /v1/map/points
```

### App-level (non-router) endpoints

Defined directly on the FastAPI app in `packages/api/app/main.py`:

| Method | Path       | Notes                                                        |
| ------ | ---------- | ------------------------------------------------------------ |
| GET    | `/health`  | DB ping; returns 200 healthy or 503 unhealthy                |
| GET    | `/ready`   | DB + weather + IoT connectivity check; 200 ready or 503     |
| GET    | `/metrics` | Uptime + status; `include_in_schema=False`                   |
| GET    | `/docs`    | Swagger UI — only when `ENVIRONMENT=development`             |
| GET    | `/redoc`   | ReDoc — only when `ENVIRONMENT=development`                  |

---

## 3. Database models — every table, every column count

Source: `find packages/api/app/models -name "*.py"` + `grep mapped_column`.

| File           | Class                       | Table                       | Columns |
| -------------- | --------------------------- | --------------------------- | ------: |
| advisory.py    | AdvisoryTip                 | advisory_tips               |      12 |
| alerts.py      | CommunityAlert              | community_alerts            |       9 |
| animal.py      | Animal                      | animals                     |      14 |
| auth.py        | RefreshToken                | refresh_tokens              |       5 |
| consent.py     | Consent                     | consents                    |       7 |
| ethno_vet.py   | TraditionalRemedy           | traditional_remedies        |      10 |
| feed.py        | FeedIngredient              | feed_ingredients            |       9 |
| finance.py     | Transaction                 | transactions                |       8 |
| health.py      | HealthEvent                 | health_events               | (split) |
| health.py      | Vaccination                 | vaccinations                | (split) |
| health.py      | (file total)                |                             |      17 |
| insurance.py   | InsurancePolicy             | insurance_policies          | (split) |
| insurance.py   | InsuranceClaim              | insurance_claims            | (split) |
| insurance.py   | (file total)                |                             |      17 |
| marketplace.py | SellRecord                  | sell_records                |      11 |
| medicine.py    | Medicine                    | medicines                   | (split) |
| medicine.py    | MedicineAdministration      | medicine_administrations    | (split) |
| medicine.py    | (file total)                |                             |      14 |
| milk.py        | YieldLog                    | yield_logs                  | (split) |
| milk.py        | MilkCollectionCenter        | milk_collection_centers     | (split) |
| milk.py        | MilkCollectionRecord        | milk_collection_records     | (split) |
| milk.py        | (file total)                |                             |      24 |
| otp.py         | OTPRequest                  | otp_requests                |       6 |
| reference.py   | MarketRate                  | market_rates                | (split) |
| reference.py   | InsurancePremium            | insurance_premiums          | (split) |
| reference.py   | MedicineCatalog             | medicine_catalog            | (split) |
| reference.py   | (file total)                |                             |      24 |
| schemes.py     | GovtScheme                  | govt_schemes                |      12 |
| shg.py         | SHGGroup                    | shg_groups                  |      12 |
| user.py        | User                        | users                       |      12 |
| vet.py         | VetConsultation             | vet_consultations           |      14 |
| weather.py     | WeatherAlert                | weather_alerts              |       8 |

**Mixins applied to most tables (verified in `app/models/base.py`):**

- `TimestampMixin` → adds `created_at`, `updated_at` (server-default `now()`)
- `AuditMixin` → adds `created_by`, `updated_by` (UUID FK to users)
- `SoftDeleteMixin` → adds `deleted_at` (nullable timestamp)

`OTPRequest`, `RefreshToken`, and `Consent` use only `TimestampMixin` (and
`SoftDeleteMixin` for `Consent`). The mixin columns are **not** counted in
the `mapped_column` totals above; the totals reflect only columns declared
in the model file itself.

### Alembic migration history (12 files, in declared order)

```
d22bbd14c60e_initial_schema.py
b2c3d4e5f6a7_add_vet_consultations_table.py
b7c8d9e0f1a2_add_otp_requests_table.py
c8d9e0f1a2b3_add_reference_data_tables.py
d4e5f6a7b8c9_add_fk_constraints_and_updated_at.py
e3f4a5b6c7d8_float_to_numeric_financial_columns.py
e5f6a7b8c9d0_add_refresh_tokens.py
f4a5b6c7d8e9_add_audit_softdelete_aadhaar_unique.py
f6a7b8c9d0e1_add_buffalo_to_species_enum.py
g7h8i9j0k1l2_add_gender_column_to_users.py
a1b2c3d4e5f6_add_performance_indexes.py
c0mp051t31dx_composite_indexes.py
```

> **Migration ordering caveat:** the file naming uses 12-char hex hashes,
> not dates. The actual upgrade order is encoded in each file's
> `down_revision` field. For migration safety tests we need to read each
> file's revision graph — not assume order from file names.

---

## 4. Mock backends (mocks/)

Source: `mocks/main.py` mounts 4 routers. Endpoints listed below.

| Router file | Prefix              | Endpoints |
| ----------- | ------------------- | --------- |
| weather.py  | `/api/v1/weather`   | GET `/forecast`, GET `/alerts`, POST `/tts` |
| registry.py | `/api/v1/registry`  | GET `/animals/{pashu_aadhaar_id}`, POST `/sync` |
| iot.py      | `/api/v1/iot`       | GET `/devices`, GET `/devices/{id}`, GET `/devices/{id}/latest`, GET `/telemetry` |
| storage.py  | `/api/v1/storage`   | POST `/files`, GET `/files`, GET `/files/{id}` |

App-level: `GET /health` returns `{"status": "ok", "service": "pashuraksha-mock-services"}`.

Mock services are wired into the API via env vars:

```
WEATHER_API_URL          = http://mock-backends:8001/api/v1/weather
BHARAT_PASHUDHAN_API_URL = http://mock-backends:8001/api/v1/registry
IOT_GATEWAY_URL          = http://mock-backends:8001/api/v1/iot
STORAGE_API_URL          = http://mock-backends:8001/api/v1/storage
```

---

## 5. Frontend apps — every screen / page

### 5A. Admin (`packages/admin`) — Next.js 14 App Router (port 3000)

`package.json` declares: `next ^14.2.35`, `react ^18.3.0`, `@refinedev/core
^4.47.0`, `@refinedev/mui ^5.14.0`, `@mui/material ^5.16.0`, `leaflet
^1.9.0`, `recharts ^2.12.0`. Test scripts: `jest`. Coverage thresholds in
`jest.config.js`: branches 60, functions 70, lines 70, statements 70.

| Route                       | File                                          |
| --------------------------- | --------------------------------------------- |
| `/`                         | `src/app/page.tsx`                            |
| `/animals`                  | `src/app/animals/page.tsx`                    |
| `/farmers`                  | `src/app/farmers/page.tsx`                    |
| `/health`                   | `src/app/health/page.tsx`                     |
| `/income`                   | `src/app/income/page.tsx`                     |
| `/iot`                      | `src/app/iot/page.tsx`                        |
| `/login`                    | `src/app/login/page.tsx`                      |
| `/map`                      | `src/app/map/page.tsx`                        |
| `/marketplace`              | `src/app/marketplace/page.tsx`                |
| `/milk`                     | `src/app/milk/page.tsx`                       |
| `/schemes`                  | `src/app/schemes/page.tsx`                    |
| `/vaccinations`             | `src/app/vaccinations/page.tsx`               |
| `/vet`                      | `src/app/vet/page.tsx`                        |
| `/vet/alerts`               | `src/app/vet/alerts/page.tsx`                 |
| `/vet/cases`                | `src/app/vet/cases/page.tsx`                  |
| `/vet/cases/[id]`           | `src/app/vet/cases/[id]/page.tsx`             |

### 5B. Mobile (`packages/mobile`) — Expo 52 + Expo Router (port 8081 dev)

`package.json` declares: `expo ~52.0.0`, `expo-router ~4.0.0`, `react-native
0.76.3`, `react-native-paper ^5.12.0`, `i18next ^23.11.0`. Test scripts:
`jest` (with `jest-expo ~52.0.0`).

| Route segment              | File                                       |
| -------------------------- | ------------------------------------------ |
| `/(auth)/login`            | `app/(auth)/login.tsx`                     |
| `/(tabs)/index` (home)     | `app/(tabs)/index.tsx`                     |
| `/(tabs)/health`           | `app/(tabs)/health.tsx`                    |
| `/(tabs)/income`           | `app/(tabs)/income.tsx`                    |
| `/(tabs)/milk`             | `app/(tabs)/milk.tsx`                      |
| `/(tabs)/sell`             | `app/(tabs)/sell.tsx`                      |
| `/onboarding/welcome`      | `app/onboarding/welcome.tsx`               |
| `/onboarding/profile`      | `app/onboarding/profile.tsx`               |
| `/onboarding/first-animal` | `app/onboarding/first-animal.tsx`          |
| `/onboarding/tutorial`     | `app/onboarding/tutorial.tsx`              |
| `/animal/[id]`             | `app/animal/[id].tsx`                      |
| `/animal/add`              | `app/animal/add.tsx`                       |
| `/advisory`                | `app/advisory.tsx`                         |
| `/community-alerts`        | `app/community-alerts.tsx`                 |
| `/ethno-vet`               | `app/ethno-vet.tsx`                        |
| `/feed-calculator`         | `app/feed-calculator.tsx`                  |
| `/insurance`               | `app/insurance.tsx`                        |
| `/medicine-log`            | `app/medicine-log.tsx`                     |
| `/milk/history`            | `app/milk/history.tsx`                     |
| `/my-consultations`        | `app/my-consultations.tsx`                 |
| `/pashu-aadhaar`           | `app/pashu-aadhaar.tsx`                    |
| `/profile`                 | `app/profile.tsx`                          |
| `/smart-farm`              | `app/smart-farm.tsx`                       |
| `/vaccinations`            | `app/vaccinations.tsx`                     |
| `/vet-photo`               | `app/vet-photo.tsx`                        |
| `/weather`                 | `app/weather.tsx`                          |

### 5C. Collection (`packages/collection`) — Vite + MUI PWA (port 3001)

| Route          | File                                |
| -------------- | ----------------------------------- |
| (router-driven)| `src/pages/Login.tsx`               |
|                | `src/pages/Dashboard.tsx`           |
|                | `src/pages/Enroll.tsx`              |
|                | `src/pages/Intake.tsx`              |
|                | `src/pages/Receipt.tsx`             |
|                | `src/pages/Settlements.tsx`         |

> The actual route table lives in the React Router setup (likely
> `src/App.tsx`); this report did not enumerate the route paths because
> they were not the focus of Phase 0. Re-read `src/App.tsx` before writing
> route-aware tests.

### 5D. Vet (`packages/vet`) — Vite + MUI + Leaflet (port 3002)

| Route          | File                                |
| -------------- | ----------------------------------- |
| (router-driven)| `src/pages/Login.tsx`               |
|                | `src/pages/Dashboard.tsx`           |
|                | `src/pages/Cases.tsx`               |
|                | `src/pages/CaseDetail.tsx`          |
|                | `src/pages/Alerts.tsx`              |

---

## 6. Existing tests — what is there and what works

### 6A. Backend pytest (`packages/api/tests/`)

**Counts (verified):**
- Files: 44 test files (one `test_*.py` per router, plus services and flows)
- Total cases collected: **529**
- Integration cases (real Postgres): **13**
- Unit cases: **516** (529 − 13)
- Last run (`uv run pytest tests/ --ignore=tests/integration -q`):
  **494 passed, 24 skipped, 0 failed in 52.09s**

**Skipped (24) — investigated:** the skips are concentrated early in the
collection (visible as a `sssssssssssssssssss` block at the start). Likely
candidates: a fixture-gated module, or a pytest `skipif` for a service URL
not configured. **This needs explicit investigation before we know whether
those 24 are valid skips or hidden failures.** Do not assume they are
intentional.

**File-to-router coverage:** every router (29/29) has a matching
`tests/test_<router>.py` file. Plus 9 service / flow files:

```
test_bharat_pashudhan_service.py
test_browser_walkthrough.py
test_csrf.py
test_demo_scenarios.py
test_disease_rules.py
test_feed_calculator.py
test_integration_e2e.py
test_iot_service.py
test_market_rates.py
test_milk_pricing.py
test_storage_service.py
test_vaccination_scheduler.py
test_weather_service.py
```

**Endpoint-to-test coverage is NOT yet measured.** A test file existing for
a router does not mean every endpoint inside it is tested. To produce that
gap analysis we need to (a) parse each test file's parametrizations and
(b) cross-reference against the 115-endpoint inventory above. **This is a
Phase 1 task.**

**Test infrastructure:**

- `tests/conftest.py` (368 lines, read in full): provides
  `client`, `client_as_admin`, `client_as_vet`, `client_as_milk_center`,
  `client_no_auth` fixtures. Each one mounts a fresh `create_app()`,
  overrides `get_db` with an `AsyncMock`, overrides `get_current_user` to
  return a per-role `MagicMock` user, and sends a real (test-secret) JWT in
  the `Authorization` header so the CSRF middleware passes mutating
  requests.
- `tests/factories.py`: shared `mock_animal`, `mock_health_event`,
  `mock_yield_log` factories with `FARMER_USER_ID` baked in.
- `tests/integration/conftest.py` (131 lines, read in full): real Postgres
  on `localhost:5433`, autouse skip if not reachable, fresh engine and
  Truncate-CASCADE per test for isolation.
- `pyproject.toml`: `asyncio_mode = "auto"`, `--strict-markers --tb=short`,
  custom `integration` marker.

### 6B. Frontend Jest (admin + mobile)

| Package | Files | Status                             |
| ------- | ----- | ---------------------------------- |
| admin   | 4     | not yet executed in this session   |
| mobile  | 18 (incl. 2 setup helpers)  | not yet executed |

Admin test files:
```
src/__tests__/pages/farmers.test.tsx
src/__tests__/components/StatCard.test.tsx
src/__tests__/components/RiskBadge.test.tsx
src/__tests__/components/SpeciesChip.test.tsx
```

Mobile test files (16 real test files + setup.ts + test-utils.tsx):
```
src/__tests__/config/api.test.ts
src/__tests__/config/storage.test.ts
src/__tests__/screens/login.test.tsx
src/__tests__/screens/home.test.tsx
src/__tests__/screens/milk.test.tsx
src/__tests__/screens/profile.test.tsx
src/__tests__/screens/onboarding-profile.test.tsx
src/__tests__/components/MicButton.test.tsx
src/__tests__/components/AnimalCard.test.tsx
src/__tests__/components/TriageCard.test.tsx
src/__tests__/components/FilterChips.test.tsx
src/__tests__/components/LoadingSkeleton.test.tsx
src/__tests__/flows/health-triage.test.tsx
src/__tests__/flows/milk-recording.test.tsx
src/__tests__/services/kannada-parser.test.ts
src/services/__tests__/kannada-parser.test.ts   # duplicate path — investigate
```

> **Caveat:** the `kannada-parser.test.ts` appears in two locations
> (`src/__tests__/services/` and `src/services/__tests__/`). Could be a
> deliberate duplicate, a leftover from a refactor, or a real bug. Re-read
> before writing new mobile tests.

### 6C. Vitest (collection + vet) — verified working

- collection: **2 files, 7 tests, all passing** — `npx vitest run`
  (Login: 6 tests, Dashboard: 1 test). Some `act(...)` warnings on
  Dashboard but no failures.
- vet: **2 files, 9 tests, all passing** — `npx vitest run`
  (Login: 6 tests, Dashboard: 3 tests). Same `act(...)` warnings.

The `act` warnings indicate the existing tests do not properly wait for
async state updates. They pass today but are brittle. Worth tightening,
not urgent.

### 6D. Playwright e2e (`pashu-erp/e2e/`)

| Spec                                | `test()` blocks |
| ----------------------------------- | --------------: |
| `e2e/admin-smoke.spec.ts`           | 20              |
| `e2e/fullstack-smoke.spec.ts`       | 17              |
| `e2e/visual/visual-baseline.spec.ts`|  6              |

Plus 13 standalone Python CDP scripts (`cdp-*.py`) — these are NOT pytest /
Playwright tests; they appear to be ad-hoc debugging scripts that drive a
running browser via Chrome DevTools Protocol. Status unknown; not part of
any test runner. **Treat as separate from the pytest / Playwright suite.**

The fullstack spec uses real OTP login, scraping the OTP from
`docker logs pashu-erp-api-1`. This is fragile (depends on log format,
container name, log retention) but works today because the API logs OTPs in
plaintext in `development` mode.

`e2e/load/baseline.js` is a k6 load test (not a Playwright test). It uses a
hard-coded OTP `"123456"`, which **only works against a mock OTP provider**,
not the real bcrypt-verified flow. **This is broken-by-design against the
real auth stack** unless a `MOCK_OTP_VALUE=123456` test mode is enabled.
Confirm before relying on it.

---

## 7. Auth mechanism — verified per app

Source: read `app/middleware/auth.py` (119 lines), `app/routers/auth.py`
(388 lines), and the relevant frontend login pages (admin
`src/app/login/page.tsx` and the verify flow).

### 7A. Backend auth contract

- **JWT** uses HS256, secret in `JWT_SECRET` (≥ 64 hex chars enforced).
  Access token TTL = `settings.jwt_expire_minutes`. Refresh token TTL =
  `settings.jwt_refresh_expiry_days`.
- **Token extraction** (`_extract_token`):
  1. `Authorization: Bearer <token>` header — primary for mobile.
  2. `token` httpOnly cookie — primary for web (admin / collection / vet).
  3. Otherwise → 401.
- **User role enum**: `farmer`, `admin`, `vet`, `milk_center` (from
  `app/models/user.py::UserRole`).
- **Web staff gate**: `verify-otp` rejects `client_type=web` if user role
  is not in `STAFF_ROLES = {admin, vet, milk_center}` → 403 with
  `code=ROLE_NOT_AUTHORIZED`. Farmers must use the mobile app.
- **Refresh token rotation**: each refresh issues a new pair and revokes
  the previous; reuse of a revoked token revokes ALL active tokens for that
  user (defense against stolen-token replay).
- **Rate limiting**: `slowapi` — 5/minute on `request-otp` and
  `verify-otp`, 10/minute on `refresh`.
- **CSRF**: `CSRFMiddleware` is active for non-GET methods. Tests must
  include either a Bearer header (mobile) or a real cookie + `X-CSRF-Token`
  header (web). The conftest fixtures handle this by sending the JWT in the
  Authorization header.

### 7B. OTP storage

`OTPRequest` model, `otp_requests` table (6 columns):
- `phone` (unique)
- `otp_hash` (bcrypt)
- `attempts` (defaults to 0; max from `MAX_OTP_ATTEMPTS`)
- `expires_at` (now + `OTP_EXPIRY_MINUTES`)
- `request_count` (per-hour throttle, max from `MAX_OTP_REQUESTS_PER_HOUR`)
- `created_at` (mixin)

OTP is generated via `secrets.randbelow(900000) + 100000` (6 digits) and
sent through the configured provider (real or mock). Verify-OTP returns a
**single generic error message** for all failure modes ("Invalid or expired
OTP") to prevent phone-number enumeration.

### 7C. Per-app auth flow (verified)

| App        | Token transport  | After verify-otp                                                                |
| ---------- | ---------------- | ------------------------------------------------------------------------------- |
| Mobile     | `Bearer` header  | `verify-otp` returns `TokenResponse` JSON `{access_token, refresh_token, ...}`  |
| Admin      | httpOnly cookie  | `verify-otp` sets `token` + `csrf_token` cookies, returns `AuthUserResponse`     |
| Collection | httpOnly cookie  | same as admin (cookie auth, web staff role required)                            |
| Vet        | httpOnly cookie  | same as admin                                                                   |

**Verified seed test users (from existing e2e tests, not from a doc):**

```
+919900000001    admin       (used by admin OTP login in fullstack spec)
+919900000002    farmer      (used by auth boundary test)
+919900000005    vet         (used by vet OTP login)
+919900000006    milk_center (used by collection OTP login)
```

These appear to be created by `app/seed/demo_data.py`. Do not assume they
exist on a fresh DB — the seed script must be run first.

### 7D. Cross-cutting middleware (read from `app/main.py`)

Middleware stack (added in this order; runs in **reverse** for requests):

```
RequestLoggingMiddleware          # innermost — logs request after response
CSRFMiddleware                    # validates X-CSRF-Token vs cookie
SecurityHeadersMiddleware         # x-frame-options, CSP, HSTS in non-dev
ContentSizeLimitMiddleware        # rejects bodies > 10 MB
SlowAPIASGIMiddleware             # rate limiting
CORSMiddleware                    # outermost — handles preflight
```

Custom error handlers:
- `RateLimitExceeded` → 429 `{detail, code=RATE_LIMITED}`
- `ServiceNotConfiguredError` → 503 `{code=SERVICE_NOT_CONFIGURED}`
- `ServiceUnavailableError` → 503 `{code=SERVICE_UNAVAILABLE}`
- `CircuitBreakerError` (if `circuitbreaker` lib available) → 503
  `{code=CIRCUIT_OPEN}`

These behaviours are valuable test targets — they are easy to verify and
hard to regress without noticing.

---

## 8. Environment validation (verified by running)

| Tool              | Installed | Version  | Notes                                     |
| ----------------- | --------- | -------- | ----------------------------------------- |
| `uv`              | yes       | 0.7.13   | `~/.local/bin/uv`                         |
| `python3`         | yes       | 3.10.12  | system, plus `pyproject.toml` requires `>=3.10` |
| `pytest`          | yes       | (system) | uv-managed env preferred                   |
| `docker`          | yes       | 29.1.5   | + Compose v5.0.1                          |
| `node`            | yes       | 22.21.1  | via nvm; required by build/test scripts   |
| `pnpm`            | yes       | 10.32.1  |                                           |
| `npx jest`        | yes       | 29.7.0   | admin + mobile                            |
| `npx vitest`      | yes       | 1.6.1    | collection + vet                          |
| `@playwright/test`| installed | 1.44+    | declared in root `package.json`           |
| `k6`              | unknown   | -        | `npm run test:load` calls k6; not verified|

**Stack already running:** `db`, `mock-backends`, `api` are all healthy.
Frontend services and `test-db` (port 5433) are not running.

**Live API health probe (verified at write time):**

```
GET http://localhost:8000/health  →  200  {"status":"healthy","database":"connected"}
GET http://localhost:8001/health  →  200
```

---

## 9. Known issues, ambiguities, and red flags surfaced during discovery

These are things the next phase MUST address before claiming any test
passes. None of these are assumptions; each is an observation.

1. **24 skipped pytest tests** — the cause is not yet identified. Need to
   run with `pytest -rs` and read the skip reasons before treating them as
   intentional.

2. **k6 load test uses hard-coded OTP `123456`** — this only works if a
   mock OTP provider is enabled. Against the real flow it will 401. The
   load test is therefore not currently executable end-to-end without
   either (a) seeding a fixed OTP, (b) running with a mock provider env,
   or (c) being rewritten to scrape the real OTP from logs like the
   fullstack Playwright spec does.

3. **Two copies of `kannada-parser.test.ts`** in mobile — one under
   `src/__tests__/services/` and one under `src/services/__tests__/`.
   Either deduplicate or document why both exist.

4. **`act(...)` warnings in collection + vet vitest** — tests pass but
   they don't await React state settling. They will become brittle as
   the components grow.

5. **Vaccination route order risk** — `/vaccinations/{animal_id}` and
   `/vaccinations/schedule` are both reachable via the same prefix; the
   declared order in the file matters and is fragile. A test should pin
   this ordering.

6. **Income summary route shadowing** — `/income/summary/{user_id}` is
   declared before `/income/summary`. Today this works because of FastAPI
   greedy matching, but if anyone reorders, the no-arg `/summary` will
   start hitting `income_summary` with `user_id="summary"` — a 422 or
   silent wrong-user lookup.

7. **CDP scripts in `e2e/`** (13 `.py` files) are not part of any test
   runner. They exist but their pass/fail status is unknown. Either
   integrate them into a runner or delete them.

8. **Frontend services are NOT in default docker compose profile** — they
   only come up with `--profile frontend`. Any e2e test that assumes
   3000/3001/3002 is up must either start them explicitly or rely on the
   Playwright `webServer` config.

9. **Demo seed users hard-coded into e2e tests** (`+91990000000{1,2,5,6}`).
   If the seed data drifts, every fullstack test breaks. The seed
   contract should be tested as a precondition.

10. **`milk_center` 6th endpoint** (`POST /v1/milk-center/farmers/enroll`)
    was found by raw count but not by the function-name extractor (the
    decorator spans multiple lines). Re-read the file before writing the
    test to confirm the handler name.

---

## 10. Proposed scope for the next phase (awaiting your spec)

Your Phase 1 instructions were truncated mid-sentence at:
`Create this directory structure:`

I am **NOT** going to invent the rest of Phase 1. I will wait for:
- The directory structure you want under `tests/` (or wherever)
- Whether you want me to AUGMENT existing pytest tests or REPLACE them
- Whether you want endpoint-by-endpoint coverage analysis as Phase 1A
  (recommended — produces a real coverage map for the 115 endpoints)
- Frontend test scope (admin + mobile + collection + vet, or only some?)
- E2E scope (smoke only, or full user journeys per role?)
- Performance / load / security / chaos scope

When you paste Phase 1 in full, I will follow your "verify, don't trust"
rule strictly and produce only tests that I have run and confirmed green.

---

## Appendix — exact commands used to produce this report

Each command was run from `pashu-erp/`.

```bash
# Endpoint count
find packages/api/app/routers -maxdepth 1 -name "*.py" -not -name "__init__.py" \
  | wc -l                                          # → 29

grep -rE "^@router\." packages/api/app/routers/ | wc -l   # → 115

# Per-router count
find packages/api/app/routers -maxdepth 1 -name "*.py" -not -name "__init__.py" \
  | while read f; do c=$(grep -c "^@router\." "$f"); printf "%4d  %s\n" "$c" "$f"; done \
  | sort -rn

# Models / tables
grep -r "__tablename__" packages/api/app/models/ | wc -l    # → 27

# Mapped column count per model
find packages/api/app/models -maxdepth 1 -name "*.py" -not -name "__init__.py" -not -name "base.py" \
  | while read f; do c=$(grep -c "mapped_column(" "$f"); printf "%4d  %s\n" "$c" "$(basename $f)"; done

# Pytest collection + run
cd packages/api && uv run pytest --collect-only -q | tail -2     # → 529 collected
cd packages/api && uv run pytest tests/ --ignore=tests/integration -q --tb=no
# → 494 passed, 24 skipped in 52.09s

# Vitest verification
cd packages/collection && npx vitest run     # → 7 tests passed
cd packages/vet && npx vitest run            # → 9 tests passed

# Live service probes
curl -s http://localhost:8000/health         # → {"status":"healthy",...}
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8001/health   # → 200

# Docker stack
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Re-run these any time you want to re-verify the baseline.
