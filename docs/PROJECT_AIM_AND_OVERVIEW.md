# 1. Project Aim & Electoral Overview

## Core Mission

The **School House Elections 2026** platform was engineered to conduct a completely tamper-proof, transparent, and seamless electronic election for a premier school institution.

The election combines physical voter accreditation (Voter ID cards with Code128 barcodes) with automated browser-based polling kiosks, real-time client-side face recognition, cloud data synchronization, and administrative oversight.

---

## Electoral Structure & Houses

The school electorate is divided into **6 Student Houses** plus a **Central School Cabinet**:

| House / Unit | Slug | Accent Color | Ink / Text Color | Electorate Rules |
| :--- | :--- | :--- | :--- | :--- |
| **Bheeshma House** | `bheeshma` | `#eab308` (Golden Amber) | `#925c04` | Registered Bheeshma students + all Teachers |
| **Gurudrona House** | `gurudrona` | `#2563eb` (Royal Blue) | `#1d4ed8` | Registered Gurudrona students + all Teachers |
| **Hanuman House** | `hanuman` | `#f97316` (Warm Orange) | `#ea580c` | Registered Hanuman students + all Teachers |
| **Karna House** | `karna` | `#b91c1c` (Crimson Red) | `#991b1b` | Registered Karna students + all Teachers |
| **Vasistha House** | `vasistha` | `#db2777` (Deep Rose) | `#be185d` | Registered Vasistha students + all Teachers |
| **Vishwamithra House** | `vishwamithra` | `#7c3aed` (Royal Purple) | `#6d28d9` | Registered Vishwamithra students + all Teachers |
| **School Cabinet** | `central` | `#059669` (Emerald Green) | `#047857` | **Teachers & Faculty ONLY** (Students blocked) |

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
