# SPR High School Elections 2026-27 (`Election Spr 2026`)

[![Status](https://img.shields.io/badge/Status-100%25%20Operational%20%26%20Production%20Ready-brightgreen.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Pure%20Static%20Client--Side-blue.svg)]()
[![Database](https://img.shields.io/badge/Database-Supabase%20Cloud%20PostgreSQL-orange.svg)]()
[![Biometrics](https://img.shields.io/badge/Biometrics-Pico.js%20Edge%20Face%20Guard-purple.svg)]()
[![License](https://img.shields.io/badge/License-Institutional%20Private-lightgrey.svg)]()

A modern, decentralized, and production-grade electronic voting, election administration, and real-time result declaration platform engineered for **SPR High School Student Council & House Elections (Academic Year 2026–27)**.

Features offline client-side AI face verification, USB hardware barcode scanning, live multi-station cloud synchronization, secret ballot voter confidentiality, teacher universal voting across all posts, comprehensive admin audit controls, and an interactive result ceremony portal with scratch cards and winner spotlights.

---

## 📁 Repository Structure & Major Folders

```
Election Spr 2026/
├── 1docs/                       # 📂 Master Documentation, Official Voter ID Registers & Candidate Dossiers
│   ├── contestets/              # 150 Candidate dossiers (Photos, Bio/Manifestos, Ballot Symbols)
│   │   ├── Bheeshma/            # Candidate folders per post (Captain, Vice Captain)
│   │   ├── Gurudrona/           # Candidate folders per post
│   │   ├── Hanuman house/       # Candidate folders per post
│   │   ├── KAran house/         # Candidate folders per post
│   │   ├── School Cabinet/      # Central Cabinet candidates (President, VP, Cultural, Sports, Literary)
│   │   ├── Vasistha house/      # Candidate folders per post
│   │   └── Vishwamithra/        # Candidate folders per post
│   ├── House_Voter_ID_Lists/    # Constituency-wise voter splits (CSV & XLSX)
│   ├── OFFICIAL_ALL_VOTER_IDS_2026.xlsx        # Consolidated master register (1,173 voters: students + faculty)
│   ├── OFFICIAL_STUDENT_VOTER_IDS_2026.xlsx    # Master student register (1,085 students)
│   ├── OFFICIAL_STUDENT_VOTER_IDS_2026.pdf     # High-resolution print-ready student voter lists
│   ├── OFFICIAL_TEACHER_VOTER_IDS_2026.xlsx    # Master teaching & admin faculty register (88 teachers)
│   ├── OFFICIAL_TEACHER_VOTER_IDS_2026.pdf     # High-resolution print-ready teacher voter lists
│   ├── TOTAL EMPLOYEES LIST 2026-27 FOR DIWALI.xlsx # Institutional staff roster with assigned Voter IDs
│   └── [House].xlsx             # House-specific student lists (Bheesma, Gurudrona, Hanuman, Karan, Vasista, Viswamitra)
│
├── Houses/                      # 🗳️ Polling Kiosks & Administrative Dashboard
│   ├── admin/                   # Master Admin Command Suite
│   │   ├── index.html           # Live Turnout KPIs, Real-time Charts, Station Monitoring
│   │   ├── edit-votes.html      # Secret Ballot Voter Inspection, Face Audit, Void/Cancel Votes
│   │   ├── results.html         # Official Result Tallies & Certificate Generation
│   │   ├── print_teachers.html  # High-density printable teacher barcode voter badges
│   │   ├── supabase-config.js   # Cloud Supabase connection endpoint & credentials
│   │   └── teachers.js / json   # Verified faculty roster data
│   ├── assets/                  # Logos, House Crests, Candidate Symbols, Audio Chimes
│   ├── bheeshma/                # Polling Kiosk for Gangotri Constituency (Bheeshma House)
│   ├── gurudrona/               # Polling Kiosk for Trimbakeshwar Constituency (Gurudrona House)
│   ├── hanuman/                 # Polling Kiosk for Yamunotri Constituency (Hanuman House)
│   ├── karna/                   # Polling Kiosk for Manasarovar Constituency (Karna House)
│   ├── vasistha/                # Polling Kiosk for Mahabaleshwar Constituency (Vasistha House)
│   ├── vishwamithra/            # Polling Kiosk for Amarkantak Constituency (Vishwamithra House)
│   ├── central/                 # Polling Kiosk for Central School Cabinet
│   ├── teachers/                # 👩‍🏫 Universal Teacher Polling Booth (Voting across all 29 posts)
│   ├── graphs.html              # Standalone Fullscreen Live Polling Graphs & Comparative Charts
│   └── index.html               # Central Polling Hub Entry Page
│
├── Result declaration/          # 🏆 Live Election Result Ceremony Portal
│   ├── index.html               # Public Result Ceremony Portal with interactive scratch cards & spotlights
│   ├── css/                     # Ceremony styles, glow animations, card flip effects
│   ├── js/                      # Real-time tally fetcher, scratch-to-reveal canvas, sound effects
│   └── assets/                  # Winner badge graphics, celebration confetti, sound FX
│
├── server/                      # ⚙️ Helper Backend Services
│   ├── otp_server.py            # Local Python OTP verification microservice
│   └── config.json              # Server environment & port configuration
│
├── scripts/                     # 🐍 Automation, ETL & Data Synchronization Tooling
│   ├── reconcile_all_contestants.py  # Synchronizes candidate dossiers with booth databases
│   ├── build_all_voter_cards.py     # Generates high-res printable voter ID cards with barcodes
│   ├── verify_live_supabase.py       # Validates cloud database integrity and audit tables
│   └── generate_roster.py           # Exports normalized rosters for kiosk data.js files
│
├── docs/                        # 📚 Technical Documentation & System Specifications
│   ├── PROJECT_AIM_AND_OVERVIEW.md
│   ├── ARCHITECTURE_AND_TECH_STACK.md
│   ├── DIRECTORY_AND_FILE_GUIDE.md
│   ├── DATABASE_SCHEMA_AND_STORAGE.md
│   ├── VOTING_KIOSKS_AND_BIOMETRICS.md
│   ├── ADMIN_PORTAL_AND_OPERATIONS.md
│   ├── DEVELOPER_RULES_WHAT_TO_EDIT_AND_WHAT_NOT.md
│   ├── CURRENT_PROGRESS_AND_CHANGELOG.md
│   └── DEPLOYMENT_AND_DOMAIN_SETUP_GUIDE.md
│
├── sample_cards/ & voter_cards/ # 🪪 Generated Voter ID Badges & Print Layouts
└── README.md                    # System Guide & Quickstart Reference
```

---

## 🏛️ Electoral Topology & Constituencies

The election manages **1,173 registered voters** (1,085 students + 88 faculty members):

| House / Category | Constituency Name | Electorate Size | Contested Posts | Polling Kiosk |
| :--- | :--- | :---: | :--- | :--- |
| **Bheeshma House** | Gangotri | 168 | Boys Captain, Girls Captain, Boys VC, Girls VC | [`/Houses/bheeshma/`](http://127.0.0.1:5500/Houses/bheeshma/index.html) |
| **Gurudrona House** | Trimbakeshwar | 181 | Boys Captain, Girls Captain, Boys VC, Girls VC | [`/Houses/gurudrona/`](http://127.0.0.1:5500/Houses/gurudrona/index.html) |
| **Hanuman House** | Yamunotri | 181 | Boys Captain, Girls Captain, Boys VC, Girls VC | [`/Houses/hanuman/`](http://127.0.0.1:5500/Houses/hanuman/index.html) |
| **Karna House** | Manasarovar | 180 | Boys Captain, Girls Captain, Boys VC, Girls VC | [`/Houses/karna/`](http://127.0.0.1:5500/Houses/karna/index.html) |
| **Vasistha House** | Mahabaleshwar | 184 | Boys Captain, Girls Captain, Boys VC, Girls VC | [`/Houses/vasistha/`](http://127.0.0.1:5500/Houses/vasistha/index.html) |
| **Vishwamithra House** | Amarkantak | 191 | Boys Captain, Girls Captain, Boys VC, Girls VC | [`/Houses/vishwamithra/`](http://127.0.0.1:5500/Houses/vishwamithra/index.html) |
| **School Cabinet** | Central Cabinet | Institutional | President, Vice President, Literary, Sports, Cultural | [`/Houses/central/`](http://127.0.0.1:5500/Houses/central/index.html) |
| **Faculty & Teachers** | Universal Faculty | 88 | All 29 Posts (5 Cabinet + 24 House Posts) | [`/Houses/teachers/`](http://127.0.0.1:5500/Houses/teachers/index.html) |

---

## ✨ System Highlights & Architecture

### 1. Universal Teacher Polling Booth (`/Houses/teachers/`)
- Allows teaching and administrative faculty (88 members) to cast ballots across **all 29 election posts**:
  - 5 Central School Cabinet positions (President, Vice President, Literary Secretary, Sports Secretary, Social & Cultural Secretary).
  - 24 House Captain & Vice Captain positions across all 6 houses.
- Tabbed constituency navigation with completion counters (`0/5`, `0/4`), selection indicators, and instant ballot review before biometric submission.

### 2. Edge AI Biometric Face Verification Guard
- Powered by `pico.js` (~5 KB) and client-side Haar cascades running offline in the browser.
- Enforces steady face alignment and anti-spoofing verification before capturing an audit photo and uploading to Supabase Cloud Storage.
- Zero GPU requirements; runs smoothly on standard school desktop PCs.

### 3. Hardware Barcode Scanner Integration
- Plug-and-play USB barcode gun support (WebHID keyboard emulation).
- Instant voter accreditation upon scanning student or teacher identity badges.

### 4. Live Multi-Station Cloud Synchronization
- All kiosks directly submit encrypted ballots to **Supabase Cloud PostgreSQL**.
- Real-time WebSockets update turnout figures and vote counts on the Admin Dashboard within 2 seconds.
- Offline fallback queue (`spr_offline_ballots_queue`) ensures zero vote loss during Wi-Fi interruptions.

### 5. Interactive Result Declaration Ceremony (`/Result declaration/`)
- Public-facing auditorium and broadcast portal.
- **Scratch-to-Reveal Winner Cards:** Interactive digital scratch cards allowing presenters to reveal elected captains and cabinet leaders live on stage.
- **Candidate Spotlight Modal:** Click any candidate to view their photo, manifesto, slogan, and ballot symbol.
- **Dynamic Polling Visualizations:** Real-time percentage breakdowns, victory margins, and confetti celebration effects.

### 6. Administration & Audit Suite (`/Houses/admin/`)
- **Live Monitoring (`index.html`):** House turnout KPIs, station heartbeat, and vote distributions.
- **Secret Ballot Audit & Vote Management (`edit-votes.html`):** Search voters, inspect biometric snapshots, and cancel ballots with mandatory officer attribution without exposing candidate selections.
- **Results & Certification (`results.html`):** Certified result generation, official victory certificates with school seals, and one-click Excel export via SheetJS.

---

## 🚀 How to Run Locally

### Prerequisites
- Any modern web browser (**Google Chrome**, **Microsoft Edge**, **Mozilla Firefox**, or **Brave**).
- No Node.js build step is required for the frontend.

### Step 1: Start Local Server
Run any local static HTTP server in the repository directory:

```powershell
# Navigate to the project folder
cd "Election Spr 2026"

# Run Python's built-in static HTTP server on port 5500
python -m http.server 5500 --bind 127.0.0.1
```

### Step 2: Open Portal
Open your browser and navigate to:
- **Central Polling Hub:** [`http://127.0.0.1:5500/Houses/index.html`](http://127.0.0.1:5500/Houses/index.html)
- **Teacher Polling Booth:** [`http://127.0.0.1:5500/Houses/teachers/index.html`](http://127.0.0.1:5500/Houses/teachers/index.html)
- **Master Admin Dashboard:** [`http://127.0.0.1:5500/Houses/admin/index.html`](http://127.0.0.1:5500/Houses/admin/index.html)
- **Result Declaration Portal:** [`http://127.0.0.1:5500/Result%20declaration/index.html`](http://127.0.0.1:5500/Result%20declaration/index.html)
- **Live Polling Graphs:** [`http://127.0.0.1:5500/Houses/graphs.html`](http://127.0.0.1:5500/Houses/graphs.html)

---

## 🔒 Security & Privacy Notice

- Local Supabase API service keys, private service role secrets, and local environment files are restricted by `.gitignore`.
- Voter ballot secrecy is enforced across all administration screens: candidate choices are decoupled from voter identity in public auditing views.

---

*Engineered for SPR High School — Student Council & House Elections 2026–27.*
