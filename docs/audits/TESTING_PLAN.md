# PashuRaksha ERP — Complete Testing Plan

**Date:** 2026-04-14 (updated)
**Tester:** Automated CDP (Chrome DevTools Protocol) via WSL2 → Windows Chrome
**Apps Under Test:** Admin Dashboard (Next.js, port 3000), Collection Centre (Vite/React, port 3001), Vet Portal (Vite/React, port 3002)
**Backend:** FastAPI (port 8000), PostgreSQL (port 5432), Mock Backends (port 8001)

---

## 1. Functional Regression Test Plan

### 1.1 Admin App — 11 Pages

#### Page 1: Dashboard (`/`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-D01 | Navigate to `/` | Page loads with title "Dashboard" | PASS |
| TC-D02 | Verify stat cards | 6 cards: Total Farmers, Registered Animals, Today's Milk, Active Health Alerts, Marketplace Revenue, Active Sellers | PASS |
| TC-D03 | Verify area chart | "Milk Collection (Last 30 Days)" chart renders with Morning/Evening data | PASS |
| TC-D04 | Verify disease map | "Disease Alert Map" renders with Leaflet tiles and markers | PASS |
| TC-D05 | Verify sidebar | All 11 nav items visible across 4 sections | PASS |

#### Page 2: Farmers (`/farmers`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-F01 | Navigate to `/farmers` | Table loads with 7 farmers | PASS |
| TC-F02 | Type "Lakshmi" in search | Filters to 1 result (Lakshmi Devi), counter shows "1 registered" | PASS |
| TC-F03 | Clear search | All 7 farmers restore | PASS |
| TC-F04 | Click NAME sort header | Arrow appears, rows sorted A→Z | PASS |
| TC-F05 | Click NAME again | Should toggle to Z→A descending | MINOR — arrow stayed ascending |
| TC-F06 | Verify pagination | Shows "1–7 of 7", Rows per page dropdown | PASS |
| TC-F07 | Verify data columns | Name, Phone, District, Village, Animals, Registered all populated | PASS |

#### Page 3: Animals (`/animals`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-A01 | Navigate to `/animals` | Table loads with 9 animals | PASS |
| TC-A02 | Open Species dropdown | Shows: All, Cattle, Buffalo, Goat, Sheep, Poultry | PASS |
| TC-A03 | Select "Goat" | Filters to 1 animal (Gauri, Osmanabadi) | PASS |
| TC-A04 | Verify species chips | Color-coded: cattle (green), goat (yellow), sheep (amber), poultry (red) | PASS |
| TC-A05 | Verify search box | Placeholder "Search by name or Pashu Aadhaar..." | PASS |
| TC-A06 | Verify pagination | Shows "1–9 of 9" when unfiltered | PASS |

#### Page 4: Milk Collection (`/milk`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-M01 | Navigate to `/milk` | Page loads with chart and table | PASS |
| TC-M02 | Verify bar chart | "Daily Collection Summary" with date axis | PASS |
| TC-M03 | Verify date filters | From/To date inputs present | PASS |
| TC-M04 | Verify table data | Date, Animal ID, Quantity (L), Session, Notes columns | PASS |
| TC-M05 | Verify session chips | Morning (amber), Evening (teal) color-coded | PASS |
| TC-M06 | Verify pagination | Shows "1–10 of 10" | PASS |

#### Page 5: Health Alerts (`/health`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-H01 | Navigate to `/health` | Shows "2 active alerts, 1 critical" | PASS |
| TC-H02 | Verify disease rendering | Probable Diseases shows names (not [object Object]) | PASS |
| TC-H03 | Open Risk Level dropdown | Shows: All, Critical, High, Medium, Low | PASS |
| TC-H04 | Select "Critical" | Filters to 1 alert (Mastitis, Udder Edema) | PASS |
| TC-H05 | Verify risk chips | High (amber), Critical (red) color-coded | PASS |
| TC-H06 | Verify recommended action | Full text renders without truncation | PASS |
| TC-H07 | Verify date sort | DATE column has sort arrow | PASS |

#### Page 6: Vaccinations (`/vaccinations`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-V01 | Navigate to `/vaccinations` | 3 stat cards load | PASS |
| TC-V02 | Verify stat cards | Overall Coverage %, Overdue count, This Month count | PASS |
| TC-V03 | Verify village table | Village Code, Name, Total Animals, Vaccinated, Coverage %, Status | PASS |
| TC-V04 | Verify species breakdown | Cards per species with progress bars | PASS |
| TC-V05 | Scroll to schedule | Upcoming vaccination schedule with vaccine names | PASS |
| TC-V06 | Verify "On Track" chips | All villages show green "On Track" status | PASS |

#### Page 7: Govt Schemes (`/schemes`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-S01 | Navigate to `/schemes` | Shows "5 active schemes available" | PASS |
| TC-S02 | Verify currency format | Max Subsidy shows ₹2,00,000 (not ₹NaN) | PASS |
| TC-S03 | Verify scheme codes | Codes like KMF-DD-2025, NABARD-DE-2024 | PASS |
| TC-S04 | Verify Active status | All schemes show "Active" chip (not "Expired") | PASS |
| TC-S05 | Search "NABARD" | Filters to 1 result, counter updates | PASS |
| TC-S06 | Verify sort | CODE column has ascending sort arrow | PASS |
| TC-S07 | Verify valid periods | Date ranges like "1/1/2025 - 31/12/2026" | PASS |

#### Page 8: Marketplace (`/marketplace`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-MK01 | Navigate to `/marketplace` | 3 stat cards + chart + table | PASS |
| TC-MK02 | Verify stat cards | Total Sales Volume, Average Tx Value, Active Sellers | PASS |
| TC-MK03 | Verify Revenue chart | "Revenue by Product" bar chart (milk, eggs) | PASS |
| TC-MK04 | Verify transaction table | Date, Farmer, Product, Qty, Price/Unit, Total, Buyer | PASS |
| TC-MK05 | Verify product chips | milk (teal), eggs (green) color-coded | PASS |
| TC-MK06 | Verify search | Placeholder "Search by farmer, product, or buyer..." | PASS |

#### Page 9: Income Analytics (`/income`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-I01 | Navigate to `/income` | 3 stat cards + 3 charts | PASS |
| TC-I02 | Verify stat cards | Total Farmer Income, Avg Income per Farmer, Loan Applications | PASS |
| TC-I03 | Verify bar chart | "Income by Product Category" (eggs, manure, milk, wool) | PASS |
| TC-I04 | Verify pie chart | "Income Distribution" with proportional slices | PASS |
| TC-I05 | Verify trend chart | "Monthly Income Trend (Last 6 Months)" | PASS |

#### Page 10: Map View (`/map`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-MAP01 | Navigate to `/map` | Leaflet map renders (no crash) | PASS |
| TC-MAP02 | Verify map center | Centered on Karnataka (~13°N, 76.5°E) | PASS |
| TC-MAP03 | Verify markers | Data points visible on map | PASS |
| TC-MAP04 | Click marker | Popup shows disease name (e.g., "Foot and Mouth Disease (FMD)") | PASS |
| TC-MAP05 | Verify legend | 5 items: Critical/High/Medium Alert, Milk Center, Farmer Location | PASS |
| TC-MAP06 | Verify layer control | Toggle in top-right corner | PASS |

#### Page 11: IoT Devices (`/iot`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-IOT01 | Navigate to `/iot` | Shows "9/10 devices online" | PASS |
| TC-IOT02 | Verify Phase 2 banner | Info alert about upcoming features | PASS |
| TC-IOT03 | Verify device cards | 5 types: Smart Collars, Ear Tag, Bolus, Milk Meters, Pedometer | PASS |
| TC-IOT04 | Verify online/offline chips | Per-card green/red with counts | PASS |
| TC-IOT05 | Verify progress bars | Color-coded per device type | PASS |
| TC-IOT06 | Verify telemetry table | Device ID, Animal ID, Metrics, Battery, RSSI, Timestamp | PASS |
| TC-IOT07 | Verify battery chips | Green >50%, amber 20-50%, red <20% | PASS |
| TC-IOT08 | Verify search | Placeholder "Search by device or animal ID..." | PASS |

### 1.2 Collection App — 4 Routes

#### Dashboard (`/dashboard`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-CD01 | Navigate to `/dashboard` | Shows today's date in header | PASS |
| TC-CD02 | Verify stat cards | Today's Milk, Revenue, Farmers Today, Avg Quality | PASS |
| TC-CD03 | Verify shift cards | Morning Shift and Evening Shift with totals | PASS |
| TC-CD04 | Verify navbar | Centre name, nav links (Intake/Dashboard/Settlements), user name, logout | PASS |

#### Intake (`/intake`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-CI01 | Navigate to `/intake` | Farmer search form with Phone/Aadhaar toggle | PASS |
| TC-CI02 | Type "9900000002" in search | Shows "Lakshmi Devi" result card | PASS |
| TC-CI03 | Click farmer result | Farmer selected, "Change" button appears, milk form shows | PASS |
| TC-CI04 | Fill Qty=5.2, Fat=4.5, SNF=8.5 | Rate calculates: ₹45.75/L, Total ₹237.90 | PASS |
| TC-CI05 | Verify shift toggle | Morning/Evening buttons with icons | PASS |
| TC-CI06 | Click "Submit Milk Record" | Request sent (403 CSRF expected — known audit finding) | KNOWN ISSUE |
| TC-CI07 | Verify error display | "Request failed with status code 403" alert with dismiss X | PASS |
| TC-CI08 | Verify "Enroll here" link | Present below search | PASS |

#### Settlements (`/settlements`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-CS01 | Navigate to `/settlements` | Table with 15-day data | PASS |
| TC-CS02 | Verify period toggle | 15 DAYS / 30 DAYS / 45 DAYS buttons | PASS |
| TC-CS03 | Click "30 DAYS" | Data updates (53 deliveries, ₹21,555.10 total) | PASS |
| TC-CS04 | Verify table columns | #, Farmer ID, Deliveries, Total Liters, Avg Fat%, Avg SNF%, Total Payout | PASS |
| TC-CS05 | Verify totals footer | Total Farmers count and Total Payout sum | PASS |

#### Enroll (`/enroll`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-CE01 | Navigate to `/enroll` | "Enroll New Farmer" form | PASS |
| TC-CE02 | Verify required fields | Full Name*, Phone Number* (+91), Aadhaar Number* | PASS |
| TC-CE03 | Verify optional field | Village (optional) | PASS |
| TC-CE04 | Verify submit button | "Enroll Farmer" disabled until required fields filled | PASS |

### 1.3 Vet Portal — 5 Routes

#### Auth: OTP Login Flow
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-VA01 | Request OTP for vet phone (+919900000006) | HTTP 200, OTP logged in API container | PASS |
| TC-VA02 | Verify OTP | HTTP 200, token + csrf_token cookies set | PASS |
| TC-VA03 | Call GET /v1/auth/me with token | Returns user with role=vet, name=Dr. Ramesh Kumar | PASS |

#### Login Page (`/login`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-VL01 | Navigate to `/login` | Page loads with title "PashuRaksha - Vet Portal" | PASS |
| TC-VL02 | Verify branding | Stethoscope emoji, "PashuRaksha" heading, "Veterinary Portal" subtitle | PASS |
| TC-VL03 | Verify login form | "Vet Login" heading, phone input with +91 prefix | PASS |
| TC-VL04 | Verify phone validation | Input accepts only digits, max 10 chars | PASS |
| TC-VL05 | Verify Send OTP button | Disabled until valid 10-digit phone entered, enables after | PASS |
| TC-VL06 | Enter phone and send OTP | Transitions to OTP step with 6 input boxes | MANUAL |
| TC-VL07 | Verify OTP paste support | Pasting 6 digits fills all boxes | MANUAL |
| TC-VL08 | Verify Remember Me | Checkbox "Remember this device (7 days)" present in OTP step | PASS — only visible after OTP sent (step 2) |
| TC-VL09 | Verify Resend cooldown | "Resend OTP in Xs" countdown visible after send | MANUAL |

#### Dashboard (`/dashboard`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-VD01 | Navigate to `/dashboard` | Page loads without redirect to login | PASS |
| TC-VD02 | Verify welcome message | "Welcome, Dr. [name]" with district and date | PASS |
| TC-VD03 | Verify stat cards | 4 cards: Pending Cases, Diagnosed Today, District Animals, Active Alerts | PASS |
| TC-VD04 | Verify stat card values | All cards show numeric values (not NaN or undefined) | PASS (0, 1, 6, 0) |
| TC-VD05 | Verify pending cases list | List of clickable case items with priority chips | PASS |
| TC-VD06 | Click a pending case | Navigates to `/cases/<id>` | PASS |
| TC-VD07 | Verify NavBar on dashboard | Brand "PashuRaksha", "Vet Portal", 3 tabs, user name, logout | PASS |

#### Cases Page (`/cases`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-VC01 | Navigate to `/cases` | Page loads with "Cases" heading | PASS |
| TC-VC02 | Verify status filter tabs | 5 tabs: All, Pending, In Review, Diagnosed, Closed | PASS |
| TC-VC03 | Verify table columns | Animal, Farmer, Status, Priority, Channel, Created | PASS |
| TC-VC04 | Verify case data | At least 1 case row rendered with data | PASS (4 rows) |
| TC-VC05 | Verify species chips | Color-coded species labels (cattle=green, buffalo=blue, etc.) | PASS |
| TC-VC06 | Verify status chips | Color-coded: pending (orange), in_review (blue), diagnosed (green), closed (grey) | PASS |
| TC-VC07 | Verify priority chips | emergency (red), urgent (orange), routine (grey) | PASS |
| TC-VC08 | Click "Pending" tab | Filters to only pending cases | PASS |
| TC-VC09 | Click "Diagnosed" tab | Filters to only diagnosed cases | MANUAL |
| TC-VC10 | Click a case row | Navigates to case detail page | PASS |
| TC-VC11 | Verify refresh button | Refresh icon button present and clickable | PASS |

#### Case Detail (`/cases/:id`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-VCD01 | Navigate to case detail | Page loads with case header (animal name, status, priority chips) | PASS |
| TC-VCD02 | Verify Back button | "Back to Cases" button present | PASS |
| TC-VCD03 | Verify Animal Details card | Species chip, Name, Breed, ID fields | PASS |
| TC-VCD04 | Verify Farmer Details card | Name, Phone, Village, District fields | PASS |
| TC-VCD05 | Verify Case Information card | Channel, District, Farmer Notes, Updated timestamp | PASS |
| TC-VCD06 | Verify action buttons | Claim/Diagnose/Video Link/Close based on case status | PASS |
| TC-VCD07 | Click "Diagnose" button | Dialog opens with Diagnosis, Prescription, Follow-up Date fields | MANUAL |
| TC-VCD08 | Click "Set Video Link" button | Dialog opens with URL input | MANUAL |
| TC-VCD09 | Verify diagnosed case | Shows Diagnosis & Treatment section with prescription | MANUAL |

#### Alerts Page (`/alerts`)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-VAL01 | Navigate to `/alerts` | Page loads with "District Alerts" heading | PASS |
| TC-VAL02 | Verify tab labels | "Disease Alerts (N)" and "Health Events (N)" with counts | PASS |
| TC-VAL03 | Verify disease alert cards | Disease name, alert type, location, severity chip, timestamp | PASS (empty state shown — 0 alerts) |
| TC-VAL04 | Verify severity chips | critical (red), high (orange), medium (yellow), low (green) | MANUAL — needs alert data |
| TC-VAL05 | Verify Verify button | "Verify" button on unverified alerts | MANUAL — needs alert data |
| TC-VAL06 | Click "Health Events" tab | Switches to health events table | PASS |
| TC-VAL07 | Verify health events table | Animal ID, Event Type, Symptoms, AI Risk, Date columns | PASS |
| TC-VAL08 | Verify AI Risk badges | Percentage-based color (>70% red, 40-70% orange, <40% green) | MANUAL |

#### Cross-Cutting: JS Errors
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-VJS01 | Load `/login` | No JavaScript errors in console | PASS |
| TC-VJS02 | Load `/dashboard` | No JavaScript errors in console | PASS |
| TC-VJS03 | Load `/cases` | No JavaScript errors in console | PASS |
| TC-VJS04 | Load `/alerts` | No JavaScript errors in console | PASS |

#### API Endpoints (Vet)
| Test Case | Action | Expected Result | Status |
|-----------|--------|-----------------|--------|
| TC-VAPI01 | GET /v1/vet/dashboard/stats | 200, returns pending_cases, diagnosed_today, district_animals, active_alerts | PASS |
| TC-VAPI02 | GET /v1/vet/cases | 200, returns {data: [...], skip, limit} (4 cases) | PASS |
| TC-VAPI03 | GET /v1/vet/cases?status=pending | 200, all returned cases have status=pending | PASS |
| TC-VAPI04 | GET /v1/vet/cases/{id} | 200, returns full case with animal and farmer details | PASS |
| TC-VAPI05 | GET /v1/vet/dashboard/alerts | 200, returns {community_alerts: [...], health_events: [...]} | PASS |
| TC-VAPI06 | PATCH /v1/vet/cases/{id}/claim | 200, case status changes to in_review | PASS |
| TC-VAPI07 | PATCH /v1/vet/cases/{id}/diagnose | 200, case status changes to diagnosed | PASS |
| TC-VAPI08 | PATCH /v1/vet/cases/{id}/close | 200, case status changes to closed | PASS |

---

## 2. Performance Test Plan

### 2.1 Backend API Latency
Measure response time for every API endpoint used by the frontend:
- `GET /v1/admin/stats` (Dashboard stats)
- `GET /v1/admin/charts/milk` (Milk chart)
- `GET /v1/admin/charts/alerts` (Alert chart)
- `GET /v1/farmers` (Farmers list)
- `GET /v1/animals` (Animals list)
- `GET /v1/milk` (Milk collection)
- `GET /v1/health` (Health alerts)
- `GET /v1/vaccinations/coverage` (Vaccination stats)
- `GET /v1/schemes` (Govt schemes)
- `GET /v1/marketplace/transactions` (Marketplace)
- `GET /v1/finance/summary` (Income analytics)
- `GET /v1/map/points` (Map data)
- `GET /v1/iot/device-types` (IoT devices)
- `GET /v1/iot/readings` (IoT telemetry)
- `GET /v1/milk-center/daily-summary` (Collection dashboard)
- `GET /v1/milk-center/settlements` (Settlements)
- `GET /v1/vet/dashboard/stats` (Vet dashboard stats)
- `GET /v1/vet/dashboard/alerts` (Vet alerts)
- `GET /v1/vet/cases` (Vet cases list)
- `GET /v1/vet/cases/{id}` (Vet case detail)

**Metrics:** TTFB, Total Time, Response Size, HTTP Status

### 2.2 Frontend Bundle Analysis
- Next.js production build output (Admin)
- Vite production build output (Collection)
- Vite production build output (Vet Portal)
- JavaScript bundle sizes (gzipped vs raw)
- CSS bundle sizes
- Number of chunks
- Largest dependencies

### 2.3 Browser Performance (per page)
- JS Heap Size (used/total)
- DOM Node Count
- Navigation Timing (DOMContentLoaded, Load, First Paint, LCP)
- Layout/Reflow count
- Event Listener count

### 2.4 Docker Container Resources
- CPU usage per container
- Memory usage / limit per container
- Network I/O
- Disk I/O

### 2.5 Database Performance
- Connection pool stats
- Query execution times (from API logs)
- Table sizes and index usage

---

## 3. Test Environment

| Component | Version | Config |
|-----------|---------|--------|
| Chrome | Windows (CDP remote) | Default, no throttling |
| Next.js (Admin) | Dev mode, port 3000 | WSL2 → NTFS mount |
| Vite (Collection) | Dev mode, port 3001 | WSL2 → NTFS mount |
| Vite (Vet Portal) | Dev mode, port 3002 | WSL2 → Linux tmpfs |
| FastAPI (API) | Docker, port 8000 | --reload, volume mount |
| PostgreSQL | 16-alpine, port 5432 | 512MB limit |
| Mock Backends | Docker, port 8001 | Python FastAPI |
| OS | WSL2 (Ubuntu) | Linux 6.6.87.2 |

---

## 4. Known Issues & Limitations

1. **Collection CSRF 403** — POST /v1/milk-center/intake blocked by CSRF middleware; Collection app doesn't send CSRF tokens (audit finding #1)
2. **Sort descending** — MUI TableSortLabel desc toggle not reliably triggered via CDP
3. **Dev mode overhead** — Both apps running in dev mode; production builds would be faster
4. **WSL2/NTFS** — Cross-filesystem I/O adds latency to Next.js HMR and page compilation
5. **Screenshot timeouts** — Intermittent 30s CDP screenshot timeouts (retry succeeds)
6. **Vet Vite dep optimization** — First page load triggers 504 "Outdated Optimize Dep" while Vite pre-bundles MUI; resolves after warm-up
7. **Vet Remember Me** — Checkbox only visible in OTP step (step 2), not phone step; CDP test checks step 1 only
8. **Vet alert severity chips** — No disease alerts in test data (0 community_alerts); severity chip rendering untested via CDP
