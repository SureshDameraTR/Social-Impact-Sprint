## ADDED Requirements

### Requirement: Product marketplace API
The API SHALL support recording and querying product sales across multiple categories (milk, eggs, goat/sheep products, manure, wool).

#### Scenario: Farmer records a sale
- **GIVEN** an authenticated farmer user
- **WHEN** they POST to `/v1/marketplace/sell` with product_type, quantity, unit, price_per_unit, and optional buyer_name
- **THEN** a sell record is created with auto-calculated total_amount and the response includes the full record

#### Scenario: Farmer views sale history
- **GIVEN** an authenticated farmer with existing sell records
- **WHEN** they GET `/v1/marketplace/history/{user_id}`
- **THEN** they receive a paginated list of their sell records sorted by most recent, filterable by product_type and date range

#### Scenario: Local market rates are available
- **GIVEN** any authenticated user
- **WHEN** they GET `/v1/marketplace/rates`
- **THEN** they receive current Karnataka APMC mandal rates for all product categories (milk ₹28-35/L, eggs ₹5-7/each, goat milk ₹60-80/L, manure ₹2-5/kg)

### Requirement: Marketplace admin stats
The API SHALL provide marketplace aggregation endpoints for admin dashboard.

#### Scenario: Admin views marketplace stats
- **GIVEN** an authenticated admin user
- **WHEN** they GET `/v1/admin/marketplace/stats`
- **THEN** they receive total sales volume, total revenue, revenue breakdown by product category, and active seller count

### Requirement: Market rate reference with Agmarknet APMC data
The API SHALL display Agmarknet APMC mandal rates alongside the farmer's asking price so farmers can make informed pricing decisions.

#### Scenario: Farmer sees APMC reference rate when listing a product
- **WHEN** `GET /v1/marketplace/rates?product_type=milk&district=Mysore` is called
- **THEN** the API returns `{product_type: "milk", farmer_avg_price: 32, apmc_rate: 34, apmc_market: "Mysore APMC", rate_date: "2026-03-30", price_difference_pct: -5.9}`

#### Scenario: Rates cover all supported product types
- **WHEN** `GET /v1/marketplace/rates` is called without filters
- **THEN** the API returns APMC reference rates for milk, goat milk, eggs, sheep wool, manure, and poultry meat

### Requirement: Buyer QR code for product traceability
The API SHALL generate a QR code for each sale record containing batch number, sale date, quality grade, and product origin district. The QR SHALL NOT contain any farmer PII.

#### Scenario: Buyer scans QR for traceability
- **WHEN** `GET /v1/marketplace/qr/{sale_id}` is called
- **THEN** the API returns a QR code image (PNG) encoding `{batch_id, product_type, quantity, quality_grade, origin_district, sale_date}` — no farmer name, phone, or address

#### Scenario: QR data is verified by buyer
- **WHEN** `GET /v1/marketplace/verify/{batch_id}` is called
- **THEN** the API returns the traceability record matching the QR batch ID

### Requirement: Seasonal price trends
The API SHALL provide historical price trend data for each commodity to help farmers plan sales timing.

#### Scenario: Farmer views 12-month price trend
- **WHEN** `GET /v1/marketplace/trends?product_type=milk&months=12` is called
- **THEN** the API returns `{product_type: "milk", trend: [{month: "2025-04", avg_price: 30}, {month: "2025-05", avg_price: 31}, ...], current_price: 34, price_change_pct: 13.3}`

#### Scenario: Trend data includes seasonal annotations
- **WHEN** price trend data is returned
- **THEN** months with known seasonal factors include `{season_note: "monsoon — lower supply, higher prices"}` annotations

### Requirement: Multi-species product support
The marketplace SHALL support product categories beyond cattle milk: goat milk, sheep wool, poultry eggs, poultry meat, and organic manure as first-class product types.

#### Scenario: Farmer records a goat milk sale
- **WHEN** `POST /v1/marketplace/sell` is called with `{product_type: "goat_milk", quantity: 2, unit: "liters", price_per_unit: 70}`
- **THEN** the sale is recorded and categorized under goat milk with appropriate APMC rate comparison

#### Scenario: Farmer records a wool sale
- **WHEN** `POST /v1/marketplace/sell` is called with `{product_type: "sheep_wool", quantity: 5, unit: "kg", price_per_unit: 150}`
- **THEN** the sale is recorded under sheep wool category
