# Admin Package — Agent Instructions

Next.js 14.2 / Refine 4.47 / MUI 5.16 / TypeScript 5.4

## Critical Rules

1. **No `any` types** — use proper interfaces, generics, or `unknown`
2. **MUI theme tokens** — use `theme.palette.primary.main` not raw hex colors
3. **Refine data provider** — all API calls go through `src/providers/data-provider.ts`, not raw fetch
4. **Auth guard** — `src/providers/auth-provider.ts` handles JWT + redirect to `/login`
5. **Dynamic imports** — Leaflet/map components must use `next/dynamic` with `ssr: false`
6. **Server components** — pages are server components by default; add `"use client"` only when needed

## File Structure

See `../../WORKSPACE.md` for the complete file registry.

- **Pages** (16): `src/app/` — Next.js App Router, file-based routing
- **Components** (6): `src/components/` — reusable UI widgets
- **Providers** (2): `src/providers/` — data + auth bindings
- **Theme** (2): `src/theme/` — MUI theme config (primary: #0d6b58)
- **Tests** (4): `src/__tests__/` — Jest component + page tests

## Adding a New Page

```
1. Page:      src/app/<route>/page.tsx        — React component
2. Sidebar:   src/components/AdminSidebar.tsx  — add nav link
3. API call:  Use Refine's useList/useOne/useCreate hooks
4. Test:      src/__tests__/pages/<route>.test.tsx
5. MANDATORY: Update ../../WORKSPACE.md — add row to Admin Pages table
```

## Running

```bash
cd pashu-erp/packages/admin
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
pnpm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npx next dev --port 3000  # Dev
npx next build                                                       # Build check
npx playwright test                                                  # E2E tests
```

## Key Patterns

- **Data fetching**: Refine `useList({ resource: "animals" })` → data-provider → `GET /v1/animals`
- **Pagination**: `TablePagination` uses `data?.total` from API envelope, not client-side count
- **Maps**: `GISMap.tsx` uses dynamic import wrapper for react-leaflet (single wrapper, not per-component)
- **Error boundary**: `error.tsx` and `global-error.tsx` catch render errors
- **API URL**: Set via `NEXT_PUBLIC_API_URL` env var (default: http://localhost:8000)
