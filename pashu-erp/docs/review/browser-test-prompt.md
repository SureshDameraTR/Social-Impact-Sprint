# Browser Test Prompt

Copy everything below this line and paste into a new Claude Code session opened in the PashuRaksha repo directory.

---

## Prompt

```
You are a QA tester. Your job is to test every page of the PashuRaksha ERP app like a real user — login, click every tab, try to add/edit/delete records, check for broken UI, errors, and slowness.

Read docs/review/browser-testing-guide.md first — it has the full test plan, setup instructions, and known issues.

## Setup

1. First check prerequisites — verify Docker containers are healthy, all 4 dev servers respond (localhost:3000, 3001, 3002, 8081), API health endpoint works, and Chrome CDP is accessible at 127.0.0.1:9222.

2. Set up Playwright MCP if not already configured:
   claude mcp add playwright -- npx @playwright/mcp@latest --cdp-endpoint http://localhost:9222 --console-level error

3. If Playwright MCP is available, use it for all browser interactions. If not, write Playwright Python scripts instead (pip install playwright && python -m playwright install chromium).

## Authentication

The app uses OTP auth. To get a fresh JWT token for any user:
- POST http://localhost:8000/v1/auth/request-otp with {"phone": "<phone>"}
- Read OTP code from Docker logs: docker logs pashu-erp-api-1 --tail 10 2>&1 | grep "Code:"
- POST http://localhost:8000/v1/auth/verify-otp with {"phone": "<phone>", "otp": "<code>"}
- Extract JWT from Set-Cookie header — inject as cookie name="token" on localhost

Test users:
- Admin: +919900000001 (Deepak Kumar) — use for admin dashboard on :3000
- Milk Center: +919900000006 (Manjunath Reddy) — use for collection centre on :3001
- Vet: +919900000005 (Dr. Ramesh) — use for vet platform on :3002
- Farmer: +919900000002 (Lakshmi Devi) — use for mobile app on :8081

## What to Test

For EACH of the 4 apps, login as the appropriate role user and test EVERY page:

### Per Page Checklist:
- [ ] Page renders (not blank, no stuck spinners)
- [ ] Sidebar/nav visible and clickable
- [ ] Header/appbar present
- [ ] Tables have data rows (not empty)
- [ ] Cards show real content
- [ ] All nav links work (click each one, verify navigation)
- [ ] "Add"/"Create" buttons open forms
- [ ] Form fields are fillable
- [ ] Submit works (or shows proper validation errors)
- [ ] No JavaScript console errors
- [ ] No network 4xx/5xx errors to API
- [ ] Page loads in < 5 seconds
- [ ] Take screenshot of every page

### CRUD Operations to Try:
- Admin /farmers: Try adding a new farmer
- Admin /animals: Try adding a new animal
- Collection /enroll: Try enrolling a farmer
- Collection /intake: Try recording milk intake
- Vet /cases: Try creating a case

### Responsive Testing:
- Test admin dashboard at 768px (tablet) and 375px (mobile) widths
- Check if nav collapses to hamburger menu

## Reporting

After testing all apps, write a report to docs/review/browser-test-results-YYYY-MM-DD.md with:

1. **Summary table**: App | Pages Tested | Pass | Fail | Issues
2. **Per-page results**: status, load time, what rendered, what was broken
3. **CRUD results**: what worked, what failed, error messages
4. **Console errors**: unique list across all pages
5. **Network errors**: any API failures
6. **Screenshots**: saved to e2e/screenshots/
7. **Critical bugs found**: with steps to reproduce
8. **Comparison with previous health check**: compare against docs/review/health-check-2026-04-18.md

Also monitor backend logs during testing:
docker logs pashu-erp-api-1 --tail 500 2>&1 | grep -iE "error|exception|500|traceback"

Report any backend errors correlated with your test actions.
```
