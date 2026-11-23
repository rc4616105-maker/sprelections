# Session 1 Progress, Issues & Engineering Log

**Project:** School House Elections 2026  
**Session Window:** 2026-11-10 22:47 IST → 2026-11-11 00:22 IST  
**Current Milestone:** Frontend UI, Interactive Portals, Turnout Graphs & Admin Console Complete (Local Browser Persistence Active; Cloud Production Setup Pending)  
**Companion Spec:** [PROJECT_PLAN.md](./PROJECT_PLAN.md)

---

## 1. Session Overview & Architecture Direction

Session 1 took the system from an initial architectural draft to a working multi-portal web application tested across all pages in headless Microsoft Edge.

### Key Direction Decision
- [PROJECT_PLAN.md](./PROJECT_PLAN.md) initially outlined a full-stack **Next.js + TypeScript + Tailwind CSS + Supabase (PostgreSQL)** stack.
- **Decision in Session 1:** Switched the active implementation to a **zero-build static HTML / CSS / Vanilla JS multi-folder web application** backed by **Firebase Firestore Web SDK (`v13.2.0`)**, with an automatic browser `localStorage` + `BroadcastChannel` synchronized store whenever Firebase credentials remain placeholders (`YOUR_FIREBASE_API_KEY`).
- Each of the six houses lives in its own **self-contained directory** (`index.html`, `styles.css`, `data.js`, `firebase-config.js`, `app.js`).

---

## 2. Progress Completed (What Is Done)

### 2.1 Root Launcher & Live Turnout Graphs
- **`index.html`:** Warm Cream Editorial hub displaying the six single-line house cards (`Bishma House`, `Gurudrona House`, `Hanuman House`, `Karna House`, `Vasistha House`, `Vishwamithra House`), a top-right **Graphs** button, balanced card spacing across `100svh`, and a 3-step bottom guide strip (`1. Select your registered house above` · `2. Verify your School Admission ID` · `3. Select one candidate & cast your vote`).
- **`graphs.html`:** Standalone live house turnout comparison page displaying:
  - School-wide KPI cards (`Total Voted`, `Total Eligible Students`, `Remaining to Vote`).
  - Vertical house-wise bar chart (`voted / total eligible` + percentage) and per-house progress cards.
  - Adaptive back navigation (`← Back to Houses` when opened from `index.html`, `← Back to Admin` when opened from `admin/index.html?from=admin`).
  - Automatic in-place updates via `BroadcastChannel("election_spr_2026_sync")`, `storage` events, Firestore `onSnapshot`, and a `2000ms` fallback check — without full-page reload or wiping DOM nodes.

### 2.2 Six Self-Contained Voting Portals
- Directories created & populated: `bishma/`, `gurudrona/`, `hanuman/`, `karna/`, `vasistha/`, `vishwamithra/`.
- **4-Step Kiosk Workflow (`app.js`):**
  1. **Admission ID Entry:** Looks up student ID (`25` sample IDs `1001`–`1025`). Blocks empty IDs, unknown IDs, inactive records, **wrong house attempts** (`Does Not Belong to This House`), and **duplicate ballots** (`Vote Already Casted`).
  2. **Confirm Voter Identity (`Next`):** Displays student name, admission ID pill, class/section, house, re-authorization tag if a prior ballot was cancelled, and silently warms up the background camera stream (`warmUpBackgroundCamera()`).
  3. **Select Candidate & `Cast Vote`:** Lists approved candidates for that house only (`18` sample candidates across 6 houses for `House Captain`). Clicking **Cast Vote** automatically snaps the webcam photo (`captureAutomaticPhotoOnCast()`, no manual Capture/Retake button) and records the ballot atomically.
  4. **Vote Casted Confirmation:** Shows confirmation and counts down `2.8s` (with GPU-animated `scaleX` progress bar) before auto-resetting back to Step 1 for the next voter.
- **Clean UI Constraints Enforced:**
  - Zero colour words printed in UI copy (house colours are purely visual themes).
  - Removed dark mode across all views; standardized on Warm Cream Editorial light palette (`#faf6ee`, `#f3ece0`, `#fffdf9`, `#e5dccb`, `#141413`, `Fraunces` + `Plus Jakarta Sans` + `JetBrains Mono`).
  - Removed clutter elements requested during review: `"Verification Rejected"`, `"Voting Booth"`, coloured dots, quick-test chips, `"Local Demo Mode"` tags, `"All Houses"` links on booths, the Step 1 subtitle eligibility warning sentence (`Only verified <House> House students can proceed.`), and the bottom eligibility footer (`One vote per student · Registered ... members only · Automatic verification capture on submission`).

### 2.3 Redesigned Admin Console
- **`admin/index.html` & `admin/app.js`:**
  - Top bar with **Graphs** (`../graphs.html?from=admin`), conditional **Seed Firestore Sample Data** (when Firebase is connected), **Reset All Votes**, and **Refresh Now**.
  - **4 Interactive KPI Drill-Down Cards:** Clicking **Total Eligible Students**, **Active Accepted Votes**, **Cancelled Ballots**, or **Remaining Not Voted** opens a searchable, house-filterable drill-down table showing voter status, selected candidate, timestamp, **View Photo**, and **Cancel Vote**.
  - **6 Clickable House Cards:** Open house-specific views (`admin/house.html?house=<slug>`).
- **`admin/house.html` & `admin/house.js`:**
  - Sidebar navigation: `← All Houses`, **`Graphs`** (default), and **`Voters`**.
  - **`Graphs` View:** House KPIs + **Participants Vote Comparison Graph** (vertical column chart & candidate comparison rows updating smoothly in place every `2500ms` + live storage/channel events).
  - **`Voters` View:** Searchable & filterable (`Voted`, `Not Voted`, `Cancelled`) master student list for that house, **View Photo** modal, one-click **Cancel Vote** confirmation modal (without mandatory reason input; marks old ballot `cancelled`, logs action, and frees student to re-vote), and **Cancelled Vote History** table.

---

## 3. Finalized House Theme Palette

| House | Folder / Slug | Code | Primary Accent | Heading / Link Ink | Button Text (`--on-accent`) | Sample Student IDs |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bishma** | `bishma/` | `BISHMA` | `#eab308` | `#925c04` | `#141413` | `1001`–`1004` |
| **Gurudrona** | `gurudrona/` | `GURUDRONA` | `#2563eb` | `#1d4ed8` | `#fffdf9` | `1005`–`1008` |
| **Hanuman** | `hanuman/` | `HANUMAN` | `#f97316` | `#ea580c` | `#141413` | `1009`–`1013` |
| **Karna** | `karna/` | `KARNA` | `#b91c1c` | `#991b1b` | `#fffdf9` | `1014`–`1017` |
| **Vasistha** | `vasistha/` | `VASISTHA` | `#db2777` | `#be185d` | `#fffdf9` | `1018`–`1021` |
| **Vishwamithra** | `vishwamithra/` | `VISHWAMITHRA` | `#7c3aed` | `#6d28d9` | `#fffdf9` | `1022`–`1025` |

---

## 4. Issues Faced & How They Were Solved

| # | Issue Encountered | Root Cause | Solution Implemented |
| :---: | :--- | :--- | :--- |
| **1** | `"Verification Rejected"` error box and `"Vote Casted"` panel leaked onto Step 1 load | CSS `display: flex` on `.alert-box` / `.step-success-panel` had higher specificity than the browser default `[hidden]` rule | Added `[hidden] { display: none !important; }` across all six `styles.css` files and `admin/styles.css`, and removed all `"Verification Rejected"` text. |
| **2** | Captured webcam photos saved as solid black squares in `View Photo` | Offscreen/hidden `<video>` with `opacity: 0` or unready frame decoding yielded empty black video frames on draw | Positioned `.sr-camera` actively (`width: 320px; height: 240px; opacity: 0.001;`) and added an RGB brightness guard (`avgBrightness > 6`) inside `captureAutomaticPhotoOnCast()`, automatically falling back to a stylized Warm Cream booth snapshot if camera frames are dark or unavailable. |
| **3** | Old black test photos & stale votes persisted in browser storage | Earlier local test votes were stored under `election_spr_2026_store_v1` and `election_spr_2026_store_v2` | Bumped active local store key to `election_spr_2026_store_v3` across all `firebase-config.js` files and added auto-cleanup (`localStorage.removeItem` for `v1` and `v2`) on startup. |
| **4** | House colour names appearing in UI text & initial dark slate theme | Early cards displayed pills like `"Blue House"` and used dark background tokens | Stripped all colour words from visible UI text (using colours solely for visual theming) and rebuilt the styling in the Warm Cream Editorial light palette (`Fraunces` + `Plus Jakarta Sans`). |
| **5** | **Bhishma → Bishma** house naming mismatch | Folder and data entries initially used `bhishma` (`Bhishma`) instead of `bishma` (`Bishma`) | Replaced `bhishma/` directory with `bishma/`, updated `PROJECT_PLAN.md`, `index.html`, `admin/data.js`, and all portals; verified zero remaining `bhishma` references. |
| **6** | **Hanuman**, **Karna**, and **Vasistha** colours looked too similar on screen | Burnt terracotta (`#c2410c`) for Hanuman sat too close in hue/luminance to Karna (`#b91c1c`) and Vasistha (`#be185d`) on cream surfaces | Switched **Hanuman** to bright orange (`#f97316` accent, `#ea580c` text, `#141413` button ink), darkened **Karna** to deep dark crimson (`#b91c1c` accent, `#991b1b` hover/text), and kept **Vasistha** magenta-pink (`#db2777` / `#be185d`). Verified side-by-side via headless Edge screenshots. |
| **7** | `Vishwamithra House` wrapped to two lines & bottom area of landing/booth screens looked empty | Card heading font size was slightly too wide for single-column card widths, and containers did not span viewport height | Tuned `.house-name` with `clamp(...)` so all 6 headings stay single-line; expanded container widths, card padding/spacing, vertically centered booths (`100svh`), and added the 3-step guide strip at the bottom of `index.html`. |
| **8** | Full-DOM graph rebuild prevented CSS bar animations | Replacing `innerHTML` every poll cycle destroyed DOM elements so CSS transitions could not interpolate | Built DOM nodes once (`initNodes()` in `graphs.html` and `graphNodes` map in `admin/house.js`), updating only heights/scales/counts in place using GPU-composited `transform: scaleY(...)` / `scaleX(...)` with `--ease-spring` (`560ms`), `@keyframes barRiseGlow`, `@keyframes numberBump`, and `@media (prefers-reduced-motion: reduce)`. |
| **9** | Node.js / Firebase CLI unavailable in local environment | Machine does not have Node.js `>= 20` installed | Used browser-native ES module imports (`firebase-app.js` + `firebase-firestore.js` `v13.2.0`) plus Python `http.server` + headless Microsoft Edge for automated DOM & visual regression testing. |

---

## 5. Deviations Between `PROJECT_PLAN.md` & Current MVP

To align future sessions, note these deliberate simplifications made during Session 1 user reviews:

1. **Static Portals + Firebase Firestore instead of Next.js + Supabase:** Self-contained static folders allow opening/serving immediately without a Node build step.
2. **Automatic Photo Capture Without Step-2 Preview:** Photos are captured automatically the instant the voter clicks `Cast Vote` rather than adding a manual Capture/Retake screen in Step 2.
3. **One-Click Vote Cancellation Without Mandatory Reason:** Per Session 1 review, the cancellation reason textarea was removed from the Admin modal (`Cancelled by Admin` default stored in audit trail).
4. **No Second-Factor Credential (OTP/PIN) Yet:** Admission ID alone grants access on the assumption booths are teacher-supervised with auto photo capture.

---

## 6. Pending Work (For Session 2 / Before Production Go-Live)

### High Priority (Required Before Real School Election)
1. **Wire Real Firebase Project (`firebaseConfig`):**
   - Create a Firebase Web App + Cloud Firestore database in the Firebase Console.
   - Replace the placeholder `window.FIREBASE_CONFIG` block in all **7** `firebase-config.js` files (`bishma/`, `gurudrona/`, `hanuman/`, `karna/`, `vasistha/`, `vishwamithra/`, `admin/`) with real keys, then seed Firestore via Admin's **Seed Firestore Sample Data** button (or bulk import script).
   - Multi-device live sync across separate polling laptops depends on this step (currently votes only persist in a single browser's `localStorage`).
2. **Import Original School Student & Candidate Data:**
   - Replace the 25 sample students (`1001`–`1025`) and 18 sample candidates in `admin/data.js` and each house's `data.js` with the official school register (`admissionNo`, `fullName`, `className`, `section`, `houseCode`, `isActive`) and approved candidates.
   - Confirm whether elections include **multiple positions** (e.g., `Vice-Captain`, `Sports Captain`); currently the booths are scoped to a single position (`HOUSE_CAPTAIN` / `House Captain`).
3. **Admin Authentication & Firestore Security Rules (`firestore.rules`):**
   - Add Firebase Auth login gating `admin/index.html` and `admin/house.html` so only the Principal / authorized election staff can view identified ballots, inspect photos, reset votes, or cancel ballots.
   - Author strict `firestore.rules` (using the `firestore-rules-author` workflow) so voting kiosks cannot overwrite/read other students' ballots directly from browser devtools.
   - Confirm whether unsupervised access requires a 2nd-factor PIN/OTP per student.
4. **HTTPS Production Deployment & Real Webcam Verification:**
   - Deploy over HTTPS (Firebase Hosting or Vercel; note Firebase CLI locally requires installing Node.js `>= 20`, or deploy via GitHub/Vercel/Console).
   - Run an end-to-end camera permission & photo quality test on target voting devices (`getUserMedia` requires HTTPS in non-localhost origins).

### Nice-to-Have / Cleanups
- Add CSV/Excel student bulk import UI and final results CSV/PDF export inside `admin/`.
- Multi-house generator script moved into [scripts/build_houses.py](../scripts/build_houses.py) for repeatable updates across all 6 portals.
- Clean up or archive the reference `1/css/` folder before production hosting upload so deployment bundles remain tiny.

---

## 7. Quick Local Start & Sample Test IDs

Run locally via PowerShell in `c:\Users\Abhinav\Documents\Election Spr 2026`:

```powershell
python -m http.server 5500
```

Then open:
- **Launcher:** `http://127.0.0.1:5500/index.html`
- **House Turnout Graphs:** `http://127.0.0.1:5500/graphs.html`
- **Admin Console:** `http://127.0.0.1:5500/admin/index.html`

**Sample Test IDs:**
- **Bishma:** `1001`–`1004` (`1001`–`1003` candidates)
- **Gurudrona:** `1005`–`1008` (`1005`–`1007` candidates)
- **Hanuman:** `1009`–`1013` (`1009`–`1011` candidates)
- **Karna:** `1014`–`1017` (`1014`–`1016` candidates)
- **Vasistha:** `1018`–`1021` (`1018`–`1020` candidates)
- **Vishwamithra:** `1022`–`1025` (`1022`–`1024` candidates)

