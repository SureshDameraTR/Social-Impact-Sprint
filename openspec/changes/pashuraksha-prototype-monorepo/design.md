## Context

PashuRaksha ERP has comprehensive architecture blueprints (3,622 lines, 25 entities, 11 microservices) but zero working code. RDO stakeholders need a **live demo** at the scoping call (April 27, 2026). This design describes HOW to build a functional prototype — monorepo with 3 packages — that proves 6 core farmer journeys end-to-end while maintaining a clean path to the full production architecture.

**Current state**: Greenfield — no existing codebase. Blueprints define the target state (`docs/architecture.md` §1-17).

**Constraints**:
- 1 developer + AI assistance, ~30 days
- Demo-driven: 6 scenarios must work flawlessly
- Packages communicate only via HTTP API (no shared imports)
- Each package independently extractable to its own repo
- Prototype simplifications: mock OTP, no offline sync, rule-based AI, no payments

## Goals / Non-Goals

**Goals:**
- Deliver a working prototype demonstrating all 6 demo scenarios
- Establish monorepo structure with clean package boundaries for future repo extraction
- Implement 10 P0 entities (from blueprint §7.1) with async SQLAlchemy + Alembic
- Build voice-first Kannada farmer app on Expo with Sarvam AI STT
- Build admin dashboard with GIS map, charts, and CRUD tables
- Auto-generate OpenAPI spec as the cross-package contract
- Seed realistic Karnataka demo data (3 farmers, 8 animals, 30 days milk)

**Non-Goals:**
- Offline sync (PowerSync deferred to post-prototype)
- ML-based disease prediction (rule-based Phase 0 only, per §9.4)
- Payment processing (Razorpay integration deferred)
- Insurance, breeding, disease reporting entities (P1/P2 scope)
- Telemedicine video calls (Twilio integration deferred)
- Production security (RS256 JWT, key rotation, rate limiting)
- Multi-tenancy or cooperative-level data isolation
- Performance optimization or load testing
- Automated CI/CD (manual deploy to Railway/Vercel free tier)

## Decisions

### D1: Monorepo Tooling — pnpm workspaces + uv workspaces + just

**Decision**: Use `pnpm workspaces` for JS packages, `uv workspaces` for Python, and `just` as the cross-language task runner.

**Alternatives considered**:
- **Option A (Makefile only)**: Fastest setup but no package isolation enforcement. Scored 52/75.
- **Option C (Nx + @nxlv/python)**: Best dependency graph but `@nxlv/python` is immature, medium-high setup cost for 3 packages. Scored 51/75.
- **Option B (chosen)**: Real package isolation via workspace declarations, OpenAPI contract bridge, clean `git filter-repo` extraction path. Scored 62/75.

**Why**: For a 1-developer prototype with a 30-day deadline, the tooling sweet spot is isolation without ceremony. pnpm/uv workspaces enforce separate dependency trees (extraction-ready) while `just` provides a single `just dev` / `just test` / `just seed` experience across languages.

### D2: FastAPI Modular Monolith with Gateway Pattern

**Decision**: Structure the API as domain folders (`app/{auth,animals,health,milk,finance,shg,schemes}/`) where each module exposes a Gateway class as its public API.

**Alternatives considered**:
- **Flat router files**: Simpler but no extraction boundary. Inter-module calls become spaghetti.
- **Full microservices**: Blueprint target (§3) but prohibitive for 30-day prototype.
- **Gateway pattern (chosen)**: Each module has `router.py, schemas.py, models.py, service.py`. Cross-module calls go through Gateway classes. When extracting to microservices, replace Gateway with HTTP client — zero other code changes.

**Source**: arctikant/fastapi-modular-monolith-starter-kit pattern, validated by research.

### D3: Contract Bridge — FastAPI → OpenAPI → @hey-api/openapi-ts

**Decision**: FastAPI auto-generates `openapi.json` from Pydantic models. `@hey-api/openapi-ts` generates a typed TypeScript SDK. Both frontends import the SDK.

**Why over manual API client**: Zero type duplication. Schema changes in Pydantic models propagate automatically to both frontends via codegen. Recommended by FastAPI docs and validated by research agent.

**Generation workflow**: `just generate-client` → reads `http://localhost:8000/openapi.json` → writes `packages/shared/api-client/` → both `admin` and `mobile` import it.

### D4: Expo SDK 52 with Dev Client (not Expo Go)

**Decision**: Use Expo SDK 52 (stable, New Architecture enabled by default) with custom Dev Client.

**Why not Expo Go**: Sarvam AI's `sarvam-conv-ai-sdk` and MMKV require native modules incompatible with Expo Go. Dev Client is required from day 1.

**Why not SDK 55**: Too new for a time-constrained prototype. SDK 52 has the most community testing and stable New Architecture support.

### D5: 10 Entities Only (Blueprint §7.1 P0 subset)

**Decision**: Implement only these 10 entities: `users, animals, health_events, vaccinations, yield_logs, milk_collection_centers, milk_collection_records, transactions, shg_groups, govt_schemes`.

**Cut entities**: breeding_record, consultation, prescription, listing, negotiation, payment, insurance_policy, insurance_claim, disease_report, fodder_inventory, fodder_plan, fodder_forecast, weather_alert, vet, shg_member, shg_meeting, group_loan.

**Why**: These 10 entities cover all 6 demo scenarios. Cut entities map to features not in the demo (telemedicine, marketplace, insurance, breeding, fodder planning). The SHG sub-entities (member, meeting, group_loan) are simplified into the `shg_groups` table with JSONB fields for the prototype.

### D6: Rule-Based Disease Triage (§9.4 Phase 0)

**Decision**: Implement 50+ veterinary rules from ICAR-IVRI/NDDB guidelines as a Python dictionary. No ML models.

**Why**: Works immediately without training data. Blueprint explicitly defines Phase 0 as rule-based (§9.4). Rules are sourced from public veterinary manuals — no data partnership needed. Demo-ready from day 1.

**Engine**: `services/disease_rules.py` — input: list of symptom codes + optional vitals → output: risk_level, probable_diseases[], recommended_action, source_reference.

### D7: Mock OTP Authentication

**Decision**: Hardcoded OTP "123456" for all phone numbers. JWT HS256 with static secret.

**Why**: No Twilio account needed. Eliminates SMS delivery issues during demo. Swap to real OTP + RS256 before production.

### D8: Online-Only with Repository Pattern (Offline-Later Architecture)

**Decision**: All data access goes through Repository interfaces that call FastAPI directly. No offline storage.

**Why**: Offline sync (PowerSync + CRDT) is 3+ weeks of work alone. Repository Pattern means the UI layer never knows about data source — swap from `ApiRepository` to `PowerSyncRepository` later with zero UI changes.

**Offline indicator**: Show a badge "Online Only — Offline mode coming soon" in the app. Not a blocker for any demo scenario.

### D9: Refine v4 + MUI + REST Data Provider

**Decision**: Use Refine's `@refinedev/simple-rest` data provider pointing to FastAPI `/v1/` endpoints.

**Why**: Refine's CRUD abstractions (`useList`, `useOne`, `useCreate`, `useUpdate`) map 1:1 to FastAPI REST endpoints. No custom data fetching code needed. MUI v5 with `RefineThemes.Blue` provides polished admin UI out of the box.

**GIS gotcha**: `react-leaflet` requires `next/dynamic` with `ssr: false` — Leaflet accesses `window` which breaks SSR.

### D10: Sarvam AI for Kannada Voice Input

**Decision**: Use Sarvam AI Saaras V3 (STT) for voice-based milk recording. API-based, not on-device.

**Why**: Key demo differentiator for RDO stakeholders. Kannada accuracy 85%+ at $0.35/hr. `sarvam-conv-ai-sdk` has a React Native entry point. Fallback to manual numpad if voice fails.

**Flow**: Mic button → record audio → POST to Sarvam STT → parse Kannada number words ("Aidu" → 5) → populate milk quantity field.

### D11: Product Marketplace (Sell Tab) — Inspired by FarmFlow

**Decision**: Add a "Sell" (ಮಾರಾಟ) tab with product categories: Milk, Eggs, Goat/Sheep products, Manure/By-products. Each category has a quantity picker with +/- controls and auto-calculated price based on local market rates.

**Alternatives considered**:
- **Full marketplace with buyer/seller matching**: Too complex for prototype. Requires listings, negotiations, payments.
- **Simple sell recording (chosen)**: Record what was sold, at what price, to whom. No matching engine needed. Data feeds into Income dashboard.

**Why**: FarmFlow's sell flow proves that farmers value tracking what they sell beyond just milk. By-product revenue (manure, eggs, wool) is a significant income source that existing dairy apps ignore. Stellapps tracks only milk; this differentiates PashuRaksha as a holistic livestock income tracker.

**UX pattern**: Large product category cards with species-specific icons → tap to select → quantity picker with +/- (like FarmFlow) → auto-price from local rate table → "Record Sale" button.

### D12: Income Dashboard — Weekly/Monthly Earnings Breakdown

**Decision**: Add an "Income" (ಆದಾಯ) tab showing weekly earnings total, breakdown by product category (pie/donut), transaction history list, and a "Download Record" button + "Apply for Loan" CTA.

**Why**: FarmFlow's income screen demonstrates that farmers need to see the financial impact of their work. The loan CTA is strategic — banks require income proof for agricultural loans. A digital income record from PashuRaksha could serve as collateral documentation. NABARD and SHG micro-lending programs already use digital records.

**Data source**: Aggregates from transactions table + sell records, grouped by product category.

### D13: Smart Farm / IoT Mockup Screen

**Decision**: Add an IoT/Smart Farm screen (mockup only) showing: GPS tracking map with animal markers, device status cards (RFID scanner, milk meter, GPS collar, smart feeder), and sensor readings.

**Why**: Deepak's pitch deck emphasizes IoT integration (RFID for animal tracking, milk meters for quality, GPS collars for grazing). While hardware integration is out of prototype scope, showing the screen in the demo signals the platform's future direction. RDO stakeholders want to see the vision beyond basic record-keeping.

**Constraint**: All data is static/mock. No real IoT devices. The screen is a design preview accessible from Home or Profile.

### D14: Multi-Species Support — Beyond Dairy Cattle

**Decision**: Expand animal management to support cattle (dairy + draft), goats, sheep, and poultry. Each species has distinct icons, species-specific data fields, and appropriate health rules.

**Alternatives considered**:
- **Cattle-only (original)**: Simpler but misses 60% of Indian livestock value. Goats are the largest livestock population.
- **Multi-species with shared model (chosen)**: Single `animals` table with `species` enum. Species-specific fields in JSONB `metadata` column. UI shows species-appropriate icons and labels.

**Why**: FarmFlow supports goats, sheep, and poultry alongside cattle. India has 148M goats (largest population), 74M sheep, and 851M poultry. A cattle-only app ignores the majority of smallholder livestock income. Multi-species support was already in the ERD (`species` field on Animal model) but the UI only showed cow icons.

### D15: 5-Tab Navigation with Profile in Header

**Decision**: Expand from 4 bottom tabs to 5: Home (ಮನೆ), Milk (ಹಾಲು), Sell (ಮಾರಾಟ), Health (ಆರೋಗ್ಯ), Income (ಆದಾಯ). Profile moves to a header avatar icon.

**Why**: 5 tabs is the maximum for comfortable thumb reach on budget Android phones. All 5 tabs represent primary farmer actions (manage animals, record milk, sell products, check health, track income). Profile is a settings function, not a daily action — it belongs in the header.

**Tab icons**: Each tab gets a distinctive 26px SVG icon with Kannada label below. Active tab gets filled icon + primary color. FarmFlow validated this 5-tab pattern.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Sarvam AI Kannada accuracy < 85% on rural accents | Voice demo fails | Fallback numpad always available; pre-test 5 common phrases ("Aidu liter", "Mooru liter") |
| Railway.app cold start > 30s during demo | Demo feels slow | Warm up API 5 min before demo; keep local Docker as backup |
| Expo Dev Client build fails on Android | Can't install on demo phone | Build APK by Day 8; backup via emulator screen share |
| Kannada translations incorrect | Credibility issue with RDO | Get 1 native speaker to review top 50 UI strings |
| Demo DB corruption from testing | Demo data inconsistent | Idempotent seed script; re-run in 30 seconds |
| Internet drops during demo | All features fail (online-only) | Record backup demo video (3-5 min) by Day 14 |
| pnpm/uv workspace config complexity | Setup delays | Document exact `pnpm-workspace.yaml` + `uv.toml` in README |
| OpenAPI codegen drift between API and frontends | Type mismatches | `just generate-client` in CI; fail build on drift |
| Multi-species data model complexity | Schema bloat | Use JSONB `metadata` for species-specific fields; keep core columns shared |
| Marketplace pricing accuracy | Farmer confusion | Use district-level APMC mandal rates; allow manual override |
| IoT mockup sets unrealistic expectations | Stakeholder over-promise | Clearly label as "Future Vision — Phase 2" on screen |
| 5-tab navigation on small screens | Tab labels truncated | Use Kannada abbreviations; test on 4.5" screens |

## Open Questions

1. **Sarvam AI API key**: Need to register for free tier or developer account before Day 4 (mobile phase). Rate limit: 60 req/min — sufficient for demo.
2. **Karnataka GIS data quality**: DataMeet GeoJSON covers village boundaries, but need to verify coverage for specific demo villages (Mysore/Mandya district).
3. **Demo device**: What Android phone model will be used at the scoping call? Need to test APK on similar spec device.
4. **Admin auth**: Should admin panel have a separate login (admin role) or use the same mock OTP flow? Recommendation: separate admin credentials seeded in DB.
