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
