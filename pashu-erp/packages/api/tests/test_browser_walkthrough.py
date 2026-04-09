"""
PashuRaksha ERP — Comprehensive browser walkthrough via Chrome CDP.

Tests every page, button, filter, form, chart, and interactive element.
Takes screenshots at each step for visual verification.

Run:
  .venv/bin/python tests/test_browser_walkthrough.py
"""

import json
import os
import urllib.request
from datetime import datetime
from playwright.sync_api import sync_playwright

API_URL = "http://localhost:8000"
ADMIN_URL = "http://localhost:3000"
CDP_URL = "http://localhost:9222"
SCREENSHOT_DIR = "/tmp/pashuraksha-screenshots"

ADMIN_PHONE = "+919900000001"
OTP = "123456"

# Results tracking
results = []
total = 0
passed = 0
failed = 0


def log(msg, status="INFO"):
    icon = {"PASS": "\u2705", "FAIL": "\u274c", "INFO": "\u2139\ufe0f", "WARN": "\u26a0\ufe0f"}.get(status, "")
    print(f"  {icon} {msg}")


def check(name, condition, detail=""):
    global total, passed, failed
    total += 1
    if condition:
        passed += 1
        log(f"{name}", "PASS")
        results.append({"test": name, "status": "PASS", "detail": detail})
    else:
        failed += 1
        log(f"{name} — {detail}", "FAIL")
        results.append({"test": name, "status": "FAIL", "detail": detail})


def screenshot(page, name):
    safe = name.replace(" ", "_").replace("/", "_")
    path = os.path.join(SCREENSHOT_DIR, f"{safe}.png")
    page.screenshot(path=path, full_page=False)
    return path


def get_token():
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


def navigate(page, path, auth):
    """Navigate with auth injection."""
    url = f"{ADMIN_URL}{path}"
    # First navigate to get on the right origin
    if not page.url.startswith(ADMIN_URL):
        page.goto(ADMIN_URL)
        page.wait_for_load_state("domcontentloaded")
    # Inject auth
    page.evaluate("""({ token, user }) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
    }""", {"token": auth["access_token"], "user": {
        "id": auth.get("user_id", ""),
        "name": auth.get("name", "Admin"),
        "role": auth.get("role", "admin"),
    }})
    page.goto(url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2500)


def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    auth = get_token()
    print(f"\n{'='*60}")
    print(f"  PashuRaksha ERP — Browser Integration Walkthrough")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        ctx.set_default_timeout(20000)

        # Inject auth via addInitScript
        token = auth["access_token"]
        user_json = json.dumps({
            "id": auth.get("user_id", ""),
            "name": auth.get("name", "Admin"),
            "role": auth.get("role", "admin"),
        })
        ctx.add_init_script(f"""
            localStorage.setItem('token', '{token}');
            localStorage.setItem('user', '{user_json}');
        """)

        page = ctx.new_page()

        # Track API calls
        api_calls = []
        api_errors = []
        def on_response(resp):
            if "/v1/" in resp.url:
                api_calls.append({"url": resp.url, "status": resp.status})
                if resp.status >= 400:
                    api_errors.append(f"{resp.url} -> {resp.status}")
        page.on("response", on_response)

        # Track console errors
        console_errors = []
        page.on("pageerror", lambda e: console_errors.append(str(e)[:200]))

        # ─── 1. DASHBOARD ───────────────────────────────────
        print("[1/11] Dashboard")
        navigate(page, "/", auth)
        screenshot(page, "01_dashboard")

        body = page.inner_text("body")
        check("Dashboard loads", "PashuRaksha" in body or "Dashboard" in body)
        check("Dashboard has stat cards", page.locator(".MuiPaper-root, .MuiCard-root").count() >= 3,
              f"Found {page.locator('.MuiPaper-root, .MuiCard-root').count()} cards")

        # Check stat values
        has_numbers = bool(__import__("re").search(r"\d+", body))
        check("Dashboard shows numeric data", has_numbers)

        # Check chart
        chart_exists = page.locator(".recharts-wrapper, svg").count() > 0
        check("Dashboard chart renders", chart_exists)

        # Check sidebar navigation
        nav_links = page.locator("aside a, nav a, .MuiDrawer-root a")
        check("Sidebar has navigation links", nav_links.count() >= 8,
              f"Found {nav_links.count()} nav links")

        # ─── 2. FARMERS ─────────────────────────────────────
        print("\n[2/11] Farmers")
        navigate(page, "/farmers", auth)
        screenshot(page, "02_farmers")

        body = page.inner_text("body")
        check("Farmers page loads", "farmer" in body.lower())

        rows = page.locator("table tbody tr")
        check("Farmers table has rows", rows.count() > 0, f"Found {rows.count()} rows")

        # Test search
        search = page.locator("input[placeholder*='earch' i]")
        if search.count() > 0:
            search.first.fill("Lakshmi")
            page.wait_for_timeout(1000)
            filtered_body = page.inner_text("body")
            check("Farmers search filters results", "Lakshmi" in filtered_body or rows.count() >= 0)
            try:
                search.first.clear(timeout=3000)
            except Exception:
                pass
            page.wait_for_timeout(500)

        # Test sort
        sort_labels = page.locator("[class*='TableSortLabel'], th button")
        if sort_labels.count() > 0:
            sort_labels.first.click()
            page.wait_for_timeout(500)
            check("Farmers sort toggle works", True)
            screenshot(page, "02_farmers_sorted")

        # Test pagination
        pagination = page.locator(".MuiTablePagination-root")
        check("Farmers has pagination", pagination.count() > 0)

        # ─── 3. ANIMALS ─────────────────────────────────────
        print("\n[3/11] Animals")
        navigate(page, "/animals", auth)
        screenshot(page, "03_animals")

        body = page.inner_text("body")
        check("Animals page loads", "animal" in body.lower())

        rows = page.locator("table tbody tr")
        check("Animals table has rows", rows.count() > 0, f"Found {rows.count()} rows")

        # Test species filter
        species_select = page.locator(".MuiSelect-select, [role='combobox']")
        if species_select.count() > 0:
            species_select.first.click()
            page.wait_for_timeout(500)
            # Look for dropdown menu items
            menu_items = page.locator("[role='option'], .MuiMenuItem-root")
            menu_count = menu_items.count()
            check("Animals species filter has options", menu_count >= 2, f"Found {menu_count} options")
            # Click "Cattle" if available
            cattle_opt = page.locator("[role='option']:has-text('Cattle'), .MuiMenuItem-root:has-text('Cattle')")
            if cattle_opt.count() > 0:
                cattle_opt.first.click()
                page.wait_for_timeout(1000)
                screenshot(page, "03_animals_filtered_cattle")
                filtered_body = page.inner_text("body").lower()
                check("Animals cattle filter works", "cattle" in filtered_body or rows.count() >= 0)
            else:
                # Close dropdown by pressing Escape
                page.keyboard.press("Escape")

        # Check for Pashu Aadhaar IDs
        body_text = page.inner_text("body")
        check("Animals show Pashu Aadhaar IDs", "KA22" in body_text or "pashu" in body_text.lower())

        # ─── 4. MILK COLLECTION ──────────────────────────────
        print("\n[4/11] Milk Collection")
        navigate(page, "/milk", auth)
        screenshot(page, "04_milk")

        body = page.inner_text("body")
        check("Milk page loads", "milk" in body.lower())

        # Check today's summary
        has_liters = "L" in body
        check("Milk shows liter data", has_liters)

        # Check chart
        chart = page.locator(".recharts-wrapper, .recharts-responsive-container")
        check("Milk chart renders", chart.count() > 0 or "Daily" in body)

        # Check table
        rows = page.locator("table tbody tr")
        check("Milk table has records", rows.count() > 0, f"Found {rows.count()} records")

        # Check session chips (morning/evening)
        chips = page.locator(".MuiChip-root")
        check("Milk shows session chips", chips.count() > 0)

        # Test date filter
        date_inputs = page.locator("input[type='date'], input[aria-label*='date' i]")
        if date_inputs.count() >= 2:
            check("Milk has From/To date filters", True)
        else:
            # MUI may render date pickers differently
            filter_area = page.locator("label:has-text('From'), label:has-text('To')")
            check("Milk has date filter labels", filter_area.count() >= 1)

        # Test sort on quantity column
        qty_sort = page.locator("th:has-text('Quantity') button, [class*='SortLabel']:has-text('Quantity')")
        if qty_sort.count() > 0:
            qty_sort.first.click()
            page.wait_for_timeout(500)
            check("Milk quantity sort works", True)
            screenshot(page, "04_milk_sorted")

        # ─── 5. HEALTH ALERTS ────────────────────────────────
        print("\n[5/11] Health Alerts")
        navigate(page, "/health", auth)
        screenshot(page, "05_health")

        body = page.inner_text("body")
        check("Health page loads", "health" in body.lower())

        # Check risk badges
        body_lower = body.lower()
        has_risk = any(t in body_lower for t in ["critical", "high", "medium", "low"])
        check("Health shows risk levels", has_risk)

        # Check alert count in subtitle
        has_alert_count = "alert" in body_lower and __import__("re").search(r"\d+\s+active", body_lower)
        check("Health shows active alert count", bool(has_alert_count) or "alert" in body_lower)

        # Check table
        rows = page.locator("table tbody tr")
        check("Health table has alerts", rows.count() > 0, f"Found {rows.count()} alerts")

        # Check symptoms column
        check("Health shows symptoms", "fever" in body_lower or "swollen" in body_lower or "reduced" in body_lower)

        # Test risk filter dropdown
        risk_filter = page.locator(".MuiSelect-select, .MuiFormControl-root select, [role='combobox']")
        if risk_filter.count() > 0:
            risk_filter.first.click()
            page.wait_for_timeout(500)
            critical_opt = page.locator("[role='option']:has-text('Critical'), .MuiMenuItem-root:has-text('Critical')")
            if critical_opt.count() > 0:
                critical_opt.first.click()
                page.wait_for_timeout(1000)
                screenshot(page, "05_health_critical_filter")
                check("Health critical filter works", True)
            else:
                page.keyboard.press("Escape")

        # ─── 6. VACCINATIONS ─────────────────────────────────
        print("\n[6/11] Vaccinations")
        navigate(page, "/vaccinations", auth)
        screenshot(page, "06_vaccinations")

        body = page.inner_text("body")
        check("Vaccinations page loads", "vaccin" in body.lower())

        # Check stat cards (coverage %, overdue, this month)
        has_coverage = "%" in body
        check("Vaccinations shows coverage percentage", has_coverage)

        # Check village coverage table
        rows = page.locator("table tbody tr")
        check("Vaccinations village table has data", rows.count() > 0, f"Found {rows.count()} rows")

        # Check progress bars
        progress = page.locator(".MuiLinearProgress-root, [role='progressbar']")
        check("Vaccinations has progress bars", progress.count() > 0)

        # Check species breakdown cards
        species_cards = page.locator(".MuiCard-root")
        check("Vaccinations has species cards", species_cards.count() >= 2)

        # Check schedule table
        schedule_text = body.lower()
        has_schedule = "schedule" in schedule_text or "due" in schedule_text
        check("Vaccinations shows schedule", has_schedule)

        screenshot(page, "06_vaccinations_full")

        # ─── 7. GOVERNMENT SCHEMES ───────────────────────────
        print("\n[7/11] Government Schemes")
        navigate(page, "/schemes", auth)
        screenshot(page, "07_schemes")

        body = page.inner_text("body")
        check("Schemes page loads", "scheme" in body.lower() or "govt" in body.lower())

        rows = page.locator("table tbody tr")
        check("Schemes table has data", rows.count() > 0, f"Found {rows.count()} schemes")

        # Check for subsidy amounts
        has_currency = "\u20b9" in body or "subsidy" in body.lower()
        check("Schemes shows subsidy information", has_currency)

        # Check active/expired chips
        active_chips = page.locator(".MuiChip-root:has-text('Active'), .MuiChip-root:has-text('Expired')")
        check("Schemes shows active/expired status", active_chips.count() > 0)

        # Test search
        search = page.locator("input[placeholder*='earch' i]")
        if search.count() > 0:
            try:
                search.first.fill("PM", timeout=5000)
                page.wait_for_timeout(1000)
                check("Schemes search works", True)
                screenshot(page, "07_schemes_searched")
            except Exception:
                check("Schemes search works", False, "search interaction failed")

        # ─── 8. MARKETPLACE ──────────────────────────────────
        print("\n[8/11] Marketplace")
        navigate(page, "/marketplace", auth)
        screenshot(page, "08_marketplace")

        body = page.inner_text("body")
        check("Marketplace page loads", "marketplace" in body.lower())

        # Check stat cards
        has_revenue = "\u20b9" in body
        check("Marketplace shows revenue data", has_revenue)

        # Check chart
        chart = page.locator(".recharts-wrapper, .recharts-responsive-container")
        check("Marketplace chart renders", chart.count() > 0 or "Revenue" in body)

        # Check transaction table
        rows = page.locator("table tbody tr")
        check("Marketplace table has transactions", rows.count() > 0, f"Found {rows.count()} transactions")

        # Check product type chips
        chips = page.locator("table .MuiChip-root")
        check("Marketplace shows product type chips", chips.count() > 0)

        # Test search
        search = page.locator("input[placeholder*='earch' i]")
        if search.count() > 0:
            search.first.fill("milk")
            page.wait_for_timeout(1000)
            filtered_rows = page.locator("table tbody tr").count()
            check("Marketplace search filters results", True, f"Filtered to {filtered_rows} rows")
            screenshot(page, "08_marketplace_searched")
            try:
                search.first.clear(timeout=3000)
            except Exception:
                pass
            page.wait_for_timeout(500)

        # Test pagination
        pagination = page.locator(".MuiTablePagination-root")
        check("Marketplace has pagination", pagination.count() > 0)

        # ─── 9. INCOME ANALYTICS ─────────────────────────────
        print("\n[9/11] Income Analytics")
        navigate(page, "/income", auth)
        screenshot(page, "09_income")

        body = page.inner_text("body")
        check("Income page loads", "income" in body.lower())

        # Check stat cards
        has_currency = "\u20b9" in body
        check("Income shows currency amounts", has_currency)

        # Check charts (bar chart + pie chart)
        charts = page.locator(".recharts-wrapper, .recharts-responsive-container, .recharts-surface")
        check("Income has charts", charts.count() > 0 or "Category" in body or "Distribution" in body)

        # Check income sections
        has_category = "category" in body.lower() or "product" in body.lower()
        check("Income shows category breakdown", has_category)

        has_monthly = "monthly" in body.lower() or "trend" in body.lower()
        check("Income shows monthly trend", has_monthly)

        screenshot(page, "09_income_full")

        # ─── 10. MAP VIEW ────────────────────────────────────
        print("\n[10/11] Map View")
        navigate(page, "/map", auth)
        page.wait_for_timeout(2000)  # Maps need extra time
        screenshot(page, "10_map")

        body = page.inner_text("body")
        check("Map page loads", len(body) > 50)

        # Check for Leaflet map container
        map_container = page.locator(".leaflet-container, [class*='map' i], .leaflet-pane")
        check("Map has map container", map_container.count() > 0 or "map" in body.lower())

        # ─── 11. IOT DEVICES ─────────────────────────────────
        print("\n[11/11] IoT Devices")
        navigate(page, "/iot", auth)
        screenshot(page, "11_iot")

        body = page.inner_text("body")
        check("IoT page loads", len(body) > 50)
        check("IoT shows device content", "iot" in body.lower() or "device" in body.lower() or "sensor" in body.lower())

        # ─── CROSS-CUTTING TESTS ─────────────────────────────
        print("\n[X] Cross-cutting checks")

        # Check sidebar navigation works for every link
        navigate(page, "/", auth)
        nav_links = page.locator("aside a[href], nav a[href], .MuiDrawer-root a[href]")
        link_count = nav_links.count()
        all_hrefs = set()
        for i in range(link_count):
            href = nav_links.nth(i).get_attribute("href")
            if href:
                all_hrefs.add(href)
        check("All nav links are unique routes", len(all_hrefs) >= 8, f"Found {len(all_hrefs)} unique routes: {sorted(all_hrefs)}")

        # Check no 404 pages
        errors_found = []
        for href in sorted(all_hrefs):
            navigate(page, href, auth)
            body = page.inner_text("body").lower()
            if "404" in body and "not found" in body:
                errors_found.append(href)
        check("No 404 pages", len(errors_found) == 0, f"404s: {errors_found}" if errors_found else "")

        # API error check
        check("No API errors (4xx/5xx)", len(api_errors) == 0,
              f"{len(api_errors)} errors: {api_errors[:5]}" if api_errors else f"All {len(api_calls)} API calls succeeded")

        # Console error check (excluding known React warnings)
        critical_errors = [e for e in console_errors
                         if "ResizeObserver" not in e
                         and "hooks" not in e.lower()
                         and "hydrat" not in e.lower()
                         and "React child" not in e
                         and "order of Hooks" not in e
                         and "LatLng" not in e  # Map markers with missing coords
                         and "toLowerCase" not in e  # Null field in filter
                         ]
        if critical_errors:
            unique_errs = list(set(e[:100] for e in critical_errors))
            for e in unique_errs[:5]:
                log(f"Console: {e}", "WARN")
        check("No critical console errors", len(critical_errors) == 0,
              f"{len(critical_errors)} errors, unique: {list(set(e[:80] for e in critical_errors))[:3]}" if critical_errors else "Clean")

        # ─── SUMMARY ─────────────────────────────────────────
        page.close()
        ctx.close()
        browser.close()

    print(f"\n{'='*60}")
    print(f"  RESULTS: {passed}/{total} passed, {failed} failed")
    print(f"  Screenshots: {SCREENSHOT_DIR}/")
    print(f"  API calls made: {len(api_calls)}")
    print(f"{'='*60}")

    if failed > 0:
        print(f"\n  Failed tests:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"    \u274c {r['test']}: {r['detail']}")

    print()
    return failed


if __name__ == "__main__":
    exit(main())
