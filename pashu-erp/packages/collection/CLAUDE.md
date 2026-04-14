# Collection Package — Agent Instructions

Vite 5.4 / React 18.3 / MUI 5.16 / React Router v6 / PWA (vite-plugin-pwa)

## Critical Rules

1. **PWA-first** — must work offline after initial load; service worker caches assets
2. **Desktop-first** — primary device is desktop/laptop at milk collection centres
3. **MUI theme tokens** — use theme, not raw colors
4. **AuthGuard** — all routes except `/login` are protected via `src/components/AuthGuard.tsx`
5. **Shift-based** — all milk intake is per-shift (morning/evening) via `ShiftSelector`

## File Structure

See `../../WORKSPACE.md` for the complete file registry.

- **Pages** (6): `src/pages/` — Login, Dashboard, Intake, Receipt, Enroll, Settlements
- **Components** (6): `src/components/` — NavBar, FarmerSearch, ShiftSelector, RatePreview, AuthGuard, ErrorBoundary
- **API client** (3): `src/api/` — client.ts, auth.ts, milk.ts
- **Hooks** (2): `src/hooks/` — useAuth, useCentre
- **Theme**: `src/theme.ts`

## Running

```bash
cd pashu-erp/packages/collection
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
pnpm install
VITE_API_URL=http://localhost:8000 npx vite --port 3001  # Dev
npx vite build                                              # Build check
```

## Adding a New Page

```
1. Page:      src/pages/<Name>.tsx          — React component
2. Route:     src/App.tsx                   — add <Route> entry
3. NavBar:    src/components/NavBar.tsx     — add navigation link
4. MANDATORY: Update ../../WORKSPACE.md    — add to Collection Pages section
```

## Key Patterns

- **Milk intake flow**: Select farmer → enter quantity/FAT/SNF → calculate rate → submit → print receipt
- **Pricing**: `src/utils/pricing.ts` — FAT/SNF-based pricing formula
- **Centre context**: `src/hooks/useCentre.tsx` — provides centre ID to all components
- **Known gap**: No offline data queue for milk intake when network drops
