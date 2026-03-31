## ADDED Requirements

### Requirement: Bharat Pashudhan national registry integration
The API SHALL integrate with the Bharat Pashudhan national livestock registry to sync Pashu Aadhaar IDs and pull/push animal records. Prototype phase uses mock API responses.

#### Scenario: Looking up animal by Pashu Aadhaar ID
- **WHEN** `GET /v1/pashudhan/lookup/{pashu_aadhaar_id}` is called with a valid 12-digit Pashu Aadhaar ID
- **THEN** the API returns `200` with the animal profile including `species`, `breed`, `sex`, `date_of_birth`, `owner_name`, `district`, and `vaccination_history`

#### Scenario: Pashu Aadhaar ID not found
- **WHEN** `GET /v1/pashudhan/lookup/{pashu_aadhaar_id}` is called with an unregistered ID
- **THEN** the API returns `404` with `error: "PASHU_AADHAAR_NOT_FOUND"` and `suggestion: "Register at nearest Pashudhan Kendra"`

#### Scenario: Syncing local health data to national registry
- **WHEN** `POST /v1/pashudhan/sync` is called with `{"pashu_aadhaar_id": "...", "health_events": [...], "vaccinations": [...]}`
- **THEN** the API pushes health data to Bharat Pashudhan and returns `200` with `sync_status: "accepted"` and `sync_id`

#### Scenario: Pulling vaccination history from registry
- **WHEN** `GET /v1/pashudhan/vaccinations/{pashu_aadhaar_id}` is called
- **THEN** the API returns the complete vaccination history from the national registry including `vaccine_name`, `date`, `administering_authority`

### Requirement: Mock responses for prototype
The API SHALL return realistic mock responses during the prototype phase, simulating Bharat Pashudhan API behavior with seeded data.

#### Scenario: Mock mode returns consistent data
- **WHEN** the API is running in prototype mode AND a lookup is performed
- **THEN** the response uses seeded mock data with `_mock: true` flag in response metadata
