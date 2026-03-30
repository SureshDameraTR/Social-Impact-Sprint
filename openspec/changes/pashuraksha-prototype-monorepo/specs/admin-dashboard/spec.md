## ADDED Requirements

### Requirement: Admin authentication
The admin panel SHALL have a login page that authenticates admin users via the same JWT auth API. Only users with `role: "admin"` SHALL access the dashboard.

#### Scenario: Admin logs in
- **WHEN** an admin enters credentials and authenticates
- **THEN** the JWT is stored and the admin sees the dashboard home page

#### Scenario: Non-admin is rejected
- **WHEN** a farmer-role user attempts to access the admin panel
- **THEN** they are redirected to a "Not authorized" page

### Requirement: Dashboard with stat cards
The admin dashboard home page SHALL display 4 stat cards: total farmers, total animals, today's milk collection (liters), and active health alerts.

#### Scenario: Dashboard loads with stats
- **WHEN** the admin navigates to the dashboard
- **THEN** 4 stat cards are displayed with current values from `GET /v1/admin/stats`

### Requirement: Milk collection line chart
The dashboard SHALL display a Recharts line chart showing daily milk collection totals for the last 30 days.

#### Scenario: Chart renders with 30-day data
- **WHEN** the dashboard loads
- **THEN** a line chart shows daily milk totals with date on x-axis and liters on y-axis

### Requirement: GIS map with disease alerts
The dashboard SHALL display a react-leaflet map centered on Karnataka showing farmer location pins and disease alert overlays. The map SHALL use OpenStreetMap tiles.

#### Scenario: Map shows disease alerts
- **WHEN** the admin views the alerts map
- **THEN** markers appear at locations with health events, color-coded by risk level (red=high, yellow=moderate, green=low)

#### Scenario: Map loads without SSR errors
- **WHEN** the admin panel page with the map is server-rendered
- **THEN** the map component is loaded via `next/dynamic` with `ssr: false` to avoid Leaflet's `window` dependency

### Requirement: Farmer CRUD table
The admin panel SHALL provide a Refine-powered data table for farmers with search, sort, and pagination.

#### Scenario: Admin searches for a farmer
- **WHEN** the admin types a name in the search box
- **THEN** the farmer table filters to matching results

### Requirement: Animal list table
The admin panel SHALL provide a filterable animal list with species filter and owner column.

#### Scenario: Admin filters animals by species
- **WHEN** the admin selects "cattle" from the species filter
- **THEN** only cattle records are displayed

### Requirement: Health alerts page
The admin panel SHALL display recent high-risk health events with farmer name, animal, symptoms, risk level, and event date.

#### Scenario: Admin views active alerts
- **WHEN** the admin navigates to the alerts page
- **THEN** health events with `risk_level: "high"` are listed in reverse chronological order

### Requirement: Government schemes catalog page
The admin panel SHALL display a read-only table of government schemes with name, ministry, subsidy amount, and active status.

#### Scenario: Admin browses schemes
- **WHEN** the admin navigates to the schemes page
- **THEN** all seeded government schemes are displayed in a sortable table

### Requirement: Responsive layout with sidebar navigation
The admin panel SHALL use Refine's `ThemedLayoutV2` with a sidebar containing navigation links to: Dashboard, Farmers, Animals, Milk Collection, Alerts, Schemes, SHG Groups.

#### Scenario: Sidebar navigation works
- **WHEN** the admin clicks "Alerts" in the sidebar
- **THEN** the alerts page is rendered in the main content area
