## ADDED Requirements

### Requirement: Income summary API
The API SHALL aggregate farmer income from all revenue sources (milk sales, product sales, transactions).

#### Scenario: Farmer views weekly income
- **GIVEN** an authenticated farmer with sell records and milk sales
- **WHEN** they GET `/v1/income/summary/{user_id}?period=week`
- **THEN** they receive total earnings for the current week, comparison with previous week, and daily breakdown

#### Scenario: Farmer views income breakdown by product
- **GIVEN** an authenticated farmer with varied product sales
- **WHEN** they GET `/v1/income/breakdown/{user_id}`
- **THEN** they receive income grouped by product category (milk, eggs, goat products, manure, other) with amounts and percentages

#### Scenario: Admin views income analytics
- **GIVEN** an authenticated admin user
- **WHEN** they GET `/v1/admin/income/stats`
- **THEN** they receive total farmer income, average income per farmer, income distribution, and top earners
