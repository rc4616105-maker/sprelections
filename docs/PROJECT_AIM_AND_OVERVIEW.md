# 1. Project Aim & Electoral Overview

## Core Mission

The **School House Elections 2026** platform was engineered to conduct a completely tamper-proof, transparent, and seamless electronic election for a premier school institution.

The election combines physical voter accreditation (Voter ID cards with Code128 barcodes) with automated browser-based polling kiosks, real-time client-side face recognition, cloud data synchronization, and administrative oversight.

---

## Electoral Structure, Houses & Constituencies

The school electorate is divided into **6 Student House Constituencies** plus a **Central School Cabinet**:

| House / Unit | Constituency | Slug | Accent Color | Ink / Text Color | Total Voters | Boys | Girls | Electorate Rules |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bheeshma House** | **Gangotri** | `bheeshma` | `#eab308` (Golden Amber) | `#925c04` | **168** | 86 | 82 | Registered Bheeshma students + all Teachers |
| **Gurudrona House** | **Trimbakeshwar** | `gurudrona` | `#2563eb` (Royal Blue) | `#1d4ed8` | **181** | 95 | 86 | Registered Gurudrona students + all Teachers |
| **Hanuman House** | **Yamunotri** | `hanuman` | `#f97316` (Warm Orange) | `#ea580c` | **181** | 95 | 86 | Registered Hanuman students + all Teachers |
| **Karna House** | **Manasarovar** | `karna` | `#b91c1c` (Crimson Red) | `#991b1b` | **180** | 77 | 103 | Registered Karna students + all Teachers |
| **Vasistha House** | **Mahabaleshwar** | `vasistha` | `#db2777` (Deep Rose) | `#be185d` | **184** | 87 | 97 | Registered Vasistha students + all Teachers |
| **Vishwamithra House** | **Amarkantak** | `vishwamithra` | `#7c3aed` (Royal Purple) | `#6d28d9` | **191** | 95 | 96 | Registered Vishwamithra students + all Teachers |
| **School Cabinet** | *Central Council* | `central` | `#059669` (Emerald Green) | `#047857` | **88** | - | - | **Teachers & Faculty ONLY** (Students blocked) |

---

## Electorate Demographics

The verified total electorate comprises **1,173 registered voters**:

- **1,085 Students across Classes 6 through 10:**
  - **535 Boys**
  - **550 Girls**
  - Verified across 6 House Constituencies (Bheeshma: 168, Gurudrona: 181, Hanuman: 181, Karna: 180, Vasistha: 184, Vishwamithra: 191).
- **88 Teaching & Administrative Faculty Members:**
  - Authorized for universal voting across all houses and central cabinet positions (Voter IDs `SPRCOR872`, `SPRPRI...`, `6001`–`6087`).
- **140 Contesting Candidates:**
  - Contesting across 29 total leadership positions (5 School Cabinet + 24 House Captains/Vice Captains).

---

## Open Leadership Positions

### A. House Leadership Positions (4 Roles per House)
For all 6 House booths, each eligible voter casts a ballot selecting 1 candidate for each of the 4 open positions:

1. **Boys Captain** (`CAPTAIN_BOY` / `Vote_10_Boy`): Class 10 Boys
2. **Girls Captain** (`CAPTAIN_GIRL` / `Vote_10_Girl`): Class 10 Girls
3. **Boys Vice Captain** (`VICE_CAPTAIN_BOY` / `Vote_9_Boy`): Class 9 Boys
4. **Girls Vice Captain** (`VICE_CAPTAIN_GIRL` / `Vote_9_Girl`): Class 9 Girls

### B. School Cabinet Executive Positions (5 Roles)
Voted exclusively by teaching faculty at the Central Booth ([Houses/central/index.html](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/Houses/central/index.html)):

1. **Head Boy** (`HEAD_BOY`)
2. **Head Girl** (`HEAD_GIRL`)
3. **Vice Head Boy** (`VICE_HEAD_BOY`)
4. **Vice Head Girl** (`VICE_HEAD_GIRL`)
5. **Sports Captain** (`SPORTS_CAPTAIN`)

---

### C. Teacher Universal Polling Booth (All-in-One 29-Role Ballot)
To provide faculty and teachers with a seamless voting experience, a dedicated **Teacher Universal Polling Booth** (`Houses/teachers/index.html`) is provided:
- **Electorate**: Teachers & Faculty ONLY (Voter IDs `6001`–`6087`, plus universal demo ID `0000`).
- **Scope**: Combines all **5 School Cabinet** leadership posts and all **24 House Leadership** posts (4 roles across Bheeshma, Gurudrona, Hanuman, Karna, Vasistha, and Vishwamithra).
- **Consolidated Flow**: Instead of visiting 7 distinct polling booths, teachers cast their complete 29-role vote in a single continuous session with interactive category navigation and a single face verification capture.

---

## Electorate Demographics

The total electorate comprises **966 registered voters**:

- **879 Students:**
  - Distributed across Classes 6 through 10 in Sections A, B, C, D, Ashoka, and Chakravarthi.
  - Assigned to their specific house based on official institutional rosters (`ELECTIONS HOUSES (1).xlsx`).
  - Restricted strictly to voting in their own House kiosk.
- **87 Teachers & Faculty Members:**
  - Assigned universal voting rights (`houseCode: "ALL"`, `isStaff: true`, Voter IDs `6001` through `6087`).
  - Derived from official staff records (`2026-27 staff details.xlsx`).
  - Permitted to vote in any student house election and exclusively elect the School Cabinet.
- **Demo / Testing Account:**
  - Voter ID `0000` (`Demo User`, `houseCode: "ALL"`). Universally active across all kiosks for system verification without altering genuine student counts.

---

## Security & Anti-Fraud Model

The voting process implements multi-layered security controls:

```
[Voter ID Card] 
       │ (Code128 Barcode Scan)
       ▼
[Eligibility Check] ──► Block if already voted OR wrong house
       │ (Confirmed)
       ▼
[Candidate Selection] ──► Must choose 1 candidate for all open roles
       │ (Ready to Cast)
       ▼
[Face Verification Guard] ──► Real-time webcam check (Pico.js + Haar Cascade)
       │                     Anti-obstruction / Anti-hand lens detection
       ▼
[Encrypted Ballot Record] ──► Upload photo to Supabase Storage
                             Write ballot with Booth Name & Officer ID
                             Mark voter as VOTED (prevents second vote)
```

1. **Double-Voting Prevention:** Once a voter submits a ballot, their record is instantly marked as `voted` in the database with their timestamp and photo reference. Any subsequent attempt to scan their card displays an alert: *"Ballot Already Recorded"*.
2. **Biometric Face Verification:** Every ballot requires live visual confirmation. The kiosk detects that an actual human face is present in front of the lens and captures a verification photo directly to the cloud.
3. **Station & Officer Accountability:** Every kiosk registers a `Booth Name` (e.g. "Computer Lab Station 3") and `Officer Name`. All votes and cancellations are tagged with this attribution.

---

## Two-Stage Electoral Lifecycle & Electoral College Architecture

The election is structured into an authentic, transparent two-stage parliamentary lifecycle:

```
┌────────────────────────────────────────────────────────────────────────┐
│               STAGE 1: HOUSE GENERAL ELECTIONS                         │
│  All 1,085 students across Classes 6–10 vote in their designated       │
│  6 House Booths (Electing 4 Captains/VCs per house = 24 Leaders)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│     ADMIN LIFECYCLE ACTION: "FREEZE HOUSE POLLING & TALLY WINNERS"     │
│  • Admin panel locks the 6 House booths ("House Polling Concluded")    │
│  • System automatically tallies all accepted ballots across 6 houses   │
│  • Identifies top vote-getters for all 24 positions                    │
│  • Locks winner records into `ELECTED_HOUSE_WINNERS_2026`              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│           STAGE 2: RESULT DECLARATION & SCRATCH CARD REVEAL            │
│  • Held in the school auditorium/hall via `Result declaration/`        │
│  • Wheel of Houses spins and dynamic Scratch Cards reveal the 24       │
│    official newly elected House Captains & Vice Captains on screen     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│         STAGE 3: SCHOOL CABINET ELECTORAL COLLEGE POLLING              │
│  • School Cabinet Booth (`Houses/central/`) unlocks for the 24 winners │
│  • The 24 winners scan their Voter IDs and are recognized as:          │
│    "🎖️ Authorized Electoral College Voter (1 of 24 House Leaders)"    │
│  • They cast ballots electing the Central School Cabinet               │
│    (Head Boy, Head Girl, Sports Captain, Cultural & Discipline Sec)    │
└────────────────────────────────────────────────────────────────────────┘
```

### Operational Rules of the Two-Stage Flow:
1. **House Booth Freeze State:** Once polling hours end for general students, the election officer freezes the house kiosks from the Admin dashboard. Attempting to scan a card displays `House Polling Concluded · Tally in Progress`, preventing any unverified post-deadline votes.
2. **Automated Winner Computation:** The tally engine iterates through all 6 house constituencies, aggregates accepted ballots per candidate, and generates the immutable `ELECTED_HOUSE_WINNERS_2026` dataset.
3. **Direct Scratch Card Synchronization:** The Result Declaration Ceremony automatically ingests this dataset, allowing students and teachers to scratch off candidate cards to reveal the true winners live.
4. **Electoral College Authorization:** The School Cabinet kiosk validates each entrant's Voter ID against `ELECTED_HOUSE_WINNERS_2026`. Non-winners and ordinary students are strictly blocked with an explanatory error notice, guaranteeing that only the 24 legitimate house leaders (plus faculty) elect the Central Cabinet.
