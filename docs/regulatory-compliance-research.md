# Indian Regulatory Compliance Research for PashuRaksha

> **Research Date:** March 30, 2026
> **Scope:** 15 regulatory areas affecting agricultural technology platforms and livestock management systems in India
> **App:** PashuRaksha — Farmer-Centric Animal Husbandry ERP & Telemedicine Platform

---

## Table of Contents

1. [DPDP Act 2023 (Digital Personal Data Protection)](#1-dpdp-act-2023)
2. [INAPH / Pashu Aadhaar Integration](#2-inaph--pashu-aadhaar)
3. [NDDB Dairy Digitization Guidelines](#3-nddb-dairy-digitization)
4. [National Livestock Mission (NLM)](#4-national-livestock-mission)
5. [e-Gopala App Analysis](#5-e-gopala-app-analysis)
6. [NABARD SHG Digitization & Panchsutra](#6-nabard-shg-digitization--panchsutra)
7. [FSSAI Food Safety Requirements](#7-fssai-food-safety-requirements)
8. [APMC Act & e-NAM Requirements](#8-apmc-act--e-nam)
9. [Aadhaar-Based Farmer Identity (AgriStack)](#9-aadhaar-based-farmer-identity)
10. [PM-Kisan & Scheme Integration](#10-pm-kisan--scheme-integration)
11. [Karnataka State Digital Initiatives](#11-karnataka-state-initiatives)
12. [ISO 27001 Data Security](#12-iso-27001-data-security)
13. [RBI Digital Payments & UPI](#13-rbi-digital-payments--upi)
14. [Veterinary Telemedicine Guidelines](#14-veterinary-telemedicine-guidelines)
15. [Upcoming Regulations (2026-2027)](#15-upcoming-regulations)
16. [Master Compliance Checklist](#16-master-compliance-checklist)

---

## 1. DPDP Act 2023

### What It Requires

The Digital Personal Data Protection Act, 2023 (enacted August 2023) with DPDP Rules 2025 (notified November 14, 2025) establishes India's legal framework for digital personal data protection. It applies to **all platforms processing digital personal data** collected online or offline-then-digitized within India.

**Core obligations:**

| Requirement | Detail |
|-------------|--------|
| **Explicit consent** | Free, informed, specific consent before processing any personal data |
| **Multilingual consent notices** | Must be available in all 22 languages of the 8th Schedule of the Constitution |
| **Purpose limitation** | Data collection only for stated, lawful purposes |
| **Data minimization** | Only collect what is necessary for the specified service |
| **Easy withdrawal** | Farmers must withdraw consent as easily as they gave it |
| **Breach notification** | Immediate intimation to data principals + detailed report to the Board within 72 hours |
| **Data security** | Encryption, masking, and security safeguards mandatory |
| **Data principal rights** | Rights to access, correct, update, erase data, and nominate representatives |
| **Legacy data** | Retroactive notification and consent opportunity for pre-Act data |
| **Consent Managers** | Optional but creates additional obligations if used (registration process effective November 13, 2026) |

### How It Affects PashuRaksha

PashuRaksha collects extensive farmer personal data:
- Name, Aadhaar number, phone number, location
- Bank account details (for payments)
- Livestock ownership records
- Health/veterinary consultation records
- Financial transaction data (milk sales, marketplace)
- SHG membership and meeting records

**All of this is "digital personal data" under the Act.** PashuRaksha is a **Data Fiduciary** under the DPDP Act.

### What We Must Implement

1. **Consent management system** with itemized data use descriptions
2. **Multilingual consent notices** — minimum Kannada + Hindi + English for Karnataka deployment; all 22 scheduled languages for pan-India
3. **Granular consent controls** — separate consent for each processing purpose (health records, marketplace, payments, scheme integration)
4. **Consent withdrawal mechanism** — one-tap withdrawal in the app
5. **Data encryption** at rest and in transit
6. **72-hour breach notification pipeline** — automated detection + notification system
7. **Data Principal rights portal** — self-service access, correction, deletion
8. **Privacy policy** in simple language across all supported languages
9. **Data retention policy** — automatic deletion when purpose is fulfilled
10. **Data Processing Agreements** with all third-party processors (Sarvam AI, payment gateways, etc.)

### Penalties

| Violation | Maximum Fine |
|-----------|-------------|
| Failing to implement reasonable security safeguards | **INR 250 crore** (~$30M) |
| Failure in breach notification | **INR 200 crore** |
| Violations concerning children's data | **INR 200 crore** |
| Non-compliance by Significant Data Fiduciaries | **INR 150 crore** |
| Consent violations, data principal rights violations | **INR 50 crore per instance** |
| Non-compliance with Board orders | **INR 20 crore** |

Fines are **per instance** and can stack.

### Timeline

| Milestone | Date |
|-----------|------|
| DPDP Rules notified | November 14, 2025 |
| Consent Manager registration process | November 13, 2026 |
| Startup/MSME exemption provisions | May 13, 2027 |
| **Penalty enforcement begins** | **May 13, 2027** |
| Full compliance expected | Mid-2027 |

**For PashuRaksha:** Begin compliance now. Core consent, security, and grievance mechanisms must be in place before launch.

---

## 2. INAPH / Pashu Aadhaar

### What It Requires

The Information Network for Animal Productivity and Health (INAPH), managed by NDDB, assigns a unique **12-digit barcoded ear tag** (Pashu Aadhaar) to every livestock animal. Over **35.68 crore** livestock have been tagged as of November 2025.

**Data captured per animal:**
- Species, breed, pedigree
- Calving, vaccination, milk production records
- Breeding (AI), treatment, general health services
- Owner's Aadhaar number (linked to animal tag)

The system is **open-source and API-integrated**, designed for real-time data recording by veterinarians, paravets, and farmers.

### How It Affects PashuRaksha

PashuRaksha's livestock management module **must integrate with Pashu Aadhaar**. Without this integration:
- Animals cannot be uniquely identified in the national system
- Insurance claims, subsidy applications, and scheme eligibility checks will fail
- Traceability for disease control (FMD vaccination) breaks down

### What We Must Implement

1. **Pashu Aadhaar lookup/validation** — accept 12-digit animal ID as primary identifier
2. **INAPH API integration** — read animal records (breed, vaccination history, AI records)
3. **Bidirectional data sync** — push health events, treatments, and vaccination records back to INAPH/Bharat Pashudhan
4. **Ear tag scanner support** — barcode scanning via mobile camera for quick animal lookup
5. **Owner-animal linking** — validate farmer Aadhaar against animal ownership records
6. **Offline capability** — field workers must record data offline and sync when connected (rural connectivity is unreliable)
7. **Bharat Pashudhan App interoperability** — ensure data compatibility with the government's field workforce app

### Penalties

No direct financial penalty for non-integration, but:
- Animals without Pashu Aadhaar are ineligible for government schemes and insurance
- Non-integrated platforms will be sidelined as NDLM becomes the mandatory digital backbone

### Timeline

- System is already live and mandatory for all bovines
- **95% of India's 303 million bovines** already tagged
- Integration should be implemented before launch

---

## 3. NDDB Dairy Digitization

### What It Requires

NDDB operates a comprehensive digital ecosystem for dairy:

| Platform | Function |
|----------|----------|
| **AMCS** (Automatic Milk Collection System) | Digital milk collection — quantity, quality, fat content, instant payment |
| **NDERP** (NDDB Dairy ERP) | End-to-end dairy ERP — finance, inventory, sales, manufacturing, HR |
| **i-DIS** (Internet-based Dairy Information System) | Centralized data for procurement, sales, manufacturing across cooperatives |
| **INAPH** | Animal productivity and health records |
| **SSMS** (Semen Station Management System) | Bull lifecycle, semen production, quality control |
| **GIS Route Optimization** | Milk collection/distribution route planning |

AMCS is operational in **12 states/UTs**, serving **26,000+ societies** and **17.3 lakh farmers** across 54 milk unions.

### How It Affects PashuRaksha

PashuRaksha's milk center management module overlaps with AMCS. We must either:
- **Integrate with AMCS** (preferred — leverage existing infrastructure)
- **Be compatible with AMCS data formats** (minimum — enable data export/import)

### What We Must Implement

1. **AMCS-compatible data formats** for milk collection records (quantity, fat content, SNF, payment)
2. **DCS Application compatibility** — ensure our data can feed into NDDB's multilingual DCS Application
3. **Digital passbook interoperability** — farmer payment records should mirror AMCS digital passbook format
4. **i-DIS reporting capability** — generate reports in i-DIS format for cooperative federation reporting
5. **INAPH integration** (covered in Section 2)

### Penalties

No direct penalties, but dairy cooperatives receiving NDDB support must use NDDB-approved digital systems. Non-compatible platforms will be excluded from cooperative ecosystem.

### Timeline

- AMCS is actively expanding to new states
- Integration should be planned for Phase 2 (post-MVP)

---

## 4. National Livestock Mission

### What It Requires

NLM 2.0 Operational Guidelines (January 2025) cover:
- Entrepreneurship promotion in livestock sector
- Per-animal productivity enhancement
- Digital portal-based application and approval process
- 90% Central / 10% State share for most activities; 50% subsidy for entrepreneurship up to INR 50 lakh

**Digital requirements:**
- Applications must go through the NLM portal
- State Level Executive Committee (SLEC) approvals marked digitally
- DAHD Project Approval Committee reviews through the portal
- Subsidy release requires digital documentation of 25% expenditure

### How It Affects PashuRaksha

PashuRaksha should help farmers and entrepreneurs:
- Discover NLM schemes they're eligible for
- Prepare documentation for NLM portal submissions
- Track application status
- Generate required expenditure reports for subsidy releases

### What We Must Implement

1. **NLM scheme directory** — searchable database of applicable schemes
2. **Eligibility checker** — match farmer profile against scheme requirements
3. **Document generation** — produce reports in formats required by NLM portal
4. **Application tracking** — integrate with or link to NLM portal for status updates
5. **Expenditure documentation** — generate auditable expenditure reports for subsidy claims

### Penalties

No penalties for platform non-compliance, but farmers miss scheme benefits without proper digital documentation.

### Timeline

- NLM 2.0 guidelines effective since January 2025
- Implement scheme discovery in Phase 1; full integration in Phase 2

---

## 5. e-Gopala App Analysis

### What It Is

e-Gopala, launched by PM Modi in September 2020 and developed by NDDB, is the government's livestock management app. **It has been replaced by the 1962 Livestock Owner Application** as part of NDLM.

**Features:**
- Livestock management (buying/selling disease-free germplasm)
- Balanced ration formulation using local feed ingredients
- Ethno-veterinary medicine for 29 common ailments
- Alerts for vaccination, pregnancy diagnosis, calving
- Government scheme notifications
- Call center access (1962 toll-free number)
- Available in 12 languages

**Scale:** Over 5 million farmers registered.

### Limitations (Opportunities for PashuRaksha)

| e-Gopala Limitation | PashuRaksha Opportunity |
|---------------------|------------------------|
| Only dairy cattle and buffaloes | Support all livestock (goats, sheep, poultry, pigs) |
| Only 12 of 22 scheduled languages | Full 22-language support via Sarvam AI |
| No marketplace for livestock products | Integrated marketplace with e-NAM compatibility |
| No SHG management | Full SHG module with Panchsutra compliance |
| No financial services integration | UPI payments, Pashu Kisan Credit Card tracking |
| No telemedicine video consultation | Full tele-vet with NITI Aayog guideline compliance |
| No ERP for cooperatives | End-to-end cooperative management |
| Digital literacy barrier (complex UI) | Voice-first interface via Sarvam AI in local languages |
| No offline capability | Offline-first architecture for rural areas |

### What We Must Implement

1. **No direct regulatory obligation** to integrate with e-Gopala (it's being deprecated)
2. **Integrate with 1962 App ecosystem** — ensure compatibility with Bharat Pashudhan/NDLM
3. **Do not duplicate** government scheme information incorrectly — source from official APIs
4. **Support farmer migration** from e-Gopala to PashuRaksha with data import capability

### Timeline

- e-Gopala being replaced by 1962 App (ongoing)
- PashuRaksha should target the gap during this transition

---

## 6. NABARD SHG Digitization & Panchsutra

### What It Requires

**NABARD's Panchsutra** — the five mandatory principles for SHG quality:

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Regular Meetings** | Consistent group meetings on scheduled dates |
| 2 | **Regular Savings** | Members contribute savings at every meeting |
| 3 | **Regular Inter-loaning** | Internal lending among members based on demand |
| 4 | **Timely Repayment** | Prompt loan repayment by members |
| 5 | **Up-to-date Books of Accounts** | Proper documentation and financial records |

SHGs following Panchsutra are graded higher by NABARD and qualify for bank linkage (loans up to INR 10 lakh without collateral).

**NABARD's e-Shakti platform** digitizes SHG operations:
- Online bookkeeping
- Auto-grading per NABARD norms
- Auto-generation of loan applications
- DBT convergence via Aadhaar-linked accounts
- Bilingual mobile app (English + Hindi)
- 12+ lakh SHGs digitized, 1+ crore members enrolled

### How It Affects PashuRaksha

PashuRaksha's SHG management module must enforce Panchsutra compliance digitally. SHGs that don't follow Panchsutra get lower grades and lose bank linkage eligibility.

### What We Must Implement

1. **Meeting scheduler + attendance tracker** — enforce regular meeting compliance
2. **Savings ledger** — track individual member savings with each meeting
3. **Inter-loan management** — record internal lending, interest, and repayment
4. **Repayment tracker** — automated reminders, overdue alerts, repayment history
5. **Digital books of accounts** — auto-generated, NABARD-format financial statements
6. **Auto-grading** — calculate SHG grade based on Panchsutra adherence (matching NABARD norms)
7. **Bank linkage reports** — generate credit reports and loan applications in bank-acceptable format
8. **e-Shakti data export** — ensure data can be exported to/imported from NABARD's e-Shakti platform
9. **SMS alerts** — meeting reminders, savings dues, repayment reminders in local language

### Penalties

No direct regulatory penalties, but:
- SHGs not following Panchsutra lose NABARD grading
- Lower grades mean no bank linkage = no institutional credit
- This directly impacts farmers' access to finance

### Timeline

- e-Shakti is already live in 100+ districts across 28 states
- Implement full Panchsutra compliance module in Phase 1 (core to SHG value proposition)

---

## 7. FSSAI Food Safety Requirements

### What It Requires

All food business operators (FBOs), including dairy product manufacturers/sellers, must obtain **FSSAI license** before selling food products.

**Key 2025-2026 changes:**

| Change | Detail |
|--------|--------|
| **Perpetual license validity** | No more periodic renewals (2026 reform) |
| **Stricter dairy labelling** | Clear dairy logo, bold display of sugar/fat/sodium content |
| **Digital compliance** | All licensing, renewal, modification, and annual returns must be done online |
| **Dairy standards update** | New parameters for fat content, milk solids, microbial limits, adulteration detection |
| **Risk-based inspections** | Automated compliance checks |
| **New product standards** | Standards added for goat milk, sheep milk, and other dairy variants |

**Dairy-specific requirements:**
- Standards for milk: fat content, milk solids, microbial limits, adulteration detection
- Supervision by qualified personnel (degree in dairy technology/veterinary science/food technology)
- Banned term "health drink" for dairy beverages
- Anti-adulteration enforcement increasing

### How It Affects PashuRaksha

PashuRaksha's marketplace module (if selling dairy products) and cooperative management module must ensure FSSAI compliance.

### What We Must Implement

1. **FSSAI license status tracker** — track license status for cooperatives, milk centers, and marketplace sellers
2. **Quality parameter recording** — fat content, SNF, microbial test results with FSSAI-compliant ranges
3. **Adulteration alerts** — flag readings outside FSSAI parameters
4. **Labelling compliance checker** — ensure product listings meet new 2026 labelling norms
5. **Annual return generation** — help FBOs file FSSAI annual returns digitally
6. **Traceability records** — maintain farm-to-consumer traceability chain
7. **Qualified personnel validation** — verify supervisor qualifications for dairy operations

### Penalties

- Operating without FSSAI license: **up to INR 5 lakh fine** and potential imprisonment
- Adulteration: **up to INR 10 lakh fine** and imprisonment up to life (for grievous harm)
- Misbranding: **up to INR 5 lakh fine**
- Non-compliance with standards: **up to INR 5 lakh fine**

### Timeline

- FSSAI digital compliance is already mandatory
- New labelling norms phasing in through 2026
- Implement FSSAI tracking in Phase 2

---

## 8. APMC Act & e-NAM

### What It Requires

The e-NAM (National Agriculture Market) is a pan-India electronic trading portal connecting 1,522+ APMCs across 23 states and 4 UTs. It covers 247 tradable commodities.

**Requirements for integration:**
- Single Trading License valid across state
- Single Point Levy of Market Fee
- E-Trading and E-Auction Framework
- Online auctions with real-time bidding
- E-payment settlement directly to farmer accounts
- Quality assaying (AI-based equipment)
- Warehouse trading (e-NAM 2.0) for stored produce

**Registration:** 1.7 crore farmers and 4,500 FPOs registered.

### How It Affects PashuRaksha

PashuRaksha's marketplace module for livestock products must comply with APMC regulations for states where APMC applies. Livestock sales in mandis require APMC-compliant documentation.

### What We Must Implement

1. **e-NAM awareness** — inform farmers about e-NAM registration and benefits
2. **APMC-compliant invoicing** — generate invoices, receipts, and agreements per APMC regulations
3. **Market fee calculation** — auto-calculate applicable mandi fees for transactions
4. **Quality documentation** — record quality assaying results in e-NAM-compatible format
5. **Price discovery feed** — show real-time mandi prices from e-NAM for farmer decision-making
6. **e-NAM registration assistance** — guide unregistered farmers through e-NAM signup

### Penalties

APMC violations vary by state. Typically:
- Trading without license: fines and market access revocation
- Fee evasion: penalties as per state APMC Act
- Record-keeping failures: audit issues and license suspension

### Timeline

- e-NAM is already operational
- Price feed integration in Phase 1; full e-NAM compatibility in Phase 2

---

## 9. Aadhaar-Based Farmer Identity (AgriStack)

### What It Requires

India's **AgriStack** under the Digital Agriculture Mission is creating digital farmer identities (**Kisan Pehchaan Patra**):

- **10-digit Farmer ID** + checksum digit, linked to Aadhaar
- Contains: farmer name, Aadhaar number, plot area, plot numbers across the state
- QR code for easy verification
- Registration requires: Aadhaar (with linked mobile), land records (Khatauni/7/12), photo, bank details

**Scale targets:**
- 20.5 million farmer IDs created as of March 2025
- Target: **110 million farmer IDs by 2026-27**
- Already mandatory in 10 states (including Maharashtra from April 15, 2025)

**Authentication methods:**
- OTP-based (Aadhaar mobile)
- Biometric (fingerprint/iris via e-POS device)
- Face authentication (new mobile app, no OTP/biometric device needed)

**Unified Farmer Service Interface (UFSI)** provides standardized APIs for consent-based data sharing between government, banks, and agritech firms.

### How It Affects PashuRaksha

PashuRaksha must integrate with AgriStack for:
- Farmer identity verification
- Scheme eligibility checking
- DBT/subsidy delivery tracking
- Land record verification (where applicable)

**Critical gap:** The current farmer registry only includes **land-owning farmers**, not tenant farmers, sharecroppers, or those in allied activities like **livestock/dairy**. This means many PashuRaksha users (landless livestock farmers) may not have a Farmer ID yet.

### What We Must Implement

1. **Aadhaar-based eKYC** — verify farmer identity via Aadhaar OTP or face authentication
2. **Farmer ID (Kisan Pehchaan Patra) lookup** — validate against AgriStack registry
3. **UFSI API integration** — consent-based access to farmer data
4. **Fallback for landless farmers** — alternative identity verification for livestock-only farmers without land records
5. **Aadhaar-animal linking** — connect farmer Aadhaar to Pashu Aadhaar records
6. **Offline Aadhaar verification** — support QR code based offline verification for areas without connectivity

### Penalties

- No direct penalties for platforms, but:
- From April 2025, only farmers with valid digital IDs are eligible for state subsidies (Maharashtra)
- Expanding to more states through 2026-27

### Timeline

- 10 states already enforcing (representing 84% of PM-Kisan beneficiaries)
- Implement Aadhaar eKYC at launch; full AgriStack integration by Phase 2

---

## 10. PM-Kisan & Scheme Integration

### What It Requires

PM-Kisan provides INR 6,000/year (3 installments of INR 2,000) to eligible farmers via DBT into Aadhaar-seeded bank accounts.

**Digital infrastructure:**
- Aadhaar authentication + eKYC mandatory
- Face authentication mobile app (new 2025)
- Know Your Status (KYS) module for status checking
- AI chatbot "Kisan-eMitra" in 11 languages, 24/7
- CSC integration (5+ lakh centers)
- UMANG app access

**Scale:** 9.32+ crore farmer families, INR 4.27+ lakh crore disbursed (22 installments as of March 2026).

### How It Affects PashuRaksha

PashuRaksha should help farmers:
- Check PM-Kisan eligibility and payment status
- Complete eKYC for PM-Kisan
- Discover other applicable schemes (Pashu Kisan Credit Card, NADCP, RGM, etc.)

**Note:** No publicly documented open API exists for third-party PM-Kisan integration. Access is via the portal, mobile app, UMANG, and CSC networks.

### What We Must Implement

1. **Scheme discovery engine** — comprehensive directory of livestock-related government schemes
2. **Eligibility matching** — auto-match farmer profile to applicable schemes
3. **eKYC facilitation** — guide farmers through Aadhaar eKYC process
4. **Deep links to PM-Kisan** — link to portal/UMANG for status checking
5. **Scheme notification system** — alert farmers about new installments, deadlines, and new schemes
6. **Document preparation** — help farmers prepare required documents for scheme applications
7. **Pashu Kisan Credit Card tracking** — track credit card applications and disbursements

**Key schemes to integrate:**
- PM-Kisan (INR 6,000/year)
- Pashu Kisan Credit Card (cattle: INR 1.6L, small ruminants: INR 72K)
- Rashtriya Gokul Mission (breed improvement)
- NADCP (disease control)
- National Livestock Mission (entrepreneurship support)
- State-specific schemes (Karnataka AH&F department)

### Timeline

- Scheme directory in Phase 1
- Deep linking and eligibility matching in Phase 2

---

## 11. Karnataka State Initiatives

### What It Requires

Karnataka is implementing several digital initiatives relevant to PashuRaksha:

| Initiative | Description |
|-----------|-------------|
| **One Health Pilot** | Integrating animal, human, and wildlife health surveillance; digitizing data collection; integrating with NDLM |
| **Data Analytics Unit (DAU)** | AI/ML-driven analytics for livestock scheme governance (established January 2025) |
| **e-Pashuhaat** | Livestock trading, semen/embryo procurement, feed/fodder info |
| **Pashu Kisan Credit Card** | Tailored credit: cattle INR 1.6L, small ruminants INR 72K |
| **Integrated Sample Survey** | Seasonal livestock production surveys (milk, egg, meat, wool) |
| **Disease Eradication** | PPR, CSF, FMD, Brucellosis elimination targets by 2030 |

**Karnataka's Centre for e-Governance (CeG)** is the nodal agency for state e-governance initiatives.

### How It Affects PashuRaksha

As a Karnataka-first deployment, PashuRaksha must align with Karnataka's digital governance ecosystem.

### What We Must Implement

1. **NDLM/Bharat Pashudhan integration** — align with Karnataka's One Health pilot data architecture
2. **Disease reporting** — support disease surveillance reporting in Karnataka's format
3. **Karnataka AH&F department compatibility** — ensure data formats align with state department systems
4. **e-Pashuhaat linking** — connect marketplace to e-Pashuhaat for germplasm trading
5. **Kannada-first interface** — primary language must be Kannada for Karnataka deployment
6. **District/taluka-level data** — support Karnataka's administrative hierarchy in data organization
7. **FMD vaccination tracking** — align with Karnataka's disease eradication timeline

### Timeline

- Align with Karnataka state systems from Phase 1
- Full One Health integration in Phase 3

---

## 12. ISO 27001 Data Security

### What It Requires

ISO/IEC 27001:2022 (the only valid version since October 2025) requires an Information Security Management System (ISMS) with **93 controls across 4 themes:**

| Theme | Controls |
|-------|----------|
| Organisational | 37 controls |
| People | 8 controls |
| Physical | 14 controls |
| Technological | 34 controls |

**New controls added in 2022 revision:** threat intelligence, cloud security, data masking, ICT readiness for business continuity, information security for cloud services, and others.

### How It Affects PashuRaksha

ISO 27001 certification:
- Supports DPDPA compliance (demonstrates "reasonable security safeguards")
- Required by many government procurement portals
- Essential for international expansion (EU partners require it)
- Builds trust with farmer cooperatives handling financial data

### What We Must Implement

1. **Define ISMS scope** — cover all PashuRaksha systems handling farmer personal/financial data
2. **Risk assessment** — identify and evaluate information security risks
3. **Access controls** — role-based access for admin, vet, farmer, SHG leader, milk center operator
4. **Encryption** — AES-256 at rest, TLS 1.3 in transit
5. **Incident response plan** — detection, containment, notification, recovery procedures
6. **Audit logging** — comprehensive audit trail for all data access and modifications
7. **Third-party security** — Data Processing Agreements with all vendors (cloud providers, AI services, payment gateways)
8. **Cloud security controls** — specific controls for cloud-hosted services
9. **Data masking** — mask sensitive data (Aadhaar numbers, bank details) in non-production environments
10. **Business continuity plan** — disaster recovery and backup strategy

### Certification Timeline & Cost

- **Timeline:** 3-12 months for initial certification
- **Validity:** 3 years with annual surveillance audits
- **Cost:** Varies by scope; estimated INR 5-15 lakh for a startup-scale ISMS

### Penalties

No direct legal penalty for not having ISO 27001, but:
- Weakens DPDPA compliance posture (increases penalty risk)
- Excludes from government tenders requiring certification
- Reduces trust with enterprise/cooperative partners

### Timeline

- Begin ISMS planning during development
- Target certification within 6 months of production launch

---

## 13. RBI Digital Payments & UPI

### What It Requires

**Key RBI/NPCI rules for digital payments (2025-2026):**

| Requirement | Detail |
|-------------|--------|
| **Two-factor authentication** | From April 1, 2026: all domestic digital payments must use two authentication factors from different categories |
| **Merchant KYC** | Even small merchants must complete e-KYC for UPI/wallet acceptance |
| **AePS regulations** | Stricter due diligence for Aadhaar Enabled Payment System operators (effective January 1, 2026) |
| **Biometric authentication** | New support for biometric UPI authentication |
| **Micro ATM integration** | UPI now supports cash withdrawals through Micro ATMs |
| **Rural awareness** | RBI conducting structured awareness in collaboration with CSCs |

**UPI Scale:** 18.4 billion transactions in June 2025, INR 24+ lakh crore, 675 banks live.

### How It Affects PashuRaksha

PashuRaksha handles financial transactions:
- Milk sale payments to farmers
- Marketplace transactions
- SHG savings and loan disbursements
- Scheme benefit tracking

### What We Must Implement

1. **UPI integration** — support UPI payments for all transactions (Razorpay/PayU as payment gateway)
2. **Two-factor authentication** — comply with April 2026 mandate
3. **Merchant onboarding KYC** — facilitate e-KYC for milk centers and marketplace sellers
4. **AePS support** — enable Aadhaar-based payments for farmers without smartphones
5. **Offline payment support** — UPI Lite / offline payment modes for low-connectivity areas
6. **Transaction limits compliance** — respect NPCI transaction limits per payment category
7. **Payment reconciliation** — automated reconciliation for cooperative milk payments
8. **DBT tracking** — show government scheme disbursement status

### Penalties

- RBI can impose penalties on regulated entities for non-compliance
- Payment gateway partners bear primary compliance responsibility
- Platform must not facilitate unauthorized payment collection

### Timeline

- UPI integration at launch (Phase 1)
- Two-factor authentication compliance by April 2026
- AePS support in Phase 2

---

## 14. Veterinary Telemedicine Guidelines

### What It Requires

**NITI Aayog's Livestock Telemedicine Framework (2023):**

| Requirement | Detail |
|-------------|--------|
| **Practitioner qualification** | Only Registered Veterinary Practitioners (RVPs) can provide telemedicine services |
| **Unique User IDs** | Required for both RVPs and animal keepers |
| **Mandatory consent** | Before initiating any telemedicine consultation |
| **Consultation modes** | Text, audio, or video calls allowed |
| **Emergency immunity** | RVPs immune from penal action if unable to establish vet-client-animal relationship in emergencies |
| **Prohibited activities** | Cannot do: pet licensing, trauma certificates, quarantine clearance, fitness certificates, birth/death certificates, euthanasia |
| **NITIVeT portal** | Government's web-based telemedicine platform (English, Hindi, Gujarati) |

**Critical context:** India has ~41,000 veterinarians for 53.58 crore livestock. One vet per 5,000 animals is the norm, meaning massive shortfall exists.

### How It Affects PashuRaksha

PashuRaksha's telemedicine module is a core differentiator. It must comply with NITI Aayog guidelines and work within VCI registration requirements.

### What We Must Implement

1. **RVP verification** — verify veterinary registration before allowing consultations
2. **Unique ID system** — assign and track unique IDs for both vets and farmers
3. **Consent capture** — mandatory digital consent before each consultation
4. **Multi-modal consultations** — support text, audio, and video
5. **Consultation records** — maintain detailed records of every consultation
6. **Prescription management** — digital prescriptions with RVP signature
7. **Prohibited activity guards** — prevent booking telemedicine for prohibited activities
8. **Emergency protocols** — clear escalation path for emergencies requiring in-person visit
9. **Ethno-veterinary medicine** — include traditional remedies (validated by NDDB) alongside modern treatment
10. **District-level matching** — connect farmers to RVPs within their district
11. **Offline consultation notes** — allow vets to document consultations offline and sync later

### Penalties

- Practicing veterinary medicine without RVP registration: illegal under VCI Act
- No specific penalties for telemedicine non-compliance (advisory guidelines, not statutory)
- However, malpractice liability applies to all consultations including telemedicine

### Timeline

- Implement telemedicine with full NITI Aayog compliance at launch
- Statutory VCI telemedicine framework expected to evolve (monitor developments)

---

## 15. Upcoming Regulations (2026-2027)

### Confirmed Changes

| Regulation | Change | Date |
|-----------|--------|------|
| **DPDP Act penalties** | Enforcement begins | May 13, 2027 |
| **Consent Manager registration** | DPDP process live | November 13, 2026 |
| **RBI 2FA mandate** | Two-factor auth for all digital payments | April 1, 2026 |
| **AePS stricter norms** | Enhanced due diligence for AePS operators | January 1, 2026 |
| **FSSAI perpetual licenses** | Lifetime validity, no periodic renewal | 2026 |
| **FSSAI labelling norms** | Stricter dairy labelling | Phasing through 2026 |
| **AgriStack expansion** | 110 million farmer IDs target | 2026-27 |
| **Maharashtra farmer ID mandate** | Digital farmer ID required for state subsidies | April 15, 2025 |

### Expected Changes (Monitor Closely)

| Area | Expected Change |
|------|----------------|
| **VCI Telemedicine Act** | Statutory framework for veterinary telemedicine (currently only advisory) |
| **Carbon/climate tracking** | New climate policies requiring carbon and input tracking for agritech platforms |
| **Automated compliance** | AI-based enforcement of policy violations across agritech channels |
| **National Agri-Food Policy** | Integrated systems for crop + livestock + agroforestry |
| **Cross-state licensing** | Clarity on veterinary telemedicine across state boundaries |
| **DPDP startup exemptions** | MSME/startup relief provisions (expected May 2027) |
| **AgriStack for livestock** | Expansion of farmer registry to include landless livestock farmers |

### Strategic Recommendations

1. **Build compliance-as-a-feature** — make regulatory compliance a competitive advantage
2. **Design for change** — use configurable rules engines for regulations that are evolving
3. **Monitor actively** — assign someone to track DAHD, FSSAI, DPDP Board, and RBI circulars monthly
4. **Engage with regulators** — participate in public consultations on upcoming rules

---

## 16. Master Compliance Checklist

### Priority 1: Must-Have Before Launch

| # | Requirement | Regulation | Module |
|---|-------------|-----------|--------|
| 1 | Multilingual consent management (Kannada + Hindi + English minimum) | DPDP Act | All |
| 2 | Data encryption at rest (AES-256) and in transit (TLS 1.3) | DPDP Act, ISO 27001 | All |
| 3 | 72-hour breach notification pipeline | DPDP Act | Platform |
| 4 | Aadhaar-based eKYC for farmer verification | AgriStack | Registration |
| 5 | Pashu Aadhaar (12-digit) as primary animal identifier | INAPH/NDLM | Livestock Mgmt |
| 6 | RVP registration verification for all veterinarians | VCI Act | Telemedicine |
| 7 | Mandatory consent capture before telemedicine consultations | NITI Aayog | Telemedicine |
| 8 | UPI payment integration | RBI/NPCI | Payments |
| 9 | Panchsutra compliance tracking for SHGs | NABARD | SHG Module |
| 10 | Privacy policy in all supported languages | DPDP Act | All |
| 11 | Data principal rights (access, correct, delete) | DPDP Act | All |
| 12 | Offline-first architecture | Rural reality | All |
| 13 | Kannada-first interface for Karnataka | State requirement | All |

### Priority 2: Required Within 6 Months of Launch

| # | Requirement | Regulation | Module |
|---|-------------|-----------|--------|
| 14 | Two-factor authentication for payments | RBI (April 2026) | Payments |
| 15 | INAPH API bidirectional sync | NDLM | Livestock Mgmt |
| 16 | FSSAI license status tracking | FSSAI | Cooperative Mgmt |
| 17 | Milk quality parameter recording (fat, SNF, microbial) | FSSAI/NDDB | Milk Center |
| 18 | e-NAM price feed integration | APMC/e-NAM | Marketplace |
| 19 | NLM/state scheme directory with eligibility matching | NLM | Schemes |
| 20 | AMCS-compatible milk collection data format | NDDB | Milk Center |
| 21 | e-Shakti data export for SHG records | NABARD | SHG Module |
| 22 | Audit logging for all data access | ISO 27001 | Platform |
| 23 | APMC-compliant invoicing | APMC Act | Marketplace |
| 24 | Merchant e-KYC for milk centers | RBI | Payments |

### Priority 3: Required Within 12 Months / Phase 2

| # | Requirement | Regulation | Module |
|---|-------------|-----------|--------|
| 25 | ISO 27001:2022 certification | ISO 27001 | Platform |
| 26 | Full AgriStack/UFSI API integration | AgriStack | Registration |
| 27 | AePS support for non-smartphone farmers | RBI | Payments |
| 28 | Full i-DIS reporting compatibility | NDDB | Cooperative Mgmt |
| 29 | Karnataka One Health data integration | State initiative | Health Mgmt |
| 30 | Carbon/input tracking (prepare for upcoming regulations) | Expected policy | All |
| 31 | DPDP Consent Manager integration (if applicable) | DPDP (Nov 2026) | All |
| 32 | FMD vaccination campaign integration | DAHD/Karnataka | Health Mgmt |
| 33 | Automated FSSAI annual return generation | FSSAI | Cooperative Mgmt |
| 34 | Full 22-language support for pan-India expansion | DPDP Act | All |

### Priority 4: Monitor & Prepare

| # | Requirement | Status |
|---|-------------|--------|
| 35 | VCI statutory telemedicine framework | Advisory only; statutory expected |
| 36 | AgriStack expansion to livestock farmers (landless) | Under development |
| 37 | DPDP startup exemptions | Expected May 2027 |
| 38 | Cross-state veterinary telemedicine licensing | Under discussion |
| 39 | AI-based automated compliance enforcement | Emerging |

---

## Key Risk Summary

| Risk | Severity | Mitigation |
|------|----------|------------|
| DPDP non-compliance after May 2027 | **CRITICAL** (up to INR 250 Cr fine) | Implement consent + security now |
| Operating telemedicine without RVP verification | **HIGH** (illegal practice) | Mandatory RVP check at onboarding |
| Processing farmer data without consent | **HIGH** (INR 50 Cr per instance) | Consent-first architecture |
| FSSAI violations in dairy marketplace | **HIGH** (INR 5-10 lakh + imprisonment) | FSSAI compliance checks in marketplace |
| Unencrypted farmer data breach | **CRITICAL** (INR 250 Cr + reputation) | Encryption by default |
| Ignoring Pashu Aadhaar integration | **MEDIUM** (excluded from national ecosystem) | Integrate at launch |
| SHG records not matching NABARD format | **MEDIUM** (bank linkage denied) | NABARD-format compliance |
| UPI payment non-compliance | **HIGH** (payment gateway suspension) | Use certified payment gateway |

---

## Sources

### DPDP Act 2023
- [EY: Decoding the DPDP Act 2023](https://www.ey.com/en_in/insights/cybersecurity/decoding-the-digital-personal-data-protection-act-2023)
- [India's DPDPA 2023 with 2025 Rules](https://www.roedl.com/en/insights/indias-dpdpa-2023-activates-with-2025-rules-revolutionizing-data-privacy-enforcement/)
- [DPDP Rules 2025 Implementation Checklist](https://www.scrut.io/post/dpdp-rules)
- [EY: Transforming Data Privacy DPDP Rules 2025](https://www.ey.com/en_in/insights/cybersecurity/transforming-data-privacy-digital-personal-data-protection-rules-2025)
- [DPDP Penalties for Non-Compliance](https://www.leegality.com/consent-blog/penalties)
- [DPDPA Penalty Trap: Hidden Risks](https://dpo-india.com/Blogs/dpdpa-penalty-trap/)
- [DPDP Act Non-Compliance Penalties 2026](https://vistainfosec.com/blog/dpdp-act-non-compliance-penalties/)

### INAPH / Pashu Aadhaar
- [Pashu Aadhar Card 2025](https://pmyojna.com/pashu-aadhar-card-2025-online-application-status-check-full-details/)
- [Pashu Aadhaar Registration Guide](https://www.tesz.in/guide/pashu-aadhaar)
- [India Digitalizes Dairy Sector, 35 Crore Livestock Get Aadhaar IDs](https://www.whalesbook.com/news/English/Agriculture/India-Digitalizes-Dairy-Sector-35-Crore-Livestock-Get-Aadhar-IDs/6960bddaef4ed95f980b16a4)
- [71.6 Million Animals Given Pashu Aadhaar](https://www.medianama.com/2020/09/223-pashu-aadhaar-animals-health-id/)

### NDDB Dairy Digitization
- [Digitalizing India's Dairy Sector (PIB)](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/jan/doc202619754001.pdf)
- [NDDB Digitalization Services](https://beta.nddb.coop/services/animal-health/digitalization)
- [India's Dairy Digital Transformation](https://www.nextias.com/ca/current-affairs/10-01-2026/digital-dairy-india)
- [Digital Transformation of India's Dairy Sector (Drishti IAS)](https://www.drishtiias.com/daily-updates/daily-news-analysis/digital-transformation-of-indias-dairy-sector)

### National Livestock Mission
- [NLM Operational Guidelines 2.0 (PDF)](https://livestock.kerala.gov.in/wp-content/uploads/2025/03/COMPREHENSIVE-OPERATIONAL-GUIDELINES-FOR-NATIONAL-LIVESTOCK-MISSION-JAN-2025.pdf)
- [NDLM Blueprint (PDF)](https://megahvt.gov.in/notification/National%20Digital%20Livestock%20Mission.pdf)
- [NDLM Press Release (PIB)](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2204580&reg=3&lang=1)
- [NLM Operational Guidelines 2.0 Released](https://visionias.in/current-affairs/news-today/2025-01-14/economics-(indian-economy)/national-livestock-mission-nlm-operational-guidelines-20-released)

### e-Gopala App
- [e-GOPALA Portal (PIB)](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1808244)
- [How e-Gopala Is Transforming Farmers' Lives](https://jaagrukbharat.com/How-eGopala-App-Is-Transforming-The-Lives-Of-Indian-Farmers-NTYx)
- [What Is e-Gopala App (Krishi Jagran)](https://krishijagran.com/animal-husbandry/what-is-e-gopala-app-and-how-it-will-help-farmers/)

### NABARD SHG / Panchsutra
- [NABARD e-Shakti Initiative](https://www.indiafilings.com/learn/e-shakti-nabard)
- [e-Shakti Pilot Project (NABARD PDF)](https://www.nabard.org/demo/auth/writereaddata/File/E-Shakti%20Pilot%20Project%20on%20Digitisation%20of%20SHGs.pdf)
- [NABARD SHG-Bank Linkage](https://www.nabard.org/contentsearch.aspx?AID=225&Key=shg+bank+linkage+programme)

### FSSAI
- [FSSAI Guidelines for Dairy Industry](https://www.zolvit.com/fssai/food-categories/dairy-products)
- [New FSSAI Labeling Rules 2026](https://www.psrcompliance.com/blog/new-fssai-labeling-rules-packaged-foods-india-2026)
- [FSSAI Rules and Reforms 2026](https://www.kanakkupillai.com/learn/key-fssai-rules-and-reforms-2026/)
- [FSSAI 2025 Food Safety Guidelines](https://corpbiz.io/learning/fssai-food-safety-regulations/)

### APMC / e-NAM
- [e-NAM Transforming Agricultural Trade (PIB)](https://www.pib.gov.in/FactsheetDetails.aspx?Id=149061&reg=3&lang=2)
- [APMC Legal Framework in India](https://www.lawrbit.com/article/demystifying-apmc-legal-framework-and-market-dynamics-in-india/)
- [One Nation One Market: APMC and e-NAM](https://www.indialaw.in/blog/civil/one-nation-one-market-apmc-act-e-nam/)

### Aadhaar / AgriStack
- [AgriStack Farmer Registry](https://agristack.info/)
- [India Makes Digital Farmer IDs Mandatory](https://idtechwire.com/india-makes-digital-farmer-ids-mandatory-for-welfare-scheme-applicants/)
- [Aadhaar Verification Amendment Regulations 2025](https://uidai.gov.in/en/about-uidai/legal-framework/regulations/19549-aadhaar-authentication-and-offline-verification-amendment-regulations-2025.html)
- [AgriStack Building Blocks (MicroSave)](https://www.microsave.net/2025/11/14/the-building-blocks-of-agristack-state-farmer-registry/)

### PM-Kisan
- [PM-Kisan 22nd Installment (PIB)](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238588&reg=3&lang=2)
- [PM-KISAN (NIC)](https://www.nic.gov.in/project/pm-kisan/)
- [PM-Kisan on Digital India](https://www.digitalindia.gov.in/initiative/pm-kisan/)

### Karnataka
- [One Health Pilot in Karnataka](https://www.global-agriculture.com/india-region/department-of-animal-husbandry-and-dairying-launches-one-health-pilot-project-in-karnataka/)
- [Karnataka AH&F Department](https://ahf.karnataka.gov.in/english)

### ISO 27001
- [ISO/IEC 27001:2022 Standard](https://www.iso.org/standard/27001)
- [ISO 27001 Certification in India 2025](https://parafoxtechnologies.in/iso-27001-certification-india-guide/)
- [ISO 27001 Guide 2026](https://www.cynorsense.com/post/iso-27001-certification-guide-2026-complete-information-security-management-system-framework)

### RBI / UPI
- [RBI Digital Payments Awareness 2026](https://edunovations.com/currentaffairs/banking/digital-payments-awareness-program/)
- [UPI New Rules 2025](https://www.lawrbit.com/article/what-is-new-in-upi-rules-2025-key-changes-you-should-know/)
- [RBI Digital Payment Authentication 2025](https://paytm.com/blog/news/rbi-digital-payment-authentication-2025/)
- [India's UPI Moment for Agriculture](https://agrospectrumindia.com/2026/03/13/india-moves-toward-upi-moment-for-agriculture-through-digital-public-infrastructure.html)

### Veterinary Telemedicine
- [NITI Aayog Telemedicine for Livestock Health (PDF)](https://www.niti.gov.in/sites/default/files/2023-07/Telemedicine-for-Livestock-Health_Inside%20Report_18072023.pdf)
- [Veterinary Telemedicine in India](https://www.pashudhanpraharee.com/veterinary-telemedicine-in-india-a-new-horizon-for-transforming-animal-healthcare/)
- [Tele-Veterinary Services & Mobile Vet Clinics](https://www.vosd.in/tele-veterinary-services-mobile-vet-clinics-india/)

### Upcoming Regulations
- [AgTech Regulations 2026](https://farmonaut.com/blogs/agtech-regulations-2026-key-strategies-for-safe-innovation)
- [7 Non-Negotiable AgriTech Trends 2026](https://www.cropin.com/blogs/7-agri-tech-trends-for-2026/)
- [AgriTech in India 2026 Market (Tracxn)](https://tracxn.com/d/explore/agritech-startups-in-india/__R7Goxl_PZW5pPOFh2nTxcoos_7UGPeuksQVbmWwyS6A)
