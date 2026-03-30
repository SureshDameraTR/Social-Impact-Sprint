## ADDED Requirements

### Requirement: Milk collection recording
The API SHALL allow farmers to record milk yield per animal per shift (morning/evening) with optional FAT% and SNF% values. The rate per liter SHALL be auto-calculated from FAT/SNF slabs when provided.

#### Scenario: Farmer records morning milk yield
- **WHEN** `POST /v1/milk/record` is called with `{"animal_id": 1, "quantity_liters": 5.0, "shift": "morning"}`
- **THEN** the API returns `201` with the record including `record_id`, `collection_date` (today), and `rate_per_liter` (default rate if no FAT/SNF)

#### Scenario: Milk record includes FAT and SNF
- **WHEN** `POST /v1/milk/record` is called with `fat_pct: 4.2` and `snf_pct: 8.5`
- **THEN** the `rate_per_liter` is calculated from the FAT/SNF pricing slab and `amount_inr` is computed

### Requirement: Farmer milk history
The API SHALL return a farmer's milk collection history with totals for a given date range.

#### Scenario: Farmer views last 30 days milk history
- **WHEN** `GET /v1/milk/farmer/{farmer_id}/history?from=2026-03-01&to=2026-03-30` is called
- **THEN** the API returns `{records: [...], total_liters: float, total_earnings: float}` with daily records

### Requirement: Collection center daily summary
The API SHALL aggregate milk collection records by center for a given date.

#### Scenario: Admin views center daily summary
- **WHEN** `GET /v1/milk/center/{center_id}/daily?date=2026-03-28` is called
- **THEN** the API returns `{records: [...], total_liters: float, avg_fat: float, farmer_count: int}`

### Requirement: Yield log for animal-level tracking
The API SHALL record individual animal yield logs separate from collection center records, supporting the mobile app's per-animal recording flow.

#### Scenario: Farmer records yield via mobile
- **WHEN** `POST /v1/milk/yield` is called with `{"animal_id": 1, "quantity_liters": 5.0, "session": "morning"}`
- **THEN** a yield_log record is created linked to the animal and the current date
