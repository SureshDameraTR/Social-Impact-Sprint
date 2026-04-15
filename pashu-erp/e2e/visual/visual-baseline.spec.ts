/**
 * Visual regression baseline tests for PashuRaksha frontends.
 *
 * Captures full-page screenshots and compares against stored baselines.
 * Run: npx playwright test e2e/visual/
 *
 * First run generates baselines in e2e/visual/screenshots/.
 * Subsequent runs diff against them. Update baselines with:
 *   npx playwright test e2e/visual/ --update-snapshots
 */
import { test, expect } from '@playwright/test';

const SERVICES = {
  admin: 'http://localhost:3000',
  collection: 'http://localhost:3001',
  vet: 'http://localhost:3002',
};

// ── Admin Pages ──────────────────────────────────────────────────────────────

test.describe('Admin Visual Baselines', () => {
  test('dashboard', async ({ page }) => {
    await page.goto(`${SERVICES.admin}/`);
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('admin-dashboard.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.02,
    });
  });

  test('farmers list', async ({ page }) => {
    await page.goto(`${SERVICES.admin}/farmers`);
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('admin-farmers.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.02,
    });
  });

  test('login page', async ({ page }) => {
    await page.goto(`${SERVICES.admin}/login`);
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('admin-login.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.02,
    });
  });

  test('map view', async ({ page }) => {
    await page.goto(`${SERVICES.admin}/map`);
    await page.waitForLoadState('networkidle');
    // Map tiles are non-deterministic — mask the map container
    await expect(page).toHaveScreenshot('admin-map.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.05,
      mask: [page.locator('.leaflet-container')],
    });
  });
});

// ── Collection Centre Pages ──────────────────────────────────────────────────

test.describe('Collection Visual Baselines', () => {
  test('login page', async ({ page }) => {
    await page.goto(`${SERVICES.collection}/`);
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('collection-login.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.02,
    });
  });
});

// ── Vet App Pages ────────────────────────────────────────────────────────────

test.describe('Vet Visual Baselines', () => {
  test('login page', async ({ page }) => {
    await page.goto(`${SERVICES.vet}/`);
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('vet-login.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.02,
    });
  });
});
