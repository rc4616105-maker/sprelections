# School House Elections 2026 (`elections`)

[![Status](https://img.shields.io/badge/Status-100%25%20Operational%20%26%20Production%20Ready-brightgreen.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Pure%20Static%20Client--Side-blue.svg)]()
[![Database](https://img.shields.io/badge/Database-Supabase%20Cloud%20PostgreSQL-orange.svg)]()
[![Biometrics](https://img.shields.io/badge/Biometrics-Pico.js%20Edge%20Face%20Guard-purple.svg)]()
[![License](https://img.shields.io/badge/License-Institutional%20Private-lightgrey.svg)]()

A decentralized, production-grade electronic voting and election administration platform engineered for school student council and house elections. Features client-side AI face verification, USB barcode card scanning, live multi-station cloud synchronization, secret ballot voter confidentiality, and instant result certification.

---

## 🏛️ System Overview

The **School House Elections 2026** platform serves an electorate of **1,173 registered voters** (1,085 students across 6 House Constituencies + 88 institutional teaching and administrative faculty members) across dedicated polling kiosks:

- **Bheeshma House** &rarr; **Gangotri Constituency** (168 voters)
- **Gurudrona House** &rarr; **Trimbakeshwar Constituency** (181 voters)
- **Hanuman House** &rarr; **Yamunotri Constituency** (181 voters)
- **Karna House** &rarr; **Manasarovar Constituency** (180 voters)
- **Vasistha House** &rarr; **Mahabaleshwar Constituency** (184 voters)
- **Vishwamithra House** &rarr; **Amarkantak Constituency** (191 voters)
- **Teacher Universal Polling Booth** &rarr; 88 Faculty members voting across all 29 roles (5 Central Cabinet + 24 House Captains/Vice Captains)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ELECTION DAY TOPOLOGY                           │
└────────────────────────────────────────────────────────────────────────┘

 [ School Lab Station 1 ] ─── Bheeshma House Kiosk   (HTTPS)
 [ School Lab Station 2 ] ─── Gurudrona House Kiosk  (HTTPS) ──┐
 [ School Lab Station 3 ] ─── Hanuman House Kiosk    (HTTPS)   │
 [ School Lab Station 4 ] ─── Karna House Kiosk      (HTTPS)   ├──> [ Live Domain / Kiosks ]
 [ School Lab Station 5 ] ─── Vasistha House Kiosk   (HTTPS)   │     (e.g. https://schoolelection.in)
 [ School Lab Station 6 ] ─── Vishwamithra Kiosk     (HTTPS)   │
 [ School Lab Station 7 ] ─── School Cabinet Kiosk   (HTTPS) ──┘
           │                                                       ▲
           ▼ (USB Scanners & Webcams)                              │
 ┌────────────────────────────────────────────────────────┐        │
 │              CLIENT-SIDE EDGE EXECUTION                │        │
 │  • Pico.js Face Verification Guard (Offline Wasm/JS)   │        │
 │  • Hardware Barcode Scanner (WebHID Keyboard Emulation)│        │
 └─────────────────────────┬──────────────────────────────┘        │
                           │                                       │
                           ▼ (Direct REST & Realtime WSS)          │
 ┌────────────────────────────────────────────────────────┐        │
 │                SUPABASE CLOUD PLATFORM                 │        │
 │  • PostgreSQL Database (ballots, voters, candidates)   │        │
 │  • Cloud Storage Bucket (voter-photos)                 │        │
 └─────────────────────────▲──────────────────────────────┘        │
                           │                                       │
                           │ (Live Admin Audit & Control)          │
                           │                                       │
 ┌─────────────────────────┴──────────────────────────────┐        │
 │           MASTER ADMIN COMMAND CONSOLE (LAPTOP)        │────────┘
 │  • Live Turnout KPIs & Real-Time Graph Monitoring      │
 │  • Secret Ballot Vote Cancellation & Attribution       │
 │  • Candidate Management on the Fly                     │
 │  • Official Certificate Printing & Excel Export        │
 └────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

- **🗳️ 7 Independent Polling Kiosks:**
  - 6 House Booths: **Bheeshma**, **Gurudrona**, **Hanuman**, **Karna**, **Vasistha**, and **Vishwamithra** (Students elect Boys Captain, Girls Captain, Boys Vice Captain, Girls Vice Captain).
  - 1 Central Booth: **School Cabinet** (Dedicated exclusively to teaching faculty electing Head Boy, Head Girl, Sports Captain, Cultural Secretary, and Discipline Secretary).
- **📷 Edge AI Biometric Face Verification Guard:**
  - Pre-trained Haar cascade classifier (`facefinder`, 239 KB) and `pico.js` (~5 KB) run 100% offline in client WebAssembly/JS.
  - Zero heavy external model downloads, zero GPU requirements — runs smoothly on any basic school computer or Chromebook.
  - Real-time anti-hand and lens-obstruction detection (evaluates frame luminance and variance).
  - Enforces 2 consecutive steady frames (~400ms) before capturing audit photo and submitting ballot.
- **🔫 Hardware Barcode Card Scanner:**
  - Standard USB barcode gun support using WebHID keyboard emulation. Scans student ID cards for instant accreditation without manual typing.
- **🛡️ Secret Ballot Confidentiality:**
  - Consolidated 1-row voter inspection in administration tables (`✓ Voted (All 4 Posts)`). Individual candidate choices are strictly hidden to preserve institutional ballot secrecy.
- **🔄 Officer-Attributed Vote Cancellation:**
  - If a student makes an error or has a card dispute, polling officers can cancel the vote with recorded officer attribution (`cancelled_by`), immediately re-enabling the student to re-vote.
- **📊 Real-Time Turnout & Live Graphs:**
  - Admin dashboard auto-syncs every 2 seconds with Supabase Cloud.
  - Visual turnout percentages, comparative candidate vote charts, and house drilldowns.
- **🏆 Official Certificate Printing & Excel Export:**
  - 1-click printable high-resolution election victory certificates with official school crests.
  - Export comprehensive ballot audit registers directly to `.xlsx` via embedded SheetJS.
- **📶 Offline Resilience & Queueing:**
  - If school Wi-Fi temporarily fluctuates, ballots queue locally in `localStorage` (`spr_offline_ballots_queue`) and auto-sync immediately when connectivity resumes.

---

## 🚀 How to Run & Use (Step-by-Step)

### 1. Prerequisites
- Any modern web browser (**Google Chrome**, **Microsoft Edge**, **Mozilla Firefox**, or **Brave**).
- **No Node.js, Python, or backend server build step is required** to run the voting kiosks or admin portal. The application is pure static HTML, CSS, and modern JavaScript.

### 2. Running Locally

Clone this repository and serve using any local static web server:

```powershell
# Navigate to the project directory
cd "Election Spr 2026"

# Option A: Python built-in HTTP server
python -m http.server 5500 --bind 127.0.0.1

# Option B: VS Code / IDE Live Server
# Right-click Houses/index.html -> "Open with Live Server" (Port 5500)
```

Open your browser at:  
👉 **`http://127.0.0.1:5500/Houses/index.html`**

---

### 3. Portal Navigation Directory

| Station / Portal | Description | URL Path |
| :--- | :--- | :--- |
| **Central Polling Hub** | Central entrance to choose any house booth | [`/Houses/index.html`](http://127.0.0.1:5500/Houses/index.html) |
| **Bheeshma Kiosk** | Polling booth for Bheeshma House students | [`/Houses/bheeshma/index.html`](http://127.0.0.1:5500/Houses/bheeshma/index.html) |
| **Gurudrona Kiosk** | Polling booth for Gurudrona House students | [`/Houses/gurudrona/index.html`](http://127.0.0.1:5500/Houses/gurudrona/index.html) |
| **Hanuman Kiosk** | Polling booth for Hanuman House students | [`/Houses/hanuman/index.html`](http://127.0.0.1:5500/Houses/hanuman/index.html) |
| **Karna Kiosk** | Polling booth for Karna House students | [`/Houses/karna/index.html`](http://127.0.0.1:5500/Houses/karna/index.html) |
| **Vasistha Kiosk** | Polling booth for Vasistha House students | [`/Houses/vasistha/index.html`](http://127.0.0.1:5500/Houses/vasistha/index.html) |
| **Vishwamithra Kiosk** | Polling booth for Vishwamithra House students | [`/Houses/vishwamithra/index.html`](http://127.0.0.1:5500/Houses/vishwamithra/index.html) |
| **School Cabinet Kiosk** | **Faculty-Only Booth** for Central School Cabinet | [`/Houses/central/index.html`](http://127.0.0.1:5500/Houses/central/index.html) |
| **Master Admin Dashboard** | Live turnout, house graphs, and station monitoring | [`/Houses/admin/index.html`](http://127.0.0.1:5500/Houses/admin/index.html) |
| **Edit & Manage Votes** | Secret Ballot voter register, photo audit & cancellations | [`/Houses/admin/edit-votes.html`](http://127.0.0.1:5500/Houses/admin/edit-votes.html) |
| **Election Results** | Final winners, vote tallies, and certificate printing | [`/Houses/admin/results.html`](http://127.0.0.1:5500/Houses/admin/results.html) |

---

### 4. Step-by-Step Voting Workflow (For Polling Stations)

1. **Station Initialization:**
   - Open the station's house URL (e.g. `/Houses/hanuman/index.html`).
   - Press `F11` for clean full-screen kiosk display.
   - Enter the Booth Station Name (e.g. `Computer Lab - Station 3`) and Polling Officer Name.
   - Allow camera permissions when prompted by the browser.
2. **Voter Accreditation:**
   - Scan the barcode on the student's ID card using the USB scanner (or type their Voter ID).
   - The screen instantly displays the student's name, class, section, and house badge.
3. **Ballot Casting:**
   - The student selects their preferred candidate for each role:
     - Boys Captain
     - Girls Captain
     - Boys Vice Captain
     - Girls Vice Captain
   - Click **Cast Vote**.
4. **Biometric Face Verification:**
   - The **Face Verification Guard** modal appears with an oval guide.
   - The student looks directly into the webcam.
   - Once a steady face is verified (~400ms), the system automatically captures an audit photo, submits the encrypted ballots directly to Cloud Supabase, and clears the screen for the next voter.

---

### 5. Administration & Audit Operations

1. **Live Monitoring:**
   - Keep `Houses/admin/index.html` open on the central administrative laptop.
   - Watch live voter turnout metrics update in real-time every 2 seconds.
2. **Handling Voter Card Disputes / Cancellations:**
   - Open `Houses/admin/edit-votes.html`.
   - Filter by voter ID or click the **Cancelled Ballots** KPI card.
   - Click **Cancel Vote**, enter your officer name and cancellation reason.
   - The vote is immediately voided in Supabase, and the student is accredited to cast a fresh ballot.
   - *Ballot secrecy is maintained: candidate names are never exposed.*
3. **Adding Candidates Dynamically:**
   - In `Houses/admin/edit-votes.html`, click **+ Add Candidate to Participate**.
   - Select house, post, candidate name, and photo URL to instantly add candidates to the ballot.
4. **Finalizing Results:**
   - When polls close, click **Print Results** to print official winner certificates and export the complete audit spreadsheet to Excel.

---



---

## 🔒 Cloud Database & Security Configuration

The platform connects to Supabase Cloud for PostgreSQL storage and photo audit buckets:

- **Configuration File:** [`Houses/admin/supabase-config.js`](./Houses/admin/supabase-config.js)
  ```javascript
  const DEFAULT_SUPABASE_URL = "https://your-project.supabase.co";
  const DEFAULT_SUPABASE_KEY = "your-anon-publishable-key";
  ```
- **Database Tables:**
  - `ballots`: Holds all cast and cancelled ballots with timestamps and verification photo URLs.
  - `voters`: Tracks voter accreditation (`status`, `cast_at`, `verified_by`).
  - `candidates`: Stores approved candidate rosters per house and post.
  - `audit_logs`: Preserves immutable administrative action logs.
- **Storage Bucket:**
  - `voter-photos`: Stores compressed biometric audit snapshots.

---

## 🌐 Production Domain & Deployment Strategy

For full computer lab deployment with a custom domain (e.g. GoDaddy `.in`) and HTTPS:
- Read the complete operational guide: **[`DEPLOYMENT_PLAN.md`](./DEPLOYMENT_PLAN.md)** or **[`docs/DEPLOYMENT_AND_DOMAIN_SETUP_GUIDE.md`](./docs/DEPLOYMENT_AND_DOMAIN_SETUP_GUIDE.md)**.
- **Crucial Rule:** Desktop browsers strictly require **HTTPS/SSL** for webcam access (`navigator.mediaDevices.getUserMedia`) when accessed from external lab computers. Running via Cloudflare Tunnel or Cloudflare Pages provides free automatic SSL.

---

## 📚 Complete Technical Documentation

Comprehensive architectural and engineering documentation is maintained in the [`docs/`](./docs/) directory:

| Document | Description |
| :--- | :--- |
| **[1. Project Aim & Overview](./docs/PROJECT_AIM_AND_OVERVIEW.md)** | Electoral rules, houses, roles, and voter electorate breakdown. |
| **[2. Architecture & Tech Stack](./docs/ARCHITECTURE_AND_TECH_STACK.md)** | Static architecture, Pico.js AI, WebHID scanners, and Supabase sync. |
| **[3. Directory & File Guide](./docs/DIRECTORY_AND_FILE_GUIDE.md)** | Exhaustive explanation of every folder, HTML file, and script. |
| **[4. Database & Storage Schema](./docs/DATABASE_SCHEMA_AND_STORAGE.md)** | Table structures, SQL definitions, RLS, and storage rules. |
| **[5. Voting Kiosks & Biometrics Flow](./docs/VOTING_KIOSKS_AND_BIOMETRICS.md)** | Complete voting lifecycle, camera handling, and face detection guide. |
| **[6. Admin Portal & Operations](./docs/ADMIN_PORTAL_AND_OPERATIONS.md)** | Administrative actions, dispute resolution, and result export. |
| **[7. Developer Rules: What to Edit & What NOT to Edit](./docs/DEVELOPER_RULES_WHAT_TO_EDIT_AND_WHAT_NOT.md)** | **Strict invariants** and architectural boundaries for developers. |
| **[8. Current Progress & Changelog](./docs/CURRENT_PROGRESS_AND_CHANGELOG.md)** | Development milestones and verification status as of Nov 16, 2026. |
| **[9. Production Deployment & Domain Setup Guide](./docs/DEPLOYMENT_AND_DOMAIN_SETUP_GUIDE.md)** | GoDaddy `.in` domain, Cloudflare SSL, and laptop command protocol. |

---

*Engineered with precision for School House Elections 2026.*
