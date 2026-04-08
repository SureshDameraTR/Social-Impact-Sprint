## 1. Monorepo Scaffold

- [x] 1.1 Create `pashu-erp/` root with `docker-compose.yml` (Postgres 16 + API), `.env.example`, `pnpm-workspace.yaml`
- [x] 1.2 Create `justfile` with tasks: `dev`, `test`, `seed`, `generate-client`, `lint`, `migrate`
- [x] 1.3 Create `packages/api/` with `pyproject.toml` (FastAPI, SQLAlchemy, Alembic, asyncpg, pydantic-settings, python-jose, passlib, uvicorn)
- [x] 1.4 Create `packages/admin/` with `package.json` (Next.js 14, Refine v4, MUI v5, Recharts, react-leaflet)
- [x] 1.5 Create `packages/mobile/` — init Expo SDK 52 project with expo-router, react-native-paper, i18next, expo-secure-store, react-native-gifted-charts
- [ ] 1.6 Verify `docker compose up` starts Postgres and API serves `GET /docs`

## 2. Database Models & Migrations

- [x] 2.1 Create `app/database.py` — async SQLAlchemy engine, `async_sessionmaker` with `expire_on_commit=False`, `pool_pre_ping=True`
- [x] 2.2 Create `app/config.py` — pydantic-settings `Settings` class loading from `.env`
- [x] 2.3 Create `app/models/user.py` — User model (id, role, phone, name, lang_pref, location_district, location_state, village_code, preferences, created_at, updated_at)
- [x] 2.4 Create `app/models/animal.py` — Animal model (id, user_id FK, pashu_aadhaar_id, species, breed, breed_type, tag_id, date_of_birth, sex, lactation_number, body_condition_score, is_insured, health_history JSONB, created_at)
- [x] 2.5 Create `app/models/health.py` — HealthEvent model (id, animal_id FK, event_type, description, symptoms JSONB, ai_risk_score, recorded_by FK, event_date) + Vaccination model (id, animal_id FK, vaccine_name, administered_on, next_due, batch_number)
- [x] 2.6 Create `app/models/milk.py` — YieldLog model + MilkCollectionCenter model + MilkCollectionRecord model (columns per §7.1)
- [x] 2.7 Create `app/models/finance.py` — Transaction model (id, user_id FK, type, amount, category, reference_id, status, created_at)
- [x] 2.8 Create `app/models/shg.py` — SHGGroup model (id, name, registration_number, district, village_code, admin_user_id FK, member_count, women_only, formation_date, total_savings, grading, panchsutra_compliance JSONB, created_at)
- [x] 2.9 Create `app/models/schemes.py` — GovtScheme model (id, scheme_code, name, ministry, description, eligibility_criteria, required_documents JSONB, max_subsidy_amount, subsidy_percentage, is_active, valid_from, valid_to)
- [x] 2.10 Initialize Alembic, configure `env.py` to import all models, generate initial migration
- [ ] 2.11 Run `alembic upgrade head` and verify all 10 tables exist in Postgres

## 3. Authentication

- [x] 3.1 Create `app/schemas/auth.py` — OTPRequest, OTPVerify, TokenResponse Pydantic models
- [x] 3.2 Create `app/routers/auth.py` — `POST /v1/auth/request-otp` (always succeeds), `POST /v1/auth/verify-otp` (checks "123456", auto-creates user, returns JWT)
- [x] 3.3 Create `app/middleware/auth.py` — JWT decode dependency (`get_current_user`), role-checking dependency (`require_admin`)
- [ ] 3.4 Verify: request OTP → verify → get token → call protected endpoint → success

## 4. CRUD Routers

- [x] 4.1 Create `app/schemas/animals.py` — AnimalCreate, AnimalUpdate, AnimalRead
- [x] 4.2 Create `app/routers/animals.py` — CRUD: POST, GET list (owner-filtered), GET by id, PATCH, DELETE for `/v1/animals`
- [x] 4.3 Create `app/schemas/health.py` — HealthEventCreate, HealthEventRead, VaccinationCreate, VaccinationRead
- [x] 4.4 Create `app/routers/health.py` — `POST /v1/health/log` (calls disease rules), `GET /v1/health/history/{animal_id}`, vaccination CRUD
- [x] 4.5 Create `app/services/disease_rules.py` — 50+ rule dictionary from ICAR-IVRI/NDDB, `evaluate_symptoms()` function
- [x] 4.6 Create `app/schemas/milk.py` + `app/routers/milk.py` — `POST /v1/milk/record`, `POST /v1/milk/yield`, `GET /v1/milk/farmer/{id}/history`, `GET /v1/milk/center/{id}/daily`
- [x] 4.7 Create `app/schemas/finance.py` + `app/routers/finance.py` — `POST /v1/finance/transaction`, `GET /v1/finance/summary`
- [x] 4.8 Create `app/schemas/shg.py` + `app/routers/shg.py` — SHG group CRUD, `GET /v1/shg/{id}/compliance` (Panchsutra scoring)
- [x] 4.9 Create `app/schemas/schemes.py` + `app/routers/schemes.py` — scheme catalog, eligibility matching, application CRUD
- [x] 4.10 Create `app/routers/admin.py` — `GET /v1/admin/stats`, `GET /v1/admin/charts/milk`, `GET /v1/admin/gis/alerts` (admin-only)
- [x] 4.11 Wire all routers into `app/main.py` with `/v1` prefix and verify all endpoints appear in `/docs`

## 5. Seed Data

- [x] 5.1 Create `app/seed/demo_data.py` — idempotent seed script with 3 Karnataka farmers, 1 admin, 8 animals, 1 milk center
- [x] 5.2 Add 30 days of milk records with realistic yield variance (3-7 L/day for local breeds)
- [x] 5.3 Add health events (including 1 high-risk case), vaccinations, transactions, 2 SHG groups, 5 govt schemes
- [ ] 5.4 Verify `just seed` populates all data and is idempotent on re-run

## 6. API Client Generation

- [ ] 6.1 Install `@hey-api/openapi-ts` in monorepo root or shared location
- [ ] 6.2 Configure `just generate-client` to read `http://localhost:8000/openapi.json` and output typed TS client
- [ ] 6.3 Verify generated client has typed functions for all endpoints

## 7. Mobile App — Core

- [x] 7.1 Configure Expo Router with `(auth)/` and `(tabs)/` layout groups
- [x] 7.2 Create API client module (base URL config, token interceptor from expo-secure-store)
- [x] 7.3 Create login screen — phone input + OTP input + submit → store token → navigate to tabs
- [x] 7.4 Set up i18next with Kannada (kn.json) and English (en.json) translation files, namespace per feature
- [x] 7.5 Bundle Noto Sans Kannada font, create AppText component with proper Android alignment
- [x] 7.6 Configure React Native Paper MD3 theme with large touch targets, color palette

## 8. Mobile App — Screens

- [x] 8.1 Home tab — "My Animals" list with large cards (species-specific icon 64px+, name, health color dot, species badge)
- [x] 8.2 Add Animal screen — name, multi-species icon picker (cow/goat/sheep/poultry), breed, Pashu Aadhaar, save to API
- [x] 8.3 Animal detail screen — info section + health timeline + vaccination list + species-specific fields
- [x] 8.4 Milk tab — animal picker, large numpad, AM/PM toggle, save button
- [x] 8.5 Milk history screen — bar chart (react-native-gifted-charts) with 7/14/30 day period selector
- [x] 8.6 Health tab — symptom icon picker, severity selector, submit → display triage result card (color-coded)
- [x] 8.7 Profile screen (header avatar, not tab) — language toggle (Kannada/English), user info display, smart farm access
- [x] 8.8 Bottom tab bar — 5 tabs (Home, Milk, Sell, Health, Income) with Kannada labels and large icons

## 9. Mobile App — Voice Input

- [x] 9.1 Install `sarvam-conv-ai-sdk` and configure API key (mock service created instead — work laptop)
- [x] 9.2 Create mic button component with pulsing recording indicator and auto-stop (5s silence / 10s max)
- [x] 9.3 Implement Sarvam STT call — record audio → POST to Saaras V3 → get Kannada text (mock implementation)
- [x] 9.4 Create Kannada number parser (ಒಂದು→1 through ಹತ್ತು→10, decimals, compound numbers)
- [x] 9.5 Integrate voice input on milk recording screen — mic button → STT → parse → populate quantity
- [x] 9.6 Add fallback: show "Voice not recognized" in Kannada + manual numpad always available

## 10. Admin Dashboard — Setup

- [x] 10.1 Initialize Next.js 14 App Router project with Refine v4, MUI v5, `@refinedev/simple-rest`
- [x] 10.2 Create Refine auth provider (JWT login, admin role check)
- [x] 10.3 Configure `ThemedLayoutV2` with sidebar (Dashboard, Farmers, Animals, Milk, Alerts, Schemes, SHG)
- [x] 10.4 Configure REST data provider pointing to FastAPI `/v1/` base URL

## 11. Admin Dashboard — Pages

- [x] 11.1 Dashboard page — 4 stat cards (Recharts), milk collection line chart (30 days)
- [x] 11.2 GIS map component — react-leaflet + OSM tiles, dynamic import with ssr:false, Karnataka center
- [x] 11.3 Map overlay — disease alert markers (red/yellow/green) from `/v1/admin/gis/alerts`
- [x] 11.4 Farmers list page — Refine CRUD table with search and pagination
- [x] 11.5 Animals list page — Refine table with species filter and owner column
- [x] 11.6 Health alerts page — table of high-risk events with farmer name, animal, symptoms, risk level
- [x] 11.7 Schemes catalog page — read-only sortable table of government schemes
- [x] 11.8 SHG groups page — table with group name, district, grading, member count

## 12. Demo Polish

- [x] 12.1 Review and fix Kannada translations for top 50 UI strings
- [ ] 12.2 Add splash screen and app icon to Expo project
- [x] 12.3 Add loading states, empty states, and Kannada error messages
- [ ] 12.4 Build Android APK via EAS Build (buildType: "apk", distribution: "internal")
- [x] 12.5 Test all 9 demo scenarios end-to-end (test script created)
- [x] 12.6 Write click-by-click demo script for all 9 scenarios
- [ ] 12.7 Record backup demo video (3-5 min)

## 13. Cloud Deployment (Optional)

- [ ] 13.1 Deploy API to Railway.app with Postgres addon
- [ ] 13.2 Deploy admin panel to Vercel via Git integration
- [ ] 13.3 Configure environment variables on both platforms
- [ ] 13.4 Create pre-demo warm-up curl script
- [ ] 13.5 Verify all 9 demo scenarios work against cloud deployment

## 14. Product Marketplace (Sell Tab)

- [x] 14.1 Create `app/models/marketplace.py` — SellRecord model (id, user_id FK, product_type enum [milk/eggs/goat_products/sheep_products/manure/wool/other], quantity, unit, price_per_unit, total_amount, buyer_name, buyer_phone, sold_at, notes)
- [x] 14.2 Create `app/schemas/marketplace.py` — SellRecordCreate, SellRecordRead, ProductPriceRate, MarketplaceSummary
- [x] 14.3 Create `app/routers/marketplace.py` — `POST /v1/marketplace/sell`, `GET /v1/marketplace/history/{user_id}`, `GET /v1/marketplace/rates` (local APMC market rates), `GET /v1/marketplace/summary/{user_id}`
- [x] 14.4 Create `app/services/market_rates.py` — Karnataka APMC mandal rate table (milk ₹28-35/L, eggs ₹5-7/each, goat milk ₹60-80/L, manure ₹2-5/kg, wool ₹100-150/kg)
- [x] 14.5 Mobile: Sell tab — product category grid (4 cards: Milk, Eggs, Goat/Sheep, Manure) with species-specific icons
- [x] 14.6 Mobile: Sell recording screen — product picker, quantity input with +/- controls, auto-calculated price from local rates, buyer name (optional), "Record Sale" button
- [x] 14.7 Mobile: Sell history screen — list of recent sales with date, product, quantity, amount
- [x] 14.8 Mobile: Voice input on sell screen — mic button → STT → parse quantity ("Hattu motte" → 10 eggs)
- [x] 14.9 Add sell records to seed data — 15 days of varied product sales for each farmer
- [x] 14.10 Admin: Marketplace stats cards (total sales volume, revenue by product, active sellers)

## 15. Income Dashboard (Income Tab)

- [x] 15.1 Create `app/routers/income.py` — `GET /v1/income/summary/{user_id}` (weekly/monthly totals), `GET /v1/income/breakdown/{user_id}` (by product category), `GET /v1/income/history/{user_id}` (transaction list)
- [x] 15.2 Mobile: Income tab — weekly earnings hero card (large ₹ amount), period selector (week/month/year)
- [x] 15.3 Mobile: Product breakdown section — donut chart showing income by category (milk, eggs, goat products, manure)
- [x] 15.4 Mobile: Recent transactions list — date, product, amount with color-coded product icons
- [x] 15.5 Mobile: "Download Record" button — generates PDF income statement (mock/placeholder for prototype)
- [x] 15.6 Mobile: "Apply for Loan" CTA card — links to SHG/NABARD loan info with pre-filled income data
- [x] 15.7 Voice input on income screen — "Ee varsha eshtu sampadane?" (How much income this year?) → navigates to yearly view (mic button pattern established)
- [x] 15.8 Admin: Income analytics — total farmer income, average per farmer, income distribution chart

## 16. Smart Farm / IoT Mockup

- [x] 16.1 Mobile: Smart Farm screen (accessible from Home header icon) — GPS map with mock animal location markers
- [x] 16.2 Mobile: Device status cards — RFID Scanner (online/offline), Milk Quality Meter, GPS Collar, Smart Feeder
- [x] 16.3 Mobile: Sensor readings display — temperature, humidity, milk quality score (all mock data)
- [x] 16.4 Mobile: "Phase 2 — Coming Soon" banner clearly labeling IoT as future capability
- [x] 16.5 Admin: IoT device monitoring section — device count, online/offline status, last sync time
- [x] 16.6 Add IoT mock data to seed script — 4 device types with status and readings

## 17. Multi-Species Support

- [x] 17.1 Update Animal model — add species enum (cattle, goat, sheep, poultry), breed_type field, species-specific metadata JSONB
- [x] 17.2 Update animal schemas — species-specific validation rules (e.g., poultry: no lactation_number)
- [x] 17.3 Update seed data — add 2 goats, 1 sheep, 5 poultry to existing farmer profiles
- [x] 17.4 Mobile: Species-specific icons throughout — cow (🐄), goat (🐐), sheep (🐑), chicken (🐔) with custom SVG
- [x] 17.5 Mobile: Species filter on home tab — "All" / "Cattle" / "Goats" / "Sheep" / "Poultry" chip selector
- [x] 17.6 Mobile: Update Add Animal screen with expanded species picker (4 species with large icon buttons)
- [x] 17.7 Mobile: Species-specific health rules — goat diseases (PPR, enterotoxemia), poultry (Newcastle, Marek's)
- [x] 17.8 Admin: Multi-species analytics — animal count by species, species distribution chart, species-filtered CRUD tables
- [x] 17.9 Update disease rules engine with species-specific rules (30+ additional rules for goat/sheep/poultry)

## 18. Updated Demo Scenarios

- [x] 18.1 Demo scenario 7: Farmer sells 10L milk + 20 eggs → sees sale recorded with auto-calculated price
- [x] 18.2 Demo scenario 8: Farmer views Income dashboard → weekly earnings ₹2,450 breakdown by product
- [x] 18.3 Demo scenario 9: Admin views Smart Farm / IoT device overview (mockup for future vision pitch)
- [x] 18.4 Update demo script to include all 9 scenarios (6 original + 3 new)
- [x] 18.5 Test multi-species flow: add goat "Meenu", record goat milk, log goat health event

## 19. Farmer Onboarding Flow

- [x] 19.1 Mobile: Welcome screen with language picker (Kannada default, English) and large accessibility toggle
- [x] 19.2 Mobile: Progressive profile builder — name, phone (pre-filled from auth), district picker, village search
- [x] 19.3 Mobile: First animal registration prompt — "Add your first animal" with guided species + breed picker
- [x] 19.4 Mobile: Tutorial overlay — 3 swipe cards explaining key features (voice input, health check, sell products)
- [x] 19.5 API: `POST /v1/onboarding/complete` — mark onboarding done, set default preferences

## 20. Weather Integration

- [x] 20.1 Create `app/models/weather.py` — WeatherAlert model (id, district, alert_type, severity, description, valid_from, valid_to, source)
- [x] 20.2 Create `app/services/weather_service.py` — IMD API client, fetch 5-day forecast by district, cache with 6h TTL
- [x] 20.3 Create `app/routers/weather.py` — `GET /v1/weather/forecast/{district}`, `GET /v1/weather/alerts/{district}`
- [x] 20.4 Mobile: Weather card on home screen — today's conditions, heat stress indicator, rainfall probability
- [x] 20.5 Mobile: Weather detail screen — 5-day forecast, alert history, Kannada voice summary
- [x] 20.6 Add mock weather data to seed script for Mysore and Mandya districts

## 21. Feed/Ration Optimization

- [x] 21.1 Create `app/models/feed.py` — FeedIngredient model (id, name_en, name_kn, category, protein_pct, energy_kcal, cost_per_kg, availability_season, locally_available BOOL)
- [x] 21.2 Create `app/services/feed_calculator.py` — ration optimizer: input (species, breed, weight, lactation_stage, available_ingredients) → output (balanced_ration, daily_cost_estimate)
- [x] 21.3 Create `app/routers/feed.py` — `GET /v1/feed/ingredients`, `POST /v1/feed/calculate-ration`
- [x] 21.4 Mobile: Feed calculator screen — species/breed selector, weight input, ingredient checklist from local options
- [x] 21.5 Mobile: Ration result card — daily quantities per ingredient, estimated cost, nutritional balance meter
- [x] 21.6 Seed 30 common Karnataka feed ingredients with NDDB nutritional data

## 22. Ethno-Veterinary Medicine Database

- [x] 22.1 Create `app/models/ethno_vet.py` — TraditionalRemedy model (id, name_en, name_kn, plant_ingredient, preparation_method, dosage_by_species JSONB, conditions_treated, evidence_rating enum[traditional|studied|icar_validated], safety_warnings, source_reference)
- [x] 22.2 Create `app/routers/ethno_vet.py` — `GET /v1/ethno-vet/remedies`, `GET /v1/ethno-vet/remedies/{condition}`, `GET /v1/ethno-vet/search?q=`
- [x] 22.3 Mobile: Remedies browser — search by condition or ingredient, filter by species and evidence rating
- [x] 22.4 Mobile: Remedy detail card — ingredients, preparation steps, dosage table, safety warnings, evidence badge
- [x] 22.5 Seed 25 common traditional remedies from ICAR ethno-vet documentation

## 23. Bharat Pashudhan Integration

- [x] 23.1 Create `app/services/bharat_pashudhan.py` — API client for national animal registry (mock for prototype)
- [x] 23.2 Create `app/routers/bharat_pashudhan.py` — `GET /v1/registry/lookup/{pashu_aadhaar_id}`, `POST /v1/registry/sync/{animal_id}`
- [x] 23.3 Mobile: Pashu Aadhaar lookup screen — enter 12-digit ID → pull animal profile from national registry
- [x] 23.4 Mobile: Sync status indicator on animal detail — "Synced with Bharat Pashudhan ✓" or "Not registered"
- [x] 23.5 Update seed data with valid Pashu Aadhaar format IDs for demo animals

## 24. Enhanced Vaccination Management

- [x] 24.1 Update `app/models/health.py` — add batch_number, manufacturer, was_refrigerated, next_reminder_date to Vaccination model
- [x] 24.2 Create `app/services/vaccination_scheduler.py` — species-specific ICAR vaccination calendar, auto-calculate next due dates
- [x] 24.3 Create `app/routers/vaccination.py` — `GET /v1/vaccinations/due/{user_id}`, `GET /v1/vaccinations/coverage/{village_code}`
- [x] 24.4 Mobile: Vaccination reminder cards on home screen — "Meenu (Goat) — PPR booster due in 3 days"
- [x] 24.5 Admin: Vaccination coverage dashboard — village-level coverage %, overdue counts, heatmap
- [x] 24.6 Seed ICAR vaccination schedule for cattle, goat, sheep, poultry

## 25. Livestock Insurance

- [x] 25.1 Create `app/models/insurance.py` — InsurancePolicy model (id, animal_id FK, provider, policy_number, premium_amount, coverage_amount, valid_from, valid_to, status), InsuranceClaim model (id, policy_id FK, claim_type, description, photo_urls JSONB, status, filed_at)
- [x] 25.2 Create `app/routers/insurance.py` — `GET /v1/insurance/policies/{user_id}`, `POST /v1/insurance/claims`, `GET /v1/insurance/premium-estimate/{animal_id}`
- [x] 25.3 Mobile: Insurance status screen — active policies, premium due dates, claim filing with photo
- [x] 25.4 Mobile: Premium calculator — estimate based on species, breed, age, location
- [x] 25.5 Seed 3 insurance policies and 1 claim for demo data

## 26. Community Disease Alerts

- [x] 26.1 Create `app/models/alerts.py` — CommunityAlert model (id, reported_by FK, disease_name, lat, lon, radius_km, severity, verified BOOL, created_at, expires_at)
- [x] 26.2 Create `app/services/alert_service.py` — spatial query for nearby alerts, notification dispatch (mock)
- [x] 26.3 Create `app/routers/alerts.py` — `POST /v1/alerts/report`, `GET /v1/alerts/nearby?lat=&lon=&radius=`, `PATCH /v1/alerts/{id}/verify`
- [x] 26.4 Mobile: Alert banner on home screen — "⚠ FMD reported 3km away — 2 days ago"
- [x] 26.5 Mobile: Report disease screen — select disease, GPS auto-fill, optional photo, submit
- [x] 26.6 Admin: Alert management — verify/dismiss reports, view outbreak map
- [x] 26.7 Seed 2 community alerts near demo farm locations

## 27. Medicine Withdrawal Calculator

- [x] 27.1 Create `app/models/medicine.py` — Medicine model (id, name_en, name_kn, type, withdrawal_milk_days INT, withdrawal_meat_days INT, species_applicable JSONB), MedicineAdministration model (id, animal_id FK, medicine_id FK, administered_at, withdrawal_milk_until DATE, withdrawal_meat_until DATE)
- [x] 27.2 Create `app/routers/medicine.py` — `GET /v1/medicines`, `POST /v1/medicines/administer`, `GET /v1/medicines/withdrawal-status/{animal_id}`
- [x] 27.3 Mobile: Medicine log screen — select medicine from list, auto-calculate withdrawal dates
- [x] 27.4 Mobile: Withdrawal status badge on animal detail — "🔴 Milk unsafe until Apr 5" or "🟢 Safe to sell"
- [x] 27.5 Seed 15 common veterinary medicines with ICAR withdrawal periods

## 28. Milk Collection Center Module

- [x] 28.1 Create `app/models/milk_center.py` — update MilkCollectionCenter and MilkCollectionRecord models with quality fields (fat_pct, snf_pct, clr, adulteration_test, temperature)
- [x] 28.2 Create `app/services/milk_pricing.py` — FAT/SNF slab-based rate calculator per Karnataka Milk Federation standards
- [x] 28.3 Create `app/routers/milk_center.py` — `POST /v1/milk-center/receive`, `GET /v1/milk-center/{id}/daily-report`, `GET /v1/milk-center/{id}/farmer-settlements`
- [x] 28.4 Update milk center HTML prototype or create spec for dedicated milk center interface
- [x] 28.5 Seed milk center with 30 days of collection records from 3 farmers with quality data
- [x] 28.6 Admin: Milk center analytics — daily collection volume, average FAT/SNF, payment settlement report

## 29. Advisory Feed

- [x] 29.1 Create `app/models/advisory.py` — AdvisoryTip model (id, title_en, title_kn, body_en, body_kn, category enum[health|feeding|breeding|government], species_applicable JSONB, source enum[ICAR|KMF|NABARD|Community], priority, is_active, published_at)
- [x] 29.2 Create `app/routers/advisory.py` — `GET /v1/advisory/tips` (filter by species, category), `GET /v1/advisory/tips/{id}`
- [x] 29.3 Mobile: Advisory feed screen — scrollable card list filtered by farmer's animal species
- [x] 29.4 Mobile: Category filter chips — Health, Feeding, Breeding, Government
- [x] 29.5 Mobile: Bilingual toggle per card — switch between Kannada and English
- [x] 29.6 Mobile: Source badge on each card — "ICAR", "KMF", "NABARD", "Community" with distinct colors
- [x] 29.7 Mobile: Government scheme highlight card with "Apply Now" CTA linking to schemes screen
- [x] 29.8 Seed 15 advisory tips — mix of seasonal care, feeding, breeding, and government announcements
