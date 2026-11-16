# 3. Directory & File Guide

Below is the complete structural map of this repository with detailed descriptions of every directory and file.

```
Election Spr 2026/
├── docs/                       # Official Comprehensive Documentation
├── Houses/                     # All Frontend Voting Kiosks & Admin Interfaces
│   ├── index.html              # Main Station Portal & Booth Registration Modal
│   ├── graphs.html             # Live Candidate Comparison Graphs
│   ├── assets/                 # Shared Station Assets & Core Drivers
│   ├── admin/                  # Administrative Console & Ballot Management
│   ├── bheeshma/               # Bheeshma House Polling Kiosk
│   ├── central/                # School Cabinet (Teacher-Only) Polling Kiosk
│   ├── gurudrona/              # Gurudrona House Polling Kiosk
│   ├── hanuman/                # Hanuman House Polling Kiosk
│   ├── karna/                  # Karna House Polling Kiosk
│   ├── vasistha/               # Vasistha House Polling Kiosk
│   └── vishwamithra/           # Vishwamithra House Polling Kiosk
├── voter_cards/                # High-Res Printable Voter ID Cards & A4 Sheets
├── scripts/                    # Python Data Parsing & Card Generation Scripts
├── 1supabase/                  # Supabase PostgreSQL Database Schemas
├── server/                     # Optional Python OTP server (Reference only)
├── 2026-27 staff details.xlsx  # Official Institutional Teaching Staff Roster
└── ELECTIONS HOUSES (1).xlsx   # Official Institutional Student Electoral Roll
```

---

## Detailed Directory Breakdown

### 1. `Houses/` Root
- **`index.html`:** The primary portal display. When a polling station computer is started, it prompts the officer to enter the **Booth Name** (e.g. "Booth 1", "Computer Lab A") and **Officer Name**. Contains cards linking to each house booth and admin portal.
- **`graphs.html`:** Fullscreen, high-contrast bar graph visualizations showing real-time vote comparisons for each candidate across all positions.

---

### 2. `Houses/assets/`
- **`booth-session.js`:** The foundational session manager. Manages station registration in `localStorage` (`last_registered_booth`, `last_registered_officer`) and `sessionStorage`. Exposes `window.getRegisteredBooth()` and `window.setRegisteredBooth()`. Also handles USB scanner gun pairing and provides `window.PendriveStorage` for local backup syncing.
- **`facefinder`:** Pre-trained 239 KB binary cascade model used by `pico.js` for real-time client-side face detection.
- **`scanner-gun.png`:** Illustrated graphic displayed on the kiosk's barcode scanning tab.

---

### 3. `Houses/admin/` (Administration & Audit)
- **`index.html`:** The master administrative dashboard. Displays live turnout KPIs, Master Register table (with filtering by House, Booth, Class, Section), progress meters, and a "Sync Roster to Supabase" button.
- **`app.js`:** Handles table rendering, multi-criteria filtering, search, and official results certificate generation.
- **`edit-votes.html`:** The dedicated ballot management workbench. Displays every cast ballot, allows photo inspection in a high-res popup, allows vote cancellation (with officer attribution), and includes the **"+ Add Candidate to Participate"** modal.
- **`edit-votes.js`:** Powers `edit-votes.html`. Features 0ms instant loading via `localStorage` snapshot cache (`spr_admin_snapshot_cache`), non-blocking photo URL resolution, and audit logging.
- **`supabase-config.js`:** The admin data adapter. Reads configuration from browser `localStorage` or `supabase.local.json`, issues REST queries to Supabase, and manages signed photo URLs.
- **`data.js`:** Static fallback roster data and position definitions.
- **`teachers.json`:** JSON compilation of the 87 faculty members.
- **`styles.css`:** Tailored styling for admin tables, cards, photo thumbnails, modals, and buttons.

---

### 4. Individual House Polling Booths (`bheeshma/`, `central/`, etc.)
Each of the 7 houses contains a standalone, self-contained kiosk booth:

| File | Purpose |
| :--- | :--- |
| **`index.html`** | 4-step voting interface: Step 1 (Scan/Enter ID), Step 2 (Confirm Identity), Step 3 (Select Candidates & Cast), Step 4 (Vote Casted / 3-Second Auto Reset). |
| **`app.js`** | Core kiosk controller: Handles scanner stream input, background camera warm-up, **Face Verification Guard modal**, face detection loop, and vote submission. |
| **`supabase-config.js`** | Kiosk backend adapter: Checks voter eligibility, verifies they haven't already voted, uploads the verification photo to Supabase Storage, and writes the ballot. |
| **`data.js`** | House metadata, list of open leadership roles, eligible candidate list, and eligible student voter roster. |
| **`pico.js`** | Lightweight, high-speed face detection engine (~5 KB) running in pure JavaScript. |
| **`facefinder`** | Local copy of the 239 KB Haar cascade binary model. |
| **`styles.css`** | House-specific theme color overrides (e.g. orange for Hanuman, royal blue for Gurudrona, emerald green for Central). |
| **`scanner-gun.png`** | Scanner graphic for the barcode kiosk panel. |

---

### 5. `voter_cards/` (Card Artifacts)
- **`a4_sheets/`:** High-resolution printable PDF / PNG sheets formatted for standard A4 paper (8 voter cards per sheet with cutting guidelines).
- Individual house subdirectories (`hanuman/`, `bheeshma/`, `teachers/`, etc.) containing single 850x560px PNG cards for every student and teacher, complete with photo, house badge, contact info, and high-contrast Code128 barcode.

---

### 6. `scripts/` (Automated Utilities)
- **`parse_roster.py`:** Reads official Excel spreadsheets and formats students and teachers into clean JSON structures.
- **`build_houses.py`:** Generates individual `data.js` files for each house directory.
- **`generate_voter_card_images.py`:** Uses Python Pillow and python-barcode to render pixel-perfect voter cards.
- **`build_all_voter_cards.py`:** Assembles individual cards into ready-to-print A4 sheets.

---

### 7. `1supabase/` (Cloud Database Definitions)
- **`schema.sql`:** The complete SQL schema definition for Supabase PostgreSQL, including tables, indexes, and Row Level Security (RLS) policies.
- **`supabase.local.json`:** Optional local configuration file specifying the Supabase project URL and anonymous key.
