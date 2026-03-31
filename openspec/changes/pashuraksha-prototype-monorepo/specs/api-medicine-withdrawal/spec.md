## ADDED Requirements

### Requirement: Medicine withdrawal period calculator API
The API SHALL track administered medicines per animal and calculate safe withdrawal dates for milk and meat based on the ICAR/FSSAI drug database.

#### Scenario: Farmer records medicine administration
- **WHEN** `POST /v1/medicines/administer` is called with `{"animal_id": 1, "medicine_id": "MED-042", "dosage": "5ml", "administered_on": "2026-03-28"}`
- **THEN** the API returns `201` with the record including `withdrawal_milk_until` and `withdrawal_meat_until` dates calculated from the ICAR/FSSAI drug database for that medicine and species

#### Scenario: Farmer queries withdrawal status for an animal
- **WHEN** `GET /v1/medicines/withdrawal-status/{animal_id}` is called
- **THEN** the API returns `{animal_id, active_medicines: [{medicine_name, milk_safe_from, meat_safe_from, days_remaining}], overall_milk_safe: bool, overall_meat_safe: bool}`

#### Scenario: Withdrawal period expires
- **WHEN** all active withdrawal periods for an animal have passed the current date
- **THEN** the animal status returns `overall_milk_safe: true` and `overall_meat_safe: true`, clearing the animal for milk and meat sale

#### Scenario: Multiple medicines with overlapping withdrawal periods
- **WHEN** an animal has multiple active medicines with different withdrawal end dates
- **THEN** the API uses the longest remaining withdrawal period for `overall_milk_safe` and `overall_meat_safe`, ensuring no medicine is still active before clearing

### Requirement: Searchable medicine catalog
The API SHALL provide a searchable medicine catalog with bilingual names and species-specific withdrawal periods sourced from ICAR/FSSAI guidelines.

#### Scenario: Farmer searches medicine catalog
- **WHEN** `GET /v1/medicines/catalog?q=amoxicillin&species=cattle` is called
- **THEN** the API returns matching medicines with `{medicine_id, name_en, name_kn, category, withdrawal_milk_days, withdrawal_meat_days, species: "cattle", source: "FSSAI"}`

#### Scenario: Farmer browses full catalog by species
- **WHEN** `GET /v1/medicines/catalog?species=goat` is called without a search query
- **THEN** the API returns the full medicine list for goats with pagination, sorted alphabetically by `name_en`
