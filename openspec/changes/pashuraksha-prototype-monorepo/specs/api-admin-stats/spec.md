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
