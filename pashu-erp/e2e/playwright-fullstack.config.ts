import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  fullyParallel: false,
  retries: 0,
  reporter: 'line',
  use: { trace: 'on-first-retry', screenshot: 'only-on-failure' },
  projects: [
    {
      name: 'fullstack',
      use: { ...devices['Desktop Chrome'] },
      testMatch: ['fullstack-smoke.spec.ts'],
    },
  ],
});
