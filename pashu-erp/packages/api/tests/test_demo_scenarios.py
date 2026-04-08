"""
PashuRaksha Demo Scenario Verification Tests
=============================================
Run:  cd packages/api && uv run python -m pytest tests/test_demo_scenarios.py -v
Or:   cd packages/api && uv run python tests/test_demo_scenarios.py
Requires: Running API (docker compose up) with seeded data.
"""

import sys
from datetime import datetime, timezone

import httpx

BASE_URL = "http://localhost:8000"
MOCK_OTP = "123456"


class TestDemoScenarios:
    """Test all 9 demo scenarios against a running API."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_farmer_token(self) -> str:
        """Login as farmer Lakshmi."""
        r = httpx.post(f"{BASE_URL}/v1/auth/verify-otp", json={
            "phone": "+919900000002", "otp": MOCK_OTP,
        })
        assert r.status_code == 200, f"Farmer auth failed: {r.text}"
        data = r.json()
        assert "access_token" in data
        assert data["role"] == "farmer"
        return data["access_token"]

    def _get_admin_token(self) -> str:
        """Login as admin Deepak."""
        r = httpx.post(f"{BASE_URL}/v1/auth/verify-otp", json={
            "phone": "+919900000001", "otp": MOCK_OTP,
        })
        assert r.status_code == 200, f"Admin auth failed: {r.text}"
        data = r.json()
        assert data["role"] == "admin"
        return data["access_token"]

    def _get_farmer_user_id(self) -> str:
        """Return the seeded farmer's user_id."""
        r = httpx.post(f"{BASE_URL}/v1/auth/verify-otp", json={
            "phone": "+919900000002", "otp": MOCK_OTP,
        })
        assert r.status_code == 200
        return r.json()["user_id"]

    def _auth(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    # ------------------------------------------------------------------
    # Scenario 1 — Farmer Registration via Phone OTP
    # ------------------------------------------------------------------

    def test_scenario_1_request_otp(self):
        """OTP request returns success message."""
        r = httpx.post(f"{BASE_URL}/v1/auth/request-otp", json={
            "phone": "+919900000099",
        })
        assert r.status_code == 200
        assert "OTP sent" in r.json()["message"]

    def test_scenario_1_verify_otp_creates_user(self):
        """Verifying OTP auto-creates a farmer account and returns a JWT."""
        r = httpx.post(f"{BASE_URL}/v1/auth/verify-otp", json={
            "phone": "+919900000099", "otp": MOCK_OTP,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["access_token"]
        assert data["role"] == "farmer"
        assert data["user_id"]

    def test_scenario_1_invalid_otp_rejected(self):
        """Wrong OTP is rejected with 401."""
        r = httpx.post(f"{BASE_URL}/v1/auth/verify-otp", json={
            "phone": "+919900000002", "otp": "000000",
        })
        assert r.status_code == 401

    def test_scenario_1_new_user_animals_empty(self):
        """A freshly-created farmer has no animals."""
        r = httpx.post(f"{BASE_URL}/v1/auth/verify-otp", json={
            "phone": "+919900000098", "otp": MOCK_OTP,
        })
        token = r.json()["access_token"]
        r = httpx.get(f"{BASE_URL}/v1/animals", headers=self._auth(token))
        assert r.status_code == 200
        assert r.json() == []

    # ------------------------------------------------------------------
    # Scenario 2 — Record Milk Yield
    # ------------------------------------------------------------------

    def test_scenario_2_record_milk(self):
        """Farmer records a morning milk yield for a cow."""
        token = self._get_farmer_token()
        headers = self._auth(token)

        # Get farmer's animals
        r = httpx.get(f"{BASE_URL}/v1/animals", headers=headers)
        assert r.status_code == 200
        animals = r.json()
        assert len(animals) > 0, "Farmer should have seeded animals"

        cow = next((a for a in animals if a.get("species") == "cattle"), None)
        if cow is None:
            # Use the first animal if no cattle found
            cow = animals[0]

        r = httpx.post(f"{BASE_URL}/v1/milk/yield", headers=headers, json={
            "animal_id": cow["id"],
            "quantity_liters": 5.0,
            "session": "morning",
            "notes": "Voice input test",
        })
        assert r.status_code == 201, f"Milk record failed: {r.text}"
        data = r.json()
        assert data["quantity_liters"] == 5.0
        assert data["session"] == "morning"

    # ------------------------------------------------------------------
    # Scenario 3 — Milk History / Bar Chart Data
    # ------------------------------------------------------------------

    def test_scenario_3_milk_history(self):
        """Farmer retrieves 30-day milk history."""
        token = self._get_farmer_token()
        user_id = self._get_farmer_user_id()
        headers = self._auth(token)

        r = httpx.get(
            f"{BASE_URL}/v1/milk/farmer/{user_id}/history?days=30",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "total_liters" in data
        assert "average_daily" in data
        assert "period_days" in data
        assert data["period_days"] == 30

    # ------------------------------------------------------------------
    # Scenario 4 — Health Triage (AI symptom checker)
    # ------------------------------------------------------------------

    def test_scenario_4_health_triage(self):
        """Logging symptoms returns an AI risk score and recommended action."""
        token = self._get_farmer_token()
        headers = self._auth(token)

        r = httpx.get(f"{BASE_URL}/v1/animals", headers=headers)
        animals = r.json()
        assert len(animals) > 0
        cow = next((a for a in animals if a.get("species") == "cattle"), animals[0])

        r = httpx.post(f"{BASE_URL}/v1/health/log", headers=headers, json={
            "animal_id": cow["id"],
            "event_type": "symptom",
            "description": "Cow has fever and swollen udder",
            "symptoms": ["fever", "swollen_udder", "reduced_milk"],
        })
        assert r.status_code == 201, f"Health log failed: {r.text}"
        data = r.json()
        assert "ai_risk_score" in data
        assert "recommended_action" in data
        assert isinstance(data["ai_risk_score"], (int, float))

    def test_scenario_4_health_history(self):
        """Health event history is retrievable per animal."""
        token = self._get_farmer_token()
        headers = self._auth(token)

        r = httpx.get(f"{BASE_URL}/v1/animals", headers=headers)
        animals = r.json()
        if animals:
            animal_id = animals[0]["id"]
            r = httpx.get(
                f"{BASE_URL}/v1/health/history/{animal_id}",
                headers=headers,
            )
            assert r.status_code == 200
            assert isinstance(r.json(), list)

    # ------------------------------------------------------------------
    # Scenario 5 — Admin Dashboard
    # ------------------------------------------------------------------

    def test_scenario_5_admin_stats(self):
        """Admin sees dashboard stats: farmer count, animals, milk, alerts."""
        token = self._get_admin_token()
        headers = self._auth(token)

        r = httpx.get(f"{BASE_URL}/v1/admin/stats", headers=headers)
        assert r.status_code == 200
        stats = r.json()
        assert "farmer_count" in stats
        assert "animal_count" in stats
        assert "todays_milk_liters" in stats
        assert "active_alerts" in stats
        assert stats["farmer_count"] > 0

    def test_scenario_5_admin_milk_chart(self):
        """Admin gets 30-day milk chart data."""
        token = self._get_admin_token()
        headers = self._auth(token)

        r = httpx.get(f"{BASE_URL}/v1/admin/charts/milk", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert data["period"] == "30_days"
        assert len(data["data"]) == 30

    def test_scenario_5_admin_gis_alerts(self):
        """Admin retrieves GIS alert markers."""
        token = self._get_admin_token()
        headers = self._auth(token)

        r = httpx.get(f"{BASE_URL}/v1/admin/gis/alerts", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "alert_count" in data
        assert "markers" in data

    # ------------------------------------------------------------------
    # Scenario 6 — Role-Based Access Control
    # ------------------------------------------------------------------

    def test_scenario_6_admin_rejects_farmer(self):
        """Admin endpoints return 403 for non-admin users."""
        token = self._get_farmer_token()
        headers = self._auth(token)

        r = httpx.get(f"{BASE_URL}/v1/admin/stats", headers=headers)
        assert r.status_code == 403, "Farmer should not access admin endpoints"

    def test_scenario_6_unauthenticated_rejected(self):
        """Protected endpoints return 401/403 without a token."""
        r = httpx.get(f"{BASE_URL}/v1/animals")
        assert r.status_code in [401, 403, 422]

    # ------------------------------------------------------------------
    # Scenario 7 — Sell Products (Marketplace)
    # ------------------------------------------------------------------

    def test_scenario_7_market_rates(self):
        """Farmer can view Karnataka APMC market rates."""
        token = self._get_farmer_token()
        headers = self._auth(token)

        r = httpx.get(f"{BASE_URL}/v1/marketplace/rates", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "rates" in data

    def test_scenario_7_sell_milk(self):
        """Farmer records a milk sale with auto-calculated total."""
        token = self._get_farmer_token()
        headers = self._auth(token)

        r = httpx.post(f"{BASE_URL}/v1/marketplace/sell", headers=headers, json={
            "product_type": "milk",
            "quantity": 10.0,
            "unit": "liters",
            "price_per_unit": 31.50,
            "buyer_name": "KMF Center",
            "sold_at": datetime.now(timezone.utc).isoformat(),
        })
        assert r.status_code == 201, f"Sell milk failed: {r.text}"
        data = r.json()
        assert data["total_amount"] == 315.0

    def test_scenario_7_sell_eggs(self):
        """Farmer records an egg sale."""
        token = self._get_farmer_token()
        headers = self._auth(token)

        r = httpx.post(f"{BASE_URL}/v1/marketplace/sell", headers=headers, json={
            "product_type": "eggs",
            "quantity": 20,
            "unit": "pieces",
            "price_per_unit": 6.0,
            "sold_at": datetime.now(timezone.utc).isoformat(),
        })
        assert r.status_code == 201, f"Sell eggs failed: {r.text}"
        data = r.json()
        assert data["total_amount"] == 120.0

    # ------------------------------------------------------------------
    # Scenario 8 — Income Dashboard
    # ------------------------------------------------------------------

    def test_scenario_8_income_summary(self):
        """Farmer views income summary for the current month."""
        token = self._get_farmer_token()
        user_id = self._get_farmer_user_id()
        headers = self._auth(token)

        r = httpx.get(
            f"{BASE_URL}/v1/income/summary/{user_id}?period=month",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "total_income" in data
        assert "total_expense" in data
        assert "net" in data

    def test_scenario_8_income_breakdown(self):
        """Farmer views income breakdown by product category."""
        token = self._get_farmer_token()
        user_id = self._get_farmer_user_id()
        headers = self._auth(token)

        r = httpx.get(
            f"{BASE_URL}/v1/income/breakdown/{user_id}?period=month",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "breakdown" in data

    def test_scenario_8_income_history(self):
        """Farmer views transaction history."""
        token = self._get_farmer_token()
        user_id = self._get_farmer_user_id()
        headers = self._auth(token)

        r = httpx.get(
            f"{BASE_URL}/v1/income/history/{user_id}?period=month",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "entries" in data

    # ------------------------------------------------------------------
    # Scenario 9 — Marketplace Summary
    # ------------------------------------------------------------------

    def test_scenario_9_marketplace_summary(self):
        """Farmer views marketplace summary with per-product breakdown."""
        token = self._get_farmer_token()
        user_id = self._get_farmer_user_id()
        headers = self._auth(token)

        r = httpx.get(
            f"{BASE_URL}/v1/marketplace/summary/{user_id}",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "total_revenue" in data
        assert "by_product" in data

    # ------------------------------------------------------------------
    # Infrastructure checks
    # ------------------------------------------------------------------

    def test_health_endpoint(self):
        """Basic health check."""
        r = httpx.get(f"{BASE_URL}/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["service"] == "pashuraksha-api"

    def test_openapi_docs_available(self):
        """OpenAPI docs and spec are served."""
        r = httpx.get(f"{BASE_URL}/docs")
        assert r.status_code == 200

        r = httpx.get(f"{BASE_URL}/openapi.json")
        assert r.status_code == 200
        spec = r.json()
        assert "paths" in spec
        assert len(spec["paths"]) > 0


# ======================================================================
# Standalone runner (without pytest)
# ======================================================================

if __name__ == "__main__":
    test = TestDemoScenarios()

    scenarios = [
        # Scenario 1: Registration
        ("1a  Request OTP", test.test_scenario_1_request_otp),
        ("1b  Verify OTP creates user", test.test_scenario_1_verify_otp_creates_user),
        ("1c  Invalid OTP rejected", test.test_scenario_1_invalid_otp_rejected),
        ("1d  New user has no animals", test.test_scenario_1_new_user_animals_empty),
        # Scenario 2: Record Milk
        ("2   Record milk yield", test.test_scenario_2_record_milk),
        # Scenario 3: Milk History
        ("3   Milk history (30 days)", test.test_scenario_3_milk_history),
        # Scenario 4: Health Triage
        ("4a  Health triage (AI)", test.test_scenario_4_health_triage),
        ("4b  Health history", test.test_scenario_4_health_history),
        # Scenario 5: Admin Dashboard
        ("5a  Admin stats", test.test_scenario_5_admin_stats),
        ("5b  Admin milk chart", test.test_scenario_5_admin_milk_chart),
        ("5c  Admin GIS alerts", test.test_scenario_5_admin_gis_alerts),
        # Scenario 6: RBAC
        ("6a  Admin rejects farmer", test.test_scenario_6_admin_rejects_farmer),
        ("6b  Unauthenticated rejected", test.test_scenario_6_unauthenticated_rejected),
        # Scenario 7: Sell Products
        ("7a  Market rates", test.test_scenario_7_market_rates),
        ("7b  Sell milk", test.test_scenario_7_sell_milk),
        ("7c  Sell eggs", test.test_scenario_7_sell_eggs),
        # Scenario 8: Income Dashboard
        ("8a  Income summary", test.test_scenario_8_income_summary),
        ("8b  Income breakdown", test.test_scenario_8_income_breakdown),
        ("8c  Income history", test.test_scenario_8_income_history),
        # Scenario 9: Marketplace Summary
        ("9   Marketplace summary", test.test_scenario_9_marketplace_summary),
        # Infrastructure
        ("INF Health check", test.test_health_endpoint),
        ("INF OpenAPI docs", test.test_openapi_docs_available),
    ]

    print("PashuRaksha Demo Scenario Verification")
    print("=" * 45)
    print()

    passed = 0
    failed = 0
    errors: list[tuple[str, str]] = []

    for name, test_fn in scenarios:
        try:
            test_fn()
            print(f"  PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {name}: {e}")
            failed += 1
            errors.append((name, str(e)))
        except Exception as e:
            print(f"  ERR   {name}: {type(e).__name__}: {e}")
            failed += 1
            errors.append((name, f"{type(e).__name__}: {e}"))

    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(scenarios)}")

    if errors:
        print()
        print("Failures:")
        for name, msg in errors:
            print(f"  - {name}: {msg}")

    sys.exit(1 if failed > 0 else 0)
