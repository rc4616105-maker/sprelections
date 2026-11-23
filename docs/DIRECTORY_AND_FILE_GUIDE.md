# 3. Directory & File Guide

Below is the complete structural map of this repository with detailed descriptions of every directory and file.

```
Election Spr 2026/
├── index.html                  # Root Instant Redirect to /Houses/index.html (Netlify & Web Server Root)
├── netlify.toml                # Netlify Zero-Build Configuration with Root 302 Redirect
├── docs/                       # Official Comprehensive Documentation
├── Houses/                     # All Frontend Voting Kiosks, Turnout Graphs & Admin Console
│   ├── index.html              # Main Polling Station Portal (House & Teacher Booths, Graphs CTA)
│   ├── graphs.html             # Live Realtime Double-Bar Turnout Graphs (Boys vs Girls, +1 Pulse)
│   ├── assets/                 # Shared Station Assets & Core Drivers
│   ├── admin/                  # Administrative Console, Ballot Workbench & Live Voters Stream
│   │   ├── index.html          # Master Admin Dashboard (KPIs, Master Register, Audit Controls)
│   │   ├── house.html          # House-Specific Admin Console (Compact Candidate Graphs, View Switcher)
│   │   ├── house.js            # House Admin Controller (Strict 168 Roster Filter, Live Polling)
│   │   ├── edit-votes.html     # Secret Ballot Management & Candidate Participation Workbench
│   │   ├── live-voters/        # Dedicated Live Incoming Voters Stream
│   │   │   └── index.html      # Realtime Voter Stream (Audio Chime, Pulse Animation, Photo Modal)
│   │   ├── data.js             # Master Roster (1,085 Students & 140 Candidates)
│   │   ├── teachers.js         # Master Faculty Roster (88 Teaching Staff Members)
│   │   └── supabase-config.js  # Admin Supabase REST Adapter & Pendrive Local Backup Driver
│   ├── bheeshma/               # Bheeshma House Kiosk (Gangotri Constituency - Amber)
│   ├── central/                # School Cabinet Teacher-Only Kiosk (Emerald Green)
│   ├── gurudrona/              # Gurudrona House Kiosk (Trimbakeshwar Constituency - Royal Blue)
│   ├── hanuman/                # Hanuman House Kiosk (Yamunotri Constituency - Warm Orange)
│   ├── karna/                  # Karna House Kiosk (Manasarovar Constituency - Crimson Red)
│   ├── teachers/               # Universal Teacher Kiosk (29-Role Ballot across All Houses & Cabinet)
│   ├── vasistha/               # Vasistha House Kiosk (Mahabaleshwar Constituency - Deep Rose)
│   └── vishwamithra/           # Vishwamithra House Kiosk (Amarkantak Constituency - Royal Purple)
├── voter_cards/                # High-Res Printable Voter ID Cards & A4 Sheets
├── scripts/                    # Python Data Parsing & Card Generation Scripts
├── 1supabase/                  # Supabase PostgreSQL Database Schemas & Constraints
└── ELECTIONS HOUSES (1).xlsx   # Official Institutional Student Electoral Roll
```

---

## Detailed Directory Breakdown

### 0. Project Root & Deployment
- **`index.html`:** Root entry point. When hosted on Netlify, GitHub Pages, or a local server root, it instantly redirects incoming requests to `/Houses/index.html` with query parameters preserved.
- **`netlify.toml`:** Production Netlify configuration instructing the edge router to publish the root directory and redirect `/` to `/Houses/index.html` with a 302 HTTP status.

---

### 1. `Houses/` Root
- **`index.html`:** The primary public election portal. Features high-contrast cards for all 6 Houses (displaying both the House name and its associated Constituency), the Teachers/Staff Cabin card, and the Live Turnout Graphs CTA.
- **`graphs.html`:** Real-time turnout analytics dashboard showing side-by-side double bar charts (Boys vs Girls) for all 6 houses. Features:
  - Total electorate KPIs (1,085 Total Voted, Boys Turnout, Girls Turnout, Pending to Vote).
  - Floating green `+1` animation directly above the affected house column when a new vote arrives.
  - Double-click anywhere on empty background space to toggle fullscreen mode cleanly.
  - Clickable title navigation that seamlessly returns to `./index.html` (or `./admin/index.html` if navigated from the admin panel).

---

### 2. `Houses/admin/` (Administration & Live Operations)
- **`index.html`:** The master administrative dashboard displaying overall turnout KPIs, Master Register table (with filtering by House, Booth, Class, Section), progress meters, and candidate seed controls.
- **`house.html` & `house.js`:** Dedicated per-house admin console. Features compact KPI cards, quick view switcher buttons (`📊 Graphs`, `👥 Master Voters List`), and candidate vote comparison bar charts styled with authentic house colors without requiring vertical scrolling. Strictly isolates student voters (e.g. 168 Bheeshma students) from faculty.
- **`live-voters/index.html`:** Dedicated Live Incoming Voters Stream screen designed for election monitoring screens. Features a Web Audio chime on every new vote, green slide-in pulse animation, voter admission/name/class/house details, live search, house filters, and a high-resolution photo verification modal.
- **`edit-votes.html` & `edit-votes.js`:** Secret Ballot management workbench. Allows inspecting cast ballots, photo inspection, vote cancellation with officer attribution, and dynamic candidate participation additions.
- **`supabase-config.js`:** Pure client-side static Supabase REST adapter pre-configured with project credentials for zero-prompt automatic loading. Also orchestrates USB pendrive local backup writes via Web File System Access API.

---

### 3. Universal Teacher Polling Booth (`Houses/teachers/`)
- **`index.html` & `app.js`:** Dedicated 29-role unified polling booth for teaching faculty. Combines all 5 School Cabinet roles and all 24 House leadership roles (4 roles × 6 houses) into an interactive zero-scroll kiosk with dynamic house theme color switching.
- **`data.js`:** Validated candidate dataset containing all 140 contesting candidates across all 29 posts with photos and symbols.

---

### 4. Individual House Polling Booths (`bheeshma/`, `gurudrona/`, etc.)
Each house booth is a completely self-contained, 4-step EVM polling kiosk:
- **`index.html`:** 4-step voting interface: Step 1 (Scan/Enter ID), Step 2 (Confirm Identity), Step 3 (Select Candidates & Cast), Step 4 (Vote Casted / 3-Second Auto Reset). Displays the house title and its assigned constituency name in a lighter shade of the house accent color.
- **`app.js`:** Hardware barcode gun scanner input, camera warm-up, offline Pico.js face detection loop, and ballot submission.
- **`supabase-config.js`:** Database client with pre-configured cloud credentials for instant connection.
- **`styles.css`:** Tailored house color schemes (Golden Amber, Royal Blue, Warm Orange, Crimson Red, Deep Rose, Royal Purple).

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
