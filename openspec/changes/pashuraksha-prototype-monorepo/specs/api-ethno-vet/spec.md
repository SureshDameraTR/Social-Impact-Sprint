## ADDED Requirements

### Requirement: Ethno-veterinary traditional medicine API
The API SHALL provide a searchable database of traditional livestock remedies with evidence ratings, preparation instructions, and safety warnings, sourced from ICAR ethno-veterinary documentation.

#### Scenario: Farmer searches remedies by condition
- **WHEN** `GET /v1/ethnovet/remedies?condition=diarrhea&species=cattle` is called
- **THEN** the API returns matching remedies filtered by species with `remedy_name`, `ingredients`, `evidence_rating` (A/B/C), and `preparation_summary`

#### Scenario: Farmer views remedy detail
- **WHEN** `GET /v1/ethnovet/remedies/{remedy_id}` is called
- **THEN** the API returns full details including `preparation_steps`, `dosage_by_species` (map of species to dosage), `evidence_rating`, `safety_warnings`, `contraindications`, and `source_reference`

#### Scenario: Search with no matching remedies
- **WHEN** no remedies match the condition and species combination
- **THEN** the API returns `200` with empty `remedies` array and `suggestion: "Consult a veterinarian for this condition"`

#### Scenario: Safety warning for pregnant animals
- **WHEN** a remedy has known risks for pregnant animals AND the request includes `pregnant: true`
- **THEN** the response includes `safety_alert: "NOT_SAFE_DURING_PREGNANCY"` with alternative remedy suggestions

### Requirement: Evidence rating system
The API SHALL classify remedies using a three-tier evidence rating: A (clinical evidence), B (field-validated), C (traditional knowledge only).

#### Scenario: Filtering by evidence level
- **WHEN** `GET /v1/ethnovet/remedies?condition=bloat&min_evidence=B` is called
- **THEN** only remedies with evidence rating A or B are returned, excluding rating C
