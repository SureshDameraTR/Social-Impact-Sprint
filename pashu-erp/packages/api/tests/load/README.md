# PashuRaksha API - k6 Load Tests

Load tests for the main write paths in the PashuRaksha ERP API.

## Prerequisites

1. **k6 installed** -- https://grafana.com/docs/k6/latest/set-up/install-k6/
   ```bash
   # Ubuntu/Debian
   sudo gpg -k
   sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
     --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D68
   echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
     | sudo tee /etc/apt/sources.list.d/k6.list
   sudo apt-get update && sudo apt-get install k6

   # macOS
   brew install k6
   ```

2. **API running** at `http://localhost:8000` (or set `BASE_URL`):
   ```bash
   cd pashu-erp && docker compose up -d
   # or
   cd pashu-erp/packages/api && uv run uvicorn app.main:app --port 8000
   ```

3. **Test user exists** -- The OTP flow will auto-create a user if one does not exist for the given phone number. In development mode the OTP provider logs the code to the console. Set `TEST_OTP` to match.

## Running

### Default run (all scenarios, 2 minutes each)

```bash
cd pashu-erp/packages/api
k6 run tests/load/k6-write-paths.js
```

### With custom settings

```bash
k6 run \
  -e BASE_URL=http://localhost:8000 \
  -e AUTH_PHONE='+919900000001' \
  -e TEST_OTP=123456 \
  -e DURATION=1m \
  -e MILK_VUS=10 \
  -e ANIMAL_VUS=3 \
  -e HEALTH_VUS=5 \
  -e MIXED_VUS=5 \
  tests/load/k6-write-paths.js
```

### Quick smoke test (low VUs, short duration)

```bash
k6 run -e DURATION=10s -e MILK_VUS=2 -e ANIMAL_VUS=1 -e HEALTH_VUS=1 -e MIXED_VUS=1 \
  tests/load/k6-write-paths.js
```

## Environment Variables

| Variable      | Default                | Description                          |
|---------------|------------------------|--------------------------------------|
| `BASE_URL`    | `http://localhost:8000`| API base URL                         |
| `AUTH_PHONE`  | `+919900000001`       | Phone number for OTP auth            |
| `TEST_OTP`    | `123456`              | OTP code (dev mode logs it to console)|
| `CLIENT_TYPE` | `mobile`              | `mobile` returns token in body       |
| `DURATION`    | `2m`                  | Duration per scenario                |
| `MILK_VUS`    | `20`                  | Virtual users for milk recording     |
| `ANIMAL_VUS`  | `5`                   | Virtual users for animal registration|
| `HEALTH_VUS`  | `10`                  | Virtual users for health events      |
| `MIXED_VUS`   | `10`                  | Virtual users for mixed writes       |

## Scenarios

| Scenario             | VUs | Endpoint                    | What it tests                          |
|----------------------|-----|-----------------------------|----------------------------------------|
| `milk_recording`     | 20  | `POST /v1/milk/yield`       | Milk yield recording with random data  |
| `animal_registration`| 5   | `POST /v1/animals`          | Animal creation + duplicate name edge  |
| `health_events`      | 10  | `POST /v1/health/log`       | Health events with symptom triage      |
| `mixed_writes`       | 10  | All write endpoints         | Realistic mixed traffic pattern        |

## Thresholds

These thresholds gate the test -- if any threshold fails, k6 exits with a non-zero code.

| Metric                                           | Threshold          |
|--------------------------------------------------|--------------------|
| `http_req_duration{scenario:milk_recording}`     | p95 < 500ms        |
| `http_req_duration{scenario:animal_registration}`| p95 < 500ms        |
| `http_req_duration{scenario:health_events}`      | p95 < 500ms        |
| `http_req_duration{scenario:mixed_writes}`       | p95 < 500ms        |
| `http_req_failed`                                | rate < 1%          |
| `http_reqs`                                      | rate > 50 req/s    |

## Interpreting Results

After a run, k6 prints a summary like:

```
     checks.........................: 98.50% 1970 out of 2000
     http_req_duration..............: avg=45ms  min=12ms  med=38ms  max=320ms  p(90)=85ms  p(95)=120ms
     http_req_failed................: 0.50%  10 out of 2000
     http_reqs......................: 2000   66.66/s
```

Key things to look for:

- **checks**: Percentage of successful response validations. Below 95% warrants investigation.
- **http_req_duration p(95)**: 95th percentile latency. Values above 500ms indicate a bottleneck.
- **http_req_failed**: Error rate. Above 1% suggests the API is dropping requests under load.
- **http_reqs rate**: Aggregate throughput. Below 50 req/s with 45 VUs means requests are queuing.

## Custom Metrics

The test tracks additional custom metrics:

| Metric                     | Type  | Description                      |
|----------------------------|-------|----------------------------------|
| `animal_created_success`   | Rate  | Fraction of 201 responses        |
| `yield_recorded_success`   | Rate  | Fraction of 201 responses        |
| `health_logged_success`    | Rate  | Fraction of 201 responses        |
| `sale_recorded_success`    | Rate  | Fraction of 201 responses        |
| `animal_create_duration`   | Trend | Latency distribution (ms)        |
| `yield_record_duration`    | Trend | Latency distribution (ms)        |
| `health_log_duration`      | Trend | Latency distribution (ms)        |
| `sale_record_duration`     | Trend | Latency distribution (ms)        |

## File Structure

```
tests/load/
  k6-config.js          # Shared config, helpers, payload factories
  k6-write-paths.js     # Main test script with scenarios
  README.md             # This file
```

## Cleanup

Load tests create real records in the database. After testing, clean up with:

```sql
-- Connect to your test database
DELETE FROM yield_logs WHERE notes LIKE 'Load test%';
DELETE FROM health_events WHERE description LIKE 'Load test%';
DELETE FROM sell_records WHERE notes LIKE 'Load test%';
DELETE FROM animals WHERE name = 'LoadTestCow' OR name = 'DuplicateTestAnimal';
```

Or, if running against Docker Compose, simply recreate the database:

```bash
docker compose down -v && docker compose up -d
```
