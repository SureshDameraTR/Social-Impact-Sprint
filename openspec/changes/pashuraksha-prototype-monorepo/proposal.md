## Why

The PashuRaksha ERP has comprehensive architecture blueprints (3,622 lines across 3 docs) but no working code. RDO stakeholders need a **live demo** at the scoping call (April 27, 2026) to validate the concept before committing to full implementation. Building a functional prototype — monorepo with clear package boundaries for future repo extraction — bridges the gap between blueprint and product while proving the 6 core farmer journeys work end-to-end.

## What Changes

- **New**: Monorepo scaffold (`pashu-erp/`) with 3 independent packages: `api` (Python/FastAPI), `admin` (Next.js/Refine), `mobile` (Expo/React Native)
- **New**: FastAPI backend with 10 prototype DB entities, async SQLAlchemy, Alembic migrations, JWT auth (mock OTP), CRUD routers, admin aggregation endpoints
- **New**: Rule-based disease triage engine (50+ veterinary rules from ICAR-IVRI/NDDB guidelines)
- **New**: Expo mobile app — farmer auth, animal management, milk recording with Kannada voice input (Sarvam AI), health logging with risk alerts, product marketplace (sell milk/eggs/manure), income dashboard with earnings breakdown, IoT/Smart Farm mockup screen, multi-species support (cattle/goat/sheep/poultry), i18n (kn/en)
- **New**: Next.js admin dashboard — farmer/animal CRUD tables, milk collection charts, disease alert GIS map, govt schemes catalog, marketplace transaction stats, IoT device monitoring, multi-species analytics
- **New**: Docker Compose for local dev (Postgres 16 + API), seed script with realistic Karnataka demo data
- **New**: OpenAPI spec auto-generated from FastAPI, serving as the cross-package contract
- **Architectural decision**: Packages communicate only via HTTP API (no shared imports) — enabling future repo-per-package split

## Capabilities

### New Capabilities
- `monorepo-scaffold`: Root monorepo structure with Docker, env config, and package boundaries designed for future repo extraction
- `api-backend`: FastAPI monolith with 10 entities, async ORM, migrations, config, and OpenAPI spec generation
- `api-auth`: Mock OTP login + JWT HS256 token issuance/validation middleware
- `api-animals`: Animal CRUD with Pashu Aadhaar support (§7.1 ANIMAL entity)
- `api-health`: Health event logging + rule-based disease triage (§6.2, §9.4 Phase 0)
- `api-milk`: Milk collection recording, farmer history, center daily summaries (§6.9)
- `api-finance`: Transaction recording and financial summaries (§6.6)
- `api-shg`: SHG group management and NABARD Panchsutra compliance scoring (§6.11)
- `api-schemes`: Government scheme catalog, eligibility matching, application tracking (§6.10)
- `api-admin-stats`: Admin aggregation endpoints — dashboard stats, chart data, GIS data
- `api-seed-data`: Idempotent seed script with 3 farmers, 8 animals, 30 days milk data, health events
- `mobile-app`: Expo farmer app — auth, animals, milk recording, health logging, voice input, i18n
- `mobile-voice`: Sarvam AI Kannada STT integration for voice-based milk recording
- `mobile-sell`: Product marketplace — sell milk, eggs, goat/sheep products, manure with quantity picker + auto-price calculation
- `mobile-income`: Income dashboard — weekly/monthly earnings breakdown by product, download records, loan application CTA
- `mobile-iot`: Smart Farm mockup screen — GPS tracking map, device status cards (sensors, milk meters, GPS collars)
- `mobile-multi-species`: Multi-species animal management — cattle, goat, sheep, poultry with species-specific icons and data fields
- `admin-dashboard`: Next.js + Refine admin panel — stats cards, charts, GIS map, CRUD tables, marketplace stats, IoT monitoring
- `deploy-local`: Docker Compose for local development
- `deploy-cloud`: Railway (API) + Vercel (admin) free-tier deployment
- `api-weather`: IMD weather alerts integration — fetch district-level forecasts, push extreme weather warnings to farmers (§future)
- `api-market-prices`: Agmarknet APMC mandi price integration — daily rates for milk, eggs, goat meat, wool, manure by district (§future)
- `api-feed-nutrition`: Feed/ration optimization — calculate balanced rations from locally available ingredients per species, breed, lactation stage (§future)
- `api-ethno-vet`: Ethno-veterinary medicine database — traditional remedies from ICAR documentation with dosage, species applicability, and evidence rating (§future)
- `api-bharat-pashudhan`: Bharat Pashudhan integration — sync Pashu Aadhaar IDs, pull vaccination history, push health records via open APIs (§7.1 ANIMAL entity)
- `api-vaccination`: Enhanced vaccination management — schedule reminders, batch tracking, coverage reports, cold chain compliance (§6.3)
- `api-insurance`: Livestock insurance integration — premium calculation, claim filing, Nandi AI biometric verification hooks (§future)
- `api-community-alerts`: Community disease alerts — outbreak notifications to farmers within configurable radius, crowd-sourced disease reporting (§future)
- `api-medicine-withdrawal`: Medicine withdrawal period calculator — track administered medicines, calculate safe milk/meat withdrawal dates per drug (§future)
- `milk-center`: Milk collection center operations — BMC management, quality testing (FAT/SNF/adulteration), rate calculation, farmer payment settlement (§6.9)
- `mobile-onboarding`: Guided farmer onboarding — progressive profile building, first animal registration, language preference, accessibility settings (§future)
- `mobile-weather`: Weather screen — 5-day forecast, rainfall alerts, heat stress warnings with Kannada voice summaries (§future)
- `mobile-advisory`: Advisory/tips feed — seasonal animal care tips, feeding recommendations, government announcements in Kannada (§future)
- `mobile-insurance`: Insurance screen — policy status, premium due, claim filing with photo upload, Nandi AI animal photo verification (§future)

### Modified Capabilities
<!-- None — greenfield prototype -->

## Impact

- **Code**: Entirely new codebase under `pashu-erp/` — no existing code modified
- **APIs**: 40+ new REST endpoints under `/v1/` (animals, health, milk, finance, shg, schemes, auth, admin, marketplace, income, iot, weather, market-prices, feed, ethno-vet, vaccination, insurance, community-alerts, withdrawal)
- **Dependencies**: Python (FastAPI, SQLAlchemy, Alembic, asyncpg, pydantic-settings, python-jose, passlib), TypeScript (Next.js, Refine, MUI, Expo, react-native-paper, i18next, react-leaflet, Recharts)
- **Infrastructure**: PostgreSQL 16 (Docker), Railway.app, Vercel
- **External services**: Sarvam AI (voice), OpenStreetMap (maps), IMD (weather), Agmarknet (prices), Bharat Pashudhan (national animal registry), Nandi AI (biometric verification)
- **Blueprint refs**: architecture.md §6-7, §9.4, §14-15; data-flow.md §1-5, §9; compliance.md §1-6
