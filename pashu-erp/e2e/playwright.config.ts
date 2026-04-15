import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { outputFolder: '../playwright-report' }], ['line']],
  snapshotPathTemplate: '{testDir}/visual/screenshots/{arg}{ext}',

  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'admin',
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:3000' },
      testMatch: ['admin-smoke.spec.ts', 'visual/visual-baseline.spec.ts'],
    },
    {
      name: 'collection',
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:3001' },
      testMatch: ['visual/visual-baseline.spec.ts'],
    },
    {
      name: 'vet',
      use: { ...devices['Desktop Chrome'], baseURL: 'http://localhost:3002' },
      testMatch: ['visual/visual-baseline.spec.ts'],
    },
  ],

  webServer: [
    {
      command: 'cd packages/admin && npx next dev --port 3000',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: 'cd packages/collection && npx vite --port 3001',
      url: 'http://localhost:3001',
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
    {
      command: 'cd packages/vet && npx vite --port 3002',
      url: 'http://localhost:3002',
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
  ],
});
