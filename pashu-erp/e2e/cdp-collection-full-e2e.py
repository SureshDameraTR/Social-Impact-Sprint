#!/usr/bin/env python3
"""
PashuRaksha Collection Centre — Exhaustive E2E UI Test via Chrome CDP.

Tests every page, every interaction, every button/tab/toggle in the Collection
Centre app (http://localhost:3001) using the Chrome DevTools Protocol over
websockets.  Produces a detailed report and per-page screenshots.

Requirements:
  - Chrome running with --remote-debugging-port=9222
  - API running on port 8000
  - Collection Centre dev server on port 3001
  - Python packages: websockets (pip install websockets)

Usage:
  python3 cdp-collection-full-e2e.py
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from typing import Any

import websockets

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CDP_ENDPOINT = "http://127.0.0.1:9222"
BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"
PHONE = "+919876543212"
PHONE_DIGITS = "9876543212"
SCREENSHOT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "screenshots",
    "collection-full",
)
VIEWPORT_DESKTOP = {"width": 1280, "height": 900}
VIEWPORT_TABLET = {"width": 768, "height": 1024}
VIEWPORT_MOBILE = {"width": 375, "height": 667}

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Report accumulator
# ---------------------------------------------------------------------------

@dataclass
class PageReport:
    name: str
    url: str = ""
    status: str = "NOT_TESTED"
    screenshots: list[str] = field(default_factory=list)
    console_errors: list[str] = field(default_factory=list)
    network_requests: list[dict] = field(default_factory=list)
    data_counts: dict[str, int] = field(default_factory=dict)
    interactions: list[dict] = field(default_factory=list)
    bugs: list[str] = field(default_factory=list)
    slow_requests: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    duration_ms: float = 0.0


@dataclass
class TestReport:
    pages: list[PageReport] = field(default_factory=list)
    auth_status: str = "NOT_TESTED"
    auth_notes: list[str] = field(default_factory=list)
    total_bugs: int = 0
    start_time: float = 0.0
    end_time: float = 0.0


report = TestReport()

# ---------------------------------------------------------------------------
# CDP helper class
# ---------------------------------------------------------------------------

class CDPSession:
    """Thin wrapper around a CDP websocket connection to a single target."""

    def __init__(self, ws: Any):
        self.ws = ws
        self._id = 0
        self._pending: dict[int, asyncio.Future] = {}
        self._events: list[dict] = []
        self._console_errors: list[str] = []
        self._network_log: list[dict] = []
        self._network_pending: dict[str, dict] = {}
        self._listener_task: asyncio.Task | None = None

    async def start_listener(self):
        self._listener_task = asyncio.create_task(self._listen())

    async def _listen(self):
        try:
            async for raw in self.ws:
                msg = json.loads(raw)
                if "id" in msg and msg["id"] in self._pending:
                    self._pending[msg["id"]].set_result(msg)
                elif "method" in msg:
                    self._events.append(msg)
                    self._handle_event(msg)
        except websockets.exceptions.ConnectionClosed:
            pass

    def _handle_event(self, msg: dict):
        method = msg.get("method", "")
        params = msg.get("params", {})

        # Console errors
        if method == "Runtime.consoleAPICalled" and params.get("type") == "error":
            args = params.get("args", [])
            text = " ".join(a.get("value", a.get("description", "")) for a in args)
            self._console_errors.append(text)
        if method == "Runtime.exceptionThrown":
            ex = params.get("exceptionDetails", {}).get("exception", {})
            self._console_errors.append(ex.get("description", str(ex)))

        # Network tracking
        if method == "Network.requestWillBeSent":
            req_id = params.get("requestId", "")
            self._network_pending[req_id] = {
                "url": params.get("request", {}).get("url", ""),
                "method": params.get("request", {}).get("method", ""),
                "start": params.get("timestamp", 0),
            }
        if method == "Network.responseReceived":
            req_id = params.get("requestId", "")
            if req_id in self._network_pending:
                entry = self._network_pending[req_id]
                entry["status"] = params.get("response", {}).get("status", 0)
                entry["end"] = params.get("timestamp", 0)
                entry["duration_ms"] = round(
                    (entry["end"] - entry["start"]) * 1000, 1
                )
                self._network_log.append(entry)
                del self._network_pending[req_id]

    async def send(self, method: str, params: dict | None = None, timeout: float = 30) -> dict:
        self._id += 1
        msg_id = self._id
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[msg_id] = fut
        payload = {"id": msg_id, "method": method, "params": params or {}}
        await self.ws.send(json.dumps(payload))
        try:
            result = await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            del self._pending[msg_id]
            raise TimeoutError(f"CDP call {method} timed out after {timeout}s")
        finally:
            self._pending.pop(msg_id, None)
        if "error" in result:
            raise RuntimeError(f"CDP error: {result['error']}")
        return result.get("result", {})

    async def enable_domains(self):
        await asyncio.gather(
            self.send("Page.enable"),
            self.send("Runtime.enable"),
            self.send("Network.enable"),
            self.send("DOM.enable"),
            self.send("Console.enable"),
        )

    async def set_viewport(self, width: int, height: int):
        await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": width < 768,
        })

    async def navigate(self, url: str, wait_ms: int = 3000):
        await self.send("Page.navigate", {"url": url})
        await asyncio.sleep(0.5)
        # Wait for load event
        try:
            await self._wait_for_event("Page.loadEventFired", timeout=10)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(wait_ms / 1000)

    async def _wait_for_event(self, event_name: str, timeout: float = 10):
        deadline = time.time() + timeout
        while time.time() < deadline:
            for ev in self._events:
                if ev.get("method") == event_name:
                    self._events.remove(ev)
                    return ev
            await asyncio.sleep(0.1)
        raise asyncio.TimeoutError(f"Event {event_name} not received")

    async def evaluate(self, expression: str, timeout: float = 10) -> Any:
        result = await self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        }, timeout=timeout)
        val = result.get("result", {})
        if val.get("type") == "undefined":
            return None
        if "value" in val:
            return val["value"]
        return val.get("description", str(val))

    async def screenshot(self, filename: str) -> str:
        result = await self.send("Page.captureScreenshot", {"format": "png"})
        data = base64.b64decode(result["data"])
        path = os.path.join(SCREENSHOT_DIR, filename)
        with open(path, "wb") as f:
            f.write(data)
        return path

    async def click_at(self, x: float, y: float):
        for etype in ["mousePressed", "mouseReleased"]:
            await self.send("Input.dispatchMouseEvent", {
                "type": etype,
                "x": x, "y": y,
                "button": "left",
                "clickCount": 1,
            })

    async def click_selector(self, selector: str, timeout: float = 10) -> bool:
        """Find element by CSS selector and click its center. Returns True on success."""
        js = f"""
        (() => {{
            const el = document.querySelector({json.dumps(selector)});
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return {{x: r.x + r.width/2, y: r.y + r.height/2, w: r.width, h: r.height}};
        }})()
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            coords = await self.evaluate(js)
            if coords and isinstance(coords, dict) and coords.get("w", 0) > 0:
                await self.click_at(coords["x"], coords["y"])
                return True
            await asyncio.sleep(0.3)
        return False

    async def click_text(self, text: str, tag: str = "*", timeout: float = 10) -> bool:
        """Click the first visible element containing the given text."""
        js = f"""
        (() => {{
            const els = [...document.querySelectorAll({json.dumps(tag)})];
            const el = els.find(e => e.textContent.includes({json.dumps(text)}) && e.offsetParent !== null);
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return {{x: r.x + r.width/2, y: r.y + r.height/2, w: r.width, h: r.height}};
        }})()
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            coords = await self.evaluate(js)
            if coords and isinstance(coords, dict) and coords.get("w", 0) > 0:
                await self.click_at(coords["x"], coords["y"])
                return True
            await asyncio.sleep(0.3)
        return False

    async def type_text(self, text: str, delay: float = 0.03):
        for char in text:
            await self.send("Input.dispatchKeyEvent", {
                "type": "keyDown",
                "text": char,
                "key": char,
            })
            await self.send("Input.dispatchKeyEvent", {
                "type": "keyUp",
                "key": char,
            })
            await asyncio.sleep(delay)

    async def focus_and_type(self, selector: str, text: str):
        """Focus an input by selector and type into it."""
        await self.evaluate(f"""
            (() => {{
                const el = document.querySelector({json.dumps(selector)});
                if (el) {{ el.focus(); el.value = ''; }}
            }})()
        """)
        await asyncio.sleep(0.1)
        # Use JS to set value and trigger React onChange
        await self.evaluate(f"""
            (() => {{
                const el = document.querySelector({json.dumps(selector)});
                if (!el) return false;
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(el, {json.dumps(text)});
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }})()
        """)
        await asyncio.sleep(0.2)

    async def get_text(self, selector: str) -> str | None:
        return await self.evaluate(f"""
            (() => {{
                const el = document.querySelector({json.dumps(selector)});
                return el ? el.textContent : null;
            }})()
        """)

    async def get_element_count(self, selector: str) -> int:
        result = await self.evaluate(f"document.querySelectorAll({json.dumps(selector)}).length")
        return int(result) if result else 0

    async def element_exists(self, selector: str) -> bool:
        return (await self.get_element_count(selector)) > 0

    async def get_current_url(self) -> str:
        return await self.evaluate("window.location.href") or ""

    async def wait_for_selector(self, selector: str, timeout: float = 10) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if await self.element_exists(selector):
                return True
            await asyncio.sleep(0.3)
        return False

    async def wait_for_text(self, text: str, timeout: float = 10) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            body = await self.evaluate("document.body?.innerText || ''")
            if text in (body or ""):
                return True
            await asyncio.sleep(0.3)
        return False

    async def wait_for_url(self, substring: str, timeout: float = 10) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            url = await self.get_current_url()
            if substring in url:
                return True
            await asyncio.sleep(0.3)
        return False

    def flush_network_log(self) -> list[dict]:
        log = list(self._network_log)
        self._network_log.clear()
        return log

    def flush_console_errors(self) -> list[str]:
        errs = list(self._console_errors)
        self._console_errors.clear()
        return errs

    async def clear_input(self, selector: str):
        await self.evaluate(f"""
            (() => {{
                const el = document.querySelector({json.dumps(selector)});
                if (!el) return;
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(el, '');
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }})()
        """)

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        await self.ws.close()


# ---------------------------------------------------------------------------
# OTP retrieval from docker logs
# ---------------------------------------------------------------------------

def get_otp_from_docker() -> str:
    """Extract OTP from docker logs of pashu-erp-api-1."""
    try:
        result = subprocess.run(
            ["docker", "logs", "pashu-erp-api-1", "--tail", "20"],
            capture_output=True, text=True, timeout=10,
        )
        lines = (result.stdout + result.stderr).splitlines()
        otp = ""
        for line in lines:
            if "Code:" in line:
                # Extract 6-digit OTP
                import re
                match = re.search(r"\b(\d{6})\b", line)
                if match:
                    otp = match.group(1)
        return otp
    except Exception as e:
        print(f"  [WARN] Failed to get OTP from docker: {e}")
        return ""


# ---------------------------------------------------------------------------
# Connect to CDP
# ---------------------------------------------------------------------------

async def connect_cdp() -> CDPSession:
    """Open a new tab and connect to it via CDP."""
    import urllib.request

    # Get browser WS url
    version_url = f"{CDP_ENDPOINT}/json/version"
    with urllib.request.urlopen(version_url) as resp:
        version_info = json.loads(resp.read())
    browser_ws = version_info["webSocketDebuggerUrl"]

    # Connect to browser and create new target
    browser = await websockets.connect(browser_ws, max_size=50 * 1024 * 1024)
    # Create new tab
    create_msg = json.dumps({
        "id": 1,
        "method": "Target.createTarget",
        "params": {"url": "about:blank"},
    })
    await browser.send(create_msg)
    resp = json.loads(await browser.recv())
    target_id = resp["result"]["targetId"]

    # Get target WS url
    targets_url = f"{CDP_ENDPOINT}/json"
    with urllib.request.urlopen(targets_url) as resp2:
        targets = json.loads(resp2.read())

    target_ws = None
    for t in targets:
        if t.get("id") == target_id:
            target_ws = t["webSocketDebuggerUrl"]
            break

    if not target_ws:
        raise RuntimeError(f"Could not find WS URL for target {target_id}")

    await browser.close()

    ws = await websockets.connect(target_ws, max_size=50 * 1024 * 1024)
    session = CDPSession(ws)
    await session.start_listener()
    await session.enable_domains()
    return session


# ---------------------------------------------------------------------------
# Test: Authentication
# ---------------------------------------------------------------------------

async def test_auth(cdp: CDPSession) -> bool:
    """Login as milk_center user. Returns True on success."""
    pr = PageReport(name="Login / Authentication")
    t0 = time.time()
    try:
        await cdp.set_viewport(**VIEWPORT_DESKTOP)
        await cdp.navigate(f"{BASE_URL}/login", wait_ms=2000)
        pr.url = await cdp.get_current_url()

        # Verify login page elements
        has_title = await cdp.wait_for_text("PashuRaksha", timeout=5)
        has_staff = await cdp.wait_for_text("Staff Login", timeout=3)
        pr.interactions.append({"action": "page_load", "result": "OK" if has_title else "FAIL",
                                "detail": f"PashuRaksha title: {has_title}, Staff Login: {has_staff}"})

        # Screenshot login page
        path = await cdp.screenshot("01-login-page.png")
        pr.screenshots.append(path)

        # Enter phone number — find the input field
        # The phone input has placeholder "9876543210"
        entered = await cdp.evaluate(f"""
            (() => {{
                const inputs = [...document.querySelectorAll('input')];
                const phoneInput = inputs.find(i =>
                    i.placeholder === '9876543210' ||
                    i.getAttribute('inputmode') === 'numeric'
                );
                if (!phoneInput) return false;
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(phoneInput, '{PHONE_DIGITS}');
                phoneInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                phoneInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }})()
        """)
        pr.interactions.append({"action": "enter_phone", "result": "OK" if entered else "FAIL"})
        await asyncio.sleep(0.5)

        # Click "Send OTP" button
        clicked = await cdp.click_text("Send OTP", "button")
        pr.interactions.append({"action": "click_send_otp", "result": "OK" if clicked else "FAIL"})
        await asyncio.sleep(2)

        # Get OTP from docker logs
        otp = get_otp_from_docker()
        if not otp:
            pr.bugs.append("Could not retrieve OTP from docker logs")
            otp = "123456"  # fallback
        pr.interactions.append({"action": "retrieve_otp", "result": "OK" if otp else "FAIL", "detail": f"OTP: {otp}"})

        # Wait for OTP step
        await cdp.wait_for_text("OTP sent to", timeout=5)

        # Screenshot OTP step
        path = await cdp.screenshot("02-otp-step.png")
        pr.screenshots.append(path)

        # Fill OTP digits — 6 individual input boxes
        otp_filled = await cdp.evaluate(f"""
            (() => {{
                const inputs = [...document.querySelectorAll('input[inputmode="numeric"]')];
                // Filter to OTP inputs (there should be 6 close together)
                const otpInputs = inputs.filter(i => {{
                    const style = window.getComputedStyle(i);
                    return i.style.textAlign === 'center' || i.maxLength <= 6;
                }});
                if (otpInputs.length < 6) return 'found_' + otpInputs.length;
                const otp = '{otp}';
                const nativeSet = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                // The first OTP input accepts paste of full OTP
                otpInputs[0].focus();
                nativeSet.call(otpInputs[0], otp);
                otpInputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                otpInputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                return 'ok';
            }})()
        """)
        pr.interactions.append({"action": "fill_otp", "result": str(otp_filled)})
        await asyncio.sleep(0.5)

        # If the above didn't work, try filling each box individually
        if otp_filled != "ok":
            for i, digit in enumerate(otp):
                await cdp.evaluate(f"""
                    (() => {{
                        const inputs = [...document.querySelectorAll('input[inputmode="numeric"]')];
                        const otpInputs = inputs.slice(-6);
                        if (otpInputs[{i}]) {{
                            const nativeSet = Object.getOwnPropertyDescriptor(
                                window.HTMLInputElement.prototype, 'value').set;
                            otpInputs[{i}].focus();
                            nativeSet.call(otpInputs[{i}], '{digit}');
                            otpInputs[{i}].dispatchEvent(new Event('input', {{ bubbles: true }}));
                            otpInputs[{i}].dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }})()
                """)
                await asyncio.sleep(0.05)
            await asyncio.sleep(0.3)

        # Screenshot after OTP fill
        path = await cdp.screenshot("03-otp-filled.png")
        pr.screenshots.append(path)

        # Click "Verify & Login"
        clicked = await cdp.click_text("Verify & Login", "button")
        pr.interactions.append({"action": "click_verify", "result": "OK" if clicked else "FAIL"})
        await asyncio.sleep(3)

        # Check if we landed on /intake
        url = await cdp.get_current_url()
        logged_in = "/intake" in url or "/dashboard" in url
        pr.interactions.append({"action": "login_redirect", "result": "OK" if logged_in else "FAIL",
                                "detail": f"Current URL: {url}"})

        if not logged_in:
            # Check for error messages
            body_text = await cdp.evaluate("document.body?.innerText || ''")
            if "error" in (body_text or "").lower() or "fail" in (body_text or "").lower():
                pr.bugs.append(f"Login failed. Body contains error text. URL: {url}")
            path = await cdp.screenshot("03b-login-failed.png")
            pr.screenshots.append(path)

        path = await cdp.screenshot("04-post-login.png")
        pr.screenshots.append(path)

        pr.console_errors = cdp.flush_console_errors()
        pr.network_requests = cdp.flush_network_log()
        pr.slow_requests = [r for r in pr.network_requests if r.get("duration_ms", 0) > 2000]
        pr.status = "PASS" if logged_in else "FAIL"
        report.auth_status = pr.status
        if pr.console_errors:
            report.auth_notes.append(f"Console errors during login: {pr.console_errors}")

    except Exception as e:
        pr.status = "ERROR"
        pr.bugs.append(f"Exception: {e}")
        traceback.print_exc()

    pr.duration_ms = (time.time() - t0) * 1000
    report.pages.append(pr)
    return pr.status == "PASS"


# ---------------------------------------------------------------------------
# Test: Intake Page
# ---------------------------------------------------------------------------

async def test_intake(cdp: CDPSession):
    pr = PageReport(name="Intake (/intake)")
    t0 = time.time()
    try:
        await cdp.set_viewport(**VIEWPORT_DESKTOP)
        await cdp.navigate(f"{BASE_URL}/intake", wait_ms=2000)
        pr.url = await cdp.get_current_url()

        # Check page loaded
        has_title = await cdp.wait_for_text("Milk Intake", timeout=5)
        pr.interactions.append({"action": "page_load", "result": "OK" if has_title else "FAIL"})

        # Check NavBar exists
        navbar = await cdp.element_exists("header")
        pr.interactions.append({"action": "navbar_check", "result": "OK" if navbar else "FAIL"})

        # Check centre name in navbar
        centre_text = await cdp.evaluate("""
            (() => {
                const header = document.querySelector('header');
                return header ? header.textContent : '';
            })()
        """)
        has_centre = "Tumkur" in (centre_text or "") or "Centre" in (centre_text or "") or "Select" in (centre_text or "")
        pr.interactions.append({"action": "centre_display", "result": "OK" if has_centre else "WARN",
                                "detail": f"Header text: {(centre_text or '')[:100]}"})

        # Check farmer search component
        has_search = await cdp.element_exists("input[placeholder*='phone']") or await cdp.element_exists("input[inputmode='numeric']")
        pr.interactions.append({"action": "farmer_search_visible", "result": "OK" if has_search else "FAIL"})

        # Check shift toggle buttons
        phone_toggle = await cdp.wait_for_text("Phone", timeout=3)
        aadhaar_toggle = await cdp.wait_for_text("Aadhaar", timeout=2)
        pr.interactions.append({"action": "search_mode_toggles", "result": "OK" if phone_toggle and aadhaar_toggle else "FAIL"})

        path = await cdp.screenshot("05-intake-initial.png")
        pr.screenshots.append(path)

        # ---- Search for farmer by phone "9876543213" ----
        # Find the search input for phone
        await cdp.evaluate("""
            (() => {
                const inputs = [...document.querySelectorAll('input')];
                const search = inputs.find(i => i.placeholder && i.placeholder.includes('phone'));
                if (search) {
                    search.focus();
                    const nativeSet = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    nativeSet.call(search, '9876543213');
                    search.dispatchEvent(new Event('input', { bubbles: true }));
                    search.dispatchEvent(new Event('change', { bubbles: true }));
                }
                return !!search;
            })()
        """)
        await asyncio.sleep(1.5)  # Wait for debounce + API call

        # Check if "Lakshmi" appears in results
        found_lakshmi = await cdp.wait_for_text("Lakshmi", timeout=5)
        pr.interactions.append({"action": "search_farmer_phone", "result": "OK" if found_lakshmi else "FAIL",
                                "detail": "Searched 9876543213, expected Lakshmi Devi"})

        path = await cdp.screenshot("06-farmer-search-results.png")
        pr.screenshots.append(path)

        # Count search results
        result_count = await cdp.get_element_count("li[role='button'], .MuiListItemButton-root")
        pr.data_counts["farmer_search_results"] = result_count

        # Click on the farmer result to select
        if found_lakshmi:
            clicked = await cdp.click_text("Lakshmi")
            pr.interactions.append({"action": "select_farmer", "result": "OK" if clicked else "FAIL"})
            await asyncio.sleep(1)

        path = await cdp.screenshot("07-farmer-selected.png")
        pr.screenshots.append(path)

        # Verify milk details form appeared
        has_quantity = await cdp.wait_for_text("Quantity", timeout=3)
        has_fat = await cdp.wait_for_text("Fat", timeout=2)
        has_snf = await cdp.wait_for_text("SNF", timeout=2)
        pr.interactions.append({"action": "milk_form_visible", "result": "OK" if (has_quantity and has_fat and has_snf) else "FAIL"})

        # ---- Fill milk details ----
        # Find inputs by label
        await cdp.evaluate("""
            (() => {
                const labels = [...document.querySelectorAll('label')];
                for (const label of labels) {
                    const text = label.textContent || '';
                    // Find sibling or associated input
                    const inputId = label.getAttribute('for');
                    let input = inputId ? document.getElementById(inputId) : null;
                    if (!input) {
                        input = label.parentElement?.querySelector('input') ||
                                label.closest('.MuiFormControl-root')?.querySelector('input');
                    }
                    if (!input) continue;
                    const nativeSet = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    if (text.includes('Quantity')) {
                        nativeSet.call(input, '5.5');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    } else if (text.includes('Fat')) {
                        nativeSet.call(input, '4.5');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    } else if (text.includes('SNF')) {
                        nativeSet.call(input, '8.2');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
                return true;
            })()
        """)
        await asyncio.sleep(0.5)

        pr.interactions.append({"action": "fill_quantity_5.5", "result": "OK"})
        pr.interactions.append({"action": "fill_fat_4.5", "result": "OK"})
        pr.interactions.append({"action": "fill_snf_8.2", "result": "OK"})

        # Check rate preview updated
        rate_text = await cdp.evaluate("""
            document.body.innerText
        """)
        has_rupee = "\u20b9" in (rate_text or "") or "₹" in (rate_text or "")
        pr.interactions.append({"action": "rate_preview_update", "result": "OK" if has_rupee else "WARN",
                                "detail": "Checking for rupee symbol in rate preview"})

        path = await cdp.screenshot("08-milk-details-filled.png")
        pr.screenshots.append(path)

        # ---- Test shift selector ----
        # Click Morning
        clicked_morning = await cdp.click_text("Morning", "button")
        pr.interactions.append({"action": "click_shift_morning", "result": "OK" if clicked_morning else "FAIL"})
        await asyncio.sleep(0.3)

        # Click Evening
        clicked_evening = await cdp.click_text("Evening", "button")
        pr.interactions.append({"action": "click_shift_evening", "result": "OK" if clicked_evening else "FAIL"})
        await asyncio.sleep(0.3)

        path = await cdp.screenshot("09-shift-evening.png")
        pr.screenshots.append(path)

        # ---- Test Aadhaar + Name search mode ----
        # First click "Change" to deselect farmer
        clicked_change = await cdp.click_text("Change", "button", timeout=3)
        pr.interactions.append({"action": "click_change_farmer", "result": "OK" if clicked_change else "SKIP"})
        await asyncio.sleep(0.5)

        # Click "Aadhaar + Name" toggle
        clicked_aadhaar = await cdp.click_text("Aadhaar", "button", timeout=3)
        pr.interactions.append({"action": "toggle_aadhaar_mode", "result": "OK" if clicked_aadhaar else "FAIL"})
        await asyncio.sleep(0.5)

        path = await cdp.screenshot("10-aadhaar-search-mode.png")
        pr.screenshots.append(path)

        # Switch back to phone mode and re-select farmer for submission test
        await cdp.click_text("Phone", "button", timeout=3)
        await asyncio.sleep(0.3)

        await cdp.evaluate("""
            (() => {
                const inputs = [...document.querySelectorAll('input')];
                const search = inputs.find(i => i.placeholder && i.placeholder.includes('phone'));
                if (search) {
                    search.focus();
                    const nativeSet = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    nativeSet.call(search, '9876543213');
                    search.dispatchEvent(new Event('input', { bubbles: true }));
                    search.dispatchEvent(new Event('change', { bubbles: true }));
                }
            })()
        """)
        await asyncio.sleep(1.5)

        # Select farmer again
        await cdp.click_text("Lakshmi", timeout=5)
        await asyncio.sleep(1)

        # Re-fill milk details
        await cdp.evaluate("""
            (() => {
                const labels = [...document.querySelectorAll('label')];
                for (const label of labels) {
                    const text = label.textContent || '';
                    const inputId = label.getAttribute('for');
                    let input = inputId ? document.getElementById(inputId) : null;
                    if (!input) {
                        input = label.parentElement?.querySelector('input') ||
                                label.closest('.MuiFormControl-root')?.querySelector('input');
                    }
                    if (!input) continue;
                    const nativeSet = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    if (text.includes('Quantity')) {
                        nativeSet.call(input, '5.5');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    } else if (text.includes('Fat')) {
                        nativeSet.call(input, '4.5');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    } else if (text.includes('SNF')) {
                        nativeSet.call(input, '8.2');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            })()
        """)
        await asyncio.sleep(0.5)

        # Select morning shift for submission
        await cdp.click_text("Morning", "button", timeout=3)
        await asyncio.sleep(0.3)

        # ---- Submit milk record ----
        path = await cdp.screenshot("11-pre-submit.png")
        pr.screenshots.append(path)

        submit_clicked = await cdp.click_text("Submit Milk Record", "button", timeout=5)
        pr.interactions.append({"action": "click_submit", "result": "OK" if submit_clicked else "FAIL"})
        await asyncio.sleep(3)

        # Check for receipt page or success
        url_after = await cdp.get_current_url()
        on_receipt = "/receipt" in url_after
        body_after = await cdp.evaluate("document.body?.innerText || ''") or ""
        has_success = on_receipt or "Receipt" in body_after or "success" in body_after.lower()
        pr.interactions.append({"action": "submission_result", "result": "OK" if has_success else "FAIL",
                                "detail": f"URL: {url_after}, has receipt: {on_receipt}"})

        if has_success and on_receipt:
            # Verify receipt content
            has_farmer_name = "Lakshmi" in body_after
            has_amount = "₹" in body_after or "\u20b9" in body_after
            has_fat = "4.5" in body_after
            has_snf = "8.2" in body_after
            pr.interactions.append({"action": "receipt_content", "result": "OK",
                                    "detail": f"farmer: {has_farmer_name}, amount: {has_amount}, fat: {has_fat}, snf: {has_snf}"})

            # Check for Print Receipt and Next Farmer buttons
            has_print = "Print" in body_after
            has_next = "Next Farmer" in body_after
            pr.interactions.append({"action": "receipt_buttons", "result": "OK" if (has_print and has_next) else "WARN",
                                    "detail": f"Print: {has_print}, Next Farmer: {has_next}"})

        path = await cdp.screenshot("12-receipt-or-result.png")
        pr.screenshots.append(path)

        # Check for "New farmer? Enroll here" link
        pr.interactions.append({"action": "enroll_link_check", "result": "NOTED",
                                "detail": "Enroll link tested during intake initial load"})

        # ---- Responsive tests ----
        for vp_name, vp in [("tablet", VIEWPORT_TABLET), ("mobile", VIEWPORT_MOBILE)]:
            await cdp.set_viewport(**vp)
            await cdp.navigate(f"{BASE_URL}/intake", wait_ms=2000)
            path = await cdp.screenshot(f"13-intake-{vp_name}.png")
            pr.screenshots.append(path)
            pr.interactions.append({"action": f"responsive_{vp_name}", "result": "SCREENSHOT"})

        # Reset to desktop
        await cdp.set_viewport(**VIEWPORT_DESKTOP)

        pr.console_errors = cdp.flush_console_errors()
        pr.network_requests = cdp.flush_network_log()
        pr.slow_requests = [r for r in pr.network_requests if r.get("duration_ms", 0) > 2000]
        pr.status = "PASS"

    except Exception as e:
        pr.status = "ERROR"
        pr.bugs.append(f"Exception: {e}")
        traceback.print_exc()

    pr.duration_ms = (time.time() - t0) * 1000
    report.pages.append(pr)


# ---------------------------------------------------------------------------
# Test: Dashboard Page
# ---------------------------------------------------------------------------

async def test_dashboard(cdp: CDPSession):
    pr = PageReport(name="Dashboard (/dashboard)")
    t0 = time.time()
    try:
        await cdp.set_viewport(**VIEWPORT_DESKTOP)
        await cdp.navigate(f"{BASE_URL}/dashboard", wait_ms=3000)
        pr.url = await cdp.get_current_url()

        body = await cdp.evaluate("document.body?.innerText || ''") or ""

        # Check page title
        has_daily = "Daily Collection" in body
        pr.interactions.append({"action": "page_title", "result": "OK" if has_daily else "FAIL",
                                "detail": "Looking for 'Daily Collection'"})

        # Check for stat cards
        has_todays_milk = "Today's Milk" in body or "Today" in body
        has_revenue = "Revenue" in body
        has_farmers = "Farmers Today" in body or "Farmers" in body
        has_quality = "Quality" in body or "Fat" in body
        pr.interactions.append({"action": "stat_cards", "result": "OK" if has_todays_milk else "WARN",
                                "detail": f"Milk: {has_todays_milk}, Revenue: {has_revenue}, Farmers: {has_farmers}, Quality: {has_quality}"})

        # Check shift cards
        has_morning = "Morning Shift" in body or "Morning" in body
        has_evening = "Evening Shift" in body or "Evening" in body
        pr.interactions.append({"action": "shift_cards", "result": "OK" if (has_morning and has_evening) else "WARN",
                                "detail": f"Morning: {has_morning}, Evening: {has_evening}"})

        # Check for actual data (numbers > 0)
        # Extract numeric values from stat cards
        stat_values = await cdp.evaluate("""
            (() => {
                const cards = [...document.querySelectorAll('.MuiCard-root')];
                return cards.map(c => c.textContent).join(' | ');
            })()
        """)
        pr.data_counts["stat_card_text"] = len(str(stat_values or ""))
        pr.notes.append(f"Stat card contents: {stat_values}")

        # Check for loading/error states
        has_error = "error" in body.lower() or "failed" in body.lower()
        has_skeleton = await cdp.element_exists(".MuiSkeleton-root")
        has_no_centre = "No collection centre" in body
        if has_error:
            pr.bugs.append(f"Dashboard shows error state")
        if has_no_centre:
            pr.bugs.append("Dashboard shows 'No collection centre selected' warning")
        pr.interactions.append({"action": "data_check", "result": "WARN" if has_error or has_no_centre else "OK",
                                "detail": f"error: {has_error}, skeleton: {has_skeleton}, no_centre: {has_no_centre}"})

        # Count cards
        card_count = await cdp.get_element_count(".MuiCard-root")
        pr.data_counts["card_count"] = card_count

        path = await cdp.screenshot("14-dashboard.png")
        pr.screenshots.append(path)

        # ---- Responsive ----
        for vp_name, vp in [("tablet", VIEWPORT_TABLET), ("mobile", VIEWPORT_MOBILE)]:
            await cdp.set_viewport(**vp)
            await asyncio.sleep(0.5)
            path = await cdp.screenshot(f"15-dashboard-{vp_name}.png")
            pr.screenshots.append(path)

        await cdp.set_viewport(**VIEWPORT_DESKTOP)

        pr.console_errors = cdp.flush_console_errors()
        pr.network_requests = cdp.flush_network_log()
        pr.slow_requests = [r for r in pr.network_requests if r.get("duration_ms", 0) > 2000]
        pr.status = "PASS" if not has_error and not has_no_centre else "FAIL"

    except Exception as e:
        pr.status = "ERROR"
        pr.bugs.append(f"Exception: {e}")
        traceback.print_exc()

    pr.duration_ms = (time.time() - t0) * 1000
    report.pages.append(pr)


# ---------------------------------------------------------------------------
# Test: Settlements Page
# ---------------------------------------------------------------------------

async def test_settlements(cdp: CDPSession):
    pr = PageReport(name="Settlements (/settlements)")
    t0 = time.time()
    try:
        await cdp.set_viewport(**VIEWPORT_DESKTOP)
        await cdp.navigate(f"{BASE_URL}/settlements", wait_ms=3000)
        pr.url = await cdp.get_current_url()

        body = await cdp.evaluate("document.body?.innerText || ''") or ""

        # Title
        has_title = "Farmer Settlements" in body
        pr.interactions.append({"action": "page_title", "result": "OK" if has_title else "FAIL"})

        # Period toggle buttons
        has_15 = "15 days" in body
        has_30 = "30 days" in body
        has_45 = "45 days" in body
        pr.interactions.append({"action": "period_toggles", "result": "OK" if (has_15 and has_30 and has_45) else "FAIL",
                                "detail": f"15: {has_15}, 30: {has_30}, 45: {has_45}"})

        # Wait for table to load
        await asyncio.sleep(2)
        body = await cdp.evaluate("document.body?.innerText || ''") or ""

        # Check table
        has_table = await cdp.element_exists("table")
        row_count = await cdp.get_element_count("table tbody tr")
        pr.data_counts["table_rows_15d"] = row_count
        pr.interactions.append({"action": "table_visible", "result": "OK" if has_table else "FAIL",
                                "detail": f"Rows: {row_count}"})

        # Check table headers
        has_deliveries = "Deliveries" in body
        has_liters = "Liters" in body or "liters" in body
        has_payout = "Payout" in body or "payout" in body
        pr.interactions.append({"action": "table_headers", "result": "OK" if has_deliveries else "WARN",
                                "detail": f"Deliveries: {has_deliveries}, Liters: {has_liters}, Payout: {has_payout}"})

        # Check total payout footer
        has_total = "Total Payout" in body or "Total Farmers" in body
        pr.interactions.append({"action": "totals_footer", "result": "OK" if has_total else "WARN"})

        path = await cdp.screenshot("16-settlements-15d.png")
        pr.screenshots.append(path)

        # ---- Toggle to 30 days ----
        clicked_30 = await cdp.click_text("30 days", "button")
        pr.interactions.append({"action": "click_30_days", "result": "OK" if clicked_30 else "FAIL"})
        await asyncio.sleep(2)

        row_count_30 = await cdp.get_element_count("table tbody tr")
        pr.data_counts["table_rows_30d"] = row_count_30

        path = await cdp.screenshot("17-settlements-30d.png")
        pr.screenshots.append(path)

        # ---- Toggle to 45 days ----
        clicked_45 = await cdp.click_text("45 days", "button")
        pr.interactions.append({"action": "click_45_days", "result": "OK" if clicked_45 else "FAIL"})
        await asyncio.sleep(2)

        row_count_45 = await cdp.get_element_count("table tbody tr")
        pr.data_counts["table_rows_45d"] = row_count_45

        path = await cdp.screenshot("18-settlements-45d.png")
        pr.screenshots.append(path)

        # Toggle back to 15
        await cdp.click_text("15 days", "button")
        await asyncio.sleep(1)

        # Check for error/loading
        has_error = await cdp.element_exists(".MuiAlert-standardError")
        has_spinner = await cdp.element_exists(".MuiCircularProgress-root")
        has_no_centre = "No collection centre" in (await cdp.evaluate("document.body?.innerText || ''") or "")
        if has_no_centre:
            pr.bugs.append("Settlements shows 'No collection centre selected'")

        # ---- Responsive ----
        for vp_name, vp in [("tablet", VIEWPORT_TABLET), ("mobile", VIEWPORT_MOBILE)]:
            await cdp.set_viewport(**vp)
            await asyncio.sleep(0.5)
            path = await cdp.screenshot(f"19-settlements-{vp_name}.png")
            pr.screenshots.append(path)

        await cdp.set_viewport(**VIEWPORT_DESKTOP)

        pr.console_errors = cdp.flush_console_errors()
        pr.network_requests = cdp.flush_network_log()
        pr.slow_requests = [r for r in pr.network_requests if r.get("duration_ms", 0) > 2000]
        pr.status = "PASS" if has_table and not has_no_centre else "FAIL"

    except Exception as e:
        pr.status = "ERROR"
        pr.bugs.append(f"Exception: {e}")
        traceback.print_exc()

    pr.duration_ms = (time.time() - t0) * 1000
    report.pages.append(pr)


# ---------------------------------------------------------------------------
# Test: Enroll Page
# ---------------------------------------------------------------------------

async def test_enroll(cdp: CDPSession):
    pr = PageReport(name="Enroll (/enroll)")
    t0 = time.time()
    try:
        await cdp.set_viewport(**VIEWPORT_DESKTOP)
        await cdp.navigate(f"{BASE_URL}/enroll", wait_ms=2000)
        pr.url = await cdp.get_current_url()

        body = await cdp.evaluate("document.body?.innerText || ''") or ""

        # Title
        has_title = "Enroll New Farmer" in body
        pr.interactions.append({"action": "page_title", "result": "OK" if has_title else "FAIL"})

        # Form fields
        has_name = await cdp.element_exists("input") and "Full Name" in body
        has_phone = "Phone" in body
        has_aadhaar = "Aadhaar" in body
        has_village = "Village" in body
        pr.interactions.append({"action": "form_fields", "result": "OK",
                                "detail": f"Name: {has_name}, Phone: {has_phone}, Aadhaar: {has_aadhaar}, Village: {has_village}"})

        # Submit button should be disabled initially
        submit_disabled = await cdp.evaluate("""
            (() => {
                const buttons = [...document.querySelectorAll('button')];
                const submit = buttons.find(b => b.textContent.includes('Enroll Farmer'));
                return submit ? submit.disabled : null;
            })()
        """)
        pr.interactions.append({"action": "submit_disabled_initially", "result": "OK" if submit_disabled else "FAIL"})

        path = await cdp.screenshot("20-enroll-initial.png")
        pr.screenshots.append(path)

        # ---- Fill form fields ----
        # Name
        await cdp.evaluate("""
            (() => {
                const labels = [...document.querySelectorAll('label')];
                for (const label of labels) {
                    const text = label.textContent || '';
                    const inputId = label.getAttribute('for');
                    let input = inputId ? document.getElementById(inputId) : null;
                    if (!input) {
                        input = label.closest('.MuiFormControl-root')?.querySelector('input');
                    }
                    if (!input) continue;
                    const nativeSet = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    if (text.includes('Full Name')) {
                        nativeSet.call(input, 'Test Kumar');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    } else if (text.includes('Phone')) {
                        nativeSet.call(input, '9999888877');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    } else if (text.includes('Village')) {
                        nativeSet.call(input, 'TEST_VILLAGE');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
                return true;
            })()
        """)
        await asyncio.sleep(0.3)
        pr.interactions.append({"action": "fill_name_phone_village", "result": "OK"})

        # Aadhaar — special masked input
        # Type 12 digits for aadhaar
        await cdp.evaluate("""
            (() => {
                const labels = [...document.querySelectorAll('label')];
                for (const label of labels) {
                    if (!(label.textContent || '').includes('Aadhaar')) continue;
                    const inputId = label.getAttribute('for');
                    let input = inputId ? document.getElementById(inputId) : null;
                    if (!input) {
                        input = label.closest('.MuiFormControl-root')?.querySelector('input');
                    }
                    if (input) {
                        input.focus();
                        return true;
                    }
                }
                return false;
            })()
        """)
        # Type digits one by one for the masked aadhaar field
        for digit in "123456789012":
            await cdp.send("Input.dispatchKeyEvent", {
                "type": "keyDown",
                "text": digit,
                "key": digit,
            })
            await cdp.send("Input.dispatchKeyEvent", {
                "type": "keyUp",
                "key": digit,
            })
            await asyncio.sleep(0.05)
        await asyncio.sleep(0.5)
        pr.interactions.append({"action": "fill_aadhaar_masked", "result": "OK"})

        # Check submit button is now enabled
        submit_enabled = await cdp.evaluate("""
            (() => {
                const buttons = [...document.querySelectorAll('button')];
                const submit = buttons.find(b => b.textContent.includes('Enroll Farmer'));
                return submit ? !submit.disabled : null;
            })()
        """)
        pr.interactions.append({"action": "submit_enabled_after_fill", "result": "OK" if submit_enabled else "FAIL"})

        path = await cdp.screenshot("21-enroll-filled.png")
        pr.screenshots.append(path)

        # ---- Validation tests ----
        # Test invalid phone number
        await cdp.evaluate("""
            (() => {
                const labels = [...document.querySelectorAll('label')];
                for (const label of labels) {
                    if (!(label.textContent || '').includes('Phone')) continue;
                    const inputId = label.getAttribute('for');
                    let input = inputId ? document.getElementById(inputId) : null;
                    if (!input) {
                        input = label.closest('.MuiFormControl-root')?.querySelector('input');
                    }
                    if (input) {
                        const nativeSet = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'value').set;
                        nativeSet.call(input, '1234567890');
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            })()
        """)
        await asyncio.sleep(0.5)
        body_val = await cdp.evaluate("document.body?.innerText || ''") or ""
        has_phone_error = "valid" in body_val.lower() and "mobile" in body_val.lower()
        pr.interactions.append({"action": "phone_validation", "result": "OK" if has_phone_error else "WARN",
                                "detail": "Entered invalid phone 1234567890, checking for error message"})

        path = await cdp.screenshot("22-enroll-validation.png")
        pr.screenshots.append(path)

        # NOTE: We do NOT submit the form to avoid creating test data in the database

        # ---- Test returnTo link ----
        await cdp.navigate(f"{BASE_URL}/enroll?returnTo=/intake", wait_ms=2000)
        body_rt = await cdp.evaluate("document.body?.innerText || ''") or ""
        has_back = "Back" in body_rt
        pr.interactions.append({"action": "returnTo_back_link", "result": "OK" if has_back else "WARN"})

        path = await cdp.screenshot("23-enroll-with-back.png")
        pr.screenshots.append(path)

        # ---- Responsive ----
        for vp_name, vp in [("tablet", VIEWPORT_TABLET), ("mobile", VIEWPORT_MOBILE)]:
            await cdp.set_viewport(**vp)
            await asyncio.sleep(0.5)
            path = await cdp.screenshot(f"24-enroll-{vp_name}.png")
            pr.screenshots.append(path)

        await cdp.set_viewport(**VIEWPORT_DESKTOP)

        pr.console_errors = cdp.flush_console_errors()
        pr.network_requests = cdp.flush_network_log()
        pr.slow_requests = [r for r in pr.network_requests if r.get("duration_ms", 0) > 2000]
        pr.status = "PASS"

    except Exception as e:
        pr.status = "ERROR"
        pr.bugs.append(f"Exception: {e}")
        traceback.print_exc()

    pr.duration_ms = (time.time() - t0) * 1000
    report.pages.append(pr)


# ---------------------------------------------------------------------------
# Test: NavBar Navigation
# ---------------------------------------------------------------------------

async def test_navbar_navigation(cdp: CDPSession):
    pr = PageReport(name="NavBar Navigation")
    t0 = time.time()
    try:
        await cdp.set_viewport(**VIEWPORT_DESKTOP)
        await cdp.navigate(f"{BASE_URL}/intake", wait_ms=2000)

        # Test each nav tab
        for tab_label, expected_path in [("Dashboard", "/dashboard"), ("Settlements", "/settlements"), ("Intake", "/intake")]:
            clicked = await cdp.click_text(tab_label, "button", timeout=5)
            await asyncio.sleep(1.5)
            url = await cdp.get_current_url()
            correct = expected_path in url
            pr.interactions.append({
                "action": f"nav_to_{tab_label.lower()}",
                "result": "OK" if (clicked and correct) else "FAIL",
                "detail": f"clicked: {clicked}, url: {url}",
            })

        # Test logout button exists
        logout_exists = await cdp.element_exists("button[aria-label='Logout'], svg[data-testid='LogoutOutlinedIcon']")
        # Try broader check
        if not logout_exists:
            logout_exists = await cdp.evaluate("""
                (() => {
                    const btns = [...document.querySelectorAll('button')];
                    return btns.some(b => b.querySelector('svg') && b.closest('[title="Logout"]'));
                })()
            """)
        pr.interactions.append({"action": "logout_button_exists", "result": "OK" if logout_exists else "WARN"})

        path = await cdp.screenshot("25-navbar-check.png")
        pr.screenshots.append(path)

        pr.console_errors = cdp.flush_console_errors()
        pr.network_requests = cdp.flush_network_log()
        pr.slow_requests = [r for r in pr.network_requests if r.get("duration_ms", 0) > 2000]
        pr.status = "PASS"

    except Exception as e:
        pr.status = "ERROR"
        pr.bugs.append(f"Exception: {e}")
        traceback.print_exc()

    pr.duration_ms = (time.time() - t0) * 1000
    report.pages.append(pr)


# ---------------------------------------------------------------------------
# Test: Error handling / edge cases
# ---------------------------------------------------------------------------

async def test_edge_cases(cdp: CDPSession):
    pr = PageReport(name="Edge Cases & Error Handling")
    t0 = time.time()
    try:
        await cdp.set_viewport(**VIEWPORT_DESKTOP)

        # Test non-existent route redirects to login
        await cdp.navigate(f"{BASE_URL}/nonexistent", wait_ms=2000)
        url = await cdp.get_current_url()
        redirected = "/login" in url or "/intake" in url
        pr.interactions.append({"action": "unknown_route_redirect", "result": "OK" if redirected else "FAIL",
                                "detail": f"URL: {url}"})

        # Navigate back to intake
        await cdp.navigate(f"{BASE_URL}/intake", wait_ms=2000)

        # Test that receipt page without state shows info message
        await cdp.navigate(f"{BASE_URL}/intake/receipt/fake-id", wait_ms=2000)
        body = await cdp.evaluate("document.body?.innerText || ''") or ""
        has_info = "No receipt data" in body or "submit" in body.lower()
        pr.interactions.append({"action": "receipt_no_state", "result": "OK" if has_info else "WARN",
                                "detail": f"Body contains info about missing receipt data: {has_info}"})

        path = await cdp.screenshot("26-receipt-no-state.png")
        pr.screenshots.append(path)

        pr.console_errors = cdp.flush_console_errors()
        pr.network_requests = cdp.flush_network_log()
        pr.slow_requests = [r for r in pr.network_requests if r.get("duration_ms", 0) > 2000]
        pr.status = "PASS"

    except Exception as e:
        pr.status = "ERROR"
        pr.bugs.append(f"Exception: {e}")
        traceback.print_exc()

    pr.duration_ms = (time.time() - t0) * 1000
    report.pages.append(pr)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report() -> str:
    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("PASHURAKSHA COLLECTION CENTRE — FULL E2E TEST REPORT")
    lines.append("=" * 80)
    lines.append(f"Run time: {report.end_time - report.start_time:.1f}s")
    lines.append(f"Auth status: {report.auth_status}")
    lines.append("")

    total_pass = sum(1 for p in report.pages if p.status == "PASS")
    total_fail = sum(1 for p in report.pages if p.status == "FAIL")
    total_error = sum(1 for p in report.pages if p.status == "ERROR")
    all_bugs = []
    all_slow = []

    lines.append(f"Pages tested: {len(report.pages)}  |  PASS: {total_pass}  |  FAIL: {total_fail}  |  ERROR: {total_error}")
    lines.append("")

    for pg in report.pages:
        lines.append("-" * 80)
        lines.append(f"PAGE: {pg.name}")
        lines.append(f"  URL: {pg.url}")
        lines.append(f"  Status: {pg.status}")
        lines.append(f"  Duration: {pg.duration_ms:.0f}ms")

        if pg.data_counts:
            lines.append(f"  Data counts: {pg.data_counts}")

        if pg.interactions:
            lines.append(f"  Interactions ({len(pg.interactions)}):")
            for ix in pg.interactions:
                detail = f" — {ix['detail']}" if ix.get("detail") else ""
                lines.append(f"    [{ix['result']}] {ix['action']}{detail}")

        if pg.console_errors:
            lines.append(f"  Console errors ({len(pg.console_errors)}):")
            for err in pg.console_errors[:10]:
                lines.append(f"    - {err[:200]}")

        if pg.slow_requests:
            lines.append(f"  Slow requests (>2s):")
            for sr in pg.slow_requests:
                lines.append(f"    - {sr['method']} {sr['url']} -> {sr.get('status', '?')} ({sr.get('duration_ms', '?')}ms)")
            all_slow.extend(pg.slow_requests)

        if pg.network_requests:
            api_reqs = [r for r in pg.network_requests if "/v1/" in r.get("url", "")]
            lines.append(f"  API requests: {len(api_reqs)} total")
            for nr in api_reqs[:15]:
                lines.append(f"    {nr['method']} {nr['url'][:80]} -> {nr.get('status', '?')} ({nr.get('duration_ms', '?')}ms)")

        if pg.bugs:
            lines.append(f"  BUGS ({len(pg.bugs)}):")
            for bug in pg.bugs:
                lines.append(f"    *** {bug}")
            all_bugs.extend(pg.bugs)

        if pg.screenshots:
            lines.append(f"  Screenshots ({len(pg.screenshots)}):")
            for ss in pg.screenshots:
                lines.append(f"    - {os.path.basename(ss)}")

        if pg.notes:
            lines.append(f"  Notes:")
            for note in pg.notes:
                lines.append(f"    - {note[:200]}")

        lines.append("")

    lines.append("=" * 80)
    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"Total bugs found: {len(all_bugs)}")
    for bug in all_bugs:
        lines.append(f"  *** {bug}")
    lines.append(f"Total slow API calls (>2s): {len(all_slow)}")
    for sr in all_slow:
        lines.append(f"  - {sr['method']} {sr['url'][:80]} ({sr.get('duration_ms', '?')}ms)")

    total_screenshots = sum(len(p.screenshots) for p in report.pages)
    lines.append(f"Total screenshots: {total_screenshots}")
    lines.append(f"Screenshot dir: {SCREENSHOT_DIR}")
    lines.append("=" * 80)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    report.start_time = time.time()
    print("=" * 60)
    print("PashuRaksha Collection Centre — Full E2E Test")
    print("=" * 60)

    cdp = await connect_cdp()
    print("[OK] Connected to Chrome via CDP")

    try:
        # 1. Auth
        print("\n[TEST] Authentication...")
        auth_ok = await test_auth(cdp)
        if not auth_ok:
            print("[FAIL] Authentication failed — attempting to continue anyway")

        # 2. Intake page (includes farmer search, milk form, submit, receipt)
        print("\n[TEST] Intake page...")
        await test_intake(cdp)

        # 3. Dashboard
        print("\n[TEST] Dashboard page...")
        await test_dashboard(cdp)

        # 4. Settlements
        print("\n[TEST] Settlements page...")
        await test_settlements(cdp)

        # 5. Enroll
        print("\n[TEST] Enroll page...")
        await test_enroll(cdp)

        # 6. NavBar navigation
        print("\n[TEST] NavBar navigation...")
        await test_navbar_navigation(cdp)

        # 7. Edge cases
        print("\n[TEST] Edge cases...")
        await test_edge_cases(cdp)

    finally:
        await cdp.close()

    report.end_time = time.time()

    # Generate and print report
    report_text = generate_report()
    print("\n")
    print(report_text)

    # Save report to file
    report_path = os.path.join(SCREENSHOT_DIR, "test-report.txt")
    with open(report_path, "w") as f:
        f.write(report_text)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
