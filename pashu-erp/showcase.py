#!/usr/bin/env python3
"""
PashuRaksha ERP — Showcase Launcher
Opens all endpoints in Chrome via CDP and auto-logs into each portal.

Prerequisites:
  - Chrome with --remote-debugging-port=9222
    (run: ~/multi-cloud/launch-chrome-debug.sh)
  - Docker stack running:
    cd pashu-erp && docker compose up -d
  - Frontend dev servers (start whichever you need):
    Admin:      cd packages/admin      && pnpm dev          # :3000
    Collection: cd packages/collection && pnpm dev          # :3001
    Vet:        cd packages/vet        && pnpm dev          # :3002
    Mobile:     cd packages/mobile     && pnpm expo:web     # :8081

Usage:
  python3 showcase.py               # Full showcase (backend + all UIs)
  python3 showcase.py --backend     # Backend endpoints only
  python3 showcase.py --ui          # UI portals only (with login)
  python3 showcase.py --no-login    # Open all pages without auto-login
  python3 showcase.py --reset       # Reset OTP rate limits before starting
"""

import argparse
import json
import re
import subprocess
import sys
import time
from typing import Optional

import requests
import websocket

# ── Configuration ────────────────────────────────────────────────────────────

CDP_BASE = "http://127.0.0.1:9222"
API_BASE = "http://localhost:8000"
MOCK_BASE = "http://localhost:8001"
DOCKER_API_CONTAINER = "pashu-erp-api-1"

# Demo users from packages/api/app/seed/demo_data.py
DEMO_USERS = {
    "admin":      {"phone": "9900000001", "label": "Admin (Deepak Kumar)"},
    "collection": {"phone": "9900000006", "label": "Milk Centre (Suresh Kumar)"},
    "vet":        {"phone": "9900000005", "label": "Vet (Dr. Ramesh)"},
    "farmer":     {"phone": "9900000002", "label": "Farmer (Lakshmi Devi)"},
}

BACKEND_PAGES = [
    ("Health",       f"{API_BASE}/health"),
    ("Readiness",    f"{API_BASE}/ready"),
    ("Metrics",      f"{API_BASE}/metrics"),
    ("Mock Health",  f"{MOCK_BASE}/health"),
]

# UI portals — admin/collection/vet share identical MUI selectors
# Mobile (Expo web) uses React Native Paper with different selectors
UI_PORTALS = [
    {"name": "Admin Portal",      "port": 3000, "path": "/login", "user": "admin",      "kind": "mui"},
    {"name": "Collection Centre", "port": 3001, "path": "/login", "user": "collection", "kind": "mui"},
    {"name": "Vet Dashboard",     "port": 3002, "path": "/login", "user": "vet",        "kind": "mui"},
    {"name": "Mobile (Farmer)",   "port": 8081, "path": "/",      "user": "farmer",     "kind": "rn"},
]

# ── Terminal colors ──────────────────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def ok(msg):   print(f"  {GREEN}[OK]{RESET}   {msg}")
def fail(msg): print(f"  {RED}[FAIL]{RESET} {msg}")
def skip(msg): print(f"  {YELLOW}[SKIP]{RESET} {msg}")
def info(msg): print(f"  {CYAN}>>{RESET}     {msg}")


# ── CDP Tab Helper ───────────────────────────────────────────────────────────

class CDPTab:
    """Chrome DevTools Protocol session for a single browser tab."""

    def __init__(self, ws_url: str, target_id: str = ""):
        self.ws = websocket.create_connection(ws_url, timeout=30)
        self._id = 0
        self.target_id = target_id

    def cmd(self, method: str, params: dict = None) -> dict:
        """Send a CDP command and wait for the response (skipping events)."""
        self._id += 1
        payload = {"id": self._id, "method": method}
        if params:
            payload["params"] = params
        self.ws.send(json.dumps(payload))

        deadline = time.time() + 30
        while time.time() < deadline:
            self.ws.settimeout(max(0.5, deadline - time.time()))
            try:
                data = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                break
            if data.get("id") == self._id:
                if "error" in data:
                    err = data["error"]
                    raise RuntimeError(err.get("message", str(err)))
                return data.get("result", {})
            # else: it's an event — ignore and keep reading
        raise TimeoutError(f"CDP timeout waiting for response to: {method}")

    def js(self, expression: str):
        """Evaluate JavaScript in the page, return the result value."""
        result = self.cmd("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        })
        remote = result.get("result", {})
        if remote.get("subtype") == "error":
            raise RuntimeError(f"JS error: {remote.get('description', '')}")
        return remote.get("value")

    def navigate(self, url: str, wait: float = 3.0):
        """Navigate to a URL and wait for React to hydrate."""
        self.cmd("Page.enable")
        self.cmd("Runtime.enable")
        self.cmd("Page.navigate", {"url": url})
        time.sleep(wait)

    def set_react_input(self, selector: str, value: str, timeout: float = 8.0) -> bool:
        """Type into a React-controlled input using CDP Input.insertText.

        Steps: wait for element → focus → select-all → insertText.
        Retries until the element appears (React hydration can be slow).
        """
        deadline = time.time() + timeout
        found = False
        while time.time() < deadline:
            found = self.js(f"""
                (() => {{
                    const el = document.querySelector('{selector}');
                    if (!el) return false;
                    el.focus();
                    el.select();
                    return true;
                }})()
            """)
            if found:
                break
            time.sleep(0.5)
        if not found:
            return False
        time.sleep(0.1)
        # CDP insertText replaces the selection with the new text,
        # firing native input events that React's onChange handles.
        self.cmd("Input.insertText", {"text": value})
        time.sleep(0.3)
        return True

    def wait_and_click_button(self, text: str, timeout: float = 5.0) -> bool:
        """Wait for a <button> containing `text` to be enabled, then click it."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            result = self.js(f"""
                (() => {{
                    const btn = Array.from(document.querySelectorAll('button'))
                        .find(b => b.textContent.includes('{text}'));
                    if (!btn) return 'NOT_FOUND';
                    if (btn.disabled || btn.getAttribute('aria-disabled') === 'true')
                        return 'DISABLED';
                    btn.click();
                    return 'CLICKED';
                }})()
            """)
            if result == "CLICKED":
                time.sleep(0.3)
                return True
            if result == "NOT_FOUND":
                return False
            # DISABLED — wait for React re-render
            time.sleep(0.3)
        return False

    def click_button_by_text(self, text: str) -> bool:
        """Click the first <button> whose text content contains `text`."""
        return self.js(f"""
            (() => {{
                const btn = Array.from(document.querySelectorAll('button'))
                    .find(b => b.textContent.includes('{text}'));
                if (!btn) return false;
                btn.click();
                return true;
            }})()
        """)

    def click_role_button_by_text(self, text: str) -> bool:
        """Click the first element with role=button whose text contains `text`.

        React Native Paper renders <Button> as <div role="button">.
        """
        return self.js(f"""
            (() => {{
                const els = document.querySelectorAll('[role="button"]');
                const btn = Array.from(els).find(b => b.textContent.includes('{text}'));
                if (!btn) return false;
                btn.click();
                return true;
            }})()
        """)

    def emulate_mobile(self, device: str = "iPhone 14 Pro"):
        """Enable mobile device emulation (viewport, touch, user-agent)."""
        # iPhone 14 Pro: 393x852 @3x
        self.cmd("Emulation.setDeviceMetricsOverride", {
            "width": 393,
            "height": 852,
            "deviceScaleFactor": 3,
            "mobile": True,
        })
        self.cmd("Emulation.setTouchEmulationEnabled", {"enabled": True})
        self.cmd("Emulation.setUserAgentOverride", {
            "userAgent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                "Mobile/15E148 Safari/604.1"
            ),
        })

    def get_url(self) -> str:
        return self.js("window.location.href") or ""

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


# ── Browser-level CDP session (for creating isolated contexts) ───────────────

def _get_browser_ws_url() -> str:
    """Get the browser-level WebSocket debugger URL."""
    r = requests.get(f"{CDP_BASE}/json/version", timeout=5)
    return r.json()["webSocketDebuggerUrl"]


def _browser_session() -> CDPTab:
    """Return a CDP session connected to the *browser* target (not a page)."""
    return CDPTab(_get_browser_ws_url())


def create_browser_context() -> str:
    """Create an isolated browser context (like incognito) — returns its ID.

    Each context has its own cookie jar, so logging into admin in one
    context won't overwrite the vet session in another.
    """
    browser = _browser_session()
    result = browser.cmd("Target.createBrowserContext", {
        "disposeOnDetach": False,
    })
    ctx_id = result["browserContextId"]
    browser.close()
    return ctx_id


# ── Utility functions ────────────────────────────────────────────────────────

def create_tab(url: str = "about:blank", browser_context_id: str = None) -> CDPTab:
    """Create a new Chrome tab and return a CDP session.

    If browser_context_id is given, the tab lives in that isolated context
    (separate cookie jar).  Otherwise it shares the default context.
    """
    if browser_context_id:
        # Use the browser-level CDP target to create a tab inside the context
        browser = _browser_session()
        result = browser.cmd("Target.createTarget", {
            "url": url,
            "browserContextId": browser_context_id,
        })
        target_id = result["targetId"]
        browser.close()
        # Fetch the WebSocket URL for this new target
        targets = requests.get(f"{CDP_BASE}/json", timeout=5).json()
        ws_url = None
        for t in targets:
            if t.get("id") == target_id:
                ws_url = t["webSocketDebuggerUrl"]
                break
        if not ws_url:
            raise RuntimeError(f"Could not find WS URL for target {target_id}")
        return CDPTab(ws_url, target_id=target_id)
    else:
        resp = requests.put(f"{CDP_BASE}/json/new?{url}", timeout=5)
        target = resp.json()
        return CDPTab(target["webSocketDebuggerUrl"], target_id=target["id"])


def open_devtools(target_id: str):
    """Open Chrome DevTools for a tab in a separate browser tab.

    Uses browser-level CDP Target.createTarget to reliably open a new tab
    (the /json/new?url HTTP endpoint misparses the nested query string).

    The CDP WebSocket to the target must be closed first (only one
    debugger connection per target is allowed).
    """
    devtools_url = (
        f"http://127.0.0.1:9222/devtools/inspector.html"
        f"?ws=127.0.0.1:9222/devtools/page/{target_id}"
    )
    browser = _browser_session()
    browser.cmd("Target.createTarget", {"url": devtools_url})
    browser.close()


def cleanup_old_tabs():
    """Close tabs from previous showcase runs to free Chrome resources.

    Closes any localhost tabs (ports 3000-3002, 8000-8001, 8081) and
    devtools inspector tabs, but leaves other tabs untouched.
    """
    try:
        targets = requests.get(f"{CDP_BASE}/json", timeout=5).json()
    except Exception:
        return 0

    showcase_patterns = re.compile(
        r"localhost:(3000|3001|3002|8000|8001|8081)|devtools/inspector"
    )
    closed = 0
    for t in targets:
        url = t.get("url", "")
        if showcase_patterns.search(url):
            try:
                requests.get(f"{CDP_BASE}/json/close/{t['id']}", timeout=3)
                closed += 1
            except Exception:
                pass
    return closed


def is_server_up(port: int) -> bool:
    try:
        requests.get(f"http://localhost:{port}", timeout=5, allow_redirects=False)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False


def extract_otp(phone_suffix: str) -> Optional[str]:
    """Extract the latest OTP for a phone from the API container's docker logs.

    The ConsoleOTPProvider prints:
        DEV OTP for +919900000001
        Code: 483921
    """
    try:
        result = subprocess.run(
            ["docker", "logs", DOCKER_API_CONTAINER, "--tail", "60"],
            capture_output=True, text=True, timeout=5,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    output = result.stderr + result.stdout
    # Match the OTP block — logs are wrapped in box-drawing chars (║)
    # and phone/code are on adjacent lines:
    #   ║  DEV OTP for +919900000001     ║
    #   ║  Code: 175360                     ║
    pattern = rf"DEV OTP for \+91{phone_suffix}[\s║]*Code:\s*(\d{{6}})"
    matches = re.findall(pattern, output, re.DOTALL)
    return matches[-1] if matches else None


def reset_otp_limits():
    """Reset OTP rate limits in the database (for repeated testing)."""
    print(f"\n{BOLD}Resetting OTP rate limits...{RESET}")
    try:
        subprocess.run(
            [
                "docker", "exec", "pashu-erp-db-1",
                "psql", "-U", "pashu", "-d", "pashuraksha",
                "-c", "UPDATE otp_requests SET request_count = 0, attempts = 0;",
            ],
            capture_output=True, text=True, timeout=10,
        )
        ok("OTP rate limits cleared")
    except Exception as e:
        fail(f"Could not reset OTP limits: {e}")


# ── Preflight checks ────────────────────────────────────────────────────────

def preflight() -> list[str]:
    """Verify prerequisites. Returns list of fatal error keys."""
    print(f"\n{BOLD}Preflight Checks{RESET}")
    errors = []

    # Chrome CDP
    try:
        r = requests.get(f"{CDP_BASE}/json/version", timeout=3)
        browser = r.json().get("Browser", "unknown")
        ok(f"Chrome CDP: {browser}")
    except Exception:
        fail("Chrome CDP not reachable on :9222")
        errors.append("cdp")

    # API backend
    if is_server_up(8000):
        ok("API server on :8000")
    else:
        fail("API server not running on :8000")
        errors.append("api")

    # Mock backends
    if is_server_up(8001):
        ok("Mock backends on :8001")
    else:
        skip("Mock backends not on :8001 (non-fatal)")

    # Frontend servers
    for p in UI_PORTALS:
        port = p["port"]
        if is_server_up(port):
            ok(f"{p['name']} on :{port}")
        else:
            skip(f"{p['name']} not running on :{port}")

    return errors


# ── Backend endpoints ────────────────────────────────────────────────────────

def open_backend():
    """Open all backend/API endpoints in Chrome tabs."""
    print(f"\n{BOLD}Backend Endpoints{RESET}")
    for name, url in BACKEND_PAGES:
        if not is_server_up(int(url.split(":")[2].split("/")[0])):
            skip(f"{name} — server not running")
            continue
        try:
            tab = create_tab(url)
            tab.close()
            ok(f"{name}: {url}")
        except Exception as e:
            fail(f"{name}: {e}")
        time.sleep(0.4)


# ── MUI login (admin, collection, vet) ──────────────────────────────────────

def login_mui_portal(portal: dict):
    """Log into an MUI-based portal (admin / collection / vet).

    All three share identical selectors:
      - Phone input:  input[placeholder="9876543210"]
      - OTP boxes:    [aria-label="OTP digit N of 6"]
      - Buttons:      <button> with text "Send OTP" / "Verify"
    """
    name = portal["name"]
    port = portal["port"]
    user = DEMO_USERS[portal["user"]]
    phone = user["phone"]
    url = f"http://localhost:{port}{portal['path']}"

    print(f"\n{BOLD}{name}{RESET}  {DIM}{user['label']} (+91{phone}){RESET}")

    if not is_server_up(port):
        skip(f"Server not running on :{port}")
        return

    tab = None
    try:
        # Each portal gets its own browser context (isolated cookie jar)
        ctx_id = create_browser_context()
        info(f"Isolated browser context created")
        tab = create_tab(url, browser_context_id=ctx_id)
        tab.navigate(url, wait=5)
        info("Login page loaded")

        # Step 1 — Enter phone number (retries up to 8s for hydration)
        if not tab.set_react_input('input[placeholder="9876543210"]', phone):
            fail("Phone input not found")
            return
        info(f"Phone entered: +91{phone}")

        # Step 2 — Wait for React to enable the button, then click
        if not tab.wait_and_click_button("Send OTP", timeout=8):
            fail('"Send OTP" button not found or stayed disabled')
            return
        info("OTP request sent")
        time.sleep(2.5)  # wait for API round-trip + docker log flush

        # Step 3 — Extract OTP from docker logs
        otp = extract_otp(phone)
        if not otp:
            fail("Could not extract OTP from docker logs")
            return
        info(f"OTP from logs: {otp}")

        # Step 4 — Paste full OTP into the first box (auto-distributes)
        if not tab.set_react_input('[aria-label="OTP digit 1 of 6"]', otp):
            fail("OTP input not found")
            return
        info("OTP entered (6 digits)")
        time.sleep(0.5)

        # Step 5 — Click "Verify & Login"
        if not tab.click_button_by_text("Verify"):
            fail('"Verify & Login" button not found')
            return
        info("Verifying OTP...")
        time.sleep(3)  # wait for auth + redirect

        # Step 6 — Check outcome
        current = tab.get_url()
        if "/login" not in current:
            ok(f"Logged in! Redirected to: {current}")
        else:
            fail(f"Still on login page: {current}")

        # Step 7 — Open DevTools for this tab
        target_id = tab.target_id
        tab.close()
        tab = None  # prevent double-close in finally
        time.sleep(0.3)
        open_devtools(target_id)
        info("DevTools opened")

    except Exception as e:
        fail(str(e))
    finally:
        if tab:
            tab.close()


# ── React Native Web login (mobile / farmer) ────────────────────────────────

def login_mobile_portal(portal: dict):
    """Log into the Expo/React Native Web mobile app.

    Actual DOM (from inspection of the static Expo web export):
      - Phone input: <input type="tel" placeholder="Enter phone number">
      - OTP boxes:   <input> with aria-label="OTP digit N of 6"
      - Buttons:     <button> (RN Paper renders as native <button> in web)
      - Button disabled state: aria-disabled="true"
    """
    name = portal["name"]
    port = portal["port"]
    user = DEMO_USERS[portal["user"]]
    phone = user["phone"]
    url = f"http://localhost:{port}{portal['path']}"

    print(f"\n{BOLD}{name}{RESET}  {DIM}{user['label']} (+91{phone}){RESET}")

    if not is_server_up(port):
        skip(f"Server not running on :{port}")
        return

    tab = None
    try:
        # Each portal gets its own browser context (isolated cookie jar)
        ctx_id = create_browser_context()
        info(f"Isolated browser context created")
        tab = create_tab(url, browser_context_id=ctx_id)

        # Emulate mobile device (iPhone 14 Pro) before loading the page
        tab.cmd("Page.enable")
        tab.cmd("Runtime.enable")
        tab.emulate_mobile()
        info("Mobile device emulation enabled (iPhone 14 Pro)")

        tab.navigate(url, wait=5)  # Expo web needs more hydration time
        info("Login page loaded")

        # Step 1 — Enter phone number
        # RN Paper TextInput renders as <input type="tel"> in web
        if not tab.set_react_input('input[type="tel"]', phone):
            fail("Phone input not found")
            return
        info(f"Phone entered: +91{phone}")

        # Step 2 — Wait for button to become enabled, then click
        if not tab.wait_and_click_button("Send OTP"):
            fail('"Send OTP" button not found or stayed disabled')
            return
        info("OTP request sent")
        time.sleep(2.5)

        # Step 3 — Extract OTP
        otp = extract_otp(phone)
        if not otp:
            fail("Could not extract OTP from docker logs")
            return
        info(f"OTP from logs: {otp}")

        # Step 4 — Enter OTP (first box, auto-distributes to all 6)
        if not tab.set_react_input('[aria-label="OTP digit 1 of 6"]', otp):
            fail("OTP input not found")
            return
        info("OTP entered (6 digits)")

        # Step 5 — Click "Verify OTP"
        if not tab.wait_and_click_button("Verify", timeout=3):
            fail('"Verify" button not found or stayed disabled')
            return
        info("Verifying OTP...")
        time.sleep(3)

        # Step 6 — Check outcome
        current = tab.get_url()
        if "/login" not in current:
            ok(f"Logged in! Redirected to: {current}")
        else:
            fail(f"Still on login page: {current}")

        # Step 7 — Open DevTools for this tab
        target_id = tab.target_id
        tab.close()
        tab = None  # prevent double-close in finally
        time.sleep(0.3)
        open_devtools(target_id)
        info("DevTools opened")

    except Exception as e:
        fail(str(e))
    finally:
        if tab:
            tab.close()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PashuRaksha ERP — Showcase Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Demo Users (from seed data):
  Admin Portal:      +91 9900000001  (Deepak Kumar)
  Collection Centre: +91 9900000006  (Suresh Kumar)
  Vet Dashboard:     +91 9900000005  (Dr. Ramesh)
  Mobile (Farmer):   +91 9900000002  (Lakshmi Devi)
        """,
    )
    parser.add_argument("--backend",  action="store_true", help="Backend endpoints only")
    parser.add_argument("--ui",       action="store_true", help="UI portals only")
    parser.add_argument("--no-login", action="store_true", help="Open pages without auto-login")
    parser.add_argument("--reset",    action="store_true", help="Reset OTP rate limits first")
    args = parser.parse_args()

    show_all = not args.backend and not args.ui

    print(f"\n{BOLD}{'=' * 52}")
    print(f"   PashuRaksha ERP  —  Showcase Launcher")
    print(f"{'=' * 52}{RESET}")

    # Preflight
    errors = preflight()
    if "cdp" in errors:
        print(f"\n{RED}Chrome CDP required. Run:{RESET}")
        print(f"  ~/multi-cloud/launch-chrome-debug.sh")
        sys.exit(1)
    if "api" in errors:
        print(f"\n{RED}Docker API required. Run:{RESET}")
        print(f"  cd pashu-erp && docker compose up -d")
        sys.exit(1)

    # Clean up stale tabs from previous runs
    closed = cleanup_old_tabs()
    if closed:
        ok(f"Closed {closed} stale tab(s) from previous runs")
        time.sleep(0.5)

    # Optional: reset rate limits
    if args.reset:
        reset_otp_limits()

    # ── Backend endpoints ──
    if show_all or args.backend:
        open_backend()

    # ── UI portals ──
    if show_all or args.ui:
        print(f"\n{BOLD}UI Portal Login{RESET}")

        for portal in UI_PORTALS:
            if args.no_login:
                # Just open the page, no login
                port = portal["port"]
                if is_server_up(port):
                    url = f"http://localhost:{port}"
                    try:
                        tab = create_tab(url)
                        tab.close()
                        ok(f"{portal['name']}: {url}")
                    except Exception as e:
                        fail(f"{portal['name']}: {e}")
                else:
                    skip(f"{portal['name']} not running on :{port}")
            elif portal["kind"] == "mui":
                login_mui_portal(portal)
            elif portal["kind"] == "rn":
                login_mobile_portal(portal)

    # ── Summary ──
    not_running = [p for p in UI_PORTALS if not is_server_up(p["port"])]
    print(f"\n{BOLD}{'=' * 52}")
    print(f"   Showcase Ready!")
    print(f"{'=' * 52}{RESET}")

    if not_running:
        print(f"\n  {YELLOW}Servers not running:{RESET}")
        for p in not_running:
            if p["port"] == 3000:
                print(f"    {p['name']:20s}  cd packages/admin && pnpm dev")
            elif p["port"] == 3001:
                print(f"    {p['name']:20s}  cd packages/collection && pnpm dev")
            elif p["port"] == 3002:
                print(f"    {p['name']:20s}  cd packages/vet && pnpm dev")
            elif p["port"] == 8081:
                print(f"    {p['name']:20s}  cd packages/mobile && pnpm expo:web")

    print(f"\n  {DIM}Tip: Run with --reset if OTP rate limits block you{RESET}")
    print()


if __name__ == "__main__":
    main()
