## ADDED Requirements

### Requirement: Transaction recording
The API SHALL allow recording income and expense transactions with category, amount, and optional reference ID.

#### Scenario: Farmer records milk sale income
- **WHEN** `POST /v1/finance/transaction` is called with `{"type": "income", "amount": 500.00, "category": "milk_sale"}`
- **THEN** the API returns `201` with `tx_id` and `status: "completed"`

#### Scenario: Farmer records veterinary expense
- **WHEN** `POST /v1/finance/transaction` is called with `{"type": "expense", "amount": 200.00, "category": "vet_fee"}`
- **THEN** the API returns `201` with the transaction record

### Requirement: Financial summary
The API SHALL provide income/expense summaries grouped by period and category.

#### Scenario: Farmer views monthly summary
- **WHEN** `GET /v1/finance/summary?period=monthly` is called
- **THEN** the API returns `{income: float, expenses: float, net: float, breakdown: [{category, amount}]}`
