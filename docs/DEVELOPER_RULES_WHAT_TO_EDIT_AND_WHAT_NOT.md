# 7. Developer Rules: What to Edit & What NOT to Edit

> [!IMPORTANT]
> **MANDATORY READING FOR ANY DEVELOPER OR AI AGENT WORKING ON THIS REPOSITORY.**  
> If you open this project in another account or environment, you must adhere strictly to these engineering boundaries. Violating these rules will break the polling stations or corrupt election data.

> [!CAUTION]
> **MANDATORY DOCUMENTATION SYNC RULE:**  
> **Whenever ANY change, feature, bugfix, UI tweak, or schema modification is done in this project, the documentation in the `docs/` folder MUST be updated immediately in the same turn.**  
> Never commit or claim a task complete without keeping `docs/` in 100% synchronization.

---

## Part 1: Golden Rules — What You Must NEVER Do

### 1. NEVER Introduce a Backend Server for Voter Authentication or Voting
- **Why:** The entire kiosk architecture is intentionally engineered as a **pure static client-side web application**. Polling kiosks must operate independently on standard static web servers (e.g. VS Code Live Server, Apache, Netlify).
- **The Trap:** Do not build a Python Flask, FastAPI, or Node.js Express server to handle login, card verification, or voting. All voting logic runs directly in `app.js` and communicates with Supabase via direct REST endpoints in `supabase-config.js`.

### 2. NEVER Remove or Alter the Binary `facefinder` Model or `pico.js`
- **Why:** Every polling booth contains an exact copy of the 239,632-byte pre-trained Haar cascade binary `facefinder` and the ~5 KB `pico.js` face detector.
- **The Trap:** Do not replace `pico.js` with heavy npm packages (like face-api.js or TensorFlow.js). They require multi-megabyte model downloads and GPU WebGL shaders that fail or crash on low-powered school laptops and Chromebooks.

### 3. NEVER Send `booth_name` to the `voters` Table Payload
- **Why:** In the database schema, the `booth_name` column is defined on the **`ballots`** table.  
  It is **NOT** a column on the `voters` table.
- **The Trap:** If you pass `booth_name` when making a `POST` or `PATCH` request to `/rest/v1/voters`, Supabase will immediately reject the request with:
  ```json
  { "code": "PGRST204", "message": "Could not find the 'booth_name' column of 'voters' in the schema cache" }
  ```
  Keep `booth_name` strictly inside the `ballots` insert payload.

### 4. NEVER Break Teacher Universal Eligibility (`houseCode: "ALL"`)
- **Why:** All 87 teaching staff members (Voter IDs `6001` through `6087`) have `houseCode: "ALL"` and `isStaff: true`.
- **The Rule:**
  - In student house booths (`bheeshma`, `gurudrona`, `hanuman`, `karna`, `vasistha`, `vishwamithra`), teachers are permitted to vote for House Captains.
  - In the Central booth (`Houses/central/index.html`), teachers are the **exclusive** voters for the School Cabinet (students are blocked).
  - Never enforce single-house restriction on voters with `houseCode: "ALL"`.

### 5. NEVER Expose Individual Student Choices in the Admin Master Register
- **Why:** The **Secret Ballot principle** is an institutional requirement. Displaying who each student voted for alongside their name in public administrative tables compromises ballot secrecy.
- **The Rule:** In `edit-votes.html`, group ballots by voter into **1 consolidated row per voter**, displaying `✓ Voted (All 4 Posts)` (or 5 for Cabinet) with `Ballot Choice Confidential`.

### 6. NEVER Forget Cache-Busting Query Strings on `<script>` Tags
- **Why:** Kiosk browsers aggressively cache JavaScript files.
- **The Rule:** Every `<script>` tag in `index.html` across all 7 houses and admin pages must include a version parameter, currently set to:
  ```html
  <script src="../assets/booth-session.js?v=995"></script>
  <script defer src="./pico.js?v=995"></script>
  <script defer src="./data.js?v=995"></script>
  <script defer src="./supabase-config.js?v=995"></script>
  <script defer src="./app.js?v=995"></script>
  ```
  Whenever you modify any JS file, increment the version string across all corresponding HTML files (e.g. `?v=996`) so browsers update without requiring manual cache clearing.

### 7. NEVER Hardcode Supabase Service Role Secret Keys
- Only public anonymous publishable keys (`anon`) may be used in the client code. Keys are dynamically read from `localStorage.getItem("election_spr_2026_sb_cfg_v1")` or `supabase.local.json`.

---

## Part 2: What and How to Edit Safely

### A. How to Add or Edit Candidates
There are two safe methods to update candidates:

1. **Method 1: Interactive Admin Workbench (Recommended)**
   - Open [Houses/admin/edit-votes.html](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/Houses/admin/edit-votes.html).
   - Click the green **"+ Add Candidate to Participate"** button.
   - Enter Candidate Name, Class, Section, select their Electoral Post (House role or Cabinet role), choose the Target House, and click **Save Candidate**.
   - This writes directly to the Supabase `candidates` table.
2. **Method 2: Static Fallback Array in `data.js`**
   - Open `Houses/<house>/data.js`.
   - Locate the `houseCandidates` array.
   - Add an entry with this exact schema:
     ```javascript
     {
       id: "HAN-10A-CAND-NEW",
       admissionNo: "10099",
       fullName: "STUDENT NAME",
       className: "10",
       section: "A",
       houseCode: "HANUMAN",
       positionId: "CAPTAIN_BOY",
       positionName: "Boys Captain",
       isApproved: true,
       photoUrl: ""
     }
     ```

---

### B. How to Connect a New Supabase Project

If you clone this project to another account or setup a new Supabase project:
1. Run the database migration script [1supabase/schema.sql](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/1supabase/schema.sql) in your Supabase SQL Editor.
2. Create a public Storage Bucket named **`voter-photos`**.
3. Open [Houses/admin/index.html](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/Houses/admin/index.html).
4. Enter your Supabase Project URL (`https://xyz.supabase.co`) and Publishable Anon Key in the config modal, and click Save.
5. Click **"Sync Roster to Supabase"** to populate all 966 voters into your new database with one click.

---

### C. How to Adjust House Theme Colors & Branding

Open `Houses/<house>/styles.css` and adjust the CSS Custom Properties in `:root`:

```css
:root {
  --house-accent: #f97316;        /* Primary button & header accent */
  --house-accent-hover: #fb923c;  /* Hover state */
  --house-accent-text: #ea580c;   /* High-contrast text accent */
  --house-on-accent: #141413;     /* Text on top of accent button */
  --house-subtle: rgba(249, 115, 22, 0.11);
  --house-border-glow: rgba(249, 115, 22, 0.42);
}
```

---

### D. How to Re-generate Physical Voter Cards

If new students join or cards need reprinting:
1. Update `ELECTIONS HOUSES (1).xlsx` or `2026-27 staff details.xlsx`.
2. Run data parsing:
   ```bash
   python scripts/parse_roster.py
   python scripts/build_houses.py
   ```
3. Generate individual PNG cards with barcodes:
   ```bash
   python scripts/generate_voter_card_images.py
   ```
4. Assemble cards into printable 8-per-page A4 sheets:
   ```bash
   python scripts/build_all_voter_cards.py
   ```
   The printable PDF/PNG files will be saved in `voter_cards/a4_sheets/`.

---

## Part 3: Troubleshooting & Known Traps

| Problem / Symptom | Root Cause | Solution |
| :--- | :--- | :--- |
| **"Could not find the 'booth_name' column of 'voters' in schema cache"** | Code attempted to send `booth_name` to `/rest/v1/voters`. | Remove `booth_name` from the voters payload. It belongs only on `ballots`. |
| **Delay / Empty table on `edit-votes.html`** | Browser waiting on Netlify proxy health-check or blocking on storage signatures. | Already resolved via `spr_admin_snapshot_cache` and non-blocking signing. Ensure `localStorage` is not disabled. |
| **Camera error / webcam not opening** | Browser blocked camera access or untrusted origin. | Webcams require `http://127.0.0.1:5500` or `https://`. If running on a local LAN IP (e.g. `192.168.x.x`), Chrome flags must allow insecure origins for media capture. |
| **Barcode scanner gun doesn't register** | Input focus lost or USB scanner configured with non-standard prefix. | Click the "Scan Barcode" tab to refocus `#barcode-scanner-stream`. Ensure scanner gun is configured for standard USB keyboard emulation with `CR/Enter` suffix. |
| **Face detection modal doesn't detect face** | Lighting is too dark, or camera lens is smudged/covered. | Check the badge message. Ensure proper front-facing lighting. Anti-hand detection requires standard ambient brightness and variance. |
