# 6. Admin Portal & Operations Guide

> [!IMPORTANT]
> **MANDATORY DOCUMENTATION SYNC POLICY:**  
> If any UI changes, new buttons, or backend methods are modified in the admin workbench or dashboard, the documentation in `docs/` must be updated immediately in the same turn.

The election administration suite provides real-time oversight, fraud auditing, candidate registration, and official results reporting.

---

## 1. Master Administration Dashboard (`Houses/admin/index.html`)

Access: [`http://127.0.0.1:5500/Houses/admin/index.html`](http://127.0.0.1:5500/Houses/admin/index.html)

### Key Features
1. **Live Turnout KPIs:**
   - **Total Eligible Voters:** Automatically tallies the 879 students + 87 teachers = **966 total electorate**.
   - **Active Accepted Votes:** Count of verified unique voters who completed voting across all stations.
   - **Cancelled Ballots:** Count of unique voters whose ballots were voided.
   - **Remaining Not Voted:** Real-time count of eligible voters who have not yet voted.
2. **Master Electoral Register & Drilldown Panels:**
   - **Active Accepted Voters View:** 1 row per voter with `<span class="badge badge-success">Voted (4/4)</span>`.
   - **Cancelled Ballots Drilldown View (Secret Ballot 1-Row Consolidation):**  
     - Grouped into **1 consolidated row per voter** (instead of 4 repeated rows).
     - **Ballot Confidentiality Enforced:** Replaced the previous `Previous Choice` column with `Cancelled Status` showing:
       `<span class="badge badge-warning">Cancelled (4 Posts)</span>` and `Ballot Choice Confidential`.
       Candidate choices are never displayed!
     - Displays **Cancelled By** (e.g. `👤 rc4616105@gmail.com`), timestamp, voter photo, and **Pending Re-vote** status.
     - Includes a direct link to **Manage in Edit Votes →**.
3. **House Turnout Cards:**
   - Six individual House cards + Central School Cabinet card with progress meters and vote counters.
4. **Operations Buttons:**
   - **Sync Roster to Supabase:** Bulk-synchronizes the static student and faculty rosters into the Supabase database.
   - **Graphs:** Opens live, full-screen candidate comparison charts.
   - **Print Results:** Renders a formal, high-resolution official election certificate suitable for printing and institutional signing.

---

## 2. Edit & Manage Votes Workbench (`Houses/admin/edit-votes.html`)

Access: [`http://127.0.0.1:5500/Houses/admin/edit-votes.html`](http://127.0.0.1:5500/Houses/admin/edit-votes.html)

This workbench is the central control panel for ballot auditing, photo verification, and vote adjustments.

### Key Capabilities

#### A. Secret Ballot 1-Row Voter Consolidation (Voter Privacy Protection)
In compliance with the **Secret Ballot principle**, individual voters are displayed in **1 consolidated row** rather than 4 repetitive rows:
- **Masked Candidate Choices:** The table does **not** reveal which specific candidates the voter voted for (preventing controversy, peer pressure, or privacy violations).
- **Voted Status Badge:** Cleanly confirms completion:
  - `<span class="badge badge-success">✓ Voted (All 4 Posts)</span>` for student houses.
  - `<span class="badge badge-success">✓ Voted (All 5 Posts)</span>` for the School Cabinet.
  - Subtitle note: `Ballot Choice Confidential`.
- **4× Cleaner & Faster:** The table is 4 times shorter, making it fast and easy to navigate and review.

#### B. 0ms Instant Load (Local Snapshot Cache)
On opening, the page renders immediately from a `localStorage` snapshot cache (`spr_admin_snapshot_cache`). It does not show an empty white table; it displays recent data in 0ms while refreshing live data from Supabase in the background.

#### C. Verification Photo Inspection
- Every voter row displays a biometric verification photo thumbnail captured when the vote was cast.
- Clicking the thumbnail opens a high-resolution modal displaying the voter's face, timestamp, and house accreditation.

#### D. Ballot Cancellation with Officer Attribution (All Posts at Once)
- When a vote must be voided (e.g. card was scanned by mistake):
  1. The officer clicks **Cancel Vote** on the voter's row.
  2. Prompts to confirm cancelling all leadership role ballots for this voter.
  3. Records the **Officer Name** (`cancelled_by`).
  4. Calls `AdminBackend.cancelStudentBallots(admissionNo, reason, actorName)` in Supabase, updating all ballot records to `cancelled`.
  5. The voter's accreditation changes to allow re-authorization if deemed appropriate.
  6. In the **Cancelled Ballots** tab, the table clearly displays **Who cancelled the vote** (`cancelled_by`), the time, and the stated reason.

#### E. Ballot Deletion & Reset
- Clicking **Delete** removes the voter's ballot entries completely and resets the voter's status to `eligible`, allowing them to vote again if authorized by the chief election commissioner.

#### F. Dynamic Candidate Addition: "+ Add Candidate to Participate"
- Located at the top-right of the table.
- Opens an interactive modal allowing administrators to register new participating candidates on the fly:
  - **Candidate Full Name**
  - **Class & Section** (e.g. Class 10, Section Ashoka)
  - **Electoral Post:** Select either a House Leadership role (Boys Captain, Girls Captain, Boys Vice Captain, Girls Vice Captain) or a School Cabinet role (Head Boy, Head Girl, Vice Head Boy, Vice Head Girl, Sports Captain).
  - **Target House:** Select the relevant house or School Cabinet.
- Submitting saves the candidate directly into the Supabase `candidates` table and makes them immediately available in polling kiosks!

#### G. Interactive KPI Cards & Filter Synchronization
The 4 KPI cards at the top (**Total Accepted Ballots**, **Cancelled Ballots**, **Eligible Master Roster**, and **Remaining Not Voted**) function as active filter triggers:
- Clicking any card applies the highlighted active state (`is-active`).
- Automatically updates the dropdown `<select id="ballot-status-filter">`.
- Re-renders the table and updates the heading/subtitle immediately to match the selected category.
- Changing the dropdown manually also updates the corresponding KPI card highlight in real time.

---

## 3. Station Booth Registration (`Houses/assets/booth-session.js`)

When a kiosk station computer boots up and opens `Houses/index.html`:

1. If no station identity is saved in `sessionStorage` or `localStorage`, a **Register Polling Booth** modal appears automatically.
2. The presiding officer fills in:
   - **Booth / Station Name** (e.g. "Booth 1", "Computer Lab A", "Library Kiosk 2").
   - **Officer Name** (e.g. "Mr. Sharma", "Officer Jane Doe").
3. Saves to `localStorage.getItem("last_registered_booth")` and `sessionStorage.getItem("election_booth_name")`.
4. Every vote cast from that device is permanently stamped with `booth_name` on its ballot record!
