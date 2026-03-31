## ADDED Requirements

### Requirement: Feed ration optimization API
The API SHALL calculate balanced daily rations from locally available ingredients based on NDDB/ICAR feeding standards for different species, breeds, and production stages.

#### Scenario: Farmer requests optimized ration
- **WHEN** `POST /v1/feed/optimize` is called with `{"species": "cattle", "breed": "Gir", "weight_kg": 350, "lactation_stage": "mid", "daily_milk_yield_liters": 8}`
- **THEN** the API returns `200` with an optimized daily ration including `ingredients` list with `name`, `quantity_kg`, `dry_matter_kg`, and total `crude_protein_pct`, `tde_pct`, `estimated_cost_inr`

#### Scenario: Farmer specifies locally available ingredients
- **WHEN** `POST /v1/feed/optimize` includes `{"available_ingredients": ["wheat_straw", "mustard_cake", "bajra", "mineral_mixture"]}`
- **THEN** the ration is optimized using only those ingredients with `cost_estimate_inr` based on local market prices

#### Scenario: Ration for non-lactating animal
- **WHEN** `POST /v1/feed/optimize` is called with `{"species": "goat", "breed": "Sirohi", "weight_kg": 35, "lactation_stage": "dry"}`
- **THEN** the API returns a maintenance ration with lower protein requirements per ICAR standards

#### Scenario: Nutritional deficiency warning
- **WHEN** the available ingredients cannot meet minimum nutritional requirements
- **THEN** the response includes `warnings` array with `deficiency_type`, `required_amount`, `actual_amount`, and `suggested_supplement`

### Requirement: Ingredient nutrient database
The API SHALL maintain a database of common Indian livestock feed ingredients with their nutritional composition per NDDB standards.

#### Scenario: Listing available feed ingredients
- **WHEN** `GET /v1/feed/ingredients?species=cattle` is called
- **THEN** the API returns all ingredients suitable for the species with `name`, `crude_protein_pct`, `tde_pct`, `cost_per_kg_inr`
