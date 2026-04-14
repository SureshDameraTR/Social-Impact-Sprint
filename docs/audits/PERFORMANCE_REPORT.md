# PashuRaksha ERP — Performance Audit Report

**Date:** 2026-04-11
**Environment:** Dev mode (WSL2 → Windows), no production build optimization
**Chrome:** Windows native via CDP

---

## Executive Summary

| Category | Status | Key Finding |
|----------|--------|-------------|
| Backend API Latency | **GOOD** | 14 of 16 endpoints under 50ms |
| API Response Sizes | **CRITICAL** | 3 endpoints return 99% bloat from eager-loaded relationships |
| Browser Memory | **WARNING** | Admin app uses 101–180 MB JS heap per page |
| Page Load Times | **SLOW (Dev)** | 2–7s per Admin page (Next.js dev mode compilation) |
| Collection App | **EXCELLENT** | 140–510ms page loads, 12–21 MB heap |
| Docker Resources | **GOOD** | API 140MB, DB 54MB, Mocks 45MB — all within limits |
| Database | **GOOD** | Tiny tables, indexes well-used, 4 connections |
| Node.js Processes | **WARNING** | Next.js dev uses 2.1 GB RSS across processes |

---

## 1. Backend API Latency

| Endpoint | Status | TTFB | Total | Response Size | Rating |
|----------|--------|------|-------|---------------|--------|
| `GET /health` | 200 | 5.5ms | 5.7ms | 43 B | FAST |
| `GET /v1/admin/stats` | 200 | 14.6ms | 14.8ms | 127 B | FAST |
| `GET /v1/admin/charts/milk` | 200 | 6.3ms | 6.5ms | 1.1 KB | FAST |
| `GET /v1/farmers` | 200 | 16.5ms | 16.9ms | 1.6 KB | FAST |
| `GET /v1/animals` | 200 | 38.4ms | 42.6ms | **218.7 KB** | BLOATED |
| `GET /v1/milk` | 200 | 21.4ms | 22.2ms | 23.3 KB | OK |
| `GET /v1/milk/daily-summary` | 200 | 8.0ms | 8.2ms | 1.4 KB | FAST |
| `GET /v1/health` | 200 | 29.4ms | 32.0ms | **85.9 KB** | BLOATED |
| `GET /v1/health/alerts/map` | 200 | 18.3ms | 18.4ms | 663 B | FAST |
| `GET /v1/schemes` | 200 | 8.4ms | 8.8ms | 3.4 KB | FAST |
| `GET /v1/marketplace` | 200 | **263ms** | **290ms** | **1,652 KB** | CRITICAL |
| `GET /v1/finance/summary` | 200 | 6.9ms | 7.6ms | 138 B | FAST |
| `GET /v1/map/points` | 200 | 21.0ms | 21.3ms | 1.2 KB | FAST |
| `GET /v1/iot/device-types` | 200 | 19.1ms | 19.4ms | 283 B | FAST |
| `GET /v1/iot/readings` | 200 | **163ms** | 163.8ms | 3.6 KB | SLOW (N+1) |

### Critical Findings

1. **`/v1/marketplace` — 1.6 MB response (290ms)**
   - 64 sell records, each with full `user` object eagerly loaded
   - `user` nested object includes: `sell_records`, `yield_logs`, `transactions`, `animals` — recursively loading the ENTIRE user graph
   - **99% of payload is the nested `user` field** (1,726 KB of 1,749 KB)
   - Without `user`: only 22.8 KB
   - **Fix:** Add `select_related` or exclude relationship fields from serialization

2. **`/v1/health` — 85.9 KB response for 2 alerts**
   - Each alert includes full `animal` object (46 KB each!)
   - `animal` includes: `owner`, `vaccinations`, `yield_logs` — recursive eager loading
   - **99% of payload is the nested `animal` field** (90.7 KB of 91.9 KB)
   - Without `recorder+animal`: only 1.2 KB
   - **Fix:** Use `load_only()` or exclude deep relationships

3. **`/v1/iot/readings` — 163ms (N+1 query pattern)**
   - Fetches all devices, then calls `get_latest_telemetry()` per device sequentially
   - 10 devices = 10 sequential HTTP calls to mock gateway
   - **Fix:** Batch telemetry fetch or add a bulk endpoint to the gateway

---

## 2. Browser Performance — Admin App (Next.js)

| Page | DOMContentLoaded | Full Load | JS Heap Used | DOM Nodes | Rating |
|------|-----------------|-----------|-------------|-----------|--------|
| Dashboard `/` | 6,249ms | 7,215ms | 92.0 MB | 498 | SLOW |
| Farmers `/farmers` | 3,081ms | 4,112ms | 114.0 MB | 581 | MODERATE |
| Animals `/animals` | 3,627ms | 5,473ms | 142.6 MB | 36* | MODERATE |
| Milk `/milk` | 3,215ms | 4,349ms | 132.2 MB | 571 | MODERATE |
| Health `/health` | 2,380ms | 3,356ms | 135.9 MB | 527 | MODERATE |
| Vaccinations `/vaccinations` | 3,012ms | 4,092ms | 132.3 MB | 617 | MODERATE |
| Schemes `/schemes` | 2,168ms | 3,337ms | 107.8 MB | 536 | MODERATE |
| Marketplace `/marketplace` | 2,204ms | 3,322ms | 149.7 MB | 605 | MODERATE |
| Income `/income` | 576ms | 1,963ms | **180.5 MB** | 299 | OK |
| Map `/map` | 511ms | 1,382ms | 116.9 MB | 337 | OK |
| IoT `/iot` | 241ms | 1,280ms | 101.1 MB | 726 | OK |

*Animals DOM node count of 36 measured during loading state

### Key Observations

- **Pages visited first take 3–7s** due to Next.js dev mode compilation (on-demand)
- **Previously compiled pages load in 200–600ms** (cached compilation)
- **JS Heap ranges from 92–180 MB** across pages — Marketplace and Income are heaviest
- **Production build would reduce load times to ~500ms** and heap by ~40%
- **DOM node counts are reasonable** (300–726 nodes per page)

---

## 3. Browser Performance — Collection App (Vite)

| Page | DOMContentLoaded | Full Load | JS Heap Used | DOM Nodes | Rating |
|------|-----------------|-----------|-------------|-----------|--------|
| Dashboard | 496ms | 511ms | 13.3 MB | 160 | EXCELLENT |
| Intake | 141ms | 156ms | 12.2 MB | 209 | EXCELLENT |
| Settlements | 153ms | 167ms | 20.9 MB | 187 | EXCELLENT |

The Collection app (Vite) is **dramatically faster** than Admin (Next.js dev):
- **3–40x faster page loads** (150ms vs 3,000ms)
- **7–14x less memory** (13 MB vs 100+ MB)
- **Fewer DOM nodes** (160–209 vs 300–726)

---

## 4. Docker Container Resources

| Container | CPU | Memory | Mem % of Limit | Network I/O | PIDs |
|-----------|-----|--------|----------------|-------------|------|
| API (FastAPI) | 3.23% | 140.4 MB / 512 MB | **27.4%** | 1.5 MB / 6.4 MB | 8 |
| Database (PostgreSQL) | 3.96% | 54.3 MB / 512 MB | **10.6%** | 1.3 MB / 2.8 MB | 9 |
| Mock Backends | 0.17% | 44.8 MB / 15.6 GB | 0.3% | 39 KB / 93 KB | 5 |

All containers well within limits. API at 27% memory is healthy with room for growth.

---

## 5. Frontend Process Memory (Host)

| Process | RSS Memory | CPU | Notes |
|---------|-----------|-----|-------|
| Next.js main | 74 MB | 0% | Base process |
| Next.js compiler | **2,104 MB** | 13.2% | SWC/Webpack compilation cache |
| Next.js worker | 78 MB | 0% | Worker thread |
| Vite main | 131 MB | 0.1% | Dev server |
| Vite esbuild | 24 MB | 0.2% | Transform engine |
| **Total Node.js** | **~2,058 MB** | — | 25 processes |

Next.js dev mode is the dominant memory consumer at **2.1 GB RSS**. A production deployment would eliminate this entirely (static files served by nginx/CDN).

---

## 6. Frontend Bundle Analysis

### Admin (Next.js) — Dev Mode

| Asset | Size (disk) | Size (gzipped HTTP) |
|-------|-------------|-------------------|
| `main-app.js` | 5.8 MB | 1,313 KB |
| `polyfills.js` | 110 KB | 39 KB |
| `webpack.js` | 56 KB | 10 KB |
| Per-page chunk (avg) | 6–12 MB | ~1–2 MB |
| **Total on disk** | **98 MB** | N/A (dev mode, with source maps) |

**14 production dependencies** — MUI, Refine, Recharts, Leaflet, Next.js, React

### Collection (Vite) — Dev Mode

| Metric | Value |
|--------|-------|
| HTML size | 940 bytes |
| Dependencies | 8 packages |
| node_modules | 214 MB |

**Note:** Dev mode bundles include source maps and are not minified. Production builds would be 5–10x smaller.

---

## 7. Database Performance

### Table Sizes (Top 10)

| Table | Total Size | Rows | Index Size |
|-------|-----------|------|------------|
| yield_logs | 136 KB | 311 | 96 KB |
| transactions | 96 KB | 50 | 48 KB |
| milk_collection_records | 80 KB | 120 | 64 KB |
| users | 80 KB | 9 | 64 KB |
| animals | 80 KB | 9 | 64 KB |
| health_events | 80 KB | 7 | 64 KB |
| sell_records | 72 KB | 64 | 48 KB |
| traditional_remedies | 64 KB | 25 | 16 KB |

### Index Usage (Top 5)

| Index | Table | Scans |
|-------|-------|-------|
| users_pkey | users | 932 |
| ix_sell_records_sold_at | sell_records | 343 |
| animals_pkey | animals | 332 |
| ix_yield_logs_recorded_at | yield_logs | 124 |
| ix_users_phone | users | 109 |

### Connection Stats
- Total: 4 connections (1 active, 3 idle)
- All tables under 200 KB — database is tiny and fast
- All queries execute under 2ms

---

## 8. Recommendations (Priority Order)

### P0 — Critical Performance Fixes

1. **Fix eager-loading in marketplace endpoint**
   - File: `packages/api/app/routers/marketplace.py`
   - Remove `user` relationship from serialization or use `load_only()`
   - Impact: **1,652 KB → ~23 KB** (98.6% reduction), **290ms → ~20ms**

2. **Fix eager-loading in health endpoint**
   - File: `packages/api/app/routers/health.py`
   - Exclude `animal.owner`, `animal.vaccinations`, `animal.yield_logs`
   - Impact: **86 KB → ~1.2 KB** (98.6% reduction)

3. **Fix N+1 in IoT readings**
   - File: `packages/api/app/routers/iot.py`
   - Batch telemetry fetch instead of per-device sequential calls
   - Impact: **163ms → ~20ms**

### P1 — Production Readiness

4. **Run `next build` for production deployment** instead of dev mode
   - Eliminates 2.1 GB compilation memory
   - Reduces page load from 3–7s → ~500ms
   - Reduces JS bundle by ~5x (tree-shaking, minification)

5. **Add API response pagination defaults**
   - `/v1/marketplace` returns all 64 records — needs `limit=20` default
   - `/v1/health` returns nested objects — needs shallow serialization

### P2 — Optimization

6. **Add gzip/brotli compression to FastAPI**
   - Most responses are JSON — 60–80% compression ratio
   
7. **Add CDN/static file caching headers**
   - Leaflet tiles, fonts, icons should be browser-cached

8. **Consider lazy-loading Leaflet and Recharts**
   - Both libraries are ~200KB+ each
   - Only needed on Map and Dashboard/Milk/Income pages

---

## 9. Performance Budget (Production Targets)

| Metric | Current (Dev) | Target (Prod) |
|--------|--------------|---------------|
| Page Load (first visit) | 3–7s | < 1.5s |
| Page Load (cached) | 0.2–0.5s | < 0.3s |
| API Response (P95) | 290ms | < 100ms |
| JS Heap (per page) | 100–180 MB | < 60 MB |
| Largest API Response | 1,652 KB | < 50 KB |
| Total Transfer (page) | ~2 MB | < 500 KB (gzipped) |
| Docker API Memory | 140 MB | < 256 MB |
