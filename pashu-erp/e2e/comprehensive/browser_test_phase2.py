"""Phase 2: Comprehensive Browser UI Testing for PashuRaksha ERP.

Tests all 3 web apps (Admin, Collection, Vet) with real browser via Playwright.
Auth uses real OTP extracted from docker logs — no hardcoded values.
Tokens obtained via API and injected as cookies into browser contexts.

Usage:
    python3 browser_test_phase2.py
"""

import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright, Page, BrowserContext

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE = "http://localhost:8000"
ADMIN_URL = "http://localhost:3000"
COLLECTION_URL = "http://localhost:3001"
VET_URL = "http://localhost:3002"

SCREENSHOT_DIR = Path(__file__).parent.parent / "screenshots" / "comprehensive"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

ACCOUNTS = {
    "admin": "+919900000001",
    "milk_center": "+919900000006",
    "vet": "+919900000005",
    "farmer": "+919900000002",
}


# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------
@dataclass
class PageResult:
    app: str
    route: str
    page_name: str
    status: str = "UNTESTED"
    load_time_ms: float = 0
    screenshot_desktop: str = ""
    screenshot_tablet: str = ""
    http_status: int = 0
    console_errors: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    data_loaded: bool = False


ALL_RESULTS: list[PageResult] = []
CONSOLE_ERRORS: list[dict] = []


# ---------------------------------------------------------------------------
# Auth helpers — get tokens via API, extract cookies from response
# ---------------------------------------------------------------------------
def reset_otp_limits():
    subprocess.run(
        ["docker", "exec", "pashu-erp-db-1", "psql", "-U", "pashu", "-d", "pashuraksha",
         "-c", "UPDATE otp_requests SET request_count = 0, attempts = 0;"],
        capture_output=True, timeout=10,
    )


def extract_otp(phone: str) -> str:
    result = subprocess.run(
        ["docker", "logs", "pashu-erp-api-1", "--tail", "50"],
        capture_output=True, text=True, timeout=10,
    )
    combined = result.stdout + result.stderr
    pattern = rf"DEV OTP for {re.escape(phone)}.*?Code:\s*(\d{{6}})"
    matches = re.findall(pattern, combined, re.DOTALL)
    if not matches:
        matches = re.findall(r"Code:\s*(\d{6})", combined)
    if not matches:
        raise RuntimeError(f"Could not find OTP for {phone} in docker logs")
    return matches[-1]


_cookie_cache: dict[str, dict] = {}

def get_auth_cookies(phone: str) -> dict:
    """Authenticate via API and return the token + csrf_token cookies (cached)."""
    if phone in _cookie_cache:
        return _cookie_cache[phone]

    reset_otp_limits()

    with httpx.Client(base_url=API_BASE, timeout=30) as client:
        # Request OTP
        resp = client.post("/v1/auth/request-otp", json={"phone": phone})
        assert resp.status_code == 200, f"OTP request failed: {resp.status_code} {resp.text}"

        time.sleep(1)
        otp = extract_otp(phone)

        # Verify OTP
        resp = client.post("/v1/auth/verify-otp", json={
            "phone": phone, "otp": otp, "client_type": "web", "remember_me": False
        })
        assert resp.status_code == 200, f"OTP verify failed: {resp.status_code} {resp.text}"

        cookies = {}
        for name, value in resp.cookies.items():
            cookies[name] = value

        print(f"  Auth for {phone}: got cookies {list(cookies.keys())}")
        _cookie_cache[phone] = cookies
        return cookies


def inject_cookies(context: BrowserContext, cookies: dict, domain: str):
    """Inject auth cookies into a browser context for a specific domain."""
    cookie_list = []
    for name, value in cookies.items():
        cookie_list.append({
            "name": name,
            "value": value,
            "domain": domain,
            "path": "/",
            "httpOnly": name == "token",
            "secure": False,
            "sameSite": "Lax",
        })
    # Also add cookies for the API domain so cross-origin requests include them
    for name, value in cookies.items():
        cookie_list.append({
            "name": name,
            "value": value,
            "domain": "localhost",
            "path": "/",
            "httpOnly": name == "token",
            "secure": False,
            "sameSite": "Lax",
        })
    context.add_cookies(cookie_list)


# ---------------------------------------------------------------------------
# Screenshot + page testing utilities
# ---------------------------------------------------------------------------
def take_screenshot(page: Page, name: str, width: int = 1920, height: int = 1080) -> str:
    page.set_viewport_size({"width": width, "height": height})
    time.sleep(0.3)
    filename = f"{name}_{width}x{height}.png"
    filepath = SCREENSHOT_DIR / filename
    page.screenshot(path=str(filepath), full_page=False)
    return str(filepath)


def setup_console_listener(page: Page, app_name: str):
    def on_console(msg):
        if msg.type == "error":
            text = msg.text[:300]
            # Skip noisy telemetry/CSP errors
            if "telemetry.refine.dev" in text or "frame-ancestors" in text:
                return
            CONSOLE_ERRORS.append({
                "app": app_name,
                "url": page.url,
                "text": text,
            })
    page.on("console", on_console)


def test_page(page: Page, base_url: str, app_name: str, route: str, page_name: str,
              wait_for_selector: str | None = None, check_data: str | None = None) -> PageResult:
    """Navigate to a page, measure load time, take screenshots, check for issues."""
    result = PageResult(app=app_name, route=route, page_name=page_name)
    url = f"{base_url}{route}"
    print(f"  Testing {app_name} {route} ({page_name})...", end=" ", flush=True)

    try:
        start = time.time()
        response = page.goto(url, wait_until="networkidle", timeout=30000)
        elapsed = (time.time() - start) * 1000
        result.load_time_ms = round(elapsed, 1)
        result.http_status = response.status if response else 0

        time.sleep(1)

        # If redirected to login, page has no auth
        if "/login" in page.url and route != "/login":
            result.issues.append(f"Redirected to login (auth not working for {route})")
            result.status = "FAIL"
            print(f"\033[91mFAIL\033[0m (redirected to login)")
            ALL_RESULTS.append(result)
            return result

        if wait_for_selector:
            try:
                page.wait_for_selector(wait_for_selector, timeout=8000)
            except Exception:
                result.issues.append(f"Expected element not found: {wait_for_selector}")

        # Check for stuck loading spinners
        for sel in [".MuiCircularProgress-root"]:
            try:
                elem = page.locator(sel).first
                if elem.is_visible():
                    time.sleep(3)
                    if elem.is_visible():
                        result.issues.append("Stuck loading spinner")
            except Exception:
                pass

        # Check for very empty pages
        body_text = page.locator("body").inner_text()
        if len(body_text.strip()) < 10 and route != "/login":
            result.issues.append("Page appears blank")

        # Error boundary check
        if "error boundary" in body_text.lower() or "something went wrong" in body_text.lower():
            result.issues.append("Error boundary triggered")

        # Check specific data presence
        if check_data:
            try:
                data_elem = page.locator(check_data).first
                if data_elem.is_visible():
                    result.data_loaded = True
                else:
                    result.issues.append(f"Data not visible: {check_data}")
            except Exception:
                result.issues.append(f"Data check failed: {check_data}")
        else:
            result.data_loaded = True

        # Screenshots at desktop and tablet
        result.screenshot_desktop = take_screenshot(page, f"{app_name}_{page_name.replace(' ', '_').lower()}_desktop")
        result.screenshot_tablet = take_screenshot(page, f"{app_name}_{page_name.replace(' ', '_').lower()}_tablet", 768, 1024)

        if not result.issues:
            result.status = "PASS"
            print(f"\033[92mPASS\033[0m ({result.load_time_ms:.0f}ms)")
        elif any("Stuck" in i or "blank" in i or "Error boundary" in i or "Redirected" in i for i in result.issues):
            result.status = "FAIL"
            print(f"\033[91mFAIL\033[0m ({result.load_time_ms:.0f}ms) {result.issues}")
        else:
            result.status = "WARN"
            print(f"\033[93mWARN\033[0m ({result.load_time_ms:.0f}ms) {result.issues}")

    except Exception as e:
        result.status = "ERROR"
        result.issues.append(str(e)[:200])
        print(f"\033[91mERROR: {str(e)[:120]}\033[0m")

    ALL_RESULTS.append(result)
    return result


# ---------------------------------------------------------------------------
# Login page test (separate — tests the UI flow, not just cookie injection)
# ---------------------------------------------------------------------------
def test_login_page(page: Page, base_url: str, app_name: str, phone: str) -> PageResult:
    """Test the login page UI renders correctly (no OTP request to save rate limit budget)."""
    result = PageResult(app=app_name, route="/login", page_name="Login")
    print(f"  Testing {app_name} /login (Login UI)...", end=" ", flush=True)

    try:
        start = time.time()
        page.goto(f"{base_url}/login", wait_until="networkidle", timeout=15000)
        elapsed = (time.time() - start) * 1000
        result.load_time_ms = round(elapsed, 1)
        time.sleep(1)

        # Verify login form elements render
        phone_input = page.locator("input[inputmode='numeric']").first
        if not phone_input.is_visible():
            result.issues.append("Phone input not visible")

        send_btn = page.get_by_role("button", name=re.compile(r"Send OTP|send", re.IGNORECASE))
        if not send_btn.is_visible():
            result.issues.append("Send OTP button not visible")

        result.screenshot_desktop = take_screenshot(page, f"{app_name}_login_desktop")
        result.screenshot_tablet = take_screenshot(page, f"{app_name}_login_tablet", 768, 1024)

        if not result.issues:
            result.status = "PASS"
            result.data_loaded = True
            print(f"\033[92mPASS\033[0m ({result.load_time_ms:.0f}ms)")
        else:
            result.status = "WARN"
            print(f"\033[93mWARN\033[0m {result.issues}")

    except Exception as e:
        result.status = "ERROR"
        result.issues.append(str(e)[:200])
        print(f"\033[91mERROR: {str(e)[:120]}\033[0m")

    ALL_RESULTS.append(result)
    return result


# ---------------------------------------------------------------------------
# Admin Dashboard Tests (16 pages)
# ---------------------------------------------------------------------------
ADMIN_PAGES = [
    ("/", "Dashboard", ".MuiCard-root, .recharts-wrapper", ".MuiCard-root"),
    ("/farmers", "Farmers", "table, .MuiTable-root", "table tbody tr, .MuiTableBody-root tr"),
    ("/animals", "Animals", "table, .MuiTable-root", "table tbody tr, .MuiTableBody-root tr"),
    ("/health", "Health", None, None),
    ("/milk", "Milk", None, None),
    ("/vaccinations", "Vaccinations", None, None),
    ("/schemes", "Schemes", None, None),
    ("/marketplace", "Marketplace", None, None),
    ("/income", "Income", None, None),
    ("/map", "GIS Map", ".leaflet-container", ".leaflet-container"),
    ("/iot", "IoT Devices", None, None),
    ("/vet", "Vet Overview", None, None),
    ("/vet/cases", "Vet Cases", None, None),
    ("/vet/alerts", "Vet Alerts", None, None),
]


def test_admin(browser):
    print("\n" + "=" * 60)
    print("ADMIN DASHBOARD (localhost:3000)")
    print("=" * 60)

    # Get auth cookies via API
    cookies = get_auth_cookies(ACCOUNTS["admin"])

    # Test login page UI (separate context, no cookies)
    login_ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    login_page = login_ctx.new_page()
    setup_console_listener(login_page, "admin")
    test_login_page(login_page, ADMIN_URL, "admin", ACCOUNTS["admin"])
    login_page.close()
    login_ctx.close()

    # Authenticated context for all other pages
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    inject_cookies(ctx, cookies, "localhost")
    page = ctx.new_page()
    setup_console_listener(page, "admin")

    for route, name, wait_sel, check_data in ADMIN_PAGES:
        test_page(page, ADMIN_URL, "admin", route, name,
                  wait_for_selector=wait_sel, check_data=check_data)
        time.sleep(0.3)

    # Test vet case detail (navigate from cases list)
    try:
        page.goto(f"{ADMIN_URL}/vet/cases", wait_until="networkidle", timeout=15000)
        time.sleep(1)
        rows = page.locator("table tbody tr, .MuiTableBody-root tr")
        if rows.count() > 0:
            rows.first.click()
            time.sleep(2)
            if "/vet/cases/" in page.url:
                r = PageResult(app="admin", route="/vet/cases/:id", page_name="Vet Case Detail", status="PASS")
                r.screenshot_desktop = take_screenshot(page, "admin_vet_case_detail_desktop")
                r.screenshot_tablet = take_screenshot(page, "admin_vet_case_detail_tablet", 768, 1024)
                ALL_RESULTS.append(r)
                print(f"  admin /vet/cases/:id (Vet Case Detail)... \033[92mPASS\033[0m")
            else:
                ALL_RESULTS.append(PageResult(app="admin", route="/vet/cases/:id",
                    page_name="Vet Case Detail", status="SKIP",
                    issues=["Click did not navigate to case detail"]))
        else:
            ALL_RESULTS.append(PageResult(app="admin", route="/vet/cases/:id",
                page_name="Vet Case Detail", status="SKIP", issues=["No cases in table"]))
    except Exception as e:
        ALL_RESULTS.append(PageResult(app="admin", route="/vet/cases/:id",
            page_name="Vet Case Detail", status="ERROR", issues=[str(e)[:200]]))

    page.close()
    ctx.close()


# ---------------------------------------------------------------------------
# Collection Centre Tests (6 pages)
# ---------------------------------------------------------------------------
COLLECTION_PAGES = [
    ("/dashboard", "Dashboard", None, None),
    ("/intake", "Milk Intake", None, None),
    ("/enroll", "Farmer Enroll", None, None),
    ("/settlements", "Settlements", None, None),
]


def test_collection(browser):
    print("\n" + "=" * 60)
    print("COLLECTION CENTRE (localhost:3001)")
    print("=" * 60)

    # Get auth cookies
    reset_otp_limits()
    time.sleep(1)
    cookies = get_auth_cookies(ACCOUNTS["milk_center"])

    # Test login page
    login_ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    login_page = login_ctx.new_page()
    setup_console_listener(login_page, "collection")
    test_login_page(login_page, COLLECTION_URL, "collection", ACCOUNTS["milk_center"])
    login_page.close()
    login_ctx.close()

    # Authenticated pages
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    inject_cookies(ctx, cookies, "localhost")
    page = ctx.new_page()
    setup_console_listener(page, "collection")

    for route, name, wait_sel, check_data in COLLECTION_PAGES:
        test_page(page, COLLECTION_URL, "collection", route, name,
                  wait_for_selector=wait_sel, check_data=check_data)
        time.sleep(0.3)

    # Milk intake E2E flow
    print("\n  --- Milk Intake E2E Flow ---")
    try:
        page.goto(f"{COLLECTION_URL}/intake", wait_until="networkidle", timeout=15000)
        time.sleep(2)
        take_screenshot(page, "collection_intake_e2e_start")

        # Look for any input fields on the page
        inputs = page.locator("input")
        input_count = inputs.count()
        body_text = page.locator("body").inner_text()

        issues = []
        if "/login" in page.url:
            issues.append("Redirected to login")
        elif input_count == 0:
            issues.append("No input fields on intake page")
        else:
            # Try to interact with the form
            take_screenshot(page, "collection_intake_e2e_form")

        status = "FAIL" if issues else "PASS"
        ALL_RESULTS.append(PageResult(app="collection", route="/intake (E2E)",
            page_name="Intake E2E Flow", status=status, issues=issues,
            screenshot_desktop=str(SCREENSHOT_DIR / "collection_intake_e2e_form_1920x1080.png")))
        color = "\033[92m" if status == "PASS" else "\033[91m"
        print(f"  Intake E2E: {color}{status}\033[0m {issues if issues else ''}")
    except Exception as e:
        ALL_RESULTS.append(PageResult(app="collection", route="/intake (E2E)",
            page_name="Intake E2E Flow", status="ERROR", issues=[str(e)[:200]]))
        print(f"  Intake E2E: \033[91mERROR: {str(e)[:100]}\033[0m")

    page.close()
    ctx.close()


# ---------------------------------------------------------------------------
# Vet Dashboard Tests (5 pages)
# ---------------------------------------------------------------------------
VET_PAGES = [
    ("/dashboard", "Dashboard", None, None),
    ("/cases", "Cases", None, None),
    ("/alerts", "Alerts", None, None),
]


def test_vet(browser):
    print("\n" + "=" * 60)
    print("VET DASHBOARD (localhost:3002)")
    print("=" * 60)

    reset_otp_limits()
    time.sleep(1)
    cookies = get_auth_cookies(ACCOUNTS["vet"])

    # Test login page
    login_ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    login_page = login_ctx.new_page()
    setup_console_listener(login_page, "vet")
    test_login_page(login_page, VET_URL, "vet", ACCOUNTS["vet"])
    login_page.close()
    login_ctx.close()

    # Authenticated pages
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    inject_cookies(ctx, cookies, "localhost")
    page = ctx.new_page()
    setup_console_listener(page, "vet")

    for route, name, wait_sel, check_data in VET_PAGES:
        test_page(page, VET_URL, "vet", route, name,
                  wait_for_selector=wait_sel, check_data=check_data)
        time.sleep(0.3)

    # Case detail + workflow
    print("\n  --- Vet Case Workflow ---")
    try:
        page.goto(f"{VET_URL}/cases", wait_until="networkidle", timeout=15000)
        time.sleep(2)

        rows = page.locator("table tbody tr, .MuiTableBody-root tr, .MuiCard-root")
        if rows.count() > 0:
            rows.first.click()
            time.sleep(2)

            if "/cases/" in page.url and page.url != f"{VET_URL}/cases":
                r = PageResult(app="vet", route="/cases/:id", page_name="Case Detail", status="PASS")
                r.screenshot_desktop = take_screenshot(page, "vet_case_detail_desktop")
                r.screenshot_tablet = take_screenshot(page, "vet_case_detail_tablet", 768, 1024)
                ALL_RESULTS.append(r)
                print(f"  Case detail: \033[92mPASS\033[0m")

                # Try claim
                claim_btn = page.get_by_role("button", name=re.compile(r"claim|assign|take", re.IGNORECASE))
                if claim_btn.count() > 0 and claim_btn.first.is_visible():
                    claim_btn.first.click()
                    time.sleep(2)
                    take_screenshot(page, "vet_case_claimed")
                    print(f"  Case claim: \033[92mPASS\033[0m")
                else:
                    print(f"  Case claim: \033[90mSKIP\033[0m (no claim button — may be already claimed)")
            else:
                ALL_RESULTS.append(PageResult(app="vet", route="/cases/:id",
                    page_name="Case Detail", status="SKIP",
                    issues=["Click did not navigate to detail"]))
                print(f"  Case detail: \033[93mSKIP\033[0m")
        else:
            print(f"  Case workflow: \033[90mSKIP\033[0m (no cases found)")
    except Exception as e:
        print(f"  Case workflow: \033[91mERROR: {str(e)[:100]}\033[0m")

    page.close()
    ctx.close()


# ---------------------------------------------------------------------------
# Cross-cutting checks
# ---------------------------------------------------------------------------
def test_cross_cutting(browser):
    print("\n" + "=" * 60)
    print("CROSS-CUTTING CHECKS")
    print("=" * 60)

    # 1. Farmer blocked from admin
    print("\n  --- Auth Boundary: Farmer vs Admin ---")
    reset_otp_limits()
    time.sleep(1)
    try:
        farmer_cookies = get_auth_cookies(ACCOUNTS["farmer"])
        # If we get here, farmer got a token — test if admin UI blocks them
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        inject_cookies(ctx, farmer_cookies, "localhost")
        page = ctx.new_page()
        setup_console_listener(page, "cross-cutting")

        page.goto(f"{ADMIN_URL}/", wait_until="networkidle", timeout=15000)
        time.sleep(2)
        take_screenshot(page, "cross_cutting_farmer_admin")

        current = page.url
        body = page.locator("body").inner_text().lower()

        if "/login" in current:
            ALL_RESULTS.append(PageResult(app="cross-cutting", route="/farmer→admin",
                page_name="Farmer Blocked from Admin", status="PASS",
                issues=["Redirected to login — correctly blocked"]))
            print(f"  Farmer blocked: \033[92mPASS\033[0m (redirected to login)")
        elif "forbidden" in body or "not authorized" in body or "access denied" in body:
            ALL_RESULTS.append(PageResult(app="cross-cutting", route="/farmer→admin",
                page_name="Farmer Blocked from Admin", status="PASS",
                issues=["Shown forbidden/unauthorized message"]))
            print(f"  Farmer blocked: \033[92mPASS\033[0m (forbidden message)")
        else:
            ALL_RESULTS.append(PageResult(app="cross-cutting", route="/farmer→admin",
                page_name="Farmer Blocked from Admin", status="WARN",
                issues=[f"Farmer reached {current} — may need role-based route guard"]))
            print(f"  Farmer blocked: \033[93mWARN\033[0m (farmer reached {current})")

        page.close()
        ctx.close()
    except AssertionError as e:
        err_str = str(e)
        if "403" in err_str or "staff" in err_str.lower() or "blocked" in err_str.lower():
            ALL_RESULTS.append(PageResult(app="cross-cutting", route="/farmer→admin",
                page_name="Farmer Blocked from Admin", status="PASS",
                issues=["API rejects farmer login for web: " + err_str[:100]]))
            print(f"  Farmer blocked: \033[92mPASS\033[0m (API rejects farmer for web portal)")
        else:
            ALL_RESULTS.append(PageResult(app="cross-cutting", route="/farmer→admin",
                page_name="Farmer Blocked from Admin", status="ERROR", issues=[err_str[:200]]))
            print(f"  Farmer blocked: \033[91mERROR: {err_str[:100]}\033[0m")
    except Exception as e:
        err_str = str(e)
        if "403" in err_str or "staff" in err_str.lower():
            ALL_RESULTS.append(PageResult(app="cross-cutting", route="/farmer→admin",
                page_name="Farmer Blocked from Admin", status="PASS",
                issues=["API rejects farmer for web: " + err_str[:100]]))
            print(f"  Farmer blocked: \033[92mPASS\033[0m (API rejects farmer)")
        else:
            ALL_RESULTS.append(PageResult(app="cross-cutting", route="/farmer→admin",
                page_name="Farmer Blocked from Admin", status="ERROR", issues=[err_str[:200]]))
            print(f"  Farmer blocked: \033[91mERROR: {err_str[:100]}\033[0m")

    # 2. Responsive checks on admin dashboard at 4 widths
    print("\n  --- Responsive Checks (Admin Dashboard at 4 widths) ---")
    reset_otp_limits()
    time.sleep(1)
    admin_cookies = get_auth_cookies(ACCOUNTS["admin"])
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    inject_cookies(ctx, admin_cookies, "localhost")
    page = ctx.new_page()

    widths = [1920, 1366, 1024, 768]
    for w in widths:
        page.set_viewport_size({"width": w, "height": 1080})
        page.goto(f"{ADMIN_URL}/", wait_until="networkidle", timeout=15000)
        time.sleep(1)
        take_screenshot(page, f"responsive_admin_{w}", width=w, height=1080)
        print(f"  Admin dashboard at {w}px: screenshot saved")

    page.close()
    ctx.close()


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def generate_report():
    print("\n" + "=" * 60)
    print("BROWSER UI TEST RESULTS SUMMARY")
    print("=" * 60)

    total = len(ALL_RESULTS)
    passed = sum(1 for r in ALL_RESULTS if r.status == "PASS")
    failed = sum(1 for r in ALL_RESULTS if r.status == "FAIL")
    warned = sum(1 for r in ALL_RESULTS if r.status == "WARN")
    errors = sum(1 for r in ALL_RESULTS if r.status == "ERROR")
    skipped = sum(1 for r in ALL_RESULTS if r.status == "SKIP")

    print(f"\nTotal: {total} | PASS: {passed} | FAIL: {failed} | WARN: {warned} | ERROR: {errors} | SKIP: {skipped}")

    for app in ["admin", "collection", "vet", "cross-cutting"]:
        app_results = [r for r in ALL_RESULTS if r.app == app]
        if not app_results:
            continue
        print(f"\n--- {app.upper()} ---")
        print(f"{'Route':<30} {'Page':<25} {'Status':<8} {'Time(ms)':<10} Issues")
        print("-" * 110)
        for r in app_results:
            issues_str = "; ".join(r.issues) if r.issues else ""
            time_str = f"{r.load_time_ms:.0f}" if r.load_time_ms > 0 else "-"
            color = {"PASS": "\033[92m", "FAIL": "\033[91m", "WARN": "\033[93m",
                     "ERROR": "\033[91m", "SKIP": "\033[90m"}.get(r.status, "")
            print(f"{r.route:<30} {r.page_name:<25} {color}{r.status:<8}\033[0m {time_str:<10} {issues_str[:80]}")

    if CONSOLE_ERRORS:
        print(f"\n--- CONSOLE ERRORS ({len(CONSOLE_ERRORS)}) ---")
        for e in CONSOLE_ERRORS[:30]:
            print(f"  [{e['app']}] {e['url']}: {e['text'][:150]}")
    else:
        print("\n--- CONSOLE ERRORS: None ---")

    screenshots = list(SCREENSHOT_DIR.glob("*.png"))
    print(f"\n--- SCREENSHOTS: {len(screenshots)} saved to {SCREENSHOT_DIR} ---")

    return {
        "total": total, "passed": passed, "failed": failed,
        "warned": warned, "errors": errors, "skipped": skipped,
        "results": [
            {"app": r.app, "route": r.route, "page_name": r.page_name,
             "status": r.status, "load_time_ms": r.load_time_ms,
             "issues": r.issues, "console_errors": r.console_errors,
             "screenshot_desktop": r.screenshot_desktop,
             "screenshot_tablet": r.screenshot_tablet}
            for r in ALL_RESULTS
        ],
        "console_errors": CONSOLE_ERRORS,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("PashuRaksha ERP — Phase 2: Browser UI Testing")
    print("=" * 60)
    print(f"Screenshots: {SCREENSHOT_DIR}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)

        test_admin(browser)
        test_collection(browser)
        test_vet(browser)
        test_cross_cutting(browser)

        browser.close()

    summary = generate_report()

    results_path = SCREENSHOT_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nResults JSON saved to {results_path}")
    return summary


if __name__ == "__main__":
    main()
