## ADDED Requirements

### Requirement: Weather forecast and alerts API
The API SHALL provide IMD district-level weather forecasts with 5-day outlook, heat stress indicators, and extreme weather alerts for livestock management.

#### Scenario: Farmer requests weather forecast
- **WHEN** `GET /v1/weather/forecast?district_code=RJ14` is called
- **THEN** the API returns `200` with a 5-day district forecast including `date`, `temp_min`, `temp_max`, `humidity`, `rainfall_mm`, and `heat_stress_index` per day

#### Scenario: Heat stress indicator included in forecast
- **WHEN** the forecast `temp_max` exceeds 40C AND `humidity` exceeds 60%
- **THEN** each affected day includes `heat_stress_level: "severe"` with `advisory: "Ensure shade, increase water availability"`

#### Scenario: Extreme weather alert is active
- **WHEN** `GET /v1/weather/forecast?district_code=RJ14` is called AND an IMD extreme weather alert is active for the district
- **THEN** the response includes an `alerts` array with `alert_type`, `severity`, `valid_until`, and `advisory_text`

#### Scenario: IMD data source unavailable
- **WHEN** the IMD API is unreachable or times out
- **THEN** the API returns the last known forecast with `stale_since` timestamp and `source: "cache"` indicator

### Requirement: Forecast caching strategy
The API SHALL cache IMD forecast data with a 6-hour TTL to reduce upstream load and ensure availability.

#### Scenario: Cached forecast served within TTL
- **WHEN** a forecast was fetched from IMD less than 6 hours ago
- **THEN** the cached response is returned with `cache_age_seconds` in the response metadata
