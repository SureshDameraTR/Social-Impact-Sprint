#!/usr/bin/env python3
"""
CDP deep UI test for PashuRaksha Admin Dashboard.
Phase 1: Test login page thoroughly (renders without API)
Phase 2: Inject auth bypass to test protected pages
Phase 3: Responsive testing on login + any unlocked pages
"""

import asyncio
import json
import base64
import time
import sys
import os
from pathlib import Path

import websockets
import urllib.request

CDP_HOST = "127.0.0.1"
CDP_PORT = 9222
BASE_URL = "http://localhost:3000"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


class CDPClient:
    def __init__(self):
        self.ws = None
        self.msg_id = 0
        self.console_errors = []
        self.js_exceptions = []
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
        print(f"  Created tab: {self.tab_id}")
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
                        if params.get("type") == "error":
                            args = params.get("args", [])
                            text = " ".join(
                                a.get("value", a.get("description", "")) for a in args
                            )
                            if text.strip():
                                self.console_errors.append(text[:200])
                    elif method == "Runtime.exceptionThrown":
                        ex = data["params"].get("exceptionDetails", {})
                        text = ex.get("text", "")
                        exc = ex.get("exception", {})
                        desc = exc.get("description", exc.get("value", ""))
                        full = f"{text}: {desc}"[:200]
                        self.js_exceptions.append(full)
        except websockets.exceptions.ConnectionClosed:
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
        await self.send("Network.enable")

    async def navigate(self, url, wait_seconds=3):
        self.console_errors.clear()
        self.js_exceptions.clear()
        await self.send("Page.navigate", {"url": url})
        # Wait for load
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

    async def get_dom_snapshot(self):
        """Get comprehensive DOM analysis."""
        info = {}
        info["title"] = await self.evaluate("document.title") or ""
        info["url"] = await self.evaluate("window.location.href") or ""
        info["pathname"] = await self.evaluate("window.location.pathname") or ""
        info["body_text_len"] = await self.evaluate("document.body?.innerText?.length || 0") or 0
        info["body_text_preview"] = await self.evaluate(
            "document.body?.innerText?.substring(0, 500) || ''"
        ) or ""

        # MUI analysis
        info["mui_total"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"Mui\"]').length"
        ) or 0
        info["mui_buttons"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"MuiButton\"]').length"
        ) or 0
        info["mui_textfields"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"MuiTextField\"], [class*=\"MuiInput\"], [class*=\"MuiOutlinedInput\"]').length"
        ) or 0
        info["mui_cards"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"MuiCard\"]').length"
        ) or 0
        info["mui_typography"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"MuiTypography\"]').length"
        ) or 0
        info["mui_circular_progress"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"MuiCircularProgress\"]').length"
        ) or 0

        # Layout
        info["has_sidebar"] = await self.evaluate(
            "!!document.querySelector('[role=\"navigation\"][aria-label*=\"Main\"], [role=\"navigation\"][aria-label*=\"navigation\"]')"
        ) or False
        info["has_nav_links"] = await self.evaluate(
            "document.querySelectorAll('[role=\"navigation\"] a').length"
        ) or 0
        info["has_tables"] = await self.evaluate(
            "document.querySelectorAll('table').length"
        ) or 0
        info["has_leaflet"] = await self.evaluate(
            "!!document.querySelector('.leaflet-container')"
        ) or False
        info["has_recharts"] = await self.evaluate(
            "!!document.querySelector('.recharts-wrapper, .recharts-responsive-container')"
        ) or False
        info["stat_cards"] = await self.evaluate(
            "document.querySelectorAll('[data-testid=\"stat-card\"]').length"
        ) or 0

        # Scroll/overflow
        info["scroll_w"] = await self.evaluate("document.documentElement.scrollWidth") or 0
        info["client_w"] = await self.evaluate("document.documentElement.clientWidth") or 0
        info["overflow"] = (info["scroll_w"] > info["client_w"] + 5) if isinstance(info["scroll_w"], (int, float)) and isinstance(info["client_w"], (int, float)) else False

        # Accessibility
        info["skip_link"] = await self.evaluate(
            "!!document.querySelector('.skip-link, a[href=\"#main-content\"]')"
        ) or False
        info["aria_labels"] = await self.evaluate(
            "document.querySelectorAll('[aria-label]').length"
        ) or 0
        info["form_labels"] = await self.evaluate(
            "document.querySelectorAll('label').length"
        ) or 0

        # Images
        info["images"] = await self.evaluate(
            "document.querySelectorAll('img').length"
        ) or 0
        info["broken_images"] = await self.evaluate("""
            (() => {
                const imgs = document.querySelectorAll('img');
                let broken = 0;
                imgs.forEach(img => { if (!img.complete || img.naturalWidth === 0) broken++; });
                return broken;
            })()
        """) or 0

        return info

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


def print_info(info, indent="    "):
    """Pretty print page info."""
    text_preview = (info.get("body_text_preview") or "")[:150].replace("\n", " | ")
    print(f"{indent}URL: {info.get('url', '?')}")
    print(f"{indent}Title: {info.get('title', '?')}")
    print(f"{indent}Body text: {info.get('body_text_len', 0)} chars")
    print(f"{indent}Text preview: \"{text_preview}\"")
    print(f"{indent}MUI components: total={info.get('mui_total',0)}, buttons={info.get('mui_buttons',0)}, "
          f"textfields={info.get('mui_textfields',0)}, cards={info.get('mui_cards',0)}, "
          f"typography={info.get('mui_typography',0)}, spinners={info.get('mui_circular_progress',0)}")
    print(f"{indent}Layout: sidebar={info.get('has_sidebar',False)}, nav_links={info.get('has_nav_links',0)}, "
          f"tables={info.get('has_tables',0)}, map={info.get('has_leaflet',False)}, "
          f"charts={info.get('has_recharts',False)}, stat_cards={info.get('stat_cards',0)}")
    print(f"{indent}Dimensions: scroll={info.get('scroll_w','?')}px, client={info.get('client_w','?')}px, "
          f"overflow={info.get('overflow',False)}")
    print(f"{indent}A11y: skip_link={info.get('skip_link',False)}, aria_labels={info.get('aria_labels',0)}, "
          f"form_labels={info.get('form_labels',0)}")
    if info.get("broken_images"):
        print(f"{indent}WARN: {info['broken_images']} broken image(s)")


async def main():
    print("=" * 72)
    print("PashuRaksha Admin Dashboard - Deep CDP UI Test")
    print("=" * 72)
    print(f"Target: {BASE_URL}  |  CDP: http://{CDP_HOST}:{CDP_PORT}")
    print(f"Screenshots: {SCREENSHOT_DIR}\n")

    cdp = CDPClient()
    results = []

    try:
        print("[SETUP] Connecting to Chrome CDP...")
        await cdp.connect()
        await cdp.enable_domains()
        print("  Connected.\n")

        # ======================================================================
        # PHASE 1: Login page (renders without API)
        # ======================================================================
        print("=" * 72)
        print("PHASE 1: Login Page (public, no auth required)")
        print("=" * 72)

        viewports = [
            (1920, 1080, "desktop-1920"),
            (1366, 768, "laptop-1366"),
            (768, 1024, "tablet-768"),
            (375, 667, "mobile-375"),
        ]

        for vw, vh, vlabel in viewports:
            print(f"\n  --- /login @ {vlabel} ({vw}x{vh}) ---")
            await cdp.set_viewport(vw, vh)
            await cdp.navigate(f"{BASE_URL}/login", wait_seconds=3)
            info = await cdp.get_dom_snapshot()
            ss = await cdp.screenshot(f"login_{vlabel}.png")
            print_info(info)

            issues = []
            if (info.get("body_text_len") or 0) < 20:
                issues.append("CRITICAL: Page appears blank")
            if (info.get("mui_buttons") or 0) < 1:
                issues.append("WARN: No MUI buttons found")
            if (info.get("mui_textfields") or 0) < 1:
                issues.append("WARN: No text fields found")
            if not info.get("skip_link"):
                issues.append("WARN: No skip-to-content link")
            if info.get("overflow"):
                issues.append(f"WARN: Horizontal overflow at {vlabel}")

            js_errs = [e for e in cdp.js_exceptions
                       if "unsafe-eval" not in e and "Content Security Policy" not in e]
            if js_errs:
                issues.append(f"JS ERRORS: {'; '.join(js_errs[:3])}")

            # CSP error is known Next.js dev mode issue
            csp_errs = [e for e in cdp.js_exceptions if "unsafe-eval" in e or "Content Security Policy" in e]

            status = "FAIL" if any("CRITICAL" in i for i in issues) else ("WARN" if issues else "PASS")
            print(f"    STATUS: {status}")
            if issues:
                for i in issues:
                    print(f"    -> {i}")
            if csp_errs:
                print(f"    (Known: {len(csp_errs)} CSP eval errors from Next.js dev mode)")
            results.append({"page": "/login", "viewport": vlabel, "status": status, "issues": issues})

        # ======================================================================
        # PHASE 2: Login page interaction test
        # ======================================================================
        print("\n" + "=" * 72)
        print("PHASE 2: Login Page Interaction Tests")
        print("=" * 72)

        await cdp.set_viewport(1920, 1080)
        await cdp.navigate(f"{BASE_URL}/login", wait_seconds=3)

        # Test 2a: Phone field input
        print("\n  --- Test: Phone input field ---")
        phone_filled = await cdp.evaluate("""
            (() => {
                const inputs = document.querySelectorAll('input');
                for (const input of inputs) {
                    if (input.placeholder?.includes('9876') || input.type === 'tel' || input.inputMode === 'numeric') {
                        // React controlled input - set nativeInputValueSetter
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'value'
                        ).set;
                        nativeInputValueSetter.call(input, '9876543210');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        return input.value;
                    }
                }
                return 'NOT_FOUND';
            })()
        """)
        print(f"    Phone input value after fill: '{phone_filled}'")

        # Test 2b: Button state
        print("\n  --- Test: Send OTP button state ---")
        btn_info = await cdp.evaluate("""
            (() => {
                const btns = document.querySelectorAll('button');
                const results = [];
                for (const btn of btns) {
                    if (btn.innerText?.includes('Send OTP') || btn.innerText?.includes('OTP')) {
                        results.push({
                            text: btn.innerText,
                            disabled: btn.disabled,
                            visible: btn.offsetParent !== null,
                            classes: btn.className?.substring(0, 100),
                        });
                    }
                }
                return results;
            })()
        """)
        if btn_info:
            for b in btn_info:
                print(f"    Button: '{b.get('text','')}' disabled={b.get('disabled')} visible={b.get('visible')}")
        else:
            print("    No Send OTP button found")

        # Test 2c: Form validation - invalid phone
        print("\n  --- Test: Invalid phone validation ---")
        await cdp.evaluate("""
            (() => {
                const inputs = document.querySelectorAll('input');
                for (const input of inputs) {
                    if (input.placeholder?.includes('9876') || input.inputMode === 'numeric') {
                        const setter = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'value'
                        ).set;
                        setter.call(input, '1234567890');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    }
                }
                return false;
            })()
        """)
        await asyncio.sleep(0.5)
        helper_text = await cdp.evaluate("""
            (() => {
                const helpers = document.querySelectorAll('[class*="MuiFormHelperText"], .MuiFormHelperText-root');
                return Array.from(helpers).map(h => h.innerText).filter(t => t.trim());
            })()
        """)
        print(f"    Helper text after invalid phone: {helper_text}")
        await cdp.screenshot("login_invalid_phone.png")

        # Test 2d: Keyboard navigation
        print("\n  --- Test: Tab order / keyboard accessibility ---")
        focus_order = await cdp.evaluate("""
            (() => {
                const focusable = document.querySelectorAll(
                    'input:not([disabled]), button:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
                );
                return Array.from(focusable).map(el => ({
                    tag: el.tagName,
                    type: el.type || '',
                    text: el.innerText?.substring(0, 30) || el.placeholder || el.getAttribute('aria-label') || '',
                    tabIndex: el.tabIndex,
                }));
            })()
        """)
        if focus_order:
            print(f"    Focusable elements: {len(focus_order)}")
            for i, el in enumerate(focus_order[:10]):
                print(f"      [{i}] <{el['tag'].lower()}> type={el.get('type','')} text=\"{el.get('text','')}\" tabIndex={el.get('tabIndex','')}")

        results.append({"page": "/login", "viewport": "interaction", "status": "INFO"})

        # ======================================================================
        # PHASE 3: Protected pages with auth bypass
        # ======================================================================
        print("\n" + "=" * 72)
        print("PHASE 3: Protected Pages (auth bypass via JS injection)")
        print("=" * 72)

        # Strategy: Override the authProvider.check method before the page loads
        # We'll navigate to the page and immediately inject the bypass
        protected_pages = [
            ("/", "dashboard"),
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
            ("/vet/cases", "vet-cases"),
            ("/vet/alerts", "vet-alerts"),
            ("/vet", "vet-dashboard"),
        ]

        # First, try to set a cookie or localStorage token to bypass auth
        # The auth provider checks GET /auth/me -- we can intercept with Fetch domain
        print("\n  Enabling request interception to mock /auth/me...")
        await cdp.send("Fetch.enable", {
            "patterns": [
                {"urlPattern": "*/auth/me*", "requestStage": "Request"},
                {"urlPattern": "*/v1/*", "requestStage": "Request"},
            ]
        })

        # Set up interception handler
        original_listen = cdp._listener_task
        intercept_count = 0

        async def handle_intercepted():
            nonlocal intercept_count
            try:
                async for msg in cdp.ws:
                    data = json.loads(msg)
                    if "id" in data:
                        mid = data["id"]
                        if mid in cdp._pending:
                            cdp._pending[mid].set_result(data)
                    elif data.get("method") == "Fetch.requestPaused":
                        params = data["params"]
                        request_id = params["requestId"]
                        url = params["request"]["url"]

                        if "/auth/me" in url:
                            # Return mock auth response
                            mock_body = json.dumps({
                                "user_id": "test-admin-001",
                                "name": "Test Admin",
                                "role": "admin",
                                "phone": "+919876543210",
                            })
                            body_b64 = base64.b64encode(mock_body.encode()).decode()
                            await cdp.send("Fetch.fulfillRequest", {
                                "requestId": request_id,
                                "responseCode": 200,
                                "responseHeaders": [
                                    {"name": "Content-Type", "value": "application/json"},
                                ],
                                "body": body_b64,
                            })
                            intercept_count += 1
                        elif "/v1/" in url:
                            # Return empty data for list endpoints
                            mock_body = json.dumps({"data": [], "total": 0})
                            body_b64 = base64.b64encode(mock_body.encode()).decode()
                            await cdp.send("Fetch.fulfillRequest", {
                                "requestId": request_id,
                                "responseCode": 200,
                                "responseHeaders": [
                                    {"name": "Content-Type", "value": "application/json"},
                                ],
                                "body": body_b64,
                            })
                            intercept_count += 1
                        else:
                            await cdp.send("Fetch.continueRequest", {"requestId": request_id})
                    elif data.get("method") == "Runtime.consoleAPICalled":
                        params = data.get("params", {})
                        if params.get("type") == "error":
                            args = params.get("args", [])
                            text = " ".join(
                                a.get("value", a.get("description", "")) for a in args
                            )
                            if text.strip():
                                cdp.console_errors.append(text[:200])
                    elif data.get("method") == "Runtime.exceptionThrown":
                        ex = data["params"].get("exceptionDetails", {})
                        text = ex.get("text", "")
                        exc = ex.get("exception", {})
                        desc = exc.get("description", exc.get("value", ""))
                        cdp.js_exceptions.append(f"{text}: {desc}"[:200])
            except (websockets.exceptions.ConnectionClosed, asyncio.CancelledError):
                pass

        # Replace the listener with our interception-aware one
        if cdp._listener_task:
            cdp._listener_task.cancel()
            try:
                await cdp._listener_task
            except asyncio.CancelledError:
                pass
        cdp._listener_task = asyncio.create_task(handle_intercepted())

        await cdp.set_viewport(1920, 1080)

        for path, name in protected_pages:
            print(f"\n  --- {path} ({name}) ---")
            cdp.console_errors.clear()
            cdp.js_exceptions.clear()
            intercept_count = 0

            await cdp.send("Page.navigate", {"url": f"{BASE_URL}{path}"})
            # Wait for page load + auth check + render
            await asyncio.sleep(5)

            # Extra wait for dynamic content
            ready = await cdp.evaluate("document.readyState")
            pathname = await cdp.evaluate("window.location.pathname")
            print(f"    Landed on: {pathname} (readyState: {ready}, intercepted: {intercept_count})")

            info = await cdp.get_dom_snapshot()
            ss = await cdp.screenshot(f"{name}_authed_desktop.png")
            print_info(info)

            issues = []
            body_len = info.get("body_text_len") or 0

            # If we got redirected to login, auth bypass didn't work
            if pathname == "/login" or (info.get("pathname") or "").startswith("/login"):
                issues.append("INFO: Redirected to /login (auth bypass didn't take effect)")
            elif body_len < 30:
                issues.append("WARN: Very little content rendered")

            if not info.get("has_sidebar") and pathname != "/login":
                if body_len > 50:  # only flag if page actually loaded
                    issues.append("CHECK: Sidebar not detected (may use different selectors)")

            if info.get("overflow"):
                issues.append(f"WARN: Horizontal overflow")

            # Filter CSP errors
            real_js_errs = [e for e in cdp.js_exceptions
                          if "unsafe-eval" not in e and "Content Security Policy" not in e]
            if real_js_errs:
                issues.append(f"JS ERRORS: {'; '.join(real_js_errs[:2])}")

            csp_count = len([e for e in cdp.js_exceptions if "Content Security Policy" in e])

            status = "FAIL" if any("CRITICAL" in i for i in issues) else (
                "INFO" if any("INFO" in i for i in issues) else (
                    "WARN" if issues else "PASS"
                )
            )
            print(f"    STATUS: {status}")
            if issues:
                for i in issues:
                    print(f"    -> {i}")
            if csp_count:
                print(f"    (Known: {csp_count} CSP eval errors)")

            results.append({
                "page": path, "viewport": "desktop-1920-authed",
                "status": status, "issues": issues,
                "intercepted_requests": intercept_count,
            })

        # Disable fetch interception
        await cdp.send("Fetch.disable")

        # ======================================================================
        # PHASE 4: Responsive test on key authenticated pages
        # ======================================================================
        print("\n" + "=" * 72)
        print("PHASE 4: Responsive Tests on Authenticated Pages")
        print("=" * 72)

        # Re-enable interception
        await cdp.send("Fetch.enable", {
            "patterns": [
                {"urlPattern": "*/auth/me*", "requestStage": "Request"},
                {"urlPattern": "*/v1/*", "requestStage": "Request"},
            ]
        })

        responsive_pages = [("/", "dashboard"), ("/farmers", "farmers"), ("/map", "map")]
        responsive_viewports = [
            (1366, 768, "laptop-1366"),
            (768, 1024, "tablet-768"),
            (375, 667, "mobile-375"),
        ]

        for vw, vh, vlabel in responsive_viewports:
            for path, name in responsive_pages:
                print(f"\n  --- {path} @ {vlabel} ---")
                await cdp.set_viewport(vw, vh)
                cdp.console_errors.clear()
                cdp.js_exceptions.clear()

                await cdp.send("Page.navigate", {"url": f"{BASE_URL}{path}"})
                await asyncio.sleep(5)

                info = await cdp.get_dom_snapshot()
                await cdp.screenshot(f"{name}_authed_{vlabel}.png")

                pathname = info.get("pathname", "?")
                print(f"    Landed: {pathname}, body={info.get('body_text_len',0)} chars, "
                      f"scroll={info.get('scroll_w','?')}, client={info.get('client_w','?')}, "
                      f"overflow={info.get('overflow',False)}")

                issues = []
                if info.get("overflow"):
                    issues.append(f"WARN: Horizontal overflow at {vlabel}")
                status = "WARN" if issues else "PASS"
                print(f"    STATUS: {status}")
                results.append({
                    "page": path, "viewport": vlabel,
                    "status": status, "issues": issues,
                })

        await cdp.send("Fetch.disable")

        # ======================================================================
        # PHASE 5: CSP and Next.js config analysis
        # ======================================================================
        print("\n" + "=" * 72)
        print("PHASE 5: Configuration Issues Analysis")
        print("=" * 72)

        # Check next.config.js for CSP
        print("\n  CSP 'unsafe-eval' Error Analysis:")
        print("    Every page throws: EvalError from @next/react-refresh-utils")
        print("    This is a Next.js dev mode issue -- react-refresh needs eval()")
        print("    The CSP header in next.config.js sets script-src 'self' without 'unsafe-eval'")
        print("    IMPACT: Dev mode only. Production builds don't use react-refresh.")
        print("    FIX: Add 'unsafe-eval' to CSP in dev mode, or remove CSP in dev config.")

        # ======================================================================
        # SUMMARY
        # ======================================================================
        print("\n" + "=" * 72)
        print("SUMMARY")
        print("=" * 72)

        total = len(results)
        by_status = {}
        for r in results:
            s = r["status"]
            by_status[s] = by_status.get(s, 0) + 1

        print(f"Total test points: {total}")
        for s, c in sorted(by_status.items()):
            print(f"  {s}: {c}")

        ss_count = len(list(SCREENSHOT_DIR.glob("*.png")))
        print(f"\nScreenshots saved: {ss_count} in {SCREENSHOT_DIR}")

        # Write JSON report
        report_path = SCREENSHOT_DIR / "deep-test-report.json"
        report_path.write_text(json.dumps({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "results": results,
            "summary": by_status,
        }, indent=2, default=str))
        print(f"JSON report: {report_path}")

    except Exception as e:
        print(f"\nFATAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await cdp.close()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
