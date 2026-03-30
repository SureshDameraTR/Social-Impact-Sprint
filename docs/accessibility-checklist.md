# PashuRaksha Accessibility & Inclusive UX Checklist

> Comprehensive guidelines for designing PashuRaksha mobile and admin interfaces for rural women farmers, low-literacy users, elderly users (60+), and budget Android devices.

---

## Table of Contents

1. [Visual Design & Contrast](#1-visual-design--contrast)
2. [Typography & Readability](#2-typography--readability)
3. [Icon-Based & Text-Free Navigation](#3-icon-based--text-free-navigation)
4. [Voice-First & Audio Interface](#4-voice-first--audio-interface)
5. [Touch Targets & Motor Accessibility](#5-touch-targets--motor-accessibility)
6. [Navigation & Information Architecture](#6-navigation--information-architecture)
7. [Multimodal Feedback (Haptic + Audio + Visual)](#7-multimodal-feedback-haptic--audio--visual)
8. [Language & Localization](#8-language--localization)
9. [Digital Confidence & Onboarding](#9-digital-confidence--onboarding)
10. [Offline-First & Low Connectivity](#10-offline-first--low-connectivity)
11. [Device Performance (2GB RAM / Budget Android)](#11-device-performance-2gb-ram--budget-android)
12. [Elderly User (60+) Specific](#12-elderly-user-60-specific)
13. [Cultural Sensitivity & Trust](#13-cultural-sensitivity--trust)
14. [Agricultural Domain Specific](#14-agricultural-domain-specific)
15. [WCAG 2.1 Compliance Matrix](#15-wcag-21-compliance-matrix)
16. [GIGW 3.0 Compliance](#16-gigw-30-compliance)
17. [Implementation Priority Matrix](#17-implementation-priority-matrix)

---

## 1. Visual Design & Contrast

### Why It Matters
Farmers view screens outdoors in bright sunlight, often on cracked screens with low-quality displays. ~80% of people with disabilities live in emerging markets. WCAG AA is the legal standard in India per GIGW 3.0 and the RPWD Act.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 1.1 | **Minimum 4.5:1 contrast ratio** for all body text against backgrounds | Must-have | WCAG 2.1 AA 1.4.3 |
| 1.2 | **Minimum 7:1 contrast ratio** for critical text (amounts, alerts, animal health status) | Must-have | WCAG 2.1 AAA 1.4.6 |
| 1.3 | **Minimum 3:1 contrast ratio** for all UI components (buttons, icons, form borders) | Must-have | WCAG 2.1 AA 1.4.11 |
| 1.4 | **Replace pure white (#FFFFFF) backgrounds** with off-white (#F5F5F0 or similar) to reduce glare in sunlight | Must-have | Google NBU |
| 1.5 | **Use solid-fill icons** instead of outline/thin-line icons (thin lines disappear at angles and in sunlight) | Must-have | Agri UX Research |
| 1.6 | **High-saturation, warm color palette**: terracotta reds, farm greens, saffron accents that reflect rural Indian culture | Must-have | Cultural UX |
| 1.7 | **Never rely on color alone** to convey information. Use color + icon + text/pattern | Must-have | WCAG 2.1 AA 1.4.1 |
| 1.8 | **Test on actual budget devices** outdoors in sunlight, not just design tools | Must-have | Google NBU |
| 1.9 | Support Android system-level **"High Contrast Text"** setting | Nice-to-have | Material Design |
| 1.10 | **Avoid pure black text on pure white** -- use dark gray (#1A1A1A) on off-white for reduced eye strain | Nice-to-have | Agri UX |

### PashuRaksha Implementation
- Health status indicators: Use color + icon + pattern (e.g., red circle with X + "Sick" audio label, not just red color)
- Animal cards: Bold text on high-contrast backgrounds, visible in sunlight
- Dashboard charts: Use distinct patterns (hatching, dots) in addition to colors for colorblind users

---

## 2. Typography & Readability

### Why It Matters
Low-literacy users recognize individual characters slowly. Elderly users (60+) experience vision decline. Hindi/Devanagari script requires larger rendering than Latin characters. Research shows 18px as the minimum effective base font for rural Indian users (BHIM Lite study).

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 2.1 | **Minimum 18px (14pt) base font size** for all body text | Must-have | BHIM Redesign / Elderly UX |
| 2.2 | **24px+ for critical information** (animal names, health alerts, financial amounts) | Must-have | Low-literacy research |
| 2.3 | **Heavy/bold font weights** for primary content (thin fonts disappear on low-res screens) | Must-have | Agri UX Research |
| 2.4 | **Avoid ALL CAPS** for body text (harder to read for low-literacy users) | Must-have | WCAG cognitive |
| 2.5 | **Line height 1.5x font size minimum** for readability | Must-have | WCAG 2.1 AA 1.4.12 |
| 2.6 | **Maximum 40 characters per line** in mobile view | Must-have | Readability research |
| 2.7 | Use **sans-serif fonts** optimized for Devanagari and regional scripts (Noto Sans Devanagari) | Must-have | Localization |
| 2.8 | Support **user-adjustable font sizes** (respect Android system font scaling) | Must-have | Elderly UX / WCAG |
| 2.9 | **Avoid justified text** -- use left-aligned (or right-aligned for RTL scripts) | Must-have | Low-literacy research |
| 2.10 | Use **numerals (1, 2, 3)** instead of written numbers ("one, two, three") | Must-have | Low-literacy UX |

### PashuRaksha Implementation
- Animal health cards: Name in 24px bold, status in 20px, details in 18px
- Financial summaries (milk sales, insurance): Use large numerals with currency symbols
- Hindi/regional script text needs 10-15% more vertical space than English equivalent

---

## 3. Icon-Based & Text-Free Navigation

### Why It Matters
750 million adults globally are illiterate. Research confirms textual interfaces are "unusable by first-time low-literacy users" (Medhi et al., 2011). Skeuomorphic, literal iconography that depicts real-world objects is understood instantly across literacy levels.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 3.1 | **Every primary action must have an icon** -- never text-only buttons for core flows | Must-have | Low-literacy research |
| 3.2 | Use **literal/skeuomorphic icons** depicting real objects (actual cow, milk pail, syringe) not abstract symbols | Must-have | SARAL Framework |
| 3.3 | **Always pair icons with short text labels** (for semi-literate users who can read some words) | Must-have | Material Design |
| 3.4 | **Bottom tab bar with 3-5 icon items** as primary navigation (thumb-reachable) | Must-have | Mobile Nav Best Practice |
| 3.5 | Icon size minimum **48x48dp** on mobile (larger than standard 24dp) | Must-have | Touch target research |
| 3.6 | Use **color coding consistently** across the app (green = healthy, red = sick, blue = information) | Must-have | Low-literacy / Voice annotation research |
| 3.7 | **Avoid hamburger menus** -- hidden navigation is least discoverable for novice users | Must-have | NN/g Research |
| 3.8 | Use **photo-realistic illustrations** for complex concepts (vaccination, insurance claim process) | Must-have | Medhi et al. |
| 3.9 | Provide **audio labels for icons** -- tap-and-hold to hear what an icon means | Must-have | Voice-first research |
| 3.10 | Test icon comprehension with **actual target users in the field** before finalizing | Must-have | IDEO / GramRaj |
| 3.11 | Create a **custom agricultural icon library** reflecting Indian rural context | Nice-to-have | Cultural UX |

### PashuRaksha Implementation
- Bottom nav: Home (house icon), My Animals (cow icon), Health (heart+cross icon), Market (shop/cart icon), Profile (person icon)
- Animal actions: Camera icon for photos, Syringe icon for vaccination, Clipboard for health records
- Registration flow: Step-by-step with large illustrated guides showing each action

---

## 4. Voice-First & Audio Interface

### Why It Matters
India is a "voice-first nation" (Sarvam AI). Research shows dialed/touch-tone input outperforms speech recognition for task completion in rural contexts (Avaaj Otalo study). Farmers specifically requested ability to listen to content rather than read it. Voice annotation + color-coded graphics are the two most effective UI components for rural women.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 4.1 | **Voice readout of all critical information** -- health alerts, vaccination reminders, market prices | Must-have | Voice-first research |
| 4.2 | **Audio confirmation for actions** -- "Vaccination recorded successfully" spoken in local language | Must-have | Haptic/Audio research |
| 4.3 | Support **Sarvam AI voice APIs** for 11+ Indian languages (Hindi, Tamil, Telugu, Kannada, etc.) | Must-have | Sarvam AI / Project stack |
| 4.4 | **Voice input for search and data entry** -- speak animal name instead of typing | Must-have | Low-literacy UX |
| 4.5 | **IVR-style fallback** -- phone call based access for users without smartphones | Nice-to-have | Avaaj Otalo model |
| 4.6 | **Audio content for advisories** -- veterinary tips, scheme information as audio clips | Must-have | Agri UX Research |
| 4.7 | Provide **volume control** and option to mute audio globally | Must-have | Accessibility |
| 4.8 | **Audio works in noisy environments** -- use clear, professional voice recordings, not TTS for critical alerts | Must-have | Rural context |
| 4.9 | Support **code-switching** (Hinglish, regional+English mix) in voice recognition | Nice-to-have | Sarvam Bulbul V3 |
| 4.10 | **WhatsApp-style voice messages** for veterinary consultations and community features | Nice-to-have | Farmer behavior research |

### PashuRaksha Implementation
- Every screen has a "Listen" button (speaker icon) that reads the page content aloud
- Vaccination reminders delivered as audio push notifications in user's language
- Voice-based animal registration: "Add my cow named Lakshmi, she is 3 years old"
- Market prices announced daily via audio in the app and optionally via SMS/WhatsApp

---

## 5. Touch Targets & Motor Accessibility

### Why It Matters
Elderly users have reduced fine motor control. Budget phones have small, low-resolution screens. Cracked screens (common in emerging markets) make small targets unreachable. Research shows thumb-based, one-handed operation is the norm.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 5.1 | **Minimum 48x48dp touch targets** (9mm physical) for all interactive elements | Must-have | WCAG 2.1 AA 2.5.5 / Material |
| 5.2 | **Recommended 56x56dp or larger** for primary action buttons | Must-have | Elderly UX / Low-literacy |
| 5.3 | **Minimum 8dp spacing** between adjacent touch targets | Must-have | Material Design |
| 5.4 | **Primary actions within thumb zone** (bottom 2/3 of screen) | Must-have | Mobile UX / BHIM study |
| 5.5 | **Avoid small checkboxes and radio buttons** -- use large toggle switches or card-based selection | Must-have | Elderly UX |
| 5.6 | **No double-tap or long-press for essential actions** (these gestures are unknown to novice users) | Must-have | Low-literacy research |
| 5.7 | **Swipe gestures only as enhancement**, never as only way to perform an action | Must-have | Elderly UX |
| 5.8 | **Visible pressed/active states** with color change + subtle animation | Must-have | Digital Confidence |
| 5.9 | Support both **portrait and landscape** orientation | Nice-to-have | Material / WCAG |
| 5.10 | **Avoid drag-and-drop** interactions entirely | Must-have | Low-literacy / Elderly |

### PashuRaksha Implementation
- All buttons: minimum 56dp height, full-width on mobile for easy tapping
- Animal selection: Large photo cards (not small list items)
- Forms: Large input fields with 48dp height, clear labels above (not inside) fields

---

## 6. Navigation & Information Architecture

### Why It Matters
Low-literacy users perform best with linear navigation (Parikh et al.). Complex hierarchies and menus cause confusion and abandonment. The "3 taps to any content" rule is validated by GramRaj's field research. Fear of getting lost in an app prevents adoption.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 6.1 | **Linear, sequential flows** for all multi-step tasks (registration, health recording, insurance claim) | Must-have | Low-literacy research |
| 6.2 | **Maximum 3 taps** to reach any core feature from home screen | Must-have | Agri UX / GramRaj |
| 6.3 | **Persistent back button** visible on every screen (do not rely on Android system back) | Must-have | Novice user research |
| 6.4 | **Clear progress indicators** for multi-step flows (Step 1 of 3, with visual progress bar) | Must-have | IDEO Digital Confidence |
| 6.5 | **Avoid deep nesting** -- maximum 2 levels of hierarchy | Must-have | Low-literacy / Elderly |
| 6.6 | **Persistent home button** accessible from any screen | Must-have | Novice user research |
| 6.7 | **No dead ends** -- every screen must have a clear next action or way to go back | Must-have | UX Best Practice |
| 6.8 | **Avoid tabs within tabs** or secondary navigation levels | Must-have | Cognitive load |
| 6.9 | **Consistent navigation placement** across all screens | Must-have | WCAG 2.1 AA 3.2.3 |
| 6.10 | **Breadcrumb or location indicator** showing where the user is | Nice-to-have | WCAG / Elderly UX |

### PashuRaksha Implementation
- Home screen: 4-6 large icon cards for primary actions (My Animals, Add Animal, Health Check, Market, Insurance, Help)
- Animal registration: Linear wizard (Photo > Name > Species > Age > Done) with progress dots
- No nested menus; all features accessible from home grid or bottom nav

---

## 7. Multimodal Feedback (Haptic + Audio + Visual)

### Why It Matters
Research confirms users prefer haptic+audio combined feedback as the most reliable. Low-literacy users cannot read confirmation messages. Multimodal feedback reduces errors and builds confidence. Critical for noisy outdoor environments where audio alone may not be heard, or situations where audio is muted.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 7.1 | **Triple confirmation for critical actions**: visual checkmark + haptic buzz + audio "Done" | Must-have | Multimodal research |
| 7.2 | **Success feedback**: green flash + gentle vibration + positive sound on successful actions | Must-have | Haptic design |
| 7.3 | **Error feedback**: red highlight + stronger vibration + warning sound on errors | Must-have | WCAG 3.3.1 |
| 7.4 | **Button press feedback**: visual depression + light haptic tap on every button press | Must-have | Android haptic principles |
| 7.5 | **Allow users to control** each feedback channel independently (mute audio, disable haptic) | Must-have | Accessibility |
| 7.6 | Use **consistent feedback patterns** -- same vibration pattern always means same thing | Must-have | Haptic design principles |
| 7.7 | **Transient haptic for taps**, continuous haptic only for loading/waiting states | Must-have | Android haptic guidelines |
| 7.8 | **Avoid excessive haptic feedback** -- use only for meaningful interactions, not scrolling | Must-have | UX Best Practice |
| 7.9 | **Visual feedback must work without** audio or haptic (for users who disable them) | Must-have | Accessibility |
| 7.10 | Test feedback on **real budget devices** (haptic motors vary dramatically by device) | Must-have | Device testing |

### PashuRaksha Implementation
- Vaccination recorded: Green checkmark animation + "Tikakaran darz" (vaccination recorded) audio + short vibration
- Payment received: Coin animation + amount spoken aloud + vibration
- Error states: Shake animation + "Kripya dobara koshish karein" (please try again) + longer vibration

---

## 8. Language & Localization

### Why It Matters
India has 22 scheduled languages and hundreds of dialects. Only 12% of government websites are available in all scheduled languages. 77.7% literacy rate means 22.3% cannot read any language. Users frequently code-switch between languages (Hinglish). Sarvam AI supports 11+ Indian languages for voice.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 8.1 | **Launch with Hindi + English** at minimum, with architecture for adding languages | Must-have | GIGW 3.0 |
| 8.2 | **Language selection on first launch** with flag/script visual indicators (not text-only menu) | Must-have | Low-literacy UX |
| 8.3 | **Easy language switching** from any screen (persistent language toggle) | Must-have | GIGW 3.0 |
| 8.4 | **Support Devanagari, Tamil, Telugu, Kannada, Bengali scripts** natively | Must-have | Indian market |
| 8.5 | **Numbers always in local numerals** with option for Arabic numerals | Must-have | Localization |
| 8.6 | **Dates in local format** (DD/MM/YYYY for India) | Must-have | Localization |
| 8.7 | **Currency in INR** with proper formatting (Rs. or rupee symbol) | Must-have | Localization |
| 8.8 | **Avoid idioms, jargon, abbreviations** -- use simple, direct language at Grade 3-5 reading level | Must-have | WCAG 3.1.5 / Low-literacy |
| 8.9 | **Text expansion accommodation** -- Hindi text is ~30% longer than English; UI must not clip | Must-have | Localization |
| 8.10 | **Audio content localized** -- not just translated text, but culturally appropriate voice and tone | Must-have | Sarvam / Cultural UX |
| 8.11 | Plan for **Marathi, Gujarati, Punjabi, Odia, Malayalam** in subsequent releases | Nice-to-have | Scaling |

### PashuRaksha Implementation
- First launch: Full-screen language picker with large script samples (showing "PashuRaksha" written in each script)
- All audio via Sarvam AI Bulbul V3 for natural-sounding regional voices
- Veterinary terms use common local names (e.g., "khurapaka" for foot-and-mouth disease in Hindi)

---

## 9. Digital Confidence & Onboarding

### Why It Matters
IDEO's research with Google Pay, Flipkart, and Airtel shows that fear of errors is the #1 barrier to digital adoption. Rural users distrust apps -- "Too complex, not for us" (GramRaj field research). First-gen smartphone users need to "look before they leap." Face-to-face demonstration before first use is the most effective onboarding for elderly and low-literacy users.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 9.1 | **No-risk exploration mode** -- let users try features without submitting real data first | Must-have | IDEO Digital Confidence |
| 9.2 | **Visual, step-by-step onboarding** with illustrations, not text instructions | Must-have | Elderly UX / Low-literacy |
| 9.3 | **Video tutorials** in local language for each major feature | Must-have | Elderly UX research |
| 9.4 | **Progressive disclosure** -- show basic features first, reveal advanced features over time | Must-have | IDEO / Google NBU |
| 9.5 | **Undo/cancel available for all actions** -- let users feel safe to explore | Must-have | Digital Confidence |
| 9.6 | **Confirmation dialogs before destructive actions** with clear, visual explanation of what will happen | Must-have | WCAG 3.3.4 |
| 9.7 | **Success celebrations** -- positive reinforcement when user completes a task (animations, sounds) | Must-have | Digital Confidence |
| 9.8 | **Error messages in plain language** with clear illustration of what went wrong and how to fix it | Must-have | WCAG 3.3.3 |
| 9.9 | Design for **face-to-face training** by milk center operators or village health workers | Must-have | Elderly UX / Field research |
| 9.10 | **Skippable but re-accessible tutorials** -- available from help section anytime | Must-have | Onboarding UX |
| 9.11 | **WhatsApp-based support** channel (most familiar app for rural Indian users) | Nice-to-have | Farmer behavior |

### PashuRaksha Implementation
- First launch: "Meet Lakshmi" guided tour with an animated cow character walking through features
- Demo mode with sample animals pre-loaded for exploration
- Milk center operators trained as digital champions for in-person onboarding
- Every error shows: illustration of problem + spoken explanation + single "Fix it" button

---

## 10. Offline-First & Low Connectivity

### Why It Matters
Rural India has intermittent connectivity. Network switches between WiFi, 3G, 2G, and no connectivity. YouTube Go proved offline-first design works in India. Farmers need to record data in the field where there is no signal. 60% of rural Indian farmers have smartphone + internet, but connectivity is unreliable.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 10.1 | **All core features work offline** -- animal registration, health recording, viewing records | Must-have | Google NBU |
| 10.2 | **Automatic sync when connectivity returns** -- no user action required | Must-have | Offline-first |
| 10.3 | **Clear offline indicator** -- visual badge (not just text) showing offline status | Must-have | UX Best Practice |
| 10.4 | **Sync status per record** -- show which records are synced and which are pending | Must-have | Data integrity |
| 10.5 | **Cache critical reference data** -- disease list, vaccination schedules, scheme information | Must-have | Offline-first |
| 10.6 | **Conflict resolution** for data edited offline by multiple users | Must-have | Data architecture |
| 10.7 | **Minimize data usage** -- compress images, use efficient data formats | Must-have | Google NBU / Cost |
| 10.8 | **Show data usage estimates** before downloads ("This will use 2 MB") | Nice-to-have | Google NBU |
| 10.9 | **Graceful degradation** -- features that need connectivity show clear "will work when online" message | Must-have | Progressive enhancement |
| 10.10 | **SMS fallback** for critical notifications (vaccination reminders, health alerts) | Nice-to-have | Rural infrastructure |

### PashuRaksha Implementation
- SQLite/WatermelonDB local storage for all animal and health data
- Photos compressed to <200KB before upload, queued for sync
- Vaccination schedule and disease reference data cached on first sync
- Market prices cached with "last updated" timestamp visible

---

## 11. Device Performance (2GB RAM / Budget Android)

### Why It Matters
40%+ of Android devices globally have 2GB RAM or less. Typical budget phone in rural India: quad-core 1.3GHz, 2GB RAM, 16GB storage, small 5" screen. App must compete for resources with WhatsApp, YouTube, and other daily-use apps. Android Go edition targets devices with 1GB RAM or less.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 11.1 | **APK size under 25MB** (ideally under 15MB) | Must-have | Android Go / NBU |
| 11.2 | **RAM usage under 90MB PSS** during normal operation | Must-have | Android Go guidelines |
| 11.3 | **Cold start under 3 seconds** on budget hardware | Must-have | Performance |
| 11.4 | **Lazy-load all non-critical content** -- images, audio, secondary features | Must-have | Android memory optimization |
| 11.5 | **Use WebP/vector graphics** instead of PNG for all assets | Must-have | Android optimization |
| 11.6 | **Avoid heavy animations** -- use simple fade/slide transitions, no Lottie on low-end | Must-have | Performance |
| 11.7 | **Implement device tiering** -- detect low-RAM devices and reduce feature complexity | Must-have | Android Build for Billions |
| 11.8 | **Respond to onTrimMemory()** -- release caches when system is under memory pressure | Must-have | Android memory mgmt |
| 11.9 | **Avoid persistent background services** -- use WorkManager for sync | Must-have | Android best practice |
| 11.10 | **Support Android 8.0+** (API 26) to cover Go edition devices | Must-have | Android Go |
| 11.11 | **ProGuard/R8 enabled** for code shrinking and optimization | Must-have | APK optimization |
| 11.12 | **Test on actual budget devices** (Jio Phone, Redmi Go, Samsung Galaxy A series) | Must-have | Quality assurance |

### PashuRaksha Implementation
- Expo/React Native with Hermes engine for reduced memory footprint
- Image loading with progressive JPEG, max 800px width for animal photos
- Feature flags to disable heavy features (video tutorials) on low-RAM devices
- Periodic memory profiling on Redmi 9A (2GB RAM) as reference device

---

## 12. Elderly User (60+) Specific

### Why It Matters
Many animal owners in rural India are elderly. Cognitive decline, reduced vision, motor impairment, and technology anxiety are common. Systematic reviews (Gomez-Hernandez 2023, 132 studies) confirm elderly users need fundamentally different design approaches, not just bigger fonts.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 12.1 | **Single-task screens** -- one primary action per screen, no multitasking | Must-have | Elderly UX research |
| 12.2 | **No time limits** on any interaction (no auto-logout, no countdown timers) | Must-have | WCAG 2.1 AA 2.2.1 |
| 12.3 | **Forgiving input** -- accept multiple date formats, fuzzy name matching, auto-correct | Must-have | Elderly UX |
| 12.4 | **Minimize keyboard use** -- prefer selection (dropdowns, date pickers, photo-based input) over typing | Must-have | Elderly / Motor |
| 12.5 | **Clear distinction between tappable and non-tappable elements** (use shadows, borders, color) | Must-have | BHIM redesign |
| 12.6 | **Avoid gestures as primary interaction** -- provide button alternatives for swipe, pinch, etc. | Must-have | Elderly UX |
| 12.7 | **Remember user preferences** -- last selected animal, preferred language, favorite features | Must-have | Cognitive load |
| 12.8 | **Slow, interruptible animations** -- no fast-moving content that is hard to follow | Must-have | Elderly / Cognitive |
| 12.9 | **Dedicated "Help" button** visible on every screen (phone icon to call support) | Must-have | Elderly UX |
| 12.10 | **Allow family member co-access** -- simple way for son/daughter to help manage the account | Nice-to-have | Rural family dynamics |

### PashuRaksha Implementation
- Animal health recording: One question per screen (What animal? > What issue? > When? > Done)
- Date entry: Calendar picker with large day buttons, not keyboard input
- Species selection: Large photo cards (cow photo, buffalo photo) not dropdown list
- Emergency vet call: Single large red button on health screen

---

## 13. Cultural Sensitivity & Trust

### Why It Matters
Rural users distrust technology they do not understand. Cultural context affects icon interpretation (e.g., shopping cart icon meaningless where there are no supermarkets). Trust is built through familiar visual language and community endorsement. Women in rural India may face additional barriers to technology access.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 13.1 | **Use culturally familiar visual metaphors** -- village art-inspired palettes, familiar animal illustrations | Must-have | GramRaj / Cultural UX |
| 13.2 | **Show real photos of similar users** (rural women farmers) in onboarding and marketing | Must-have | Trust / IDEO |
| 13.3 | **Government scheme logos and branding** visible to build institutional trust | Must-have | Indian context |
| 13.4 | **Privacy explanations in simple visual terms** -- "Your data stays on your phone" with lock icon | Must-have | Trust / GIGW |
| 13.5 | **No surprise data charges** -- warn before any large download with estimated cost | Must-have | Google NBU |
| 13.6 | **Community endorsement features** -- show how many local farmers use the app | Nice-to-have | Social proof |
| 13.7 | **Respect local naming conventions** and forms of address | Must-have | Cultural sensitivity |
| 13.8 | **Calendar integration** with local festivals, agricultural seasons, and market days | Nice-to-have | Domain relevance |
| 13.9 | **Avoid Western/urban imagery** -- no stock photos of tech-savvy urban users | Must-have | Cultural fit |
| 13.10 | **Women-centered design** -- feature women as primary users in all illustrations and photos | Must-have | Gender inclusion |

### PashuRaksha Implementation
- Onboarding shows illustration of a rural woman farmer using the app with her animals
- Government scheme information includes official logos (NDDB, DAHD, state dairy cooperatives)
- Color palette inspired by rangoli art and Indian agricultural imagery
- All avatar defaults are culturally appropriate illustrations

---

## 14. Agricultural Domain Specific

### Why It Matters
Farmers want crop/animal-specific data, not generic information. The desire to sell for more, have healthier animals, and access government grants are the motivators that drive adoption. 58% of Indian rural households depend on farming. Most farmers already use YouTube and WhatsApp for agricultural learning.

### Checklist

| # | Guideline | Priority | Standard |
|---|-----------|----------|----------|
| 14.1 | **Animal-specific customization** -- show only relevant data for the user's actual animals | Must-have | Agri UX |
| 14.2 | **Photo-based animal identification** -- camera as primary data entry method | Must-have | Low-literacy UX |
| 14.3 | **Vaccination schedules as visual timeline** with animal photos, not text tables | Must-have | Domain UX |
| 14.4 | **Market prices in context** -- show per-liter milk price with daily/weekly trend arrows | Must-have | Farmer needs |
| 14.5 | **Weather integration** with simple icons (sun, rain, cloud) and impact on animal care | Nice-to-have | Agri apps |
| 14.6 | **Seasonal advisories** -- calving season tips, monsoon disease prevention, summer heat stress | Must-have | Domain expertise |
| 14.7 | **Video tutorials** from local veterinarians in regional language | Must-have | YouTube learning pattern |
| 14.8 | **Quick-dial veterinarian** from within the app | Must-have | Emergency access |
| 14.9 | **Insurance claim flow** simplified to photo + 3 taps maximum | Must-have | Financial inclusion |
| 14.10 | **Milk collection record** integrated with local dairy cooperative data | Must-have | Revenue tracking |

### PashuRaksha Implementation
- Home screen prominently shows "Today's Milk Price" and "Next Vaccination Due"
- Animal health check: Photo capture > select symptom from visual grid > get advisory
- Insurance: Pre-filled claim form from animal records, just add incident photo
- Integration with NDDB/dairy cooperative APIs for milk collection data

---

## 15. WCAG 2.1 Compliance Matrix

Specific WCAG 2.1 success criteria most relevant to PashuRaksha's target users:

| WCAG Criterion | Level | Relevance | Implementation |
|---|---|---|---|
| **1.1.1** Text Alternatives | A | All icons/images need alt text for screen readers | Provide contentDescription for all images |
| **1.3.1** Info and Relationships | A | Structure conveyed through semantics | Use proper heading hierarchy, labeled form fields |
| **1.3.4** Orientation | AA | Some users mount phones | Support both portrait and landscape |
| **1.4.1** Use of Color | A | Colorblind users, outdoor glare | Never use color alone for meaning |
| **1.4.3** Contrast (Minimum) | AA | Sunlight, low-res screens | 4.5:1 for text, 3:1 for UI |
| **1.4.4** Resize Text | AA | Elderly users, low vision | Support 200% zoom without loss |
| **1.4.11** Non-text Contrast | AA | UI component visibility | 3:1 for all interactive elements |
| **1.4.12** Text Spacing | AA | Readability | Allow user override of spacing |
| **2.1.1** Keyboard | A | Assistive device users | All functions operable without touch gestures |
| **2.2.1** Timing Adjustable | A | Elderly, cognitive | No time limits on interactions |
| **2.4.6** Headings and Labels | AA | Navigation clarity | Descriptive headings on all screens |
| **2.5.5** Target Size | AAA (recommended) | Motor impairment, elderly | 44x44 CSS px minimum |
| **3.1.2** Language of Parts | AA | Multilingual content | Mark language changes in content |
| **3.2.3** Consistent Navigation | AA | Cognitive, novice users | Same nav on every screen |
| **3.3.1** Error Identification | A | All users | Clear visual + audio error messages |
| **3.3.2** Labels or Instructions | A | Low-literacy, novice | Visual labels for all form inputs |
| **3.3.3** Error Suggestion | AA | All users | Plain-language fix suggestions |
| **3.3.4** Error Prevention | AA | Financial/legal actions | Confirm before insurance claims, data deletion |

---

## 16. GIGW 3.0 Compliance

Key GIGW 3.0 requirements applicable to PashuRaksha:

| GIGW Area | Requirement | PashuRaksha Implementation |
|---|---|---|
| **Accessibility** | 50 WCAG 2.1 Level AA criteria | Full compliance per Section 15 above |
| **Multi-language** | Support for scheduled Indian languages | Hindi + English at launch, architecture for 22 languages |
| **Mobile-first** | Responsive, mobile-accessible design | React Native / Expo mobile-first architecture |
| **Security** | CERT-In advisories compliance | HTTPS, encrypted local storage, secure auth |
| **Content** | Clear, simple, citizen-friendly language | Grade 3-5 reading level, audio alternatives |
| **Usability** | User-centric, universally accessible (UUU) | All guidelines in this checklist |

---

## 17. Implementation Priority Matrix

### Phase 1: MVP (Must-Have for Launch)

**Visual & Contrast**
- [ ] 4.5:1+ contrast ratios throughout
- [ ] Off-white backgrounds for sunlight readability
- [ ] Solid-fill icons
- [ ] Color + icon + text for all status indicators

**Typography**
- [ ] 18px minimum base font
- [ ] 24px+ for critical data
- [ ] Bold weights for primary content
- [ ] Support system font scaling

**Navigation**
- [ ] Bottom tab bar with 4-5 icon items
- [ ] 3 taps to any core feature
- [ ] Linear flows for all multi-step tasks
- [ ] Persistent back + home buttons

**Touch & Motor**
- [ ] 48dp+ touch targets (56dp for primary actions)
- [ ] Primary actions in thumb zone
- [ ] No gesture-only interactions

**Voice & Audio**
- [ ] Voice readout for health alerts and reminders
- [ ] Audio confirmation for key actions
- [ ] Hindi + English voice support via Sarvam
- [ ] Listen button on critical screens

**Language**
- [ ] Hindi + English at launch
- [ ] Language picker on first launch
- [ ] Simple, Grade 3-5 reading level text

**Offline**
- [ ] Core features work offline
- [ ] Auto-sync on reconnect
- [ ] Offline status indicator

**Performance**
- [ ] APK under 25MB
- [ ] RAM under 90MB PSS
- [ ] Cold start under 3 seconds
- [ ] Test on Redmi 9A reference device

**Feedback**
- [ ] Visual + haptic confirmation for actions
- [ ] Clear error states with fix suggestions
- [ ] Success celebrations

**Onboarding**
- [ ] Visual step-by-step guided tour
- [ ] Demo/exploration mode
- [ ] Video tutorials for core features

### Phase 2: Enhancement (Post-Launch Sprint)

- [ ] Additional 5+ Indian languages
- [ ] Voice input for data entry and search
- [ ] IVR phone-based fallback access
- [ ] Advanced device tiering (low/mid/high)
- [ ] WhatsApp support channel integration
- [ ] Family member co-access feature
- [ ] SMS fallback for notifications
- [ ] Community endorsement features
- [ ] Calendar integration with agricultural seasons

### Phase 3: Scale (Ongoing)

- [ ] All 22 scheduled Indian languages
- [ ] Code-switching support in voice recognition
- [ ] AI-powered symptom checker with voice
- [ ] Regional dialect voice models
- [ ] Feature usage analytics for UX optimization
- [ ] Longitudinal usability testing with elderly users
- [ ] STQC CQW certification for GIGW compliance

---

## Key Sources & References

### Standards & Guidelines
- [WCAG 2.1 W3C Specification](https://www.w3.org/TR/WCAG21/)
- [GIGW 3.0 Guidelines for Indian Government Websites](https://guidelines.india.gov.in/)
- [Material Design 3 Accessibility](https://m3.material.io/foundations/accessible-design/overview)
- [Android Build for Billions](https://developer.android.com/docs/quality-guidelines/build-for-billions/device-capacity)
- [Android Memory Optimization](https://developer.android.com/guide/topics/androidgo/optimize-memory)

### Research Papers
- [Medhi et al. (2011) - Designing Mobile Interfaces for Novice and Low-Literacy Users (ACM TOCHI)](https://dl.acm.org/doi/10.1145/1959022.1959024)
- [SARAL Framework (2021) - Actionable UI Guidelines for Low-Literate Users (ACM CSCW)](https://dl.acm.org/doi/10.1145/3449210)
- [Islam et al. (2023) - Designing UIs for Illiterate and Semi-Literate Users (SAGE)](https://journals.sagepub.com/doi/full/10.1177/21582440231172741)
- [Patel et al. (2009) - Experiences Designing a Voice Interface for Rural India (IEEE)](https://ieeexplore.ieee.org/document/4777830/)
- [Gomez-Hernandez et al. (2023) - Design Guidelines for Mobile Apps for Older Adults (JMIR)](https://mhealth.jmir.org/2023/1/e43186)
- [Chaudry et al. (2012) - Mobile Interface Design for Low-Literacy Populations](https://course.khoury.northeastern.edu/is4300f13/ssl/chaudry.pdf)

### Design Frameworks & Tools
- [Google Next Billion Users - Connectivity, Culture, and Credit](https://design.google/library/connectivity-culture-and-credit)
- [Google Designing for Global Accessibility Part III](https://design.google/library/designing-global-accessibility-part-iii)
- [IDEO Digital Confidence Design Tools](https://digitalconfidence.design/tools)
- [IDEO - 5 Tools to Design for Digital Confidence](https://www.ideo.com/journal/5-tools-to-design-for-digital-confidence)
- [UNESCO - Designing Inclusive Digital Solutions](https://unesdoc.unesco.org/ark:/48223/pf0000265537)

### Voice & Language Technology
- [Sarvam AI - Text to Speech API](https://www.sarvam.ai/apis/text-to-speech)
- [Sarvam AI - Bulbul V3 Voice Model](https://www.varindia.com/news/sarvam-unveils-bulbul-v3-ai-voice-model-for-indian-languages)

### India-Specific UX
- [BHIM UPI Lite Version Case Study for Rural Users](https://ariqnarasaputra.hashnode.dev/uiux-case-study-designing-lite-version-of-bhim-upi-app-for-rural-indian-users)
- [BHIM UX Redesign Case Study (NetBramha)](https://netbramha.com/work/bhim-user-experience-design-case-study/)
- [FarmRise Agriculture App Design (Lollypop Design)](https://lollypop.design/projects/farmrise/)
- [GramRaj Agriculture/Farming App Case Study](https://www.designstudiouiux.com/case-study/agriculture-farming-app-design/)
- [India Digital Accessibility Laws Overview](https://www.digitala11y.com/indias-digital-accessibility-laws-and-overview/)
- [RPWD Act and IS 17802: India's Digital Accessibility Standards](https://www.pivotalaccessibility.com/2025/06/rpwd-act-and-is-17802-indias-digital-accessibility-standards-2025-guide/)

### Android Haptic & Feedback
- [Android Haptics Design Principles](https://developer.android.com/develop/ui/views/haptics/haptics-principles)
- [Haptic Feedback Impact on Mobile Usability](https://livewithoutinternet.com/the-impact-of-haptic-feedback-on-mobile-device-usability-and-accessibility/)

### Color & Contrast
- [W3C Colors with Good Contrast](https://www.w3.org/WAI/perspective-videos/contrast/)
- [WCAG Color Contrast Guide 2025](https://www.allaccessible.org/blog/color-contrast-accessibility-wcag-guide-2025)
