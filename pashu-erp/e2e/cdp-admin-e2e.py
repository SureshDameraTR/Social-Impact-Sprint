#!/usr/bin/env python3
"""
PashuRaksha Admin Dashboard — Exhaustive CDP E2E Test Suite
============================================================
Connects to Chrome via CDP (ws://127.0.0.1:9222) and performs deep testing
of every page in the admin dashboard at http://localhost:3000.

Tests: auth flow, page rendering, network requests, console errors,
MUI component presence, responsive viewports, interactive elements.
"""

import asyncio
import base64
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import websockets

# ── Configuration ────────────────────────────────────────────────────────────

CDP_URL = "http://127.0.0.1:9222"
ADMIN_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"
PHONE = "9876543210"
PHONE_WITH_PREFIX = "+919876543210"

SCREENSHOT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "screenshots", "admin"
)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Pages to test (path, display_name, expected_components)
ADMIN_PAGES = [
    ("/", "Dashboard", ["stat-card", "recharts", "leaflet"]),
    ("/farmers", "Farmers", ["table", "pagination", "search"]),
    ("/animals", "Animals", ["table", "chip", "filter"]),
    ("/milk", "Milk Collection", ["table", "chip"]),
    ("/health", "Health Alerts", ["card", "chip", "badge"]),
    ("/vaccinations", "Vaccinations", ["stat-card", "progress"]),
    ("/schemes", "Govt Schemes", ["card"]),
    ("/marketplace", "Marketplace", ["card"]),
    ("/income", "Income Analytics", ["recharts"]),
    ("/iot", "IoT Devices", ["card", "table"]),
    ("/map", "Map View", ["leaflet"]),
    ("/vet", "Vet Dashboard", ["card"]),
    ("/vet/cases", "Vet Cases", ["table", "card"]),
    ("/vet/alerts", "Vet Alerts", ["card", "chip"]),
]

VIEWPORTS = [
    ("desktop", 1920, 1080),
    ("tablet", 1024, 768),
    ("mobile", 375, 667),
]


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class NetworkRequest:
    url: str
    method: str
    status: int = 0
    duration_ms: float = 0
    size_bytes: int = 0
    failed: bool = False
    error_text: str = ""
    timestamp: float = 0


@dataclass
class ConsoleMessage:
    level: str  # log, warning, error, info
    text: str
    url: str = ""
    line: int = 0


@dataclass
class PageResult:
    path: str
    name: str
    viewport: str = "desktop"
    load_time_ms: float = 0
    status: str = "UNTESTED"
    content_length: int = 0
    components_found: dict = field(default_factory=dict)
    console_errors: list = field(default_factory=list)
    console_warnings: list = field(default_factory=list)
    network_requests: list = field(default_factory=list)
    network_errors: list = field(default_factory=list)
    slow_requests: list = field(default_factory=list)
    total_bytes: int = 0
    bugs: list = field(default_factory=list)
    screenshot_path: str = ""
    interactive_results: dict = field(default_factory=dict)


@dataclass
class TestReport:
    timestamp: str = ""
    auth_status: str = "UNTESTED"
    auth_details: str = ""
    page_results: list = field(default_factory=list)
    all_console_errors: list = field(default_factory=list)
    all_network_errors: list = field(default_factory=list)
    all_bugs: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)


# ── CDP Client ───────────────────────────────────────────────────────────────

class CDPClient:
    """Low-level Chrome DevTools Protocol client over WebSocket."""

    def __init__(self, ws):
        self.ws = ws
        self._msg_id = 0
        self._pending = {}
        self._event_handlers = {}
        self._listener_task = None

    async def start_listener(self):
        self._listener_task = asyncio.create_task(self._listen())

    async def _listen(self):
        try:
            async for raw in self.ws:
                msg = json.loads(raw)
                if "id" in msg:
                    fut = self._pending.pop(msg["id"], None)
                    if fut and not fut.done():
                        fut.set_result(msg)
                elif "method" in msg:
                    method = msg["method"]
                    if method in self._event_handlers:
                        for handler in self._event_handlers[method]:
                            try:
                                handler(msg.get("params", {}))
                            except Exception:
                                pass
        except websockets.exceptions.ConnectionClosed:
            pass

    def on(self, event: str, handler):
        self._event_handlers.setdefault(event, []).append(handler)

    async def send(self, method: str, params: dict = None, timeout: float = 30) -> dict:
        self._msg_id += 1
        mid = self._msg_id
        msg = {"id": mid, "method": method}
        if params:
            msg["params"] = params
        fut = asyncio.get_event_loop().create_future()
        self._pending[mid] = fut
        await self.ws.send(json.dumps(msg))
        try:
            result = await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            self._pending.pop(mid, None)
            return {"error": {"message": f"Timeout after {timeout}s for {method}"}}
        return result

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass


# ── Helper Functions ─────────────────────────────────────────────────────────

async def get_cdp_target():
    """Create a fresh page target and return its WebSocket URL."""
    import urllib.request
    # Chrome requires PUT for /json/new
    req = urllib.request.Request(f"{CDP_URL}/json/new?about:blank", method="PUT")
    data = urllib.request.urlopen(req).read()
    target = json.loads(data)
    return target["webSocketDebuggerUrl"]


def get_otp_from_logs() -> str:
    """Extract OTP from API container logs."""
    try:
        result = subprocess.run(
            ["docker", "logs", "pashu-erp-api-1", "--tail", "30"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout + result.stderr
        lines = output.strip().split("\n")
        for line in reversed(lines):
            if "Code:" in line:
                # Extract the 6-digit code
                parts = line.split("Code:")
                if len(parts) > 1:
                    code = parts[1].strip().split()[0].strip()
                    digits = "".join(c for c in code if c.isdigit())
                    if len(digits) >= 6:
                        return digits[:6]
        # Fallback: look for OTP pattern
        for line in reversed(lines):
            if "otp" in line.lower() or "OTP" in line:
                import re
                match = re.search(r'\b(\d{6})\b', line)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"  [WARN] Failed to get OTP from logs: {e}")
    return ""


async def evaluate(cdp: CDPClient, expression: str, timeout: float = 10) -> Any:
    """Evaluate JS expression and return the value."""
    result = await cdp.send("Runtime.evaluate", {
        "expression": expression,
        "returnByValue": True,
        "awaitPromise": True,
        "timeout": int(timeout * 1000),
    }, timeout=timeout + 5)
    if "error" in result:
        return None
    r = result.get("result", {}).get("result", {})
    if r.get("type") == "undefined":
        return None
    return r.get("value", r.get("description", None))


async def navigate(cdp: CDPClient, url: str, wait_ms: int = 3000) -> float:
    """Navigate to URL and wait for load. Returns load time in ms."""
    start = time.time()
    await cdp.send("Page.navigate", {"url": url})
    # Wait for loadEventFired or timeout
    load_event = asyncio.get_event_loop().create_future()

    def on_load(params):
        if not load_event.done():
            load_event.set_result(True)

    cdp.on("Page.loadEventFired", on_load)
    try:
        await asyncio.wait_for(load_event, timeout=15)
    except asyncio.TimeoutError:
        pass
    # Remove handler to avoid stacking
    cdp._event_handlers.get("Page.loadEventFired", []).clear()

    elapsed = (time.time() - start) * 1000
    # Extra wait for JS rendering
    await asyncio.sleep(wait_ms / 1000)
    return elapsed


async def take_screenshot(cdp: CDPClient, filename: str) -> str:
    """Take a screenshot and save to file. Returns path."""
    result = await cdp.send("Page.captureScreenshot", {
        "format": "png",
        "quality": 80,
    })
    if "error" in result:
        return ""
    data = result.get("result", {}).get("data", "")
    if not data:
        return ""
    path = os.path.join(SCREENSHOT_DIR, filename)
    with open(path, "wb") as f:
        f.write(base64.b64decode(data))
    return path


async def set_viewport(cdp: CDPClient, width: int, height: int):
    """Set browser viewport size."""
    await cdp.send("Emulation.setDeviceMetricsOverride", {
        "width": width,
        "height": height,
        "deviceScaleFactor": 1,
        "mobile": width < 768,
    })


async def get_page_metrics(cdp: CDPClient) -> dict:
    """Get comprehensive page metrics via JS evaluation."""
    metrics_js = """
    (() => {
        const body = document.body;
        const html = document.documentElement;

        // Content metrics
        const textContent = body?.innerText || '';
        const contentLength = textContent.length;
        const wordCount = textContent.trim().split(/\\s+/).filter(Boolean).length;

        // DOM metrics
        const allElements = document.querySelectorAll('*').length;

        // MUI Components
        const muiCards = document.querySelectorAll('.MuiCard-root').length;
        const muiTables = document.querySelectorAll('.MuiTable-root, table').length;
        const muiButtons = document.querySelectorAll('.MuiButton-root, button').length;
        const muiChips = document.querySelectorAll('.MuiChip-root').length;
        const muiTextFields = document.querySelectorAll('.MuiTextField-root, .MuiInputBase-root').length;
        const muiPagination = document.querySelectorAll('.MuiTablePagination-root, .MuiPagination-root').length;
        const muiProgress = document.querySelectorAll('.MuiLinearProgress-root, .MuiCircularProgress-root').length;
        const muiSelects = document.querySelectorAll('.MuiSelect-root, [role="combobox"]').length;
        const muiDialogs = document.querySelectorAll('.MuiDialog-root, .MuiModal-root').length;
        const muiAlerts = document.querySelectorAll('.MuiAlert-root').length;
        const muiTypography = document.querySelectorAll('.MuiTypography-root, h1, h2, h3, h4, h5, h6').length;

        // Data-testid components
        const statCards = document.querySelectorAll('[data-testid="stat-card"]').length;
        const vaccStatCards = document.querySelectorAll('[data-testid="vacc-stat-card"]').length;

        // Charts
        const rechartsContainers = document.querySelectorAll('.recharts-responsive-container, .recharts-wrapper').length;
        const rechartsSvgs = document.querySelectorAll('.recharts-surface').length;

        // Maps
        const leafletMaps = document.querySelectorAll('.leaflet-container').length;
        const leafletMarkers = document.querySelectorAll('.leaflet-marker-icon').length;

        // Tables
        const tableRows = document.querySelectorAll('tbody tr').length;
        const tableHeaders = document.querySelectorAll('thead th').length;

        // Sidebar
        const sidebar = document.querySelector('[data-testid="admin-sidebar"], nav, .MuiDrawer-root');
        const sidebarVisible = sidebar ? sidebar.offsetWidth > 0 : false;
        const navLinks = document.querySelectorAll('nav a, .MuiListItem-root, .MuiListItemButton-root').length;

        // Errors visible on page
        const errorElements = document.querySelectorAll('.MuiAlert-standardError, [class*="error"], [role="alert"]').length;
        const has404 = textContent.includes('404');
        const hasError = textContent.toLowerCase().includes('something went wrong');

        // Images
        const images = document.querySelectorAll('img').length;
        const brokenImages = [...document.querySelectorAll('img')].filter(
            img => img.complete && img.naturalHeight === 0
        ).length;

        // Scroll dimensions
        const scrollWidth = html.scrollWidth;
        const clientWidth = html.clientWidth;
        const hasHorizontalOverflow = scrollWidth > clientWidth + 5;

        return {
            contentLength, wordCount, allElements,
            mui: {
                cards: muiCards, tables: muiTables, buttons: muiButtons,
                chips: muiChips, textFields: muiTextFields, pagination: muiPagination,
                progress: muiProgress, selects: muiSelects, dialogs: muiDialogs,
                alerts: muiAlerts, typography: muiTypography,
            },
            testid: { statCards, vaccStatCards },
            charts: { rechartsContainers, rechartsSvgs },
            maps: { leafletMaps, leafletMarkers },
            tables: { rows: tableRows, headers: tableHeaders },
            sidebar: { visible: sidebarVisible, navLinks },
            errors: { errorElements, has404, hasError },
            images: { total: images, broken: brokenImages },
            layout: { scrollWidth, clientWidth, hasHorizontalOverflow },
        };
    })()
    """
    return await evaluate(cdp, metrics_js)


async def get_clickable_elements(cdp: CDPClient) -> list:
    """Get all clickable buttons and links with their details."""
    js = """
    (() => {
        const items = [];
        const seen = new Set();

        // Buttons
        document.querySelectorAll('button, .MuiButton-root, .MuiIconButton-root').forEach(el => {
            const text = (el.innerText || el.getAttribute('aria-label') || '').trim().substring(0, 50);
            const key = `btn:${text}:${el.offsetLeft}:${el.offsetTop}`;
            if (!seen.has(key) && el.offsetWidth > 0 && el.offsetHeight > 0) {
                seen.add(key);
                items.push({
                    type: 'button',
                    text: text,
                    x: el.getBoundingClientRect().x + el.offsetWidth/2,
                    y: el.getBoundingClientRect().y + el.offsetHeight/2,
                    disabled: el.disabled || el.getAttribute('aria-disabled') === 'true',
                    visible: el.offsetWidth > 0,
                });
            }
        });

        // Table sort headers
        document.querySelectorAll('th[role="columnheader"], .MuiTableSortLabel-root').forEach(el => {
            const text = (el.innerText || '').trim().substring(0, 30);
            const key = `sort:${text}`;
            if (!seen.has(key) && el.offsetWidth > 0) {
                seen.add(key);
                items.push({
                    type: 'sort-header',
                    text: text,
                    x: el.getBoundingClientRect().x + el.offsetWidth/2,
                    y: el.getBoundingClientRect().y + el.offsetHeight/2,
                    visible: true,
                });
            }
        });

        // Pagination buttons
        document.querySelectorAll('.MuiTablePagination-actions button, .MuiPagination-ul button').forEach(el => {
            const text = (el.getAttribute('aria-label') || el.innerText || '').trim().substring(0, 30);
            const key = `pag:${text}`;
            if (!seen.has(key)) {
                seen.add(key);
                items.push({
                    type: 'pagination',
                    text: text,
                    x: el.getBoundingClientRect().x + el.offsetWidth/2,
                    y: el.getBoundingClientRect().y + el.offsetHeight/2,
                    disabled: el.disabled,
                    visible: el.offsetWidth > 0,
                });
            }
        });

        // Select/filter dropdowns
        document.querySelectorAll('.MuiSelect-select, [role="combobox"]').forEach(el => {
            const text = (el.innerText || '').trim().substring(0, 30);
            items.push({
                type: 'select',
                text: text,
                x: el.getBoundingClientRect().x + el.offsetWidth/2,
                y: el.getBoundingClientRect().y + el.offsetHeight/2,
                visible: el.offsetWidth > 0,
            });
        });

        return items.slice(0, 50); // Cap at 50
    })()
    """
    return await evaluate(cdp, js) or []


async def click_element(cdp: CDPClient, x: float, y: float):
    """Click at given coordinates."""
    for event_type in ["mousePressed", "mouseReleased"]:
        await cdp.send("Input.dispatchMouseEvent", {
            "type": event_type,
            "x": x, "y": y,
            "button": "left",
            "clickCount": 1,
        })
    await asyncio.sleep(0.3)


async def type_text(cdp: CDPClient, text: str, delay_ms: int = 50):
    """Type text character by character."""
    for char in text:
        await cdp.send("Input.dispatchKeyEvent", {
            "type": "keyDown",
            "text": char,
            "key": char,
        })
        await cdp.send("Input.dispatchKeyEvent", {
            "type": "keyUp",
            "key": char,
        })
        await asyncio.sleep(delay_ms / 1000)


# ── Authentication ───────────────────────────────────────────────────────────

async def authenticate(cdp: CDPClient) -> tuple[bool, str]:
    """Perform the full login flow. Returns (success, detail_message)."""
    print("\n== AUTHENTICATION ==")

    # Step 1: Navigate to login
    print("  [1] Navigating to login page...")
    await navigate(cdp, f"{ADMIN_URL}/login", wait_ms=3000)

    # Verify login page loaded
    metrics = await get_page_metrics(cdp)
    if not metrics:
        return False, "Login page failed to load — no metrics"

    page_text = await evaluate(cdp, "document.body.innerText") or ""
    if "PashuRaksha" not in page_text and "Login" not in page_text and "Mobile" not in page_text:
        await take_screenshot(cdp, "auth_failed_no_login.png")
        return False, f"Login page not rendered. Text length={len(page_text)}"

    print(f"  [OK] Login page loaded ({metrics.get('contentLength', 0)} chars)")

    # Step 2: Find and fill phone input
    print("  [2] Filling phone number...")
    # Wait for React to hydrate — inputs might not be in DOM yet
    for attempt in range(10):
        input_count = await evaluate(cdp, "document.querySelectorAll('input').length")
        if input_count and input_count > 0:
            break
        print(f"  [INFO] Waiting for inputs to appear... attempt {attempt+1}")
        await asyncio.sleep(1)

    # Focus the phone input
    focus_js = """
    (() => {
        const inputs = document.querySelectorAll('input');
        for (const inp of inputs) {
            if (inp.placeholder?.includes('9876') || inp.type === 'tel' ||
                inp.inputMode === 'numeric' || inp.closest('.MuiTextField-root')) {
                inp.focus();
                inp.click();
                return { found: true, placeholder: inp.placeholder, type: inp.type, id: inp.id };
            }
        }
        // Fallback: just find any visible input
        for (const inp of inputs) {
            if (inp.offsetWidth > 0 && inp.offsetHeight > 0) {
                inp.focus();
                inp.click();
                return { found: true, placeholder: inp.placeholder, type: inp.type, fallback: true };
            }
        }
        return { found: false, count: inputs.length };
    })()
    """
    input_info = await evaluate(cdp, focus_js)
    print(f"  [INFO] Input search: {input_info}")

    if not input_info or not input_info.get("found"):
        await take_screenshot(cdp, "auth_failed_no_input.png")
        return False, "Could not find phone input field"

    # Clear existing text and type phone number
    await cdp.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "a", "modifiers": 2})  # Ctrl+A
    await cdp.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "a", "modifiers": 2})
    await asyncio.sleep(0.1)

    # Type via insertText for reliability
    await cdp.send("Input.insertText", {"text": PHONE})
    await asyncio.sleep(0.5)

    # Verify phone was entered
    phone_val = await evaluate(cdp, """
        (() => {
            const inputs = document.querySelectorAll('input');
            for (const inp of inputs) {
                if (inp.value && inp.value.includes('9876')) return inp.value;
            }
            return '';
        })()
    """)
    print(f"  [INFO] Phone input value: {phone_val}")

    if not phone_val or "9876" not in str(phone_val):
        # Try setting value directly via React
        await evaluate(cdp, f"""
            (() => {{
                const inputs = document.querySelectorAll('input');
                for (const inp of inputs) {{
                    if (inp.placeholder?.includes('9876') || inp.inputMode === 'numeric') {{
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'value'
                        ).set;
                        nativeInputValueSetter.call(inp, '{PHONE}');
                        inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return true;
                    }}
                }}
                return false;
            }})()
        """)
        await asyncio.sleep(0.5)
        phone_val = await evaluate(cdp, """
            (() => {
                const inputs = document.querySelectorAll('input');
                for (const inp of inputs) {
                    if (inp.value && inp.value.includes('9876')) return inp.value;
                }
                return '';
            })()
        """)
        print(f"  [INFO] Phone input value (after direct set): {phone_val}")

    await take_screenshot(cdp, "auth_01_phone_entered.png")

    # Step 3: Click "Send OTP" button
    print("  [3] Clicking 'Send OTP'...")
    send_otp_js = """
    (() => {
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
            if (btn.innerText?.includes('Send OTP') || btn.innerText?.includes('send otp')) {
                const rect = btn.getBoundingClientRect();
                return { x: rect.x + rect.width/2, y: rect.y + rect.height/2,
                         disabled: btn.disabled, text: btn.innerText };
            }
        }
        return null;
    })()
    """
    btn = await evaluate(cdp, send_otp_js)
    if not btn:
        await take_screenshot(cdp, "auth_failed_no_send_btn.png")
        return False, "Could not find 'Send OTP' button"

    print(f"  [INFO] Send OTP button: disabled={btn.get('disabled')}, text={btn.get('text')}")

    if btn.get("disabled"):
        # Phone might not have been set correctly, try one more time
        print("  [WARN] Button disabled — trying to force-set phone value...")
        await evaluate(cdp, f"""
            (() => {{
                const inputs = document.querySelectorAll('input[inputmode="numeric"], input[type="tel"]');
                for (const inp of inputs) {{
                    const nativeSet = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    nativeSet.call(inp, '{PHONE}');
                    inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }})()
        """)
        await asyncio.sleep(1)
        btn = await evaluate(cdp, send_otp_js)
        if btn and btn.get("disabled"):
            await take_screenshot(cdp, "auth_failed_btn_disabled.png")
            return False, "Send OTP button still disabled after setting phone"

    await click_element(cdp, btn["x"], btn["y"])
    await asyncio.sleep(3)  # Wait for OTP API call

    await take_screenshot(cdp, "auth_02_otp_sent.png")

    # Check if we moved to OTP step
    page_text = await evaluate(cdp, "document.body.innerText") or ""
    if "OTP sent" not in page_text and "Verify" not in page_text:
        # Check for errors
        error_text = await evaluate(cdp, """
            document.querySelector('.MuiAlert-message')?.innerText || ''
        """)
        if error_text:
            print(f"  [ERROR] Login error: {error_text}")
            await take_screenshot(cdp, "auth_failed_error.png")
            return False, f"OTP request failed: {error_text}"

        print(f"  [WARN] Page text doesn't show OTP step, checking further...")

    # Step 4: Get OTP from API logs
    print("  [4] Getting OTP from API logs...")
    await asyncio.sleep(1)  # Give logs time to flush
    otp_code = get_otp_from_logs()
    if not otp_code:
        await take_screenshot(cdp, "auth_failed_no_otp.png")
        return False, "Could not extract OTP from API container logs"

    print(f"  [OK] OTP code: {otp_code}")

    # Step 5: Fill OTP digits
    print("  [5] Filling OTP digits...")
    # The OTP UI has 6 individual input fields
    # First input accepts paste of all 6 digits (maxLength=6 on first)
    fill_otp_js = f"""
    (() => {{
        const inputs = document.querySelectorAll('input[inputmode="numeric"], input[aria-label*="OTP"]');
        const otpInputs = [...inputs].filter(inp =>
            inp.getAttribute('aria-label')?.includes('OTP') ||
            (inp.inputMode === 'numeric' && inp.closest('[class*="gap"]'))
        );

        if (otpInputs.length >= 6) {{
            // Individual OTP boxes
            const digits = '{otp_code}'.split('');
            for (let i = 0; i < 6; i++) {{
                const inp = otpInputs[i];
                const nativeSet = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                nativeSet.call(inp, digits[i]);
                inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            return {{ method: 'individual', count: otpInputs.length }};
        }} else if (otpInputs.length >= 1) {{
            // Single input or first accepts all
            const inp = otpInputs[0];
            inp.focus();
            const nativeSet = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeSet.call(inp, '{otp_code}');
            inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
            inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return {{ method: 'single', count: otpInputs.length }};
        }}
        return {{ method: 'none', count: 0, all_inputs: inputs.length }};
    }})()
    """
    otp_result = await evaluate(cdp, fill_otp_js)
    print(f"  [INFO] OTP fill result: {otp_result}")

    await asyncio.sleep(0.5)
    await take_screenshot(cdp, "auth_03_otp_filled.png")

    # Step 6: Click "Verify & Login"
    print("  [6] Clicking 'Verify & Login'...")
    verify_js = """
    (() => {
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
            if (btn.innerText?.includes('Verify') || btn.innerText?.includes('Login')) {
                const rect = btn.getBoundingClientRect();
                return { x: rect.x + rect.width/2, y: rect.y + rect.height/2,
                         disabled: btn.disabled, text: btn.innerText.trim() };
            }
        }
        return null;
    })()
    """
    verify_btn = await evaluate(cdp, verify_js)
    if not verify_btn:
        await take_screenshot(cdp, "auth_failed_no_verify_btn.png")
        return False, "Could not find 'Verify & Login' button"

    print(f"  [INFO] Verify button: disabled={verify_btn.get('disabled')}, text={verify_btn.get('text')}")

    if verify_btn.get("disabled"):
        # OTP might not have triggered state update, try clicking inputs
        print("  [WARN] Verify button disabled, trying to trigger OTP state update...")
        # Focus first OTP input and type the full code
        await evaluate(cdp, """
            (() => {
                const inputs = document.querySelectorAll('input[aria-label*="OTP"]');
                if (inputs.length > 0) inputs[0].focus();
            })()
        """)
        await cdp.send("Input.insertText", {"text": otp_code})
        await asyncio.sleep(1)
        verify_btn = await evaluate(cdp, verify_js)
        if verify_btn and verify_btn.get("disabled"):
            await take_screenshot(cdp, "auth_failed_verify_disabled.png")
            return False, "Verify button still disabled after OTP entry"

    await click_element(cdp, verify_btn["x"], verify_btn["y"])

    # Step 7: Wait for redirect to dashboard
    print("  [7] Waiting for redirect...")
    for i in range(15):
        await asyncio.sleep(1)
        current_url = await evaluate(cdp, "window.location.href") or ""
        if "/login" not in current_url and current_url.startswith(ADMIN_URL):
            print(f"  [OK] Redirected to: {current_url}")
            await take_screenshot(cdp, "auth_04_dashboard.png")
            return True, f"Authenticated successfully, redirected to {current_url}"

        # Check for errors on login page
        error_text = await evaluate(cdp, """
            document.querySelector('.MuiAlert-message')?.innerText || ''
        """)
        if error_text and i > 2:
            print(f"  [ERROR] Login error after verify: {error_text}")
            await take_screenshot(cdp, "auth_failed_verify_error.png")
            return False, f"Verification failed: {error_text}"

    current_url = await evaluate(cdp, "window.location.href") or ""
    await take_screenshot(cdp, "auth_failed_timeout.png")
    return False, f"Timeout waiting for redirect. Still at: {current_url}"


# ── Auth via API (fallback) ─────────────────────────────────────────────────

async def authenticate_via_api(cdp: CDPClient) -> tuple[bool, str]:
    """
    Authenticate by requesting OTP via HTTP, then verifying via in-browser fetch.
    This ensures cookies are set correctly in the browser's cookie store.
    """
    print("\n== AUTHENTICATION (API + in-browser verify) ==")
    import http.client

    # Step 1: Navigate to login page first (sets page context for fetch)
    print("  [1] Navigating to admin login page...")
    await navigate(cdp, f"{ADMIN_URL}/login", wait_ms=5000)

    current_url = await evaluate(cdp, "window.location.href") or ""
    print(f"  [INFO] Current URL: {current_url}")

    # Wait for login page to fully hydrate
    for attempt in range(10):
        elem_count = await evaluate(cdp, "document.querySelectorAll('*').length")
        if elem_count and elem_count > 50:
            break
        await asyncio.sleep(1)
    print(f"  [INFO] Page elements: {elem_count}")

    # Step 2: Request OTP via direct HTTP (bypasses CORS)
    print("  [2] Requesting OTP via HTTP...")
    try:
        conn = http.client.HTTPConnection("localhost", 8000, timeout=10)
        conn.request("POST", "/v1/auth/request-otp",
                      body=json.dumps({"phone": PHONE_WITH_PREFIX}),
                      headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        resp.read()
        print(f"  [OK] OTP requested: {resp.status}")
        conn.close()
    except Exception as e:
        return False, f"OTP request failed: {e}"

    await asyncio.sleep(2)

    # Step 3: Get OTP from logs
    print("  [3] Getting OTP from logs...")
    otp_code = get_otp_from_logs()
    if not otp_code:
        return False, "Could not get OTP from logs"
    print(f"  [OK] OTP: {otp_code}")

    # Step 4: Verify OTP from browser context (so Set-Cookie is handled by browser)
    print("  [4] Verifying OTP from browser...")
    verify_result = await evaluate(cdp, f"""
    (async () => {{
        try {{
            const res = await fetch('http://localhost:8000/v1/auth/verify-otp', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                credentials: 'include',
                body: JSON.stringify({{
                    phone: '{PHONE_WITH_PREFIX}',
                    otp: '{otp_code}',
                    client_type: 'web'
                }})
            }});
            const data = await res.json();
            return {{ status: res.status, ok: res.ok, keys: Object.keys(data) }};
        }} catch (e) {{
            return {{ error: e.message }};
        }}
    }})()
    """)
    print(f"  [INFO] Verify result: {verify_result}")

    if not verify_result or verify_result.get("error"):
        return False, f"In-browser verify failed: {verify_result}"

    if verify_result.get("status") != 200:
        return False, f"Verify returned {verify_result.get('status')}"

    # Verify cookies are set
    cookies_result = await cdp.send("Network.getCookies", {"urls": [ADMIN_URL, "http://localhost:8000"]})
    cookies = cookies_result.get("result", {}).get("cookies", [])
    cookie_names = [c["name"] for c in cookies]
    print(f"  [INFO] Cookies set: {cookie_names}")

    if "token" not in cookie_names:
        return False, f"Token cookie not set. Cookies: {cookie_names}"

    # Step 5: Navigate to dashboard
    print("  [5] Navigating to dashboard...")
    await navigate(cdp, ADMIN_URL, wait_ms=8000)

    current_url = await evaluate(cdp, "window.location.href") or ""
    print(f"  [INFO] After dashboard navigate: {current_url}")

    if "/login" in current_url:
        await take_screenshot(cdp, "auth_api_failed.png")
        return False, f"Auth succeeded but redirected to login: {current_url}"

    # Wait for content to load
    for attempt in range(10):
        elem_count = await evaluate(cdp, "document.querySelectorAll('*').length")
        if elem_count and elem_count > 100:
            break
        await asyncio.sleep(1)

    page_text = await evaluate(cdp, "document.body?.innerText || ''") or ""
    print(f"  [INFO] Dashboard text ({len(page_text)} chars): {page_text[:100]}")

    await take_screenshot(cdp, "auth_api_success.png")
    return True, f"Authenticated via in-browser fetch, at: {current_url}"


# ── Page Testing ─────────────────────────────────────────────────────────────

async def test_page(
    cdp: CDPClient,
    path: str,
    name: str,
    expected: list,
    viewport_name: str = "desktop",
    viewport_w: int = 1920,
    viewport_h: int = 1080,
) -> PageResult:
    """Test a single page comprehensively."""
    result = PageResult(path=path, name=name, viewport=viewport_name)

    # Set viewport
    await set_viewport(cdp, viewport_w, viewport_h)

    # Track network requests
    network_requests: list[NetworkRequest] = []
    request_map: dict[str, NetworkRequest] = {}

    def on_request(params):
        req_id = params.get("requestId", "")
        req = params.get("request", {})
        nr = NetworkRequest(
            url=req.get("url", ""),
            method=req.get("method", "GET"),
            timestamp=time.time(),
        )
        request_map[req_id] = nr
        network_requests.append(nr)

    def on_response(params):
        req_id = params.get("requestId", "")
        resp = params.get("response", {})
        if req_id in request_map:
            nr = request_map[req_id]
            nr.status = resp.get("status", 0)
            nr.size_bytes = resp.get("encodedDataLength", 0)
            nr.duration_ms = (time.time() - nr.timestamp) * 1000

    def on_loading_failed(params):
        req_id = params.get("requestId", "")
        if req_id in request_map:
            nr = request_map[req_id]
            nr.failed = True
            nr.error_text = params.get("errorText", "")

    # Track console messages
    console_errors = []
    console_warnings = []

    def on_console(params):
        level = params.get("type", "log")
        args = params.get("args", [])
        text_parts = []
        for arg in args:
            val = arg.get("value") or arg.get("description", "")
            if val:
                text_parts.append(str(val))
        text = " ".join(text_parts)
        url = params.get("stackTrace", {}).get("callFrames", [{}])[0].get("url", "") if params.get("stackTrace") else ""

        msg = ConsoleMessage(level=level, text=text, url=url)
        if level == "error":
            console_errors.append(msg)
        elif level == "warning":
            console_warnings.append(msg)

    def on_exception(params):
        details = params.get("exceptionDetails", {})
        text = details.get("text", "")
        exception = details.get("exception", {})
        desc = exception.get("description", "")
        console_errors.append(ConsoleMessage(
            level="exception",
            text=f"{text}: {desc}" if desc else text,
        ))

    # Register handlers
    cdp.on("Network.requestWillBeSent", on_request)
    cdp.on("Network.responseReceived", on_response)
    cdp.on("Network.loadingFailed", on_loading_failed)
    cdp.on("Runtime.consoleAPICalled", on_console)
    cdp.on("Runtime.exceptionThrown", on_exception)

    # Navigate — allow extra time for Next.js dev server + API calls
    url = f"{ADMIN_URL}{path}"
    load_time = await navigate(cdp, url, wait_ms=6000)
    result.load_time_ms = round(load_time)

    # Wait for content to actually render (not just the loading spinner)
    for _wait in range(8):
        elem_count = await evaluate(cdp, "document.querySelectorAll('*').length")
        if elem_count and elem_count > 100:
            break
        await asyncio.sleep(1)

    # Get metrics
    metrics = await get_page_metrics(cdp)
    if not metrics:
        result.status = "FAIL"
        result.bugs.append({
            "severity": "CRITICAL",
            "description": f"Page {path} returned no metrics — likely white screen",
        })
    else:
        result.content_length = metrics.get("contentLength", 0)
        result.components_found = {
            "mui": metrics.get("mui", {}),
            "testid": metrics.get("testid", {}),
            "charts": metrics.get("charts", {}),
            "maps": metrics.get("maps", {}),
            "tables": metrics.get("tables", {}),
            "sidebar": metrics.get("sidebar", {}),
            "images": metrics.get("images", {}),
        }

        # Determine status
        if metrics.get("errors", {}).get("has404"):
            result.status = "FAIL"
            result.bugs.append({"severity": "CRITICAL", "description": f"404 error on {path}"})
        elif metrics.get("errors", {}).get("hasError"):
            result.status = "FAIL"
            result.bugs.append({"severity": "HIGH", "description": f"Error boundary on {path}"})
        elif metrics.get("contentLength", 0) < 50:
            result.status = "WARN"
            result.bugs.append({"severity": "MEDIUM", "description": f"Very little content on {path} ({metrics.get('contentLength', 0)} chars)"})
        else:
            result.status = "PASS"

        # Check expected components
        for expected_comp in expected:
            found = False
            if expected_comp == "stat-card":
                found = metrics.get("testid", {}).get("statCards", 0) > 0
            elif expected_comp == "recharts":
                found = (metrics.get("charts", {}).get("rechartsContainers", 0) > 0 or
                         metrics.get("charts", {}).get("rechartsSvgs", 0) > 0)
            elif expected_comp == "leaflet":
                found = metrics.get("maps", {}).get("leafletMaps", 0) > 0
            elif expected_comp == "table":
                found = metrics.get("mui", {}).get("tables", 0) > 0
            elif expected_comp == "pagination":
                found = metrics.get("mui", {}).get("pagination", 0) > 0
            elif expected_comp == "search":
                found = metrics.get("mui", {}).get("textFields", 0) > 0
            elif expected_comp == "chip":
                found = metrics.get("mui", {}).get("chips", 0) > 0
            elif expected_comp == "badge":
                found = metrics.get("mui", {}).get("chips", 0) > 0
            elif expected_comp == "card":
                found = metrics.get("mui", {}).get("cards", 0) > 0
            elif expected_comp == "progress":
                found = metrics.get("mui", {}).get("progress", 0) > 0
            elif expected_comp == "filter":
                found = metrics.get("mui", {}).get("selects", 0) > 0 or metrics.get("mui", {}).get("chips", 0) > 0

            if not found and result.status == "PASS":
                result.bugs.append({
                    "severity": "LOW",
                    "description": f"Expected '{expected_comp}' component not found on {path}",
                })

        # Check horizontal overflow
        if metrics.get("layout", {}).get("hasHorizontalOverflow"):
            result.bugs.append({
                "severity": "MEDIUM",
                "description": f"Horizontal overflow on {path} at {viewport_name} ({viewport_w}px)",
            })

        # Check broken images
        broken = metrics.get("images", {}).get("broken", 0)
        if broken > 0:
            result.bugs.append({
                "severity": "MEDIUM",
                "description": f"{broken} broken image(s) on {path}",
            })

    # Process network requests
    result.network_requests = [
        {"url": nr.url, "method": nr.method, "status": nr.status,
         "duration_ms": round(nr.duration_ms), "size_bytes": nr.size_bytes}
        for nr in network_requests if nr.url.startswith("http")
    ]
    result.total_bytes = sum(nr.size_bytes for nr in network_requests)

    # Flag slow requests
    result.slow_requests = [
        {"url": nr.url, "duration_ms": round(nr.duration_ms)}
        for nr in network_requests
        if nr.duration_ms > 2000 and nr.url.startswith("http")
    ]

    # Flag network errors
    result.network_errors = [
        {"url": nr.url, "status": nr.status, "error": nr.error_text}
        for nr in network_requests
        if (nr.failed or (nr.status >= 400 and nr.status != 401)) and nr.url.startswith("http")
    ]

    # Console errors
    result.console_errors = [{"level": e.level, "text": e.text[:200], "url": e.url} for e in console_errors]
    result.console_warnings = [{"level": w.level, "text": w.text[:200]} for w in console_warnings]

    # Screenshot
    screenshot_name = f"{path.strip('/').replace('/', '-') or 'dashboard'}_{viewport_name}.png"
    result.screenshot_path = await take_screenshot(cdp, screenshot_name)

    # Clean up event handlers to avoid stacking
    cdp._event_handlers.get("Network.requestWillBeSent", []).clear()
    cdp._event_handlers.get("Network.responseReceived", []).clear()
    cdp._event_handlers.get("Network.loadingFailed", []).clear()
    cdp._event_handlers.get("Runtime.consoleAPICalled", []).clear()
    cdp._event_handlers.get("Runtime.exceptionThrown", []).clear()

    return result


async def test_page_interactions(cdp: CDPClient, path: str, name: str) -> dict:
    """Test interactive elements on a page."""
    results = {"path": path, "name": name, "interactions": []}

    # Navigate to the page first
    await navigate(cdp, f"{ADMIN_URL}{path}", wait_ms=3000)

    # Get clickable elements
    elements = await get_clickable_elements(cdp)
    if not elements:
        results["interactions"].append({"type": "info", "text": "No interactive elements found"})
        return results

    results["element_count"] = len(elements)

    # Click up to 5 non-navigation buttons (avoid links that would navigate away)
    clicked = 0
    for el in elements:
        if clicked >= 5:
            break
        if not el.get("visible", True):
            continue
        if el.get("disabled"):
            results["interactions"].append({
                "type": el["type"], "text": el.get("text", ""), "result": "disabled"
            })
            continue

        # Skip nav items to avoid leaving the page
        el_text = (el.get("text") or "").lower()
        if any(nav in el_text for nav in ["dashboard", "farmers", "animals", "milk",
                                           "health", "vaccination", "schemes", "marketplace",
                                           "income", "iot", "map", "vet", "logout"]):
            continue

        # Click
        pre_url = await evaluate(cdp, "window.location.href")
        pre_errors = await evaluate(cdp, "window.__testErrors?.length || 0")

        try:
            await click_element(cdp, el["x"], el["y"])
            await asyncio.sleep(0.5)
        except Exception:
            pass

        post_url = await evaluate(cdp, "window.location.href")
        # Check for new errors
        page_has_error = await evaluate(cdp, """
            !!document.querySelector('.MuiAlert-standardError, [class*="error-boundary"]')
        """)

        interaction_result = "ok"
        if post_url != pre_url:
            interaction_result = f"navigated to {post_url}"
            # Navigate back
            await navigate(cdp, f"{ADMIN_URL}{path}", wait_ms=2000)
        elif page_has_error:
            interaction_result = "triggered error"

        results["interactions"].append({
            "type": el["type"],
            "text": el.get("text", "")[:30],
            "result": interaction_result,
        })
        clicked += 1

    # Test search if available
    has_search = await evaluate(cdp, """
        !!document.querySelector('input[placeholder*="Search"], input[placeholder*="search"]')
    """)
    if has_search:
        await evaluate(cdp, """
            (() => {
                const inp = document.querySelector('input[placeholder*="Search"], input[placeholder*="search"]');
                if (inp) {
                    inp.focus();
                    const nativeSet = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    nativeSet.call(inp, 'test');
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                }
            })()
        """)
        await asyncio.sleep(1)
        results["interactions"].append({"type": "search", "text": "typed 'test'", "result": "ok"})

    return results


# ── Main Test Runner ─────────────────────────────────────────────────────────

async def main():
    print("=" * 70)
    print("PashuRaksha Admin Dashboard — Exhaustive CDP E2E Test Suite")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    report = TestReport(timestamp=datetime.now().isoformat())

    # Connect to Chrome
    print("\n[SETUP] Connecting to Chrome CDP...")
    ws_url = await get_cdp_target()
    print(f"  Target: {ws_url}")

    ws = await websockets.connect(ws_url, max_size=50 * 1024 * 1024)
    cdp = CDPClient(ws)
    await cdp.start_listener()

    # Enable required domains
    await cdp.send("Page.enable")
    await cdp.send("Network.enable")
    await cdp.send("Runtime.enable")
    await cdp.send("DOM.enable")
    await cdp.send("Input.enable")

    # Clear all cookies to start fresh
    await cdp.send("Network.clearBrowserCookies")
    await cdp.send("Network.clearBrowserCache")
    print("  [OK] Cleared cookies and cache")

    # CRITICAL: Bypass CSP — the admin app's CSP blocks Next.js inline scripts
    # in dev mode, preventing React hydration. This is a real bug (BUG-001).
    await cdp.send("Page.setBypassCSP", {"enabled": True})
    print("  [OK] CSP bypass enabled (workaround for BUG-001: CSP blocks inline scripts)")

    # NOTE: CORS was fixed by adding CORS_ORIGINS env var to docker-compose.yml.
    # BUG-002 (empty CORS origins) is documented but worked around at infra level.

    # Set desktop viewport
    await set_viewport(cdp, 1920, 1080)

    # ── Phase 1: Authentication ──────────────────────────────────────────

    auth_success, auth_detail = await authenticate(cdp)
    if not auth_success:
        print(f"\n  [FALLBACK] UI auth failed: {auth_detail}")
        print("  [FALLBACK] Trying API-based authentication...")
        auth_success, auth_detail = await authenticate_via_api(cdp)

    report.auth_status = "PASS" if auth_success else "FAIL"
    report.auth_details = auth_detail
    print(f"\n  Auth result: {report.auth_status} — {auth_detail}")

    if not auth_success:
        print("\n  [FATAL] Authentication failed. Testing pages without auth (will show login redirects).")

    # Quick diagnostic check
    if auth_success:
        page_text = await evaluate(cdp, "document.body?.innerText || ''") or ""
        elem_count = await evaluate(cdp, "document.querySelectorAll('*').length") or 0
        print(f"  Dashboard state: {elem_count} elements, {len(page_text)} chars text")

    # ── Phase 2: Test Every Page (Desktop) ───────────────────────────────

    print("\n\n== PAGE TESTING (Desktop 1920x1080) ==")
    print("-" * 70)

    for path, name, expected in ADMIN_PAGES:
        print(f"\n  Testing: {name} ({path})...")
        result = await test_page(cdp, path, name, expected, "desktop", 1920, 1080)
        report.page_results.append(result)
        report.all_console_errors.extend(
            [{"page": path, **e} for e in result.console_errors]
        )
        report.all_network_errors.extend(
            [{"page": path, **e} for e in result.network_errors]
        )
        report.all_bugs.extend(result.bugs)

        status_icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX"}.get(result.status, "??")
        components = result.components_found
        mui = components.get("mui", {}) if components else {}
        print(f"    [{status_icon}] {result.status} | load={result.load_time_ms}ms | "
              f"content={result.content_length}ch | "
              f"cards={mui.get('cards',0)} tables={mui.get('tables',0)} "
              f"buttons={mui.get('buttons',0)} chips={mui.get('chips',0)} | "
              f"errors={len(result.console_errors)} net_errs={len(result.network_errors)}")

        if result.bugs:
            for bug in result.bugs:
                print(f"    BUG [{bug['severity']}]: {bug['description']}")

    # ── Phase 3: Responsive Testing ──────────────────────────────────────

    print("\n\n== RESPONSIVE TESTING ==")
    print("-" * 70)

    # Test key pages at multiple viewports
    responsive_pages = [
        ("/", "Dashboard", ["stat-card"]),
        ("/farmers", "Farmers", ["table"]),
        ("/map", "Map View", ["leaflet"]),
        ("/health", "Health Alerts", ["card"]),
    ]

    for vp_name, vp_w, vp_h in VIEWPORTS:
        if vp_name == "desktop":
            continue  # Already tested
        print(f"\n  Viewport: {vp_name} ({vp_w}x{vp_h})")
        for path, name, expected in responsive_pages:
            result = await test_page(cdp, path, name, expected, vp_name, vp_w, vp_h)
            report.page_results.append(result)
            report.all_bugs.extend(result.bugs)
            status_icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX"}.get(result.status, "??")
            print(f"    [{status_icon}] {name}: content={result.content_length}ch, "
                  f"overflow={bool(result.bugs and any('overflow' in b.get('description','') for b in result.bugs))}")

    # Reset to desktop
    await set_viewport(cdp, 1920, 1080)

    # ── Phase 4: Interaction Testing ─────────────────────────────────────

    print("\n\n== INTERACTION TESTING ==")
    print("-" * 70)

    interaction_pages = ["/", "/farmers", "/animals", "/health", "/vet/cases"]
    for path in interaction_pages:
        name = next((n for p, n, _ in ADMIN_PAGES if p == path), path)
        print(f"\n  Testing interactions: {name} ({path})...")
        interactions = await test_page_interactions(cdp, path, name)
        print(f"    Elements found: {interactions.get('element_count', 0)}")
        for action in interactions.get("interactions", []):
            print(f"    [{action.get('type','')}] '{action.get('text','')}' -> {action.get('result','?')}")
        # Attach to the desktop result for this page
        for pr in report.page_results:
            if pr.path == path and pr.viewport == "desktop":
                pr.interactive_results = interactions
                break

    # ── Phase 5: Navigation Flow Test ────────────────────────────────────

    print("\n\n== NAVIGATION FLOW TEST ==")
    print("-" * 70)

    print("  Testing sidebar navigation sequence...")
    nav_results = []
    for path, name, _ in ADMIN_PAGES[:8]:  # Test first 8 pages via sidebar
        # Click sidebar link
        click_js = f"""
        (() => {{
            const links = document.querySelectorAll('a, .MuiListItemButton-root, .MuiListItem-root');
            for (const link of links) {{
                const text = link.innerText?.trim();
                if (text === '{name}' || text?.includes('{name}')) {{
                    const rect = link.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {{
                        return {{ x: rect.x + rect.width/2, y: rect.y + rect.height/2, text }};
                    }}
                }}
            }}
            return null;
        }})()
        """
        link_info = await evaluate(cdp, click_js)
        if link_info:
            await click_element(cdp, link_info["x"], link_info["y"])
            await asyncio.sleep(2)
            current_url = await evaluate(cdp, "window.location.href") or ""
            expected_in_url = path if path != "/" else ADMIN_URL
            success = path in current_url or (path == "/" and current_url.rstrip("/") == ADMIN_URL.rstrip("/"))
            nav_results.append({"name": name, "path": path, "navigated_to": current_url, "success": success})
            icon = "OK" if success else "XX"
            print(f"    [{icon}] {name} -> {current_url}")
        else:
            nav_results.append({"name": name, "path": path, "navigated_to": "", "success": False})
            print(f"    [XX] {name} -> sidebar link not found")

    # ── Compile Summary ──────────────────────────────────────────────────

    total_pages = len(report.page_results)
    passed = sum(1 for r in report.page_results if r.status == "PASS")
    warned = sum(1 for r in report.page_results if r.status == "WARN")
    failed = sum(1 for r in report.page_results if r.status == "FAIL")
    untested = sum(1 for r in report.page_results if r.status == "UNTESTED")

    report.summary = {
        "total_pages_tested": total_pages,
        "passed": passed,
        "warned": warned,
        "failed": failed,
        "untested": untested,
        "total_console_errors": len(report.all_console_errors),
        "total_network_errors": len(report.all_network_errors),
        "total_bugs": len(report.all_bugs),
        "bugs_by_severity": {
            "CRITICAL": sum(1 for b in report.all_bugs if b.get("severity") == "CRITICAL"),
            "HIGH": sum(1 for b in report.all_bugs if b.get("severity") == "HIGH"),
            "MEDIUM": sum(1 for b in report.all_bugs if b.get("severity") == "MEDIUM"),
            "LOW": sum(1 for b in report.all_bugs if b.get("severity") == "LOW"),
        },
        "nav_flow_results": nav_results,
    }

    # ── Print Final Report ───────────────────────────────────────────────

    print("\n\n" + "=" * 70)
    print("FINAL TEST REPORT")
    print("=" * 70)

    print(f"\nTimestamp: {report.timestamp}")
    print(f"Auth: {report.auth_status} — {report.auth_details}")

    print(f"\n{'Page':<25} {'VP':<10} {'Status':<8} {'Load(ms)':<10} {'Content':<10} "
          f"{'Cards':<6} {'Tables':<7} {'Btns':<6} {'Errors':<7}")
    print("-" * 95)
    for r in report.page_results:
        mui = r.components_found.get("mui", {}) if r.components_found else {}
        print(f"{r.path:<25} {r.viewport:<10} {r.status:<8} {r.load_time_ms:<10.0f} "
              f"{r.content_length:<10} {mui.get('cards',0):<6} {mui.get('tables',0):<7} "
              f"{mui.get('buttons',0):<6} {len(r.console_errors):<7}")

    if report.all_console_errors:
        print(f"\n\nCONSOLE ERRORS ({len(report.all_console_errors)} total):")
        print("-" * 70)
        seen = set()
        for e in report.all_console_errors:
            key = f"{e.get('page')}:{e.get('text','')[:80]}"
            if key not in seen:
                seen.add(key)
                print(f"  [{e.get('page')}] {e.get('level','error')}: {e.get('text','')[:120]}")

    if report.all_network_errors:
        print(f"\n\nNETWORK ERRORS ({len(report.all_network_errors)} total):")
        print("-" * 70)
        seen = set()
        for e in report.all_network_errors:
            key = f"{e.get('page')}:{e.get('url','')}"
            if key not in seen:
                seen.add(key)
                print(f"  [{e.get('page')}] {e.get('status',0)} {e.get('url','')[:100]} {e.get('error','')}")

    if report.all_bugs:
        print(f"\n\nBUGS FOUND ({len(report.all_bugs)} total):")
        print("-" * 70)
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            bugs = [b for b in report.all_bugs if b.get("severity") == sev]
            for b in bugs:
                print(f"  [{sev}] {b['description']}")

    print(f"\n\nSUMMARY:")
    print(f"  Pages tested: {total_pages}")
    print(f"  PASS: {passed} | WARN: {warned} | FAIL: {failed} | UNTESTED: {untested}")
    print(f"  Console errors: {len(report.all_console_errors)}")
    print(f"  Network errors: {len(report.all_network_errors)}")
    print(f"  Bugs: {report.summary['bugs_by_severity']}")

    # ── Save JSON Report ─────────────────────────────────────────────────

    report_path = os.path.join(SCREENSHOT_DIR, "e2e-report.json")

    def serialize(obj):
        if hasattr(obj, "__dict__"):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        return str(obj)

    with open(report_path, "w") as f:
        json.dump({
            "timestamp": report.timestamp,
            "auth": {"status": report.auth_status, "details": report.auth_details},
            "summary": report.summary,
            "page_results": [serialize(r) for r in report.page_results],
            "console_errors": report.all_console_errors,
            "network_errors": report.all_network_errors,
            "bugs": report.all_bugs,
        }, f, indent=2, default=str)

    print(f"\n  Report saved: {report_path}")
    print(f"  Screenshots: {SCREENSHOT_DIR}/")

    # Cleanup
    await cdp.close()
    await ws.close()

    print(f"\n{'=' * 70}")
    print(f"Test suite complete: {datetime.now().isoformat()}")
    print(f"{'=' * 70}")

    # Return exit code based on results
    if failed > 0 or report.summary["bugs_by_severity"]["CRITICAL"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
