## ADDED Requirements

### Requirement: APMC mandi commodity price API
The API SHALL provide daily APMC mandi rates for livestock commodities including milk, eggs, goat meat, wool, and manure by district, sourced from Agmarknet.

#### Scenario: Farmer requests today's commodity rates
- **WHEN** `GET /v1/market/prices?district_code=RJ14` is called
- **THEN** the API returns `200` with today's APMC prices for all tracked commodities including `commodity`, `unit`, `min_price`, `max_price`, `modal_price`, and `mandi_name`

#### Scenario: Farmer requests rates for specific commodity
- **WHEN** `GET /v1/market/prices?district_code=RJ14&commodity=goat_meat` is called
- **THEN** the API returns prices filtered to the specified commodity across all mandis in the district

#### Scenario: Price data unavailable for today
- **WHEN** today's Agmarknet data has not yet been published or the source is unreachable
- **THEN** the API returns the last known prices with `stale_since` timestamp and `data_date` indicating the actual date of the prices

#### Scenario: Price trend requested
- **WHEN** `GET /v1/market/prices/trend?district_code=RJ14&commodity=milk&days=30` is called
- **THEN** the API returns daily modal prices for the past 30 days with `trend_direction` (rising/falling/stable)

### Requirement: Agmarknet data ingestion
The API SHALL ingest daily price data from Agmarknet and store it locally for historical trend analysis.

#### Scenario: Daily price ingestion succeeds
- **WHEN** the scheduled daily ingestion job runs at 10:00 IST
- **THEN** prices for all tracked commodities and districts are fetched and stored with `ingested_at` timestamp
