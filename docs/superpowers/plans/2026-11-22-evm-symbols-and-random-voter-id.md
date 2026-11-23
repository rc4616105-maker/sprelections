# Implementation Plan: EVM Symbol Images & 6-Character Random Voter ID Scheme

- **Date:** 2026-11-22
- **Goal:** Replace emoji symbol badges with real graphic symbol images, reorder the candidate ballot row to `[ Candidate Photo ] -> [ Symbol Image ] -> [ Candidate Name & Info ] -> [ LED / Vote Button ]`, and transition the voter ID format to an authentic 6-character randomized code (`1CXXXX`) starting with the demo voter (`1C8492`, Class 10-CS).

---

## Proposed Changes

### 1. Symbol Graphic Assets (`Houses/assets/symbols/`)
- Create 10 clean, high-resolution ballot symbol images (PNG & SVG):
  - `torch.png` / `torch.svg`
  - `shield.png` / `shield.svg`
  - `rising_sun.png` / `rising_sun.svg`
  - `book.png` / `book.svg`
  - `star.png` / `star.svg`
  - `trophy.png` / `trophy.svg`
  - `tree.png` / `tree.svg`
  - `bell.png` / `bell.svg`
  - `rocket.png` / `rocket.svg`
  - `compass.png` / `compass.svg`
- Mirror to `Result declaration/assets/symbols/`.

### 2. Candidate Data Mapping (`scripts/parse_roster.py` & `data.js`)
- Attach `symbolImage: "../assets/symbols/<slug>.png"` to all candidate objects in `CANDIDATE_PROFILES`.
- Regenerate `data.js` across all 6 houses (`bheeshma`, `gurudrona`, `hanuman`, `karna`, `vasistha`, `vishwamithra`), `central`, `admin`, and `teachers`.

### 3. Candidate Row Layout Reordering
- In `Houses/*/app.js`:
  - Render Candidate Photo avatar first (`.evm-cand-avatar`).
  - Render Symbol Image avatar second (`.evm-cand-symbol` with `<img>` and title).
  - Render Candidate Name and class third (`.evm-cand-info`).
  - Render LED lamp and VOTE button fourth (`.evm-right-cluster`).
  - Update Step 4 review cards to also display candidate photo and symbol image side by side.
- In `Houses/*/styles.css`:
  - Style `.evm-cand-symbol` as a neat, high-contrast ballot badge with clean borders and crisp image sizing (64x64px / 72x72px).

### 4. 6-Character Randomized Voter ID Scheme (`1CXXXX`)
- Demo Voter profile:
  - Name: `Aditya Vikram (Demo Voter)`
  - Class: `10`
  - Section: `Chatrapathi Shivaji` (Abbreviated as `CS` or `1C`)
  - Voter ID: `1C8492` (6 characters: `1` for Class 10, `C` for CS, `8492` random digits).
  - Backward compatibility: Keep `0000` and `000000` active so all booths recognize both.
- Update `scripts/generate_voter_card_images.py` to generate:
  - `1C8492_Demo_User.png`
  - `0000_Demo_User.png`
  - Code-128 barcode encoding `1C8492`.

---

## Verification Plan
1. Open `http://127.0.0.1:5500/Houses/bheeshma/index.html` in browser.
2. Authenticate using `1C8492` (and verify `0000` also works).
3. Confirm Candidate Row displays:
   - Left: Candidate Portrait Photo
   - Second: Real Symbol Graphic Image
   - Third: Candidate Name & Class Subtitle
   - Right: LED Lamp & Blue Vote Button
4. Cast a ballot and verify Step 4 Review reflects candidate photo and symbol graphic.
5. Verify all tests and documentation sync in `docs/CURRENT_PROGRESS_AND_CHANGELOG.md`.
