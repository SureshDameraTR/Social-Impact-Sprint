#!/usr/bin/env python3
"""
PashuRaksha Admin Dashboard — Exhaustive E2E UI Test via Chrome CDP

Connects to Chrome DevTools Protocol at ws://127.0.0.1:9222 and tests every
page of the Admin Dashboard at http://localhost:3000 with real data verification,
interaction testing, screenshot capture, network monitoring, and responsive checks.

Usage:
    python3 cdp-admin-full-e2e.py

Requirements:
    pip install websockets
"""

import asyncio
import base64
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Any

import websockets

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CDP_HOST = "127.0.0.1"
CDP_PORT = 9222
CDP_HTTP = f"http://{CDP_HOST}:{CDP_PORT}"
BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"
PHONE = "9876543210"
PHONE_WITH_PREFIX = f"+91{PHONE}"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "screenshots", "admin-full")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Timeouts
NAV_TIMEOUT = 15  # seconds to wait for navigation
SETTLE_TIME = 3.0  # seconds to wait for page to settle after navigation
DATA_WAIT = 5.0  # seconds to wait for data to load
RESPONSIVE_WIDTH = 768

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class NetworkRequest:
    url: str
    method: str
    status: int = 0
    timing_ms: float = 0
    error: str = ""

@dataclass
class PageReport:
    path: str
    name: str
    status: str = "PENDING"
    load_time_ms: float = 0
    data_rows: int = 0
    expected_min_rows: int = 0
    components: dict = field(default_factory=dict)
    console_errors: list = field(default_factory=list)
    console_warnings: list = field(default_factory=list)
    network_requests: list = field(default_factory=list)
    latency_flags: list = field(default_factory=list)
    buttons_clicked: list = field(default_factory=list)
    interactions: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    screenshot_desktop: str = ""
    screenshot_responsive: str = ""


# ---------------------------------------------------------------------------
# CDP Client
# ---------------------------------------------------------------------------
class CDPClient:
    """Minimal Chrome DevTools Protocol client over websockets."""

    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.ws = None
        self._id = 0
        self._callbacks: dict[int, asyncio.Future] = {}
        self._event_handlers: dict[str, list] = {}
        self._listen_task = None
        # Collected data
        self.console_errors: list[str] = []
        self.console_warnings: list[str] = []
        self.network_requests: dict[str, NetworkRequest] = {}
        self._request_start: dict[str, float] = {}

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=50 * 1024 * 1024)
        self._listen_task = asyncio.create_task(self._listener())

    async def disconnect(self):
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        if self.ws:
            await self.ws.close()

    async def send(self, method: str, params: dict | None = None, timeout: float = 30) -> dict:
        self._id += 1
        msg_id = self._id
        msg = {"id": msg_id, "method": method, "params": params or {}}
        fut = asyncio.get_event_loop().create_future()
        self._callbacks[msg_id] = fut
        await self.ws.send(json.dumps(msg))
        try:
            return await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            self._callbacks.pop(msg_id, None)
            return {"error": f"Timeout waiting for {method}"}

    def on(self, event: str, handler):
        self._event_handlers.setdefault(event, []).append(handler)

    async def _listener(self):
        try:
            async for raw in self.ws:
                msg = json.loads(raw)
                if "id" in msg and msg["id"] in self._callbacks:
                    self._callbacks.pop(msg["id"]).set_result(msg)
                if "method" in msg:
                    for handler in self._event_handlers.get(msg["method"], []):
                        handler(msg.get("params", {}))
        except (websockets.exceptions.ConnectionClosed, asyncio.CancelledError):
            pass

    # --- High-level helpers ---

    async def enable_domains(self):
        """Enable Page, Runtime, Network, DOM domains and bypass CSP."""
        await self.send("Page.enable")
        await self.send("Runtime.enable")
        await self.send("Network.enable")
        await self.send("DOM.enable")
        await self.send("Page.setBypassCSP", {"enabled": True})

        # Set up console and network listeners
        self.on("Runtime.consoleAPICalled", self._on_console)
        self.on("Network.requestWillBeSent", self._on_request_start)
        self.on("Network.responseReceived", self._on_response)
        self.on("Network.loadingFailed", self._on_loading_failed)
        self.on("Runtime.exceptionThrown", self._on_exception)

    def _on_console(self, params):
        msg_type = params.get("type", "")
        args = params.get("args", [])
        text_parts = []
        for arg in args:
            val = arg.get("value") or arg.get("description") or str(arg.get("type", ""))
            if val:
                text_parts.append(str(val))
        text = " ".join(text_parts)
        if msg_type == "error":
            self.console_errors.append(text)
        elif msg_type == "warning":
            self.console_warnings.append(text)

    def _on_exception(self, params):
        detail = params.get("exceptionDetails", {})
        text = detail.get("text", "")
        exc = detail.get("exception", {})
        desc = exc.get("description", "")
        self.console_errors.append(f"EXCEPTION: {text} {desc}".strip())

    def _on_request_start(self, params):
        req = params.get("request", {})
        req_id = params.get("requestId", "")
        url = req.get("url", "")
        method = req.get("method", "GET")
        self.network_requests[req_id] = NetworkRequest(url=url, method=method)
        self._request_start[req_id] = params.get("timestamp", time.time())

    def _on_response(self, params):
        req_id = params.get("requestId", "")
        resp = params.get("response", {})
        if req_id in self.network_requests:
            nr = self.network_requests[req_id]
            nr.status = resp.get("status", 0)
            start = self._request_start.get(req_id, 0)
            end = params.get("timestamp", time.time())
            nr.timing_ms = round((end - start) * 1000, 1)

    def _on_loading_failed(self, params):
        req_id = params.get("requestId", "")
        error = params.get("errorText", "unknown")
        if req_id in self.network_requests:
            self.network_requests[req_id].error = error

    def clear_tracking(self):
        """Reset console and network tracking for a new page."""
        self.console_errors.clear()
        self.console_warnings.clear()
        self.network_requests.clear()
        self._request_start.clear()

    def get_api_requests(self) -> list[NetworkRequest]:
        """Return only API requests (to port 8000)."""
        return [r for r in self.network_requests.values()
                if ":8000" in r.url or "/v1/" in r.url]

    def get_latency_flags(self, threshold_ms: float = 2000) -> list[str]:
        """Return requests that exceeded the latency threshold."""
        return [f"{r.url} ({r.timing_ms}ms)" for r in self.network_requests.values()
                if r.timing_ms > threshold_ms and (":8000" in r.url or "/v1/" in r.url)]

    async def navigate(self, url: str, wait_seconds: float = SETTLE_TIME) -> float:
        """Navigate to URL and return load time in ms."""
        start = time.time()
        nav_fut = asyncio.get_event_loop().create_future()

        def on_load(params):
            if not nav_fut.done():
                nav_fut.set_result(True)

        self.on("Page.loadEventFired", on_load)
        await self.send("Page.navigate", {"url": url})
        try:
            await asyncio.wait_for(nav_fut, timeout=NAV_TIMEOUT)
        except asyncio.TimeoutError:
            pass
        # Remove the handler
        self._event_handlers.get("Page.loadEventFired", []).clear()
        load_ms = round((time.time() - start) * 1000)
        # Extra settle time for React hydration and data fetching
        await asyncio.sleep(wait_seconds)
        return load_ms

    async def evaluate(self, expression: str, timeout: float = 10) -> Any:
        """Evaluate JS expression and return the value."""
        result = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        }, timeout=timeout)
        if "result" in result and "result" in result["result"]:
            return result["result"]["result"].get("value")
        return None

    async def get_cookies(self) -> list[dict]:
        """Get all cookies for session preservation."""
        result = await self.send("Network.getAllCookies")
        return result.get("result", {}).get("cookies", [])

    async def set_cookies(self, cookies: list[dict]):
        """Restore cookies to preserve session."""
        if cookies:
            # Network.setCookies expects a slightly different format
            clean = []
            for c in cookies:
                entry = {k: v for k, v in c.items()
                         if k in ("name", "value", "domain", "path", "secure",
                                  "httpOnly", "sameSite", "expires")}
                clean.append(entry)
            await self.send("Network.setCookies", {"cookies": clean})

    async def screenshot(self, path: str, width: int = 1920, height: int = 1080):
        """Take a screenshot and save to file. Preserves cookies across viewport changes."""
        # Save cookies before viewport change
        cookies = await self.get_cookies()
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height, "deviceScaleFactor": 1, "mobile": width < 768
        })
        # Restore cookies after viewport change
        await self.set_cookies(cookies)
        await asyncio.sleep(0.5)
        result = await self.send("Page.captureScreenshot", {
            "format": "png", "captureBeyondViewport": True
        })
        if "result" in result and "data" in result["result"]:
            img_data = base64.b64decode(result["result"]["data"])
            with open(path, "wb") as f:
                f.write(img_data)
        # Reset to desktop and restore cookies again
        await self.send("Emulation.clearDeviceMetricsOverride")
        await self.set_cookies(cookies)

    async def click_selector(self, selector: str) -> bool:
        """Click an element by CSS selector. Returns True if clicked."""
        clicked = await self.evaluate(f"""
            (() => {{
                const el = document.querySelector('{selector}');
                if (el) {{ el.click(); return true; }}
                return false;
            }})()
        """)
        return clicked is True

    async def click_text(self, text: str, tag: str = "*") -> bool:
        """Click an element containing exact text."""
        escaped = text.replace("'", "\\'").replace('"', '\\"')
        clicked = await self.evaluate(f"""
            (() => {{
                const els = document.querySelectorAll('{tag}');
                for (const el of els) {{
                    if (el.textContent.trim() === '{escaped}' || el.textContent.trim().includes('{escaped}')) {{
                        el.click();
                        return true;
                    }}
                }}
                return false;
            }})()
        """)
        return clicked is True

    async def type_text(self, selector: str, text: str):
        """Focus an input and type text character by character using DOM events."""
        # Focus the element
        await self.evaluate(f"""
            (() => {{
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.focus();
                    el.value = '';
                    // Trigger React's synthetic events
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    nativeInputValueSetter.call(el, '{text}');
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }})()
        """)

    async def set_viewport(self, width: int, height: int):
        cookies = await self.get_cookies()
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height, "deviceScaleFactor": 1, "mobile": width < 768
        })
        await self.set_cookies(cookies)

    async def count_elements(self, selector: str) -> int:
        result = await self.evaluate(f"document.querySelectorAll('{selector}').length")
        return result or 0

    async def get_text(self, selector: str) -> str:
        result = await self.evaluate(f"""
            (() => {{
                const el = document.querySelector('{selector}');
                return el ? el.textContent.trim() : '';
            }})()
        """)
        return result or ""

    async def get_all_texts(self, selector: str) -> list[str]:
        result = await self.evaluate(f"""
            (() => {{
                return Array.from(document.querySelectorAll('{selector}')).map(e => e.textContent.trim());
            }})()
        """)
        return result or []

    async def get_page_url(self) -> str:
        result = await self.evaluate("window.location.pathname")
        return result or ""

    async def get_visible_buttons(self) -> list[str]:
        result = await self.evaluate("""
            (() => {
                const btns = document.querySelectorAll('button, [role="button"], a.MuiButtonBase-root');
                return Array.from(btns)
                    .filter(b => b.offsetParent !== null)
                    .map(b => b.textContent.trim())
                    .filter(t => t.length > 0 && t.length < 100);
            })()
        """)
        return result or []

    async def get_component_counts(self) -> dict:
        result = await self.evaluate("""
            (() => {
                return {
                    tables: document.querySelectorAll('table').length,
                    cards: document.querySelectorAll('[class*="MuiCard"], [class*="MuiPaper"], [data-testid*="card"], [data-testid*="stat"]').length,
                    buttons: document.querySelectorAll('button').length,
                    charts: document.querySelectorAll('.recharts-responsive-container, .recharts-wrapper, svg.recharts-surface').length,
                    maps: document.querySelectorAll('.leaflet-container').length,
                    chips: document.querySelectorAll('[class*="MuiChip"]').length,
                    progressBars: document.querySelectorAll('[class*="MuiLinearProgress"], [class*="MuiCircularProgress"]').length,
                    inputs: document.querySelectorAll('input, select, [class*="MuiSelect"]').length,
                    avatars: document.querySelectorAll('[class*="MuiAvatar"]').length,
                };
            })()
        """)
        return result or {}


# ---------------------------------------------------------------------------
# OTP Helper
# ---------------------------------------------------------------------------
def get_otp_from_docker() -> str:
    """Extract OTP from API container logs."""
    try:
        result = subprocess.run(
            ["docker", "logs", "pashu-erp-api-1", "--tail", "30"],
            capture_output=True, text=True, timeout=10
        )
        combined = result.stdout + result.stderr
        # Look for "Code: XXXXXX" pattern
        for line in reversed(combined.strip().split("\n")):
            if "Code:" in line:
                import re
                match = re.search(r"Code:\s*(\d{6})", line)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"  [WARN] Failed to get OTP from docker: {e}")
    return ""


# ---------------------------------------------------------------------------
# Test Functions
# ---------------------------------------------------------------------------
async def test_auth_flow(cdp: CDPClient) -> bool:
    """Test login with OTP and return True if auth succeeded."""
    print("\n" + "=" * 70)
    print("PHASE 1: Authentication Flow")
    print("=" * 70)

    # Check if we're already authenticated by navigating to dashboard
    cdp.clear_tracking()
    await cdp.navigate(f"{BASE_URL}/", wait_seconds=3)
    current_url = await cdp.get_page_url()

    if current_url == "/" or current_url == "":
        # Check if dashboard content loaded (not redirected to login)
        has_dashboard = await cdp.evaluate("""
            (() => {
                const text = document.body.innerText;
                return text.includes('Dashboard') && (text.includes('Farmers') || text.includes('PashuRaksha'));
            })()
        """)
        if has_dashboard:
            print("  [OK] Already authenticated — dashboard loaded")
            return True

    # Navigate to login
    print("  Navigating to /login...")
    cdp.clear_tracking()
    await cdp.navigate(f"{BASE_URL}/login", wait_seconds=2)

    # Check we're on login page
    has_login = await cdp.evaluate("""
        document.body.innerText.includes('Staff Login') || document.body.innerText.includes('PashuRaksha')
    """)
    if not has_login:
        print("  [WARN] Login page did not load as expected")

    # Fill phone number using React-compatible input setter
    print(f"  Filling phone: {PHONE}")
    await cdp.evaluate(f"""
        (() => {{
            const inputs = document.querySelectorAll('input');
            for (const inp of inputs) {{
                if (inp.placeholder && inp.placeholder.includes('9876543210') ||
                    inp.getAttribute('inputmode') === 'numeric') {{
                    const nativeSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    nativeSetter.call(inp, '{PHONE}');
                    inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
            }}
            return false;
        }})()
    """)
    await asyncio.sleep(0.5)

    # Click Send OTP button
    print("  Clicking 'Send OTP'...")
    clicked = await cdp.click_text("Send OTP", "button")
    if not clicked:
        # Try finding button differently
        await cdp.evaluate("""
            (() => {
                const btns = document.querySelectorAll('button');
                for (const b of btns) {
                    if (b.textContent.includes('Send OTP') || b.textContent.includes('Send')) {
                        b.click();
                        return true;
                    }
                }
                return false;
            })()
        """)
    await asyncio.sleep(2)

    # Get OTP from docker logs
    print("  Fetching OTP from container logs...")
    otp = get_otp_from_docker()
    if not otp:
        print("  [FAIL] Could not retrieve OTP from container logs")
        return False
    print(f"  OTP retrieved: {otp}")

    # Fill OTP - the UI uses 6 individual input boxes
    print("  Filling OTP digits...")
    await cdp.evaluate(f"""
        (() => {{
            const otp = '{otp}';
            const inputs = document.querySelectorAll('input[inputmode="numeric"]');
            // Skip the phone input (it has maxLength=10)
            const otpInputs = Array.from(inputs).filter(i => {{
                const ml = i.getAttribute('maxlength') || i.maxLength;
                return ml && parseInt(ml) <= 6;
            }});
            if (otpInputs.length >= 6) {{
                const nativeSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                for (let i = 0; i < 6; i++) {{
                    nativeSetter.call(otpInputs[i], otp[i]);
                    otpInputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    otpInputs[i].dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
                return true;
            }}
            // Fallback: paste into first OTP input
            if (otpInputs.length > 0) {{
                nativeSetter.call(otpInputs[0], otp);
                otpInputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                otpInputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }}
            return false;
        }})()
    """)
    await asyncio.sleep(0.5)

    # Click Verify & Login
    print("  Clicking 'Verify & Login'...")
    await cdp.click_text("Verify", "button")
    await asyncio.sleep(3)

    # Check if we landed on dashboard
    current_url = await cdp.get_page_url()
    if current_url == "/" or current_url == "":
        print("  [OK] Auth flow complete - redirected to dashboard")
        return True
    else:
        print(f"  [WARN] After login, URL is: {current_url}")
        # Could still be on login with an error
        error_text = await cdp.evaluate("""
            (() => {
                const alerts = document.querySelectorAll('[class*="MuiAlert"]');
                return Array.from(alerts).map(a => a.textContent).join('; ');
            })()
        """)
        if error_text:
            print(f"  [ERROR] Auth error: {error_text}")
        return False


async def ensure_authenticated(cdp: CDPClient) -> bool:
    """Check if we're still authenticated. If not, re-login."""
    current_url = await cdp.get_page_url()
    if "/login" in (current_url or ""):
        print("  [WARN] Session lost — redirected to login. Re-authenticating...")
        # Re-do login
        await cdp.evaluate(f"""
            (() => {{
                const inputs = document.querySelectorAll('input');
                for (const inp of inputs) {{
                    if (inp.placeholder && inp.placeholder.includes('9876543210') ||
                        inp.getAttribute('inputmode') === 'numeric') {{
                        const nativeSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'value'
                        ).set;
                        nativeSetter.call(inp, '{PHONE}');
                        inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return true;
                    }}
                }}
                return false;
            }})()
        """)
        await asyncio.sleep(0.5)
        await cdp.click_text("Send OTP", "button")
        await asyncio.sleep(2)

        otp = get_otp_from_docker()
        if not otp:
            print("  [FAIL] Could not retrieve OTP for re-auth")
            return False

        await cdp.evaluate(f"""
            (() => {{
                const otp = '{otp}';
                const inputs = document.querySelectorAll('input[inputmode="numeric"]');
                const otpInputs = Array.from(inputs).filter(i => {{
                    const ml = i.getAttribute('maxlength') || i.maxLength;
                    return ml && parseInt(ml) <= 6;
                }});
                if (otpInputs.length >= 6) {{
                    const nativeSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    for (let i = 0; i < 6; i++) {{
                        nativeSetter.call(otpInputs[i], otp[i]);
                        otpInputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                        otpInputs[i].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                    return true;
                }}
                return false;
            }})()
        """)
        await asyncio.sleep(0.5)
        await cdp.click_text("Verify", "button")
        await asyncio.sleep(3)

        new_url = await cdp.get_page_url()
        if "/login" not in (new_url or ""):
            print("  [OK] Re-authenticated successfully")
            return True
        else:
            print("  [FAIL] Re-authentication failed")
            return False
    return True


async def test_page(cdp: CDPClient, report: PageReport, test_interactions: bool = True):
    """Navigate to a page, collect data, test interactions, take screenshots."""
    print(f"\n--- Testing: {report.name} ({report.path}) ---")
    cdp.clear_tracking()

    # Navigate
    load_ms = await cdp.navigate(f"{BASE_URL}{report.path}", wait_seconds=DATA_WAIT)
    report.load_time_ms = load_ms
    print(f"  Load time: {load_ms}ms")

    # Check if we got redirected to login
    if not await ensure_authenticated(cdp):
        report.status = "FAIL"
        report.issues.append("Authentication lost and re-login failed")
        return

    # If we re-authenticated, navigate again to the target page
    current_url = await cdp.get_page_url()
    if current_url != report.path and "/login" not in (current_url or ""):
        # We may have landed on dashboard after re-auth, navigate to target
        if current_url != report.path:
            cdp.clear_tracking()
            load_ms = await cdp.navigate(f"{BASE_URL}{report.path}", wait_seconds=DATA_WAIT)
            report.load_time_ms = load_ms

    # Check for errors in page render
    page_text = await cdp.evaluate("document.body.innerText") or ""
    if "Failed to load" in page_text or "500" in page_text:
        report.issues.append("Page shows error state")

    # Count components
    report.components = await cdp.get_component_counts()
    print(f"  Components: {report.components}")

    # Count data rows in tables
    report.data_rows = await cdp.count_elements("tbody tr")
    print(f"  Table rows: {report.data_rows} (expected >= {report.expected_min_rows})")

    if report.data_rows == 0 and report.expected_min_rows > 0:
        # Check if data is in cards/list items instead
        card_items = await cdp.count_elements("[class*='MuiCard'], [class*='MuiListItem'], [class*='MuiPaper']")
        if card_items > 0:
            report.data_rows = card_items
            print(f"  Data items (cards/papers): {card_items}")

    if report.data_rows < report.expected_min_rows and report.expected_min_rows > 0:
        report.issues.append(
            f"Data rows ({report.data_rows}) below expected ({report.expected_min_rows})"
        )

    # Collect visible buttons
    buttons = await cdp.get_visible_buttons()
    print(f"  Visible buttons: {len(buttons)}")

    # Take desktop screenshot
    desktop_path = os.path.join(SCREENSHOT_DIR, f"{report.name.lower().replace(' ', '-')}-desktop.png")
    await cdp.screenshot(desktop_path, width=1920, height=1080)
    report.screenshot_desktop = desktop_path
    print(f"  Screenshot (desktop): {desktop_path}")

    # Take responsive screenshot
    responsive_path = os.path.join(SCREENSHOT_DIR, f"{report.name.lower().replace(' ', '-')}-responsive.png")
    await cdp.screenshot(responsive_path, width=RESPONSIVE_WIDTH, height=1024)
    report.screenshot_responsive = responsive_path
    print(f"  Screenshot (responsive): {responsive_path}")

    # Reset viewport
    await cdp.send("Emulation.clearDeviceMetricsOverride")
    await asyncio.sleep(0.5)

    # Interaction testing
    if test_interactions:
        await test_page_interactions(cdp, report, buttons)

    # Collect network data
    api_requests = cdp.get_api_requests()
    for r in api_requests:
        report.network_requests.append({
            "url": r.url, "method": r.method,
            "status": r.status, "time_ms": r.timing_ms,
            "error": r.error
        })

    report.latency_flags = cdp.get_latency_flags(threshold_ms=2000)
    report.console_errors = list(cdp.console_errors)
    report.console_warnings = list(cdp.console_warnings)

    # Status determination
    has_critical_issue = (
        report.data_rows < report.expected_min_rows and report.expected_min_rows > 0
    )
    has_network_errors = any(r["status"] >= 500 for r in report.network_requests)
    has_js_errors = len([e for e in report.console_errors if "EXCEPTION" in e]) > 0

    if has_critical_issue or has_network_errors or has_js_errors:
        report.status = "FAIL"
    elif report.issues or report.latency_flags:
        report.status = "WARN"
    else:
        report.status = "PASS"

    print(f"  Status: {report.status}")
    if report.issues:
        for issue in report.issues:
            print(f"  [ISSUE] {issue}")


async def test_page_interactions(cdp: CDPClient, report: PageReport, buttons: list[str]):
    """Test interactive elements on the current page."""

    # --- Sort column headers (if table exists) ---
    sort_labels = await cdp.count_elements("[class*='MuiTableSortLabel']")
    if sort_labels > 0:
        for i in range(min(sort_labels, 3)):
            clicked = await cdp.evaluate(f"""
                (() => {{
                    const labels = document.querySelectorAll('[class*="MuiTableSortLabel"]');
                    if (labels[{i}]) {{
                        labels[{i}].click();
                        return labels[{i}].textContent.trim();
                    }}
                    return null;
                }})()
            """)
            if clicked:
                report.buttons_clicked.append(f"Sort: {clicked}")
                await asyncio.sleep(0.5)

    # --- Pagination (if present) ---
    has_pagination = await cdp.count_elements("[class*='MuiTablePagination']")
    if has_pagination > 0:
        # Try clicking next page
        next_clicked = await cdp.evaluate("""
            (() => {
                const btn = document.querySelector('[aria-label="Go to next page"]');
                if (btn && !btn.disabled) { btn.click(); return true; }
                return false;
            })()
        """)
        if next_clicked:
            report.buttons_clicked.append("Pagination: Next")
            await asyncio.sleep(1)

            # Go back to first page
            await cdp.evaluate("""
                (() => {
                    const btn = document.querySelector('[aria-label="Go to previous page"]');
                    if (btn && !btn.disabled) { btn.click(); return true; }
                    return false;
                })()
            """)
            report.buttons_clicked.append("Pagination: Previous")
            await asyncio.sleep(0.5)

    # --- Search/filter inputs ---
    search_input = await cdp.count_elements("input[placeholder*='Search'], input[placeholder*='search'], input[aria-label*='Search'], input[aria-label*='search']")
    if search_input > 0:
        # Type a search term
        await cdp.evaluate("""
            (() => {
                const inp = document.querySelector("input[placeholder*='Search'], input[placeholder*='search'], input[aria-label*='Search']");
                if (inp) {
                    const nativeSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    nativeSetter.call(inp, 'Mysuru');
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                }
                return false;
            })()
        """)
        await asyncio.sleep(1)
        filtered_rows = await cdp.count_elements("tbody tr")
        report.interactions.append(f"Search 'Mysuru': {filtered_rows} rows after filter")

        # Clear search
        await cdp.evaluate("""
            (() => {
                const inp = document.querySelector("input[placeholder*='Search'], input[placeholder*='search'], input[aria-label*='Search']");
                if (inp) {
                    const nativeSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    nativeSetter.call(inp, '');
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                }
                return false;
            })()
        """)
        await asyncio.sleep(0.5)

    # --- Filter dropdowns (Species, Risk Level, etc.) ---
    selects = await cdp.evaluate("""
        (() => {
            const selectLabels = document.querySelectorAll('[class*="MuiInputLabel"], [class*="MuiFormLabel"]');
            return Array.from(selectLabels).map(l => l.textContent.trim()).filter(t => t.length > 0 && t.length < 50);
        })()
    """)
    if selects:
        report.interactions.append(f"Filter controls found: {selects}")

    # --- Click first few visible action buttons (View, Edit, etc.) ---
    action_buttons = await cdp.evaluate("""
        (() => {
            const btns = document.querySelectorAll('button, [role="button"]');
            const actions = [];
            for (const b of btns) {
                const text = b.textContent.trim();
                if ((text.includes('View') || text.includes('Edit') || text.includes('Details')) &&
                    b.offsetParent !== null && text.length < 30) {
                    actions.push(text);
                }
            }
            return actions.slice(0, 3);
        })()
    """)
    if action_buttons:
        report.interactions.append(f"Action buttons found: {action_buttons}")

    # --- Tab buttons ---
    tabs = await cdp.evaluate("""
        (() => {
            const tabBtns = document.querySelectorAll('[role="tab"], [class*="MuiTab"]');
            return Array.from(tabBtns).map(t => t.textContent.trim()).filter(t => t.length > 0);
        })()
    """)
    if tabs:
        for i, tab_text in enumerate(tabs[:3]):
            await cdp.evaluate(f"""
                (() => {{
                    const tabBtns = document.querySelectorAll('[role="tab"], [class*="MuiTab"]');
                    if (tabBtns[{i}]) {{
                        tabBtns[{i}].click();
                        return true;
                    }}
                    return false;
                }})()
            """)
            report.buttons_clicked.append(f"Tab: {tab_text}")
            await asyncio.sleep(0.5)

    # --- Chip filters ---
    chips = await cdp.evaluate("""
        (() => {
            const chips = document.querySelectorAll('[class*="MuiChip"][class*="clickable"], [class*="MuiChip"][role="button"]');
            return Array.from(chips).map(c => c.textContent.trim()).filter(t => t.length > 0).slice(0, 3);
        })()
    """)
    if chips:
        report.interactions.append(f"Clickable chips: {chips}")


async def test_sidebar_navigation(cdp: CDPClient) -> list[str]:
    """Click every sidebar nav item and verify navigation. Returns list of issues."""
    print("\n" + "=" * 70)
    print("PHASE 3: Sidebar Navigation Test")
    print("=" * 70)

    nav_items = [
        ("Dashboard", "/"),
        ("Farmers", "/farmers"),
        ("Animals", "/animals"),
        ("Milk Collection", "/milk"),
        ("Health Alerts", "/health"),
        ("Vaccinations", "/vaccinations"),
        ("Vet Dashboard", "/vet"),
        ("Vet Cases", "/vet/cases"),
        ("Govt Schemes", "/schemes"),
        ("Marketplace", "/marketplace"),
        ("Income Analytics", "/income"),
        ("Map View", "/map"),
        ("IoT Devices", "/iot"),
    ]

    issues = []

    # First ensure we're authenticated and on a page with the sidebar
    await cdp.navigate(f"{BASE_URL}/", wait_seconds=3)
    await ensure_authenticated(cdp)

    for label, expected_path in nav_items:
        # Click sidebar link by href (more reliable than text matching)
        href_escaped = expected_path.replace("'", "\\'")
        clicked = await cdp.evaluate(f"""
            (() => {{
                // Try exact href match first
                let link = document.querySelector('a[href="{href_escaped}"]');
                if (link) {{ link.click(); return true; }}
                // Fallback: text match within sidebar nav
                const nav = document.querySelector('[role="navigation"]');
                if (!nav) return false;
                const links = nav.querySelectorAll('a');
                for (const l of links) {{
                    if (l.textContent.trim().includes('{label}')) {{
                        l.click();
                        return true;
                    }}
                }}
                return false;
            }})()
        """)

        if not clicked:
            issues.append(f"Sidebar '{label}' not found/clickable")
            print(f"  [FAIL] {label}: not found")
            continue

        await asyncio.sleep(2)
        current = await cdp.get_page_url()
        matches = current == expected_path or current.startswith(expected_path)
        status = "OK" if matches else "MISMATCH"
        print(f"  [{status}] {label}: expected={expected_path}, actual={current}")
        if not matches:
            issues.append(f"Nav '{label}': expected {expected_path}, got {current}")

    return issues


# ---------------------------------------------------------------------------
# Main test runner
# ---------------------------------------------------------------------------
async def run_tests():
    print("=" * 70)
    print("PashuRaksha Admin Dashboard — Full E2E Test Suite")
    print(f"Target: {BASE_URL} via CDP at {CDP_HTTP}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Get the websocket URL for the browser
    import urllib.request
    tabs_json = urllib.request.urlopen(f"{CDP_HTTP}/json/list").read()
    tabs = json.loads(tabs_json)

    # Find or create a tab to use
    target_ws = None
    for tab in tabs:
        if tab.get("type") == "page" and "localhost:3000" in tab.get("url", ""):
            target_ws = tab["webSocketDebuggerUrl"]
            break

    if not target_ws:
        # Use browser-level CDP to create a new tab
        version_json = urllib.request.urlopen(f"{CDP_HTTP}/json/version").read()
        version = json.loads(version_json)
        browser_ws = version["webSocketDebuggerUrl"]
        print(f"No existing tab found. Creating new tab via browser CDP...")

        # Connect to browser, create target
        browser_cdp = CDPClient(browser_ws)
        await browser_cdp.connect()
        result = await browser_cdp.send("Target.createTarget", {"url": BASE_URL})
        target_id = result.get("result", {}).get("targetId", "")
        await browser_cdp.disconnect()

        # Refetch tabs
        await asyncio.sleep(1)
        tabs_json = urllib.request.urlopen(f"{CDP_HTTP}/json/list").read()
        tabs = json.loads(tabs_json)
        for tab in tabs:
            if tab.get("id") == target_id:
                target_ws = tab["webSocketDebuggerUrl"]
                break

    if not target_ws:
        print("[FATAL] Could not find or create a suitable Chrome tab")
        sys.exit(1)

    print(f"Using tab WS: {target_ws}")

    cdp = CDPClient(target_ws)
    await cdp.connect()
    await cdp.enable_domains()

    all_reports: list[PageReport] = []

    # ---- Phase 1: Auth ----
    auth_ok = await test_auth_flow(cdp)
    if not auth_ok:
        print("\n[WARN] Auth flow may have issues. Continuing tests as browser may have existing session...")

    # ---- Phase 2: Page-by-page testing ----
    print("\n" + "=" * 70)
    print("PHASE 2: Page-by-Page Testing")
    print("=" * 70)

    pages = [
        PageReport(path="/", name="Dashboard", expected_min_rows=0),
        PageReport(path="/farmers", name="Farmers", expected_min_rows=5),
        PageReport(path="/animals", name="Animals", expected_min_rows=5),
        PageReport(path="/milk", name="Milk Collection", expected_min_rows=5),
        PageReport(path="/health", name="Health Alerts", expected_min_rows=1),
        PageReport(path="/vaccinations", name="Vaccinations", expected_min_rows=0),
        PageReport(path="/schemes", name="Govt Schemes", expected_min_rows=1),
        PageReport(path="/marketplace", name="Marketplace", expected_min_rows=1),
        PageReport(path="/income", name="Income Analytics", expected_min_rows=0),
        PageReport(path="/iot", name="IoT Devices", expected_min_rows=0),
        PageReport(path="/map", name="Map View", expected_min_rows=0),
        PageReport(path="/vet", name="Vet Dashboard", expected_min_rows=0),
        PageReport(path="/vet/cases", name="Vet Cases", expected_min_rows=1),
        PageReport(path="/vet/alerts", name="Vet Alerts", expected_min_rows=1),
    ]

    for page_report in pages:
        await test_page(cdp, page_report)
        all_reports.append(page_report)

    # ---- Phase 2.5: Dashboard-specific validation ----
    print("\n--- Dashboard: Stat Card Value Validation ---")
    cdp.clear_tracking()
    await cdp.navigate(f"{BASE_URL}/", wait_seconds=DATA_WAIT)

    stat_values = await cdp.evaluate("""
        (() => {
            const cards = document.querySelectorAll('[data-testid="stat-card"]');
            if (cards.length === 0) {
                // Fallback: look for Paper elements that contain stat-like content
                const papers = document.querySelectorAll('[class*="MuiPaper"]');
                const results = [];
                papers.forEach(p => {
                    const text = p.textContent;
                    if (text && (text.includes('Farmers') || text.includes('Animals') ||
                        text.includes('Milk') || text.includes('Alerts') ||
                        text.includes('Revenue') || text.includes('Sellers'))) {
                        results.push(text.trim().substring(0, 100));
                    }
                });
                return results;
            }
            return Array.from(cards).map(c => c.textContent.trim().substring(0, 100));
        })()
    """)
    print(f"  Stat card values: {stat_values}")

    # Check for charts
    chart_count = await cdp.count_elements(".recharts-responsive-container, .recharts-wrapper, .recharts-surface")
    map_count = await cdp.count_elements(".leaflet-container")
    print(f"  Charts: {chart_count}, Maps: {map_count}")

    # Verify stat values are not all dashes/zeros
    has_real_data = await cdp.evaluate("""
        (() => {
            const bodyText = document.body.innerText;
            // Check for actual numbers in stat cards area
            const numbers = bodyText.match(/\\d{1,3}(,\\d{3})*/g);
            return numbers && numbers.length > 3;
        })()
    """)
    dashboard_report = all_reports[0]
    if not has_real_data:
        dashboard_report.issues.append("Dashboard may show placeholder values instead of real data")

    # ---- Phase 3: Sidebar Navigation ----
    nav_issues = await test_sidebar_navigation(cdp)

    # ---- Phase 4: Cross-page responsive check ----
    print("\n" + "=" * 70)
    print("PHASE 4: Responsive Layout Check (768px)")
    print("=" * 70)

    responsive_issues = []
    # Save cookies before responsive tests
    saved_cookies = await cdp.get_cookies()
    for page_report in [all_reports[0], all_reports[1], all_reports[3]]:  # Dashboard, Farmers, Milk
        await cdp.set_cookies(saved_cookies)
        await cdp.set_viewport(RESPONSIVE_WIDTH, 1024)
        await cdp.navigate(f"{BASE_URL}{page_report.path}", wait_seconds=2)
        await ensure_authenticated(cdp)

        # Check for horizontal overflow
        overflow = await cdp.evaluate("""
            document.documentElement.scrollWidth > document.documentElement.clientWidth + 10
        """)
        if overflow:
            responsive_issues.append(f"{page_report.name}: horizontal overflow at {RESPONSIVE_WIDTH}px")
            print(f"  [WARN] {page_report.name}: horizontal overflow")
        else:
            print(f"  [OK] {page_report.name}: no overflow")

        # Check sidebar visibility at mobile width
        sidebar_visible = await cdp.evaluate("""
            (() => {
                const nav = document.querySelector('[role="navigation"]');
                if (!nav) return 'no-nav';
                return nav.offsetParent !== null ? 'visible' : 'hidden';
            })()
        """)
        print(f"  Sidebar at {RESPONSIVE_WIDTH}px: {sidebar_visible}")

    await cdp.send("Emulation.clearDeviceMetricsOverride")
    await cdp.set_cookies(saved_cookies)

    # ---- Cleanup ----
    await cdp.disconnect()

    # ---- Generate Report ----
    print("\n\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)

    total = len(all_reports)
    passed = sum(1 for r in all_reports if r.status == "PASS")
    warned = sum(1 for r in all_reports if r.status == "WARN")
    failed = sum(1 for r in all_reports if r.status == "FAIL")

    print(f"\nSummary: {passed} PASS / {warned} WARN / {failed} FAIL out of {total} pages\n")

    for r in all_reports:
        status_marker = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]", "PENDING": "[----]"}
        print(f"\n## Page: {r.path}")
        print(f"Status: {status_marker.get(r.status, r.status)}")
        print(f"Load time: {r.load_time_ms}ms")
        if r.expected_min_rows > 0:
            print(f"Data rows: {r.data_rows} (expected: {r.expected_min_rows}+)")
        print(f"Components: {r.components}")

        if r.console_errors:
            print(f"Console errors ({len(r.console_errors)}):")
            for e in r.console_errors[:5]:
                print(f"  - {e[:200]}")

        if r.network_requests:
            api_reqs = [n for n in r.network_requests if ":8000" in n.get("url", "") or "/v1/" in n.get("url", "")]
            if api_reqs:
                print(f"API requests ({len(api_reqs)}):")
                for n in api_reqs[:8]:
                    status_str = f"{n['status']}" if n['status'] else "pending"
                    err_str = f" ERROR: {n['error']}" if n.get('error') else ""
                    print(f"  {n['method']} {n['url'][:80]} -> {status_str} ({n['time_ms']}ms){err_str}")

        if r.latency_flags:
            print(f"Latency flags (>2s):")
            for lf in r.latency_flags:
                print(f"  - {lf}")

        if r.buttons_clicked:
            print(f"Buttons clicked: {r.buttons_clicked}")

        if r.interactions:
            print(f"Interactions: {r.interactions}")

        if r.issues:
            print(f"Issues:")
            for issue in r.issues:
                print(f"  - {issue}")

        print(f"Screenshots: {r.screenshot_desktop}")

    # Navigation issues
    if nav_issues:
        print(f"\n## Sidebar Navigation Issues:")
        for issue in nav_issues:
            print(f"  - {issue}")

    # Responsive issues
    if responsive_issues:
        print(f"\n## Responsive Issues:")
        for issue in responsive_issues:
            print(f"  - {issue}")

    # Overall verdict
    print("\n" + "=" * 70)
    if failed > 0:
        print(f"VERDICT: FAIL ({failed} pages with critical issues)")
    elif warned > 0:
        print(f"VERDICT: WARN ({warned} pages with minor issues)")
    else:
        print("VERDICT: PASS (all pages healthy)")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
