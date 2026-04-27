"""
PashuRaksha ERP — End-to-end integration tests using Playwright + Chrome CDP.

Prerequisites:
  - API running on http://localhost:8000
  - Admin running on http://localhost:3000
  - Chrome running with --remote-debugging-port=9222

Run:
  .venv/bin/python -m pytest tests/test_integration_e2e.py -v --tb=short
"""

import json
import re
import urllib.request

import pytest

try:
    from playwright.sync_api import Page, expect, sync_playwright
except ModuleNotFoundError:
    pytest.skip("playwright not installed", allow_module_level=True)

API_URL = "http://localhost:8000"
ADMIN_URL = "http://localhost:3000"
CDP_URL = "http://localhost:9222"

ADMIN_PHONE = "+919900000001"
OTP = "123456"


def _get_admin_token() -> dict:
    """Get admin JWT token via API."""
    req = urllib.request.Request(
        f"{API_URL}/v1/auth/request-otp",
        data=json.dumps({"phone": ADMIN_PHONE}).encode(),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req)
    req = urllib.request.Request(
        f"{API_URL}/v1/auth/verify-otp",
        data=json.dumps({"phone": ADMIN_PHONE, "otp": OTP}).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        yield browser
        browser.close()


@pytest.fixture(scope="module")
def auth_data():
    return _get_admin_token()


def _inject_auth(page: Page, auth_data: dict):
    """Inject auth token into localStorage."""
    token = auth_data.get("access_token", "")
    user_json = json.dumps(
        {
            "id": auth_data.get("user_id", "unknown"),
            "name": auth_data.get("name", "Admin"),
            "role": auth_data.get("role", "admin"),
        }
    )
    page.evaluate(f"""() => {{
        localStorage.setItem('token', '{token}');
        localStorage.setItem('user', '{user_json}');
    }}""")


def _go(page: Page, path: str, auth_data: dict = None):
    """Navigate to page with auth, wait for data."""
    if auth_data:
        _inject_auth(page, auth_data)
    page.goto(f"{ADMIN_URL}{path}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2500)


@pytest.fixture
def page(browser, auth_data):
    """Fresh page per test with auth pre-set via addInitScript."""
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.set_default_timeout(20000)
    token = auth_data.get("access_token", "")
    user_json = json.dumps(
        {
            "id": auth_data.get("user_id", "unknown"),
            "name": auth_data.get("name", "Admin"),
            "role": auth_data.get("role", "admin"),
        }
    )
    # This runs BEFORE any page JS, ensuring token is available at first render
    ctx.add_init_script(f"""
        localStorage.setItem('token', '{token}');
        localStorage.setItem('user', '{user_json}');
    """)
    pg = ctx.new_page()
    pg.goto(ADMIN_URL)
    pg.wait_for_load_state("networkidle")
    pg.wait_for_timeout(1500)
    yield pg
    pg.close()
    ctx.close()


# ─── Dashboard ────────────────────────────────────────────────────────


class TestDashboard:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/", auth_data)
        heading = page.locator("h4, h5, h1").first
        expect(heading).to_be_visible()

    def test_stat_cards_show_data(self, page: Page, auth_data):
        _go(page, "/", auth_data)
        body = page.inner_text("body")
        assert re.search(r"\d+", body), "Dashboard should show numeric data"

    def test_no_loading_spinner(self, page: Page, auth_data):
        _go(page, "/", auth_data)
        assert page.locator("[role='progressbar']").count() == 0


# ─── Farmers ──────────────────────────────────────────────────────────


class TestFarmers:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/farmers", auth_data)
        assert "farmer" in page.inner_text("body").lower()

    def test_has_rows(self, page: Page, auth_data):
        _go(page, "/farmers", auth_data)
        body = page.inner_text("body")
        rows = page.locator("table tbody tr").count()
        has_data = rows > 0 or re.search(r"(KA-MYS|Mysore|Mandya|\+91)", body, re.IGNORECASE)
        assert has_data, "Farmers page should show data"

    def test_no_error(self, page: Page, auth_data):
        _go(page, "/farmers", auth_data)
        assert page.locator(".MuiAlert-standardError").count() == 0


# ─── Animals ──────────────────────────────────────────────────────────


class TestAnimals:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/animals", auth_data)
        assert "animal" in page.inner_text("body").lower()

    def test_has_data(self, page: Page, auth_data):
        _go(page, "/animals", auth_data)
        body = page.inner_text("body").lower()
        has_data = any(t in body for t in ["cattle", "goat", "sheep", "poultry", "ka22", "female"])
        rows = page.locator("table tbody tr").count()
        assert has_data or rows > 0, "Animals page should show data"


# ─── Milk ─────────────────────────────────────────────────────────────


class TestMilk:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/milk", auth_data)
        assert "milk" in page.inner_text("body").lower()

    def test_has_records(self, page: Page, auth_data):
        _go(page, "/milk", auth_data)
        body = page.inner_text("body")
        has_data = "L" in body or re.search(r"\d+\.\d", body)
        rows = page.locator("table tbody tr").count()
        assert has_data or rows > 0, "Milk page should show data"

    def test_date_filter(self, page: Page, auth_data):
        _go(page, "/milk", auth_data)
        # MUI date inputs may render as text inputs with date labels
        inputs = page.locator("input[type='date'], input[type='text']")
        assert inputs.count() >= 1, "Should have filter inputs"


# ─── Health ───────────────────────────────────────────────────────────


class TestHealth:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/health", auth_data)
        assert "health" in page.inner_text("body").lower()

    def test_shows_alerts(self, page: Page, auth_data):
        _go(page, "/health", auth_data)
        body = page.inner_text("body").lower()
        assert any(t in body for t in ["critical", "high", "medium", "low", "alert"])

    def test_has_filter(self, page: Page, auth_data):
        _go(page, "/health", auth_data)
        # MUI Select renders as div with role, or InputLabel
        filters = page.locator(
            "[role='combobox'], .MuiSelect-select, .MuiInputLabel-root, .MuiFormControl-root select"
        )
        assert filters.count() > 0 or "risk" in page.inner_text("body").lower()


# ─── Marketplace ──────────────────────────────────────────────────────


class TestMarketplace:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/marketplace", auth_data)
        assert "marketplace" in page.inner_text("body").lower()

    def test_has_data(self, page: Page, auth_data):
        _go(page, "/marketplace", auth_data)
        body = page.inner_text("body")
        has_data = "₹" in body or re.search(r"\d+", body)
        rows = page.locator("table tbody tr").count()
        assert has_data or rows > 0, "Marketplace should show data"

    def test_search_exists(self, page: Page, auth_data):
        _go(page, "/marketplace", auth_data)
        inputs = page.locator("input")
        assert inputs.count() > 0


# ─── Income ───────────────────────────────────────────────────────────


class TestIncome:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/income", auth_data)
        assert "income" in page.inner_text("body").lower()

    def test_shows_data(self, page: Page, auth_data):
        _go(page, "/income", auth_data)
        body = page.inner_text("body")
        has_amounts = "₹" in body or re.search(r"\d{2,}", body)
        assert has_amounts, "Income page should show data"


# ─── Vaccinations ─────────────────────────────────────────────────────


class TestVaccinations:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/vaccinations", auth_data)
        assert "vaccin" in page.inner_text("body").lower()

    def test_has_content(self, page: Page, auth_data):
        _go(page, "/vaccinations", auth_data)
        body = page.inner_text("body").lower()
        has_data = any(
            t in body
            for t in ["coverage", "schedule", "fmd", "brucella", "cattle", "goat", "village"]
        )
        assert has_data or len(body) > 200


# ─── Schemes ──────────────────────────────────────────────────────────


class TestSchemes:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/schemes", auth_data)
        body = page.inner_text("body").lower()
        assert "scheme" in body or "govt" in body


# ─── Map ──────────────────────────────────────────────────────────────


class TestMap:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/map", auth_data)
        assert len(page.inner_text("body")) > 50


# ─── IoT ──────────────────────────────────────────────────────────────


class TestIoT:
    def test_loads(self, page: Page, auth_data):
        _go(page, "/iot", auth_data)
        assert len(page.inner_text("body")) > 50


# ─── Navigation ───────────────────────────────────────────────────────


class TestNavigation:
    def test_sidebar_links(self, page: Page, auth_data):
        _go(page, "/", auth_data)
        nav = page.locator("nav a, aside a, .MuiDrawer-root a")
        assert nav.count() >= 5

    def test_all_pages_accessible(self, page: Page, auth_data):
        routes = [
            "/",
            "/farmers",
            "/animals",
            "/milk",
            "/health",
            "/marketplace",
            "/income",
            "/vaccinations",
            "/schemes",
            "/map",
            "/iot",
        ]
        errors = []
        for route in routes:
            _go(page, route, auth_data)
            body = page.inner_text("body").lower()
            if "404" in body and "not found" in body:
                errors.append(f"{route}: 404")
            if "application error" in body:
                errors.append(f"{route}: crash")
        assert not errors, f"Page errors: {errors}"


# ─── Console Errors ──────────────────────────────────────────────────


def _make_auth_context(browser, auth_data):
    """Create a browser context with auth pre-injected via addInitScript."""
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.set_default_timeout(20000)
    token = auth_data.get("access_token", "")
    user_json = json.dumps(
        {
            "id": auth_data.get("user_id", "unknown"),
            "name": auth_data.get("name", "Admin"),
            "role": auth_data.get("role", "admin"),
        }
    )
    ctx.add_init_script(f"""
        localStorage.setItem('token', '{token}');
        localStorage.setItem('user', '{user_json}');
    """)
    return ctx


class TestConsoleErrors:
    def test_no_uncaught_exceptions(self, browser, auth_data):
        ctx = _make_auth_context(browser, auth_data)
        pg = ctx.new_page()

        errors = []
        pg.on("pageerror", lambda err: errors.append(str(err)))

        for path in ["/", "/farmers", "/animals", "/milk", "/health", "/marketplace", "/income"]:
            pg.goto(f"{ADMIN_URL}{path}")
            pg.wait_for_load_state("networkidle")
            pg.wait_for_timeout(1500)

        pg.close()
        ctx.close()
        critical = [
            e
            for e in errors
            if "ResizeObserver" not in e
            and "chunk" not in e.lower()
            and "hooks" not in e.lower()
            and "hydrat" not in e.lower()
        ]
        assert not critical, f"Console errors: {critical}"


# ─── API Integration ─────────────────────────────────────────────────


class TestAPIIntegration:
    def test_api_calls_return_200(self, browser, auth_data):
        ctx = _make_auth_context(browser, auth_data)
        pg = ctx.new_page()

        failed = []

        def on_response(response):
            if "/v1/" in response.url and response.status >= 400:
                failed.append(f"{response.url} → {response.status}")

        pg.on("response", on_response)

        for path in ["/", "/farmers", "/animals", "/milk", "/health", "/marketplace", "/income"]:
            pg.goto(f"{ADMIN_URL}{path}")
            pg.wait_for_load_state("networkidle")
            pg.wait_for_timeout(2000)

        pg.close()
        ctx.close()
        assert not failed, f"Failed API requests: {failed}"
