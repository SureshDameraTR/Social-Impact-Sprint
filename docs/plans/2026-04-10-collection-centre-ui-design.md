# Milk Collection Centre UI — Design Document

**Date**: 2026-04-10
**Status**: Approved
**Package**: `pashu-erp/packages/collection/`

## Overview

A standalone PWA for milk collection centre agents to record milk intake, enroll new farmers, view shift summaries, and generate farmer settlement reports. Runs on tablets/kiosks at rural collection centres.

## Tech Stack

- **Vite** + React 18 + TypeScript
- **MUI 5** (same version as admin for visual consistency)
- **React Router v6** (lightweight client-side routing)
- **PWA** via `vite-plugin-pwa` (installable, online-only for now)
- **Axios** for API communication
- **Port**: 3001 (admin is on 3000)

## Screens (6 total)

| Route | Screen | Auth |
|-------|--------|------|
| `/login` | OTP login (same flow as mobile) | No |
| `/intake` | Milk intake form — primary workflow | Yes |
| `/intake/receipt/:id` | Printable receipt after submission | Yes |
| `/enroll` | Quick farmer registration | Yes |
| `/dashboard` | Shift-wise daily summary | Yes |
| `/settlements` | Farmer payout summary for billing period | Yes |

## Milk Intake Flow (Core Screen)

Single-page form optimized for tablet — large touch targets, minimal scrolling.

### Workflow

1. **Farmer lookup**
   - Type phone number — autocomplete search
   - OR type last 4 Aadhaar digits + name — filtered match
   - "New farmer?" link redirects to `/enroll`, returns back after

2. **Milk entry**
   - Quantity (liters) — numeric keypad input
   - Fat % — numeric (1.0–12.0)
   - SNF % — numeric (6.0–12.0)
   - Shift — auto-detected (before 12pm = morning, after = evening), overridable

3. **Rate calculation**
   - Displayed live as fat/SNF are entered
   - Mirrors backend `calculate_rate` formula client-side for instant feedback
   - Shows: rate/liter x quantity = total amount (INR)

4. **Submit**
   - `POST /v1/milk-center/receive`
   - On success: navigate to `/intake/receipt/:id`
   - On error: inline error message, form retains values

### UX Decisions

- Fat/SNF fields get focus after farmer is selected (most-typed values)
- Rate preview updates on every keystroke (debounced)
- Shift auto-detected from time of day to save one tap per entry
- After receipt, "Next Farmer" button returns to blank intake form

## Quick Enroll

**Fields**:
- Full name (required)
- Phone number (required, 10 digits, Indian mobile format)
- Aadhaar number (required, 12 digits — stored masked as `XXXX-XXXX-1234`)
- Village name (optional, dropdown from centre's district)

On submit: `POST /v1/onboarding/register` with role `farmer`. On success, redirects back to intake with the new farmer pre-selected.

## Receipt

**Content**: Centre name & code, farmer name & phone, date, shift, time, quantity, fat%, SNF%, rate per liter, total amount (INR), unique receipt number (shortened UUID).

**Actions**:
- "Print" — `window.print()` with thermal-printer-optimized CSS (80mm width, no color)
- "Next Farmer" — back to blank intake form

## Dashboard

Cards showing today's summary:
- Total liters
- Total amount (INR)
- Farmer count
- Avg fat% / SNF%

Below cards: Morning vs Evening split (liters + farmer count per shift).

Data source: `GET /v1/milk-center/{id}/daily-report`

## Settlements

Table of farmers sorted by payout (descending):
- Columns: Farmer name, deliveries, total liters, avg fat%, avg SNF%, total payout
- Period selector: 15 / 30 / 45 days (default 15)
- Total payout summary at bottom

Data source: `GET /v1/milk-center/{id}/farmer-settlements`

## API Changes

### New: User role `collector`

```python
class UserRole(str, enum.Enum):
    farmer = "farmer"
    admin = "admin"
    collector = "collector"  # Milk collection centre agent
```

### New: Aadhaar fields on User model

- `aadhaar_hash` — SHA-256 of full Aadhaar (for dedup, nullable)
- `aadhaar_last4` — last 4 digits (indexed, for search, nullable)
- Full Aadhaar is never stored in plaintext

### New: Farmer search endpoint

```
GET /v1/milk-center/farmers/search?phone=9876&aadhaar_last4=1234&name=ram
```

- Returns farmers matching any provided filter (OR logic)
- Response: `[{id, name, phone, aadhaar_masked, village}]`
- Limited to 10 results
- Only returns masked Aadhaar, never full

### Existing endpoints (no changes needed)

- `POST /v1/auth/otp-request` + `otp-verify` — login
- `POST /v1/milk-center/receive` — intake
- `GET /v1/milk-center/{id}/daily-report` — dashboard
- `GET /v1/milk-center/{id}/farmer-settlements` — settlements
- `POST /v1/onboarding/register` — enroll (minor tweaks for Aadhaar masking)

## Project Structure

```
packages/collection/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── public/
│   ├── manifest.json
│   └── icons/
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── theme.ts
    ├── api/
    │   ├── client.ts
    │   ├── auth.ts
    │   ├── milk.ts
    │   └── farmers.ts
    ├── hooks/
    │   ├── useAuth.ts
    │   └── useCentre.ts
    ├── pages/
    │   ├── Login.tsx
    │   ├── Intake.tsx
    │   ├── Receipt.tsx
    │   ├── Enroll.tsx
    │   ├── Dashboard.tsx
    │   └── Settlements.tsx
    ├── components/
    │   ├── FarmerSearch.tsx
    │   ├── RatePreview.tsx
    │   ├── ShiftSelector.tsx
    │   ├── NavBar.tsx
    │   └── AuthGuard.tsx
    └── utils/
        ├── pricing.ts
        └── print.css
```

~20 files total. No new backend dependencies.

## Auth & Centre Binding

- Reuses existing OTP flow
- JWT stored in localStorage
- After login, agent selects their centre (or pre-bound via `manager_user_id` on `MilkCollectionCenter`)
- All subsequent API calls scope to that `center_id`

## Scope Exclusions

- No offline support (online-only for sprint, can add later)
- No farmer profile management (belongs in admin)
- No centre management/CRUD (belongs in admin)
- No charts/analytics (cards + tables only)
- No QR/barcode scanning (phone + Aadhaar last 4 is sufficient)
