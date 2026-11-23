# 4. Database Schema & Storage Architecture

The application uses **Supabase (PostgreSQL 15)** via direct PostgREST calls and the Supabase Storage API.

---

## 1. Table: `ballots`

The authoritative ledger of all cast votes. Each role voted for generates 1 ballot row (4 rows for a complete House ballot, 5 rows for a School Cabinet ballot).

```sql
CREATE TABLE IF NOT EXISTS public.ballots (
  id TEXT PRIMARY KEY,                       -- e.g. "BLT-K29FA-6082-CAPTAINBOY"
  election_id TEXT NOT NULL DEFAULT 'ELECTION_2026',
  admission_no TEXT NOT NULL,                 -- Voter ID / Admission number
  house_code TEXT NOT NULL,                   -- "HANUMAN", "BHEESHMA", "CENTRAL", etc.
  position_id TEXT NOT NULL,                  -- "CAPTAIN_BOY", "HEAD_BOY", etc.
  position_name TEXT NOT NULL,                -- "Boys Captain", "Head Boy", etc.
  candidate_id TEXT NOT NULL,                 -- Candidate identifier
  candidate_name TEXT NOT NULL,               -- Full name of selected candidate
  photo_url TEXT,                             -- Relative path in 'voter-photos' bucket
  booth_name TEXT DEFAULT 'Booth 1',          -- Name of physical station / room
  status TEXT NOT NULL DEFAULT 'accepted',    -- 'accepted' or 'cancelled'
  cast_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_cancelled BOOLEAN NOT NULL DEFAULT FALSE,
  cancelled_at TIMESTAMPTZ,
  cancelled_reason TEXT,
  cancelled_by TEXT                           -- Name of Polling Officer / Admin who cancelled
);

CREATE INDEX IF NOT EXISTS idx_ballots_voter_pos 
  ON public.ballots (admission_no, position_id);
CREATE INDEX IF NOT EXISTS idx_ballots_house 
  ON public.ballots (house_code);
CREATE INDEX IF NOT EXISTS idx_ballots_status 
  ON public.ballots (status);
```

> [!IMPORTANT]
> **Schema Note regarding `booth_name`:**  
> The `booth_name` column is present on the **`ballots`** table.  
> It is **NOT** present on the `voters` table. Never include `booth_name` in payloads sent to `/rest/v1/voters`.

---

## 2. Table: `voters`

Tracks accreditation and double-voting prevention for every eligible student and teacher.

```sql
CREATE TABLE IF NOT EXISTS public.voters (
  admission_no TEXT PRIMARY KEY,              -- e.g. "10001" or "6082"
  full_name TEXT NOT NULL,
  class_name TEXT,                            -- e.g. "10", "9", or "Staff"
  section TEXT,                               -- e.g. "A", "Ashoka", or "Faculty"
  house_code TEXT NOT NULL,                   -- House slug or "ALL" for Teachers
  status TEXT NOT NULL DEFAULT 'eligible',    -- 'eligible', 'voted', 'cancelled'
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  voted_at TIMESTAMPTZ,
  photo_url TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_voters_house 
  ON public.voters (house_code);
CREATE INDEX IF NOT EXISTS idx_voters_status 
  ON public.voters (status);
```

---

## 3. Table: `candidates`

Stores the official candidate roster for all houses and the School Cabinet.

```sql
CREATE TABLE IF NOT EXISTS public.candidates (
  id TEXT PRIMARY KEY,                        -- e.g. "HAN-CB-BOYS"
  election_id TEXT NOT NULL DEFAULT 'ELECTION_2026',
  admission_no TEXT,
  full_name TEXT NOT NULL,
  class_name TEXT,
  section TEXT,
  house_code TEXT NOT NULL,
  position_id TEXT NOT NULL,
  position_name TEXT NOT NULL,
  photo_url TEXT,
  votes_count INTEGER NOT NULL DEFAULT 0,
  is_approved BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 4. Table: `audit_logs`

Maintains a non-repudiable audit trail of administrative actions (e.g. vote cancellations, manual overrides).

```sql
CREATE TABLE IF NOT EXISTS public.audit_logs (
  id BIGSERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  action TEXT NOT NULL,                       -- e.g. "CANCEL_BALLOT", "DELETE_BALLOT"
  actor TEXT NOT NULL,                        -- Officer Name or Admin Username
  details JSONB NOT NULL                      -- { admission_no, position_id, reason, officer_name }
);
```

---

## 5. Storage Bucket: `voter-photos`

- **Purpose:** Stores the biometric verification photo captured at the moment of voting.
- **Path Pattern:**  
  `{house_slug}/{admission_no}/{timestamp}.jpg`  
  *Example:* `hanuman/6082/1700000000.jpg`
- **MIME Type:** `image/jpeg`
- **Upload Method:** Base64 Data URL converted to a binary `Blob` uploaded with header `x-upsert: true`.
- **Retrieval:** Kiosks and the admin dashboard request a 1-hour signed URL via:
  ```text
  POST /storage/v1/object/sign/voter-photos/{path}
  Body: { "expiresIn": 3600 }
  ```
  URLs are cached in the browser for fast thumbnail rendering.

---

## 6. How Supabase Credentials are Configured

To protect against committing API keys into source control, the frontend reads credentials dynamically:

1. **Browser `localStorage` (Primary Method):**  
   The key `election_spr_2026_sb_cfg_v1` stores:
   ```json
   {
     "url": "https://<your-project-id>.supabase.co",
     "anonKey": "<your-publishable-anon-key>"
   }
   ```
   *Any admin can paste their Supabase URL and Publishable anon key into the Admin Dashboard login card, which persists across all tabs on that browser origin.*
2. **Local Fallback (`supabase.local.json`):**  
   If no localStorage key exists, booths attempt to read `../supabase.local.json`.

---

## 7. Local Pendrive & Directory Backup Architecture (`window.PendriveStorage`)

In addition to Supabase cloud storage, every kiosk and admin station supports direct local pendrive syncing via the native File System Access API (`showDirectoryPicker`):

1. **House-Wise Directory Encapsulation:**
   - Handled via `getHouseDirectory(rootHandle, meta)`.
   - Regardless of whether the root of a USB flash drive or a parent directory is selected, all data is strictly encapsulated inside that specific house's subfolder:
     ```text
     [USB Drive or Selected Folder]/
     └── bheeshma/
         ├── 0000_Demo_User/
         │   ├── photo.jpg
         │   └── result.md
         ├── 6082_RAVI_CHANDRA/
         │   ├── photo.jpg
         │   └── result.md
         ├── result.md
         └── BHEESHMA_SUMMARY.md
     ```
   - Prevents student voter folders and summaries from spilling into the root directory.
2. **Confidential Candidate Results & Winner Tallies:**
   - The house backup summary (`result.md` and `<HOUSE>_SUMMARY.md`) strictly contains candidate tally statistics:
     `Role | Candidate | Admission No | Class | Votes Received | Result (🏆 WINNER / Runner-up)`.
   - Student voter choices are completely excluded from house summaries to preserve the institutional Secret Ballot principle.
3. **Delayed Loading Protection:**
   - The UI displays `"Saving Ballot..."` if pendrive disk writes or network calls take longer than 350ms, ensuring complete transparency during slow operations.
