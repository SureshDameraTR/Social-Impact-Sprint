# Visual Regression Baseline Report

**Agent**: visual-regression-tester
**Date**: 2026-04-16
**Type**: FIRST RELEASE ASSESSMENT (no prior baselines)
**Scope**: 3 web packages — Admin, Collection, Vet

---

## Executive Summary

The visual layer is well-structured with a centralized theme per package, consistent font family, and matching component primitives. The Vet package intentionally diverges in primary color (blue vs green) which is acceptable for role differentiation. However, several findings require attention: hardcoded hex colors in components that bypass theme tokens, missing responsive breakpoints across all packages, divergent SpeciesChip implementations between Admin and Vet, and sparse `data-testid` coverage that limits visual regression test targeting.

**Verdict: WARN** -- No blocking issues, but 2 high and 5 medium findings need resolution before the visual baseline can be considered stable.

---

## 1. Theme Configuration Analysis

### 1.1 Theme Files

| Package | File | Primary | Background | Font |
|---------|------|---------|------------|------|
| Admin | `src/theme/theme.ts` | `#0d6b58` (teal-green) | `#f0f4f3` | IBM Plex Sans |
| Collection | `src/theme.ts` | `#0d6b58` (teal-green) | `#f0f4f3` | IBM Plex Sans |
| Vet | `src/theme.ts` | `#1565c0` (blue) | `#f5f7fa` | IBM Plex Sans |

### 1.2 Palette Comparison

| Token | Admin | Collection | Vet | Consistent? |
|-------|-------|------------|-----|-------------|
| primary.main | `#0d6b58` | `#0d6b58` | `#1565c0` | INTENTIONAL DIVERGENCE |
| secondary.main | `#1e3a5f` | `#1e3a5f` | `#0d6b58` | Vet swaps primary/secondary |
| error.main | `#c0392b` | `#c0392b` | `#c62828` | DRIFT |
| warning.main | `#d97706` | `#d97706` | `#e65100` | DRIFT |
| success.main | `#16a34a` | `#16a34a` | `#2e7d32` | DRIFT |
| info.main | `#0369a1` | `#0369a1` | `#0277bd` | DRIFT |
| background.default | `#f0f4f3` | `#f0f4f3` | `#f5f7fa` | INTENTIONAL |
| text.primary | `#1a2e2a` | `#1a2e2a` | `#1a2332` | MINOR DRIFT |
| text.secondary | `#5f7a74` | `#5f7a74` | `#5f6d7e` | MINOR DRIFT |

**Assessment**: Admin and Collection share an identical palette. Vet has a blue primary (role-based differentiation) but also diverges on error/warning/success/info colors unnecessarily. These semantic colors should be consistent across the product for uniform severity communication.

### 1.3 Component Overrides Comparison

| Override | Admin | Collection | Vet |
|----------|-------|------------|-----|
| MuiButton borderRadius | 8 | 8 | 8 |
| MuiButton textTransform | none | none | none |
| MuiButton fontWeight | 600 | 600 | 600 |
| MuiCard borderRadius | 14 | 14 | 14 |
| MuiCard boxShadow | identical | identical | identical |
| MuiTextField borderRadius | 8 | 8 | 8 |
| MuiChip borderRadius | 10 | -- | 6 |
| MuiChip fontWeight | 500 | -- | 600 |
| MuiChip fontSize | 12px | -- | 11px |
| MuiPaper | yes | -- | -- |
| MuiTableHead | yes | -- | -- |
| MuiTableBody | yes | -- | -- |
| MuiTableRow | yes | -- | -- |
| MuiLinearProgress | yes | -- | -- |
| MuiAlert | yes | -- | -- |

**Assessment**: Core component shapes (Button, Card, TextField) are consistent. Chip styling diverges between Admin (borderRadius 10, 12px) and Vet (borderRadius 6, 11px). Collection lacks Chip overrides entirely, falling back to MUI defaults.

### 1.4 Shape & Border Radius

All three packages: `shape.borderRadius: 10` -- Consistent.

---

## 2. Color Usage Audit

### 2.1 Hardcoded Colors Outside Theme Files

| File | Colors Found | Severity |
|------|-------------|----------|
| `admin/src/components/GISMap.tsx` | `#c0392b`, `#d97706`, `#16a34a`, `#0369a1` (8 instances) | MEDIUM -- Leaflet styling cannot use MUI theme tokens, but should reference the `colors` export |
| `admin/src/app/global-error.tsx` | `#f0f4f3`, `#1a2e2a`, `#5f7a74`, `#ffffff`, `#0d6b58` (5 instances) | LOW -- Error boundary renders outside ThemeProvider, hardcoded is acceptable |
| `admin/src/app/layout.tsx` | `#0f2b24`, `#ffffff`, `#f0f4f3` (3 instances) | LOW -- Root layout CSS for flash-of-white prevention, acceptable |
| `vet/src/components/SpeciesChip.tsx` | `#f3e5f5`, `#7b1fa2`, `#fff8e1`, `#f57f17` (4 instances) | MEDIUM -- Sheep and poultry colors are hardcoded, not from theme |

### 2.2 Theme Token Usage Patterns

- **Admin components (RiskBadge, SpeciesChip, StatCard, AdminSidebar)**: All reference the `colors` export from `theme.ts` -- good centralized approach
- **Admin pages**: Login page uses MUI `sx` theme references (`primary.dark`, `background.default`) -- correct
- **Collection pages**: Zero hardcoded hex colors outside theme.ts -- excellent
- **Vet pages**: Zero hardcoded hex colors outside theme.ts -- excellent
- **Vet theme.ts**: Exports a `colors` object for status mapping -- good pattern, mirrors Admin approach

### 2.3 Admin `colors` Export

The Admin theme exports a comprehensive `colors` object (20 tokens) that components use instead of raw hex. This is a strong pattern. The Vet package does something similar with its status-specific `colors` export. Collection has no equivalent -- it relies purely on MUI theme palette, which is also acceptable since it has fewer custom components.

---

## 3. Typography Consistency

### 3.1 Font Family

All three packages use `"IBM Plex Sans", system-ui, -apple-system, sans-serif` -- Consistent.

### 3.2 Typography Variants

| Setting | Admin | Collection | Vet |
|---------|-------|------------|-----|
| h4.fontWeight | 700 | MUI default | MUI default |
| h5.fontWeight | 700 | MUI default | MUI default |
| h6.fontWeight | 600 | MUI default | MUI default |
| h6.fontSize | 14px | MUI default (1.25rem) | MUI default |
| body1.fontSize | 13.5px | MUI default (1rem) | MUI default |
| body2.fontSize | 12px | MUI default (0.875rem) | MUI default |
| body2.color | hardcoded `#5f7a74` | MUI default | MUI default |
| caption | custom (11px, uppercase, 600) | MUI default | MUI default |

**Assessment**: Admin has extensive typography customization. Collection and Vet rely on MUI defaults. This means the same `<Typography variant="body1">` renders at 13.5px in Admin but 16px (1rem) in Collection/Vet. Heading weights also differ. This is not a visual regression risk (separate apps) but impacts brand consistency if a user navigates between apps.

### 3.3 Monospace Font

Only Admin defines a `monoFont` export (`IBM Plex Mono`). No other package uses monospace typography.

---

## 4. Component Pattern Consistency

### 4.1 Login Pages

All three login pages share the same structure:
- Centered card (maxWidth 440, borderRadius 3, boxShadow 3)
- Colored header banner with emoji + brand name + portal subtitle
- Phone/OTP two-step flow with identical UX
- Same OTP input boxes (width 52, 6 digits, auto-focus)

**Differences**:
- Admin uses `bgcolor: "primary.dark"` and explicit button styling (`bgcolor: "primary.dark"`)
- Collection uses `bgcolor: "primary.dark"` and default MUI button styling
- Vet uses `bgcolor: "primary.dark"` and default MUI button styling
- Admin login button has custom border radius (2) vs theme default (8)

### 4.2 Navigation

| Pattern | Admin | Collection | Vet |
|---------|-------|------------|-----|
| Component | Fixed sidebar (260px) | Top AppBar with Tabs | Top AppBar with Tabs |
| Brand display | Logo + "PashuRaksha" + "ERP Admin" | "PashuRaksha" + centre name | "PashuRaksha" + "Vet Portal" |
| Navigation style | Vertical list with sections | Horizontal tabs | Horizontal tabs |
| Active indicator | Left border (3px green) | Tab indicator (white) | Tab indicator (white) |

**Assessment**: Admin uses a sidebar pattern; Collection and Vet use a top AppBar pattern. This is intentional (admin is data-heavy, others are task-focused) and the NavBar implementations for Collection and Vet are nearly identical -- good consistency for similar app types.

### 4.3 Shared Components

| Component | Admin | Collection | Vet | Consistent? |
|-----------|-------|------------|-----|-------------|
| SpeciesChip | Full emoji + species map, uses `colors` export | N/A | Hardcoded sheep/poultry colors, no emoji | DIVERGED |
| StatCard | Border-top accent, trend chip, `colors` export | N/A | Simpler: icon-left layout, uses MUI tokens | DIFFERENT DESIGN |
| RiskBadge | Uses `colors` export | N/A | N/A | N/A |
| EmptyState | N/A (exists in `components/`) | N/A | Clean MUI-token implementation | N/A |
| ErrorBoundary | `error.tsx` + `global-error.tsx` | `ErrorBoundary.tsx` | `ErrorBoundary.tsx` | Different patterns (Next.js vs React) |
| AuthGuard | In `providers.tsx` | `AuthGuard.tsx` | `AuthGuard.tsx` | Similar logic, different structure |

### 4.4 SpeciesChip Divergence (HIGH)

Admin's SpeciesChip:
- Uses emoji prefixes (cow, buffalo, goat, etc.)
- References centralized `colors` export for all species
- Handles 8 species variants

Vet's SpeciesChip:
- No emoji prefixes
- Uses `vetTheme.palette` for cattle/buffalo/goat
- Hardcodes `#f3e5f5`/`#7b1fa2` for sheep and `#fff8e1`/`#f57f17` for poultry
- Only handles 5 species variants

This means the same animal species renders differently between Admin and Vet.

---

## 5. Responsive Breakpoints

### 5.1 Breakpoint Usage

**No package uses MUI responsive breakpoints** (`xs:`, `sm:`, `md:`, `lg:`, `xl:` in sx props, `useMediaQuery`, or theme `breakpoints`).

- Admin: Fixed 260px sidebar with no collapse mechanism. No responsive grid adjustments.
- Collection: AppBar is inherently responsive (Tabs wrap). No explicit breakpoint handling.
- Vet: Same as Collection.

### 5.2 Viewport Overflow Testing

The existing E2E tests check for horizontal overflow at 1440px and 1024px (admin only). No mobile viewport tests exist. The admin sidebar (260px fixed) will cause layout issues below ~768px.

---

## 6. Playwright Visual Regression Setup

### 6.1 Current State

**Config**: `e2e/playwright.config.ts` -- present and well-configured:
- Three projects: admin (3000), collection (3001), vet (3002)
- Desktop Chrome for all
- `snapshotPathTemplate` configured for screenshot storage
- Web server commands for all three packages
- HTML + line reporters

**Visual baseline spec**: `e2e/visual/visual-baseline.spec.ts` -- present with:
- Admin: 4 tests (dashboard, farmers, login, map with Leaflet masking)
- Collection: 1 test (login page)
- Vet: 1 test (login page)
- `maxDiffPixelRatio: 0.02` (2% tolerance, reasonable)
- Map view uses `0.05` with `.leaflet-container` mask (good)

**Functional smoke tests**: `e2e/admin-smoke.spec.ts` -- 16 tests covering dashboard, farmers, animals, health, vaccinations, map, sidebar navigation, and basic responsive checks.

### 6.2 Gaps

| Gap | Severity |
|-----|----------|
| No `animations: "disabled"` in Playwright config `expect.toHaveScreenshot` | MEDIUM |
| No consistent viewport/locale/timezone in config | MEDIUM |
| No `threshold` per-pixel setting (only `maxDiffPixelRatio`) | LOW |
| Visual baselines do not cover authenticated admin pages (dashboard, farmers) require auth cookie setup | HIGH |
| Collection/Vet only test login -- no post-auth page coverage | MEDIUM |
| No component-level screenshot tests (StatCard, RiskBadge, SpeciesChip) | LOW |
| No tablet/mobile viewport projects | MEDIUM |
| No dynamic content masking (timestamps, counts, charts) in visual specs | MEDIUM |
| No `data-testid` attributes on Vet or Collection components for test targeting | MEDIUM |
| Admin has only 1 `data-testid` outside tests (`trend-chip` in StatCard) | MEDIUM |

### 6.3 Missing `toHaveScreenshot` Config

The Playwright config has no `expect.toHaveScreenshot` block. The per-test `maxDiffPixelRatio` works but should be centralized with:
- `animations: "disabled"`
- `threshold: 0.2`
- Consistent viewport (`1280x720`)
- `locale: "en-IN"` / `timezoneId: "Asia/Kolkata"`

---

## 7. Findings Summary

### CRITICAL (0)

None.

### HIGH (2)

| ID | Finding | Location | Impact |
|----|---------|----------|--------|
| H-1 | Semantic color drift across packages: error, warning, success, info colors differ between Admin/Collection and Vet without design justification | `vet/src/theme.ts` vs `admin/src/theme/theme.ts` | A "critical" health alert renders in different red shades across apps |
| H-2 | Visual baseline tests lack auth setup -- authenticated pages (dashboard, tables) are not covered | `e2e/visual/visual-baseline.spec.ts` | Visual regressions on data-rich pages will go undetected |

### MEDIUM (5)

| ID | Finding | Location | Impact |
|----|---------|----------|--------|
| M-1 | SpeciesChip implementations diverge between Admin and Vet (emoji vs no-emoji, different color maps, hardcoded hex in Vet) | `admin/src/components/SpeciesChip.tsx`, `vet/src/components/SpeciesChip.tsx` | Same species looks different to admin vs vet user |
| M-2 | GISMap.tsx uses hardcoded hex colors instead of importing from `colors` export | `admin/src/components/GISMap.tsx:18-21,113-136` | Color drift risk if theme palette changes |
| M-3 | No responsive breakpoints in any package; admin sidebar is fixed 260px with no collapse | All packages | Admin UI will overflow or be unusable below 768px |
| M-4 | Chip component overrides inconsistent: Admin (borderRadius 10, 12px), Vet (borderRadius 6, 11px), Collection (none) | Theme files | Same semantic chip looks different across apps |
| M-5 | Playwright visual config missing `animations: "disabled"`, consistent viewport, locale settings | `e2e/playwright.config.ts` | Flaky visual regression tests when baselines are generated |

### LOW (4)

| ID | Finding | Location | Impact |
|----|---------|----------|--------|
| L-1 | Typography variants only customized in Admin; Collection/Vet use MUI defaults | Theme files | body1 renders at 13.5px in Admin vs 16px elsewhere |
| L-2 | No `data-testid` attributes on Vet or Collection components | All component files | Cannot target components for visual regression screenshots |
| L-3 | Admin `body2.color` is hardcoded in typography config instead of using `text.secondary` | `admin/src/theme/theme.ts:20` | Minor -- effectively same value |
| L-4 | No component-level visual regression tests (StatCard, RiskBadge, SpeciesChip variants) | `e2e/visual/visual-baseline.spec.ts` | Fine-grained component regressions undetected |

---

## 8. Recommendations

### Immediate (before baseline generation)

1. **Unify semantic colors**: Align error/warning/success/info across all three themes. Only primary and secondary should differ per role.
2. **Add auth cookie setup** to visual baseline spec `beforeEach` for authenticated page screenshots.
3. **Add `expect.toHaveScreenshot`** config block to `playwright.config.ts` with `animations: "disabled"`, viewport, locale, threshold.

### Short-term (before release)

4. **Consolidate SpeciesChip**: Extract to a shared design-tokens package or align implementations manually.
5. **Add `data-testid` attributes** to key components across all packages for test targeting.
6. **Expand visual baseline coverage**: Add authenticated admin pages (dashboard, farmers, animals, health) and collection/vet post-auth pages.
7. **Fix GISMap.tsx**: Import colors from theme export instead of hardcoding hex values.

### Post-release

8. **Add responsive breakpoints**: Implement sidebar collapse for admin, test at tablet/mobile viewports.
9. **Unify Chip overrides**: Align borderRadius and fontSize across all theme configs.
10. **Add component-level screenshot tests** for badge/chip/card variants.

---

## 9. Baseline Artifact Inventory

| Artifact | Path | Status |
|----------|------|--------|
| Playwright config | `e2e/playwright.config.ts` | EXISTS -- needs enhancement |
| Visual baseline spec | `e2e/visual/visual-baseline.spec.ts` | EXISTS -- needs expansion |
| Admin smoke tests | `e2e/admin-smoke.spec.ts` | EXISTS -- 16 tests, good coverage |
| Screenshot baselines | `e2e/visual/screenshots/` | NOT YET GENERATED -- first run needed |
| Admin theme | `packages/admin/src/theme/theme.ts` | EXISTS |
| Collection theme | `packages/collection/src/theme.ts` | EXISTS |
| Vet theme | `packages/vet/src/theme.ts` | EXISTS |

---

```json
{"agent":"vis-regress","verdict":"WARN","critical":0,"high":2,"medium":5,"low":4}
```
