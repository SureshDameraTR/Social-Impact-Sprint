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
