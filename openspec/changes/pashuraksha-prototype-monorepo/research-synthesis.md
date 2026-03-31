# PashuRaksha ERP — Research Synthesis

## Research Completed (4 parallel agents + 3 research streams)

### 1. Monorepo Tooling (monorepo-research)

**Key Finding**: Nx + `@nxlv/python` plugin is the strongest option for polyglot Python+TS monorepos, but adds complexity. For a prototype with 1 developer + AI, the simpler approach wins.

| Option | Verdict |
|--------|---------|
| **Nx + @nxlv/python** | Best cross-language dependency graph, but medium setup complexity |
| **Turborepo + uv side-by-side** | Good for JS/TS, Python is second-class citizen |
| **pnpm workspaces + uv workspaces + just/Makefile** | Simplest, most manual, lowest learning curve |
| **Pants** | No JS/TS support — rejected |

**Repo Splitting**: `git filter-repo` for one-time extraction (month 6-12). Shared types via OpenAPI spec + `@hey-api/openapi-ts` for TS client generation.

**Contract Bridge**: FastAPI auto-generates OpenAPI → `@hey-api/openapi-ts` generates typed TS SDK → both frontends import SDK. Zero manual type duplication.

### 2. FastAPI Architecture (fastapi-research)

**Key Finding**: Modular monolith with domain-based folders + Gateway pattern enables clean microservice extraction later.

**Recommended Structure**:
- Domain folders: `app/{health,livestock,milk,finance,shg,schemes,auth}/` each with `router.py, schemas.py, models.py, service.py`
- Gateway pattern: each module exposes a Gateway class as its public API; replace with HTTP calls when splitting
- Event-driven inter-module: `fastapi-events` in-process bus → swap to RabbitMQ later

**Key Technical Decisions**:
- `async_sessionmaker` with `expire_on_commit=False` (mandatory for async)
- `pool_pre_ping=True` for connection health
- Separate input/output Pydantic models (never `response_model_exclude`)
- Alembic: import all models in `env.py`, use `version_locations` for future per-domain migrations
- `@hey-api/openapi-ts` (recommended by FastAPI docs) for TS client generation

**Templates Reviewed**: tiangolo/full-stack-fastapi-template (sync DB — don't adopt), zhanymkanov/fastapi-best-practices (conventions), arctikant/fastapi-modular-monolith-starter-kit (Gateway pattern).

### 3. Mobile App (mobile-research)

**Key Finding**: Dev Client required from day 1 (Sarvam AI + MMKV need native modules). Voice-first UX is THE primary interface for low-literacy farmers.

**Stack Confirmed**:
- Expo SDK 55 + Dev Client (not Expo Go)
- React Native Paper (MD3, 48dp touch targets built-in)
- MMKV for app state, expo-secure-store for tokens
- i18next with namespace splitting per feature module
- Noto Sans Kannada bundled (avoid OEM font inconsistencies)
- react-native-gifted-charts (good performance on budget Android)
- Sarvam AI `sarvam-conv-ai-sdk` for STT/TTS (has RN entry point)

**Offline Strategy**: Repository Pattern now (online-only fetch), swap to PowerSync later — zero UI changes.

**UX Patterns from Livestock Apps**:
- Voice as PRIMARY input/output (FarmerChat model)
- Photo-centric animal profiles (MoooFarm)
- Audio tutorials on first use (DigiCow voice notes)
- Flat navigation: max 2 taps, bottom tabs only, max 4-5 tabs
- Color-coded status (green/yellow/red)
- Minimal text, maximum icons (64px+ pictographic)
- WhatsApp-familiar chat patterns for vet consultation
- Target APK < 25MB

### 4. Admin Dashboard + Agritech Platforms (admin-agritech-research)

**Key Finding**: Refine v4 + MUI + Recharts is the proven admin stack. Stellapps (India) is the closest real-world analog for milk collection digitization.

**Stack Confirmed**:
- Refine v4 + `@refinedev/simple-rest` → FastAPI
- MUI v5 + `ThemedLayoutV2` with RefineThemes.Blue
- Recharts v3 for charts (used in official Refine examples)
- react-leaflet + OpenStreetMap + marker clustering for GIS
- Karnataka village boundary data: DataMeet GeoJSON + samashti/KGIS

**Agritech Platform Insights**:
| Platform | Key Pattern to Adopt |
|----------|---------------------|
| **Stellapps** (India) | Milk collection flow: weigh → FAT/SNF → auto-price → digital pay |
| **CropIn** (India) | Three-layer: Apps / Data Hub / Intelligence |
| **FarmERP** (India) | Module-per-domain maps to Refine resources |
| **AgriWebb** (Australia) | Mob vs individual animal tracking, offline-first |
| **NABARD e-Shakti** | SHG digitization: auto-grading, meeting tracking, 31+ MIS reports |

**Sarvam AI Details**:
- STT (Saaras V3): Kannada `kn-IN`, REST/Batch/Streaming, 85%+ accuracy, $0.35/hr
- TTS (Bulbul V3): Kannada, sub-150ms TTFT in fast mode, ₹30 per 10K chars
- JS SDK available, Vercel AI SDK provider exists
- **Correction**: No dedicated RN SDK found in admin research (but mobile research found `sarvam-conv-ai-sdk` with RN entry point)
- Rate limits: 60 req/min per key, token bucket model

### 5. Dairy Cooperative Technology Landscape

India's dairy cooperative ecosystem is rapidly digitizing at the top tier but remains fragmented for smallholder farmers. Amul leads with its AMCS platform powered by Prompt Dairy Tech across 28 states, and recently launched the Sarlaben AI assistant with Gujarati voice support (Feb 2026). However, no solution addresses the critical combination of offline capability and Kannada language support needed for Karnataka's dairy farmers, where 60% of milk flows through the unorganized sector without reliable connectivity.

**Key Findings**:
- Amul's AMCS with Sarlaben AI assistant provides Gujarati voice support (launched Feb 2026), powered by Prompt Dairy Tech across 28 states
- KMF/Nandini has achieved partial digitization but significant farmer-side gaps remain
- Bharat Pashudhan: 35.96 crore animals tagged with Pashu Aadhaar 12-digit unique IDs
- INAPH provides national health tracking; NDERP serves as the cooperative ERP backbone
- Stellapps IoT deployment spans 42,000 villages for milk collection digitization
- Critical gap: zero offline capability and no Kannada language support across Karnataka's cooperative tech stack
- 60% of India's milk is in the unorganized sector operating without connectivity infrastructure

**Implications for PashuRaksha**:
- Offline-first architecture is a non-negotiable differentiator — no competitor addresses this
- Kannada voice interface fills a gap that even Amul's Sarlaben (Gujarati-only) does not cover
- Bharat Pashudhan's Pashu Aadhaar 12-digit IDs are the natural integration point for animal identity
- Transparent disease detection rules (not black-box AI) build trust with cooperative societies
- Multi-species support and SHG integration are unaddressed by any existing platform
- INAPH and NDERP APIs should be P1 integration targets for health records and cooperative data

### 6. Global Competitor Analysis

A comprehensive analysis of 30+ livestock management apps across 6 regions (New Zealand, Australia, Ireland/UK, East Africa, India, Global) reveals that no single competitor offers the combination of voice-first Kannada interface, SHG financial workflows, and government scheme integration. The analysis also surfaces critical adoption lessons: complexity kills uptake among smallholder farmers, offline support is mandatory, and farmers in developing markets prefer paper over complex digital tools.

**Key Findings**:
- 30+ apps analyzed across 6 regions (NZ, AU, IE/UK, East Africa, India, Global)
- No competitor offers all three: voice-first Kannada, SHG workflows, and government scheme integration
- FarmFlow features absorbed into PashuRaksha: sell tab, income dashboard, IoT mockup, multi-species support, 5-tab navigation
- 15 P0/P1 features recommended: feed optimization, weather alerts (IMD API), mandi prices (Agmarknet), ethno-vet medicine DB, withdrawal calculator
- Common pain points: complexity kills adoption, offline is mandatory, paper preference persists over complex apps
- MoooFarm marketplace failed due to fake listings — trust is the critical issue in tier-3 markets
- Stellapps B2B2C model (free-for-farmer) is the most sustainable commercial approach
- Herdwatch per-species pricing creates friction and churn among multi-species farmers
- African apps (FlockWise) validate voice AI and animation-based advisory as effective for low-literacy users

**Implications for PashuRaksha**:
- Voice-first + Kannada + SHG + govt schemes is a unique value proposition with no direct competitor
- FarmFlow's proven UX patterns (5-tab nav, sell tab, income dashboard) should be adopted rather than reinvented
- Free-for-farmer (B2B2C via cooperatives) is the right commercial model — avoid per-user or per-species pricing
- Trust mechanisms (verified listings, cooperative endorsement) are essential for any marketplace features
- Feed optimization and weather alerts are high-value, low-complexity features to prioritize for P1
- Animation-based advisory (validated in East Africa) should be considered for health education modules

### 7. Accessibility and Compliance

Rural India's digital literacy gap (76.6% lacking digital literacy) makes accessibility the foundation of PashuRaksha's design, not an afterthought. The 10 crore women in Self-Help Groups represent an existing financial network that lacks livestock integration — a direct opportunity. Compliance with the DPDP Act 2023 and integration with Bharat Pashudhan's open APIs are regulatory and technical prerequisites for any agricultural data platform operating in India.

**Key Findings**:
- 76.6% of rural Indians lack digital literacy — voice interfaces and local language support are essential, not optional
- 10 crore SHG women have access to financial tools but no livestock management integration exists
- DPDP Act 2023 imposes specific requirements for agricultural data collection, storage, and consent
- Bharat Pashudhan open APIs provide the P0 integration foundation for animal identity and health records
- Accessibility checklist created for rural Indian users: large touch targets (48dp+), high contrast ratios, Kannada-first UI, minimal text reliance

**Implications for PashuRaksha**:
- Kannada-first (not Kannada-as-translation) must be the default language, with English as secondary
- Voice input/output is the primary interface — text is supplementary for low-literacy users
- SHG integration creates a distribution channel (10 crore women) and solves the last-mile adoption problem
- DPDP Act compliance must be designed into the data layer from day one (consent flows, data minimization, right to erasure)
- Bharat Pashudhan API integration is P0 — animal identity is the foundation for all health, breeding, and insurance features
- All UI components must meet the rural accessibility checklist: 48dp+ touch targets, high contrast, pictographic navigation

## Research Gaps / Contradictions

1. **Sarvam AI RN SDK**: Mobile research found `sarvam-conv-ai-sdk/react-native`, admin research said "no RN SDK". The npm package exists — mobile research is correct.
2. **Expo SDK version**: Mobile research mentions SDK 55 (latest), plan says SDK 52. **Use SDK 52 for stability** — it's the one with New Architecture enabled by default and most community testing. SDK 55 is too new for a time-constrained prototype.
3. **Monorepo tooling**: Research says Nx is "best" but for a 1-person prototype, the overhead isn't justified. Simpler tooling wins.
