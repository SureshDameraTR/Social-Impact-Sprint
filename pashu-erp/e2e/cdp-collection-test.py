#!/usr/bin/env python3
"""
CDP-based UI testing for PashuRaksha Collection Centre (port 3001).
Connects to Chrome DevTools Protocol at 127.0.0.1:9222.
Tests each page for rendering, JS errors, layout, and responsiveness.

NOTE: Backend API (port 8000) is expected to be DOWN. Tests distinguish
between "broken UI" and "missing data because API is down".
"""

import asyncio
import json
import base64
import time
import sys
import os
from pathlib import Path

try:
    import websockets
except ImportError:
    print("ERROR: pip install websockets")
    sys.exit(1)

CDP_HOST = "127.0.0.1"
CDP_PORT = 9222
BASE_URL = "http://localhost:3001"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots" / "collection"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Pages to test
# Note: all routes except /login are protected by AuthGuard.
# With API down, useAuth will fail => user=null => redirect to /login.
# We test /login directly (renders without auth) and also test
# protected routes to verify they redirect gracefully.
PAGES = [
    ("/login", "login"),
    ("/intake", "intake"),
    ("/dashboard", "dashboard"),
    ("/settlements", "settlements"),
    ("/enroll", "enroll"),
    ("/intake/receipt/test-123", "receipt"),
]

VIEWPORTS = [
    (1920, 1080, "desktop-1920"),
    (1366, 768, "laptop-1366"),
    (768, 1024, "tablet-768"),
    (375, 667, "mobile-375"),
]

# Known API-down error patterns that should NOT be counted as UI bugs
API_DOWN_PATTERNS = [
    "network", "fetch", "ECONNREFUSED", "ERR_CONNECTION_REFUSED",
    "axios", "AxiosError", "request failed", "status code",
    "Failed to load", "net::", "proxy", "/v1/",
]


def is_api_error(error_text):
    """Check if an error is caused by the backend being down."""
    lower = error_text.lower()
    return any(pat.lower() in lower for pat in API_DOWN_PATTERNS)


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
        """Connect to Chrome CDP, creating a new tab for testing."""
        import urllib.request
        req = urllib.request.Request(
            f"http://{CDP_HOST}:{CDP_PORT}/json/new?about:blank",
            method="PUT"
        )
        resp = urllib.request.urlopen(req)
        tab_info = json.loads(resp.read())
        ws_url = tab_info["webSocketDebuggerUrl"]
        self.tab_id = tab_info["id"]
        print(f"  Created new tab: {self.tab_id}")
        self.ws = await websockets.connect(ws_url, max_size=50 * 1024 * 1024)
        self._listener_task = asyncio.create_task(self._listen())

    async def _listen(self):
        """Background listener for CDP messages."""
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
                                a.get("value", a.get("description", ""))
                                for a in args
                            )
                            self.console_errors.append(text)
                    elif method == "Runtime.exceptionThrown":
                        ex = data["params"].get("exceptionDetails", {})
                        text = ex.get("text", "")
                        exc = ex.get("exception", {})
                        desc = exc.get("description", exc.get("value", ""))
                        self.js_exceptions.append(f"{text}: {desc}")
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
        await self.send("Console.enable")
        await self.send("DOM.enable")
        await self.send("Network.enable")

    async def navigate(self, url):
        """Navigate and wait for load."""
        self.console_errors.clear()
        self.js_exceptions.clear()
        await self.send("Page.navigate", {"url": url})
        await asyncio.sleep(0.5)
        for _ in range(40):
            try:
                state = await self.send("Runtime.evaluate", {
                    "expression": "document.readyState",
                    "returnByValue": True
                })
                if state.get("result", {}).get("value") == "complete":
                    break
            except Exception:
                pass
            await asyncio.sleep(0.5)
        # Extra wait for React hydration + auth check + redirect
        await asyncio.sleep(2)

    async def screenshot(self, filename):
        result = await self.send("Page.captureScreenshot", {"format": "png"})
        data = base64.b64decode(result["data"])
        path = SCREENSHOT_DIR / filename
        path.write_bytes(data)
        return str(path)

    async def set_viewport(self, width, height):
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": width < 768,
        })

    async def evaluate(self, expression):
        result = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        })
        if "exceptionDetails" in result:
            return {"error": result["exceptionDetails"].get("text", "eval error")}
        return result.get("result", {}).get("value")

    async def get_page_info(self):
        """Gather comprehensive page state info."""
        info = {}

        info["title"] = await self.evaluate("document.title")
        info["current_url"] = await self.evaluate("window.location.href")
        info["pathname"] = await self.evaluate("window.location.pathname")
        info["body_text_length"] = await self.evaluate(
            "document.body?.innerText?.length || 0"
        )

        # React root check
        info["has_react_root"] = await self.evaluate(
            "!!document.getElementById('root')?.children?.length"
        )

        # MUI components
        info["mui_components"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"Mui\"]').length"
        )

        # AppBar / header
        info["has_header"] = await self.evaluate(
            "!!document.querySelector('[class*=\"MuiAppBar\"], header, [class*=\"MuiToolbar\"]')"
        )

        # Tabs (NavBar tabs)
        info["tab_count"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"MuiTab-root\"]').length"
        )

        # Cards
        info["card_count"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"MuiCard-root\"]').length"
        )

        # Text fields / inputs
        info["input_count"] = await self.evaluate(
            "document.querySelectorAll('input, [class*=\"MuiTextField\"]').length"
        )

        # Buttons
        info["button_count"] = await self.evaluate(
            "document.querySelectorAll('button, [class*=\"MuiButton-root\"]').length"
        )

        # Tables
        info["table_count"] = await self.evaluate(
            "document.querySelectorAll('table, [class*=\"MuiTable\"]').length"
        )

        # Alert components (MUI Alert)
        info["alert_count"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"MuiAlert-root\"]').length"
        )

        # Skeleton loaders
        info["skeleton_count"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"MuiSkeleton\"]').length"
        )

        # Loading spinner
        info["has_spinner"] = await self.evaluate(
            "!!document.querySelector('[class*=\"MuiCircularProgress\"]')"
        )

        # Check for error states
        info["visible_errors"] = await self.evaluate("""
            (() => {
                const els = document.querySelectorAll('[class*=\"MuiAlert-standardError\"]');
                const texts = [];
                els.forEach(el => {
                    if (el.offsetParent !== null && el.innerText)
                        texts.push(el.innerText.substring(0, 200));
                });
                return texts.slice(0, 5);
            })()
        """)

        # Check for warning states
        info["visible_warnings"] = await self.evaluate("""
            (() => {
                const els = document.querySelectorAll('[class*=\"MuiAlert-standardWarning\"]');
                const texts = [];
                els.forEach(el => {
                    if (el.offsetParent !== null && el.innerText)
                        texts.push(el.innerText.substring(0, 200));
                });
                return texts.slice(0, 5);
            })()
        """)

        # 404 check
        info["has_404"] = await self.evaluate(
            "!!document.body?.innerText?.match(/404|not found/i)"
        )

        # Horizontal overflow
        info["scroll_width"] = await self.evaluate(
            "document.documentElement.scrollWidth"
        )
        info["client_width"] = await self.evaluate(
            "document.documentElement.clientWidth"
        )
        info["has_horizontal_overflow"] = await self.evaluate(
            "document.documentElement.scrollWidth > document.documentElement.clientWidth + 5"
        )

        # PWA: service worker registration
        info["has_service_worker"] = await self.evaluate(
            "'serviceWorker' in navigator"
        )

        # PWA: manifest link
        info["has_manifest_link"] = await self.evaluate(
            "!!document.querySelector('link[rel=\"manifest\"]')"
        )

        # Body text snippet (first 300 chars for debugging)
        info["body_text_preview"] = await self.evaluate(
            "document.body?.innerText?.substring(0, 300) || ''"
        )

        return info

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
        if self.ws:
            await self.ws.close()
        if self.tab_id:
            try:
                import urllib.request
                urllib.request.urlopen(
                    f"http://{CDP_HOST}:{CDP_PORT}/json/close/{self.tab_id}"
                )
            except Exception:
                pass


async def test_page(cdp, path, name, viewport_width=1920, viewport_height=1080,
                    viewport_label="desktop-1920"):
    """Test a single page at a given viewport."""
    result = {
        "page": path,
        "name": name,
        "viewport": viewport_label,
        "status": "UNKNOWN",
        "issues": [],
        "info": {},
        "screenshot": None,
        "js_errors": [],
        "console_errors": [],
        "api_errors": [],
    }

    try:
        await cdp.set_viewport(viewport_width, viewport_height)
        await cdp.navigate(f"{BASE_URL}{path}")

        info = await cdp.get_page_info()
        result["info"] = info

        # Separate API errors from real JS errors
        all_js_errors = list(cdp.js_exceptions)
        real_js_errors = [e for e in all_js_errors if not is_api_error(e)]
        api_js_errors = [e for e in all_js_errors if is_api_error(e)]

        all_console_errors = list(cdp.console_errors)
        real_console_errors = [e for e in all_console_errors if not is_api_error(e)]
        api_console_errors = [e for e in all_console_errors if is_api_error(e)]

        result["js_errors"] = real_js_errors
        result["console_errors"] = real_console_errors
        result["api_errors"] = api_js_errors + api_console_errors

        # Screenshot
        ss_name = f"{name}_{viewport_label}.png"
        await cdp.screenshot(ss_name)
        result["screenshot"] = ss_name

        issues = []

        # White screen check
        body_len = info.get("body_text_length", 0)
        if isinstance(body_len, (int, float)) and body_len < 5:
            issues.append("CRITICAL: Page appears blank (body text < 5 chars)")

        # React root check
        if not info.get("has_react_root"):
            issues.append("CRITICAL: React root has no children (app crashed)")

        # 404 check
        if info.get("has_404"):
            issues.append("CRITICAL: Page shows 404")

        # Real JS exceptions (not API-related)
        if real_js_errors:
            issues.append(
                f"JS EXCEPTIONS ({len(real_js_errors)}): "
                f"{'; '.join(e[:120] for e in real_js_errors[:3])}"
            )

        # Auth redirect check for protected routes
        actual_path = info.get("pathname", "")
        if path != "/login" and actual_path == "/login":
            # Expected when API is down
            issues.append(
                "INFO: Redirected to /login (expected with API down)"
            )

        # MUI rendering check
        mui_count = info.get("mui_components", 0)
        if isinstance(mui_count, (int, float)) and mui_count < 2:
            issues.append("WARN: Very few MUI components rendered (<2)")

        # Horizontal overflow
        if info.get("has_horizontal_overflow"):
            issues.append(
                f"WARN: Horizontal overflow at {viewport_label} "
                f"({info.get('scroll_width')}px > {info.get('client_width')}px)"
            )

        result["issues"] = issues
        has_critical = any("CRITICAL" in i for i in issues)
        has_warn = any("WARN" in i for i in issues)
        result["status"] = (
            "FAIL" if has_critical
            else "WARN" if has_warn
            else "PASS"
        )

    except Exception as e:
        result["status"] = "ERROR"
        result["issues"] = [f"Test error: {str(e)}"]

    return result


async def test_login_form_validation(cdp):
    """Test the login form UI interactions."""
    results = []
    await cdp.set_viewport(1920, 1080)
    await cdp.navigate(f"{BASE_URL}/login")

    # Test 1: Login page renders with expected elements
    info = await cdp.get_page_info()
    r = {"test": "login_renders", "status": "PASS", "details": ""}
    if info.get("card_count", 0) < 1:
        r["status"] = "FAIL"
        r["details"] = "No Card component found on login page"
    elif info.get("input_count", 0) < 1:
        r["status"] = "FAIL"
        r["details"] = "No input field found on login page"
    elif info.get("button_count", 0) < 1:
        r["status"] = "FAIL"
        r["details"] = "No button found on login page"
    else:
        r["details"] = (
            f"cards={info.get('card_count')}, "
            f"inputs={info.get('input_count')}, "
            f"buttons={info.get('button_count')}, "
            f"mui={info.get('mui_components')}"
        )
    results.append(r)

    # Test 2: Branding text present
    has_branding = await cdp.evaluate(
        "!!document.body.innerText.match(/PashuRaksha/i)"
    )
    has_cc_label = await cdp.evaluate(
        "!!document.body.innerText.match(/Collection Centre/i)"
    )
    r = {"test": "login_branding", "status": "PASS", "details": ""}
    if not has_branding:
        r["status"] = "FAIL"
        r["details"] = "PashuRaksha branding not found"
    elif not has_cc_label:
        r["status"] = "WARN"
        r["details"] = "Collection Centre label not found"
    else:
        r["details"] = "PashuRaksha + Collection Centre branding present"
    results.append(r)

    # Test 3: Phone input has +91 prefix
    has_prefix = await cdp.evaluate(
        "!!document.body.innerText.match(/\\+91/)"
    )
    r = {"test": "login_phone_prefix", "status": "PASS" if has_prefix else "FAIL",
         "details": "+91 prefix present" if has_prefix else "+91 prefix not found"}
    results.append(r)

    # Test 4: Send OTP button present and initially disabled
    btn_disabled = await cdp.evaluate("""
        (() => {
            const btns = document.querySelectorAll('button');
            for (const b of btns) {
                if (b.innerText.match(/Send OTP/i)) {
                    return b.disabled;
                }
            }
            return null;
        })()
    """)
    r = {"test": "login_send_otp_btn", "status": "UNKNOWN", "details": ""}
    if btn_disabled is None:
        r["status"] = "FAIL"
        r["details"] = "Send OTP button not found"
    elif btn_disabled:
        r["status"] = "PASS"
        r["details"] = "Send OTP button is disabled when phone is empty"
    else:
        r["status"] = "WARN"
        r["details"] = "Send OTP button is enabled even when phone is empty"
    results.append(r)

    # Test 5: Type valid phone and check button enables
    await cdp.evaluate("""
        (() => {
            const input = document.querySelector('input');
            if (input) {
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                nativeInputValueSetter.call(input, '9876543210');
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        })()
    """)
    await asyncio.sleep(0.5)
    btn_disabled_after = await cdp.evaluate("""
        (() => {
            const btns = document.querySelectorAll('button');
            for (const b of btns) {
                if (b.innerText.match(/Send OTP/i)) return b.disabled;
            }
            return null;
        })()
    """)
    r = {"test": "login_phone_enables_btn", "status": "UNKNOWN", "details": ""}
    if btn_disabled_after is False:
        r["status"] = "PASS"
        r["details"] = "Send OTP button enabled after valid phone entry"
    elif btn_disabled_after is True:
        r["status"] = "WARN"
        r["details"] = (
            "Button still disabled after phone entry "
            "(may be React controlled input issue with CDP)"
        )
    else:
        r["status"] = "FAIL"
        r["details"] = "Could not find Send OTP button after phone entry"
    results.append(r)

    # Test 6: Staff Login text
    has_staff_login = await cdp.evaluate(
        "!!document.body.innerText.match(/Staff Login/i)"
    )
    r = {"test": "login_staff_label", "status": "PASS" if has_staff_login else "WARN",
         "details": "Staff Login label present" if has_staff_login else "Staff Login label not found"}
    results.append(r)

    return results


async def test_pwa_features(cdp):
    """Test PWA-related features."""
    results = []
    await cdp.set_viewport(1920, 1080)
    await cdp.navigate(f"{BASE_URL}/login")

    # Test 1: Service worker API available
    sw_available = await cdp.evaluate("'serviceWorker' in navigator")
    results.append({
        "test": "pwa_sw_api",
        "status": "PASS" if sw_available else "FAIL",
        "details": "ServiceWorker API available" if sw_available else "ServiceWorker API not in navigator",
    })

    # Test 2: Manifest link in HTML
    manifest_href = await cdp.evaluate("""
        (() => {
            const link = document.querySelector('link[rel="manifest"]');
            return link ? link.getAttribute('href') : null;
        })()
    """)
    results.append({
        "test": "pwa_manifest_link",
        "status": "PASS" if manifest_href else "WARN",
        "details": f"Manifest at {manifest_href}" if manifest_href else "No manifest link found in HTML",
    })

    # Test 3: Meta viewport tag
    has_viewport = await cdp.evaluate(
        "!!document.querySelector('meta[name=\"viewport\"]')"
    )
    results.append({
        "test": "pwa_viewport_meta",
        "status": "PASS" if has_viewport else "FAIL",
        "details": "Viewport meta tag present" if has_viewport else "Missing viewport meta tag",
    })

    # Test 4: Theme color meta
    theme_color = await cdp.evaluate("""
        (() => {
            const meta = document.querySelector('meta[name="theme-color"]');
            return meta ? meta.getAttribute('content') : null;
        })()
    """)
    results.append({
        "test": "pwa_theme_color",
        "status": "PASS" if theme_color else "INFO",
        "details": f"Theme color: {theme_color}" if theme_color else "No theme-color meta tag",
    })

    # Test 5: Check if manifest.json is fetchable
    manifest_ok = await cdp.evaluate("""
        (async () => {
            try {
                const resp = await fetch('/manifest.json');
                if (!resp.ok) return 'fetch_failed: ' + resp.status;
                const data = await resp.json();
                return 'ok: ' + (data.name || data.short_name || 'unnamed');
            } catch (e) {
                return 'error: ' + e.message;
            }
        })()
    """)
    is_ok = isinstance(manifest_ok, str) and manifest_ok.startswith("ok:")
    results.append({
        "test": "pwa_manifest_fetch",
        "status": "PASS" if is_ok else "WARN",
        "details": str(manifest_ok),
    })

    return results


async def test_responsive_login(cdp):
    """Test login page at multiple viewport sizes."""
    results = []
    for vw, vh, vlabel in VIEWPORTS:
        await cdp.set_viewport(vw, vh)
        await cdp.navigate(f"{BASE_URL}/login")

        info = await cdp.get_page_info()
        ss_name = f"login_{vlabel}.png"
        await cdp.screenshot(ss_name)

        issues = []

        body_len = info.get("body_text_length", 0)
        if isinstance(body_len, (int, float)) and body_len < 5:
            issues.append("Page blank")

        if info.get("has_horizontal_overflow"):
            issues.append(
                f"Horizontal overflow ({info.get('scroll_width')}px > "
                f"{info.get('client_width')}px)"
            )

        mui = info.get("mui_components", 0)
        if isinstance(mui, (int, float)) and mui < 2:
            issues.append(f"Few MUI components ({mui})")

        status = "FAIL" if "Page blank" in str(issues) else (
            "WARN" if issues else "PASS"
        )
        results.append({
            "viewport": vlabel,
            "width": vw,
            "height": vh,
            "status": status,
            "issues": issues,
            "screenshot": ss_name,
            "mui_count": mui,
            "card_count": info.get("card_count", 0),
            "body_text_len": body_len,
        })

    return results


async def main():
    print("=" * 70)
    print("PashuRaksha Collection Centre - CDP UI Test")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"CDP: http://{CDP_HOST}:{CDP_PORT}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print(f"API status: DOWN (expected)")
    print()

    cdp = CDPClient()
    try:
        print("[1/5] Connecting to Chrome CDP...")
        await cdp.connect()
        await cdp.enable_domains()
        print("  Connected successfully.\n")

        # ---- Phase 1: Page load tests at desktop ----
        print("[2/5] Testing all pages at desktop viewport (1920x1080)...")
        print("-" * 70)
        all_results = []
        for path, name in PAGES:
            result = await test_page(cdp, path, name, 1920, 1080, "desktop-1920")
            icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX", "ERROR": "??"}.get(
                result["status"], "??"
            )
            info = result["info"]
            extras = []
            if info.get("card_count"):
                extras.append(f"cards={info['card_count']}")
            if info.get("input_count"):
                extras.append(f"inputs={info['input_count']}")
            if info.get("button_count"):
                extras.append(f"buttons={info['button_count']}")
            if info.get("mui_components"):
                extras.append(f"mui={info['mui_components']}")
            if info.get("tab_count"):
                extras.append(f"tabs={info['tab_count']}")
            if info.get("table_count"):
                extras.append(f"tables={info['table_count']}")
            if info.get("alert_count"):
                extras.append(f"alerts={info['alert_count']}")
            if info.get("skeleton_count"):
                extras.append(f"skeletons={info['skeleton_count']}")
            actual_path = info.get("pathname", "?")
            extras_str = f" [{', '.join(extras)}]" if extras else ""
            redirect = f" -> {actual_path}" if actual_path != path else ""
            print(
                f"  [{icon}] {path:25s} {result['status']:6s}"
                f"{redirect}{extras_str}"
            )
            if result["issues"]:
                for issue in result["issues"]:
                    tag = "INFO" if "INFO:" in issue else "ISSUE"
                    print(f"       {tag}: {issue}")
            if result["api_errors"]:
                print(
                    f"       API-DOWN: {len(result['api_errors'])} errors "
                    f"(expected, backend offline)"
                )
            if result["js_errors"]:
                for err in result["js_errors"][:2]:
                    print(f"       JS-BUG: {err[:120]}")
            all_results.append(result)

        # ---- Phase 2: Login form validation ----
        print(f"\n[3/5] Login form interaction tests...")
        print("-" * 70)
        form_results = await test_login_form_validation(cdp)
        for r in form_results:
            icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX", "INFO": "ii"}.get(
                r["status"], "??"
            )
            print(f"  [{icon}] {r['test']:30s} {r['status']:6s} {r['details']}")

        # ---- Phase 3: Responsive testing ----
        print(f"\n[4/5] Responsive viewport testing (login page)...")
        print("-" * 70)
        responsive_results = await test_responsive_login(cdp)
        for r in responsive_results:
            icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX"}.get(
                r["status"], "??"
            )
            print(
                f"  [{icon}] {r['viewport']:15s} {r['status']:6s} "
                f"(mui={r['mui_count']}, cards={r['card_count']}, "
                f"text={r['body_text_len']})"
            )
            if r["issues"]:
                for issue in r["issues"]:
                    print(f"       -> {issue}")

        # ---- Phase 4: PWA features ----
        print(f"\n[5/5] PWA feature checks...")
        print("-" * 70)
        pwa_results = await test_pwa_features(cdp)
        for r in pwa_results:
            icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX", "INFO": "ii"}.get(
                r["status"], "??"
            )
            print(f"  [{icon}] {r['test']:25s} {r['status']:6s} {r['details']}")

        # ---- Summary ----
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        total = len(all_results)
        passed = sum(1 for r in all_results if r["status"] == "PASS")
        warned = sum(1 for r in all_results if r["status"] == "WARN")
        failed = sum(1 for r in all_results if r["status"] == "FAIL")
        errored = sum(1 for r in all_results if r["status"] == "ERROR")
        print(f"Page load tests: {total}")
        print(f"  PASS: {passed}  WARN: {warned}  FAIL: {failed}  ERROR: {errored}")

        form_passed = sum(1 for r in form_results if r["status"] == "PASS")
        print(f"\nForm validation tests: {len(form_results)} total, {form_passed} passed")

        resp_overflow = sum(
            1 for r in responsive_results if "Horizontal overflow" in str(r["issues"])
        )
        resp_pass = sum(1 for r in responsive_results if r["status"] == "PASS")
        print(
            f"Responsive tests: {len(responsive_results)} viewports, "
            f"{resp_pass} pass, {resp_overflow} with overflow"
        )

        pwa_pass = sum(1 for r in pwa_results if r["status"] == "PASS")
        print(f"PWA tests: {len(pwa_results)} total, {pwa_pass} passed")

        api_error_count = sum(len(r.get("api_errors", [])) for r in all_results)
        print(f"\nAPI-down errors (not UI bugs): {api_error_count}")

        ss_count = len(list(SCREENSHOT_DIR.glob("*.png")))
        print(f"Screenshots saved: {ss_count} in {SCREENSHOT_DIR}")

        # Write JSON report
        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "base_url": BASE_URL,
            "api_status": "DOWN",
            "pages": all_results,
            "form_tests": form_results,
            "responsive": responsive_results,
            "pwa": pwa_results,
            "summary": {
                "page_tests": {"total": total, "pass": passed, "warn": warned,
                               "fail": failed, "error": errored},
                "form_tests": {"total": len(form_results), "pass": form_passed},
                "responsive": {"total": len(responsive_results),
                               "pass": resp_pass, "overflow": resp_overflow},
                "pwa": {"total": len(pwa_results), "pass": pwa_pass},
                "api_down_errors": api_error_count,
            },
        }
        report_path = SCREENSHOT_DIR / "test-report.json"
        report_path.write_text(json.dumps(report, indent=2, default=str))
        print(f"JSON report: {report_path}")

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await cdp.close()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
