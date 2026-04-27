# Phase 2: Browser UI Testing — Prompt for Claude Code

> **Context**: Phase 1 (Backend API Testing) is complete. 387/391 tests pass against real API.
> Read `pashu-erp/testing-handover-phase1.md` for full context.
> 
> **How to use**: Clear context, then paste everything below the line into Claude Code.
> **Working directory**: `/home/sdamera/workbench/Social-Impact-Sprint`

---

## PROMPT START

Read `pashu-erp/testing-handover-phase1.md` first to understand what was completed in Phase 1.

You are continuing comprehensive testing of PashuRaksha ERP. Phase 1 (backend API testing) is done — 387 tests passing across 29 routers. Now you're doing Phase 2: Browser UI Testing.

### CRITICAL RULES

1. **NO HALLUCINATIONS**: Never claim a page renders correctly without actually navigating to it in a real browser and seeing the result. If something doesn't work, report it honestly.
2. **REAL BROWSER ONLY**: Use Playwright in headed mode (`--headed`) or Chrome CDP. Headless tests miss real rendering issues (fonts, layout, CSS). If headed mode doesn't work in WSL, ASK ME.
3. **SCREENSHOTS AS EVIDENCE**: Take a screenshot of every page tested. Save to `pashu-erp/e2e/screenshots/comprehensive/`.
4. **CONTEXT HANDOVER**: Before context fills up, write state to `pashu-erp/testing-handover-phase2.md`.
5. **ASK, DON'T ASSUME**: If frontends won't start, ports don't respond, or browsers won't launch — ask me.

### STEP 0: ENVIRONMENT SETUP

```bash
# Start all frontends
cd pashu-erp && docker compose --profile frontend up -d

# Wait for healthy
sleep 30

# Verify all ports respond
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000  # Admin → expect 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001  # Collection → expect 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:3002  # Vet → expect 200

# Install Playwright if needed
cd pashu-erp && npx playwright install chromium
```

If frontends fail to start, check docker logs:
```bash
docker compose --profile frontend logs admin --tail 30
docker compose --profile frontend logs collection --tail 30
docker compose --profile frontend logs vet --tail 30
```

**If any frontend fails to start, STOP and ask me. Do not skip it.**

### STEP 1: AUTH MECHANISM (Important for all UI testing)

All 3 UIs use OTP login. The OTP is **randomly generated** — NOT "123456".

**For Playwright tests**, you have two options:
- **Option A**: Intercept the OTP from docker logs after the UI triggers `request-otp`
- **Option B**: Use API to pre-authenticate and inject the token cookie/header before navigating

Test accounts:
| Role | Phone | UI |
|------|-------|-----|
| admin | +919900000001 | Admin (localhost:3000) |
| farmer | +919900000002 | N/A (farmers blocked from web) |
| vet | +919900000005 | Vet (localhost:3002) |

For Collection Centre (localhost:3001), you need a milk_center user. Check the database:
```bash
docker exec pashu-erp-db-1 psql -U pashu -d pashuraksha -c "SELECT phone, name, role FROM users WHERE role = 'milk_center';"
```

**OTP extraction from docker logs** (use after login form submits):
```bash
docker logs pashu-erp-api-1 --tail 15 2>&1 | grep "Code:" | tail -1 | grep -oP '\d{6}'
```

### STEP 2: ADMIN DASHBOARD (localhost:3000) — 16 pages

Login as admin (phone: +919900000001). Test EVERY page:

| # | Route | Page | What to Verify |
|---|-------|------|----------------|
| 1 | /login | Login | Phone input works, OTP field appears, login completes, redirect to / |
| 2 | / | Dashboard | 4+ stat cards with real numbers (not 0/NaN), Recharts area chart renders, Leaflet GIS map loads with markers |
| 3 | /farmers | Farmers | Data table loads with rows, search input filters results, pagination buttons work |
| 4 | /animals | Animals | Table loads, species dropdown filter works, RiskBadge chips show colors |
| 5 | /health | Health | Risk level filter dropdown works, health events list loads |
| 6 | /milk | Milk | Collection data renders, daily summary visible |
| 7 | /vaccinations | Vaccinations | Coverage stat cards render, progress bars show percentages |
| 8 | /schemes | Schemes | Government schemes list loads with items |
| 9 | /marketplace | Marketplace | Listings render in table |
| 10 | /income | Income | Income analytics render (charts/numbers) |
| 11 | /map | Map | Full-page Leaflet map loads, zoom controls work, markers visible |
| 12 | /iot | IoT | Device list renders with status indicators |
| 13 | /vet | Vet Overview | Vet dashboard stats render |
| 14 | /vet/cases | Vet Cases | Case list table loads |
| 15 | /vet/cases/:id | Case Detail | Pick first case from list, navigate, details render |
| 16 | /vet/alerts | Vet Alerts | Alert list renders |

**For EACH page**:
- [ ] Page loads without JS console errors
- [ ] No stuck "loading..." spinners (wait up to 10 seconds)
- [ ] No blank white screens
- [ ] Data tables show actual data (not empty states when seed data exists)
- [ ] Take screenshot at 1920x1080
- [ ] Take screenshot at 768x1024 (tablet) for responsive check
- [ ] Record page load time
- [ ] Check sidebar navigation: click link → URL changes → correct page loads

### STEP 3: COLLECTION CENTRE (localhost:3001) — 6 pages

Login as milk_center user. Test:

| # | Route | What to Verify |
|---|-------|----------------|
| 1 | /login | OTP login flow works |
| 2 | /dashboard | Daily intake summary, shift stats render |
| 3 | /intake | Farmer search, enter qty/FAT/SNF, rate preview calculates, submit works |
| 4 | /intake/receipt/:id | Receipt renders after intake, looks printable |
| 5 | /enroll | Farmer enrollment form, fields validate, submit creates farmer |
| 6 | /settlements | Payment settlement list renders |

**CRITICAL FLOW to test end-to-end**:
1. Login → Dashboard
2. Navigate to Intake
3. Search for a farmer
4. Enter milk: qty=5.5L, FAT=4.2, SNF=8.5
5. Verify rate preview shows a number (not NaN)
6. Submit
7. Verify redirect to receipt page
8. Verify receipt shows correct data

### STEP 4: VET DASHBOARD (localhost:3002) — 5 pages

Login as vet (phone: +919900000005). Test:

| # | Route | What to Verify |
|---|-------|----------------|
| 1 | /login | OTP login flow works |
| 2 | /dashboard | Welcome message, stats cards, pending cases count |
| 3 | /cases | Case list loads, tabs (All/My Cases) switch correctly |
| 4 | /cases/:id | Case details render, claim/diagnose/close buttons visible |
| 5 | /alerts | Alert list with map markers |

**CRITICAL FLOW**:
1. Login → Dashboard
2. Navigate to Cases
3. Click into a case
4. Claim the case
5. Verify status changes

### STEP 5: CROSS-CUTTING CHECKS

After testing all 3 apps:

1. **Auth boundary**: Farmer (phone +919900000002) should be BLOCKED from admin login (web portal blocks farmers)
2. **Session expiry**: After 30 min token expiry, verify redirect to login
3. **Console errors**: Check browser console on every page — report any JS errors
4. **Responsive**: Test critical pages at 1920px, 1366px, 1024px, 768px widths
5. **Fonts**: Verify no missing glyphs, especially if any Kannada text appears

### AGENTS TO USE

| Agent | Purpose |
|-------|---------|
| `browser-ui-tester` | Write and run Playwright specs for all 3 apps |
| `e2e-tester` | End-to-end user journeys (login→action→verify) |

You can also use the `playwriter` skill for Chrome CDP browser control if Playwright headed mode doesn't work.

### OUTPUT

Write Playwright test specs to `pashu-erp/e2e/comprehensive/`.
Save screenshots to `pashu-erp/e2e/screenshots/comprehensive/`.

After all testing, create `pashu-erp/testing-handover-phase2.md` with:
- Per-page results table (page, status, load time, screenshot path, issues)
- Console errors found
- Visual/UX issues found
- Responsive issues found
- Anything that needs fixing before production

### WHAT SUCCESS LOOKS LIKE

- [ ] All 27 pages tested in real browser with screenshots
- [ ] All 3 login flows tested
- [ ] Milk intake end-to-end flow tested
- [ ] Vet case workflow tested
- [ ] No stuck loading states
- [ ] No JS console errors (or all documented)
- [ ] Responsive checks at 4 widths on critical pages
- [ ] Auth boundary test (farmer blocked from admin)
- [ ] Handover document written

## PROMPT END
