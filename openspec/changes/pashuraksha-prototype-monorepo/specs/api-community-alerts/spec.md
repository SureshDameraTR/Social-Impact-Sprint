## ADDED Requirements

### Requirement: Community disease alert system API
The API SHALL enable crowd-sourced disease reporting with GPS coordinates, spatial querying for nearby alerts, admin verification, and hotspot detection with k-anonymity safeguards.

#### Scenario: Farmer reports a disease observation
- **WHEN** `POST /v1/alerts/report` is called with `{"disease_type": "FMD_suspected", "species_affected": "cattle", "animal_count": 3, "gps_lat": 26.9124, "gps_lon": 75.7873, "description": "Blisters on mouth and feet"}`
- **THEN** the API returns `201` with `alert_id`, `status: "unverified"`, and `nearby_reports_count`

#### Scenario: Querying nearby active alerts
- **WHEN** `GET /v1/alerts/nearby?lat=26.9124&lon=75.7873&radius_km=25` is called
- **THEN** the API returns active alerts within the radius with `alert_id`, `disease_type`, `distance_km`, `report_count`, `status`, and `reported_at`

#### Scenario: Admin verifies a disease alert
- **WHEN** `PUT /v1/alerts/{alert_id}/verify` is called by an admin with `{"status": "confirmed", "verified_disease": "FMD"}`
- **THEN** the alert is marked as confirmed AND push notifications are triggered to farmers within 25km radius

#### Scenario: Hotspot detection with k-anonymity
- **WHEN** 5 or more unverified reports for the same disease type exist within a 10km radius within 7 days
- **THEN** a hotspot is automatically created with `hotspot_id` and `severity_level` without revealing individual reporter identities

#### Scenario: Alert expiry
- **WHEN** an alert has no new reports for 14 days AND is not admin-confirmed
- **THEN** the alert status changes to `expired` and is excluded from nearby queries

### Requirement: Privacy safeguards
The API SHALL enforce k-anonymity with a minimum threshold of 5 reports before creating a hotspot, ensuring individual reporters cannot be identified.

#### Scenario: Below k-anonymity threshold
- **WHEN** fewer than 5 reports exist in a cluster
- **THEN** the reports are tracked internally but no public hotspot is created
