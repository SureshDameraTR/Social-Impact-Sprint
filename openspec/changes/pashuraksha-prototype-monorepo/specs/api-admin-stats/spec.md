## ADDED Requirements

### Requirement: Dashboard statistics endpoint
The API SHALL provide aggregated statistics for the admin dashboard including total farmers, total animals, today's milk collection, and active health alerts.

#### Scenario: Admin fetches dashboard stats
- **WHEN** `GET /v1/admin/stats` is called by an admin user
- **THEN** the API returns `{total_farmers: int, total_animals: int, today_milk_liters: float, active_alerts: int, total_shg_groups: int}`

### Requirement: Milk collection chart data
The API SHALL provide time-series data for milk collection charts.

#### Scenario: Admin fetches 30-day milk chart
- **WHEN** `GET /v1/admin/charts/milk?days=30` is called
- **THEN** the API returns `{data: [{date: str, total_liters: float, farmer_count: int}]}` for each day

### Requirement: GIS data for disease alerts map
The API SHALL provide geo-located data for rendering disease alerts on a map.

#### Scenario: Admin fetches map data
- **WHEN** `GET /v1/admin/gis/alerts` is called
- **THEN** the API returns `{alerts: [{id, animal_id, farmer_name, village, lat, lng, risk_level, symptoms, event_date}]}`

### Requirement: Admin-only access control
Admin aggregation endpoints SHALL require the requesting user to have `role: "admin"`.

#### Scenario: Farmer cannot access admin stats
- **WHEN** `GET /v1/admin/stats` is called by a user with `role: "farmer"`
- **THEN** the API returns `403 {"detail": "Admin access required"}`

### Requirement: IoT device monitoring stats
The API SHALL provide aggregated IoT device statistics for admin monitoring.

#### Scenario: Admin fetches IoT device stats
- **WHEN** `GET /v1/admin/stats/iot` is called
- **THEN** the API returns `{total_devices: int, online: int, offline: int, last_sync_oldest: datetime, devices_by_type: {weather_station: int, milk_analyzer: int, rfid_reader: int}}`

#### Scenario: Admin views device list with status
- **WHEN** `GET /v1/admin/iot/devices` is called
- **THEN** the API returns `[{device_id, device_type, farmer_id, village, status: "online"|"offline", firmware_version, last_sync_at}]` with pagination

### Requirement: Multi-species analytics
The API SHALL provide species distribution analytics for the admin dashboard.

#### Scenario: Admin fetches species distribution
- **WHEN** `GET /v1/admin/stats/species` is called
- **THEN** the API returns `{total_animals: int, by_species: {cattle: int, buffalo: int, goat: int, sheep: int, poultry: int}, species_distribution_pct: {cattle: float, ...}}`

### Requirement: Income analytics
The API SHALL provide aggregated income analytics across all farmers.

#### Scenario: Admin fetches income stats
- **WHEN** `GET /v1/admin/stats/income` is called
- **THEN** the API returns `{total_income: float, avg_income_per_farmer: float, income_by_product: {milk: float, eggs: float, goat_milk: float, wool: float, manure: float}, income_distribution: [{range: "0-5000", farmer_count: int}, ...]}`

### Requirement: Disease surveillance stats
The API SHALL provide disease surveillance aggregation for outbreak monitoring.

#### Scenario: Admin fetches disease surveillance
- **WHEN** `GET /v1/admin/stats/disease-surveillance` is called
- **THEN** the API returns `{active_hotspots: int, outbreak_reports: [{id, status, affected_area, animal_count, probable_diseases}], containment_rate_pct: float, high_risk_events_7d: int}`

### Requirement: Platform impact metrics
The API SHALL provide high-level impact metrics for government reporting and stakeholder dashboards.

#### Scenario: Admin fetches impact metrics
- **WHEN** `GET /v1/admin/stats/impact` is called
- **THEN** the API returns `{total_farmers: int, total_animals: int, total_income_generated: float, scheme_applications_served: int, shg_groups_active: int, villages_covered: int, vaccinations_administered: int}`

### Requirement: Vaccination coverage stats
The API SHALL provide village-level vaccination coverage percentages.

#### Scenario: Admin fetches vaccination coverage
- **WHEN** `GET /v1/admin/stats/vaccination-coverage` is called
- **THEN** the API returns `{overall_coverage_pct: float, by_village: [{village_code, village_name, total_animals, vaccinated_animals, coverage_pct, overdue_count}], by_species: [{species, coverage_pct}]}`
