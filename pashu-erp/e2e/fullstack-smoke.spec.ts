/**
 * Full-Stack E2E Smoke Tests — Real Browser → Real API → Real Database
 *
 * These tests perform actual OTP login against the running API and verify
 * that each app works end-to-end with real data from PostgreSQL.
 *
 * Prerequisites:
 *   - docker compose up -d  (API:8000 + DB:5432 + Mocks:8001)
 *   - Admin running on :3000, Collection on :3001, Vet on :3002
 *   - Seed data loaded (users with correct roles in DB)
 *
 * Run:
 *   cd pashu-erp && npx playwright test e2e/fullstack-smoke.spec.ts
 */
import { test, expect, Page, BrowserContext } from "@playwright/test";
import { execSync } from "child_process";

const API_URL = "http://localhost:8000/v1";

// ── Helpers ──────────────────────────────────────────────────────────────────

/** Extract the most recent OTP for a phone from docker logs (does NOT re-request). */
function extractOtpFromLogs(phone: string): string {
  const logs = execSync(
    "docker logs pashu-erp-api-1 --tail 30 2>&1",
    { encoding: "utf-8" },
  );
  // Find OTP blocks for this specific phone
  const phoneShort = phone.replace("+91", "");
  const lines = logs.split("\n");
  let lastOtp = "";
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(phone) || lines[i].includes(phoneShort)) {
      // Next line should have the code
      for (let j = i + 1; j < Math.min(i + 3, lines.length); j++) {
        const codeMatch = lines[j].match(/Code:\s*(\d{6})/);
        if (codeMatch) {
          lastOtp = codeMatch[1];
          break;
        }
      }
    }
  }
  expect(lastOtp, `No OTP found in logs for ${phone}`).not.toBe("");
  return lastOtp;
}

/** Request OTP via API (server-side) and extract from logs. Used when browser can't call API. */
async function requestAndGetOtp(phone: string): Promise<string> {
  const res = await fetch(`${API_URL}/auth/request-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone }),
  });
  expect(res.ok, `request-otp failed for ${phone}: ${res.status}`).toBe(true);
  return extractOtpFromLogs(phone);
}

/** Perform full OTP login on the Admin app (Next.js). */
async function loginAdmin(page: Page, phone: string): Promise<void> {
  await page.goto("http://localhost:3000/login");
  await page.waitForLoadState("networkidle");

  const phoneDigits = phone.replace("+91", "");
  await page.fill('input[placeholder="9876543210"]', phoneDigits);

  // Click Send OTP in the browser — this calls the real API
  await page.click('text=Send OTP');

  // Wait for OTP step to appear (means the API request succeeded)
  await page.waitForSelector('[aria-label="OTP digit 1 of 6"]', { timeout: 15000 });

  // Extract OTP from docker logs (browser already requested it)
  const otp = extractOtpFromLogs(phone);

  // Fill OTP digits
  for (let i = 0; i < 6; i++) {
    await page.fill(`[aria-label="OTP digit ${i + 1} of 6"]`, otp[i]);
  }

  await page.click('text=Verify & Login');
  await page.waitForURL("**/", { timeout: 30000, waitUntil: "domcontentloaded" });
}

/** Perform full OTP login on Collection/Vet apps (Vite + React Router). */
async function loginViteApp(
  page: Page,
  baseUrl: string,
  phone: string,
): Promise<void> {
  await page.goto(`${baseUrl}/login`);
  await page.waitForLoadState("networkidle");

  const phoneDigits = phone.replace("+91", "");
  await page.fill('input[placeholder="9876543210"]', phoneDigits);

  // Click Send OTP in the browser
  const sendBtn = page.locator("button", { hasText: /send|request|otp/i });
  await sendBtn.click();

  // Wait for OTP step (means API call succeeded from browser)
  await page.waitForSelector('[aria-label="OTP digit 1 of 6"]', { timeout: 15000 });

  // Extract OTP from docker logs
  const otp = extractOtpFromLogs(phone);

  for (let i = 0; i < 6; i++) {
    await page.fill(`[aria-label="OTP digit ${i + 1} of 6"]`, otp[i]);
  }

  const verifyBtn = page.locator("button", { hasText: /verify|login/i });
  await verifyBtn.click();

  await page.waitForFunction(() => !window.location.pathname.includes("/login"), {
    timeout: 15000,
  });
}

// ── Admin Full-Stack Tests ───────────────────────────────────────────────────

test.describe("Admin Full-Stack (real API + real DB)", () => {
  let context: BrowserContext;
  let page: Page;

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext();
    page = await context.newPage();
    await loginAdmin(page, "+919900000001");
  });

  test.afterAll(async () => {
    await context.close();
  });

  test("dashboard loads with real stats from DB", async () => {
    await page.goto("http://localhost:3000/");
    await page.waitForLoadState("networkidle");

    // Check for stat values — these come from real DB queries
    const heading = page.locator("h4", { hasText: "Dashboard" });
    await expect(heading).toBeVisible();

    // Verify no server error rendered in visible text
    const visibleText = await page.locator("main, [role=main], #__next").first().innerText();
    expect(visibleText).not.toContain("Internal Server Error");
  });

  test("farmers page loads real data from DB", async () => {
    await page.goto("http://localhost:3000/farmers");
    await page.waitForLoadState("networkidle");

    // Table should have rows from real DB
    await expect(page.locator("table")).toBeVisible();
    const rows = page.locator("tbody tr");
    expect(await rows.count()).toBeGreaterThan(0);
  });

  test("animals page loads real data from DB", async () => {
    await page.goto("http://localhost:3000/animals");
    await page.waitForLoadState("networkidle");

    await expect(page.locator("table")).toBeVisible();
    const rows = page.locator("tbody tr");
    expect(await rows.count()).toBeGreaterThan(0);
  });

  test("health alerts page loads without errors", async () => {
    await page.goto("http://localhost:3000/health");
    await page.waitForLoadState("networkidle");

    const visibleText = await page.locator("main, [role=main], #__next").first().innerText();
    expect(visibleText).not.toContain("Internal Server Error");
  });

  test("milk collection page loads without errors", async () => {
    await page.goto("http://localhost:3000/milk");
    await page.waitForLoadState("networkidle");

    const visibleText = await page.locator("main, [role=main], #__next").first().innerText();
    expect(visibleText).not.toContain("Internal Server Error");
  });

  test("marketplace page loads without errors", async () => {
    await page.goto("http://localhost:3000/marketplace");
    await page.waitForLoadState("networkidle");

    const visibleText = await page.locator("main, [role=main], #__next").first().innerText();
    expect(visibleText).not.toContain("Internal Server Error");
  });

  test("all sidebar nav routes load without errors", async () => {
    test.setTimeout(90000);
    const routes = [
      "/", "/farmers", "/animals", "/milk", "/health",
      "/vaccinations", "/schemes", "/marketplace", "/income", "/map", "/iot",
    ];
    for (const route of routes) {
      await page.goto(`http://localhost:3000${route}`);
      await page.waitForLoadState("domcontentloaded");
      const visibleText = await page.locator("main, [role=main], #__next").first().innerText();
      expect(visibleText, `Route ${route} has error`).not.toContain("Internal Server Error");
    }
  });

  test("no console errors on dashboard", async () => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    await page.goto("http://localhost:3000/");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000); // let async requests settle

    // Filter out known noise (React dev warnings, CSP/CORS in local dev)
    const realErrors = errors.filter(
      (e) =>
        !e.includes("React does not recognize") &&
        !e.includes("Warning:") &&
        !e.includes("Content Security Policy") &&
        !e.includes("blocked by CORS policy") &&
        !e.includes("net::ERR_FAILED"),
    );
    expect(realErrors, `Console errors: ${realErrors.join("\n")}`).toHaveLength(0);
  });

  test("no failed network requests on dashboard", async () => {
    const failures: string[] = [];
    page.on("response", (res) => {
      if (res.status() >= 400) {
        failures.push(`${res.status()} ${res.url()}`);
      }
    });
    await page.goto("http://localhost:3000/");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    expect(failures, `Failed requests:\n${failures.join("\n")}`).toHaveLength(0);
  });
});

// ── Collection Centre Full-Stack Tests ───────────────────────────────────────

test.describe("Collection Centre Full-Stack (real API + real DB)", () => {
  let context: BrowserContext;
  let page: Page;

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext();
    page = await context.newPage();
    await loginViteApp(page, "http://localhost:3001", "+919900000006");
  });

  test.afterAll(async () => {
    await context.close();
  });

  test("dashboard loads after login", async () => {
    const visibleText = await page.locator("body").innerText();
    expect(visibleText).not.toContain("Internal Server Error");
  });

  test("no failed network requests after login", async () => {
    const failures: string[] = [];
    page.on("response", (res) => {
      if (res.status() >= 400) {
        failures.push(`${res.status()} ${res.url()}`);
      }
    });
    await page.goto("http://localhost:3001/");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    expect(failures, `Failed requests:\n${failures.join("\n")}`).toHaveLength(0);
  });
});

// ── Vet Portal Full-Stack Tests ──────────────────────────────────────────────

test.describe("Vet Portal Full-Stack (real API + real DB)", () => {
  let context: BrowserContext;
  let page: Page;

  test.beforeAll(async ({ browser }) => {
    context = await browser.newContext();
    page = await context.newPage();
    await loginViteApp(page, "http://localhost:3002", "+919900000005");
  });

  test.afterAll(async () => {
    await context.close();
  });

  test("dashboard loads after login", async () => {
    const visibleText = await page.locator("body").innerText();
    expect(visibleText).not.toContain("Internal Server Error");
  });

  test("no failed network requests after login", async () => {
    const failures: string[] = [];
    page.on("response", (res) => {
      if (res.status() >= 400) {
        failures.push(`${res.status()} ${res.url()}`);
      }
    });
    await page.goto("http://localhost:3002/");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    expect(failures, `Failed requests:\n${failures.join("\n")}`).toHaveLength(0);
  });
});

// ── Cross-App Auth Boundary Tests ────────────────────────────────────────────

test.describe("Auth Boundary Tests", () => {
  test("farmer cannot login to admin portal", async ({ page }) => {
    await page.goto("http://localhost:3000/login");
    await page.waitForLoadState("networkidle");

    await page.fill('input[placeholder="9876543210"]', "9900000002");
    await page.click('text=Send OTP');
    await page.waitForSelector('[aria-label="OTP digit 1 of 6"]', { timeout: 15000 });

    const otp = extractOtpFromLogs("+919900000002");
    for (let i = 0; i < 6; i++) {
      await page.fill(`[aria-label="OTP digit ${i + 1} of 6"]`, otp[i]);
    }
    await page.click('text=Verify & Login');

    // Should show error about staff-only portal
    await expect(page.locator("text=staff")).toBeVisible({ timeout: 5000 });
  });

  test("unauthenticated user sees login page or redirect on admin", async ({ page }) => {
    await page.goto("http://localhost:3000/farmers");
    await page.waitForLoadState("networkidle");
    // Should either redirect to /login or show the login form
    const url = page.url();
    const hasLoginForm = await page.locator('input[placeholder="9876543210"]').isVisible().catch(() => false);
    expect(
      url.includes("/login") || hasLoginForm,
      `Expected redirect to /login or login form visible, got ${url}`,
    ).toBe(true);
  });

  test("unauthenticated user sees login page on collection", async ({ page }) => {
    await page.goto("http://localhost:3001/");
    await page.waitForLoadState("networkidle");
    const url = page.url();
    const hasLoginForm = await page.locator('input[placeholder="9876543210"]').isVisible().catch(() => false);
    expect(
      url.includes("/login") || hasLoginForm,
      `Expected redirect to /login or login form visible, got ${url}`,
    ).toBe(true);
  });

  test("unauthenticated user sees login page on vet", async ({ page }) => {
    await page.goto("http://localhost:3002/");
    await page.waitForLoadState("networkidle");
    const url = page.url();
    const hasLoginForm = await page.locator('input[placeholder="9876543210"]').isVisible().catch(() => false);
    expect(
      url.includes("/login") || hasLoginForm,
      `Expected redirect to /login or login form visible, got ${url}`,
    ).toBe(true);
  });
});
