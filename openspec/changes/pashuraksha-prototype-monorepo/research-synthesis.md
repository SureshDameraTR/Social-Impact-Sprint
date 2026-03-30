# PashuRaksha ERP — Research Synthesis

## Research Completed (4 parallel agents)

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

## Research Gaps / Contradictions

1. **Sarvam AI RN SDK**: Mobile research found `sarvam-conv-ai-sdk/react-native`, admin research said "no RN SDK". The npm package exists — mobile research is correct.
2. **Expo SDK version**: Mobile research mentions SDK 55 (latest), plan says SDK 52. **Use SDK 52 for stability** — it's the one with New Architecture enabled by default and most community testing. SDK 55 is too new for a time-constrained prototype.
3. **Monorepo tooling**: Research says Nx is "best" but for a 1-person prototype, the overhead isn't justified. Simpler tooling wins.
