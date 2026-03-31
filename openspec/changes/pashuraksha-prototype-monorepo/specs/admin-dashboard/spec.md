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

### Requirement: IoT device management page
The admin panel SHALL display an IoT device management page listing all registered devices with status, firmware version, and last sync time.

#### Scenario: Admin views IoT device list
- **WHEN** the admin navigates to the IoT Devices page
- **THEN** a table displays all devices with columns: device ID, type, assigned farmer, village, status (online/offline badge), firmware version, and last sync timestamp

#### Scenario: Admin filters offline devices
- **WHEN** the admin filters by status "offline"
- **THEN** only devices that have not synced within the expected interval are shown

### Requirement: Disease surveillance map
The admin panel SHALL display a disease surveillance map showing outbreak report markers and hotspot circles on GIS (react-leaflet with OpenStreetMap tiles).

#### Scenario: Map shows outbreak report markers
- **WHEN** the admin navigates to the Disease Surveillance page
- **THEN** the map displays red markers for active outbreak reports with popup details (affected animals, probable diseases, status)

#### Scenario: Map shows hotspot circles
- **WHEN** active hotspots exist
- **THEN** semi-transparent red circles overlay the map showing the affected radius area for each hotspot

### Requirement: Income analytics page
The admin panel SHALL display an income analytics page with farmer income distribution chart, revenue breakdown by product category, and trend charts.

#### Scenario: Admin views income distribution
- **WHEN** the admin navigates to the Income Analytics page
- **THEN** a bar chart shows farmer count by income range (0-5K, 5K-10K, 10K-20K, 20K+) and a pie chart shows revenue by product type (milk, eggs, goat milk, wool, manure)

#### Scenario: Admin views income trend
- **WHEN** the admin selects a 6-month view
- **THEN** a line chart shows monthly total farmer income over the selected period

### Requirement: Vaccination coverage page
The admin panel SHALL display a vaccination coverage page with a heatmap by village and overdue alerts list.

#### Scenario: Admin views vaccination heatmap
- **WHEN** the admin navigates to the Vaccination Coverage page
- **THEN** a color-coded table or map shows vaccination coverage percentage per village (green >= 80%, yellow 50-79%, red < 50%)

#### Scenario: Admin views overdue vaccination alerts
- **WHEN** overdue vaccinations exist
- **THEN** a list below the heatmap shows animals with overdue vaccinations including farmer name, animal name, vaccine name, and days overdue

### Requirement: Impact dashboard
The admin panel SHALL display a high-level impact dashboard with platform metrics suitable for government reporting.

#### Scenario: Admin views impact dashboard
- **WHEN** the admin navigates to the Impact Dashboard page
- **THEN** large metric cards display: total farmers registered, total animals tracked, total farmer income generated, scheme applications processed, SHG groups active, and villages covered

#### Scenario: Impact metrics are exportable
- **WHEN** the admin clicks "Export Report"
- **THEN** a PDF summary of impact metrics is generated for government stakeholder sharing
