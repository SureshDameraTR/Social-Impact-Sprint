# Vet Package — Agent Instructions

Vite 5.4 / React 18.3 / MUI 5.16 / Leaflet + React-Leaflet / React Router v6

## Critical Rules

1. **Map integration** — Leaflet for case locations; dynamic import if SSR issues arise
2. **Case-centric** — primary workflow is case list → case detail → update status
3. **MUI theme tokens** — use theme, not raw colors
4. **AuthGuard** — all routes protected via `src/components/AuthGuard.tsx`

## File Structure

See `../../WORKSPACE.md` for the complete file registry.

- **Pages** (5): `src/pages/` — Login, Dashboard, Cases, CaseDetail, Alerts
- **Components** (6): `src/components/` — NavBar, StatCard, SpeciesChip, EmptyState, AuthGuard, ErrorBoundary
- **API client** (3): `src/api/` — client.ts, auth.ts, vet.ts
- **Hooks** (1): `src/hooks/` — useAuth
- **Theme**: `src/theme.ts`

## Running

```bash
cd pashu-erp/packages/vet
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
pnpm install
VITE_API_URL=http://localhost:8000 npx vite --port 3002  # Dev
npx vite build                                              # Build check
```

## Adding a New Page

```
1. Page:      src/pages/<Name>.tsx          — React component
2. Route:     src/App.tsx                   — add <Route> entry
3. NavBar:    src/components/NavBar.tsx     — add navigation link
4. MANDATORY: Update ../../WORKSPACE.md    — add to Vet Pages section
```

## Key Patterns

- **Case workflow**: Vet receives alert → opens case → examines animal → prescribes treatment → closes case
- **Geolocation**: Cases shown on Leaflet map with cluster markers
- **Disease alerts**: `/alerts` page shows nearby health alerts from community reports
