#!/usr/bin/env python3
"""
CDP-based UI testing for PashuRaksha Admin Dashboard.
Connects to Chrome DevTools Protocol at 127.0.0.1:9222.
Tests each page for rendering, JS errors, layout, and responsiveness.
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
BASE_URL = "http://localhost:3000"
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

# Pages to test
PAGES = [
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
    ("/login", "login"),
]

VIEWPORTS = [
    (1920, 1080, "desktop-1920"),
    (1366, 768, "laptop-1366"),
    (768, 1024, "tablet-768"),
]


class CDPClient:
    def __init__(self):
        self.ws = None
        self.msg_id = 0
        self.console_errors = []
        self.js_exceptions = []
        self._pending = {}
        self._listener_task = None

    async def connect(self):
        """Connect to Chrome CDP, creating a new tab for testing."""
        import urllib.request
        # Create a new tab so we don't disrupt existing browsing (Chrome requires PUT)
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
                            text = " ".join(a.get("value", a.get("description", "")) for a in args)
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
        result = await self.send("Page.navigate", {"url": url})
        # Wait for page to load
        await asyncio.sleep(0.5)
        # Wait for loadEventFired or just poll
        for _ in range(60):  # up to 30 seconds
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
        # Extra wait for React/Next.js hydration
        await asyncio.sleep(2)
        return result

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

        # Title
        info["title"] = await self.evaluate("document.title")

        # Body text length (is page blank?)
        info["body_text_length"] = await self.evaluate("document.body?.innerText?.length || 0")

        # Check for visible content
        info["has_main_content"] = await self.evaluate(
            "!!document.querySelector('main, [role=\"main\"], #__next > div')"
        )

        # Check for MUI components
        info["mui_components"] = await self.evaluate(
            "document.querySelectorAll('[class*=\"Mui\"]').length"
        )

        # Check for sidebar/drawer
        info["has_sidebar"] = await self.evaluate(
            "!!document.querySelector('[class*=\"MuiDrawer\"], [data-testid*=\"sidebar\"], nav')"
        )

        # Check for app bar/header
        info["has_header"] = await self.evaluate(
            "!!document.querySelector('[class*=\"MuiAppBar\"], header, [class*=\"MuiToolbar\"]')"
        )

        # Check for tables
        info["table_count"] = await self.evaluate(
            "document.querySelectorAll('table, [class*=\"MuiTable\"]').length"
        )

        # Check for Leaflet maps
        info["has_map"] = await self.evaluate(
            "!!document.querySelector('.leaflet-container')"
        )

        # Check for Recharts
        info["has_chart"] = await self.evaluate(
            "!!document.querySelector('.recharts-responsive-container, .recharts-wrapper, svg.recharts-surface')"
        )

        # Check for error states visible in DOM
        info["visible_errors"] = await self.evaluate("""
            (() => {
                const els = document.querySelectorAll('[class*="error" i], [class*="Error"]');
                const texts = [];
                els.forEach(el => {
                    if (el.offsetParent !== null && el.innerText) texts.push(el.innerText.substring(0, 100));
                });
                return texts.slice(0, 5);
            })()
        """)

        # Check for 404 text
        info["has_404"] = await self.evaluate(
            "!!document.body?.innerText?.match(/404|not found/i)"
        )

        # Scroll dimensions (overflow check)
        info["scroll_width"] = await self.evaluate("document.documentElement.scrollWidth")
        info["client_width"] = await self.evaluate("document.documentElement.clientWidth")
        info["has_horizontal_overflow"] = await self.evaluate(
            "document.documentElement.scrollWidth > document.documentElement.clientWidth + 5"
        )

        # Check stat cards
        info["stat_cards"] = await self.evaluate(
            "document.querySelectorAll('[data-testid=\"stat-card\"]').length"
        )

        # Check for loading indicators
        info["has_loading"] = await self.evaluate(
            "!!document.querySelector('[class*=\"MuiCircularProgress\"], [class*=\"MuiSkeleton\"], [class*=\"loading\" i]')"
        )

        # Navigation links count
        info["nav_links"] = await self.evaluate(
            "document.querySelectorAll('nav a, [class*=\"MuiDrawer\"] a, [class*=\"MuiList\"] a').length"
        )

        return info

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
        if self.ws:
            await self.ws.close()
        # Close the tab we created
        try:
            import urllib.request
            urllib.request.urlopen(f"http://{CDP_HOST}:{CDP_PORT}/json/close/{self.tab_id}")
        except Exception:
            pass


async def test_page(cdp, path, name, viewport_width=1920, viewport_height=1080, viewport_label="desktop-1920"):
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
    }

    try:
        await cdp.set_viewport(viewport_width, viewport_height)
        await cdp.navigate(f"{BASE_URL}{path}")

        # Capture state
        info = await cdp.get_page_info()
        result["info"] = info
        result["js_errors"] = list(cdp.js_exceptions)
        result["console_errors"] = list(cdp.console_errors)

        # Screenshot
        ss_name = f"{name}_{viewport_label}.png"
        ss_path = await cdp.screenshot(ss_name)
        result["screenshot"] = ss_name

        # Determine pass/fail
        issues = []

        # White screen check
        body_len = info.get("body_text_length", 0)
        if isinstance(body_len, (int, float)) and body_len < 10:
            issues.append("CRITICAL: Page appears blank (body text < 10 chars)")

        # 404 check
        if info.get("has_404"):
            issues.append("CRITICAL: Page shows 404")

        # JS exceptions
        if cdp.js_exceptions:
            # Filter out known API-down errors
            real_errors = [e for e in cdp.js_exceptions if "fetch" not in e.lower() and "network" not in e.lower() and "ECONNREFUSED" not in e]
            if real_errors:
                issues.append(f"JS EXCEPTIONS ({len(real_errors)}): {'; '.join(real_errors[:3])}")

        # Layout checks (only at desktop viewport)
        if viewport_width >= 1024:
            if not info.get("has_sidebar") and path != "/login":
                issues.append("WARN: No sidebar/nav detected")
            if not info.get("has_header") and path != "/login":
                issues.append("WARN: No header/appbar detected")

        # MUI rendering
        mui_count = info.get("mui_components", 0)
        if isinstance(mui_count, (int, float)) and mui_count < 2 and path != "/login":
            issues.append("WARN: Very few MUI components rendered (<2)")

        # Horizontal overflow
        if info.get("has_horizontal_overflow"):
            issues.append(f"WARN: Horizontal overflow at {viewport_label} ({info.get('scroll_width')}px > {info.get('client_width')}px)")

        result["issues"] = issues
        has_critical = any("CRITICAL" in i for i in issues)
        result["status"] = "FAIL" if has_critical else ("WARN" if issues else "PASS")

    except Exception as e:
        result["status"] = "ERROR"
        result["issues"] = [f"Test error: {str(e)}"]

    return result


async def test_navigation(cdp):
    """Test sidebar navigation by clicking links."""
    results = []
    await cdp.set_viewport(1920, 1080)
    await cdp.navigate(f"{BASE_URL}/")
    await asyncio.sleep(2)

    # Get all nav links
    nav_data = await cdp.evaluate("""
        (() => {
            const links = document.querySelectorAll('nav a, [class*="MuiDrawer"] a, [class*="MuiListItem"] a');
            return Array.from(links).map(a => ({
                text: a.innerText?.trim(),
                href: a.getAttribute('href'),
            })).filter(l => l.text && l.href);
        })()
    """)

    if nav_data and isinstance(nav_data, list):
        for link in nav_data[:15]:  # limit to 15
            text = link.get("text", "?")
            href = link.get("href", "")
            try:
                # Click the link via JS
                clicked = await cdp.evaluate(f"""
                    (() => {{
                        const links = document.querySelectorAll('nav a, [class*="MuiDrawer"] a, [class*="MuiListItem"] a');
                        for (const a of links) {{
                            if (a.innerText?.trim() === '{text}') {{
                                a.click();
                                return true;
                            }}
                        }}
                        return false;
                    }})()
                """)
                await asyncio.sleep(2)
                current_url = await cdp.evaluate("window.location.pathname")
                results.append({
                    "link_text": text,
                    "expected_href": href,
                    "actual_url": current_url,
                    "navigated": clicked,
                    "status": "PASS" if current_url and href and current_url.startswith(href.split("?")[0]) else "CHECK",
                })
            except Exception as e:
                results.append({
                    "link_text": text,
                    "expected_href": href,
                    "status": "ERROR",
                    "error": str(e)[:100],
                })
    else:
        results.append({"status": "WARN", "message": "No navigation links found or not a list"})

    return results


async def main():
    print("=" * 70)
    print("PashuRaksha Admin Dashboard - CDP UI Test")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"CDP: http://{CDP_HOST}:{CDP_PORT}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print()

    cdp = CDPClient()
    try:
        print("[1/4] Connecting to Chrome CDP...")
        await cdp.connect()
        await cdp.enable_domains()
        print("  Connected successfully.\n")

        # Phase 1: Test each page at desktop viewport
        print("[2/4] Testing pages at desktop viewport (1920x1080)...")
        print("-" * 70)
        all_results = []
        for path, name in PAGES:
            result = await test_page(cdp, path, name, 1920, 1080, "desktop-1920")
            status_icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX", "ERROR": "??"}.get(result["status"], "??")
            info = result["info"]
            extras = []
            if info.get("table_count"): extras.append(f"tables={info['table_count']}")
            if info.get("has_map"): extras.append("map=yes")
            if info.get("has_chart"): extras.append("chart=yes")
            if info.get("stat_cards"): extras.append(f"stat_cards={info['stat_cards']}")
            if info.get("mui_components"): extras.append(f"mui={info['mui_components']}")
            if info.get("nav_links"): extras.append(f"nav_links={info['nav_links']}")
            extras_str = f" [{', '.join(extras)}]" if extras else ""
            print(f"  [{status_icon}] {path:20s} {result['status']:6s}{extras_str}")
            if result["issues"]:
                for issue in result["issues"]:
                    print(f"       -> {issue}")
            if result["js_errors"]:
                for err in result["js_errors"][:2]:
                    print(f"       JS: {err[:120]}")
            all_results.append(result)

        # Phase 2: Responsive testing on key pages
        print(f"\n[3/4] Responsive viewport testing...")
        print("-" * 70)
        responsive_pages = [("/", "dashboard"), ("/farmers", "farmers"), ("/map", "map")]
        responsive_results = []
        for vw, vh, vlabel in VIEWPORTS:
            for path, name in responsive_pages:
                result = await test_page(cdp, path, name, vw, vh, vlabel)
                status_icon = {"PASS": "OK", "WARN": "!!", "FAIL": "XX", "ERROR": "??"}.get(result["status"], "??")
                print(f"  [{status_icon}] {vlabel:15s} {path:20s} {result['status']:6s} (scroll={result['info'].get('scroll_width','?')}, client={result['info'].get('client_width','?')})")
                if result["issues"]:
                    for issue in result["issues"]:
                        print(f"       -> {issue}")
                responsive_results.append(result)

        # Phase 3: Navigation test
        print(f"\n[4/4] Navigation link click test...")
        print("-" * 70)
        nav_results = await test_navigation(cdp)
        for nr in nav_results:
            if "link_text" in nr:
                status_icon = {"PASS": "OK", "CHECK": "??", "ERROR": "!!"}.get(nr["status"], "??")
                print(f"  [{status_icon}] '{nr['link_text']}' -> href={nr.get('expected_href','?')} actual={nr.get('actual_url','?')}")
            else:
                print(f"  [{nr['status']}] {nr.get('message','')}")

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        total = len(all_results)
        passed = sum(1 for r in all_results if r["status"] == "PASS")
        warned = sum(1 for r in all_results if r["status"] == "WARN")
        failed = sum(1 for r in all_results if r["status"] == "FAIL")
        errored = sum(1 for r in all_results if r["status"] == "ERROR")
        print(f"Pages tested: {total}")
        print(f"  PASS: {passed}")
        print(f"  WARN: {warned}")
        print(f"  FAIL: {failed}")
        print(f"  ERROR: {errored}")

        resp_overflow = sum(1 for r in responsive_results if r["info"].get("has_horizontal_overflow"))
        print(f"\nResponsive tests: {len(responsive_results)} ({resp_overflow} with overflow)")

        nav_ok = sum(1 for r in nav_results if r.get("status") == "PASS")
        print(f"Navigation links: {len(nav_results)} tested, {nav_ok} confirmed working")

        ss_count = len(list(SCREENSHOT_DIR.glob("*.png")))
        print(f"\nScreenshots saved: {ss_count} in {SCREENSHOT_DIR}")

        # Write JSON results
        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "base_url": BASE_URL,
            "pages": all_results,
            "responsive": responsive_results,
            "navigation": nav_results,
            "summary": {
                "total": total, "pass": passed, "warn": warned,
                "fail": failed, "error": errored,
                "responsive_overflow_count": resp_overflow,
            }
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
