## 1. Monorepo Scaffold

- [ ] 1.1 Create `pashu-erp/` root with `docker-compose.yml` (Postgres 16 + API), `.env.example`, `pnpm-workspace.yaml`
- [ ] 1.2 Create `justfile` with tasks: `dev`, `test`, `seed`, `generate-client`, `lint`, `migrate`
- [ ] 1.3 Create `packages/api/` with `pyproject.toml` (FastAPI, SQLAlchemy, Alembic, asyncpg, pydantic-settings, python-jose, passlib, uvicorn)
- [ ] 1.4 Create `packages/admin/` with `package.json` (Next.js 14, Refine v4, MUI v5, Recharts, react-leaflet)
- [ ] 1.5 Create `packages/mobile/` — init Expo SDK 52 project with expo-router, react-native-paper, i18next, expo-secure-store, react-native-gifted-charts
- [ ] 1.6 Verify `docker compose up` starts Postgres and API serves `GET /docs`

## 2. Database Models & Migrations

- [ ] 2.1 Create `app/database.py` — async SQLAlchemy engine, `async_sessionmaker` with `expire_on_commit=False`, `pool_pre_ping=True`
- [ ] 2.2 Create `app/config.py` — pydantic-settings `Settings` class loading from `.env`
- [ ] 2.3 Create `app/models/user.py` — User model (id, role, phone, name, lang_pref, location_district, location_state, village_code, preferences, created_at, updated_at)
- [ ] 2.4 Create `app/models/animal.py` — Animal model (id, user_id FK, pashu_aadhaar_id, species, breed, breed_type, tag_id, date_of_birth, sex, lactation_number, body_condition_score, is_insured, health_history JSONB, created_at)
- [ ] 2.5 Create `app/models/health.py` — HealthEvent model (id, animal_id FK, event_type, description, symptoms JSONB, ai_risk_score, recorded_by FK, event_date) + Vaccination model (id, animal_id FK, vaccine_name, administered_on, next_due, batch_number)
- [ ] 2.6 Create `app/models/milk.py` — YieldLog model + MilkCollectionCenter model + MilkCollectionRecord model (columns per §7.1)
- [ ] 2.7 Create `app/models/finance.py` — Transaction model (id, user_id FK, type, amount, category, reference_id, status, created_at)
- [ ] 2.8 Create `app/models/shg.py` — SHGGroup model (id, name, registration_number, district, village_code, admin_user_id FK, member_count, women_only, formation_date, total_savings, grading, panchsutra_compliance JSONB, created_at)
- [ ] 2.9 Create `app/models/schemes.py` — GovtScheme model (id, scheme_code, name, ministry, description, eligibility_criteria, required_documents JSONB, max_subsidy_amount, subsidy_percentage, is_active, valid_from, valid_to)
- [ ] 2.10 Initialize Alembic, configure `env.py` to import all models, generate initial migration
- [ ] 2.11 Run `alembic upgrade head` and verify all 10 tables exist in Postgres

## 3. Authentication

- [ ] 3.1 Create `app/schemas/auth.py` — OTPRequest, OTPVerify, TokenResponse Pydantic models
- [ ] 3.2 Create `app/routers/auth.py` — `POST /v1/auth/request-otp` (always succeeds), `POST /v1/auth/verify-otp` (checks "123456", auto-creates user, returns JWT)
- [ ] 3.3 Create `app/middleware/auth.py` — JWT decode dependency (`get_current_user`), role-checking dependency (`require_admin`)
- [ ] 3.4 Verify: request OTP → verify → get token → call protected endpoint → success

## 4. CRUD Routers

- [ ] 4.1 Create `app/schemas/animals.py` — AnimalCreate, AnimalUpdate, AnimalRead
- [ ] 4.2 Create `app/routers/animals.py` — CRUD: POST, GET list (owner-filtered), GET by id, PATCH, DELETE for `/v1/animals`
- [ ] 4.3 Create `app/schemas/health.py` — HealthEventCreate, HealthEventRead, VaccinationCreate, VaccinationRead
- [ ] 4.4 Create `app/routers/health.py` — `POST /v1/health/log` (calls disease rules), `GET /v1/health/history/{animal_id}`, vaccination CRUD
- [ ] 4.5 Create `app/services/disease_rules.py` — 50+ rule dictionary from ICAR-IVRI/NDDB, `evaluate_symptoms()` function
- [ ] 4.6 Create `app/schemas/milk.py` + `app/routers/milk.py` — `POST /v1/milk/record`, `POST /v1/milk/yield`, `GET /v1/milk/farmer/{id}/history`, `GET /v1/milk/center/{id}/daily`
- [ ] 4.7 Create `app/schemas/finance.py` + `app/routers/finance.py` — `POST /v1/finance/transaction`, `GET /v1/finance/summary`
- [ ] 4.8 Create `app/schemas/shg.py` + `app/routers/shg.py` — SHG group CRUD, `GET /v1/shg/{id}/compliance` (Panchsutra scoring)
- [ ] 4.9 Create `app/schemas/schemes.py` + `app/routers/schemes.py` — scheme catalog, eligibility matching, application CRUD
- [ ] 4.10 Create `app/routers/admin.py` — `GET /v1/admin/stats`, `GET /v1/admin/charts/milk`, `GET /v1/admin/gis/alerts` (admin-only)
- [ ] 4.11 Wire all routers into `app/main.py` with `/v1` prefix and verify all endpoints appear in `/docs`

## 5. Seed Data

- [ ] 5.1 Create `app/seed/demo_data.py` — idempotent seed script with 3 Karnataka farmers, 1 admin, 8 animals, 1 milk center
- [ ] 5.2 Add 30 days of milk records with realistic yield variance (3-7 L/day for local breeds)
- [ ] 5.3 Add health events (including 1 high-risk case), vaccinations, transactions, 2 SHG groups, 5 govt schemes
- [ ] 5.4 Verify `just seed` populates all data and is idempotent on re-run

## 6. API Client Generation

- [ ] 6.1 Install `@hey-api/openapi-ts` in monorepo root or shared location
- [ ] 6.2 Configure `just generate-client` to read `http://localhost:8000/openapi.json` and output typed TS client
- [ ] 6.3 Verify generated client has typed functions for all endpoints

## 7. Mobile App — Core

- [ ] 7.1 Configure Expo Router with `(auth)/` and `(tabs)/` layout groups
- [ ] 7.2 Create API client module (base URL config, token interceptor from expo-secure-store)
- [ ] 7.3 Create login screen — phone input + OTP input + submit → store token → navigate to tabs
- [ ] 7.4 Set up i18next with Kannada (kn.json) and English (en.json) translation files, namespace per feature
- [ ] 7.5 Bundle Noto Sans Kannada font, create AppText component with proper Android alignment
- [ ] 7.6 Configure React Native Paper MD3 theme with large touch targets, color palette

## 8. Mobile App — Screens

- [ ] 8.1 Home tab — "My Animals" list with large cards (species-specific icon 64px+, name, health color dot, species badge)
- [ ] 8.2 Add Animal screen — name, multi-species icon picker (cow/goat/sheep/poultry), breed, Pashu Aadhaar, save to API
- [ ] 8.3 Animal detail screen — info section + health timeline + vaccination list + species-specific fields
- [ ] 8.4 Milk tab — animal picker, large numpad, AM/PM toggle, save button
- [ ] 8.5 Milk history screen — bar chart (react-native-gifted-charts) with 7/14/30 day period selector
- [ ] 8.6 Health tab — symptom icon picker, severity selector, submit → display triage result card (color-coded)
- [ ] 8.7 Profile screen (header avatar, not tab) — language toggle (Kannada/English), user info display, smart farm access
- [ ] 8.8 Bottom tab bar — 5 tabs (Home, Milk, Sell, Health, Income) with Kannada labels and large icons

## 9. Mobile App — Voice Input

- [ ] 9.1 Install `sarvam-conv-ai-sdk` and configure API key
- [ ] 9.2 Create mic button component with pulsing recording indicator and auto-stop (5s silence / 10s max)
- [ ] 9.3 Implement Sarvam STT call — record audio → POST to Saaras V3 → get Kannada text
- [ ] 9.4 Create Kannada number parser (ಒಂದು→1 through ಹತ್ತು→10, decimals, compound numbers)
- [ ] 9.5 Integrate voice input on milk recording screen — mic button → STT → parse → populate quantity
- [ ] 9.6 Add fallback: show "Voice not recognized" in Kannada + manual numpad always available

## 10. Admin Dashboard — Setup

- [ ] 10.1 Initialize Next.js 14 App Router project with Refine v4, MUI v5, `@refinedev/simple-rest`
- [ ] 10.2 Create Refine auth provider (JWT login, admin role check)
- [ ] 10.3 Configure `ThemedLayoutV2` with sidebar (Dashboard, Farmers, Animals, Milk, Alerts, Schemes, SHG)
- [ ] 10.4 Configure REST data provider pointing to FastAPI `/v1/` base URL

## 11. Admin Dashboard — Pages

- [ ] 11.1 Dashboard page — 4 stat cards (Recharts), milk collection line chart (30 days)
- [ ] 11.2 GIS map component — react-leaflet + OSM tiles, dynamic import with ssr:false, Karnataka center
- [ ] 11.3 Map overlay — disease alert markers (red/yellow/green) from `/v1/admin/gis/alerts`
- [ ] 11.4 Farmers list page — Refine CRUD table with search and pagination
- [ ] 11.5 Animals list page — Refine table with species filter and owner column
- [ ] 11.6 Health alerts page — table of high-risk events with farmer name, animal, symptoms, risk level
- [ ] 11.7 Schemes catalog page — read-only sortable table of government schemes
- [ ] 11.8 SHG groups page — table with group name, district, grading, member count

## 12. Demo Polish

- [ ] 12.1 Review and fix Kannada translations for top 50 UI strings
- [ ] 12.2 Add splash screen and app icon to Expo project
- [ ] 12.3 Add loading states, empty states, and Kannada error messages
- [ ] 12.4 Build Android APK via EAS Build (buildType: "apk", distribution: "internal")
- [ ] 12.5 Test all 9 demo scenarios end-to-end on Android device/emulator
- [ ] 12.6 Write click-by-click demo script for all 9 scenarios
- [ ] 12.7 Record backup demo video (3-5 min)

## 13. Cloud Deployment (Optional)

- [ ] 13.1 Deploy API to Railway.app with Postgres addon
- [ ] 13.2 Deploy admin panel to Vercel via Git integration
- [ ] 13.3 Configure environment variables on both platforms
- [ ] 13.4 Create pre-demo warm-up curl script
- [ ] 13.5 Verify all 9 demo scenarios work against cloud deployment

## 14. Product Marketplace (Sell Tab)

- [ ] 14.1 Create `app/models/marketplace.py` — SellRecord model (id, user_id FK, product_type enum [milk/eggs/goat_products/sheep_products/manure/wool/other], quantity, unit, price_per_unit, total_amount, buyer_name, buyer_phone, sold_at, notes)
- [ ] 14.2 Create `app/schemas/marketplace.py` — SellRecordCreate, SellRecordRead, ProductPriceRate, MarketplaceSummary
- [ ] 14.3 Create `app/routers/marketplace.py` — `POST /v1/marketplace/sell`, `GET /v1/marketplace/history/{user_id}`, `GET /v1/marketplace/rates` (local APMC market rates), `GET /v1/marketplace/summary/{user_id}`
- [ ] 14.4 Create `app/services/market_rates.py` — Karnataka APMC mandal rate table (milk ₹28-35/L, eggs ₹5-7/each, goat milk ₹60-80/L, manure ₹2-5/kg, wool ₹100-150/kg)
- [ ] 14.5 Mobile: Sell tab — product category grid (4 cards: Milk, Eggs, Goat/Sheep, Manure) with species-specific icons
- [ ] 14.6 Mobile: Sell recording screen — product picker, quantity input with +/- controls, auto-calculated price from local rates, buyer name (optional), "Record Sale" button
- [ ] 14.7 Mobile: Sell history screen — list of recent sales with date, product, quantity, amount
- [ ] 14.8 Mobile: Voice input on sell screen — mic button → STT → parse quantity ("Hattu motte" → 10 eggs)
- [ ] 14.9 Add sell records to seed data — 15 days of varied product sales for each farmer
- [ ] 14.10 Admin: Marketplace stats cards (total sales volume, revenue by product, active sellers)

## 15. Income Dashboard (Income Tab)

- [ ] 15.1 Create `app/routers/income.py` — `GET /v1/income/summary/{user_id}` (weekly/monthly totals), `GET /v1/income/breakdown/{user_id}` (by product category), `GET /v1/income/history/{user_id}` (transaction list)
- [ ] 15.2 Mobile: Income tab — weekly earnings hero card (large ₹ amount), period selector (week/month/year)
- [ ] 15.3 Mobile: Product breakdown section — donut chart showing income by category (milk, eggs, goat products, manure)
- [ ] 15.4 Mobile: Recent transactions list — date, product, amount with color-coded product icons
- [ ] 15.5 Mobile: "Download Record" button — generates PDF income statement (mock/placeholder for prototype)
- [ ] 15.6 Mobile: "Apply for Loan" CTA card — links to SHG/NABARD loan info with pre-filled income data
- [ ] 15.7 Voice input on income screen — "Ee varsha eshtu sampadane?" (How much income this year?) → navigates to yearly view
- [ ] 15.8 Admin: Income analytics — total farmer income, average per farmer, income distribution chart

## 16. Smart Farm / IoT Mockup

- [ ] 16.1 Mobile: Smart Farm screen (accessible from Home header icon) — GPS map with mock animal location markers
- [ ] 16.2 Mobile: Device status cards — RFID Scanner (online/offline), Milk Quality Meter, GPS Collar, Smart Feeder
- [ ] 16.3 Mobile: Sensor readings display — temperature, humidity, milk quality score (all mock data)
- [ ] 16.4 Mobile: "Phase 2 — Coming Soon" banner clearly labeling IoT as future capability
- [ ] 16.5 Admin: IoT device monitoring section — device count, online/offline status, last sync time
- [ ] 16.6 Add IoT mock data to seed script — 4 device types with status and readings

## 17. Multi-Species Support

- [ ] 17.1 Update Animal model — add species enum (cattle, goat, sheep, poultry), breed_type field, species-specific metadata JSONB
- [ ] 17.2 Update animal schemas — species-specific validation rules (e.g., poultry: no lactation_number)
- [ ] 17.3 Update seed data — add 2 goats, 1 sheep, 5 poultry to existing farmer profiles
- [ ] 17.4 Mobile: Species-specific icons throughout — cow (🐄), goat (🐐), sheep (🐑), chicken (🐔) with custom SVG
- [ ] 17.5 Mobile: Species filter on home tab — "All" / "Cattle" / "Goats" / "Sheep" / "Poultry" chip selector
- [ ] 17.6 Mobile: Update Add Animal screen with expanded species picker (4 species with large icon buttons)
- [ ] 17.7 Mobile: Species-specific health rules — goat diseases (PPR, enterotoxemia), poultry (Newcastle, Marek's)
- [ ] 17.8 Admin: Multi-species analytics — animal count by species, species distribution chart, species-filtered CRUD tables
- [ ] 17.9 Update disease rules engine with species-specific rules (30+ additional rules for goat/sheep/poultry)

## 18. Updated Demo Scenarios

- [ ] 18.1 Demo scenario 7: Farmer sells 10L milk + 20 eggs → sees sale recorded with auto-calculated price
- [ ] 18.2 Demo scenario 8: Farmer views Income dashboard → weekly earnings ₹2,450 breakdown by product
- [ ] 18.3 Demo scenario 9: Admin views Smart Farm / IoT device overview (mockup for future vision pitch)
- [ ] 18.4 Update demo script to include all 9 scenarios (6 original + 3 new)
- [ ] 18.5 Test multi-species flow: add goat "Meenu", record goat milk, log goat health event

## 19. Farmer Onboarding Flow

- [ ] 19.1 Mobile: Welcome screen with language picker (Kannada default, English) and large accessibility toggle
- [ ] 19.2 Mobile: Progressive profile builder — name, phone (pre-filled from auth), district picker, village search
- [ ] 19.3 Mobile: First animal registration prompt — "Add your first animal" with guided species + breed picker
- [ ] 19.4 Mobile: Tutorial overlay — 3 swipe cards explaining key features (voice input, health check, sell products)
- [ ] 19.5 API: `POST /v1/onboarding/complete` — mark onboarding done, set default preferences

## 20. Weather Integration

- [ ] 20.1 Create `app/models/weather.py` — WeatherAlert model (id, district, alert_type, severity, description, valid_from, valid_to, source)
- [ ] 20.2 Create `app/services/weather_service.py` — IMD API client, fetch 5-day forecast by district, cache with 6h TTL
- [ ] 20.3 Create `app/routers/weather.py` — `GET /v1/weather/forecast/{district}`, `GET /v1/weather/alerts/{district}`
- [ ] 20.4 Mobile: Weather card on home screen — today's conditions, heat stress indicator, rainfall probability
- [ ] 20.5 Mobile: Weather detail screen — 5-day forecast, alert history, Kannada voice summary
- [ ] 20.6 Add mock weather data to seed script for Mysore and Mandya districts

## 21. Feed/Ration Optimization

- [ ] 21.1 Create `app/models/feed.py` — FeedIngredient model (id, name_en, name_kn, category, protein_pct, energy_kcal, cost_per_kg, availability_season, locally_available BOOL)
- [ ] 21.2 Create `app/services/feed_calculator.py` — ration optimizer: input (species, breed, weight, lactation_stage, available_ingredients) → output (balanced_ration, daily_cost_estimate)
- [ ] 21.3 Create `app/routers/feed.py` — `GET /v1/feed/ingredients`, `POST /v1/feed/calculate-ration`
- [ ] 21.4 Mobile: Feed calculator screen — species/breed selector, weight input, ingredient checklist from local options
- [ ] 21.5 Mobile: Ration result card — daily quantities per ingredient, estimated cost, nutritional balance meter
- [ ] 21.6 Seed 30 common Karnataka feed ingredients with NDDB nutritional data

## 22. Ethno-Veterinary Medicine Database

- [ ] 22.1 Create `app/models/ethno_vet.py` — TraditionalRemedy model (id, name_en, name_kn, plant_ingredient, preparation_method, dosage_by_species JSONB, conditions_treated, evidence_rating enum[traditional|studied|icar_validated], safety_warnings, source_reference)
- [ ] 22.2 Create `app/routers/ethno_vet.py` — `GET /v1/ethno-vet/remedies`, `GET /v1/ethno-vet/remedies/{condition}`, `GET /v1/ethno-vet/search?q=`
- [ ] 22.3 Mobile: Remedies browser — search by condition or ingredient, filter by species and evidence rating
- [ ] 22.4 Mobile: Remedy detail card — ingredients, preparation steps, dosage table, safety warnings, evidence badge
- [ ] 22.5 Seed 25 common traditional remedies from ICAR ethno-vet documentation

## 23. Bharat Pashudhan Integration

- [ ] 23.1 Create `app/services/bharat_pashudhan.py` — API client for national animal registry (mock for prototype)
- [ ] 23.2 Create `app/routers/bharat_pashudhan.py` — `GET /v1/registry/lookup/{pashu_aadhaar_id}`, `POST /v1/registry/sync/{animal_id}`
- [ ] 23.3 Mobile: Pashu Aadhaar lookup screen — enter 12-digit ID → pull animal profile from national registry
- [ ] 23.4 Mobile: Sync status indicator on animal detail — "Synced with Bharat Pashudhan ✓" or "Not registered"
- [ ] 23.5 Update seed data with valid Pashu Aadhaar format IDs for demo animals

## 24. Enhanced Vaccination Management

- [ ] 24.1 Update `app/models/health.py` — add batch_number, manufacturer, was_refrigerated, next_reminder_date to Vaccination model
- [ ] 24.2 Create `app/services/vaccination_scheduler.py` — species-specific ICAR vaccination calendar, auto-calculate next due dates
- [ ] 24.3 Create `app/routers/vaccination.py` — `GET /v1/vaccinations/due/{user_id}`, `GET /v1/vaccinations/coverage/{village_code}`
- [ ] 24.4 Mobile: Vaccination reminder cards on home screen — "Meenu (Goat) — PPR booster due in 3 days"
- [ ] 24.5 Admin: Vaccination coverage dashboard — village-level coverage %, overdue counts, heatmap
- [ ] 24.6 Seed ICAR vaccination schedule for cattle, goat, sheep, poultry

## 25. Livestock Insurance

- [ ] 25.1 Create `app/models/insurance.py` — InsurancePolicy model (id, animal_id FK, provider, policy_number, premium_amount, coverage_amount, valid_from, valid_to, status), InsuranceClaim model (id, policy_id FK, claim_type, description, photo_urls JSONB, status, filed_at)
- [ ] 25.2 Create `app/routers/insurance.py` — `GET /v1/insurance/policies/{user_id}`, `POST /v1/insurance/claims`, `GET /v1/insurance/premium-estimate/{animal_id}`
- [ ] 25.3 Mobile: Insurance status screen — active policies, premium due dates, claim filing with photo
- [ ] 25.4 Mobile: Premium calculator — estimate based on species, breed, age, location
- [ ] 25.5 Seed 3 insurance policies and 1 claim for demo data

## 26. Community Disease Alerts

- [ ] 26.1 Create `app/models/alerts.py` — CommunityAlert model (id, reported_by FK, disease_name, lat, lon, radius_km, severity, verified BOOL, created_at, expires_at)
- [ ] 26.2 Create `app/services/alert_service.py` — spatial query for nearby alerts, notification dispatch (mock)
- [ ] 26.3 Create `app/routers/alerts.py` — `POST /v1/alerts/report`, `GET /v1/alerts/nearby?lat=&lon=&radius=`, `PATCH /v1/alerts/{id}/verify`
- [ ] 26.4 Mobile: Alert banner on home screen — "⚠ FMD reported 3km away — 2 days ago"
- [ ] 26.5 Mobile: Report disease screen — select disease, GPS auto-fill, optional photo, submit
- [ ] 26.6 Admin: Alert management — verify/dismiss reports, view outbreak map
- [ ] 26.7 Seed 2 community alerts near demo farm locations

## 27. Medicine Withdrawal Calculator

- [ ] 27.1 Create `app/models/medicine.py` — Medicine model (id, name_en, name_kn, type, withdrawal_milk_days INT, withdrawal_meat_days INT, species_applicable JSONB), MedicineAdministration model (id, animal_id FK, medicine_id FK, administered_at, withdrawal_milk_until DATE, withdrawal_meat_until DATE)
- [ ] 27.2 Create `app/routers/medicine.py` — `GET /v1/medicines`, `POST /v1/medicines/administer`, `GET /v1/medicines/withdrawal-status/{animal_id}`
- [ ] 27.3 Mobile: Medicine log screen — select medicine from list, auto-calculate withdrawal dates
- [ ] 27.4 Mobile: Withdrawal status badge on animal detail — "🔴 Milk unsafe until Apr 5" or "🟢 Safe to sell"
- [ ] 27.5 Seed 15 common veterinary medicines with ICAR withdrawal periods

## 28. Milk Collection Center Module

- [ ] 28.1 Create `app/models/milk_center.py` — update MilkCollectionCenter and MilkCollectionRecord models with quality fields (fat_pct, snf_pct, clr, adulteration_test, temperature)
- [ ] 28.2 Create `app/services/milk_pricing.py` — FAT/SNF slab-based rate calculator per Karnataka Milk Federation standards
- [ ] 28.3 Create `app/routers/milk_center.py` — `POST /v1/milk-center/receive`, `GET /v1/milk-center/{id}/daily-report`, `GET /v1/milk-center/{id}/farmer-settlements`
- [ ] 28.4 Update milk center HTML prototype or create spec for dedicated milk center interface
- [ ] 28.5 Seed milk center with 30 days of collection records from 3 farmers with quality data
- [ ] 28.6 Admin: Milk center analytics — daily collection volume, average FAT/SNF, payment settlement report

## 29. Advisory Feed

- [ ] 29.1 Create `app/models/advisory.py` — AdvisoryTip model (id, title_en, title_kn, body_en, body_kn, category enum[health|feeding|breeding|government], species_applicable JSONB, source enum[ICAR|KMF|NABARD|Community], priority, is_active, published_at)
- [ ] 29.2 Create `app/routers/advisory.py` — `GET /v1/advisory/tips` (filter by species, category), `GET /v1/advisory/tips/{id}`
- [ ] 29.3 Mobile: Advisory feed screen — scrollable card list filtered by farmer's animal species
- [ ] 29.4 Mobile: Category filter chips — Health, Feeding, Breeding, Government
- [ ] 29.5 Mobile: Bilingual toggle per card — switch between Kannada and English
- [ ] 29.6 Mobile: Source badge on each card — "ICAR", "KMF", "NABARD", "Community" with distinct colors
- [ ] 29.7 Mobile: Government scheme highlight card with "Apply Now" CTA linking to schemes screen
- [ ] 29.8 Seed 15 advisory tips — mix of seasonal care, feeding, breeding, and government announcements
