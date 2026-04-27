"""
Mobile app comprehensive test — Expo 52 / React Native (web export)
Served at http://localhost:8081 (SPA — only / works for direct nav)
API at http://localhost:8000

Strategy:
  1. Log in via the actual OTP UI flow
  2. Navigate each screen using Expo Router links/tabs (UI clicks)
  3. Screenshot at mobile dimensions (390x844)
"""
import subprocess
import re
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, Page

BASE_URL    = "http://localhost:8081"
API_URL     = "http://localhost:8000"
PHONE       = "9900000002"          # without +91 prefix (app adds it)
SCREENSHOTS = Path("/home/sdamera/workbench/Social-Impact-Sprint/pashu-erp/e2e/screenshots/comprehensive")
SCREENSHOTS.mkdir(parents=True, exist_ok=True)

MOBILE_W = 390
MOBILE_H = 844


# ── Screens to visit ──────────────────────────────────────────────────────────
# Each entry: (label, navigation_method, nav_target, expected_text_hint)
#
# nav_method: "tab" | "link_text" | "href" | "home_button"
# nav_target: text for link_text; href fragment for href; tab label for tab
#
SCREENS = [
    # Tab bar
    ("tab_milk",      "tab",        "Milk",             "milk|litre|log"),
    ("tab_sell",      "tab",        "Sell",             "sell|market|price"),
    ("tab_health",    "tab",        "Health",           "health|vet|weight"),
    ("tab_income",    "tab",        "Income",           "income|revenue|earn"),
    ("tab_home",      "tab",        "Home",             "hello|farm|animal"),
    # Home-screen quick-links
    ("add_milk",      "link_text",  "Add Milk",         "milk|litre|log"),
    ("health_check",  "link_text",  "Health Check",     "health|weight|vet"),
    ("sell_screen",   "link_text",  "Sell",             "sell|market|price"),
    ("income_screen", "link_text",  "Income",           "income|revenue"),
    ("vaccination",   "link_text",  "Vaccination",      "vaccination|vaccine|due"),
    ("feeding",       "link_text",  "Feeding",          "feed|fodder|calculator"),
    ("weather",       "link_text",  "Weather",          "weather|rain|temp"),
    ("insurance",     "link_text",  "Insurance",        "insurance|policy|claim"),
    ("vet_help",      "link_text",  "Vet Help",         "vet|consult|photo"),
    ("my_consultations","link_text","My Consultations",  "consult|request|vet"),
]


def reset_rate_limits():
    subprocess.run(
        ["docker", "exec", "pashu-erp-db-1", "psql", "-U", "pashu", "-d", "pashuraksha",
         "-c", "UPDATE otp_requests SET request_count = 0, attempts = 0;"],
        capture_output=True, text=True, timeout=15,
    )


def do_login(page: Page) -> bool:
    """Complete OTP login via the app UI. Returns True on success."""
    page.goto(BASE_URL, wait_until="networkidle", timeout=30000)

    # Phone input
    phone_input = page.locator('input').first
    phone_input.fill(PHONE)
    page.get_by_text("Send OTP").click()
    page.wait_for_timeout(2000)

    # Read OTP from docker logs
    logs = subprocess.run(
        ["docker", "logs", "pashu-erp-api-1", "--tail", "15"],
        capture_output=True, text=True, timeout=15,
    )
    combined = logs.stdout + logs.stderr
    match = re.search(r"Code:\s*(\d{6})", combined)
    if not match:
        print("  ERROR: Could not find OTP in logs")
        print(f"  Log tail: {combined[-300:]}")
        return False

    otp = match.group(1)
    print(f"  OTP: {otp}")

    otp_boxes = page.locator('input[maxlength="1"]').all()
    if len(otp_boxes) != 6:
        print(f"  ERROR: Expected 6 OTP boxes, found {len(otp_boxes)}")
        return False

    for i, digit in enumerate(otp):
        otp_boxes[i].fill(digit)
        time.sleep(0.05)

    page.get_by_text("Verify OTP").click()
    page.wait_for_timeout(4000)

    # Check we landed on the home screen
    body = page.locator("body").inner_text(timeout=5000)
    if "invalid" in body.lower() or "expired" in body.lower():
        print(f"  ERROR: OTP verification failed: {body[:100]}")
        return False

    print(f"  Login OK — URL={page.url}")
    return True


def screenshot(page: Page, name: str) -> str:
    path = str(SCREENSHOTS / f"mobile_{name}.png")
    page.screenshot(path=path)
    return path


def body_text(page: Page) -> str:
    try:
        return page.locator("body").inner_text(timeout=3000)
    except Exception:
        return ""


def go_home(page: Page):
    """Navigate back to Home tab."""
    try:
        page.locator('[role="tab"]').filter(has_text="Home").click()
        page.wait_for_timeout(1000)
    except Exception:
        try:
            page.get_by_text("Home").last.click()
            page.wait_for_timeout(1000)
        except Exception:
            pass


def navigate_to(page: Page, method: str, target: str):
    """Click navigation element to reach a screen."""
    if method == "tab":
        # Click tab bar item
        tab = page.locator('[role="tab"]').filter(has_text=target)
        if tab.count() > 0:
            tab.first.click()
        else:
            # Fallback: find any clickable with that text at bottom
            page.get_by_text(target, exact=True).last.click()
        page.wait_for_timeout(1500)

    elif method == "link_text":
        # Click a link/button with matching text on the home screen.
        # First try a normal click; if the element is clipped inside
        # a horizontal ScrollView (common for quick-action items past
        # the viewport), fall back to clicking via JS dispatchEvent.
        go_home(page)
        page.wait_for_timeout(500)
        el = page.get_by_text(target, exact=True)
        if el.count() == 0:
            el = page.get_by_text(target)
        try:
            el.first.click(timeout=3000)
        except Exception:
            # JS click fallback — find the pressable parent and click it
            page.evaluate(
                """t => {
                    const all = document.querySelectorAll('[role="button"]');
                    for (const btn of all) {
                        if (btn.textContent.includes(t)) {
                            btn.dispatchEvent(new PointerEvent('pointerdown', {bubbles:true}));
                            btn.dispatchEvent(new PointerEvent('pointerup', {bubbles:true}));
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }""",
                target,
            )
        page.wait_for_timeout(2000)

    elif method == "href":
        page.evaluate(f"window.history.pushState(null, '', '{target}')")
        page.evaluate("window.dispatchEvent(new PopStateEvent('popstate', {state: null}))")
        page.wait_for_timeout(1500)


def probe_screen(page: Page, label: str, method: str, target: str,
                 hint: str, results: list, console_errors: list):
    errors_before = len(console_errors)
    print(f"  → {label}")
    try:
        navigate_to(page, method, target)
        url = page.url
        bt  = body_text(page)
        lower = bt.lower()

        # Classify
        crash_kw = ["something went wrong", "cannot read", "undefined is not",
                    "null is not", "typeerror", "referenceerror", "unexpected token"]
        crashed  = any(k in lower for k in crash_kw)
        blank    = len(bt.strip()) < 30
        on_login = "send otp" in lower

        hint_found = any(h in lower for h in hint.split("|"))
        errors_new = console_errors[errors_before:]

        if crashed:
            status = "CRASH"
        elif blank:
            status = "BLANK"
        elif on_login:
            status = "AUTH_LOST"
        else:
            status = "OK"

        shot = screenshot(page, label)
        flag = "hint✓" if hint_found else "no_hint"
        print(f"    {status} {flag}  url={url}  body={bt[:60].replace(chr(10),' ')!r}")

        results.append({
            "screen":       label,
            "method":       method,
            "target":       target,
            "status":       status,
            "url":          url,
            "hint_found":   hint_found,
            "body_preview": bt[:150].replace("\n", " "),
            "console_errors": [e[:120] for e in errors_new[:5]],
            "screenshot":   shot,
        })
    except Exception as exc:
        print(f"    ERROR: {exc}")
        try:
            shot = screenshot(page, f"{label}_error")
        except Exception:
            shot = ""
        results.append({
            "screen": label, "method": method, "target": target,
            "status": "ERROR", "error": str(exc)[:200], "screenshot": shot,
        })


def main():
    print("=" * 60)
    print("PashuRaksha Mobile — Comprehensive Screen Test")
    print("=" * 60)

    results:        list[dict] = []
    init_info:      dict       = {}
    console_errors: list[str]  = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": MOBILE_W, "height": MOBILE_H},
            user_agent=(
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Mobile Safari/537.36"
            ),
        )

        # ── [1] Initial load (unauthenticated) ──────────────────────────────
        print("\n[1] Initial load (unauthenticated)...")
        pg0 = context.new_page()
        init_errors: list[str] = []
        pg0.on("console", lambda m: init_errors.append(f"[{m.type}] {m.text}") if m.type == "error" else None)
        pg0.on("pageerror", lambda e: init_errors.append(f"[pageerror] {e}"))
        pg0.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        pg0.wait_for_timeout(1500)
        init_url  = pg0.url
        init_body = body_text(pg0)
        init_shot = screenshot(pg0, "00_initial_login_page")
        print(f"  URL={init_url}")
        print(f"  Body: {init_body[:120]!r}")
        print(f"  Console errors: {len(init_errors)}")
        for e in init_errors[:3]:
            print(f"    {e[:100]}")
        init_info = {
            "url": init_url, "body_preview": init_body[:300],
            "console_errors": init_errors[:10], "screenshot": init_shot,
        }
        pg0.close()

        # ── [2] Login ────────────────────────────────────────────────────────
        print("\n[2] Logging in via OTP UI flow...")
        reset_rate_limits()
        page = context.new_page()
        page.on("console", lambda m: console_errors.append(f"[{m.type}] {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda e: console_errors.append(f"[pageerror] {e}"))

        login_ok = do_login(page)
        if not login_ok:
            print("  FATAL: Login failed — aborting screen tour")
            page.close()
            browser.close()
            return

        # ── [3] Home screen ──────────────────────────────────────────────────
        print("\n[3] Capturing home screen...")
        home_shot = screenshot(page, "01_home_authenticated")
        home_body = body_text(page)
        print(f"  URL={page.url}  body={home_body[:100].replace(chr(10),' ')!r}")

        # ── [4] Screen tour ──────────────────────────────────────────────────
        print(f"\n[4] Probing {len(SCREENS)} screens...")
        for label, method, target, hint in SCREENS:
            probe_screen(page, label, method, target, hint, results, console_errors)
            # Return to home between home-button screens
            if method == "link_text":
                go_home(page)
                page.wait_for_timeout(300)

        page.close()
        browser.close()

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    by_status: dict[str, list] = {}
    for r in results:
        by_status.setdefault(r["status"], []).append(r)

    for status in ("OK", "CRASH", "BLANK", "AUTH_LOST", "ERROR"):
        items = by_status.get(status, [])
        if not items:
            continue
        print(f"\n  {status} ({len(items)}):")
        for r in items:
            hint = "hint✓" if r.get("hint_found") else "?"
            print(f"    [{hint}] {r['screen']:28s} via {r['method']}:{r['target']}")

    # Console errors
    all_errs = init_info.get("console_errors", []) + console_errors
    if all_errs:
        print(f"\nConsole errors ({len(all_errs)} total, unique below):")
        seen: set[str] = set()
        for e in all_errs:
            k = e[:90]
            if k not in seen:
                seen.add(k)
                print(f"  {k}")

    # Save report
    report = {
        "initial_load": init_info,
        "home_screen":  {"url": page.url if False else "N/A", "body": home_body[:400], "screenshot": home_shot},
        "screens":      results,
        "summary":      {s: len(v) for s, v in by_status.items()},
        "console_errors_total": len(all_errs),
    }
    rp = SCREENSHOTS / "mobile_test_report.json"
    rp.write_text(json.dumps(report, indent=2, default=str))
    print(f"\nReport: {rp}")
    print(f"Screenshots dir: {SCREENSHOTS}")


if __name__ == "__main__":
    main()
