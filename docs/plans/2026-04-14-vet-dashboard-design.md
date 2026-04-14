# Vet Dashboard & Video Consultation — Design Document

**Date:** 2026-04-14
**Status:** Approved
**Scope:** API + Admin Dashboard + Mobile

---

## Summary

Add a veterinary dashboard to the existing admin portal and a video consultation flow connecting farmers to district vets. Vets get a hybrid visibility model: passive awareness of all health events/alerts in their district, plus an active caseload of consultations referred to them via photo submissions.

Video consultation uses external link-out (WhatsApp/JioMeet) — the vet pastes a call URL into the case, farmer taps to join. Zero video infrastructure to build.

---

## 1. Data Model

### New Table: `vet_consultations`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID, PK | |
| `animal_id` | UUID, FK → animals | |
| `farmer_id` | UUID, FK → users | Who requested help |
| `vet_id` | UUID, FK → users, nullable | Assigned vet (null = unassigned) |
| `status` | Enum: pending / in_review / diagnosed / closed | |
| `priority` | Enum: routine / urgent / emergency | |
| `channel` | Enum: photo / walk_in / referral | |
| `farmer_notes` | Text | "My cow is not eating" |
| `photo_urls` | JSONB (list of strings) | Uploaded photos from mobile |
| `diagnosis` | Text, nullable | Vet's findings |
| `prescription` | Text, nullable | Treatment plan |
| `follow_up_date` | Date, nullable | |
| `video_call_url` | String(500), nullable | WhatsApp/JioMeet link |
| `district` | String(100) | Denormalized from farmer for fast queries |
| `created_at` | DateTime | |
| `updated_at` | DateTime | |

### Design Decisions
- District denormalized so vet dashboard queries don't join through farmer → user → district
- `photo_urls` is JSONB list (not FK to files table) for simplicity — same pattern as insurance claims
- `video_call_url` is a plain string — vet pastes any video call link
- `channel` tracks how the case originated (photo upload, walk-in at clinic, admin referral)

---

## 2. API Changes

### New Middleware: `require_vet_or_admin()`

File: `packages/api/app/middleware/auth.py`

```python
async def require_vet_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("vet", "admin"):
        raise HTTPException(403, "Vet or admin access required")
    return current_user
```

### New Router: `routers/vet.py` (prefix: `/v1/vet`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/cases` | vet/admin | List cases in vet's district. Filters: status, priority, skip, limit |
| GET | `/cases/{id}` | vet/admin | Case detail with animal info, photos, health history |
| PATCH | `/cases/{id}/claim` | vet | Set vet_id = current user, status = in_review |
| PATCH | `/cases/{id}/diagnose` | vet/admin | Set diagnosis, prescription, follow_up_date, status = diagnosed |
| PATCH | `/cases/{id}/video-link` | vet | Set video_call_url |
| PATCH | `/cases/{id}/close` | vet/admin | Set status = closed |
| GET | `/dashboard/stats` | vet/admin | Stats: pending_cases, diagnosed_today, district_animals, active_alerts |
| GET | `/dashboard/alerts` | vet/admin | District health alerts + community disease reports |
| GET | `/my-cases` | farmer | Farmer's own consultation cases with status/diagnosis/video link |

### Modified Existing Endpoints

| File | Endpoint | Change |
|------|----------|--------|
| `routers/health.py` | `POST /v1/health/log` | When photo_urls present, auto-create VetConsultation (status=pending, channel=photo) |
| `routers/health.py` | `GET /v1/health` | If role=vet, show all events in vet's district (not just own animals) |
| `routers/alerts.py` | `PATCH /v1/alerts/{id}/verify` | Allow role=vet in addition to admin |
| `routers/animals.py` | `GET /v1/animals` | If role=vet, show all animals in vet's district |
| `middleware/auth.py` | — | Add `require_vet_or_admin()` dependency |

---

## 3. Admin Dashboard — Vet Pages

### Sidebar (role-based navigation)

File: `packages/admin/src/components/AdminSidebar.tsx`

```
Vet sees:                    Admin sees (unchanged + new):
─────────────────            ─────────────────────────────
Vet Dashboard                Everything existing
  My Cases                   + Vet section visible too
  District Health Map
  District Alerts
Lookup
  Animal Search
  Vaccination Coverage
  Ethno-Vet Reference
```

Logic: sidebar reads user role from auth provider, renders sections conditionally.

### New Pages (4 files in `src/app/vet/`)

#### Page 1: Vet Dashboard (`vet/page.tsx`)
- 4 StatCards: Pending Cases, Diagnosed Today, Animals in District, Active Alerts
- Recent unassigned cases table (click row to claim)
- District alert mini-map (reuse GISMap component, scoped to vet's district)
- Data: `GET /v1/vet/dashboard/stats` + `GET /v1/vet/cases?status=pending&limit=10`

#### Page 2: My Cases (`vet/cases/page.tsx`)
- Status tab filter: Pending | In Review | Diagnosed | Closed
- Table columns: farmer name, animal (species icon + name), channel badge, priority badge, date, status
- Click row → navigates to case detail
- Data: `GET /v1/vet/cases?status={tab}`

#### Page 3: Case Detail (`vet/cases/[id]/page.tsx`)
- **Left panel:** Farmer info card, animal card (species, breed, age, Pashu Aadhaar), photo gallery (clickable thumbnails), farmer's notes
- **Right panel:** Health history timeline for the animal (past events, vaccinations, medicine administrations)
- **Action section (bottom):**
  - "Claim Case" button (if unassigned) → PATCH `/cases/{id}/claim`
  - Diagnosis textarea
  - Prescription textarea
  - Follow-up date picker
  - Video call URL text input → PATCH `/cases/{id}/video-link`
  - "Save Diagnosis" button → PATCH `/cases/{id}/diagnose`
  - "Close Case" button → PATCH `/cases/{id}/close`

#### Page 4: District Alerts (`vet/alerts/page.tsx`)
- Reuses GISMap component filtered to vet's district
- Alert list with severity badges
- "Verify" button on each alert → PATCH `/v1/alerts/{id}/verify`

### Reused Components (no new components needed)
- StatCard, GISMap, RiskBadge, SpeciesChip — all existing

---

## 4. Mobile App — Farmer Side

### Modified: `app/vet-photo.tsx`
- On successful submission, display case ID + message "Your request has been sent to a nearby vet"
- Link to "View My Consultations"

### New Screen: `app/my-consultations.tsx`
- List from `GET /v1/vet/my-cases`
- Each card: animal name + species icon, status badge (pending=yellow, in_review=blue, diagnosed=green, closed=grey), date
- Tap card → detail:
  - Vet's diagnosis (if available)
  - Prescription text
  - Follow-up date
  - "Join Video Call" button → `Linking.openURL(video_call_url)` (prominent, only shown when URL exists)
  - Pending state: "A vet will review your case soon"

### Navigation
- Add "My Consultations" to quick actions grid on home screen
- Link from vet-photo success screen

### Translations
- Add `consultations` namespace to all 6 language files (en, hi, kn, ta, te, gu)

---

## 5. Implementation Plan

### Batch 1: API Foundation (parallel agents)
| # | Task | Files |
|---|------|-------|
| 1a | VetConsultation model + migration | models/vet.py, alembic/versions/ |
| 1b | `require_vet_or_admin()` middleware | middleware/auth.py |
| 1c | Vet router with all 9 endpoints | routers/vet.py |
| 1d | Modify health.py — auto-create consultation on photo upload, district scoping | routers/health.py |
| 1e | Modify alerts.py — allow vet verification | routers/alerts.py |
| 1f | Modify animals.py — district scoping for vets | routers/animals.py |
| 1g | Register vet router in main.py | main.py |
| 1h | Add vet user to seed data | seed/demo_data.py |

### Batch 2: Admin Dashboard (parallel agents)
| # | Task | Files |
|---|------|-------|
| 2a | Role-based sidebar | components/AdminSidebar.tsx |
| 2b | Vet Dashboard page | app/vet/page.tsx |
| 2c | Cases list page | app/vet/cases/page.tsx |
| 2d | Case detail page | app/vet/cases/[id]/page.tsx |
| 2e | District alerts page | app/vet/alerts/page.tsx |

### Batch 3: Mobile (parallel agents)
| # | Task | Files |
|---|------|-------|
| 3a | My Consultations screen + navigation | app/my-consultations.tsx, app/_layout.tsx, app/(tabs)/index.tsx |
| 3b | Update vet-photo.tsx with case feedback | app/vet-photo.tsx |
| 3c | Translations for all 6 languages | src/i18n/*.json |

---

## 6. Estimated Scope

| Layer | New Files | Modified Files |
|-------|-----------|----------------|
| API | 3 (model, migration, vet router) | 4 (health, alerts, animals, auth, main, seed) |
| Admin | 4 pages | 1 (sidebar) |
| Mobile | 1 screen | 3 (vet-photo, home, layout) + 6 translation files |
| **Total** | **8 new** | **14 modified** |
