# Research: Admin Panel, User Onboarding & Scheme Management
## Social Impact Sprint — Farmer-Centric Animal Husbandry Platform

---

# PART 1: ADMIN PANEL RESEARCH

## 1.1 How Indian Cooperative Platforms Manage Admin Operations

### Amul — Digital Backbone
Amul has built India's most advanced cooperative digital ecosystem:
- **ERP**: IBM-partnered ERP (SAP S/4HANA) integrating finance, procurement, inventory, manufacturing, HR, and reporting across multiple plants and cooperatives ([Amul Supply Chain](https://logisticsviewpoints.com/2024/10/15/amuls-optimized-supply-chain-driving-global-growth-in-the-dairy-industry/))
- **Amul AI Platform (2026)**: Built on 50 years of cooperative data — manages 200 crore+ annual milk procurement transactions, veterinary records from 1,200+ doctors covering ~3 crore cattle, ~70 lakh AI (artificial insemination) per year, and ISRO satellite imagery for fodder mapping ([Amul AI](https://www.artificialintelligence-news.com/news/amul-ai-dairy-farming-platform-india/))
- **Automatic Milk Collection System (AMCS)**: Real-time milk quality testing and payment at village collection centers
- **Multi-channel Access**: Mobile app (10 lakh+ downloads) + voice calls for feature phone users, built on Bhashini multilingual framework (20 languages)
- **GIS Integration**: Geographical Information System at both procurement and marketing ends

### KMF / Nandini (Karnataka)
- Second-largest milk cooperative in India, founded 1974 under World Bank backing
- 14 Milk Unions covering all Karnataka districts, procuring from Primary Dairy Cooperative Societies (DCS)
- Follows the AMUL cooperative pattern but with less publicly documented technology infrastructure
- Key learning: Even the second-largest cooperative still has significant digitization gaps — opportunity for our platform ([KMF Wikipedia](https://en.wikipedia.org/wiki/Karnataka_Milk_Federation))

### Key Admin Patterns from Cooperatives
| Feature | Amul | KMF/Nandini |
|---------|------|-------------|
| ERP System | SAP S/4HANA (IBM) | Limited/manual |
| Mobile App | Amul Farmer App | Basic web portal |
| AI/ML | Amul AI platform | None documented |
| Multi-language | 20 languages (Bhashini) | Kannada + English |
| Farmer ID | Biometric/UID | Cooperative membership |
| Voice Access | Yes (feature phone) | No |

---

## 1.2 Government Admin Portals — Lessons Learned

### e-GOPALA (NDDB — Livestock Management)
The government's primary livestock management platform, launched by PM Modi in September 2020 ([e-GOPALA PIB](https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1808244)):

**Admin Features (IMAP Web Portal):**
- Geographical presentation of project coverage via INAPH
- State/district-wise animal registration coverage vs population
- PSK Service ticket status (registration, AI, pregnancy diagnosis, calving, vaccination, treatment)
- Real-time monitoring of NAIP and NADCP government projects
- Available in 12 languages including Kannada

**Farmer-Facing Features:**
- Breed improvement marketplace (germplasm buying/selling)
- Quality breeding service discovery (AI, veterinary first aid, vaccination)
- Balanced ration formulation using local feed ingredients
- Real-time alerts (vaccination due dates, pregnancy diagnosis, calving)
- Direct call center connectivity
- Impact: 5 million+ farmers, 32% yield improvement in trials

**Design Lessons for Our Platform:**
- Admin portal should provide geographical (GIS-based) views of coverage
- Separate admin views for service delivery tracking (ticket-based workflow)
- Integration with national databases (INAPH) is essential
- 12-language support is the baseline expectation

### eNAM (National Agriculture Market)
India's pan-India electronic trading portal for agricultural commodities ([eNAM Wikipedia](https://en.wikipedia.org/wiki/E-NAM)):

**Admin Architecture:**
- Four module groups: Masters (configuration), Transactions (workflows + reports), Administration (authorized admins only)
- ~20 report types: Gate Entry/Exit, Weighbridge, Farmer/Trader Registration, Arrival Summary, Daily Reports
- MIS Dashboard (since 2018) for per-mandi performance monitoring
- Role-based access for farmers, traders, commission agents, processors, exporters, mandi functionaries
- Integrated payment system (Kotak Mahindra Bank)
- 1,473 mandis currently connected

**Design Lessons:**
- Master data management is a critical admin function (commodity configs, market rules, pricing)
- Multi-role stakeholder support with clear workflow separation
- Comprehensive MIS reporting is non-negotiable for government compliance
- Payment integration must be a first-class concern

---

## 1.3 Role-Based Access Control (RBAC) Design

### Recommended RBAC Architecture for Our Platform

Based on research from [NocoBase](https://www.nocobase.com/en/blog/how-to-design-rbac-role-based-access-control-system), [Pathlock](https://pathlock.com/blog/role-based-access-control-rbac/), and agriculture-specific cybersecurity research ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12040926/)):

**Hybrid RBAC + ABAC Model Recommended**
- RBAC for standard job-function roles
- ABAC (Attribute-Based) for context-sensitive refinements (geography, cooperative membership, scheme eligibility)

**Role Hierarchy:**

```
Super Admin (Platform)
  |-- State Admin
  |     |-- District Admin
  |           |-- Block/Taluk Admin
  |                 |-- Village Coordinator
  |
  |-- Cooperative Admin (KMF/Union level)
  |     |-- DCS Manager (Dairy Cooperative Society)
  |
  |-- Veterinary Admin
  |     |-- Senior Veterinarian
  |     |-- Field Veterinarian
  |     |-- Para-Vet / Community Animal Health Worker
  |
  |-- Financial Admin
  |     |-- Bank Branch Manager
  |     |-- Insurance Agent
  |     |-- SHG Coordinator
  |
  |-- Trader/Market Admin
  |     |-- Registered Trader
  |     |-- Commission Agent
  |
  |-- Farmer (end user)
  |     |-- SHG Member (additional role)
  |     |-- FPO Member (additional role)
```

**Permission Matrix:**

| Role | Animal Records | Health/Treatment | Trading | Finance | Schemes | Analytics | User Mgmt |
|------|---------------|-----------------|---------|---------|---------|-----------|-----------|
| Super Admin | Full | Full | Full | Full | Full | Full | Full |
| State Admin | Read All | Read All | Read All | Read All | Manage | Full | State-level |
| District Admin | Read District | Read District | Read District | Read District | Approve | District | District |
| Cooperative Admin | Read Coop | Read Coop | Manage | Read | View | Coop | Coop members |
| Veterinarian | Read Assigned | Create/Update | - | - | View | Own cases | - |
| Para-Vet | Read Assigned | Create (limited) | - | - | View | - | - |
| Bank Manager | - | - | Read | Approve/Manage | View/Approve | Financial | - |
| Trader | Read Listed | Read (certified) | Create/Bid | Own txns | - | Own trades | - |
| Farmer | Own animals | Own animals | Own listings | Own records | Apply/View | Own data | Own profile |
| SHG Coordinator | Read SHG | Read SHG | Read SHG | Manage SHG funds | Apply for SHG | SHG analytics | SHG members |

**Key Design Principles:**
1. **Principle of Least Privilege**: Every role gets minimum necessary access
2. **Multi-role Assignment**: A farmer can also be an SHG member and FPO member
3. **Geographic Scoping**: Admin roles are scoped by geography (state > district > block > village)
4. **Audit Logging**: Every permission change and data access logged for compliance
5. **Backend Enforcement**: API-level RBAC, not just UI hiding — critical for government audit

---

## 1.4 Report Generation for Government/NABARD Compliance

### NABARD Compliance Requirements ([NABARD Supervision](https://www.nabard.org/about-departments.aspx?id=5&cid=469))

Reports the platform must generate:

**1. Off-Site Surveillance (OSS) Returns**
- Financial ratios and qualitative indicators
- Submitted digitally via NABARD's SuperSoft application (v2.0)
- Pre-defined data formats with strict submission deadlines

**2. CAMELSC Framework Data**
- Capital Adequacy metrics
- Asset Quality reports
- Management assessment data
- Earnings statements
- Liquidity ratios
- Systems compliance
- Compliance status reports

**3. Annual Compliance Reports**
- Audited financial statements (CA-certified)
- Income Tax Returns (even for exempt societies)
- GST Returns (if applicable)
- Long Form Audit Report (LFAR) — detailed format per ICAI guidelines
- Corporate Governance Index Return

**4. KYC/AML/CFT Reports**
- FIU-IND reporting for suspicious transactions
- CERSAI reporting
- FATF compliance data

### Platform Report Module Design

```
Report Categories:
├── Operational Reports
│   ├── Daily Collection Summary (milk/produce)
│   ├── Animal Health Summary (vaccinations, treatments, births, deaths)
│   ├── Trading Activity (listings, transactions, settlements)
│   └── User Activity (registrations, active users, feature usage)
│
├── Financial Reports
│   ├── SHG Fund Status (savings, loans, repayments)
│   ├── Insurance Claims (filed, approved, rejected, disbursed)
│   ├── KCC Utilization (disbursed, outstanding, repayments)
│   └── Revenue/Cost Summary (platform economics)
│
├── Government/NABARD Reports
│   ├── OSS Returns (pre-formatted)
│   ├── Scheme Utilization (RGM, NLM, PMFBY, KCC)
│   ├── Beneficiary Statistics (by gender, caste, geography)
│   ├── DBT Disbursement Reports
│   └── Social Audit Reports
│
├── Analytics/MIS
│   ├── GIS-based Coverage Maps
│   ├── Breed Improvement Statistics
│   ├── Disease Surveillance Dashboard
│   ├── Market Price Trends
│   └── Adoption Metrics (digital literacy progression)
│
└── Compliance/Audit
    ├── LFAR Data Export
    ├── CAMELSC Framework Data
    ├── KYC/AML Transaction Reports
    └── Complete Audit Trail Export
```

---

## 1.5 Open-Source Admin Framework Recommendation

### Comparison: React-Admin vs Refine vs AdminJS

Based on research from [Marmelab](https://marmelab.com/blog/2023/07/04/react-admin-vs-refine.html), [Refine](https://refine.dev/core/docs/further-readings/comparison/), and FastAPI integration analysis:

| Criteria | React-Admin | Refine | AdminJS |
|----------|-------------|--------|---------|
| **FastAPI Compatibility** | Via REST data providers (custom headers needed) | Via Simple REST provider | Node.js only — NOT compatible |
| **Maturity** | 5+ years, ~4,000 closed issues | Since 2021, rapidly growing | Mature but wrong ecosystem |
| **Relationship Handling** | Excellent built-in (`<ReferenceField>`, dedup) | Manual — significant boilerplate | Auto-detected from ORM |
| **Form Components** | Rich (multiple layouts) | Basic (`useForm` only) | Auto-generated |
| **UI Framework** | Material UI (opinionated) | Headless (MUI, Ant, Mantine, Tailwind) | Built-in React UI |
| **SSR Support** | Limited (react-router only) | Next.js, Remix support | No |
| **Offline/PWA** | FakeRest in-browser provider | Not built-in | No |
| **i18n** | Built-in | Built-in | Built-in |
| **Community Data Provider for FastAPI** | `fastapi-react-admin` (PyPI) | Simple REST works directly | N/A |

### Recommendation: **Refine** (Primary) with FastAPI Backend

**Why Refine over React-Admin:**
1. **Headless architecture** — we already chose Material-UI for the farmer-facing app; Refine lets us use MUI on admin too for consistency
2. **SSR support via Next.js** — better for admin dashboards loaded over slow connections in field offices
3. **More flexible** — we need custom components for GIS maps, scheme management, and report builders that don't fit React-Admin's opinionated structure
4. **Growing ecosystem** — despite being newer, Refine is actively maintained with 27k+ GitHub stars

**Why not AdminJS:**
- AdminJS is Node.js-only (Express, Fastify, Hapi) — does NOT work with Python/FastAPI
- Would require a separate Node.js service just for admin, adding unnecessary architectural complexity

**Implementation Approach:**
```
Admin Panel Stack:
- Framework: Refine (headless) + Next.js
- UI: Material UI (consistent with farmer app)
- Data Provider: Custom REST provider for FastAPI endpoints
- Auth Provider: Custom (JWT/OAuth2 matching main platform auth)
- Charts: Recharts or Chart.js
- Maps: Leaflet/MapLibre for GIS views
- Reports: React-PDF for exportable reports
- Tables: AG Grid or TanStack Table for complex data grids
```

---

# PART 2: USER ONBOARDING RESEARCH

## 2.1 Design Principles for Low-Literacy Rural Users

### Voice-First Design

Research from multiple sources confirms voice is the primary interface for rural India:

- **370 million adults in India are illiterate** — voice tech is the only way to reach them ([LBBOnline](https://lbbonline.com/news/why-rural-india-holds-surprising-insights-about-the-power-of-voice))
- **Avaaj Otalo** research: Voice-based telephony platforms have "extensive global network coverage, minimal literacy requirements, and widespread accessibility" ([ResearchGate](https://www.researchgate.net/publication/221518989_Avaaj_Otalo_-_A_field_study_of_an_interactive_voice_forum_for_small_farmers_in_rural_India))
- **FarmerChat (Digital Green)**: Reached 350,000+ farmers, 35% women, 60% act on advice — multimodal: voice, text, image, video ([News9Live](https://www.news9live.com/technology/digital-greens-ai-chatbot-transforms-farming-for-indias-smallholders-2918678))
- **Bharat-VISTAAR**: Government platform that's voice-first — works via phone call, chatbot, and web, no smartphone required ([Tribune India](https://www.tribuneindia.com/news/india/shivraj-chouhan-launches-ai-powered-bharat-vistaar-platform-for-farmers/))
- **Sarvam AI** (our chosen stack for Indic TTS/STT): Aligns perfectly with this research

### UI Design Research for Illiterate/Semi-Literate Users

From a systematic review in SAGE Journals ([UI Design for Illiterate Users](https://journals.sagepub.com/doi/full/10.1177/21582440231172741)):

**Do:**
- Use large, colorful icons with real-world metaphors (cow icon for animal records, not abstract symbols)
- Audio feedback for every interaction (tap = sound confirmation)
- Visual progress indicators (not text-based)
- Consistent navigation patterns (same position, same colors)
- Minimal text — use pictograms and voice labels
- High contrast ratios (WCAG 2.1 AA minimum)

**Avoid:**
- Text-heavy interfaces
- Abstract icons or Western metaphors
- Deep navigation hierarchies (max 2 levels)
- Small tap targets (minimum 48x48dp, recommend 56x56dp)
- Reliance on typing/keyboard input

---

## 2.2 Successful Indian App Onboarding Strategies

### PhonePe Strategy ([upGrowth](https://upgrowth.in/phonepe-won-india-upi-war-gtm-strategy-teardown/))
- **On-ground sales force** for merchant onboarding at street level
- **QR code simplicity** — one physical artifact to bridge digital divide
- **Vernacular language** support making app feel "native to each region"
- **18 million+ merchants** onboarded, heavy rural/Tier 2-3 penetration

### Google Pay Strategy ([DataNext](https://www.datanext.ai/case-study/google-pay-upi-app/))
- Started as "Tez" — meaning "fast" in Hindi, culturally resonant naming
- **Audio QR** (ultrasonic sound) for proximity payments — no need to scan
- **Reward-driven incentives** for behavioral change
- Helped normalize digital payments among "auto-rickshaw drivers to elderly pensioners"

### Common Success Patterns
1. **Extreme simplicity** — minimum taps to complete core action
2. **Vernacular first** — not English-first with translation, but native-language-first
3. **Physical-digital bridge** — QR codes, physical cards, or phone calls as entry points
4. **Trust via familiarity** — use metaphors from existing trusted interactions
5. **Incentivize first action** — cashback, rewards, immediate tangible benefit

---

## 2.3 Dropout Rates & Failure Points

### Key Statistics ([ICTworks](https://www.ictworks.org/12-reasons-why-farmers-do-not-use-mobile-agritech-services/), [BharatInclusion](https://medium.com/bharatinclusion/using-smartphone-based-applications-some-challenges-faced-by-farmers-e51f9e3b73d1))

**Why Farmers Abandon Apps:**
1. **Language barrier**: Only 36% of agriculture apps support multiple languages
2. **Network issues**: Most apps require high-speed connectivity; rural areas have intermittent 3G
3. **Storage limits**: Entry-level phones (1-2GB RAM, limited storage) — farmers reluctant to install new apps
4. **Generic content**: Advice doesn't match their land size, crop cycles, or local conditions
5. **Digital literacy gap**: Don't understand passwords, encryption, or smartphone capabilities
6. **Power access**: Some areas have inconsistent electricity; phones kept off to save battery
7. **Trust deficit**: Apps seen as "tools by outsiders who don't understand local realities"
8. **No immediate value**: If first experience doesn't show clear benefit, user never returns

**Device Reality in Rural India:**
- Entry-level Android: Itel, Lava, Micromax — 4-5 inch screens, 1-2GB RAM, older Android versions
- ~60% of rural farmers have smartphone with internet access
- 70% of farmers with high school+ education have smartphones
- **60% of consumer expenditure still in cash** even in 2025

---

## 2.4 Progressive Disclosure vs Upfront Training

### Research Verdict: Progressive Disclosure Wins

From Nielsen Norman Group ([NN/g](https://www.nngroup.com/articles/progressive-disclosure/)) and India-specific UX research ([Google Design](https://design.google/library/connectivity-culture-and-credit), [MeinBhiDesigner](https://medium.com/@meinbhidesigner1/crafting-ux-for-indias-next-billion-digital-users-141b07f55210)):

**Progressive disclosure improves 3 of 5 usability components:** learnability, efficiency, and error rate.

**For rural India specifically:**
- Minimal interface aesthetics from Western design "can't compete for attention" in sensory-rich Indian environments — use vibrant, dense visual design
- Entry-level devices have small screens — progressive disclosure is essential for screen real estate
- "If an app crashes once too often, users won't wait — they go back to cash"
- Dream11's guided progressive onboarding (step-by-step team creation) is cited as an Indian success model

### Recommended Onboarding Flow

```
Phase 1: First Launch (Day 1)
├── Splash screen in detected language (with language selector)
├── 30-second animated video showing core value prop
├── Single-screen registration: Phone number + OTP (that's it)
├── Voice prompt: "Welcome! I am [App Name]. What is your name?"
├── Voice-guided profile: Name, village, how many animals?
└── Immediately show: "Your 3 animals are now registered!"

Phase 2: First Week (Guided by Field Agent)
├── Feature 1: View your animal records (pre-populated from registration)
├── Feature 2: Set vaccination reminder (immediate tangible value)
├── Feature 3: Check market price for milk/fodder
└── Achievement badge: "You completed your first week!"

Phase 3: Week 2-4 (Self-guided with contextual tips)
├── Unlock: Health record logging
├── Unlock: Fodder planning
├── Unlock: Scheme eligibility checker
└── Each unlock triggered by contextual need or field agent suggestion

Phase 4: Month 2+ (Full feature access)
├── Trading/marketplace
├── SHG group features
├── Finance tools (insurance, KCC)
├── Community forum
└── Advanced analytics
```

---

## 2.5 Field-Agent Assisted "Buddy" Onboarding Model

### Research-Backed Intermediary Model

The research strongly supports human intermediaries for rural digital onboarding:

**Government Infrastructure:**
- **PMGDISHA** trained 6.39 crore people, 4.78 crore certified — through 3 lakh+ training centers via Common Service Centers (CSCs) in every panchayat ([PMGDISHA](https://pmgdisha.org/what-is-pmgdisha/))
- Curriculum: 20 hours across 5 modules covering device basics, internet, communications, apps, and digital payments
- Available in 22 scheduled languages + English

**Proven Models:**
- **Digital Green/FarmerChat**: Uses SHGs, FPOs, and frontline workers as onboarding anchors — 350,000 farmers reached
- **Rocket Learning**: Uses Anganwadi workers as digital intermediaries via WhatsApp ([WEF](https://www.weforum.org/stories/2023/12/how-smartphones-can-boost-digital-literacy-among-indias-rural-communities/))
- **Amul**: On-ground cooperative infrastructure from village collection centers upward

### Recommended "Buddy" Onboarding Design

```
Buddy Onboarding Model:

Tier 1 — Village-Level Buddies (Sakhi/Sahayak)
├── Recruited from: SHG leaders, progressive farmers, Anganwadi workers
├── Training: 2-day in-person + ongoing WhatsApp support group
├── Responsibility: Onboard 20-50 farmers in their village
├── Tools: Buddy mode in app (can set up profiles for others)
├── Incentive: ₹50-100 per successful onboarding, monthly buddy leaderboard
└── Ongoing: First point of contact for tech issues

Tier 2 — Block-Level Coordinators
├── Recruited from: NGO field staff, cooperative extension workers
├── Training: 5-day intensive + monthly refresher
├── Responsibility: Support 10-15 village buddies
├── Tools: Coordinator dashboard (onboarding metrics, issue tracking)
└── Incentive: Monthly stipend + performance bonus

Tier 3 — District Champions
├── Recruited from: RDO staff, veterinary officers, cooperative managers
├── Training: Ongoing (train-the-trainer model)
├── Responsibility: Strategic oversight, escalation handling
└── Tools: Full admin panel access for their district
```

**App Features for Buddy Mode:**
- "Setup for someone else" flow — buddy enters details on behalf of farmer
- QR-based farmer ID card printout — physical artifact for the farmer
- Offline buddy onboarding — sync when connectivity available
- Video call escalation to Tier 2/3 for complex issues
- Buddy analytics: how many farmers onboarded, active rate, feature adoption

---

## 2.6 DISHA/PMGDISHA Guidelines Integration

### Aligning with Government Digital Literacy Standards ([NextIAS](https://www.nextias.com/blog/digital-saksharta-abhiyan-disha/))

The platform should incorporate PMGDISHA's training curriculum as a baseline:

**Module Alignment:**
| PMGDISHA Module | Our Platform Feature |
|----------------|---------------------|
| Introduction to digital devices | First-launch guided tour |
| Operating digital devices | Contextual help tooltips |
| Internet concepts | Offline-first design (no internet dependency) |
| Internet communications | In-app messaging, video calling vet |
| Internet applications | Scheme discovery, market access |
| Digital payments (UPI, AEPS) | Integrated Razorpay payment flows |

**Certification Integration:**
- Users who complete all 4 onboarding phases could receive a "Digital Pashu Mitra" certificate
- Shareable to DigiLocker
- Counts toward PMGDISHA digital literacy metrics for the village

---

# PART 3: SCHEME MANAGEMENT RESEARCH

## 3.1 Key Livestock Schemes to Integrate

### Rashtriya Gokul Mission (RGM)
([DAHD](https://dahd.gov.in/schemes/programmes/rashtriya_gokul_mission), [PIB](https://pib.gov.in/PressReleasePage.aspx?PRID=2112789))

- **Budget**: Rs. 3,400 crore (2021-22 to 2025-26)
- **Relevant Features**:
  - Free Artificial Insemination at doorstep (NAIP) — 605 districts, 8.39 crore animals
  - 35% capital cost assistance for Heifer Rearing Centres
  - 3% interest subvention on loans for High Genetic Merit IVF heifers
  - IVF labs under State Livestock Boards (22 labs, 2,541+ HGM calves)
- **Platform Integration**: AI service booking, breeding record tracking, IVF program enrollment

### National Livestock Mission (NLM)
([DAHD](https://dahd.gov.in/schemes/programmes/national_livestock_mission))

- **Budget**: Rs. 2,300 crore
- **Livestock Insurance Component**:
  - Premium subsidy: 60:40 or 90:10 (Centre:State), beneficiary pays 15%
  - Max premium: 4.5% of sum insured
  - Max 5 animals per household (50 for sheep/goats/pigs/rabbits)
- **Platform Integration**: Insurance enrollment, premium calculation, claim filing

### Kisan Credit Card (KCC) for Animal Husbandry
([DAHD KCC](https://dahd.gov.in/division/kcc), [BankBazaar](https://www.bankbazaar.com/pashu-kisan-credit-card.html))

- **Interest Rate**: 4% (subsidized)
- **Loan Limit**: Up to Rs. 3 lakh
- **Repayment**: 5-year period
- **Target**: All dairy farmers of Milk Cooperatives and Milk Producer Companies
- **Platform Integration**: KCC application tracking, loan utilization monitoring, repayment reminders

### PMFBY (Crop Insurance — Livestock Adaptation)
([PMFBY](https://pmfby.gov.in/))

- **Farmer Premium**: 1-2% of sum insured (50:50 Centre:State subsidy for remainder)
- **Coverage**: Natural calamities, disease outbreaks, adverse weather
- **Platform Integration**: Claim filing with photo/video evidence, weather data integration

### Pashu Kisan Credit Card
([Krishi Jagran](https://krishijagran.com/animal-husbandry/pashu-kisan-credit-card-govt-is-giving-70-subsidy-on-insurance-installment-how-to-apply-important-documents-eligibility/))

- **Insurance subsidy**: 70% government subsidy on insurance premium installments
- **Eligibility**: Livestock owners with valid Aadhaar and bank account
- **Documents**: Aadhaar, PAN, passport photos, animal details, bank passbook
- **Platform Integration**: Document collection, eligibility check, application submission

---

## 3.2 Government System Integrations

### DigiLocker Integration
([API Setu](https://apisetu.gov.in/digilocker), [FRSLABS Guide](https://www.frslabs.com/frsblog/2023/10/12/digilocker-how-to-integrate-digilocker-api-into-your-web-or-mobile-app-for-kyc/))

**Technical Integration:**
- Requires DigiLocker partnership registration → get clientId + clientSecret
- **Issuer API** (v1.13): For our platform to issue certificates to DigiLocker (e.g., vaccination certificates, animal registration, digital literacy certificate)
- **Requester API**: For our platform to pull documents from user's DigiLocker (Aadhaar, PAN, land records, cooperative membership)
- **Auth Flow**: Aadhaar + OTP → access token → document URI → fetch/parse XML to JSON
- **Security**: Must validate name + DOB match between DigiLocker params and certificate

**Use Cases for Our Platform:**
1. KYC: Pull Aadhaar, PAN from DigiLocker during registration
2. Scheme eligibility: Pull caste certificate, income certificate, land records
3. Issue: Animal health certificates, vaccination records, training certificates
4. Store: Insurance policies, loan documents, scheme approval letters

### PM-KISAN / DBT Integration
([PFMS](https://pfms.nic.in/SitePages/about-Verticals-DBT.aspx), [IMPRI](https://www.impriindia.com/insights/dbt-2-0-transforming-welfare-delivery/))

**DBT Architecture:**
- PFMS (Public Financial Management System) is the backbone for all DBT
- JAM Trinity (Jan Dhan + Aadhaar + Mobile) enables targeted transfers
- Aadhaar-based de-duplication eliminated 2.1 crore fake beneficiaries, saving Rs. 22,106 crore in PM-KISAN alone

**Platform Integration Points:**
- Aadhaar seeding: Link user's Aadhaar to bank account for DBT readiness
- PFMS status check: Track disbursement status for scheme payments
- Beneficiary validation: Cross-check eligibility against SECC/Aadhaar data
- Payment confirmation: Receive callback when DBT reaches farmer's account

### Assam DIDS as Reference Architecture
([PwC Case Study](https://www.pwc.in/case-studies/assam-digital-infrastructure-dbt-schemes.html))

Assam's Digital Infrastructure for DBT Schemes (DIDS) is the best reference model:
- Social registry of 2.34 crore citizens
- 12+ schemes integrated
- Reduced verification from 3 months to 3 weeks
- Reduced disbursement from 25 days to 7 days
- Identified 2.3% duplicate beneficiaries
- Rs. 350 crore monthly disbursements

---

## 3.3 Scheme Tracking Data Model

### Proposed Database Schema

```sql
-- Core scheme registry
CREATE TABLE schemes (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,              -- "Rashtriya Gokul Mission"
    code VARCHAR(50) UNIQUE NOT NULL,         -- "RGM"
    ministry VARCHAR(255),                    -- "DAHD"
    scheme_type VARCHAR(50),                  -- "central", "state", "centrally_sponsored"
    description TEXT,
    eligibility_rules JSONB,                  -- Machine-readable eligibility criteria
    benefits JSONB,                           -- Structured benefit details
    required_documents TEXT[],                -- ["aadhaar", "caste_certificate", "land_record"]
    max_beneficiaries_per_household INT,
    budget_allocation_crore DECIMAL(12,2),
    valid_from DATE,
    valid_to DATE,
    status VARCHAR(20) DEFAULT 'active',      -- active, suspended, expired
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Eligibility criteria (normalized)
CREATE TABLE scheme_eligibility_criteria (
    id UUID PRIMARY KEY,
    scheme_id UUID REFERENCES schemes(id),
    criterion_type VARCHAR(50),               -- "income", "caste", "gender", "land_holding", "animal_count"
    operator VARCHAR(10),                     -- "<=", ">=", "=", "IN", "BETWEEN"
    value JSONB,                              -- {"max": 200000} or {"values": ["SC", "ST", "OBC"]}
    is_mandatory BOOLEAN DEFAULT true,
    priority INT DEFAULT 0                    -- For tie-breaking when oversubscribed
);

-- Farmer scheme applications
CREATE TABLE scheme_applications (
    id UUID PRIMARY KEY,
    scheme_id UUID REFERENCES schemes(id),
    farmer_id UUID REFERENCES farmers(id),
    application_number VARCHAR(50) UNIQUE,    -- Auto-generated, human-readable
    status VARCHAR(30) NOT NULL,              -- See lifecycle below
    applied_via VARCHAR(20),                  -- "app", "csc", "field_agent", "portal"
    field_agent_id UUID,                      -- If assisted application
    eligibility_check_result JSONB,           -- Automated check results
    documents_submitted JSONB,                -- {doc_type: {uri, verified, verified_by, verified_at}}
    rejection_reason TEXT,
    approved_by UUID,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Application status lifecycle:
-- draft → submitted → documents_pending → under_review →
-- eligible → approved → disbursement_initiated → disbursed → completed
-- (at any stage) → rejected / returned_for_correction

-- Disbursement tracking
CREATE TABLE scheme_disbursements (
    id UUID PRIMARY KEY,
    application_id UUID REFERENCES scheme_applications(id),
    installment_number INT DEFAULT 1,
    amount DECIMAL(12,2) NOT NULL,
    disbursement_mode VARCHAR(20),            -- "dbt", "cheque", "in_kind"
    pfms_transaction_id VARCHAR(100),         -- PFMS reference
    bank_account_id UUID,
    dbt_status VARCHAR(30),                   -- "initiated", "processing", "credited", "failed", "reversed"
    credited_at TIMESTAMP,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit trail (immutable)
CREATE TABLE scheme_audit_log (
    id UUID PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,         -- "application", "disbursement", "eligibility_check"
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,              -- "created", "status_changed", "document_verified", etc.
    old_value JSONB,
    new_value JSONB,
    performed_by UUID NOT NULL,
    performed_by_role VARCHAR(50),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Document verification tracking
CREATE TABLE scheme_documents (
    id UUID PRIMARY KEY,
    application_id UUID REFERENCES scheme_applications(id),
    document_type VARCHAR(50),                -- "aadhaar", "caste_certificate", "income_certificate"
    source VARCHAR(30),                       -- "digilocker", "upload", "field_verification"
    digilocker_uri VARCHAR(500),
    file_path VARCHAR(500),
    verification_status VARCHAR(20),          -- "pending", "verified", "rejected", "expired"
    verified_by UUID,
    verified_at TIMESTAMP,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Scheme-specific benefit tracking (e.g., animals insured under NLM)
CREATE TABLE scheme_benefits_received (
    id UUID PRIMARY KEY,
    application_id UUID REFERENCES scheme_applications(id),
    benefit_type VARCHAR(50),                 -- "insurance_premium_subsidy", "ai_service", "heifer_subsidy"
    benefit_description TEXT,
    monetary_value DECIMAL(12,2),
    in_kind_description TEXT,
    delivered_at TIMESTAMP,
    delivery_proof JSONB,                     -- photos, signatures, GPS location
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_applications_farmer ON scheme_applications(farmer_id);
CREATE INDEX idx_applications_scheme ON scheme_applications(scheme_id);
CREATE INDEX idx_applications_status ON scheme_applications(status);
CREATE INDEX idx_disbursements_dbt_status ON scheme_disbursements(dbt_status);
CREATE INDEX idx_audit_entity ON scheme_audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_timestamp ON scheme_audit_log(created_at);
```

### Application Lifecycle State Machine

```
                    ┌─────────────┐
                    │    draft     │ (farmer starts, can save and return)
                    └──────┬──────┘
                           │ submit
                    ┌──────▼──────┐
                    │  submitted  │
                    └──────┬──────┘
                           │ auto-check documents
               ┌───────────┴───────────┐
               │                       │
        ┌──────▼──────┐    ┌───────────▼───────────┐
        │ docs_pending │    │    under_review        │
        └──────┬──────┘    └───────────┬───────────┘
               │ docs uploaded         │ manual review
               └───────────┬───────────┘
                           │
               ┌───────────┴───────────┐
               │                       │
        ┌──────▼──────┐    ┌───────────▼───────────┐
        │   eligible  │    │  returned_for_         │
        └──────┬──────┘    │  correction            │
               │           └───────────┬───────────┘
               │ approve               │ (back to submitted)
        ┌──────▼──────┐
        │  approved   │──────────────┐
        └──────┬──────┘              │ reject at any stage
               │ initiate            │
        ┌──────▼──────────────┐  ┌───▼───────┐
        │ disbursement_       │  │ rejected  │
        │ initiated           │  └───────────┘
        └──────┬──────────────┘
               │ DBT confirmed
        ┌──────▼──────┐
        │  disbursed  │
        └──────┬──────┘
               │ all installments done
        ┌──────▼──────┐
        │  completed  │
        └─────────────┘
```

---

# PART 4: PRACTICAL RECOMMENDATIONS

## 4.1 Admin Panel — Build Priorities

**Phase 1 (Sprint deliverable — design only):**
- Role hierarchy and permission matrix (documented above)
- Dashboard wireframes: operational metrics, GIS coverage map, scheme utilization
- Report templates: NABARD OSS format, scheme beneficiary reports
- User management flows: registration approval, role assignment, geographic scoping

**Phase 2 (MVP build — months 1-3):**
- Refine + Next.js + Material UI admin shell
- User management with RBAC (farmer, vet, coordinator, admin)
- Animal registration and health record management
- Basic reporting (CSV/PDF export)
- Scheme application review workflow

**Phase 3 (Scale — months 4-6):**
- GIS-based dashboards (Leaflet/MapLibre)
- NABARD-compliant reporting module
- DigiLocker integration for document verification
- DBT tracking integration with PFMS
- Advanced analytics and ML insights

## 4.2 Onboarding — Build Priorities

**Phase 1 (Sprint deliverable — design only):**
- Onboarding flow wireframes (4-phase progressive disclosure)
- Buddy onboarding model documentation
- Voice interaction scripts in Kannada
- Persona-based user journey maps (low-literacy woman farmer, progressive male farmer, SHG leader)

**Phase 2 (MVP build — months 1-3):**
- Phone + OTP registration
- Voice-guided profile creation (Sarvam AI integration)
- Offline-capable onboarding flow
- Buddy mode: "setup for someone else"
- First 3 features unlocked progressively

**Phase 3 (Scale — months 4-6):**
- Full PMGDISHA-aligned digital literacy tracking
- QR-based farmer ID cards
- Video call escalation to district champions
- Gamification (badges, levels, leaderboards)
- Auto-generated training certificates → DigiLocker

## 4.3 Scheme Management — Build Priorities

**Phase 1 (Sprint deliverable — design only):**
- Scheme data model (documented above)
- Eligibility rules engine design
- Application lifecycle state machine
- Integration architecture for DigiLocker, PFMS, DBT

**Phase 2 (MVP build — months 1-3):**
- Scheme registry (top 5 schemes: RGM, NLM, KCC, Pashu KCC, PMFBY)
- Basic eligibility checker (rule-based)
- Application submission flow
- Document upload and tracking
- Manual disbursement tracking

**Phase 3 (Scale — months 4-6):**
- DigiLocker API integration (pull + issue documents)
- PFMS/DBT integration for disbursement tracking
- Automated eligibility checking against SECC data
- Bulk application processing for SHGs/FPOs
- Audit trail export for CAG/NABARD compliance

---

## Sources

### Admin Panel
- [Digital Transformation of Agricultural Cooperatives](https://farmonaut.com/asia/revolutionizing-indias-agriculture-national-cooperative-database-empowers-rural-development-and-digital-transformation)
- [Amul Supply Chain & ERP](https://logisticsviewpoints.com/2024/10/15/amuls-optimized-supply-chain-driving-global-growth-in-the-dairy-industry/)
- [Amul AI Platform](https://www.artificialintelligence-news.com/news/amul-ai-dairy-farming-platform-india/)
- [e-GOPALA Portal (PIB)](https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=1808244)
- [NDDB e-GOPALA + IMAP](https://www.nddb.coop/node/2246)
- [eNAM Wikipedia](https://en.wikipedia.org/wiki/E-NAM)
- [eNAM Training Manual (PDF)](https://enam.gov.in/web/docs/eNAM%20Portal.pdf)
- [React-Admin vs Refine (Marmelab)](https://marmelab.com/blog/2023/07/04/react-admin-vs-refine.html)
- [Refine Comparison](https://refine.dev/core/docs/further-readings/comparison/)
- [RBAC Design (NocoBase)](https://www.nocobase.com/en/blog/how-to-design-rbac-role-based-access-control-system)
- [Digital Livestock Cybersecurity (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12040926/)
- [NABARD Supervision Department](https://www.nabard.org/about-departments.aspx?id=5&cid=469)
- [NABARD Supervisory Role Report (PDF)](https://www.nabard.org/pdf/2023/supervisory-role-of-nabard-eng.pdf)

### Onboarding
- [AgriApps Bridge Literacy Gaps (GOOD)](https://www.good.is/articles/agricultural-apps-bridge-literacy-gaps-in-india)
- [Voice Design for Rural India (tap2k PDF)](https://tap2k.org/papers/slt4d-patel.pdf)
- [Avaaj Otalo Research (ResearchGate)](https://www.researchgate.net/publication/221518989_Avaaj_Otalo_-_A_field_study_of_an_interactive_voice_forum_for_small_farmers_in_rural_India)
- [FarmerChat / Digital Green (News9Live)](https://www.news9live.com/technology/digital-greens-ai-chatbot-transforms-farming-for-indias-smallholders-2918678)
- [Bharat-VISTAAR (Tribune India)](https://www.tribuneindia.com/news/india/shivraj-chouhan-launches-ai-powered-bharat-vistaar-platform-for-farmers/)
- [Building India's Voice AI Future (People+AI)](https://peopleplus.ai/blog/building-india-s-voice-ai-future)
- [12 Reasons Farmers Don't Use AgriTech (ICTworks)](https://www.ictworks.org/12-reasons-why-farmers-do-not-use-mobile-agritech-services/)
- [Farmer Smartphone Challenges (BharatInclusion)](https://medium.com/bharatinclusion/using-smartphone-based-applications-some-challenges-faced-by-farmers-e51f9e3b73d1)
- [Progressive Disclosure (NN/g)](https://www.nngroup.com/articles/progressive-disclosure/)
- [Google Design: Next Billion Users](https://design.google/library/connectivity-culture-and-credit)
- [Crafting UX for India's Next Billion](https://medium.com/@meinbhidesigner1/crafting-ux-for-indias-next-billion-digital-users-141b07f55210)
- [PhonePe GTM Strategy (upGrowth)](https://upgrowth.in/phonepe-won-india-upi-war-gtm-strategy-teardown/)
- [Google Pay Case Study (DataNext)](https://www.datanext.ai/case-study/google-pay-upi-app/)
- [UI Design for Illiterate Users (SAGE)](https://journals.sagepub.com/doi/full/10.1177/21582440231172741)
- [PMGDISHA Full Guide](https://pmgdisha.org/pmgdisha-full-guide/)
- [DISHA (NextIAS)](https://www.nextias.com/blog/digital-saksharta-abhiyan-disha/)
- [Digital Literacy Rural India (WEF)](https://www.weforum.org/stories/2023/12/how-smartphones-can-boost-digital-literacy-among-indias-rural-communities/)
- [Digital Divide Rural India (Springer)](https://innovation-entrepreneurship.springeropen.com/articles/10.1186/s13731-024-00380-w)

### Schemes & Government Integration
- [Rashtriya Gokul Mission (DAHD)](https://dahd.gov.in/schemes/programmes/rashtriya_gokul_mission)
- [Revised RGM Approval (PIB)](https://pib.gov.in/PressReleasePage.aspx?PRID=2112789)
- [National Livestock Mission (DAHD)](https://dahd.gov.in/schemes/programmes/national_livestock_mission)
- [NLM Free Insurance for Cows (Krishi Jagran)](https://krishijagran.com/news/national-livestock-mission-govt-plans-free-insurance-for-cows-possibility-of-100-subsidy-on-premium/)
- [KCC for Animal Husbandry (DAHD)](https://dahd.gov.in/division/kcc)
- [Pashu KCC (BankBazaar)](https://www.bankbazaar.com/pashu-kisan-credit-card.html)
- [PMFBY Portal](https://pmfby.gov.in/)
- [DigiLocker API Setu](https://apisetu.gov.in/digilocker)
- [DigiLocker Issuer API v1.13 (PDF)](https://cf-media.api-setu.in/resources/DigiLocker-Issuer-APISpecification-v1-13.pdf)
- [PFMS DBT Portal](https://pfms.nic.in/SitePages/about-Verticals-DBT.aspx)
- [DBT 2.0 (IMPRI)](https://www.impriindia.com/insights/dbt-2-0-transforming-welfare-delivery/)
- [Assam DIDS Platform (PwC)](https://www.pwc.in/case-studies/assam-digital-infrastructure-dbt-schemes.html)
- [myScheme National Portal](https://www.myscheme.gov.in/)
