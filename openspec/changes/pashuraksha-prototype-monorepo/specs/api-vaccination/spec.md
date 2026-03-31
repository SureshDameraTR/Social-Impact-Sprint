## ADDED Requirements

### Requirement: Enhanced vaccination management with scheduling
The API SHALL provide species-specific vaccination calendars based on ICAR guidelines, automatic booster scheduling, reminder generation, and village-level coverage reporting.

#### Scenario: Vaccination recorded with auto-scheduling
- **WHEN** `POST /v1/vaccinations/record` is called with `{"animal_id": 1, "vaccine_name": "HS", "batch_number": "HS2026-A1", "administered_by": "Dr. Sharma"}`
- **THEN** the API returns `201` with the vaccination record AND auto-schedules the next booster based on the species-specific ICAR calendar with `next_due_date`

#### Scenario: Querying due vaccinations for a farmer
- **WHEN** `GET /v1/vaccinations/due?farmer_id=42&window_days=30` is called
- **THEN** the API returns animals with upcoming or overdue vaccinations including `animal_name`, `vaccine_name`, `due_date`, and `status` (upcoming/overdue)

#### Scenario: Overdue vaccinations flagged
- **WHEN** a vaccination due date has passed without a recorded administration
- **THEN** the animal appears in due queries with `status: "overdue"` and `days_overdue` count

#### Scenario: Village-level vaccination coverage report
- **WHEN** `GET /v1/vaccinations/coverage?village_code=RJ14001&vaccine=FMD` is called
- **THEN** the API returns `total_eligible`, `total_vaccinated`, `coverage_pct`, and `last_campaign_date`

### Requirement: ICAR vaccination calendar
The API SHALL maintain species-specific vaccination schedules per ICAR guidelines with vaccine name, recommended age, and booster intervals.

#### Scenario: Retrieving vaccination calendar for species
- **WHEN** `GET /v1/vaccinations/calendar?species=cattle` is called
- **THEN** the API returns the full ICAR vaccination schedule with `vaccine_name`, `first_dose_age_months`, `booster_interval_months`, and `mandatory` flag
