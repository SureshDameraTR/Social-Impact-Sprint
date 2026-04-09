# PashuRaksha ERP — Test Suite

## Install testing dependencies

### Mobile (React Native / Expo)
```bash
cd packages/mobile
npm install --save-dev \
  jest-expo \
  @testing-library/react-native \
  @testing-library/jest-native \
  @types/jest
```

### Admin (Next.js / MUI)
```bash
cd packages/admin
npm install --save-dev \
  jest \
  jest-environment-jsdom \
  @testing-library/react \
  @testing-library/jest-dom \
  @testing-library/user-event \
  @types/jest
```

### E2E (Playwright)
```bash
cd pashu-erp   # monorepo root
npm install --save-dev @playwright/test
npx playwright install chromium
```

## Run tests

```bash
# Mobile unit tests
cd packages/mobile && npx jest

# Mobile unit tests (with coverage)
cd packages/mobile && npx jest --coverage

# Admin unit tests
cd packages/admin && npx jest

# E2E (requires admin dev server)
cd pashu-erp && npx playwright test e2e/admin-smoke.spec.ts
# Or with automatic server startup:
cd pashu-erp && npx playwright test
```

## Test file locations

```
pashu-erp/
├── e2e/
│   ├── playwright.config.ts
│   └── admin-smoke.spec.ts          # 30 Playwright E2E tests
│
└── packages/
    ├── mobile/
    │   ├── jest.config.js
    │   └── src/__tests__/
    │       ├── components/
    │       │   ├── AnimalCard.test.tsx       # 10 tests
    │       │   ├── FilterChips.test.tsx      # 6 tests
    │       │   ├── TriageCard.test.tsx       # 8 tests
    │       │   ├── MicButton.test.tsx        # 6 tests
    │       │   └── LoadingSkeleton.test.tsx  # 5 tests
    │       └── flows/
    │           ├── milk-recording.test.tsx   # 6 tests
    │           └── health-triage.test.tsx    # 6 tests
    │
    └── admin/
        ├── jest.config.js
        ├── jest.setup.ts
        └── src/__tests__/
            ├── components/
            │   ├── StatCard.test.tsx         # 9 tests
            │   ├── RiskBadge.test.tsx        # 5 tests
            │   └── SpeciesChip.test.tsx      # 4 tests
            └── pages/
                └── farmers.test.tsx         # 9 tests
```

Total: ~74 tests across unit + integration + E2E layers
