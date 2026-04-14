# Mobile Package — Agent Instructions

Expo 52 / React Native 0.76 / React Native Paper 5.12 / Expo Router 4.0 / TypeScript 5.4

## Critical Rules

1. **File-based routing** — `app/` directory is Expo Router; filenames = routes
2. **React Native Paper** — use Paper components (`Button`, `TextInput`, `Card`), not raw RN
3. **i18n everywhere** — use `t('key')` from i18next, never hardcode user-facing strings
4. **Error handling** — never `catch (e) {}` silently; show `Snackbar` or log to console
5. **Offline awareness** — check network state before API calls (TODO: NetInfo integration)
6. **Touch targets** — minimum 48x48dp for all interactive elements (rural farmer hands)
7. **Voice input** — weather screen has voice playback; advisory may add voice input

## File Structure

See `../../WORKSPACE.md` for the complete file registry.

- **Screens** (26): `app/` — Expo Router file-based routing
- **Components**: `src/components/` — reusable RN Paper widgets
- **API client**: `src/config/api.ts` — Axios (15s timeout, 3 retries, exponential backoff)
- **i18n** (3): `src/i18n/` — en.json, kn.json (Kannada), hi.json (Hindi)
- **Config**: `app.json` — Expo app config

## Adding a New Screen

```
1. Screen:    app/<name>.tsx                — React component
2. Navigate:  router.push("/<name>")        — Expo Router navigation
3. API call:  import ApiClient from src/config/api.ts
4. i18n:      Add keys to src/i18n/en.json + kn.json + hi.json
5. Tab:       app/(tabs)/<name>.tsx for tab screens
6. MANDATORY: Update ../../WORKSPACE.md — add row to Mobile Screens table
```

## Running

```bash
cd pashu-erp/packages/mobile
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
pnpm install
# WSL: Expo dev server doesn't work well; use static export
EXPO_USE_FAST_RESOLVER=1 CI=true npx expo export --platform web
npx serve dist -l 8081
```

## Key Patterns

- **API client**: `ApiClient.get("/v1/animals")` — auto-injects JWT, retries on 5xx
- **Auth flow**: OTP login → JWT stored in SecureStore → auto-injected in headers
- **Tab layout**: 5 tabs (Home, Milk, Health, Income, Sell) in `app/(tabs)/_layout.tsx`
- **Onboarding**: 4-step flow (welcome → profile → first-animal → tutorial)
- **Known gap**: No offline queue, no NetInfo listener, no background sync
