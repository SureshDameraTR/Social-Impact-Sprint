#!/usr/bin/env python3
"""
CDP test with auth bypass via fetch() override injected before page load.
This patches window.fetch to intercept /auth/me and /v1/* API calls.
"""

import asyncio
import json
import base64
import time
import sys
from pathlib import Path

import websockets
import urllib.request

CDP_HOST = "127.0.0.1"
CDP_PORT = 9222
BASE_URL = "http://localhost:3000"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

# Script to inject before page load — overrides fetch to mock API responses
FETCH_OVERRIDE_SCRIPT = """
(function() {
    const _origFetch = window.fetch;
    let interceptCount = 0;
    window.__cdpInterceptCount = 0;

    window.fetch = function(input, init) {
        const url = typeof input === 'string' ? input : input?.url || '';

        // Mock /auth/me
        if (url.includes('/auth/me')) {
            interceptCount++;
            window.__cdpInterceptCount = interceptCount;
            return Promise.resolve(new Response(JSON.stringify({
                user_id: 'test-admin-001',
                name: 'Test Admin',
                role: 'admin',
                phone: '+919876543210',
            }), {
                status: 200,
                headers: { 'Content-Type': 'application/json' },
            }));
        }

        // Mock /auth/logout
        if (url.includes('/auth/logout')) {
            return Promise.resolve(new Response('{}', { status: 200 }));
        }

        // Mock /v1/ API calls with empty data
        if (url.includes('/v1/')) {
            interceptCount++;
            window.__cdpInterceptCount = interceptCount;

            // For admin stats, return mock stat data
            if (url.includes('/v1/admin/stats') || url.includes('/v1/admin/dashboard')) {
                return Promise.resolve(new Response(JSON.stringify({
                    total_farmers: 1247,
                    total_animals: 3891,
                    active_alerts: 23,
                    daily_milk_litres: 8420,
                    vaccinations_due: 156,
                    scheme_applications: 89,
                }), {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' },
                }));
            }

            // For list endpoints
            if (url.includes('/v1/farmers') || url.includes('/v1/animals') ||
                url.includes('/v1/milk') || url.includes('/v1/health') ||
                url.includes('/v1/alerts') || url.includes('/v1/vaccinations') ||
                url.includes('/v1/schemes') || url.includes('/v1/marketplace') ||
                url.includes('/v1/vet') || url.includes('/v1/iot') ||
                url.includes('/v1/map') || url.includes('/v1/income') ||
                url.includes('/v1/users')) {
                return Promise.resolve(new Response(JSON.stringify({
                    data: [],
                    total: 0,
                }), {
                    status: 200,
                    headers: {
                        'Content-Type': 'application/json',
                        'x-total-count': '0',
                    },
                }));
            }

            // Generic API fallback
            return Promise.resolve(new Response(JSON.stringify({
                data: [],
                total: 0,
            }), {
                status: 200,
                headers: { 'Content-Type': 'application/json' },
            }));
        }

        // Pass through all other requests
        return _origFetch.apply(this, arguments);
    };

    console.log('[CDP-TEST] Fetch override installed');
})();
"""


class CDPClient:
    def __init__(self):
        self.ws = None
        self.msg_id = 0
        self.console_errors = []
        self.js_exceptions = []
        self.console_logs = []
        self._pending = {}
        self._listener_task = None
        self.tab_id = None

    async def connect(self):
        req = urllib.request.Request(
            f"http://{CDP_HOST}:{CDP_PORT}/json/new?about:blank", method="PUT"
        )
        resp = urllib.request.urlopen(req)
        tab_info = json.loads(resp.read())
        ws_url = tab_info["webSocketDebuggerUrl"]
        self.tab_id = tab_info["id"]
        self.ws = await websockets.connect(ws_url, max_size=50 * 1024 * 1024)
        self._listener_task = asyncio.create_task(self._listen())

    async def _listen(self):
        try:
            async for msg in self.ws:
                data = json.loads(msg)
                if "id" in data:
                    mid = data["id"]
                    if mid in self._pending:
                        self._pending[mid].set_result(data)
                elif "method" in data:
                    method = data["method"]
                    if method == "Runtime.consoleAPICalled":
                        params = data.get("params", {})
                        args = params.get("args", [])
                        text = " ".join(
                            a.get("value", a.get("description", "")) for a in args
                        )
                        if params.get("type") == "error" and text.strip():
                            self.console_errors.append(text[:200])
                        elif params.get("type") == "log" and text.strip():
                            self.console_logs.append(text[:200])
                    elif method == "Runtime.exceptionThrown":
                        ex = data["params"].get("exceptionDetails", {})
                        text = ex.get("text", "")
                        exc = ex.get("exception", {})
                        desc = exc.get("description", exc.get("value", ""))
                        self.js_exceptions.append(f"{text}: {desc}"[:200])
        except (websockets.exceptions.ConnectionClosed, asyncio.CancelledError):
            pass

    async def send(self, method, params=None, timeout=30):
        self.msg_id += 1
        mid = self.msg_id
        msg = {"id": mid, "method": method}
        if params:
            msg["params"] = params
        fut = asyncio.get_event_loop().create_future()
        self._pending[mid] = fut
        await self.ws.send(json.dumps(msg))
        try:
            result = await asyncio.wait_for(fut, timeout=timeout)
        finally:
            self._pending.pop(mid, None)
        if "error" in result:
            raise Exception(f"CDP error: {result['error']}")
        return result.get("result", {})

    async def enable_domains(self):
        await self.send("Page.enable")
        await self.send("Runtime.enable")
        await self.send("DOM.enable")

    async def install_fetch_override(self):
        """Inject fetch override that runs before any page script."""
        await self.send("Page.addScriptToEvaluateOnNewDocument", {
            "source": FETCH_OVERRIDE_SCRIPT,
        })

    async def navigate(self, url, wait_seconds=4):
        self.console_errors.clear()
        self.js_exceptions.clear()
        self.console_logs.clear()
        await self.send("Page.navigate", {"url": url})
        for _ in range(40):
            try:
                state = await self.send("Runtime.evaluate", {
                    "expression": "document.readyState",
                    "returnByValue": True,
                })
                if state.get("result", {}).get("value") == "complete":
                    break
            except Exception:
                pass
            await asyncio.sleep(0.5)
        await asyncio.sleep(wait_seconds)

    async def screenshot(self, filename):
        result = await self.send("Page.captureScreenshot", {"format": "png"})
        data = base64.b64decode(result["data"])
        path = SCREENSHOT_DIR / filename
        path.write_bytes(data)
        return str(path)

    async def set_viewport(self, width, height):
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height,
            "deviceScaleFactor": 1, "mobile": width < 768,
        })

    async def evaluate(self, expression):
        result = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        })
        if "exceptionDetails" in result:
            return None
        return result.get("result", {}).get("value")

    async def get_page_analysis(self):
        """Comprehensive page analysis."""
        return await self.evaluate("""
            (() => {
                const r = {};
                r.url = location.href;
                r.pathname = location.pathname;
                r.title = document.title;
                r.bodyTextLen = document.body?.innerText?.length || 0;
                r.bodyPreview = (document.body?.innerText || '').substring(0, 400);

                // MUI
                r.muiTotal = document.querySelectorAll('[class*="Mui"]').length;
                r.muiButtons = document.querySelectorAll('[class*="MuiButton"]').length;
                r.muiTextFields = document.querySelectorAll('[class*="MuiTextField"], [class*="MuiOutlinedInput"]').length;
                r.muiCards = document.querySelectorAll('[class*="MuiCard"]').length;
                r.muiTypography = document.querySelectorAll('[class*="MuiTypography"]').length;
                r.muiSpinners = document.querySelectorAll('[class*="MuiCircularProgress"]').length;
                r.muiChips = document.querySelectorAll('[class*="MuiChip"]').length;
                r.muiTables = document.querySelectorAll('[class*="MuiTable"]').length;
                r.muiDrawers = document.querySelectorAll('[class*="MuiDrawer"]').length;
                r.muiListItems = document.querySelectorAll('[class*="MuiListItem"]').length;
                r.muiLinearProgress = document.querySelectorAll('[class*="MuiLinearProgress"]').length;

                // Layout
                r.hasSidebar = !!document.querySelector('[role="navigation"][aria-label]');
                r.sidebarLinks = document.querySelectorAll('[role="navigation"] a').length;
                r.hasMainContent = !!document.querySelector('#main-content, [role="main"], main');
                r.tables = document.querySelectorAll('table').length;
                r.hasLeaflet = !!document.querySelector('.leaflet-container');
                r.hasRecharts = !!document.querySelector('.recharts-wrapper, .recharts-responsive-container');
                r.statCards = document.querySelectorAll('[data-testid="stat-card"]').length;

                // Scroll
                r.scrollW = document.documentElement.scrollWidth;
                r.clientW = document.documentElement.clientWidth;
                r.overflow = r.scrollW > r.clientW + 5;

                // A11y
                r.skipLink = !!document.querySelector('a[href="#main-content"]');
                r.ariaLabels = document.querySelectorAll('[aria-label]').length;
                r.formLabels = document.querySelectorAll('label').length;
                r.headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6').length;

                // Intercept count
                r.interceptCount = window.__cdpInterceptCount || 0;

                // Data-testid elements
                r.testIds = Array.from(document.querySelectorAll('[data-testid]')).map(
                    el => el.getAttribute('data-testid')
                );

                return r;
            })()
        """)

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
        if self.ws:
            await self.ws.close()
        if self.tab_id:
            try:
                urllib.request.urlopen(
                    f"http://{CDP_HOST}:{CDP_PORT}/json/close/{self.tab_id}"
                )
            except Exception:
                pass


def fmt(info):
    """Format page analysis for printing."""
    preview = (info.get("bodyPreview") or "")[:200].replace("\n", " | ")
    lines = []
    lines.append(f"  URL: {info.get('url','?')}  Title: {info.get('title','?')}")
    lines.append(f"  Body: {info.get('bodyTextLen',0)} chars  Preview: \"{preview}\"")
    lines.append(f"  MUI: total={info.get('muiTotal',0)} buttons={info.get('muiButtons',0)} "
                f"fields={info.get('muiTextFields',0)} cards={info.get('muiCards',0)} "
                f"typo={info.get('muiTypography',0)} spinners={info.get('muiSpinners',0)} "
                f"chips={info.get('muiChips',0)} tables={info.get('muiTables',0)} "
                f"list_items={info.get('muiListItems',0)} drawers={info.get('muiDrawers',0)}")
    lines.append(f"  Layout: sidebar={info.get('hasSidebar',False)} nav_links={info.get('sidebarLinks',0)} "
                f"main_content={info.get('hasMainContent',False)} tables={info.get('tables',0)} "
                f"map={info.get('hasLeaflet',False)} charts={info.get('hasRecharts',False)} "
                f"stat_cards={info.get('statCards',0)}")
    lines.append(f"  Viewport: scroll={info.get('scrollW','?')} client={info.get('clientW','?')} overflow={info.get('overflow',False)}")
    lines.append(f"  A11y: skip={info.get('skipLink',False)} aria={info.get('ariaLabels',0)} "
                f"labels={info.get('formLabels',0)} headings={info.get('headings',0)}")
    lines.append(f"  Intercepts: {info.get('interceptCount',0)}")
    if info.get("testIds"):
        lines.append(f"  data-testid: {info['testIds'][:10]}")
    return "\n".join(lines)


async def main():
    print("=" * 72)
    print("PashuRaksha Admin - CDP Test with Auth Bypass (fetch override)")
    print("=" * 72)

    cdp = CDPClient()
    all_results = []

    try:
        print("\n[SETUP] Connecting...")
        await cdp.connect()
        await cdp.enable_domains()
        print("[SETUP] Installing fetch override (runs before each page load)...")
        await cdp.install_fetch_override()
        print("[SETUP] Ready.\n")

        pages = [
            ("/", "dashboard"),
            ("/login", "login"),
            ("/farmers", "farmers"),
            ("/animals", "animals"),
            ("/milk", "milk"),
            ("/health", "health"),
            ("/vaccinations", "vaccinations"),
            ("/schemes", "schemes"),
            ("/marketplace", "marketplace"),
            ("/income", "income"),
            ("/map", "map"),
            ("/iot", "iot"),
            ("/vet", "vet-dashboard"),
            ("/vet/cases", "vet-cases"),
            ("/vet/alerts", "vet-alerts"),
        ]

        viewports = [
            (1920, 1080, "desktop"),
            (768, 1024, "tablet"),
            (375, 667, "mobile"),
        ]

        for path, name in pages:
            print(f"\n{'='*60}")
            print(f"PAGE: {path} ({name})")
            print(f"{'='*60}")

            for vw, vh, vlabel in viewports:
                print(f"\n  [{vlabel} {vw}x{vh}]")
                await cdp.set_viewport(vw, vh)
                cdp.console_errors.clear()
                cdp.js_exceptions.clear()
                cdp.console_logs.clear()

                await cdp.navigate(f"{BASE_URL}{path}", wait_seconds=5)

                info = await cdp.get_page_analysis()
                ss_name = f"{name}_{vlabel}.png"
                await cdp.screenshot(ss_name)

                if info:
                    print(fmt(info))
                else:
                    print("  ERROR: Could not get page analysis")
                    info = {}

                # Check for our fetch override log
                cdp_logs = [l for l in cdp.console_logs if "CDP-TEST" in l]
                if cdp_logs:
                    print(f"  Fetch override: ACTIVE ({cdp_logs[0]})")
                else:
                    print(f"  Fetch override: NOT DETECTED in console logs")

                # JS errors (excluding CSP)
                real_errs = [e for e in cdp.js_exceptions
                           if "Content Security Policy" not in e and "unsafe-eval" not in e]
                csp_errs = len(cdp.js_exceptions) - len(real_errs)

                issues = []
                body_len = info.get("bodyTextLen", 0) if info else 0

                if body_len < 30 and path != "/login":
                    has_spinner = (info.get("muiSpinners", 0) or 0) > 0 if info else False
                    if has_spinner:
                        issues.append("AUTH-BLOCKED: Page shows spinner (auth check pending/failed)")
                    else:
                        issues.append("CRITICAL: Page blank, no spinner")

                if info and info.get("overflow"):
                    issues.append(f"OVERFLOW: Horizontal scroll at {vlabel}")

                if real_errs:
                    issues.append(f"JS-ERROR: {'; '.join(real_errs[:2])}")

                # Page-specific checks
                if path == "/login" and body_len > 50:
                    if (info.get("muiButtons", 0) or 0) < 1:
                        issues.append("MISSING: No login button")
                    if (info.get("muiTextFields", 0) or 0) < 1:
                        issues.append("MISSING: No input fields")

                if path == "/" and body_len > 100:
                    if not info.get("statCards") and not info.get("hasRecharts"):
                        issues.append("CHECK: Dashboard missing stat cards and charts")

                if path == "/map" and body_len > 100:
                    if not info.get("hasLeaflet"):
                        issues.append("CHECK: Map page missing Leaflet container")

                status = "FAIL" if any("CRITICAL" in i for i in issues) else (
                    "BLOCKED" if any("AUTH-BLOCKED" in i for i in issues) else (
                        "WARN" if issues else "PASS"
                    )
                )
                icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX", "BLOCKED": "##"}.get(status, "??")
                print(f"  [{icon}] {status}")
                if issues:
                    for i in issues:
                        print(f"      -> {i}")
                if csp_errs:
                    print(f"      (CSP eval errors: {csp_errs} -- Next.js dev mode known issue)")

                all_results.append({
                    "page": path, "name": name, "viewport": vlabel,
                    "status": status, "issues": issues,
                    "intercepts": info.get("interceptCount", 0) if info else 0,
                    "body_len": body_len,
                    "mui_total": info.get("muiTotal", 0) if info else 0,
                })

        # Summary
        print("\n" + "=" * 72)
        print("FINAL SUMMARY")
        print("=" * 72)

        by_status = {}
        for r in all_results:
            by_status[r["status"]] = by_status.get(r["status"], 0) + 1

        print(f"Total tests: {len(all_results)}")
        for s in ["PASS", "WARN", "BLOCKED", "FAIL"]:
            if s in by_status:
                print(f"  {s}: {by_status[s]}")

        # Per-page summary
        print(f"\nPer-page results (desktop viewport):")
        for r in all_results:
            if r["viewport"] == "desktop":
                icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX", "BLOCKED": "##"}.get(r["status"], "??")
                extras = f"body={r['body_len']}ch mui={r['mui_total']} intercepts={r['intercepts']}"
                print(f"  [{icon}] {r['page']:20s} {r['status']:8s} {extras}")

        print(f"\nScreenshots: {len(list(SCREENSHOT_DIR.glob('*.png')))} in {SCREENSHOT_DIR}")

    except Exception as e:
        print(f"\nFATAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await cdp.close()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
