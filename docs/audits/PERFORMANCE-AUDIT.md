# PashuRaksha ERP — Performance Audit Report

**Date:** 2026-04-08
**Auditor:** AI Performance Engineer
**Status:** Findings only — no changes made

---

## Phase 1: Discovery Summary

| Target | Stack | Bundler | Entry Point |
|--------|-------|---------|-------------|
| **Admin** | Next.js 14 + Refine + MUI 5 | Webpack (Next.js) | `src/app/layout.tsx` → 11 routes |
| **Mobile** | Expo 52 + React Native 0.76 + Paper 5 | Metro | `app/_layout.tsx` → 5 tabs + 10+ screens |
| **Web** | Expo web export (static) | Metro → static HTML | `dist/index.html` |
| **API** | FastAPI + SQLAlchemy 2.0 (async) + asyncpg | N/A | `app/main.py` → 21 routers |
| **Database** | PostgreSQL + Alembic | N/A | Single migration `d22bbd14c60e` |

**Shared packages:** None (no `packages/shared`). React and TypeScript are duplicated across admin and mobile.

**Build & Test Commands:**
- Admin: `next dev` / `next build` / `next start`
- Mobile: `expo start --dev-client` / `expo run:android` / `expo run:ios`
- API: `uvicorn app.main:app` / `pytest` / `ruff`

---

## CRITICAL — Fix Immediately

### C1. N+1 Queries in 3 API Endpoints

**Severity:** Critical | **Apps:** API + all frontends

| Endpoint | File:Line | Pattern | Worst Case |
|----------|-----------|---------|------------|
| `GET /admin/gis-alerts` | `api/app/routers/admin.py:110-157` | Fetches 100 events, then queries Animal + User **per event** | **201 queries** |
| `GET /vaccinations/due` | `api/app/routers/vaccine.py:27-74` | Fetches animals, then queries vaccinations **per animal** | **1 + N queries** |
| `GET /medicines/withdrawal` | `api/app/routers/medicine.py:84-132` | Fetches administrations, then queries Medicine **per record** | **1 + N queries** |

**Recommended fix:** Use `selectinload()` or `joinedload()` on the initial query to batch-load relationships in 1-2 queries instead of N.

```python
# Before (admin.py:120-128)
result = await db.execute(select(HealthEvent).limit(100))
events = result.scalars().all()
for event in events:
    animal = await db.execute(select(Animal).where(Animal.id == event.animal_id))  # N+1!

# After
from sqlalchemy.orm import selectinload
result = await db.execute(
    select(HealthEvent)
    .options(selectinload(HealthEvent.animal).selectinload(Animal.owner))
    .limit(100)
)
```

**Expected impact:** Reduce GIS alerts from ~201 queries to 2-3. Latency drop from seconds to <100ms at scale.

**Benchmark:** Log query count with `echo=True`, compare before/after.

---

### C2. Missing Database Indexes on 15+ Foreign Key Columns

**Severity:** Critical | **File:** `api/alembic/versions/d22bbd14c60e_initial_schema.py`

Only 1 index exists (`ix_users_phone`). All FK columns and time-range columns are **unindexed**:

| Column | Tables Using It | Query Pattern |
|--------|----------------|---------------|
| `user_id` | animals, yield_logs, sell_records, transactions | Every user-scoped list query |
| `animal_id` | health_events, vaccinations, yield_logs, medicine_administrations, insurance_policies | Every animal-detail query |
| `event_date`, `recorded_at`, `collected_at`, `sold_at`, `created_at` | Multiple | Every time-range filter |
| `center_id`, `farmer_user_id` | milk_collection_records | Daily collection reports |

**Recommended fix:** New Alembic migration adding indexes:

```python
# New migration
def upgrade():
    # Foreign key indexes
    op.create_index("ix_animals_user_id", "animals", ["user_id"])
    op.create_index("ix_health_events_animal_id", "health_events", ["animal_id"])
    op.create_index("ix_health_events_event_date", "health_events", ["event_date"])
    op.create_index("ix_vaccinations_animal_id", "vaccinations", ["animal_id"])
    op.create_index("ix_yield_logs_user_id", "yield_logs", ["user_id"])
    op.create_index("ix_yield_logs_animal_id", "yield_logs", ["animal_id"])
    op.create_index("ix_yield_logs_recorded_at", "yield_logs", ["recorded_at"])
    op.create_index("ix_milk_collection_center_id", "milk_collection_records", ["center_id"])
    op.create_index("ix_milk_collection_farmer", "milk_collection_records", ["farmer_user_id"])
    op.create_index("ix_sell_records_user_id", "sell_records", ["user_id"])
    op.create_index("ix_sell_records_sold_at", "sell_records", ["sold_at"])
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])
    op.create_index("ix_medicine_admin_animal_id", "medicine_administrations", ["animal_id"])
    op.create_index("ix_insurance_policies_animal_id", "insurance_policies", ["animal_id"])
    # Composite indexes for common queries
    op.create_index("ix_animals_user_created", "animals", ["user_id", "created_at"])
    op.create_index("ix_health_events_animal_date", "health_events", ["animal_id", "event_date"])
    op.create_index("ix_yield_logs_user_recorded", "yield_logs", ["user_id", "recorded_at"])
    op.create_index("ix_milk_collection_center_date", "milk_collection_records", ["center_id", "collected_at"])
```

**Expected impact:** 10-100x speedup on filtered queries once tables exceed ~1K rows.

**Benchmark:** `EXPLAIN ANALYZE` on common queries before/after index creation.

---

### C3. Auth Middleware Queries Database on Every Request

**Severity:** Critical | **File:** `api/app/middleware/auth.py:38`

`get_current_user()` executes `SELECT * FROM users WHERE id = ?` on **every protected endpoint call**. At 100 concurrent users making 10 req/min each = **1,000 unnecessary DB queries/minute**.

```python
# Current (auth.py:38)
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
```

**Recommended fix:** Add LRU cache or store user info in JWT claims:

```python
# Option A: In-memory cache with TTL
from functools import lru_cache
from cachetools import TTLCache

_user_cache = TTLCache(maxsize=1000, ttl=60)  # 60s TTL

async def get_current_user(...):
    # ... decode JWT ...
    if user_id in _user_cache:
        return _user_cache[user_id]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        _user_cache[user_id] = user
    return user

# Option B: Richer JWT claims (preferred)
# Store role in JWT payload, only query DB when full profile needed
```

**Expected impact:** Eliminate ~99% of auth-related DB queries.

**Benchmark:** Count `SELECT` on `users` table via pg_stat_statements before/after.

---

### C4. Leaflet CSS Loaded on All Admin Pages

**Severity:** Critical | **File:** `admin/src/app/layout.tsx:28-32`

```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
```

This external CDN stylesheet is loaded on **every page** (11 routes), but only needed on `/map` and `/` (dashboard with map). Blocks rendering on all pages, adds external dependency.

**Recommended fix:** Move the `<link>` into the `GISMap` component or only the pages that render maps:

```tsx
// Option A: In GISMap.tsx, add a useEffect to inject the CSS
useEffect(() => {
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
  document.head.appendChild(link);
  return () => { document.head.removeChild(link); };
}, []);

// Option B: Import in page-level layout for /map only
// Create src/app/map/layout.tsx with the <link>
```

**Expected impact:** Remove render-blocking CSS from 9 of 11 routes. Improve LCP by ~100-300ms on non-map pages.

**Benchmark:** Lighthouse LCP on `/animals`, `/farmers` etc. before/after.

---

## HIGH — Fix This Sprint

### H1. No Pagination on 14+ API Endpoints

**Severity:** High | **Apps:** API + all frontends

These endpoints return **all records** via `.all()` with no `LIMIT`/`OFFSET`:

| Endpoint | File:Line |
|----------|-----------|
| `/animals` | `animals.py:52-64` |
| `/health/history/{animal_id}` | `health.py:65-85` |
| `/vaccinations/{animal_id}` | `health.py:121-140` |
| `/milk/farmer/{user_id}/history` | `milk.py:48-75` |
| `/marketplace/history/{user_id}` | `marketplace.py:84-99` |
| `/income/history/{user_id}` | `income.py:120-174` |
| `/shg` | `shg.py:97+` |
| `/feed/ingredients` | `feed.py:17+` |
| `/advisory/tips` | `advisory.py:16+` |
| `/ethno-vet/remedies` | `ethno_vet.py:16+` |
| `/insurance/policies/{user_id}` | `insurance.py:40-64` |
| `/schemes` | `schemes.py:60+` |
| `/medicines` | `medicine.py:20+` |
| `/milk-center/farmer-settlements` | `milk_center.py:128-190` |

**Recommended fix:** Add `skip` and `limit` query params to all list endpoints:

```python
from fastapi import Query

@router.get("/animals")
async def list_animals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Animal)
        .where(Animal.user_id == user.id)
        .order_by(Animal.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
```

**Expected impact:** Prevent memory exhaustion at scale. Reduce response time from O(n) to O(1).

---

### H2. Python-Side Aggregation Instead of SQL GROUP BY

**Severity:** High | **Multiple files**

| File:Line | Current Pattern | Recommended SQL |
|-----------|-----------------|-----------------|
| `milk.py:67-68` | `sum(l.quantity_liters for l in logs)` | `select(func.sum(YieldLog.quantity_liters))` |
| `milk_center.py:150-180` | Loop-based settlement grouping | `GROUP BY farmer_user_id` with `func.sum()` |
| `income.py:98-111` | Dict-based category grouping | `GROUP BY category` with `func.sum()` |
| `admin.py:89-104` | **30 separate queries** in date loop | Single `GROUP BY date_trunc('day', ...)` |

**Example fix for admin.py milk chart (30 queries → 1):**

```python
# Before (admin.py:89-104) — 30 queries in a loop
for i in range(30):
    day = today - timedelta(days=29 - i)
    result = await db.execute(
        select(func.sum(YieldLog.quantity_liters))
        .where(YieldLog.recorded_at >= day, YieldLog.recorded_at < day + timedelta(days=1))
    )

# After — 1 query
from sqlalchemy import func, cast, Date
result = await db.execute(
    select(
        cast(YieldLog.recorded_at, Date).label("day"),
        func.sum(YieldLog.quantity_liters).label("total")
    )
    .where(YieldLog.recorded_at >= today - timedelta(days=30))
    .group_by(cast(YieldLog.recorded_at, Date))
    .order_by("day")
)
```

**Expected impact:** Admin milk chart: 30 queries → 1. Aggregation endpoints: fetch summary rows only.

---

### H3. Unused Dependency: `react-native-gifted-charts`

**Severity:** High | **File:** `mobile/package.json:27`

Listed as dependency but **zero imports** found in any source file.

```bash
# Fix
cd pashu-erp/packages/mobile
npm uninstall react-native-gifted-charts
```

**Expected impact:** Reduce mobile bundle by ~50-100KB immediately.

---

### H4. Zero React.memo() Usage Across Entire Frontend

**Severity:** High | **Apps:** Admin (5 components), Mobile (8 components)

**No component in the entire monorepo uses `React.memo()`.**

#### Admin Components to Memoize

| Component | File | Times Rendered Per Page |
|-----------|------|------------------------|
| `StatCard` | `admin/src/components/StatCard.tsx` | 6+ per dashboard |
| `RiskBadge` | `admin/src/components/RiskBadge.tsx` | Per table row (10+) |
| `SpeciesChip` | `admin/src/components/SpeciesChip.tsx` | Per table row (10+) |
| `AdminSidebar` | `admin/src/components/AdminSidebar.tsx` | Every route change |

**Fix pattern:**

```tsx
// Before (StatCard.tsx)
export default function StatCard({ title, value, icon, color }: Props) { ... }

// After
function StatCard({ title, value, icon, color }: Props) { ... }
export default React.memo(StatCard);
```

#### Mobile Components to Memoize

| Component | File | Times Rendered |
|-----------|------|----------------|
| `AnimalCard` | `mobile/src/components/AnimalCard.tsx` | 7+ in home FlatList |
| `ProductCard` | `mobile/src/components/ProductCard.tsx` | 4+ in sell grid |
| `EarningsHero` | `mobile/src/components/EarningsHero.tsx` | 1 per income tab |
| `FilterChips` | `mobile/src/components/FilterChips.tsx` | 1 per home tab |
| `TriageCard` | `mobile/src/components/TriageCard.tsx` | Per health list |
| `HeaderRight` | `mobile/app/(tabs)/_layout.tsx:8-30` | Every tab render |

**Expected impact:** Eliminate 50-100+ unnecessary re-renders per interaction cycle.

---

### H5. No `useCallback` Anywhere

**Severity:** High | **Apps:** Admin + Mobile

Event handlers are recreated on every render. When passed to child components (especially in lists), this defeats any `React.memo` optimization.

**Key locations needing `useCallback`:**

| File:Line | Handler |
|-----------|---------|
| `admin/src/app/animals/page.tsx:93` | Filter/search handlers |
| `admin/src/app/farmers/page.tsx:104` | Pagination handlers |
| `admin/src/app/schemes/page.tsx:60-82` | Sort handlers |
| `mobile/app/(tabs)/index.tsx` | All list callbacks |
| `mobile/app/(tabs)/_layout.tsx:8-30` | HeaderRight icon press handlers |

**Fix pattern:**

```tsx
// Before
const handleSearch = (text: string) => setSearch(text);

// After
const handleSearch = useCallback((text: string) => setSearch(text), []);
```

---

### H6. CORS Wildcard with Credentials (Security + Performance)

**Severity:** High | **File:** `api/app/main.py:37-43`

```python
# Current — INSECURE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Modern browsers will reject `allow_origins=["*"]` + `allow_credentials=True` per spec.

**Recommended fix:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Admin (Next.js)
        "http://localhost:8081",   # Mobile (Expo web)
        "http://localhost:19006",  # Expo dev
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

### H7. Geospatial Queries Done in Python

**Severity:** High | **File:** `api/app/routers/alerts.py:52-78`

Fetches **ALL** non-expired alerts into memory (line 63-68), then calculates Haversine distance in Python for every record (line 71-74).

**Recommended fix:** Use PostgreSQL `earth_distance` extension:

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS cube;
CREATE EXTENSION IF NOT EXISTS earthdistance;

-- Query with distance filter
SELECT * FROM disease_alerts
WHERE earth_box(ll_to_earth(user_lat, user_lon), radius_meters) @> ll_to_earth(lat, lon)
  AND expires_at > NOW();
```

Or use raw SQL in SQLAlchemy:

```python
from sqlalchemy import text
result = await db.execute(text("""
    SELECT * FROM disease_alerts
    WHERE earth_distance(
        ll_to_earth(:lat, :lon),
        ll_to_earth(latitude, longitude)
    ) <= :radius
    AND expires_at > NOW()
"""), {"lat": lat, "lon": lon, "radius": radius_m})
```

**Expected impact:** From O(n) memory + CPU to O(log n) with spatial index.

---

## MEDIUM — Plan for Next Sprint

### M1. Recharts Loaded Eagerly on 4 Admin Pages

**Severity:** Medium | **Files:** `page.tsx`, `income/page.tsx`, `milk/page.tsx`, `marketplace/page.tsx`

Recharts is ~150KB gzipped. Each page loads it statically.

**Recommended fix:** Wrap chart sections with `next/dynamic`:

```tsx
import dynamic from "next/dynamic";

const MilkChart = dynamic(() => import("../components/MilkChart"), {
  loading: () => <Skeleton variant="rectangular" height={300} />,
  ssr: false,
});
```

**Expected impact:** Reduce initial JS bundle by ~150KB for non-chart pages.

---

### M2. 11 MUI Icons Imported at Root Layout

**Severity:** Medium | **File:** `admin/src/app/layout.tsx:6-16`

11 icon imports for the sidebar menu are in the root layout, loaded on every page. These are also duplicated in `AdminSidebar.tsx:15-25`.

**Recommended fix:** Remove icon imports from `layout.tsx`. Keep them only in `AdminSidebar.tsx`.

---

### M3. Missing `useMemo` for Calculations

**Severity:** Medium

| File:Line | Calculation | Fix |
|-----------|-------------|-----|
| `income/page.tsx:46-47` | `totalIncome`, `avgPerFarmer` | `useMemo(() => ..., [data])` |
| `marketplace/page.tsx:77-78` | `totalVolume`, `uniqueSellers` | `useMemo(() => ..., [data])` |
| `vaccinations/page.tsx:121-125` | Multiple statistics | `useMemo(() => ..., [data])` |

---

### M4. Mobile FlatList Missing Optimization Props

**Severity:** Medium | **File:** `mobile/app/(tabs)/index.tsx:75-147`

```tsx
// Current
<FlatList data={animals} renderItem={renderAnimal} keyExtractor={...} />

// Recommended
<FlatList
  data={animals}
  renderItem={renderAnimal}
  keyExtractor={(item) => item.id}
  getItemLayout={(_, index) => ({ length: ITEM_HEIGHT, offset: ITEM_HEIGHT * index, index })}
  windowSize={5}
  maxToRenderPerBatch={10}
  removeClippedSubviews={true}
  initialNumToRender={5}
/>
```

**Expected impact:** Smoother scrolling, lower memory usage on home tab.

---

### M5. Both i18n Files Loaded Upfront

**Severity:** Medium | **File:** `mobile/src/i18n/index.ts:7-10`

Both `en.json` (9.2KB) and `kn.json` (15KB) loaded into memory at startup.

**Recommended fix:** Lazy-load the non-default language:

```ts
// Only load English at startup
i18n.init({
  lng: "en",
  resources: { en: { translation: en } },
});

// Lazy load Kannada when selected
export async function loadLanguage(lang: string) {
  if (lang === "kn" && !i18n.hasResourceBundle("kn", "translation")) {
    const kn = await import("./kn.json");
    i18n.addResourceBundle("kn", "translation", kn.default);
  }
  i18n.changeLanguage(lang);
}
```

**Expected impact:** Save ~15KB memory for English users (majority case).

---

### M6. Default Lazy Loading on All SQLAlchemy Relationships

**Severity:** Medium | **Files:** `api/app/models/animal.py:55-58`, `user.py:40-43`, `health.py:45-46`, `milk.py:35-37`

All relationships use default `lazy="select"` (lazy loading).

**Recommended fix:**

```python
# For frequently accessed in list views
health_events = relationship("HealthEvent", back_populates="animal", lazy="selectin")

# For relationships that should never be implicitly loaded
vaccinations = relationship("Vaccination", back_populates="animal", lazy="raise")
```

---

### M7. No Explicit Connection Pool Config

**Severity:** Medium | **File:** `api/app/database.py:5-9`

```python
# Current
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,
)

# Recommended
engine = create_async_engine(
    settings.database_url,
    echo=False,  # C3 fix: never echo in production
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)
```

---

### M8. No Global State Management in Mobile App

**Severity:** Medium | **All mobile screen files**

Each screen uses local `useState` for data. Navigating away and back re-fetches everything. No data sharing between tabs.

**Recommended fix:** Add React Context or Zustand with request caching:

```tsx
// Minimal approach with Context
const DataContext = createContext<{ animals: Animal[]; refresh: () => void }>();

// Better: use Zustand
import { create } from 'zustand';
const useStore = create((set) => ({
  animals: [],
  fetchAnimals: async () => {
    const data = await api.get("/animals");
    set({ animals: data });
  },
}));
```

---

## LOW — Backlog

### L1. No Table Virtualization in Admin

**Severity:** Low (current data is small) | **8 table components**

All tables render all rows. With current mock data (8-12 items), this is fine. Becomes a problem at 100+ rows.

**Fix when needed:** Switch to MUI DataGrid or add `react-window`.

---

### L2. `next.config.js` Minimal

**Severity:** Low | **File:** `admin/next.config.js`

```js
// Current — minimal
const nextConfig = {
  transpilePackages: ["react-leaflet", "@react-leaflet/core", "leaflet"],
  experimental: {},
};

// Recommended additions
const nextConfig = {
  transpilePackages: ["react-leaflet", "@react-leaflet/core", "leaflet"],
  images: {
    formats: ["image/avif", "image/webp"],
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
        ],
      },
    ];
  },
};
```

---

### L3. Theme Object Spread in Mobile

**Severity:** Low | **File:** `mobile/src/config/theme.ts:82`

`{ ...MD3LightTheme, colors: ... }` creates new object on every import. Negligible for single import.

---

### L4. `echo=True` in Development

**Severity:** Low (dev only) | **File:** `api/app/database.py:7`

SQL logging is enabled when `environment == "development"`. Ensure it's off in production. Covered by M7 fix.

---

## Core Web Vitals Estimate (Admin App)

| Metric | Current Risk | Primary Cause | Fix |
|--------|-------------|---------------|-----|
| **LCP** | Poor (>2.5s likely) | Render-blocking Leaflet CSS on all pages + CDN dependency | C4: Move CSS to map-only pages |
| **INP** | Moderate | Unmemoized components cause excess re-renders on interaction | H4, H5: Add memo + useCallback |
| **CLS** | Low-Moderate | Tables may shift on data load; charts resize | Add skeleton loaders with fixed dimensions |

---

## Mobile-Specific Performance Summary

| Concern | Status | Fix |
|---------|--------|-----|
| App startup | i18n loads synchronously, all tabs eager | M5: Lazy load translations |
| Main thread | Animations use `useNativeDriver: true` | No action needed |
| Memory leaks | `LoadingSkeleton` and `MicButton` have proper cleanup | No action needed |
| Image caching | No real images yet (mock data) | Address when real assets added |
| Unused dep | `react-native-gifted-charts` adds dead weight | H3: Remove it |

---

## Admin App — Full File Inventory

| File | Lines | Issues Found |
|------|-------|-------------|
| `vaccinations/page.tsx` | 346 | No memoization, stats not memoized |
| `AdminSidebar.tsx` | 264 | Not memoized, rendered on every route |
| `iot/page.tsx` | 278 | Large page, 6 icon imports |
| `schemes/page.tsx` | 230 | Sort logic not memoized |
| `marketplace/page.tsx` | 217 | Charts not lazy, calcs not memoized |
| `GISMap.tsx` | 207 | Dynamic imported (correct) |
| `farmers/page.tsx` | 207 | Only page with pagination params |
| `milk/page.tsx` | 206 | Charts not lazy, no API pagination |
| `page.tsx (dashboard)` | 198 | Heavy charts, 6 icons, Leaflet CSS |
| `animals/page.tsx` | 175 | No API pagination |
| `income/page.tsx` | 168 | Calcs not memoized, charts not lazy |
| `health/page.tsx` | 150 | No memoization |
| `layout.tsx` | 122 | Leaflet CSS global, 11 icon imports |
| `StatCard.tsx` | 101 | Not memoized, used 6+ times |
| `map/page.tsx` | 91 | Fine |
| `SpeciesChip.tsx` | 40 | Not memoized |
| `RiskBadge.tsx` | 36 | Not memoized |

---

## Mobile App — Full File Inventory

| File | Lines | Issues Found |
|------|-------|-------------|
| `ethno-vet.tsx` | 444 | Longest screen, complex |
| `health.tsx` | 394 | 3 state vars, symptom grid not memoized |
| `milk.tsx` | 347 | 5 state vars, no FlatList |
| `income.tsx` | 330 | EarningsHero not memoized |
| `feed-calculator.tsx` | 323 | Complex form |
| `sell.tsx` | 294 | Product grid not memoized |
| `insurance.tsx` | 337 | Similar patterns |
| `weather.tsx` | 254 | No list optimization |
| `vaccinations.tsx` | 250 | No list optimization |
| `index.tsx (home)` | 240 | FlatList missing optimization props |
| `_layout.tsx (tabs)` | 161 | HeaderRight not memoized |
| `AnimalCard.tsx` | 158 | Not memoized |
| `MicButton.tsx` | 149 | Uses useCallback (only component!) |
| `ProductCard.tsx` | 118 | Not memoized |
| `TriageCard.tsx` | 97 | Not memoized |
| `LoadingSkeleton.tsx` | 90 | Proper cleanup |
| `FilterChips.tsx` | 85 | Not memoized |
| `EarningsHero.tsx` | 71 | Not memoized |
| `EmptyState.tsx` | 71 | Simple |

---

## API — Full Router Inventory

| Router | File | Key Issues |
|--------|------|------------|
| `admin` | `admin.py` | **N+1 GIS alerts (201 queries)**, 30-query milk chart loop |
| `vaccine` | `vaccine.py` | **N+1 per-animal query** |
| `medicine` | `medicine.py` | **N+1 per-administration query** |
| `alerts` | `alerts.py` | **Python-side geospatial filtering** |
| `animals` | `animals.py` | No pagination |
| `health` | `health.py` | No pagination |
| `milk` | `milk.py` | Python aggregation, no pagination |
| `milk_center` | `milk_center.py` | Python aggregation, no pagination |
| `income` | `income.py` | Python aggregation, no pagination |
| `marketplace` | `marketplace.py` | No pagination |
| `insurance` | `insurance.py` | No pagination |
| `schemes` | `schemes.py` | No pagination |
| `shg` | `shg.py` | No pagination |
| `feed` | `feed.py` | No pagination |
| `advisory` | `advisory.py` | No pagination |
| `ethno_vet` | `ethno_vet.py` | No pagination |
| `finance` | `finance.py` | No pagination |
| `weather` | `weather.py` | OK (external API proxy) |
| `auth` | `auth.py` | OK |
| `onboarding` | `onboarding.py` | OK |
| `bharat_pashudhan` | `bharat_pashudhan.py` | OK |

---

## Remediation Roadmap

| Priority | Items | Effort | Impact |
|----------|-------|--------|--------|
| **Week 1** | C1, C2, C3, C4, H3, H6 | 2-3 days | Eliminate worst DB bottlenecks, fix security, unblock LCP |
| **Week 2** | H1, H2, H4, H5, H7 | 3-4 days | Pagination, SQL aggregation, memoization |
| **Week 3** | M1-M8 | 3-4 days | Bundle splitting, caching, state management |
| **Backlog** | L1-L4 | As needed | Scale-dependent improvements |

---

## How to Benchmark

1. **Database queries:** Enable `echo=True` temporarily, count queries per endpoint
2. **Bundle size:** `next build` → check `.next/analyze` with `@next/bundle-analyzer`
3. **Mobile bundle:** `npx expo export --dump-sourcemap` → analyze with source-map-explorer
4. **API latency:** Use `httpx` or `wrk` for endpoint benchmarking
5. **React renders:** Use React DevTools Profiler → record interaction → count renders
6. **Core Web Vitals:** Lighthouse CI on admin pages
7. **Database indexes:** `EXPLAIN ANALYZE` on top queries before/after
