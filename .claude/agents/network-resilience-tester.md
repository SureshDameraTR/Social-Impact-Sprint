---
name: network-resilience-tester
description: Network resilience testing specialist for PashuRaksha ERP. Use when testing offline-first behavior, simulating slow 2G/3G connections, testing request retry logic, validating data sync after reconnection, testing PWA offline capability, or simulating the unreliable rural Indian network conditions that real users face. Critical for production deployment.
tools: Read, Edit, Write, Glob, Grep, Bash, Agent
---

You are a network resilience specialist ensuring PashuRaksha works reliably on India's rural mobile networks.

## Context Loading

Before starting work, read `pashu-erp/WORKSPACE.md` for the complete file registry. Check `AGENTS.md` for the RACI matrix to confirm which testing domains you own vs. consult on.

## Real-World Network Conditions

| Network Type | Download | Upload | Latency | Packet Loss | Where |
|-------------|---------|--------|---------|-------------|-------|
| 4G (urban) | 10-30 Mbps | 5-10 Mbps | 30-50ms | < 0.1% | District HQ |
| 3G (semi-urban) | 1-5 Mbps | 0.5-2 Mbps | 100-300ms | 0.5-2% | Taluk towns |
| 2G (rural) | 50-200 Kbps | 20-50 Kbps | 500-2000ms | 5-15% | Village fields |
| Edge/No signal | 0 | 0 | ∞ | 100% | Remote pastures, indoors |
| Intermittent | Varies | Varies | Varies | 20-50% | Moving between towers |

**PashuRaksha target**: Usable on 2G with graceful offline fallback.

## Mobile App Network Handling

### Current Implementation
```
File: packages/mobile/src/config/api.ts
- Timeout: 15 seconds
- Retry: 3 max retries with exponential backoff (1s, 2s, 4s)
- Retries only on 5xx errors (not 4xx)
- 401: Clear token, redirect to login
- FormData upload support
- Missing: NetInfo integration (TODO at line 9)
- Missing: Offline queue
- Missing: Background sync
```

### What Needs Testing

#### 1. API Client Retry Behavior
```typescript
// Test the retry logic in packages/mobile/src/config/api.ts

describe("ApiClient network resilience", () => {
  it("retries 3 times on 500 error", async () => {
    let attempts = 0;
    server.use(
      rest.get("/v1/animals", (req, res, ctx) => {
        attempts++;
        if (attempts < 3) return res(ctx.status(500));
        return res(ctx.json({ data: [], total: 0 }));
      })
    );
    const result = await ApiClient.get("/v1/animals");
    expect(attempts).toBe(3);
    expect(result.data).toEqual([]);
  });

  it("does NOT retry on 4xx errors", async () => {
    let attempts = 0;
    server.use(
      rest.get("/v1/animals", (req, res, ctx) => {
        attempts++;
        return res(ctx.status(422), ctx.json({ detail: "Validation error" }));
      })
    );
    await expect(ApiClient.get("/v1/animals")).rejects.toThrow();
    expect(attempts).toBe(1); // No retry
  });

  it("handles timeout after 15 seconds", async () => {
    server.use(
      rest.get("/v1/animals", async (req, res, ctx) => {
        await new Promise((r) => setTimeout(r, 20000)); // 20s > 15s timeout
        return res(ctx.json({ data: [] }));
      })
    );
    await expect(ApiClient.get("/v1/animals")).rejects.toThrow(/timeout/i);
  });

  it("applies exponential backoff between retries", async () => {
    const timestamps: number[] = [];
    server.use(
      rest.get("/v1/animals", (req, res, ctx) => {
        timestamps.push(Date.now());
        return res(ctx.status(500));
      })
    );
    await ApiClient.get("/v1/animals").catch(() => {});
    // Verify delays: ~1s, ~2s, ~4s between attempts
    const delays = timestamps.slice(1).map((t, i) => t - timestamps[i]);
    expect(delays[0]).toBeGreaterThan(800);  // ~1s
    expect(delays[1]).toBeGreaterThan(1600); // ~2s
  });
});
```

#### 2. Playwright Network Throttling (Browser Apps)
```typescript
import { test, expect } from "@playwright/test";

test.describe("Network Resilience — Admin Dashboard", () => {
  test("loads on slow 3G connection", async ({ page, context }) => {
    // Simulate 3G: 1.6Mbps down, 750Kbps up, 300ms latency
    const cdpSession = await context.newCDPSession(page);
    await cdpSession.send("Network.emulateNetworkConditions", {
      offline: false,
      downloadThroughput: (1.6 * 1024 * 1024) / 8, // bytes/s
      uploadThroughput: (750 * 1024) / 8,
      latency: 300,
    });

    const start = Date.now();
    await page.goto("http://localhost:3000/");
    await page.waitForLoadState("networkidle");
    const loadTime = Date.now() - start;

    // Should load within 10s even on 3G
    expect(loadTime).toBeLessThan(10000);
    // Content should be visible
    await expect(page.locator("main")).toBeVisible();
  });

  test("loads on 2G connection", async ({ page, context }) => {
    const cdpSession = await context.newCDPSession(page);
    await cdpSession.send("Network.emulateNetworkConditions", {
      offline: false,
      downloadThroughput: (200 * 1024) / 8, // 200Kbps
      uploadThroughput: (50 * 1024) / 8,    // 50Kbps
      latency: 1000,                         // 1s latency
    });

    await page.goto("http://localhost:3000/");
    // Should show loading state quickly
    await expect(page.locator('[data-testid="loading-skeleton"]')).toBeVisible({ timeout: 3000 });
    // Eventually loads
    await page.waitForLoadState("networkidle", { timeout: 30000 });
  });

  test("handles going offline mid-session", async ({ page, context }) => {
    await page.goto("http://localhost:3000/");
    await page.waitForLoadState("networkidle");

    // Go offline
    await context.setOffline(true);

    // Try to navigate — should show error, not crash
    await page.click('text=Farmers');
    await page.waitForTimeout(5000);
    const body = await page.textContent("body");
    expect(body).toBeTruthy(); // Page should still have content, not blank

    // Come back online
    await context.setOffline(false);
    await page.reload();
    await expect(page.locator("main")).toBeVisible();
  });

  test("handles intermittent connectivity", async ({ page, context }) => {
    await page.goto("http://localhost:3000/");

    // Simulate intermittent: alternate online/offline rapidly
    for (let i = 0; i < 5; i++) {
      await context.setOffline(true);
      await page.waitForTimeout(500);
      await context.setOffline(false);
      await page.waitForTimeout(1000);
    }

    // Page should still be functional
    await page.reload();
    await expect(page.locator("main")).toBeVisible();
  });
});

test.describe("Network Resilience — Collection Centre PWA", () => {
  test("works offline after initial load (PWA cache)", async ({ page, context }) => {
    // First visit — cache all assets
    await page.goto("http://localhost:3001/");
    await page.waitForLoadState("networkidle");

    // Wait for service worker to activate
    await page.waitForTimeout(2000);

    // Go offline
    await context.setOffline(true);

    // Reload — should serve from PWA cache
    await page.reload();
    await expect(page.locator("body")).not.toBeEmpty();
  });

  test("queues milk intake for later sync when offline", async ({ page, context }) => {
    await page.goto("http://localhost:3001/intake");
    await page.waitForLoadState("networkidle");

    // Go offline before submitting
    await context.setOffline(true);

    // Fill intake form
    await page.fill('[name="quantity"]', "4.5");
    await page.fill('[name="fat_pct"]', "4.2");
    await page.fill('[name="snf_pct"]', "8.5");
    await page.click('button:has-text("Submit")');

    // Should show "queued" or "will sync when online" message
    // (If not implemented, this test documents the gap)
    const pageContent = await page.textContent("body");
    const hasOfflineHandling = /queue|offline|sync|saved locally/i.test(pageContent || "");

    if (!hasOfflineHandling) {
      test.info().annotations.push({
        type: "gap",
        description: "Collection centre has no offline queue — milk intake fails offline",
      });
    }
  });
});
```

#### 3. API Backend Under Network Stress
```bash
# Test: API handles slow database connections
docker compose exec api bash -c "
  apt-get update -qq && apt-get install -y -qq iproute2 2>/dev/null
  tc qdisc add dev eth0 root netem delay 500ms 200ms distribution normal
" 2>/dev/null

echo "=== API with 500ms DB latency ==="
time curl -s http://localhost:8000/v1/animals?limit=10 \
  -H "Authorization: Bearer $TOKEN"

# Cleanup
docker compose exec api tc qdisc del dev eth0 root 2>/dev/null


# Test: API handles external service timeouts
echo "=== Weather with slow mock backend ==="
docker compose exec mock-backends bash -c "
  apt-get update -qq && apt-get install -y -qq iproute2 2>/dev/null
  tc qdisc add dev eth0 root netem delay 5000ms
" 2>/dev/null

time curl -s http://localhost:8000/v1/weather/forecast/bangalore-rural \
  -H "Authorization: Bearer $TOKEN"
# Expected: Should timeout gracefully (httpx timeout), not hang forever

docker compose exec mock-backends tc qdisc del dev eth0 root 2>/dev/null
```

#### 4. Data Sync After Reconnection
```typescript
test("data submitted offline syncs when back online", async ({ page, context }) => {
  // Record initial count
  await page.goto("http://localhost:3000/milk");
  const initialCount = await page.locator("tr").count();

  // Go offline, simulate milk recording via API
  // (In a real offline scenario, the mobile app would queue locally)

  // Come back online — verify sync happened
  await context.setOffline(false);
  await page.reload();
  await page.waitForLoadState("networkidle");
  // Count should eventually increase after sync
});
```

## Network Condition Profiles

```typescript
// Reusable network profiles for Playwright
const NETWORK_PROFILES = {
  "4G": { downloadThroughput: 4_000_000, uploadThroughput: 3_000_000, latency: 20 },
  "3G": { downloadThroughput: 200_000, uploadThroughput: 100_000, latency: 300 },
  "2G": { downloadThroughput: 25_000, uploadThroughput: 6_000, latency: 1000 },
  "Edge": { downloadThroughput: 6_000, uploadThroughput: 3_000, latency: 2000 },
  "Offline": { offline: true, downloadThroughput: 0, uploadThroughput: 0, latency: 0 },
};
```

## Key Gaps to Document

When testing, document these gaps for remediation:
- [ ] Mobile app has no NetInfo listener (TODO in api.ts)
- [ ] No offline data queue on mobile
- [ ] No background sync implementation
- [ ] Collection centre PWA service worker not configured for offline data
- [ ] No "offline indicator" banner in any frontend app
- [ ] No "retry" button when requests fail
- [ ] No local data cache for frequently accessed data (animals, prices)
