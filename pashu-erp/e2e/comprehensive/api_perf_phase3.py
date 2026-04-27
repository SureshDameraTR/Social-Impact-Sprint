"""Phase 3 Part A: API Response Time Profiling.

Authenticates via OTP extraction from docker logs, then measures response
time for every reachable API endpoint.  Outputs a sorted table.
"""

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field

import httpx

API = "http://localhost:8000"


# ── Auth helpers (same pattern as conftest.py) ─────────────────────────────

def reset_otp_limits():
    subprocess.run(
        ["docker", "exec", "pashu-erp-db-1", "psql", "-U", "pashu", "-d",
         "pashuraksha", "-c",
         "UPDATE otp_requests SET request_count = 0, attempts = 0;"],
        capture_output=True, timeout=10,
    )


def extract_otp(phone: str) -> str:
    result = subprocess.run(
        ["docker", "logs", "pashu-erp-api-1", "--tail", "40"],
        capture_output=True, text=True, timeout=10,
    )
    combined = result.stdout + result.stderr
    pattern = rf"DEV OTP for {re.escape(phone)}.*?Code:\s*(\d{{6}})"
    matches = re.findall(pattern, combined, re.DOTALL)
    if not matches:
        matches = re.findall(r"Code:\s*(\d{6})", combined)
    if not matches:
        raise RuntimeError(f"No OTP found for {phone}")
    return matches[-1]


def get_token(phone: str, client_type: str = "mobile") -> str:
    with httpx.Client(base_url=API, timeout=30) as c:
        resp = c.post("/v1/auth/request-otp", json={"phone": phone})
        if resp.status_code != 200:
            raise RuntimeError(f"OTP request failed: {resp.status_code} {resp.text}")
        time.sleep(0.5)
        otp = extract_otp(phone)
        resp = c.post("/v1/auth/verify-otp",
                       json={"phone": phone, "otp": otp, "client_type": client_type})
        if resp.status_code != 200:
            raise RuntimeError(f"Verify failed: {resp.status_code} {resp.text}")
        return resp.json()["access_token"]


# ── Measurement ────────────────────────────────────────────────────────────

@dataclass
class Result:
    method: str
    path: str
    status: int
    time_ms: float
    size_bytes: int
    error: str = ""


def measure(client: httpx.Client, method: str, path: str,
            headers: dict, json_body: dict | None = None) -> Result:
    start = time.perf_counter()
    try:
        resp = client.request(method, path, headers=headers, json=json_body, timeout=30)
        elapsed = (time.perf_counter() - start) * 1000
        return Result(method, path, resp.status_code, round(elapsed, 1),
                      len(resp.content))
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        return Result(method, path, 0, round(elapsed, 1), 0, str(e)[:80])


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Phase 3 Part A: API Response Time Profiling")
    print("=" * 70)

    # 1. Auth
    reset_otp_limits()
    # Restart API to clear in-memory slowapi rate limiter
    subprocess.run(["docker", "restart", "pashu-erp-api-1"],
                   capture_output=True, timeout=30)
    # Wait for API to become healthy
    for _ in range(20):
        try:
            r = httpx.get(f"{API}/health", timeout=3)
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(1)

    print("\n[auth] Getting admin token...")
    admin_token = get_token("+919900000001")
    time.sleep(2)
    print("[auth] Getting farmer token...")
    farmer_token = get_token("+919900000002")
    time.sleep(2)
    print("[auth] Getting vet token...")
    vet_token = get_token("+919900000005")
    print("[auth] All tokens acquired.\n")

    admin_h = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    farmer_h = {"Authorization": f"Bearer {farmer_token}", "Content-Type": "application/json"}
    vet_h = {"Authorization": f"Bearer {vet_token}", "Content-Type": "application/json"}

    # 2. Fetch IDs we'll need for parameterized endpoints
    with httpx.Client(base_url=API, timeout=30) as c:
        # Get an animal ID
        r = c.get("/v1/animals?page=1&page_size=1", headers=admin_h)
        animal_id = r.json()["data"][0]["id"] if r.status_code == 200 and r.json().get("data") else "00000000-0000-0000-0000-000000000000"

        # Get farmer user_id
        r = c.get("/v1/farmers?page=1&page_size=1", headers=admin_h)
        farmer_uid = r.json()["data"][0]["id"] if r.status_code == 200 and r.json().get("data") else "00000000-0000-0000-0000-000000000000"

        # Get vet case ID
        r = c.get("/v1/vet/cases?page=1&page_size=1", headers=admin_h)
        case_id = r.json()["data"][0]["id"] if r.status_code == 200 and r.json().get("data") else "00000000-0000-0000-0000-000000000000"

        # Get a scheme ID
        r = c.get("/v1/schemes?page=1&page_size=1", headers=admin_h)
        scheme_id = r.json()["data"][0]["id"] if r.status_code == 200 and r.json().get("data") else "00000000-0000-0000-0000-000000000000"

        # Get SHG ID
        r = c.get("/v1/shg?page=1&page_size=1", headers=admin_h)
        shg_id = r.json()["data"][0]["id"] if r.status_code == 200 and r.json().get("data") else "00000000-0000-0000-0000-000000000000"

        # Get vaccination ID
        r = c.get("/v1/vaccinations/due", headers=farmer_h)
        vacc_id = "00000000-0000-0000-0000-000000000000"
        if r.status_code == 200:
            data = r.json().get("data", r.json()) if isinstance(r.json(), dict) else r.json()
            if isinstance(data, list) and data:
                vacc_id = data[0].get("id", vacc_id)

        # Get IoT device ID (uses device_id field, not id)
        r = c.get("/v1/iot/devices?page=1&page_size=1", headers=admin_h)
        device_id = "SC-GIR-0042"
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                device_id = data[0].get("device_id", data[0].get("id", device_id))

        # Get center ID
        r = c.get("/v1/milk-center/my-center", headers=admin_h)
        center_id = "00000000-0000-0000-0000-000000000000"
        if r.status_code == 200:
            center_id = r.json().get("id", center_id)

        # Get ethno-vet remedy ID
        r = c.get("/v1/ethno-vet/remedies?page=1&page_size=1", headers=admin_h)
        remedy_id = "00000000-0000-0000-0000-000000000000"
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                remedy_id = data[0]["id"]

        # Get advisory tip ID
        r = c.get("/v1/advisory/tips?page=1&page_size=1", headers=admin_h)
        tip_id = "00000000-0000-0000-0000-000000000000"
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                tip_id = data[0]["id"]

        # Get file ID
        r = c.get("/v1/files", headers=admin_h)
        file_id = "00000000-0000-0000-0000-000000000000"
        if r.status_code == 200:
            data = r.json().get("data", r.json())
            if isinstance(data, list) and data:
                file_id = data[0].get("id", data[0].get("file_id", file_id))

        # Get market rate + premium IDs
        r = c.get("/v1/reference/market-rates", headers=admin_h)
        rate_id = "00000000-0000-0000-0000-000000000000"
        if r.status_code == 200:
            data = r.json().get("data", r.json())
            if isinstance(data, list) and data:
                rate_id = data[0].get("id", rate_id)

        r = c.get("/v1/reference/insurance-premiums", headers=admin_h)
        premium_id = "00000000-0000-0000-0000-000000000000"
        if r.status_code == 200:
            data = r.json().get("data", r.json())
            if isinstance(data, list) and data:
                premium_id = data[0].get("id", premium_id)

    print(f"  animal_id={animal_id[:12]}..  farmer_uid={farmer_uid[:12]}..")
    print(f"  case_id={case_id[:12]}..  center_id={center_id[:12]}..")
    print()

    # 3. Define all GET endpoints to profile
    # Format: (method, path, auth_headers)
    endpoints = [
        # Infrastructure
        ("GET", "/health", {}),
        ("GET", "/ready", {}),
        ("GET", "/metrics", {}),
        # Auth
        ("GET", "/v1/auth/me", admin_h),
        # Admin
        ("GET", "/v1/admin/stats", admin_h),
        ("GET", "/v1/admin/charts/milk", admin_h),
        ("GET", "/v1/admin/gis/alerts", admin_h),
        # Animals
        ("GET", "/v1/animals", admin_h),
        ("GET", f"/v1/animals/{animal_id}", admin_h),
        # Farmers
        ("GET", "/v1/farmers", admin_h),
        # Health
        ("GET", "/v1/health", admin_h),
        ("GET", "/v1/health/alerts/map", admin_h),
        ("GET", f"/v1/health/history/{animal_id}", admin_h),
        # Milk
        ("GET", "/v1/milk", admin_h),
        ("GET", "/v1/milk/today", farmer_h),
        ("GET", "/v1/milk/daily-summary", admin_h),
        ("GET", "/v1/milk/history", farmer_h),
        ("GET", f"/v1/milk/farmer/{farmer_uid}/history", admin_h),
        ("GET", f"/v1/milk/center/{center_id}/daily", admin_h),
        # Milk center
        ("GET", "/v1/milk-center/my-center", admin_h),
        ("GET", "/v1/milk-center/farmers/search?q=raj", admin_h),
        ("GET", f"/v1/milk-center/{center_id}/daily-report", admin_h),
        ("GET", f"/v1/milk-center/{center_id}/farmer-settlements", admin_h),
        # Finance
        ("GET", "/v1/finance/summary", farmer_h),
        # Income
        ("GET", "/v1/income/summary", admin_h),
        ("GET", f"/v1/income/summary/{farmer_uid}", admin_h),
        ("GET", "/v1/income/monthly", admin_h),
        ("GET", "/v1/income/by-category", admin_h),
        ("GET", "/v1/income/transactions", admin_h),
        ("GET", f"/v1/income/history/{farmer_uid}", admin_h),
        ("GET", f"/v1/income/breakdown/{farmer_uid}", admin_h),
        # Marketplace
        ("GET", "/v1/marketplace", admin_h),
        ("GET", "/v1/marketplace/rates", admin_h),
        ("GET", f"/v1/marketplace/summary/{farmer_uid}", admin_h),
        ("GET", f"/v1/marketplace/history/{farmer_uid}", admin_h),
        # Insurance
        ("GET", f"/v1/insurance/policies/{farmer_uid}", admin_h),
        ("GET", f"/v1/insurance/premium-estimate/{animal_id}", admin_h),
        # Schemes
        ("GET", "/v1/schemes", admin_h),
        ("GET", f"/v1/schemes/{scheme_id}", admin_h),
        # SHG
        ("GET", "/v1/shg", admin_h),
        ("GET", f"/v1/shg/{shg_id}", admin_h),
        ("GET", f"/v1/shg/{shg_id}/compliance", admin_h),
        # Vaccinations
        ("GET", "/v1/vaccinations/due", farmer_h),
        ("GET", f"/v1/vaccinations/due/{farmer_uid}", admin_h),
        ("GET", "/v1/vaccinations/schedule", admin_h),
        ("GET", "/v1/vaccinations/schedule/cattle", admin_h),
        ("GET", f"/v1/vaccinations/{animal_id}", admin_h),
        ("GET", "/v1/vaccinations/coverage/VLG001", admin_h),
        ("GET", "/v1/vaccinations/species-breakdown", admin_h),
        ("GET", "/v1/vaccinations/village-coverage", admin_h),
        # Vet
        ("GET", "/v1/vet/cases", admin_h),
        ("GET", f"/v1/vet/cases/{case_id}", admin_h),
        ("GET", "/v1/vet/my-cases", vet_h),
        ("GET", "/v1/vet/dashboard/stats", vet_h),
        ("GET", "/v1/vet/dashboard/alerts", vet_h),
        # Medicines
        ("GET", "/v1/medicines", admin_h),
        ("GET", f"/v1/medicines/withdrawal-status/{animal_id}", admin_h),
        ("GET", "/v1/medicine-log/withdrawals", admin_h),
        # Alerts
        ("GET", "/v1/alerts/nearby?lat=12.97&lng=77.59", farmer_h),
        # Weather
        ("GET", "/v1/weather/forecast/Bangalore Urban", admin_h),
        ("GET", "/v1/weather/alerts/Bangalore Urban", admin_h),
        ("GET", "/v1/weather/tts/Bangalore Urban", admin_h),
        # IoT
        ("GET", "/v1/iot/devices", admin_h),
        ("GET", "/v1/iot/device-types", admin_h),
        ("GET", f"/v1/iot/devices/{device_id}", admin_h),
        ("GET", f"/v1/iot/devices/{device_id}/latest", admin_h),
        ("GET", "/v1/iot/readings", admin_h),
        # Registry
        ("GET", f"/v1/registry/lookup/IN-KA-001-0001", admin_h),
        # Feed
        ("GET", "/v1/feed/ingredients", admin_h),
        # Ethno-vet
        ("GET", "/v1/ethno-vet/remedies", admin_h),
        ("GET", f"/v1/ethno-vet/remedies/{remedy_id}", admin_h),
        ("GET", "/v1/ethno-vet/search?q=fever", admin_h),
        # Advisory
        ("GET", "/v1/advisory/tips", admin_h),
        ("GET", f"/v1/advisory/tips/{tip_id}", admin_h),
        # Users
        ("GET", "/v1/users/profile", farmer_h),
        # Reference
        ("GET", "/v1/reference/market-rates", admin_h),
        ("GET", "/v1/reference/insurance-premiums", admin_h),
        ("GET", "/v1/reference/medicines", admin_h),
        # Files
        ("GET", "/v1/files", admin_h),
        ("GET", f"/v1/files/{file_id}", admin_h),
        # Map
        ("GET", "/v1/map/points", admin_h),
        # Consent
        ("GET", "/v1/consent/my", farmer_h),
        # Onboarding
        # (POST only — skip)
    ]

    # 4. Measure each endpoint
    results: list[Result] = []
    with httpx.Client(base_url=API, timeout=30) as client:
        for method, path, headers in endpoints:
            r = measure(client, method, path, headers)
            results.append(r)
            # Color indicator
            if r.time_ms < 200:
                color = "\033[92m"  # green
            elif r.time_ms < 500:
                color = "\033[93m"  # yellow
            else:
                color = "\033[91m"  # red
            status_str = f"{r.status}" if r.status else "ERR"
            print(f"  {color}{r.time_ms:>8.1f}ms\033[0m  {status_str:>3}  {method} {path[:70]}")

    # 5. Sort by response time descending
    results.sort(key=lambda r: r.time_ms, reverse=True)

    # 6. Print summary table
    print("\n" + "=" * 90)
    print(f"{'TIME':>10}  {'STATUS':>6}  {'SIZE':>8}  {'METHOD':<6}  PATH")
    print("-" * 90)
    for r in results:
        if r.time_ms < 200:
            tier = "GREEN"
        elif r.time_ms < 500:
            tier = "YELLOW"
        else:
            tier = "RED"
        size_str = f"{r.size_bytes:,}" if r.size_bytes else "—"
        print(f"{r.time_ms:>8.1f}ms  {r.status:>6}  {size_str:>8}  {r.method:<6}  {r.path}")

    # 7. Stats
    times = [r.time_ms for r in results if r.status and r.status < 500]
    if times:
        times_sorted = sorted(times)
        p50 = times_sorted[len(times_sorted) // 2]
        p95 = times_sorted[int(len(times_sorted) * 0.95)]
        p99 = times_sorted[int(len(times_sorted) * 0.99)]
        avg = sum(times) / len(times)
        green = sum(1 for t in times if t < 200)
        yellow = sum(1 for t in times if 200 <= t < 500)
        red = sum(1 for t in times if t >= 500)

        print(f"\n{'─' * 50}")
        print(f"  Total endpoints measured: {len(results)}")
        print(f"  Successful (2xx/4xx):     {len(times)}")
        print(f"  Average:   {avg:.1f}ms")
        print(f"  P50:       {p50:.1f}ms")
        print(f"  P95:       {p95:.1f}ms")
        print(f"  P99:       {p99:.1f}ms")
        print(f"  Min:       {times_sorted[0]:.1f}ms")
        print(f"  Max:       {times_sorted[-1]:.1f}ms")
        print(f"  GREEN (<200ms):  {green}")
        print(f"  YELLOW (200-500ms): {yellow}")
        print(f"  RED (>500ms):    {red}")

    # 8. Save to JSON
    out = {
        "total": len(results),
        "stats": {
            "avg_ms": round(avg, 1) if times else 0,
            "p50_ms": round(p50, 1) if times else 0,
            "p95_ms": round(p95, 1) if times else 0,
            "p99_ms": round(p99, 1) if times else 0,
            "min_ms": round(times_sorted[0], 1) if times else 0,
            "max_ms": round(times_sorted[-1], 1) if times else 0,
        },
        "results": [
            {"method": r.method, "path": r.path, "status": r.status,
             "time_ms": r.time_ms, "size_bytes": r.size_bytes, "error": r.error}
            for r in results
        ],
    }
    with open("/home/sdamera/workbench/Social-Impact-Sprint/pashu-erp/e2e/comprehensive/perf_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  Results saved to e2e/comprehensive/perf_results.json")


if __name__ == "__main__":
    main()
