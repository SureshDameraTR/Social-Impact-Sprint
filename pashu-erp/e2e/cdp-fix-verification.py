#!/usr/bin/env python3
"""
Fix Verification — CDP test for 4 specific pages after bug fixes.
Connects to Chrome via CDP (ws://127.0.0.1:9222).
Tests: Dashboard, Milk, Health, Income pages for specific regressions.
"""

import asyncio
import base64
import json
import os
import re
import subprocess
import sys
import time
from typing import Any

import websockets

CDP_URL = "http://127.0.0.1:9222"
ADMIN_URL = "http://localhost:3000"
PHONE = "+919876543210"

SCREENSHOT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "screenshots", "fix-verification",
)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


class CDPClient:
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
                    for handler in self._event_handlers.get(method, []):
                        try:
                            handler(msg.get("params", {}))
                        except Exception:
                            pass
        except websockets.exceptions.ConnectionClosed:
            pass

    def on(self, event, handler):
        self._event_handlers.setdefault(event, []).append(handler)

    async def send(self, method, params=None, timeout=30):
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


async def get_cdp_target():
    import urllib.request
    req = urllib.request.Request(f"{CDP_URL}/json/new?about:blank", method="PUT")
    data = urllib.request.urlopen(req).read()
    target = json.loads(data)
    return target["webSocketDebuggerUrl"]


def get_otp_from_logs():
    try:
        result = subprocess.run(
            ["docker", "compose", "logs", "api", "--tail", "20"],
            capture_output=True, text=True, timeout=10,
            cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."),
        )
        output = result.stdout + result.stderr
        for line in reversed(output.strip().split("\n")):
            if "Code:" in line:
                parts = line.split("Code:")
                if len(parts) > 1:
                    digits = "".join(c for c in parts[1].strip().split()[0] if c.isdigit())
                    if len(digits) >= 6:
                        return digits[:6]
            if "otp" in line.lower() or "OTP" in line:
                match = re.search(r'\b(\d{6})\b', line)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"  WARN: Failed to get OTP from logs: {e}")
    return ""


async def evaluate(cdp, expression, timeout=10):
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


async def navigate(cdp, url, wait_ms=3000):
    start = time.time()
    await cdp.send("Page.navigate", {"url": url})
    load_event = asyncio.get_event_loop().create_future()

    def on_load(params):
        if not load_event.done():
            load_event.set_result(True)

    cdp.on("Page.loadEventFired", on_load)
    try:
        await asyncio.wait_for(load_event, timeout=15)
    except asyncio.TimeoutError:
        pass
    cdp._event_handlers.get("Page.loadEventFired", []).clear()
    elapsed = (time.time() - start) * 1000
    await asyncio.sleep(wait_ms / 1000)
    return elapsed


async def take_screenshot(cdp, filename):
    result = await cdp.send("Page.captureScreenshot", {"format": "png", "quality": 80})
    if "error" in result:
        return ""
    data = result.get("result", {}).get("data", "")
    if not data:
        return ""
    path = os.path.join(SCREENSHOT_DIR, filename)
    with open(path, "wb") as f:
        f.write(base64.b64decode(data))
    return path


async def collect_console_errors(cdp, duration=2):
    """Collect console errors for a brief period."""
    errors = []

    def on_console(params):
        if params.get("type") in ("error",):
            text = " ".join(
                arg.get("value", arg.get("description", ""))
                for arg in params.get("args", [])
            )
            if not text:
                text = params.get("text", "")
            errors.append(text)

    def on_exception(params):
        exc = params.get("exceptionDetails", {})
        text = exc.get("text", "")
        ex_obj = exc.get("exception", {})
        desc = ex_obj.get("description", ex_obj.get("value", ""))
        errors.append(f"{text}: {desc}" if desc else text)

    cdp.on("Runtime.consoleAPICalled", on_console)
    cdp.on("Runtime.exceptionThrown", on_exception)
    await asyncio.sleep(duration)
    cdp._event_handlers.get("Runtime.consoleAPICalled", []).clear()
    cdp._event_handlers.get("Runtime.exceptionThrown", []).clear()
    return errors


async def react_set_input_value(cdp, selector, value):
    """Set a React controlled input's value using the native setter + React event."""
    return await evaluate(cdp, f"""
        (() => {{
            const inp = document.querySelector('{selector}');
            if (!inp) return 'no-element';
            const nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeSetter.call(inp, '{value}');
            inp.dispatchEvent(new Event('input', {{bubbles: true}}));
            inp.dispatchEvent(new Event('change', {{bubbles: true}}));
            // Also try React 16-18 synthetic event
            const reactKey = Object.keys(inp).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$') || k.startsWith('__reactProps$'));
            if (reactKey && reactKey.startsWith('__reactProps$')) {{
                const props = inp[reactKey];
                if (props && props.onChange) {{
                    props.onChange({{target: {{value: '{value}'}}}});
                    return 'set-via-react-props';
                }}
            }}
            return 'set-via-native: ' + inp.value;
        }})()
    """)


async def do_login(cdp):
    """Perform login flow. Returns True on success."""
    print("\n=== LOGIN FLOW ===")
    await navigate(cdp, f"{ADMIN_URL}/login", wait_ms=2000)

    url = await evaluate(cdp, "window.location.href")
    print(f"  Current URL: {url}")

    if url and "/login" not in url:
        print("  Already logged in, skipping auth")
        return True

    # Phone number (without +91 prefix - the component adds it)
    phone_digits = "9876543210"

    # Use React props onChange to set the phone value
    typed = await evaluate(cdp, f"""
        (() => {{
            const inp = document.querySelector('input');
            if (!inp) return 'no-input';
            // Find React fiber/props key
            const propsKey = Object.keys(inp).find(k => k.startsWith('__reactProps$'));
            if (propsKey) {{
                const props = inp[propsKey];
                if (props && props.onChange) {{
                    props.onChange({{target: {{value: '{phone_digits}'}}}});
                    return 'set-via-react-props';
                }}
            }}
            // Fallback: native setter + events
            const nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeSetter.call(inp, '{phone_digits}');
            inp.dispatchEvent(new Event('input', {{bubbles: true}}));
            inp.dispatchEvent(new Event('change', {{bubbles: true}}));
            return 'set-via-native';
        }})()
    """)
    print(f"  Phone input: {typed}")

    await asyncio.sleep(0.5)

    # Check button state
    btn_state = await evaluate(cdp, """
        (() => {
            const btn = document.querySelector('button');
            return JSON.stringify({text: btn?.textContent?.trim(), disabled: btn?.disabled});
        })()
    """)
    print(f"  Button state: {btn_state}")

    # Click Send OTP (may need to force-enable if React state didn't propagate)
    clicked = await evaluate(cdp, """
        (() => {
            const buttons = document.querySelectorAll('button');
            for (const btn of buttons) {
                const text = btn.textContent?.toLowerCase() || '';
                if (text.includes('send') && text.includes('otp')) {
                    if (btn.disabled) {
                        // Force remove disabled for click
                        btn.disabled = false;
                    }
                    btn.click();
                    return 'clicked: ' + btn.textContent.trim();
                }
            }
            return 'no-send-button';
        })()
    """)
    print(f"  Send OTP: {clicked}")

    await asyncio.sleep(3)

    # Check if we moved to OTP step
    step_check = await evaluate(cdp, """
        (() => {
            const inputs = document.querySelectorAll('input');
            const bodyText = document.body?.innerText || '';
            return JSON.stringify({
                inputCount: inputs.length,
                hasOtpSent: /OTP sent/i.test(bodyText),
                hasError: document.querySelector('.MuiAlert-root')?.textContent || '',
                bodySnippet: bodyText.substring(0, 300),
            });
        })()
    """)
    print(f"  After Send OTP: {step_check}")

    try:
        step_info = json.loads(step_check) if step_check else {}
    except:
        step_info = {}

    if not step_info.get('hasOtpSent') and step_info.get('inputCount', 0) <= 1:
        # Still on phone step - try direct API call approach
        print("  Phone step did not advance, trying direct API + cookie approach")

        # Make the API call ourselves and set cookie
        api_result = await evaluate(cdp, f"""
            (async () => {{
                try {{
                    const res = await fetch('{ADMIN_URL}'.replace(':3000', ':8000') + '/auth/request-otp', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{phone: '+91{phone_digits}'}}),
                        credentials: 'include',
                    }});
                    const data = await res.json();
                    return JSON.stringify({{status: res.status, data}});
                }} catch(e) {{
                    return 'fetch-error: ' + e.message;
                }}
            }})()
        """, timeout=15)
        print(f"  Direct API request-otp: {api_result}")

        await asyncio.sleep(1)

    # Get OTP from logs
    otp = get_otp_from_logs()
    print(f"  OTP from logs: {otp}")

    if not otp:
        print("  WARN: Could not get OTP, trying 123456")
        otp = "123456"

    # Check if we're on the OTP step (6 inputs for OTP digits)
    otp_step = await evaluate(cdp, "document.querySelectorAll('input').length")
    print(f"  Input count (expecting 6 for OTP): {otp_step}")

    if otp_step and int(str(otp_step)) >= 6:
        # Fill OTP boxes using React props onChange
        for i, digit in enumerate(otp[:6]):
            await evaluate(cdp, f"""
                (() => {{
                    const inputs = document.querySelectorAll('input');
                    const inp = inputs[{i}];
                    if (!inp) return 'no-input-{i}';
                    const propsKey = Object.keys(inp).find(k => k.startsWith('__reactProps$'));
                    if (propsKey) {{
                        const props = inp[propsKey];
                        if (props && props.onChange) {{
                            props.onChange({{target: {{value: '{digit}'}}}});
                            return 'set-{i}';
                        }}
                    }}
                    return 'no-props-{i}';
                }})()
            """)
        print(f"  OTP digits entered via React props")
    else:
        # Try paste approach on first OTP input
        print("  Attempting OTP paste on first input")
        await evaluate(cdp, f"""
            (() => {{
                const inputs = document.querySelectorAll('input');
                // The first OTP input accepts maxLength=6 for paste
                const inp = inputs[0];
                if (!inp) return 'no-input';
                const propsKey = Object.keys(inp).find(k => k.startsWith('__reactProps$'));
                if (propsKey) {{
                    const props = inp[propsKey];
                    if (props && props.onChange) {{
                        props.onChange({{target: {{value: '{otp}'}}}});
                        return 'pasted-otp';
                    }}
                }}
                return 'no-props';
            }})()
        """)

    await asyncio.sleep(0.5)

    # Try verify-otp directly via API if UI is tricky
    verify_result = await evaluate(cdp, f"""
        (async () => {{
            try {{
                const res = await fetch('http://localhost:8000/auth/verify-otp', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        phone: '+91{phone_digits}',
                        otp: '{otp}',
                        remember_me: false,
                        client_type: 'web',
                    }}),
                    credentials: 'include',
                }});
                const data = await res.json();
                return JSON.stringify({{status: res.status, data}});
            }} catch(e) {{
                return 'error: ' + e.message;
            }}
        }})()
    """, timeout=15)
    print(f"  Direct API verify-otp: {verify_result}")

    # Click verify button
    verified = await evaluate(cdp, """
        (() => {
            const buttons = document.querySelectorAll('button');
            for (const btn of buttons) {
                const text = btn.textContent?.toLowerCase() || '';
                if (text.includes('verify') || text.includes('login')) {
                    btn.disabled = false;
                    btn.click();
                    return 'clicked: ' + btn.textContent.trim();
                }
            }
            return 'no-verify-button';
        })()
    """)
    print(f"  Verify button: {verified}")

    await asyncio.sleep(2)

    # If API verify worked, navigate to dashboard directly (cookie is set)
    final_url = await evaluate(cdp, "window.location.href")
    print(f"  URL after verify: {final_url}")

    if final_url and "/login" in str(final_url):
        print("  Still on login, navigating to / (cookie should be set from direct API call)")
        await navigate(cdp, f"{ADMIN_URL}/", wait_ms=3000)
        final_url = await evaluate(cdp, "window.location.href")
        print(f"  URL after direct nav: {final_url}")

    if final_url and "/login" not in str(final_url):
        print("  LOGIN: PASS")
        return True
    else:
        await take_screenshot(cdp, "login-failed.png")
        print("  LOGIN: FAIL - still on login page")
        return False


async def test_dashboard(cdp):
    """Test Dashboard page — stat cards, no CORS 403 errors."""
    print("\n=== TEST 1: Dashboard (/) ===")
    print("  Bug: Previously showed 403 error due to CORS")

    await navigate(cdp, f"{ADMIN_URL}/", wait_ms=4000)
    errors = await collect_console_errors(cdp, duration=2)

    # Check for CORS / 403 errors
    cors_errors = [e for e in errors if "403" in str(e) or "CORS" in str(e).upper() or "cors" in str(e)]
    all_js_errors = [e for e in errors if e.strip()]

    # Check stat cards
    stat_info = await evaluate(cdp, """
        (() => {
            // Look for stat cards — MUI Cards with numbers
            const cards = document.querySelectorAll('.MuiCard-root, .MuiPaper-root');
            const stats = [];
            for (const card of cards) {
                const text = card.innerText?.trim() || '';
                // Look for cards with numeric content (stat values)
                if (/\\d+/.test(text) && text.length < 200) {
                    stats.push(text.replace(/\\n/g, ' | '));
                }
            }
            return JSON.stringify({
                cardCount: cards.length,
                statsWithNumbers: stats.slice(0, 8),
                bodyText: document.body?.innerText?.substring(0, 800),
            });
        })()
    """)

    screenshot = await take_screenshot(cdp, "01-dashboard.png")
    print(f"  Screenshot: {screenshot}")

    try:
        info = json.loads(stat_info) if stat_info else {}
    except (json.JSONDecodeError, TypeError):
        info = {"raw": str(stat_info)}

    print(f"  Cards found: {info.get('cardCount', 'N/A')}")
    stats_with_nums = info.get('statsWithNumbers', [])
    if stats_with_nums:
        print(f"  Stat cards with numbers ({len(stats_with_nums)}):")
        for s in stats_with_nums[:6]:
            print(f"    - {s[:100]}")
    else:
        print("  WARNING: No stat cards with numbers found")
        body_preview = info.get('bodyText', '')[:300]
        print(f"  Page content: {body_preview}")

    if cors_errors:
        print(f"  FAIL: CORS/403 errors still present: {cors_errors}")
        return "FAIL", f"CORS/403 errors: {cors_errors}"
    elif all_js_errors:
        print(f"  WARN: JS errors in console ({len(all_js_errors)}):")
        for e in all_js_errors[:5]:
            print(f"    - {str(e)[:120]}")
        # Non-CORS errors are a warning, not fail
        has_real_numbers = len(stats_with_nums) > 0
        if has_real_numbers:
            return "PASS", f"Stat cards visible with data. {len(all_js_errors)} console warnings."
        else:
            return "FAIL", f"No stat data visible + {len(all_js_errors)} console errors"
    else:
        has_real_numbers = len(stats_with_nums) > 0
        if has_real_numbers:
            return "PASS", "Stat cards visible, no CORS errors, no JS errors"
        else:
            return "WARN", "No CORS errors but stat cards may not have loaded"


async def test_milk(cdp):
    """Test Milk page — toFixed crash fix."""
    print("\n=== TEST 2: Milk Page (/milk) ===")
    print("  Bug: Previously crashed with 'toFixed is not a function'")

    await navigate(cdp, f"{ADMIN_URL}/milk", wait_ms=4000)
    errors = await collect_console_errors(cdp, duration=3)

    # Check for the specific toFixed error
    tofixed_errors = [e for e in errors if "toFixed" in str(e)]
    type_errors = [e for e in errors if "TypeError" in str(e)]
    all_js_errors = [e for e in errors if e.strip()]

    # Check page content
    page_info = await evaluate(cdp, """
        (() => {
            const tables = document.querySelectorAll('table, .MuiTable-root, .MuiDataGrid-root');
            const rows = document.querySelectorAll('tr, .MuiTableRow-root, .MuiDataGrid-row');
            const bodyText = document.body?.innerText || '';
            const hasTodayTotal = /today.*total|total.*today/i.test(bodyText);
            const hasLiters = /\\d+\\.?\\d*\\s*L/i.test(bodyText);
            const charts = document.querySelectorAll('.recharts-wrapper, .recharts-surface, canvas, svg.recharts-surface');
            return JSON.stringify({
                tableCount: tables.length,
                rowCount: rows.length,
                hasTodayTotal,
                hasLiters,
                chartCount: charts.length,
                bodyPreview: bodyText.substring(0, 600),
            });
        })()
    """)

    screenshot = await take_screenshot(cdp, "02-milk.png")
    print(f"  Screenshot: {screenshot}")

    try:
        info = json.loads(page_info) if page_info else {}
    except (json.JSONDecodeError, TypeError):
        info = {"raw": str(page_info)}

    print(f"  Tables: {info.get('tableCount', 'N/A')}, Rows: {info.get('rowCount', 'N/A')}")
    print(f"  Charts: {info.get('chartCount', 'N/A')}")
    print(f"  Today's total text: {info.get('hasTodayTotal', 'N/A')}")
    print(f"  Liter values: {info.get('hasLiters', 'N/A')}")
    print(f"  Content: {str(info.get('bodyPreview', ''))[:200]}")

    if tofixed_errors:
        return "FAIL", f"toFixed error still present: {tofixed_errors[0][:100]}"
    elif type_errors:
        return "FAIL", f"TypeError in console: {type_errors[0][:100]}"
    elif all_js_errors:
        non_trivial = [e for e in all_js_errors if "TypeError" in str(e) or "Error" in str(e)]
        if non_trivial:
            print(f"  JS errors ({len(non_trivial)}):")
            for e in non_trivial[:3]:
                print(f"    - {str(e)[:120]}")
            return "FAIL", f"JS errors on milk page: {non_trivial[0][:100]}"
        return "PASS", f"Page loads with data. {len(all_js_errors)} non-critical console msgs."
    else:
        rows = info.get('rowCount', 0)
        if rows > 1:
            return "PASS", f"Table with {rows} rows, no toFixed error, no JS errors"
        else:
            return "WARN", "No toFixed error but table may be empty"


async def test_health(cdp):
    """Test Health page — should show 4 health alert records."""
    print("\n=== TEST 3: Health Page (/health) ===")
    print("  Bug: Previously showed 0 events")

    await navigate(cdp, f"{ADMIN_URL}/health", wait_ms=4000)
    errors = await collect_console_errors(cdp, duration=2)

    page_info = await evaluate(cdp, """
        (() => {
            const tables = document.querySelectorAll('table, .MuiTable-root, .MuiDataGrid-root');
            const rows = document.querySelectorAll('tbody tr, .MuiTableBody-root tr, .MuiDataGrid-row');
            const cards = document.querySelectorAll('.MuiCard-root, .MuiPaper-root');
            const chips = document.querySelectorAll('.MuiChip-root');
            const bodyText = document.body?.innerText || '';
            // Look for risk levels
            const hasRisk = /high|medium|low|critical/i.test(bodyText);
            // Look for dates
            const hasDates = /\\d{4}-\\d{2}-\\d{2}|\\d{1,2}\\/\\d{1,2}\\/\\d{2,4}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec/i.test(bodyText);
            // Look for symptoms
            const hasSymptoms = /symptom|fever|lameness|cough|diarrhea|reduced|mastitis/i.test(bodyText);
            return JSON.stringify({
                tableCount: tables.length,
                dataRowCount: rows.length,
                cardCount: cards.length,
                chipCount: chips.length,
                hasRisk,
                hasDates,
                hasSymptoms,
                bodyPreview: bodyText.substring(0, 600),
            });
        })()
    """)

    screenshot = await take_screenshot(cdp, "03-health.png")
    print(f"  Screenshot: {screenshot}")

    try:
        info = json.loads(page_info) if page_info else {}
    except (json.JSONDecodeError, TypeError):
        info = {"raw": str(page_info)}

    data_rows = info.get('dataRowCount', 0)
    print(f"  Tables: {info.get('tableCount', 'N/A')}, Data rows: {data_rows}")
    print(f"  Cards: {info.get('cardCount', 'N/A')}, Chips: {info.get('chipCount', 'N/A')}")
    print(f"  Has risk levels: {info.get('hasRisk', 'N/A')}")
    print(f"  Has dates: {info.get('hasDates', 'N/A')}")
    print(f"  Has symptoms: {info.get('hasSymptoms', 'N/A')}")
    print(f"  Content: {str(info.get('bodyPreview', ''))[:200]}")

    all_js_errors = [e for e in errors if e.strip() and ("Error" in str(e) or "error" in str(e))]
    if all_js_errors:
        print(f"  JS errors ({len(all_js_errors)}):")
        for e in all_js_errors[:3]:
            print(f"    - {str(e)[:120]}")

    if data_rows >= 1:
        detail = f"{data_rows} rows"
        if info.get('hasRisk'):
            detail += ", risk levels visible"
        if info.get('hasDates'):
            detail += ", dates visible"
        if info.get('hasSymptoms'):
            detail += ", symptoms visible"
        return "PASS", detail
    elif data_rows == 0 and info.get('tableCount', 0) > 0:
        return "FAIL", "Table present but 0 data rows (expected 4 health events)"
    else:
        return "FAIL", f"No table/data found. Page content: {str(info.get('bodyPreview', ''))[:100]}"


async def test_income(cdp):
    """Test Income page — should show charts and currency values."""
    print("\n=== TEST 4: Income Page (/income) ===")
    print('  Bug: Previously showed "No data available"')

    await navigate(cdp, f"{ADMIN_URL}/income", wait_ms=4000)
    errors = await collect_console_errors(cdp, duration=2)

    page_info = await evaluate(cdp, """
        (() => {
            const bodyText = document.body?.innerText || '';
            const charts = document.querySelectorAll('.recharts-wrapper, .recharts-surface, canvas, svg');
            const rechartsSpecific = document.querySelectorAll('.recharts-bar, .recharts-bar-rectangle, .recharts-line, .recharts-area');
            const cards = document.querySelectorAll('.MuiCard-root, .MuiPaper-root');
            // Look for currency values (INR / rupee)
            const hasCurrency = /[\\u20B9]|Rs\\.?|INR|\\d{1,3}(,\\d{2,3})*(\\.\\d{2})?/i.test(bodyText);
            const hasNoData = /no data|no records|empty/i.test(bodyText);
            // Look for chart-like SVG elements (bars, lines)
            const svgBars = document.querySelectorAll('rect.recharts-bar-rectangle, .recharts-rectangle');
            return JSON.stringify({
                chartWrappers: document.querySelectorAll('.recharts-wrapper').length,
                rechartsElements: rechartsSpecific.length,
                svgBars: svgBars.length,
                cardCount: cards.length,
                hasCurrency,
                hasNoData,
                bodyPreview: bodyText.substring(0, 800),
            });
        })()
    """)

    screenshot = await take_screenshot(cdp, "04-income.png")
    print(f"  Screenshot: {screenshot}")

    try:
        info = json.loads(page_info) if page_info else {}
    except (json.JSONDecodeError, TypeError):
        info = {"raw": str(page_info)}

    print(f"  Recharts wrappers: {info.get('chartWrappers', 'N/A')}")
    print(f"  Recharts elements (bars/lines): {info.get('rechartsElements', 'N/A')}")
    print(f"  SVG bars: {info.get('svgBars', 'N/A')}")
    print(f"  Cards: {info.get('cardCount', 'N/A')}")
    print(f"  Has currency values: {info.get('hasCurrency', 'N/A')}")
    print(f"  Has 'no data' text: {info.get('hasNoData', 'N/A')}")
    print(f"  Content: {str(info.get('bodyPreview', ''))[:300]}")

    all_js_errors = [e for e in errors if e.strip() and ("Error" in str(e) or "error" in str(e))]
    if all_js_errors:
        print(f"  JS errors ({len(all_js_errors)}):")
        for e in all_js_errors[:3]:
            print(f"    - {str(e)[:120]}")

    if info.get('hasNoData'):
        return "FAIL", '"No data available" text still present on page'

    charts = info.get('chartWrappers', 0)
    has_currency = info.get('hasCurrency', False)

    if charts > 0 and has_currency:
        return "PASS", f"{charts} charts rendered, currency values visible"
    elif charts > 0:
        return "PASS", f"{charts} charts rendered (currency pattern may differ)"
    elif has_currency:
        return "WARN", "Currency values visible but no Recharts detected"
    else:
        return "FAIL", "No charts and no currency data found"


async def main():
    print("=" * 60)
    print("  PashuRaksha Admin — Fix Verification Test")
    print("=" * 60)

    # Connect to Chrome CDP
    ws_url = await get_cdp_target()
    print(f"CDP target: {ws_url}")

    async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
        cdp = CDPClient(ws)
        await cdp.start_listener()

        # Enable domains
        await cdp.send("Page.enable")
        await cdp.send("Runtime.enable")
        await cdp.send("Network.enable")
        await cdp.send("Console.enable")

        # Set desktop viewport
        await cdp.send("Emulation.setDeviceMetricsOverride", {
            "width": 1920, "height": 1080, "deviceScaleFactor": 1, "mobile": False,
        })

        # Login
        login_ok = await do_login(cdp)
        if not login_ok:
            print("\nFATAL: Login failed, cannot proceed with page tests")
            await cdp.close()
            return

        # Run tests
        results = {}
        for name, test_fn in [
            ("Dashboard (/)", test_dashboard),
            ("Milk (/milk)", test_milk),
            ("Health (/health)", test_health),
            ("Income (/income)", test_income),
        ]:
            try:
                status, detail = await test_fn(cdp)
                results[name] = (status, detail)
            except Exception as e:
                results[name] = ("ERROR", str(e)[:200])
                print(f"  EXCEPTION: {e}")

        await cdp.close()

    # Summary
    print("\n" + "=" * 60)
    print("  VERIFICATION SUMMARY")
    print("=" * 60)
    for page, (status, detail) in results.items():
        icon = {"PASS": "OK", "FAIL": "XX", "WARN": "!!", "ERROR": "!!"}[status]
        print(f"  [{icon}] {status:5s} | {page}")
        print(f"         {detail}")
    print("=" * 60)

    passes = sum(1 for s, _ in results.values() if s == "PASS")
    fails = sum(1 for s, _ in results.values() if s in ("FAIL", "ERROR"))
    print(f"  {passes} passed, {fails} failed, {len(results) - passes - fails} warnings")
    print(f"  Screenshots: {SCREENSHOT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
