# PashuRaksha ERP — Accessibility & Inclusive Design Audit

**Audit Date:** April 8, 2026
**Apps Audited:** Mobile (React Native / Expo), Admin Web (Next.js / MUI), API (FastAPI — out of scope for UI)
**Auditor Role:** Accessibility & Inclusive Design Expert — Indian Market
**Domains Covered:** A) Illiterate & Low-Literacy Usability, B) Indian Government Compliance (GIGW 3.0, WCAG 2.1 AA, RPwD Act 2016, IS 17802)

---

## Section 1: Literacy Accessibility Scores

### Mobile App (farmer-facing)

| Dimension | Score | Rationale |
|---|---|---|
| **Text independence** | 5/10 | Core flows (milk, health, sell) use icon+text pairs. But triage results, vaccination dates, loan CTAs, and emergency subtitles are hardcoded English text with no visual substitute. |
| **Visual clarity** | 6/10 | Emojis for species/symptoms are expressive. Health dot (red/green 10×10dp circle) is color-only and too small. Quick action labels are 11px — unreadable at arm's length. |
| **Navigation simplicity** | 7/10 | 5-tab bottom nav is excellent. Quick actions buried in a horizontal scroll (8 icons) create discovery problems. Navigation depth ≤ 3 levels throughout. |
| **Voice/audio support** | 3/10 | Voice input exists on one screen only (milk quantity). No text-to-speech, no read-aloud, no voice input for health symptoms, sell, or onboarding. |
| **Language coverage** | 4/10 | English + Kannada only. Hindi — India's largest language by speakers — is absent. 20+ hardcoded English strings remain untranslated in the Kannada build. |

**Overall Mobile Score: 5/10**

---

### Admin Web App (veterinarian/official-facing)

| Dimension | Score | Rationale |
|---|---|---|
| **Text independence** | 2/10 | This is a professional admin tool — text dependency is high by design. However, charts have zero text alternatives, which blocks screen reader users entirely. |
| **Visual clarity** | 6/10 | MUI icons are consistent and labeled. Sidebar section labels (~3.7:1 contrast estimated) are nearly invisible. Trend chips combine color + icon + text — good. |
| **Navigation simplicity** | 7/10 | Sidebar with grouped sections is clear. Active state uses both color + left border. No keyboard skip link makes tab navigation laborious. |
| **Voice/audio support** | 0/10 | No voice features. Admin users are professionals, so this is lower priority, but screen reader access is completely broken for charts and maps. |
| **Language coverage** | 1/10 | English only. No i18n framework wired in. No language toggle. |

**Overall Admin Score: 3/10**

---

## Section 2: GIGW / WCAG Compliance Matrix

### 2a. Mobile App (WCAG 2.1 Level AA)

| Criterion | Status | Location / File |
|---|---|---|
| **1.1.1 Non-text content (alt text)** | **FAIL** | `AnimalCard.tsx:42` — health dot has no text alternative. Colors are the only way to understand health status. |
| **1.1.1 Non-text content (icons)** | **PARTIAL** | `MicButton.tsx:103` has `accessibilityLabel`. All other `Pressable` + `IconButton` combinations across `_layout.tsx:11-27`, `index.tsx:97-114` have **no** `accessibilityLabel`. |
| **1.3.1 Info and relationships** | **FAIL** | `health.tsx:120-138` — symptom cards lack `accessibilityRole="checkbox"` and `accessibilityState={{ checked: isSelected }}`. Screen readers cannot convey selection state. Same issue for animal chips in `health.tsx:93-110`, `milk.tsx:103-120`. |
| **1.3.3 Sensory characteristics** | **FAIL** | `AnimalCard.tsx:40-46` — health status communicated by red/green dot color alone. No text or icon label. |
| **1.4.1 Use of color** | **FAIL** | AnimalCard health dot: green = healthy, red = sick — color is the **only** distinguishing feature. |
| **1.4.3 Contrast (minimum)** | **PARTIAL** | `index.tsx:204` — quick action labels use `fontSize: 11`. Main text contrast passes. `welcome.tsx:93-95` high contrast mode only sets `backgroundColor: '#000000'` but text colors are unchanged — all text becomes invisible. |
| **1.4.4 Resize text** | **PASS** | System font scaling is not blocked. react-native-paper respects font scale. |
| **2.1.1 Keyboard** | **N/A** | Native mobile — hardware keyboard partially applies. OTP boxes auto-advance focus correctly. |
| **2.4.3 Focus order** | **PARTIAL** | Tab/focus order generally follows visual order. `_layout.tsx:23-27` profile Pressable has no `accessibilityLabel` so focus announces "button" with no context. |
| **2.4.6 Headings and labels** | **FAIL** | `login.tsx:102-119` — six OTP `RNTextInput` boxes have no `accessibilityLabel`. Screen reader users cannot identify each box's position. |
| **3.1.1 Language of page** | **FAIL** | Triage messages in `health.tsx:29-42` are hardcoded English strings regardless of selected language: `"Possible FMD infection. Immediate vet attention needed."` |
| **3.3.1 Error identification** | **PARTIAL** | Voice failure shows status text but errors are ephemeral (2.5s). No persistent error state for invalid phone number in `login.tsx`. |
| **3.3.2 Labels or instructions** | **FAIL** | `login.tsx:104` OTP boxes: no label. `milk.tsx:306-314` numpad keys: no `accessibilityLabel`. |
| **4.1.2 Name, role, value** | **FAIL** | Widespread — all `Pressable` elements except `MicButton` lack `accessibilityRole`. Selected state not communicated on chips or symptom cards. |
| **4.1.3 Status messages** | **FAIL** | `milk.tsx:177-184` Snackbar: not announced to screen readers. `AccessibilityInfo.announceForAccessibility` is never called. |

---

### 2b. Admin Web App (WCAG 2.1 Level AA)

| Criterion | Status | Location / File |
|---|---|---|
| **1.1.1 Non-text content** | **FAIL** | `page.tsx:120-170` — Recharts `AreaChart` SVG has no `aria-label`, `title`, or data table fallback. `GISMap.tsx` Leaflet markers have no `aria-label`. `StatCard.tsx:95-97` — icon elements have no `aria-label`. |
| **1.3.1 Info and relationships** | **FAIL** | `AdminSidebar.tsx:148-159` — section headers ("CORE OPERATIONS", "LIVELIHOODS & SCHEMES") are `<Typography>` with no semantic role or aria-label. Not identified as navigation landmarks. `<Box component="main">` (`layout.tsx:105`) does not carry `aria-label`. |
| **1.4.3 Contrast (minimum)** | **FAIL** | `AdminSidebar.tsx:155` — section label color `rgba(200,221,216,0.45)` on background `#0f2b24`. Estimated blended contrast ≈ **3.7:1** — fails 4.5:1 for normal text at 10px uppercase. |
| **1.4.5 Images of text** | **PASS** | No images of text used. |
| **2.1.1 Keyboard** | **FAIL** | `GISMap.tsx` — Leaflet map is entirely mouse/touch only. No keyboard access to markers or map controls. Charts not keyboard navigable. |
| **2.4.1 Bypass blocks** | **FAIL** | `layout.tsx` — no skip navigation link to bypass the 260px fixed sidebar with 11 navigation items on every page load. |
| **2.4.2 Page titled** | **FAIL** | `layout.tsx:27` — `<title>PashuRaksha ERP - Admin Dashboard</title>` is static and identical on all 11 pages. |
| **2.4.6 Headings and labels** | **PARTIAL** | MUI `Typography variant="h4"` renders as `<h4>`. But no `<h1>` exists on any page — heading hierarchy starts at h4. |
| **3.1.1 Language of page** | **PARTIAL** | `layout.tsx:25` — `lang="en"` is set. No multi-language support. |
| **3.3.2 Labels or instructions** | **PASS** | `health/page.tsx:77-92` — FormControl + InputLabel correctly paired. |
| **4.1.2 Name, role, value** | **FAIL** | `StatCard.tsx:9` — icon rendered with no `aria-label` wrapper. Charts have no accessible name. |
| **4.1.3 Status messages** | **FAIL** | No `aria-live` regions anywhere. Dynamic content (filtered alert count `health/page.tsx:71`) changes without announcement. |

---

## Section 3: Critical Findings

---

### FINDING 1 — Missing `accessibilityLabel` on ~30+ Interactive Elements

| | |
|---|---|
| **Domain** | WCAG 4.1.2 / RPwD Act 2016 |
| **Severity** | **Critical (legal risk)** |
| **Affected users** | All TalkBack (Android) and VoiceOver (iOS) users — estimated 7+ million blind mobile users in India |
| **Priority** | Must-fix-before-launch |

**Current state:** Nearly all `Pressable` elements across the mobile app are missing `accessibilityLabel` and `accessibilityRole`. Specific locations:
- `_layout.tsx:11-27` — 3 header buttons (Smart Farm sprout, bell notification, profile) have no labels
- `index.tsx:97-114` — 8 quick action buttons read as "button" with no context
- `health.tsx:93-110` — animal chips have no label or selected state
- `health.tsx:119-139` — 7 symptom cards have no role, no selected state
- `milk.tsx:103-120` — animal chips have no selected state
- `milk.tsx:140-148` — 12 numpad keys have no label
- `login.tsx:23-27` — profile avatar Pressable has no label

**Required fix:**
```tsx
// _layout.tsx — fix header buttons
<IconButton
  icon="sprout"
  accessibilityLabel={t('common.smartFarm')}
  accessibilityRole="button"
/>
<IconButton
  icon="bell-outline"
  accessibilityLabel={t('common.notifications')}
  accessibilityRole="button"
/>

// index.tsx — fix quick action items
<Pressable
  key={action.key}
  onPress={() => router.push(action.route as any)}
  style={styles.quickActionItem}
  accessibilityLabel={t(`home.${action.key}`)}
  accessibilityRole="button"
>

// health.tsx — fix symptom cards
<Pressable
  key={symptom.key}
  onPress={() => toggleSymptom(symptom.key)}
  accessibilityLabel={t(`health.${symptom.key}`)}
  accessibilityRole="checkbox"
  accessibilityState={{ checked: isSelected }}
>

// milk.tsx — numpad keys
<Pressable
  key={key}
  onPress={() => handleNumpad(key)}
  accessibilityLabel={key === '⌫' ? 'Delete' : key}
  accessibilityRole="button"
>
```

**Legal reference:** WCAG 2.1 SC 4.1.2; RPwD Act 2016 §40-42; IS 17802

---

### FINDING 2 — Health Status Dot Is Color-Only (WCAG 1.4.1 Failure)

| | |
|---|---|
| **Domain** | WCAG 1.4.1 / Literacy Usability |
| **Severity** | **Critical (legal risk)** |
| **Affected users** | ~275 million people with color vision deficiency in India; all blind users |
| **Priority** | Must-fix-before-launch |

**Current state:** `AnimalCard.tsx:40-46` — a 10×10dp circle (green = healthy `#2E7D32`, red = sick `#C62828`) is the only health indicator on every animal card. No icon, no text label, no pattern.

**Required fix:**
```tsx
// AnimalCard.tsx — add text and icon alternative to health dot
<View style={styles.healthDotContainer}>
  <View
    style={[styles.healthDot, { backgroundColor: HEALTH_DOT[animal.healthStatus] }]}
  />
  {animal.healthStatus === 'sick' && (
    <Text style={styles.sickIndicator}>!</Text>
  )}
</View>

// Also add accessible label to the whole card:
<Pressable
  onPress={() => onPress(animal.id)}
  accessibilityLabel={`${animal.name}, ${t(`animals.${animal.species}`)}, ${t(`animals.${animal.healthStatus}`)}`}
  accessibilityRole="button"
  style={styles.pressable}
>
```

**Legal reference:** WCAG 2.1 SC 1.4.1 (Use of Color); SC 1.1.1 (Non-text Content); IS 17802

---

### FINDING 3 — Triage Messages Are Hardcoded English (Health-Critical Safety Failure)

| | |
|---|---|
| **Domain** | Literacy Usability / WCAG 3.1.1 |
| **Severity** | **Critical — health safety + legal risk** |
| **Affected users** | ~287 million illiterate adults in India; all Kannada-only speakers |
| **Priority** | Must-fix-before-launch |

**Current state:** `health.tsx:29-42` — `getTriageResult()` returns hardcoded English strings:
```
"Possible FMD infection. Immediate vet attention needed."
"Bloating detected. Risk of ruminal acidosis."
"Multiple symptoms detected. Vet visit recommended."
"Monitor closely. If symptoms persist, consult vet."
"Minor symptom. Keep monitoring for 24 hours."
```
A Kannada-only farmer sees the "Critical" badge in red but cannot understand the explanation or required action.

Additional hardcoded English strings found (all require i18n):
- `health.tsx:183` — `"24/7 Emergency Line"` (emergency contact subtitle)
- `health.tsx:198` — `"FMD - Due: 2026-05-15"` (vaccination schedule)
- `health.tsx:202` — `"Brucellosis - Due: 2026-06-01"` (vaccination schedule)
- `health.tsx:206` — `"HS/BQ - Due: 2026-07-10"` (vaccination schedule)
- `income.tsx:118` — `"Kisan Credit Card - Low interest"` (loan subtitle)
- `income.tsx:130` — `"Apply"` button label (not using `t()`)

**Required fix:**
```json
// en.json — add triage message keys
"health": {
  ...existing keys...,
  "triageFMD": "Possible FMD infection. Immediate vet attention needed.",
  "triageBloating": "Bloating detected. Risk of ruminal acidosis.",
  "triageMultipleHigh": "Multiple symptoms detected. Vet visit recommended.",
  "triageMultipleMedium": "Monitor closely. If symptoms persist, consult vet.",
  "triageMinor": "Minor symptom. Keep monitoring for 24 hours.",
  "emergencyLine": "24/7 Emergency Line",
  "kisanCreditCard": "Kisan Credit Card - Low interest"
}

// kn.json — human-reviewed Kannada translations required
"health": {
  "triageFMD": "ಸಾಧ್ಯ FMD ಸೋಂಕು. ತಕ್ಷಣ ಪಶುವೈದ್ಯರ ಗಮನ ಅಗತ್ಯ.",
  "triageBloating": "ಉಬ್ಬರ ಪತ್ತೆಯಾಗಿದೆ. ಹೊಟ್ಟೆ ಆಮ್ಲೀಯತೆ ಅಪಾಯ.",
  ...
}
```
```tsx
// health.tsx — replace hardcoded strings
function getTriageResult(symptoms: string[]): { severity: Severity; messageKey: string } | null {
  if (symptoms.length === 0) return null;
  if (symptoms.includes('fever') && symptoms.includes('diarrhea'))
    return { severity: 'critical', messageKey: 'health.triageFMD' };
  if (symptoms.includes('bloating'))
    return { severity: 'high', messageKey: 'health.triageBloating' };
  ...
}

// TriageCard.tsx — render translated message
<Text variant="bodyLarge" style={styles.message}>
  {t(messageKey)}
</Text>
```

**Legal reference:** WCAG 2.1 SC 3.1.1 (Language of Page); GIGW 3.0 §4.1 (Bilingual Content); RPwD Act 2016 §42

---

### FINDING 4 — High Contrast Mode Is Broken (Creates Lower Contrast, Not Higher)

| | |
|---|---|
| **Domain** | Literacy Usability / WCAG 1.4.3 |
| **Severity** | **Critical** |
| **Affected users** | ~40 million people with low vision in India |
| **Priority** | Must-fix-before-launch |

**Current state:** `welcome.tsx:93-95`:
```tsx
highContrast: {
  backgroundColor: '#000000',  // ONLY this changes
},
```
When enabled, only the background turns black. Text colors do not change: the title uses `color: '#2E7D32'` (dark green on black ≈ 2.7:1 — FAILS), subtitle uses `color: '#616161'` (barely visible), section labels use `color: '#212121'` (dark grey on black ≈ near-invisible). The user who enables this feature to aid their vision sees a nearly blank black screen.

**Required fix:**
```tsx
// welcome.tsx — propagate high contrast to all child styles
const titleStyle = [styles.title, highContrast && { color: '#FFFFFF' }];
const subtitleStyle = [styles.subtitle, highContrast && { color: '#EEEEEE' }];
const labelStyle = [styles.sectionLabel, highContrast && { color: '#FFFFFF' }];
const containerStyle = [styles.container, highContrast && styles.highContrast];
```
Long-term: Implement a `ThemeContext` that propagates the high contrast toggle app-wide so it applies consistently to all screens, not just the welcome screen.

**Legal reference:** WCAG 2.1 SC 1.4.3 (Contrast Minimum); SC 1.4.6 (Enhanced Contrast)

---

### FINDING 5 — Admin App Missing Skip Navigation + Static Page Titles

| | |
|---|---|
| **Domain** | WCAG 2.4.1 / WCAG 2.4.2 |
| **Severity** | **High (legal violation)** |
| **Affected users** | All keyboard-only and screen reader users of the admin app |
| **Priority** | Must-fix-before-launch |

**Current state (two issues):**
1. `layout.tsx` — no skip-to-main-content link. Users must tab through 11 sidebar items on every page load.
2. `layout.tsx:27` — `<title>PashuRaksha ERP - Admin Dashboard</title>` is identical across all 11 pages. Screen reader users cannot identify the current page from the title alone.

**Required fix:**
```tsx
// layout.tsx — add skip link
<a
  href="#main-content"
  style={{
    position: 'absolute',
    top: '-40px',
    left: '0',
    background: '#0f2b24',
    color: '#fff',
    padding: '8px',
    zIndex: 9999,
  }}
  onFocus={(e) => { e.currentTarget.style.top = '0'; }}
  onBlur={(e) => { e.currentTarget.style.top = '-40px'; }}
>
  Skip to main content
</a>

// layout.tsx — wrap sidebar in <nav>
<Box component="nav" aria-label="Primary navigation">
  <AdminSidebar />
</Box>
<Box component="main" id="main-content" ...>
  {children}
</Box>
```
```tsx
// Each page file — add unique title via Next.js metadata API
// admin/app/health/page.tsx
export const metadata = { title: 'Health Alerts — PashuRaksha ERP' };
// admin/app/farmers/page.tsx
export const metadata = { title: 'Farmers — PashuRaksha ERP' };
// admin/app/animals/page.tsx
export const metadata = { title: 'Animals — PashuRaksha ERP' };
// ... repeat for all 11 pages
```

**Legal reference:** WCAG 2.1 SC 2.4.1 (Bypass Blocks); SC 2.4.2 (Page Titled)

---

### FINDING 6 — Admin Charts and Maps Are Completely Inaccessible

| | |
|---|---|
| **Domain** | WCAG 1.1.1 / WCAG 2.1.1 |
| **Severity** | **High** |
| **Affected users** | All blind and low-vision admin users |
| **Priority** | Must-fix-before-launch |

**Current state:**
- `page.tsx:120-170` — Recharts `AreaChart` SVG renders with no `aria-label`, no `role="img"`, no data table fallback
- `GISMap.tsx` — Leaflet map markers are not keyboard-reachable; no text alternative describes alert locations
- `StatCard.tsx:82-97` — icon container renders SVG with no accessible name

**Required fix:**
```tsx
// page.tsx — accessible chart wrapper
<Typography variant="h6" id="milk-chart-title" gutterBottom>
  Milk Collection (Last 30 Days)
</Typography>
<div
  role="img"
  aria-labelledby="milk-chart-title"
  aria-describedby="milk-chart-desc"
>
  <ResponsiveContainer width="100%" height={320}>
    <AreaChart data={milkData}>...</AreaChart>
  </ResponsiveContainer>
</div>
<p
  id="milk-chart-desc"
  style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden' }}
>
  Area chart showing 30-day milk collection. Morning sessions average ~1000L,
  evening sessions average ~750L.
</p>
{/* Optional: accessible data table */}
<details>
  <summary>View as data table</summary>
  <table>
    <thead><tr><th>Date</th><th>Morning (L)</th><th>Evening (L)</th></tr></thead>
    <tbody>{milkData.map(d => (
      <tr key={d.date}><td>{d.date}</td><td>{d.morning}</td><td>{d.evening}</td></tr>
    ))}</tbody>
  </table>
</details>

// StatCard.tsx — label the icon container
<Box
  sx={{ ... }}
  role="img"
  aria-label={`${title} icon`}
>
  {icon}
</Box>
```

For `GISMap.tsx`, add an accessible summary table of alert points below the map as a keyboard-accessible alternative.

**Legal reference:** WCAG 2.1 SC 1.1.1 (Non-text Content); SC 2.1.1 (Keyboard)

---

### FINDING 7 — No Accessibility Statement or Issue Reporting Mechanism

| | |
|---|---|
| **Domain** | RPwD Act 2016 / IS 17802 |
| **Severity** | **High (legal non-compliance)** |
| **Affected users** | All users with disabilities |
| **Priority** | Must-fix-before-launch |

**Current state:** Neither the mobile app nor the admin web app has:
- An accessibility statement declaring WCAG compliance level
- A mechanism for users to report accessibility issues
- Documentation of available accessibility features (high contrast, voice input, language switching)
- A last-reviewed date for accessibility

India's Supreme Court (April 2025) ruled digital access is part of the right to life under Article 21. Absence of an accessibility statement is documented non-compliance.

**Required fix:**
- **Mobile:** Add an "Accessibility" item in `profile.tsx` settings linking to a new screen listing: supported languages, high contrast mode, voice input, keyboard navigation, and a contact email/phone for accessibility feedback.
- **Admin:** Add a footer link or settings page with a formal accessibility statement.

Statement minimum content:
```
Accessibility Statement — PashuRaksha ERP
Compliance level targeted: WCAG 2.1 Level AA
Last reviewed: April 2026
Known issues: [list from this audit]
Report an issue: [email / in-app form]
```

**Legal reference:** RPwD Act 2016 §40-46; IS 17802:2022 §5; Supreme Court Order (April 2025)

---

### FINDING 8 — Voice Input Missing on 4 of 5 Core Workflows

| | |
|---|---|
| **Domain** | Literacy Usability A4 |
| **Severity** | **High (excludes primary user group)** |
| **Affected users** | ~287 million illiterate adults who cannot type |
| **Priority** | Fix-in-next-sprint |

**Current state:** `MicButton.tsx` and `voice.ts` are only wired into the milk recording screen (`milk.tsx`). The following key screens require reading and typing with no voice alternative:
- `health.tsx` — selecting animal and symptoms
- `sell.tsx` — product selection and quantity
- `income.tsx` — no voice interaction
- `onboarding/profile.tsx` — name, phone number, village (all text fields)

The voice fallback error on failure (`errors.voiceFailed`) says "Voice not recognized — enter manually" — this is impossible for an illiterate user.

**Required fix (priority order):**
1. Add `MicButton` to the sell screen for quantity entry (reuse existing component — 30min)
2. Add TTS read-aloud to `TriageCard.tsx` using `expo-speech`:
```tsx
import * as Speech from 'expo-speech';

// TriageCard.tsx — add speak button
<Button
  icon="volume-high"
  mode="text"
  onPress={() => Speech.speak(t(messageKey), { language: 'kn-IN' })}
  accessibilityLabel="Read result aloud"
>
  {t('common.listen')}
</Button>
```
3. Change voice failure message to "ಮತ್ತೆ ಮಾತನಾಡಿ" ("Speak again") with a retry icon — remove the phrase "enter manually"
4. Add voice-activated symptom selection to health screen (voice command recognition for symptom names)

**Legal reference:** RPwD Act 2016 §40-46 (digital accessibility mandate)

---

### FINDING 9 — Admin Sidebar Section Labels Fail Contrast Ratio

| | |
|---|---|
| **Domain** | WCAG 1.4.3 |
| **Severity** | **High (legal violation)** |
| **Affected users** | All users with low vision; users on low-quality monitors |
| **Priority** | Fix-in-next-sprint |

**Current state:** `AdminSidebar.tsx:155-158`:
```tsx
color: 'rgba(200,221,216,0.45)',  // on background #0f2b24
```
Blended color of `rgba(200,221,216,0.45)` over `#0f2b24` is approximately `#637b75`.
- L(`#637b75`) ≈ 0.19, L(`#0f2b24`) ≈ 0.015
- Contrast ratio: (0.19 + 0.05) / (0.015 + 0.05) ≈ **3.7:1**
- WCAG AA requires **4.5:1** for text at this size (10px uppercase)

**Required fix:**
```tsx
// AdminSidebar.tsx:155
color: 'rgba(200,221,216,0.72)',  // was 0.45 — increases contrast to ~5.4:1
```

**Legal reference:** WCAG 2.1 SC 1.4.3 (Contrast Minimum)

---

### FINDING 10 — Snackbar Confirmations Are Silent to Screen Readers

| | |
|---|---|
| **Domain** | WCAG 4.1.3 |
| **Severity** | **Medium** |
| **Affected users** | All screen reader users on mobile |
| **Priority** | Fix-in-next-sprint |

**Current state:** `milk.tsx:177-184`, `sell.tsx` — Snackbar components show visual confirmations ("Milk recorded", "Sale recorded") but `AccessibilityInfo.announceForAccessibility` is never called. A blind farmer has no confirmation their action succeeded.

**Required fix:**
```tsx
// milk.tsx — announce all status messages
import { AccessibilityInfo } from 'react-native';

const handleRecord = () => {
  const msg = t('milk.recorded');
  setSnackMessage(msg);
  setSnackVisible(true);
  AccessibilityInfo.announceForAccessibility(msg);
  setQuantity('');
  setSelectedAnimal('');
};
```
Apply the same pattern to every `setSnackVisible(true)` call across all tab screens.

**Legal reference:** WCAG 2.1 SC 4.1.3 (Status Messages)

---

### FINDING 11 — OTP Input Boxes Have No Accessibility Labels

| | |
|---|---|
| **Domain** | WCAG 3.3.2 / WCAG 4.1.2 |
| **Severity** | **Medium** |
| **Affected users** | All screen reader users during login |
| **Priority** | Fix-in-next-sprint |

**Current state:** `login.tsx:103-119` — six `RNTextInput` OTP boxes have no `accessibilityLabel`. Screen reader announces "text field, text field, text field..." six times with no indication of position or purpose.

**Required fix:**
```tsx
<RNTextInput
  key={i}
  ref={(ref) => { otpRefs.current[i] = ref; }}
  accessibilityLabel={`OTP digit ${i + 1} of 6`}
  accessibilityHint="Enter one digit"
  value={digit}
  ...
/>
```

**Legal reference:** WCAG 2.1 SC 3.3.2 (Labels or Instructions); SC 4.1.2 (Name, Role, Value)

---

### FINDING 12 — Only 2 Languages Supported (Hindi Missing)

| | |
|---|---|
| **Domain** | GIGW 3.0 / Literacy Usability A6 |
| **Severity** | **Medium** |
| **Affected users** | ~600 million Hindi speakers; migrant agricultural workers across states |
| **Priority** | Fix-in-next-sprint |

**Current state:** Mobile app supports only English (`en`) and Kannada (`kn`). While the app targets Karnataka for pilot, government digital guidelines (GIGW 3.0 §4.1) mandate Hindi + at least one regional language as minimum. National integrations (Pashu Aadhaar, PM-Kisan, Bharat Pashudhan) require Hindi-language readiness.

**Required fix:**
- Add `packages/mobile/src/i18n/hi.json` (Hindi translations)
- Register `hi` language in `src/i18n/index.ts`
- Add "हिन्दी" button to `welcome.tsx` language selector
- **All translations must be human-reviewed** — GIGW 3.0 §4.2 explicitly prohibits raw machine translations for government-adjacent services

**Legal reference:** GIGW 3.0 §4.1 (Bilingual Minimum); Official Languages Act 1963

---

### FINDING 13 — Admin App Has No Internationalization (GIGW 3.0 Violation)

| | |
|---|---|
| **Domain** | GIGW 3.0 / RPwD Act |
| **Severity** | **Medium** |
| **Affected users** | ASHA workers, gram panchayat operators, AHD staff who communicate primarily in Kannada or Hindi |
| **Priority** | Fix-in-next-sprint |

**Current state:** The admin app (`packages/admin`) has no i18n configuration whatsoever. All content, labels, navigation, and table headers are English-only. The app serves district-level officials and veterinarians who may not be fluent in English.

**Required fix:** Add `i18next` and `react-i18next` to the admin package and provide Kannada translations for the admin interface. Add a language toggle to the admin header.

**Legal reference:** GIGW 3.0 §3.1 (Language Selection); Official Languages Act 1963

---

### FINDING 14 — Ambiguous Symptom Emoji for Low-Literacy Users

| | |
|---|---|
| **Domain** | Literacy Usability A2 |
| **Severity** | **Medium** |
| **Affected users** | Illiterate and low-literacy users (~400 million in India) |
| **Priority** | Fix-in-next-sprint |

**Current state:** `health.tsx:16-24` — symptom emojis include:
- Bloating: `🎈` (balloon/party) — does not suggest abdominal swelling in animals
- Discharge: `💧` (water drop) — abstract, not body-specific
- Limping: `🦿` (human prosthetic leg) — uses a human prosthetic, not an animal walking impairment
- Diarrhea: `⚠️` (warning triangle) — completely abstract

Research on Indian rural users shows realistic pictorial images significantly outperform abstract emoji for low-literacy comprehension.

**Required fix (short-term):**
```tsx
const SYMPTOM_DATA = [
  { key: 'fever',      icon: '🌡️' },   // thermometer — clear
  { key: 'noAppetite', icon: '🍃❌' },  // plant with X (no eating)
  { key: 'limping',    icon: '🐾' },    // paw print — animal walking
  { key: 'discharge',  icon: '🔴💧' },  // colored drop — more specific
  { key: 'bloating',   icon: '🐄💨' }, // animal with gas/swelling
  { key: 'coughing',   icon: '💨' },    // wind — acceptable
  { key: 'diarrhea',   icon: '⚠️🚿' }, // warning + wash symbol
];
```

**Long-term fix:** Commission a custom icon set with silhouettes of cattle/goats showing the affected body part — swollen belly, bent leg, runny nose, etc. These are far more recognizable than abstract emoji for first-time smartphone users.

---

### FINDING 15 — Vaccination Dates Displayed in ISO Format (Illiterate Users Cannot Parse)

| | |
|---|---|
| **Domain** | Literacy Usability A6 |
| **Severity** | **Low** |
| **Affected users** | Illiterate users who cannot parse ISO 8601 date format |
| **Priority** | Fix-in-next-sprint |

**Current state:** `health.tsx:198-206` — vaccination reminders are hardcoded:
```
"FMD - Due: 2026-05-15"
"Brucellosis - Due: 2026-06-01"
```
ISO date format is unintelligible to illiterate users. Indian rural users understand relative terms ("tomorrow", "3 days from now") or day-month formats far better than YYYY-MM-DD.

**Required fix:** Use relative date formatting with the existing i18n keys:
```tsx
// The i18n already has: "dueIn": "Due in" and "days": "days"
// Use them: "Due in 37 days" → t('vaccinations.dueIn', { count: daysUntilDue })

const daysUntilDue = Math.round(
  (new Date(vaccine.dueDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
);
const dueDateLabel = daysUntilDue <= 0
  ? t('vaccinations.overdue')
  : `${t('vaccinations.dueIn')} ${daysUntilDue} ${t('vaccinations.days')}`;
```

---

## Section 4: Remediation Roadmap

### Week 1 — Critical / Legal (Block Launch)

| # | Fix | Files | Effort |
|---|---|---|---|
| 1 | Add `accessibilityLabel` + `accessibilityRole` to all Pressable elements — header, quick actions, numpad | `index.tsx`, `_layout.tsx`, `milk.tsx` | 2h |
| 2 | Add `accessibilityRole="checkbox"` + `accessibilityState={{ checked }}` to symptom cards and animal chips | `health.tsx`, `milk.tsx` | 2h |
| 3 | Fix color-only health dot — add text label and icon alternative | `AnimalCard.tsx` | 1h |
| 4 | Move all triage messages and hardcoded English strings into i18n | `health.tsx`, `income.tsx` | 3h |
| 5 | Fix broken high contrast mode — apply text/title/label color overrides when toggled | `welcome.tsx` | 2h |
| 6 | Add OTP box accessibility labels (`accessibilityLabel`, `accessibilityHint`) | `login.tsx` | 30m |
| 7 | Add skip navigation link + unique `<title>` per page in admin | `layout.tsx`, all admin page files | 1h |
| 8 | Wrap admin charts with `role="img"`, `aria-label`, and hidden data table | `page.tsx`, `StatCard.tsx` | 3h |
| 9 | Add `<Box component="nav" aria-label>` wrapper around admin sidebar | `layout.tsx` | 30m |
| 10 | Add accessibility statement screen (mobile) + page (admin) with contact mechanism | New files | 2h |

---

### Weeks 2–3 — High Impact (Unlock Access for Largest User Groups)

| # | Fix | Files | Effort |
|---|---|---|---|
| 11 | Call `AccessibilityInfo.announceForAccessibility()` for all Snackbar confirmations | All tab screens | 1h |
| 12 | Add TTS "read aloud" button to `TriageCard` using `expo-speech` | `TriageCard.tsx` | 2h |
| 13 | Fix admin sidebar section label contrast (opacity 0.45 → 0.72) | `AdminSidebar.tsx` | 15m |
| 14 | Increase quick action label font size from 11px to 13px | `index.tsx` | 15m |
| 15 | Add accessible alternative table for GIS map markers | `GISMap.tsx` | 4h |
| 16 | Add Hindi language support (`hi.json`) — human translation required | `src/i18n/` | 8h |
| 17 | Replace ambiguous symptom emojis with clearer alternatives | `health.tsx` | 1h |
| 18 | Switch vaccination due dates to relative date format using existing i18n keys | `health.tsx`, `vaccinations.tsx` | 2h |
| 19 | Change voice failure error from "enter manually" to "Speak again" + retry icon | `en.json`, `kn.json`, `MicButton.tsx` | 1h |

---

### Month 2 — Improvements (Usability & Broader Coverage)

| # | Fix | Files | Effort |
|---|---|---|---|
| 20 | Commission realistic animal-body pictographic icon set for symptoms (replaces emoji) | Design + component | 2 weeks |
| 21 | Extend voice input to health symptom selection (voice-command symptom toggle) | `health.tsx`, `voice.ts` | 1 week |
| 22 | Extend voice input to sell screen quantity entry | `sell.tsx` | 3 days |
| 23 | Implement app-wide high contrast `ThemeContext` (not per-screen toggle) | `theme.ts`, root `_layout.tsx` | 3 days |
| 24 | Add i18n to admin app (Kannada minimum, Hindi stretch goal) | `packages/admin` | 1 week |
| 25 | Add Tamil support for southern India scaling (`ta.json`) | `src/i18n/` | 8h (translation) |
| 26 | Add heading hierarchy fix in admin — ensure `<h1>` exists on every page | All admin page files | 2h |

---

### Ongoing — Continuous Compliance

| Recommendation | Detail |
|---|---|
| **Screen reader QA protocol** | Test every new screen against TalkBack (Android) and VoiceOver (iOS) before merging. Checklist: all Pressables labeled, selected state communicated, status messages announced. |
| **Translation process** | Human review for all i18n strings — especially medical/veterinary content. AI-only translations for health advice can cause animal deaths. |
| **Contrast audit tooling** | Add `axe-core/react` or `eslint-plugin-jsx-a11y` to the admin build pipeline for automated WCAG contrast and landmark checks. |
| **Annual GIGW review** | GIGW guidelines and IS 17802 are updated periodically. Schedule an annual accessibility review. |
| **Low-literacy user testing** | Before each major release, conduct in-field testing with 5–10 actual low-literacy farmers in Karnataka. Code review does not substitute for watching a first-time smartphone user interact with the app. |
| **Bhashini integration** | Integrate with CDAC Bhashini for cross-language speech recognition — extends voice coverage to 22+ Indian languages without per-language API contracts. |
| **expo-speech TTS coverage** | Audit every screen that displays health, financial, or action-required information. Add a "read aloud" button to all of them using `expo-speech` with language set to `'kn-IN'` or user's selected language. |

---

## Summary Scorecard

| Category | Mobile | Admin |
|---|---|---|
| **Literacy accessibility** | 5/10 | 3/10 |
| **WCAG 2.1 AA** | ~45% pass | ~50% pass |
| **GIGW 3.0** | Partial | Minimal |
| **RPwD Act 2016** | Non-compliant | Non-compliant |
| **IS 17802** | Non-compliant | Non-compliant |
| **Ready for rural India launch?** | **Not yet** | **Not yet** |

---

## What the App Gets Right (Preserve These)

The foundation has genuine inclusive design intent — do not sacrifice these in the remediation sprint:

- **Emoji species icons** (🐄🐐🐑🐔) are excellent — universally recognized in rural India
- **Kannada as the default language** — correct for Karnataka deployment
- **Sarvam AI voice input on milk screen** — the right architecture, needs expansion
- **48dp minimum touch targets** — meets WCAG and exceeds typical Indian agri-app quality
- **Numpad for milk quantity** — critical for users with low numeric literacy
- **Progressive disclosure** in health screen (symptoms only shown after animal selected)
- **High contrast toggle presence** in onboarding — intent is correct, implementation needs fixing
- **Language switcher on first screen** — correct placement, users can choose before seeing any content
- **Session picker emoji** (☀️ Morning / 🌙 Evening) — reduces text dependency for time-based data entry
- **Sarkari-aligned Pashu Aadhaar integration** — builds on existing farmer digital literacy with government ID systems

---

*Report generated: April 8, 2026 | Audit methodology: Direct source code analysis of all 164 files across mobile, admin, and API packages*
