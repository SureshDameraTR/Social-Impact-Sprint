## ADDED Requirements

### Requirement: Animal CRUD with Pashu Aadhaar support
The API SHALL provide full CRUD operations for animals owned by the authenticated farmer. Animals SHALL support the `pashu_aadhaar_id` field (12-digit INAPH ear tag, nullable). List endpoints SHALL support filtering by species.

#### Scenario: Farmer adds a new cow
- **WHEN** `POST /v1/animals` is called with `{"name": "Lakshmi", "species": "cattle", "breed": "Hallikar", "sex": "female"}`
- **THEN** the API returns `201` with the created animal including auto-generated `id` and `created_at`

#### Scenario: Farmer lists their animals
- **WHEN** `GET /v1/animals` is called by an authenticated farmer
- **THEN** the API returns only animals owned by that farmer, with pagination support

#### Scenario: Farmer views animal detail
- **WHEN** `GET /v1/animals/{id}` is called for an animal owned by the farmer
- **THEN** the API returns the full animal record including health summary and vaccination status

#### Scenario: Farmer updates Pashu Aadhaar
- **WHEN** `PATCH /v1/animals/{id}` is called with `{"pashu_aadhaar_id": "123456789012"}`
- **THEN** the animal's Pashu Aadhaar ID is updated

#### Scenario: Farmer cannot access another farmer's animal
- **WHEN** `GET /v1/animals/{id}` is called for an animal owned by a different farmer
- **THEN** the API returns `404`
