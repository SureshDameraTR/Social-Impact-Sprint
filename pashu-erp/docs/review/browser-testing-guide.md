# PashuRaksha — Browser Testing Strategy (April 2026)

## TL;DR

Use **Playwright MCP** as the primary approach. It gives Claude Code direct browser tools — navigate, click, fill, screenshot, console errors, network requests — all via natural language. No scripts to write.

Fallback: **Playwright Python scripts** for repeatable regression suites.

---

## Approach Comparison (April 2026)

| Approach | Auth Reuse | Click/Fill | Screenshots | Console/Network | Context Cost | Setup |
|----------|-----------|------------|-------------|-----------------|-------------|-------|
| **Playwright MCP** | YES (cdp/extension) | YES | YES | YES | Medium | 1 command |
| **Claude --chrome** | YES (native) | YES | YES | YES | Low | Extension install |
| **Playwright Python** | YES (connect_over_cdp) | YES | YES | YES | Zero (script) | pip install |
| **Glance MCP** | YES | YES | YES (vision) | YES | Medium | npm install |
| **Agent Browser** | YES | YES | YES | Partial | 93% less | cargo/npm |
| **Raw CDP** | YES | Fragile | YES | YES | Zero | None |
| **browser-use** | YES | YES | Partial | Partial | High + LLM $ | pip install |
| **Stagehand** | YES | YES | YES | Partial | Medium + LLM $ | npm install |

---

## Option 1: Playwright MCP (RECOMMENDED)

### Why
- Official Microsoft MCP server — maintained, stable
- Claude Code gets 25+ browser tools as first-class capabilities
- Connects to your existing Chrome at :9222 (reuses cookies, sessions)
- No script writing needed — describe tests in natural language
- Captures console errors, network requests, screenshots
- Can also run arbitrary Playwright code via `browser_run_code`

### Setup

```bash
# Install Playwright MCP server (one-time)
claude mcp add playwright -- npx @playwright/mcp@latest \
  --cdp-endpoint http://localhost:9222 \
  --console-level error

# OR with the Chrome extension (reuses logged-in tabs):
# 1. Install "Playwright MCP Bridge" from Chrome Web Store
# 2. Then:
claude mcp add playwright -- npx @playwright/mcp@latest --extension
```

### Usage in Claude Code
Just tell Claude:
```
Use Playwright MCP to test the admin dashboard at localhost:3000.
Login with OTP, navigate all pages, click all nav links, try adding a farmer,
report console errors and network failures.
```

---

## Option 2: Claude --chrome (Native, Beta)

### Why
- Built into Claude Code — zero external tools
- Shares your browser's login state automatically
- Visible browser window — watch interactions in real-time
- Captures console logs, network requests

### Setup

```bash
# 1. Install "Claude in Chrome" extension from Chrome Web Store
# 2. Sign in with your Claude account
# 3. Start Claude Code with:
claude --chrome

# OR enable permanently from inside Claude Code:
/chrome  # then select "Enabled by default"
```

### WSL Note
WSL support was added in Claude Code v2.1.0. If it doesn't work:
- Ensure Chrome extension is installed on your **Windows** Chrome
- Try: `export BROWSER="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"`
- Check: https://github.com/anthropics/claude-code/issues/14367

---

## Option 3: Playwright Python Scripts (Repeatable Regression)

### Why
- Deterministic — same test, same result every time
- Full control over assertions, timing, error handling
- Can be committed to repo as regression suite
- Zero LLM cost per run

### Setup

```bash
pip install playwright requests
python -m playwright install chromium
```

### Auth Pattern (OTP flow)

```python
from playwright.sync_api import sync_playwright
import requests, subprocess, re

def get_fresh_token(phone="+919900000001"):
    """Request OTP, extract from Docker logs, verify, return JWT."""
    requests.post("http://localhost:8000/v1/auth/request-otp",
                  json={"phone": phone})
    import time; time.sleep(1)
    logs = subprocess.run(
        ["docker", "logs", "pashu-erp-api-1", "--tail", "10"],
        capture_output=True, text=True
    ).stderr
    otp = re.search(r"Code:\s*(\d{6})", logs).group(1)
    resp = requests.post("http://localhost:8000/v1/auth/verify-otp",
                         json={"phone": phone, "otp": otp})
    return resp.cookies.get("token")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]

    # Inject auth cookie
    token = get_fresh_token()
    context.add_cookies([{
        "name": "token", "value": token,
        "domain": "localhost", "path": "/",
    }])

    page = context.new_page()
    page.goto("http://localhost:3000/farmers")
    page.wait_for_load_state("networkidle")

    # Console errors
    errors = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)

    # Network failures
    page.on("requestfailed", lambda req: print(f"FAIL: {req.url}"))

    # Assertions
    assert page.title(), "Page has no title"
    assert page.locator("nav").count() > 0, "No navigation rendered"

    # Click "Add" button
    add_btn = page.locator("button:has-text('Add'), button:has-text('Create')")
    if add_btn.count() > 0:
        add_btn.first.click()
        page.wait_for_timeout(1000)
        assert page.locator("input").count() > 0, "No form appeared"

    page.screenshot(path="/tmp/farmers.png")
    print(f"PASS: Farmers page — {page.locator('tr').count()} rows")
    page.close()
```

### Save & Reuse Auth State

```python
# After first login:
context.storage_state(path="/tmp/pashu-auth-state.json")

# In subsequent tests:
context = browser.new_context(storage_state="/tmp/pashu-auth-state.json")
```

---

## Option 4: Glance MCP (Visual Testing)

### Why
- Claude sees actual screenshots (pixel-level)
- 30 tools including visual regression
- Security profiles for safe testing
- Session recording

### Setup
```bash
npm i -g glance-mcp
claude mcp add glance -- glance-mcp --allowed-origins "http://localhost:*"
```

---

## PashuRaksha-Specific Test Plan

### Apps to Test
| App | URL | Framework | Auth Cookie |
|-----|-----|-----------|-------------|
| Admin Dashboard | localhost:3000 | Next.js 14 + Refine + MUI | `token` (JWT) |
| Collection Centre | localhost:3001 | Vite + React + MUI | `token` (JWT) |
| Vet Platform | localhost:3002 | Vite + React Router + MUI | `token` (JWT) |
| Mobile (Web) | localhost:8081 | Expo React Native Web | `token` (JWT) |

### Test Users (from database)
| Role | Name | Phone | Use For |
|------|------|-------|---------|
| admin | Deepak Kumar | +919900000001 | Admin dashboard |
| farmer | Lakshmi Devi | +919900000002 | Mobile app |
| farmer | Annapurna Gowda | +919900000003 | Mobile app |
| vet | Dr. Ramesh | +919900000005 | Vet platform |
| milk_center | Manjunath Reddy | +919900000006 | Collection centre |

### Pages to Test

**Admin (13 pages):**
/, /farmers, /animals, /milk, /health, /vaccinations, /schemes, /marketplace, /income, /map, /iot, /vet/cases, /vet/alerts

**Collection (4 pages):**
/dashboard, /intake, /settlements, /enroll

**Vet (3 pages):**
/dashboard, /cases, /alerts

**Mobile (5+ screens):**
/login, /home, /animals, /health, /profile

### What to Check Per Page
1. **Renders** — not blank, no stuck spinners, body text > 30 chars
2. **Layout** — sidebar/nav visible, appbar/header present
3. **Content** — tables have rows, cards have data, headings present
4. **Interaction** — click nav links (navigate between pages), click Add/Create buttons (forms appear), fill forms
5. **CRUD** — try creating a record (enroll farmer, add animal), try editing, try deleting
6. **Console** — zero JS errors, zero unhandled exceptions
7. **Network** — zero 5xx from API, zero 401s on authenticated pages, no failed requests
8. **Performance** — page loads < 5s, no requests > 2s
9. **Responsive** — check tablet (768px) and mobile (375px) viewports

### Known Issues (from 2026-04-18 health check)
- `@mui/icons-material` missing — all 3 frontend builds fail
- Admin layout: Refine framework not rendering sidebar (SSR/hydration issue)
- OTP verify: rate limiting aggressive, tokens expire in 30 min
- SQLAlchemy connection pool leak in backend
- React Router v7 deprecation warnings in vet app

---

## Prerequisites

Before starting a test session:

```bash
# 1. Verify all containers are healthy
docker ps --format "table {{.Names}}\t{{.Status}}"

# 2. Verify API responds
curl -s http://localhost:8000/health | python3 -m json.tool

# 3. Verify dev servers are running
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000  # admin
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001  # collection
curl -s -o /dev/null -w "%{http_code}" http://localhost:3002  # vet
curl -s -o /dev/null -w "%{http_code}" http://localhost:8081  # mobile

# 4. Verify Chrome CDP is accessible
curl -s http://127.0.0.1:9222/json/version | python3 -m json.tool

# 5. Install Playwright MCP (if not already)
claude mcp add playwright -- npx @playwright/mcp@latest \
  --cdp-endpoint http://localhost:9222 --console-level error
```
