/**
 * Playwright E2E smoke tests for PashuRaksha Admin (Next.js)
 *
 * Run with:
 *   cd pashu-erp/packages/admin
 *   npx playwright test ../../e2e/admin-smoke.spec.ts
 *
 * Requires admin dev server running on http://localhost:3000
 */
import { test, expect, Page } from '@playwright/test';

const BASE = 'http://localhost:3000';

async function goto(page: Page, path: string) {
  await page.goto(`${BASE}${path}`);
  await page.waitForLoadState('networkidle');
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
test.describe('Dashboard', () => {
  test('loads and shows all 6 stat cards', async ({ page }) => {
    await goto(page, '/');
    await expect(page.locator('[data-testid="stat-card"]')).toHaveCount(6);
  });

  test('sidebar navigation links are visible', async ({ page }) => {
    await goto(page, '/');
    await expect(page.getByText('Dashboard')).toBeVisible();
    await expect(page.getByText('Farmers')).toBeVisible();
    await expect(page.getByText('Animals')).toBeVisible();
    await expect(page.getByText('Milk Collection')).toBeVisible();
  });

  test('recharts area chart renders', async ({ page }) => {
    await goto(page, '/');
    // Recharts renders an SVG
    await expect(page.locator('.recharts-responsive-container svg').first()).toBeVisible();
  });

  test('GIS disease alert map renders', async ({ page }) => {
    await goto(page, '/');
    await expect(page.locator('.leaflet-container').first()).toBeVisible();
  });
});

// ── Farmers Page ──────────────────────────────────────────────────────────────
test.describe('Farmers Page', () => {
  test('loads farmers table with data', async ({ page }) => {
    await goto(page, '/farmers');
    await expect(page.locator('table')).toBeVisible();
    // Should have at least one data row
    const rows = page.locator('tbody tr');
    await expect(rows).toHaveCountGreaterThan(0);
  });

  test('search filters table rows', async ({ page }) => {
    await goto(page, '/farmers');
    const initialCount = await page.locator('tbody tr').count();
    await page.fill('input[placeholder*="Search"]', 'Mysuru');
    await page.waitForTimeout(300); // debounce
    const filteredCount = await page.locator('tbody tr').count();
    expect(filteredCount).toBeLessThanOrEqual(initialCount);
  });

  test('clearing search restores all rows', async ({ page }) => {
    await goto(page, '/farmers');
    const initialCount = await page.locator('tbody tr').count();
    await page.fill('input[placeholder*="Search"]', 'xyz_no_results');
    await page.fill('input[placeholder*="Search"]', '');
    await page.waitForTimeout(300);
    expect(await page.locator('tbody tr').count()).toBe(initialCount);
  });

  test('pagination controls are present', async ({ page }) => {
    await goto(page, '/farmers');
    await expect(page.locator('.MuiTablePagination-root')).toBeVisible();
  });
});

// ── Animals Page ──────────────────────────────────────────────────────────────
test.describe('Animals Page', () => {
  test('species filter dropdown renders', async ({ page }) => {
    await goto(page, '/animals');
    await expect(page.locator('text=Species')).toBeVisible();
  });

  test('filtering by species reduces visible rows', async ({ page }) => {
    await goto(page, '/animals');
    const initialCount = await page.locator('tbody tr').count();
    // Open species dropdown and select Cattle
    await page.click('text=Species');
    await page.click('[data-value="Cattle"]');
    await page.waitForTimeout(200);
    const cattleCount = await page.locator('tbody tr').count();
    expect(cattleCount).toBeLessThanOrEqual(initialCount);
  });

  test('RiskBadge chips are visible in health status column', async ({ page }) => {
    await goto(page, '/animals');
    await expect(page.locator('[class*="MuiChip"]').first()).toBeVisible();
  });
});

// ── Health Alerts Page ────────────────────────────────────────────────────────
test.describe('Health Alerts Page', () => {
  test('risk level filter dropdown exists', async ({ page }) => {
    await goto(page, '/health');
    await expect(page.locator('text=Risk Level')).toBeVisible();
  });

  test('critical alerts appear with red badge', async ({ page }) => {
    await goto(page, '/health');
    // Select Critical filter
    await page.click('text=Risk Level');
    await page.click('[data-value="critical"]');
    await page.waitForTimeout(200);
    // All visible badges should now say Critical
    const badges = page.locator('[class*="MuiChip"]');
    const count = await badges.count();
    for (let i = 0; i < count; i++) {
      const text = await badges.nth(i).textContent();
      if (text?.trim()) expect(text).toMatch(/Critical/i);
    }
  });
});

// ── Vaccinations Page ─────────────────────────────────────────────────────────
test.describe('Vaccinations Page', () => {
  test('shows 3 summary stat cards', async ({ page }) => {
    await goto(page, '/vaccinations');
    await expect(page.locator('[data-testid="vacc-stat-card"]')).toHaveCount(3);
  });

  test('linear progress bars are visible for coverage', async ({ page }) => {
    await goto(page, '/vaccinations');
    await expect(page.locator('.MuiLinearProgress-root').first()).toBeVisible();
  });
});

// ── Map View Page ─────────────────────────────────────────────────────────────
test.describe('Map View Page', () => {
  test('full map renders with legend', async ({ page }) => {
    await goto(page, '/map');
    await expect(page.locator('.leaflet-container')).toBeVisible();
    await expect(page.locator('text=Critical Alert')).toBeVisible();
    await expect(page.locator('text=Milk Center')).toBeVisible();
  });
});

// ── Sidebar Navigation ────────────────────────────────────────────────────────
test.describe('Sidebar Navigation', () => {
  const navItems = [
    { label: 'Dashboard', path: '/' },
    { label: 'Farmers', path: '/farmers' },
    { label: 'Animals', path: '/animals' },
    { label: 'Milk Collection', path: '/milk' },
    { label: 'Health Alerts', path: '/health' },
    { label: 'Vaccinations', path: '/vaccinations' },
    { label: 'Govt Schemes', path: '/schemes' },
    { label: 'Marketplace', path: '/marketplace' },
    { label: 'Income Analytics', path: '/income' },
    { label: 'Map View', path: '/map' },
    { label: 'IoT Devices', path: '/iot' },
  ];

  for (const { label, path } of navItems) {
    test(`navigates to ${label} page`, async ({ page }) => {
      await goto(page, '/');
      await page.click(`text=${label}`);
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain(path === '/' ? '' : path);
      // Page should not show a 404 error
      await expect(page.locator('text=404')).not.toBeVisible();
    });
  }

  test('active nav item is highlighted', async ({ page }) => {
    await goto(page, '/farmers');
    const farmersLink = page.locator('[data-testid="nav-farmers"]');
    const style = await farmersLink.getAttribute('style') ?? '';
    // Active state adds left border with primary sidebar color
    expect(style).toMatch(/border-left|borderLeft/i);
  });
});

// ── Responsive (basic) ────────────────────────────────────────────────────────
test.describe('Responsive Behavior', () => {
  test('no horizontal overflow on 1440px desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await goto(page, '/');
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 5); // 5px tolerance
  });

  test('no horizontal overflow on 1024px tablet', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await goto(page, '/farmers');
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 5);
  });
});
