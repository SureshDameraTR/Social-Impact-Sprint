# Indian Dairy Cooperative Technology Landscape: Research Report

**Date:** 2026-03-30
**Purpose:** Map existing digital platforms across Indian dairy cooperatives, identify pain points and gaps, and define PashuRaksha integration opportunities.

---

## 1. Major Cooperative Digital Platforms

### 1.1 Amul / GCMMF (Gujarat) — Most Advanced

**Scale:** 36 lakh+ farmers, 18,500+ villages, 350 lakh liters/day

**Digital Infrastructure:**
- **AMCS (Automatic Milk Collection System):** Developed with Prompt Dairy Tech. Records quantity, FAT%, SNF% in real-time at Village Dairy Cooperative Societies (VDCS). Auto-calculates farmer payment from rate charts. Direct bank deposit. Covers 26,000+ DCS across 12 states.
- **Amul Farmer App:** 10 lakh+ downloads (Android). Digital passbook — daily/monthly/yearly milk data, payment tracking, statistical comparisons, alert messages. Farmers can filter collection data by date.
- **Pashudhan Application:** Veterinary and animal health management, breeding records, integrated with AMCS.
- **Sarlaben AI Assistant (Feb 2026):** Voice-based AI on the Amul Farmer App + phone calls. Real-time guidance on cattle health, vaccination schedules, breeding, feed management, and government schemes. Primary language: Gujarati. Accessible on feature phones via voice call.
- **Massive Data Layer:** 200 crore+ annual milk procurement transactions, veterinary records from 1,200+ doctors covering ~3 crore cattle, ~70 lakh AI (artificial insemination) records/year, ISRO satellite imagery for fodder production.

**Pain Points:**
- Sarlaben is Gujarati-only as of launch — no multi-language support yet.
- System tightly coupled to Amul cooperative structure — not available to non-Amul farmers.
- Feature phone access limited to voice calls; no SMS-based data access for non-smartphone users.

**Sources:** [Amul Farmer AMCS App](https://apps.apple.com/in/app/amul-farmer-amcs/id6466649621) | [Amul AI Sarlaben](https://agronfoodprocessing.com/amul-launches-ai-assistant-sarlaben-to-empower-dairy-farmers-with-24x7-digital-support/) | [Prompt AMCS](https://promptamcs.com/)

---

### 1.2 KMF / Nandini (Karnataka) — Moderate Digitization

**Scale:** 2.7 million+ farmers, 15,981 DCS, 16 district milk unions, ~1 crore liters/day procurement

**Digital Infrastructure:**
- **BAMUL App:** Bangalore Milk Union Ltd. app on Google Play — connects farmers and consumers.
- **KMF Nandini App:** Basic health/nutrition info app developed by ITSPL.
- **Automatic Computerized Milk Collection Units (AMCU):** Installed at DCS level, linked to Bulk Milk Coolers. Claims milk quality "comparable to international standards."
- **QR Code Authentication:** Unique QR codes on Nandini products (ghee sachets first) for consumer anti-counterfeiting via smartphone scan.
- **AI Product Counting:** AI-based counting for milk packets and curd cups in packaging/dispatch — reduces manual checks, improves inventory accuracy.
- **Community Milking Parlours:** Mechanized milking at village level to eliminate mastitis and improve milk quality.

**What's MISSING at KMF:**
- **No unified farmer-facing digital app** with milk data, payments, and health services.
- **No AI-based cattle disease detection** — relies on manual veterinary camps and infertility camps.
- **No digital farmer grievance system** — only toll-free phone (1800 425 8030), email, and WhatsApp.
- **No digital payment passbook** for farmers comparable to Amul's.
- **No voice-based assistance** in Kannada for farmers.
- **No integration with Bharat Pashudhan/INAPH** publicly documented.

**Sources:** [KMF Official](https://www.kmfnandini.coop/) | [BAMUL App](https://play.google.com/store/apps/details?id=com.bamulnandini.dairy&hl=en_IN) | [Nandini AI Counting](https://dairynews.today/news/nandini-introduces-ai-based-product-counting-solution-for-enhanced-efficiency.html)

---

### 1.3 Aavin / TCMPF (Tamil Nadu)

**Scale:** 3.8 lakh+ producers, 34.42 lakh liters/day procurement

**Digital Infrastructure:**
- **Integrated Dairy Management System (IDMS):** Comprehensive computerization platform covering operations, service delivery, and procurement management. Designed to be replicable in other states.
- **Cloud-Based Quality Monitoring:** Monitors quality, quantity, pricing, and temperature control in real-time.
- **Online Milk Sales:** E-commerce capabilities for milk and dairy products.
- **Telegram Outreach:** Digital communication for farmer training and scheme updates.

**What's MISSING at Aavin:**
- No dedicated farmer mobile app found in search results.
- No AI-powered advisory or disease detection.
- No digital payment passbook for farmers.
- Limited public documentation on IDMS capabilities and API availability.

**Sources:** [Aavin IDMS](https://aavin.tn.gov.in/idms) | [Aavin Official](https://aavin.tn.gov.in/)

---

### 1.4 Milma / KCMMF (Kerala)

**Scale:** 3,076 primary societies, 10.4 lakh+ farmer members

**Digital Infrastructure:**
- ICT and mobile-based farmer training.
- Women-centric SHG integration in procurement.
- Solar-powered Bulk Milk Coolers for sustainability.
- State-of-the-art laboratory quality checks at dairies.
- Distinction: highest milk procurement price in India; best microbiological quality.

**What's MISSING at Milma:**
- No farmer-facing mobile app found in search results.
- No public AI/ML initiatives for animal health or advisory.
- Limited digital payment infrastructure documentation.

**Sources:** [Milma Official](https://milma.com/) | [Malabar Milma](https://www.mrcmpu.com/profile.php)

---

### 1.5 Verka / MILKFED (Punjab)

**Digital Infrastructure:**
- Systems & IT department exists within organizational structure.
- Standard cooperative milk procurement operations.

**What's MISSING at Verka:**
- Minimal public digital initiative information available.
- No farmer app or digital advisory system found.

**Sources:** [Verka Official](https://verka.coop/)

---

### 1.6 Mother Dairy (Delhi NCR)

**Note:** Subsidiary of NDDB. Major urban milk distributor. Search results did not surface specific farmer-facing digital tools or cooperative technology platforms — likely because Mother Dairy operates more as a consumer brand than a traditional cooperative structure.

---

## 2. National Government Digital Infrastructure

### 2.1 NDDB AMCS (National)

- Developed by NDDB. Multi-platform, multi-lingual milk collection software.
- Links DCS/Union/Federation/National levels.
- Used by 25+ milk unions across 12 states, covering 23,760+ DCS and 11,01,200+ milk pourers.
- Integrated with financial inclusion (bank account linkage) and mobile informatics.
- **Key fact:** AMCS is the de facto standard for cooperative milk collection digitization in India.

**Sources:** [NDDB AMCS](https://www.nddb.coop/resources/amcs) | [AMCS Portal](https://amcs.nddb.coop/)

### 2.2 NDERP — NDDB Dairy ERP

- Open-source ERP built on Frappe/ERPNext framework.
- Modules: Accounts, Purchase, Inventory, Sales, Production & Quality, HR & Payroll.
- **Integrated with AMCS** — end-to-end from cow to consumer.
- Mobile app (mNDERP) and distributor portal (iNDERP).
- Implemented at: Jharkhand Milk Federation, West Assam Milk Union, Varanasi Milk Union, Karnataka Oil Federation, MRIDA, CALF, North East Dairy Foods.
- GST compliance, cheque printing, bank API integrations.
- **Open-source technology stack** — potentially extensible.

**Sources:** [NDERP Portal](https://nderp.nddb.coop/subpage) | [NDDB ICT](https://beta.nddb.coop/what-we-do/information-and-communication-technology/)

### 2.3 INAPH — Information Network for Animal Productivity & Health

- Desktop/notebook/Android field application for real-time data on Breeding, Nutrition, and Health services.
- Backbone of the National Animal Disease Control Programme (NADCP) — Rs 13,343 crore outlay.
- Individual animal records via ear-tag numbers: vaccination, deworming, disease testing, fertility, treatment, follow-up.
- Pathology laboratory module for disease diagnosis and outbreak confirmation.
- Portal: [inaph.nddb.coop](https://inaph.nddb.coop)

**Sources:** [NDDB INAPH](https://www.nddb.coop/resources/inaph) | [INAPH Health Module](https://www.nddb.org/services/animalhealth/healthmodule)

### 2.4 Bharat Pashudhan / NDLM — National Digital Livestock Mission

- **Pashu Aadhaar:** 12-digit bar-coded ear tag for every animal — 35.96 crore animals tagged, 9.5 crore livestock owners registered, 84 crore+ transactions logged.
- **Modules:** Animal Management (registration, ownership transfer, ear tag change), Animal Health (treatment, vaccination, deworming, disease testing/reporting), Animal Breeding (AI, pregnancy diagnosis, calving).
- **1962 Livestock Owner App:** Farmer-facing app integrated with NDLM database. View registered animals, access government schemes, livestock services. Replaced earlier e-Gopala app.
- **CRITICAL: Open API architecture.** Cloud-based, secure, integrated database on open-source architecture. **API-based integration environment** connecting dairy processors, livestock manufacturers, private software developers, and researchers via **open APIs**.
- **Design pedigree:** iSpirt team (UIDAI Aadhaar designers) mentored the architecture.

**Sources:** [Bharat Pashudhan](https://bharatpashudhan.ndlm.co.in/) | [NDLM Overview](https://delmerindia.com/national-digital-livestock-mission-ndlm-empowering-farmers-through-digital-innovation/)

---

## 3. Dairy Tech Companies Serving Cooperatives

### 3.1 Stellapps Technologies (Bangalore)

**Scale:** 42,000 villages, 3.5 million+ farmers, 14 million liters monitored daily. Revenue: Rs 400 crore.

**Products:**
| Product | Function |
|---------|----------|
| SmartMoo IoT Platform | Data acquisition via sensors in milking systems, wearables, chilling equipment |
| mooON | "Fitbit for cattle" — leg-worn activity tracker. Detects illness (less movement) and ovulation (more movement) |
| smartAMCU | Automated milk collection unit |
| smartCC | Cold chain monitoring |
| ConTrak | Logistics tracking |
| mooPay | Direct digital farmer payments — single-click bank transfers to lakhs of farmers |
| mooFlowERP | Dairy ERP system |
| mooOpt | Route optimization |

**Customers:** Amul, Nandini/KMF, Aavin, Sudha, Milma, Hatsun, Heritage, Dodla, Creamline, Milky Mist.

**mooPay FinTech:** Alternate credit scoring via milk cash flow + cattle vaccination history + deworming compliance. Partnership with India Post Payments Bank (IPPB) for banking at milk collection centers (cash withdrawal, deposits, bill payments, insurance).

**Sources:** [Stellapps/mooPay](http://www.moopay.in/about/) | [Stellapps + IPPB](https://ippbonline.bank.in/documents/31498/0/Stellapps+Ties+up+with+IPPB_Feb+24_Final+V.pdf) | [Business India](https://businessindia.co/magazine/corporate-report/from-software-to-dairy-stellapps-shows-the-milky-way)

### 3.2 Prompt Dairy Tech (Ahmedabad)

**Scale:** 28 states, 70,000+ villages.

**Products:**
- **AMCS Software:** Core milk collection software — quantity, FAT, SNF, water proportion, milk density. Integrates with RFID/smart card/barcode for farmer identification. Cloud analytics.
- **MU Portal:** Real-time analytics for milk unions — collection activities, farmer/employee management.
- **Farmers App:** Free Android app — digital passbook, daily/monthly/yearly milk data.
- **VDCS App:** Village society daily analytics.
- **Transporter App:** Truck sheet data, dipstick image capture.
- **Hardware:** DPU-based (basic) and PC-based (advanced accounting) AMCS units. Solar-powered option. Integrates with ERP, Oracle, SAP.

**Key partnership:** Technology partner for Amul's AMCS.

**Sources:** [Prompt Dairy Tech](https://www.promptdairytech.com/) | [Prompt AMCS](https://promptamcs.com/)

### 3.3 Mr. Milkman (now Dairy.com India)

- Last-mile dairy supply chain SaaS platform.
- 60+ Indian dairy brands as clients.
- Customer subscription management, delivery optimization, payment processing.
- Acquired 100% by Dairy.com (USA) in October 2021 — first dairy/agri-tech acquisition in India by an international player.
- Clients include: Akshayakalpa, Amlaan, Gyan Dairy, House of Nanak, Milk Mantra, Raw Pressery, Yakult.

**Sources:** [Mr. Milkman/Dairy.com](https://www.indianretailer.com/news/dairy-com-acquires-100-stake-in-dairy-tech-startup-mr-milkman.n11755)

### 3.4 Country Delight

- Farm-to-doorstep subscription model.
- Direct farmer engagement — premium pricing, ethical procurement.
- Cold chain and quality testing at farmer location.
- Mobile app for consumer subscription management.
- Focus: eliminating adulteration, improving farmer cash flow.

### 3.5 Other Notable Players

| Company | Focus |
|---------|-------|
| IndiFOSS | MilkoScreen AMCS — milk quality testing and adulteration screening. 10,000+ units deployed. |
| FOSS | Milk analysis instruments, adulteration detection |
| DeLaval | Robotic milking systems, voluntary milking system (VMS) sensors |
| SomaDetect | Real-time milk quality sensors (fat, somatic cell count) |

---

## 4. Critical Pain Points in Current Systems

### 4.1 Technology Access Gaps

| Pain Point | Severity | Details |
|------------|----------|---------|
| **60% milk in unorganized sector** | Critical | Handled by middlemen with zero digital infrastructure. Cooperatives cover only 40% of surplus milk. |
| **Low smartphone penetration** | High | Most small/marginal dairy farmers use feature phones. Apps require Android smartphones. |
| **No internet in remote areas** | High | Cloud-based systems like AMCS fail without connectivity. No offline-first solutions. |
| **Digital literacy gap** | High | Especially among women farmers (who are majority of dairy workforce). |
| **Language barriers** | High | Most apps are English or Hindi only. Kannada, Tamil, Telugu, Malayalam poorly served. |

### 4.2 Milk Collection & Quality

| Pain Point | Severity | Details |
|------------|----------|---------|
| **Manual data entry errors** | High | Many DCS still use manual ledgers or basic DPU units without cloud sync. |
| **Adulteration detection gaps** | Critical | 70.6% adulteration rate in unregulated samples (2024 study). Standard tests being outpaced by sophisticated adulterants. |
| **No portable testing in rural areas** | High | Advanced testing equipment concentrated in urban/district labs. |
| **Cold chain breaks** | High | Infrastructure gaps between farmer doorstep and BMC. Significant milk wastage. |

### 4.3 Financial & Payment Issues

| Pain Point | Severity | Details |
|------------|----------|---------|
| **Payment delays** | High | Many cooperatives still process payments in 10-15 day cycles, not real-time. |
| **No bank accounts** | Medium | Many smallholder farmers lack bank accounts for digital payments. |
| **No credit history** | High | Banks cannot assess farmer creditworthiness without data. |
| **Non-transparent pricing** | High | Farmers cannot independently verify FAT/SNF readings and rate calculations. |

### 4.4 Animal Health & Veterinary Services

| Pain Point | Severity | Details |
|------------|----------|---------|
| **Inadequate veterinary reach** | Critical | Government vets cover huge territories. Average response time measured in days, not hours. |
| **No digital disease reporting** | High | Most disease surveillance is paper-based at village level. |
| **Vaccination record gaps** | High | Paper records lost/damaged. No linkage between animal identity and vaccination history for most cooperative farmers. |
| **Climate-driven disease spikes** | High | 10-30% yield decline in northern states from heatwaves. Lumpy Skin Disease caused 10% output drop in 2022-23. |
| **Mastitis losses** | High | Rs 14,000 crore annual losses from mastitis alone. |

### 4.5 Data & Integration Issues

| Pain Point | Severity | Details |
|------------|----------|---------|
| **Siloed systems** | Critical | AMCS, INAPH, NDERP, state cooperatives all maintain separate databases. No unified farmer view. |
| **No standard data formats** | High | Each cooperative system uses proprietary formats. No interoperability. |
| **State-level fragmentation** | High | Each state cooperative (KMF, Aavin, Milma, etc.) operates independently with different tech stacks. |
| **Paper-to-digital gap** | High | Many DCS operate in hybrid paper+digital mode with data quality issues. |

---

## 5. PashuRaksha Integration Opportunities & Feature Recommendations

### 5.1 Bharat Pashudhan / NDLM Integration (HIGHEST PRIORITY)

**Why:** Open API architecture, 35.96 crore animals already tagged with Pashu Aadhaar, government mandate for digital livestock identity.

**How PashuRaksha should integrate:**
- **Use Pashu Aadhaar as the primary animal identifier.** The `api-animals` module already has Pashu Aadhaar support (proposal.md line 22: "Animal CRUD with Pashu Aadhaar support"). This is the right approach.
- **Pull animal registration data** from Bharat Pashudhan via their open APIs — owner, breed, age, vaccination history.
- **Push health events** (disease reports, vaccinations, treatments) back to the NDLM database so the national disease surveillance system has village-level data from PashuRaksha users.
- **Sync breeding records** — AI (artificial insemination) records, pregnancy diagnosis, calving data.

**Implementation notes:**
- Bharat Pashudhan uses open-source architecture designed by iSpirt (Aadhaar team).
- API documentation likely available at [bharatpashudhan.ndlm.co.in](https://bharatpashudhan.ndlm.co.in/).
- Contact NDDB for API access: anand@nddb.coop, Tel: 91-2692-260148.

### 5.2 NDDB AMCS Data Bridge

**Why:** AMCS is the de facto standard for milk collection digitization (25+ unions, 12 states, 23,760+ DCS).

**How PashuRaksha should integrate:**
- **Do NOT replace AMCS.** Cooperatives will not abandon their AMCS investment. Instead, position PashuRaksha as a **farmer-side companion** that adds health/advisory/marketplace capabilities alongside AMCS milk data.
- **Read AMCS milk collection data** to populate PashuRaksha's milk history and income dashboards. AMCS already sends SMS notifications to farmers — PashuRaksha could pull this data via the farmer's consent.
- **NDERP integration:** NDERP is built on Frappe/ERPNext (open source, Python). PashuRaksha could integrate via ERPNext REST APIs for financial data, inventory, and milk procurement records.

### 5.3 Stellapps Ecosystem Bridge

**Why:** Stellapps already serves Amul, KMF, Aavin, Milma — the exact cooperatives PashuRaksha would target. 42,000 villages digitized.

**How PashuRaksha should integrate:**
- **mooPay for payments:** Instead of building a payment system, integrate with mooPay for financial services and credit scoring.
- **mooON health data:** If a farmer's cattle wear mooON wearables, PashuRaksha's disease triage engine could consume activity data to improve predictions (less movement = potential illness).
- **smartCC cold chain data:** Pull BMC temperature data into PashuRaksha's admin dashboard for cooperative supervisors.

### 5.4 Features PashuRaksha Must Include (Competitive Positioning)

Based on the gap analysis, these features position PashuRaksha as the **missing layer** in the cooperative tech stack:

#### A. Offline-First Architecture (CRITICAL GAP)
- **None of the current cooperative apps work offline.** AMCS, NDERP, Stellapps all require connectivity.
- PashuRaksha must cache milk records, health events, and vaccination data locally and sync when connected.
- This alone makes PashuRaksha viable in the 60% unorganized sector that cooperatives cannot reach.

#### B. Kannada Voice-First Interface (KMF/NANDINI GAP)
- Amul has Sarlaben (Gujarati voice AI). **KMF has nothing comparable in Kannada.**
- PashuRaksha already has Sarvam AI Kannada STT in its spec. This is a direct competitive advantage for Karnataka.
- Extend to Tamil (Aavin), Malayalam (Milma), Punjabi (Verka) for multi-state deployment.

#### C. Rule-Based Disease Triage (UNIQUE DIFFERENTIATOR)
- Amul's Sarlaben provides advisory but is **AI/LLM-based** — a black box.
- PashuRaksha's rule-based triage (50+ ICAR-IVRI/NDDB rules) is **transparent and auditable** — critical for government/cooperative trust.
- No other cooperative app offers symptom-based cattle disease triage with risk scoring.
- Add: **Integration with INAPH animal health module** to push treatment records to the national database.

#### D. Multi-Species Support (UNDERSERVED MARKET)
- All cooperative systems focus exclusively on cattle/buffalo (milk).
- PashuRaksha already specs goat, sheep, and poultry. This serves the **70% of rural households** that have mixed livestock.
- This is particularly relevant for SHGs where women manage goats/poultry alongside dairy.

#### E. SHG/NABARD Integration (UNIQUE TO PASHURAKSHA)
- No existing cooperative app has SHG management or NABARD Panchsutra scoring.
- This fills a critical gap for women's cooperative groups that are the backbone of dairy at village level.

#### F. Farmer Grievance & Transparency Module (KMF GAP)
- KMF has only phone/email grievance. No digital tracking.
- PashuRaksha should add: digital complaint filing, status tracking, cooperative response SLA, escalation to union level.
- This builds farmer trust and gives cooperatives accountability data.

#### G. Milk Quality Verification (TRUST GAP)
- Current systems: cooperative-controlled testing. Farmer has no independent verification.
- PashuRaksha feature: photograph-based milk record with timestamp + GPS, allowing farmers to maintain their own records to cross-check cooperative readings.
- Future: Bluetooth integration with portable milk analyzers for independent FAT/SNF testing.

### 5.5 Data Format Recommendations

Based on the ecosystem analysis:

| System | Data Format | Integration Method |
|--------|-------------|-------------------|
| Bharat Pashudhan | REST API (open-source, API-first) | Direct API integration via Pashu Aadhaar |
| NDDB AMCS | Proprietary (NDDB-developed) | SMS/notification parsing or NDERP bridge |
| NDERP | Frappe/ERPNext REST API | Standard ERPNext API calls |
| Stellapps | Proprietary SaaS APIs | Partnership/API agreement required |
| Prompt AMCS | Cloud API + hardware integration | API agreement with Prompt Group |
| INAPH | NDDB-developed, ear-tag-based | Via NDLM/Bharat Pashudhan APIs |

### 5.6 Recommended Integration Priority

| Priority | Integration | Effort | Impact |
|----------|-------------|--------|--------|
| P0 | Bharat Pashudhan / Pashu Aadhaar | Medium | National animal ID linkage — prerequisite for everything else |
| P0 | Offline-first architecture | High | Only way to serve 60% unorganized sector |
| P1 | INAPH health data sync | Medium | Disease surveillance, vaccination records |
| P1 | Kannada voice interface (Sarvam AI) | Low (already specced) | KMF/Karnataka market differentiator |
| P2 | NDERP/ERPNext bridge | Medium | Financial and procurement data |
| P2 | Stellapps mooPay | Low | Payment gateway, credit scoring |
| P3 | AMCS milk data read | High | Cooperative milk collection records |
| P3 | Bluetooth milk analyzer | High | Independent quality verification |

---

## 6. Competitive Positioning Summary

```
WHAT EXISTS                          WHERE PASHURAKSHA FITS
==========================           ==============================
AMCS → Milk collection recording     PashuRaksha → Animal health + advisory
NDERP → Cooperative ERP              PashuRaksha → Farmer-side companion app
Sarlaben → Gujarati AI advisory      PashuRaksha → Kannada rule-based triage
Stellapps → IoT + payments           PashuRaksha → Offline-first + multi-species
Bharat Pashudhan → Animal ID         PashuRaksha → Consumes Pashu Aadhaar
INAPH → National health records      PashuRaksha → Village-level data contributor
```

**PashuRaksha's unique value proposition:**
The cooperative ecosystem has strong **collection-to-consumer** tech (AMCS, NDERP, Stellapps) but weak **farmer-to-collection** tech. PashuRaksha fills the gap between the farmer's doorstep and the collection center — health management, disease triage, multi-species support, SHG integration, voice-first Kannada interface, and offline capability. It does not compete with AMCS/NDERP but complements them by giving farmers tools that cooperatives do not provide.

---

## 7. Key Contacts & Resources

| Resource | URL/Contact |
|----------|-------------|
| Bharat Pashudhan Portal | https://bharatpashudhan.ndlm.co.in/ |
| NDDB AMCS Portal | https://amcs.nddb.coop/ |
| NDERP Portal | https://nderp.nddb.coop/subpage |
| INAPH Portal | https://inaph.nddb.coop |
| NDDB Contact | anand@nddb.coop, Tel: 91-2692-260148 |
| Stellapps | http://www.moopay.in/about/ |
| Prompt Dairy Tech | https://www.promptdairytech.com/ |
| KMF Official | https://www.kmfnandini.coop/ |
| Aavin IDMS | https://aavin.tn.gov.in/idms |
| 1962 Livestock Owner App | Google Play (integrated with NDLM) |
