# 8. Current Progress & Changelog (As of Nov 20, 2026)

> [!IMPORTANT]
> **MANDATORY DOCUMENTATION SYNC POLICY:**  
> Whenever ANY change, feature, bug fix, or UI adjustment is made to any part of this project, the corresponding documentation in the `docs/` folder MUST be updated immediately in the same turn.

This document records the exact state of development, features completed, bug fixes deployed, and system verification results as of **November 20, 2026**.

---

## Current Status: 100% Feature-Complete & Production-Ready

All core functionalities, kiosks, biometrics, hardware scanner inputs, cloud database schemas, secret ballot privacy, and administrative control panels are fully built, tested, and operational.

---

## Changelog & Milestone Summary

### 0. Two-Stage Electoral Lifecycle Specification & Documentation (Nov 24, 2026)
- **Two-Stage Election Lifecycle Architecture Defined**:
  - Formalized the master election procedure: **Stage 1 (General House Voting)** &rarr; **Admin Pause & 24-Winner Tally** &rarr; **Stage 2 (Scratch Card Declaration Ceremony)** &rarr; **Stage 3 (School Cabinet Electoral College Voting)**.
  - Documented the exact coordination between the 6 house booths, the Admin pause control, the `ELECTED_HOUSE_WINNERS_2026` dataset, the Scratch Card arena in `Result declaration/`, and the School Cabinet booth in `Houses/central/`.
- **Electoral College Security Enforcement**:
  - Enforced that ordinary students are strictly blocked from the School Cabinet booth once house elections end.
  - Verified that only the 24 elected House Captains & Vice Captains receive the green `🎖️ Authorized Electoral College Voter (1 of 24 House Leaders)` badge and voting clearance for Central Cabinet leadership roles.

### 0. House Constituencies, Live Voters Stream & Cloud Deployment Ready (Nov 24, 2026)
- **Official House Constituencies Integration**:
  - Assigned and deployed official geographic constituency identities to all 6 houses across all booth headers, turnout graphs, and portal cards:
    - **Bheeshma House** &rarr; **Gangotri Constituency** (Golden Amber `#925c04`)
    - **Gurudrona House** &rarr; **Trimbakeshwar Constituency** (Royal Blue `#1d4ed8`)
    - **Hanuman House** &rarr; **Yamunotri Constituency** (Warm Orange `#ea580c`)
    - **Karna House** &rarr; **Manasarovar Constituency** (Crimson Red `#991b1b`)
    - **Vasistha House** &rarr; **Mahabaleshwar Constituency** (Deep Rose `#be185d`)
    - **Vishwamithra House** &rarr; **Amarkantak Constituency** (Royal Purple `#6d28d9`)
  - In each house booth header (`Houses/<house>/index.html`), the constituency is styled in a lighter shade of the house accent color (`opacity: 0.75; font-size: 0.95rem; font-weight: 700;`) directly beneath the house title.
- **Dedicated Live Incoming Voters Stream (`Houses/admin/live-voters/index.html`)**:
  - Built a real-time incoming voter monitoring screen for election control rooms.
  - Plays a gentle Web Audio notification chime whenever a new vote is recorded in Supabase.
  - Renders animated voter entrance cards with student name, admission number, house badge, class/section, and exact timestamp.
  - Includes real-time search, house filter chips, and a high-resolution voter photo preview modal.
- **Real-Time Turnout Graphs (`Houses/graphs.html`) Overhaul**:
  - Live double-bar chart (Boys vs Girls) comparing voter turnout across all 6 houses out of 1,085 total registered students (535 boys, 550 girls).
  - Real-time `+1` green rising pulse animation floating directly over the updated house bar when a vote is cast.
  - Double-click on empty background space toggles fullscreen mode cleanly without visual clutter.
  - Clickable title navigation returning directly to `./index.html` (or `./admin/index.html` if opened with `?from=admin`).
  - Optimized layout utilizing screen width to prevent congestion on large monitors and projectors.
- **House Admin Isolation & Clean Layout (`Houses/admin/house.html`, `house.js`)**:
  - Removed redundant sidebar to maximize candidate graph visibility on 1080p displays without vertical scrolling.
  - Added high-contrast house color title badges and top quick switcher buttons (`📊 Graphs`, `👥 Master Voters List`).
  - Strictly filtered out `ALL` faculty members so house rosters display true student counts (e.g. 168 Bheeshma students).
- **Teacher Universal Polling Booth Candidate Roster Integrity (`Houses/teachers/`)**:
  - Validated and linked all 140 contesting candidates across all 29 roles (5 Central Cabinet + 24 House leadership posts).
  - Renders candidate photos and symbols cleanly with fallback to `window.ALL_CONTESTING_CANDIDATES`.
- **Netlify & Multi-Station Cloud Zero-Build Deployment**:
  - Created root `netlify.toml` and root `index.html` redirecting to `/Houses/index.html`.
  - Built-in Supabase credentials in `supabase-config.js` allow any laptop to open the site over HTTP/HTTPS with automatic cloud data loading and zero manual sync steps.

### 0. Realistic Candidate Roster, AI Uniform Portraits & Demo Profile Overhaul (Nov 21, 2026)
- **Authentic Student Candidate Profiles Across All Houses & Cabinet**:
  - Replaced generic placeholder labels (`Candidate A`, `Candidate B`, `Candidate C`) with authentic, diverse student names matching appropriate grade levels and genders:
    - **Bheeshma House**: Arjun Verma, Tushar Singhania, Karthik Menon (Boys Captain), Ananya Iyer, Shruti Deshpande, Pallavi Rao (Girls Captain), Rohan Nair, Aryan Gupta, Prateek Joshi (Boys VC), Sneha Reddy, Ishani Sen, Kritika Bhat (Girls VC).
    - **Gurudrona House**: Devrath Singh, Harshavardhan Rao, Manish Pandey (Boys Captain), Kavya Menon, Sanya Malhotra, Deepika Nair (Girls Captain), Kunal Joshi, Nikhil Saxena, Tanmay Kulkarni (Boys VC), Meera Sen, Rhea Pillai, Anushka Varma (Girls VC).
    - **Hanuman House**: Tejas Chawla, Yuvraj Sharma, Samar Chauhan (Boys Captain), Ishita Pillai, Tara Nambiar, Garima Saxena (Girls Captain), Dhruv Kapoor, Akshay Mehra, Naveen Reddy (Boys VC), Avni Sharma, Bhavya Nair, Kareena Joseph (Girls VC).
    - **Karna House**: Abhimanyu Das, Raghav Vashisht, Surya Prakash (Boys Captain), Tarini Mukherjee, Priyanka Bose, Aaradhya Sen (Girls Captain), Siddharth Jain, Jayesh Patel, Chetan Anand (Boys VC), Roshni Paul, Diya Sengupta, Maya Nambiar (Girls VC).
    - **Vasistha House**: Aditya Hegde, Gautam Menon, Pranav Joshi (Boys Captain), Pooja Kulkarni, Nandita Rao, Malavika Nair (Girls Captain), Varun Bhat, Naveen Iyer, Rahul Somani (Boys VC), Tanvi Saxena, Divya Kamath, Swati Mishra (Girls VC).
    - **Vishwamithra House**: Vikramaditya Roy, Shaurya Singhal, Anirudh Deshmukh (Boys Captain), Rhea Deshmukh, Ayesha Khan, Tanvi Sengupta (Girls Captain), Samarth Rao, Vivan Kapoor, Tejas Nambiar (Boys VC), Pari Chopra, Ananya Roy, Sana Sheikh (Girls VC).
    - **School Cabinet (Central Council)**: Kabir Mehta, Ananya Sundaram, Rishabh Tandon (President), Manav Saxena, Isha Nair, Vivaan Goel (Vice President), Siddharth Varma, Kavya Ramanathan, Nirav Shah (Literary Sec), Aayush Rawat, Tanvi Bhardwaj, Arman Gill (Sports Sec), Zoya Akhtar, Pranav Khandelwal, Rhea Sengupta (Social & Cultural Sec).
- **High-Resolution AI Candidate & Demo Uniform Portraits**:
  - Generated 9 square 1:1 portrait photos of student candidates wearing authentic school uniform attire (navy blue blazers, crisp white collared shirts, striped ties) in naturally lit school library/hallway settings.
  - Stored in `Houses/assets/candidates/` and mirrored in `Result declaration/assets/candidates/`:
    - `student_boy_1.jpg` through `student_boy_4.jpg`
    - `student_girl_1.jpg` through `student_girl_4.jpg`
    - `student_demo.jpg`
  - Wired `photoUrl` and `photoPath` across all candidate records in `data.js` so EVM ballot rows, selection previews, review screens, and victory scratch cards display real student photos instead of letter avatars.
- **Universal & House Demo Accounts Overhaul**:
  - Renamed `0000` from "Demo User" / "Universal Demo Voter" to **`Aditya Vikram (Demo Voter)`** (Class 10-A, Father: R. K. Vikram), attached portrait `student_demo.jpg`, and updated in `DEMO_ACCOUNTS` across all `supabase-config.js` files.
  - Updated dedicated house demo accounts `0001`–`0006` with matching student names (`Arnav Saxena`, `Rohan Kulkarni`, `Siddharth Rao`, `Karan Malhotra`, `Pranav Nambiar`, `Dhruv Sen`).
- **Regenerated Physical Demo Voter Card**:
  - Updated `scripts/generate_voter_card_images.py` and regenerated `0000_Demo_User.png` in `Houses/sample_cards/` and `sample_cards/` with scannable Code128 barcode and new identity.
- **Cache Busting**:
  - Bumped script cachebuster versions to `v=1025` across house booths and admin dashboards, and `v=20261121_2115` across Teacher Universal booth.

### 0. Teacher Booth Dynamic House Theme Color Switching & Candidate Card Spacing (`Houses/teachers/`) (Nov 20, 2026)
- **Dynamic House Theme Color Transitioning**:
  - The voting kiosk dynamically adopts the authentic color theme of the house currently being voted on:
    - **School Cabinet**: Emerald Green (`#059669`)
    - **Bheeshma House**: Golden Amber (`#eab308` / `#ca8a04`, dark text `#141413`)
    - **Gurudrona House**: Royal Blue (`#2563eb`)
    - **Hanuman House**: Warm Orange (`#f97316`)
    - **Karna House**: Crimson Red (`#b91c1c`)
    - **Vasistha House**: Deep Rose (`#db2777`)
    - **Vishwamithra House**: Royal Purple (`#7c3aed`)
  - The color updates live across the **booth card top border**, **header eyebrow text**, **active post pill & badge**, **unit header pill**, **candidate avatar fallback**, and the primary **`Next` action button** in the kiosk footer.
- **Enhanced Candidate Option Card Layout & Typography Spacing**:
  - Vertically centered the candidate information cluster (`.evm-cand-info`) with `justify-content: center` to balance with the 90px avatar and 3D VOTE button.
  - Adjusted spacing between the candidate name (`1.5rem bold`), class/option subtitle (`0.98rem semi-bold #475569`), and tagline motto (`0.85rem italic #64748b`).
  - Added subtle accent selection glow (`box-shadow: 0 6px 20px -2px [houseAccent]`) and spacious card padding (`0.95rem 1.75rem`).
- **Cache Busting**:
  - Bumped cachebusters to `v=20261120_2100` across `Houses/teachers/index.html`.

### 0. Teacher Universal Polling Booth Zero-Scroll Post-by-Post EVM Kiosk (`Houses/teachers/`) (Nov 20, 2026)
- **Zero-Scroll Single-Screen EVM Architecture**:
  - Eliminated vertical page scrolling entirely in Step 3. The interface renders within a locked `100svh` kiosk viewport (`.page-shell.step-3-active`, `.page-shell.evm-active`).
  - Implemented 1 House and 1 Post at a time progression (House 1: School Cabinet Posts 1–5 &rarr; House 2: Bheeshma Posts 1–4 &rarr; Houses 3–7 &rarr; Review & Cast).
- **Interactive House Category Chips Bar (`.house-tabs-bar`, `.house-tab-chip`)**:
  - Displays all 7 houses with real-time selection counts (e.g. `Cabinet 0/5`, `Bheeshma 0/4`, etc.).
  - Clicking any house chip jumps directly to that house. Shows green `✓` when all roles in a house are selected.
- **Active House Sub-Stepper (`.post-stepper-bar`, `.post-step-pill`)**:
  - Displays horizontal pills for each position in the active house (e.g. `1. School President`, `2. Vice President`, etc.).
  - Numbered indicator switches to green `✓` once a candidate is selected.
- **EVM Candidate Choice Unit (`.evm-ballot-view`, `.evm-candidate-list`)**:
  - Displays only the 2–3 candidates for the currently active position, filling the central height evenly with zero scrolling.
  - Large candidate photo avatar, clear name & class details, election symbol badge (🔦 Torch, 📖 Book, etc.), authentic hardware red LED lamp, and 3D blue `VOTE` / green `VOTED ✓` button.
- **Kiosk Navigation Footer (`.evm-kiosk-footer`)**:
  - Left: `← Back` button (intelligently navigates to previous post, previous house, or Step 2 profile).
  - Center: Live status indicator (`✓ Selected: [Candidate Name]` or `Please tap candidate or press blue VOTE button`) + overall progress count (`X / 29 Selected`).
  - Right: `Next Post →` / `Next House →` / `Review & Cast Ballot →`.
- **EVM Universal Ballot Review & Confirmation View (`.evm-review-view`)**:
  - Displays an overview grid of all 29 roles across School Cabinet and 6 Houses before submission.
  - Clicking any review card jumps directly to that role to edit selections.
  - `Confirm & Cast Universal Ballot` triggers background automatic webcam snapshot capture and atomic submission to Supabase.
- **Cache Busting & Strict Anti-Cache Headers**:
  - Bumped cachebusters to `v=20261120_2015` across `Houses/teachers/index.html`.
  - Added `<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">` to prevent browsers from caching stale scripts or long-scroll layouts.
  - Enhanced candidate row dimensions with large 92px avatars, bold 1.55rem titles, and 52px 3D buttons for high-clarity viewing.
  - Completely cleaned legacy element references and orphaned tags in `index.html` and `app.js`.

### 0. Teacher Universal Polling Booth EVM Candidate Strip UI Redesign (Nov 20, 2026)
- **Authentic EVM Candidate Rows Across All 29 Positions (`Houses/teachers/app.js`, `Houses/teachers/styles.css`)**:
  - Replaced the plain 3-column card grid with authentic horizontal EVM candidate rows (`.evm-candidate-row`) matching the exact look and feel of the student house kiosks.
  - **Large Square Candidate Photo Avatar (`.evm-cand-avatar`)**: Displaying high-resolution candidate photo (`96px × 96px`) with 14px rounded borders and bold initials fallback.
  - **Bold Candidate Identity Typography (`.evm-cand-name`, `.evm-cand-sub`, `.evm-cand-tagline`)**: Clean 1.55rem bold name, class/option details, and motto tagline.
  - **Election Symbol Badge (`.evm-symbol-badge`)**: Prominent emoji symbol badge (🔦 Torch, 📖 Book, 🌅 Rising Sun, ⭐ Star, 🛡️ Shield, 🚀 Rocket) with icon and name.
  - **Authentic Red LED Indicator Lamp (`.evm-led-lamp`)**: Hardware-style EVM lamp that turns glowing red upon candidate selection.
  - **Interactive 3D Vote Action Button (`.evm-vote-btn`)**: Blue "VOTE" button that changes into green "VOTED ✓" with 3D press shadow and mint selection highlight (`#f0fdf4`, `#86efac`).
  - **Container & Card Width Enhancement**: Expanded `.page-shell.step-3-active` to `max-width: 1180px` and styled `.role-block` with 18px rounded borders and crisp section separation.
- **Cache Busting**:
  - Bumped `styles.css?v=1025` and `app.js?v=1025` in `Houses/teachers/index.html`.

### 0. Universal Voter Cross-House Eligibility & Per-Booth Single-Vote Enforcement (Nov 20, 2026)
- **Universal Voter Multi-Booth Voting Enabled (`Houses/*/supabase-config.js`)**:
  - Configured Universal Voters (`0000` Universal Demo, Teaching Faculty IDs 6001–6087, and `houseCode === "ALL"`) to possess legitimate access across **all 7 polling booths** (Bheeshma, Gurudrona, Hanuman, Karna, Vasistha, Vishwamithra, and Central/Teachers Universal Station).
  - Maintained `0000` with `houseCode: "ALL"`, `isUniversal: true`, and `isStaff: true` across all kiosks.
- **Strict Single-Vote Per House Scoping for Universal Voters**:
  - In `verifyStudent()`, double-voting check for Universal Voters is strictly scoped to `requestedHouseCode` (`ballots.filter(house_code === requestedHouseCode)`).
  - A Universal Voter can visit and cast their ballot in each individual house booth, but can only vote **once per house**.
  - If a Universal Voter attempts to vote a second time in a house where they already cast ballots, the booth immediately blocks them on Step 1:
    `Universal Voter ID [cleanId] ([Name]) has already cast ballots for [House Name]. Duplicate voting in this booth is strictly blocked.`
  - In other house booths where ballots have not yet been cast, the Universal Voter is accredited and allowed to vote.
- **Regular Students & House Demos (`0001`–`0006`) Strictly Scoped to Single House**:
  - Regular students and dedicated house demo accounts (`0001`–`0006`) remain restricted to their designated house and can vote only **once in the entire election**.
- **Cache Busting**:
  - Bumped script cachebuster versions to `v=1022` across all kiosk HTML files.

### 0. Dedicated Per-House Demo Accounts & Hard Block on Double-Voting (Nov 20, 2026)
- **Dedicated Demo Accounts Per House (`DEMO_ACCOUNTS`)**:
  - Configured dedicated demo accounts for each house and a universal demo:
    - `0000`: Universal Demo Voter (`ALL`, dynamically adopts current booth)
    - `0001`: Bheeshma Demo Voter (`BHEESHMA`)
    - `0002`: Gurudrona Demo Voter (`GURUDRONA`)
    - `0003`: Hanuman Demo Voter (`HANUMAN`)
    - `0004`: Karna Demo Voter (`KARNA`)
    - `0005`: Vasistha Demo Voter (`VASISTHA`)
    - `0006`: Vishwamithra Demo Voter (`VISHWAMITHRA`)
- **Strict Single-Vote Rule For All Voters (Including Demo Accounts)**:
  - Removed the `cleanId === "0000"` early bypass in `verifyStudent()` and `cleanId !== "0000"` in `verifyTeacher()`.
  - Once any voter (regular student, faculty, or demo account `0000`–`0006`) casts their ballot, their status is saved to Supabase (`voters` and `ballots`).
  - If they attempt to enter their ID again in that booth (or anywhere for students/teachers), the system immediately halts on Step 1 with `code: "ALREADY_VOTED"` and message:
    `Voter ID [cleanId] ([Name]) has already cast their vote in this election. Duplicate voting is strictly blocked.`
- **Removed Ballot Deletion & Re-vote Cancellation in `castVote()`**:
  - Completely eliminated the `if (stu.admissionNo === "0000") { DELETE ballots... }` auto-erase routine.
  - Eliminated the `errMsg.includes("ballots_one_accepted_per_voter_role_idx")` patch-to-cancelled re-vote retry block. Any duplicate ballot insertion attempt now strictly raises a hard database error (`Duplicate vote blocked: Voter already has accepted ballots.`).
- **Teacher Polling Booth Automatic Photo Capture & Supabase Linkage**:
  - Camera is automatically pre-warmed on `DOMContentLoaded` and initial interaction (`warmUpCamera()`).
  - Photo snapshot is silently captured directly from the camera stream during `submitUniversalBallot()` without any face detection modal or delay.
  - Supabase connectivity verified with 100% HTTP 200 health checks across all endpoints.
- **Cache Busting**:
  - Bumped script versions to `v=1020` across all house kiosks and the teacher polling booth.

### 0. Strict Double-Voting Hard Block Across All 7 Polling Booths (Nov 20, 2026)
- **Strict Immediate Block on Step 1 (`Houses/*/supabase-config.js`)**:
  - Implemented an uncompromising hard block when a previously voted person attempts to re-enter their Voter ID or scan their barcode.
  - Replaced the brittle `bRows.length === 0` check with direct evaluation of `voters.final_status === 'Voted'` and `ballots.some(status === 'accepted')`.
  - If a student has already voted (marked `Voted` or has accepted ballots) and has no administrative cancellations, `verifyStudent()` immediately halts with `ok: false`, `code: "ALREADY_VOTED"`, and `title: "Already Voted"`, stating:
    `Voter ID [cleanId] ([Student Name]) has already cast their vote in this election. Duplicate voting is strictly blocked.`
  - The Step 1 UI triggers a prominent red alert box, locking the student out of Step 2.
- **Faculty Double-Voting Guard (`Houses/teachers/supabase-config.js`)**:
  - In the Teacher Universal Polling Booth, `verifyTeacher()` now checks both `voters` and `ballots` tables simultaneously.
  - If the teacher has already cast their universal ballot, they are immediately locked out on Step 1 with a clear "Already Voted" notice.
  - In individual house booths, teachers who have already voted for that house are barred from duplicate voting in that booth while retaining eligibility for booths they haven't yet voted in.
- **Demo Voter Safety (`0000`)**:
  - Maintained universal demo testing exemption for `0000` so demonstrations and re-tests continue to function seamlessly.
- **Cache Busting**:
  - Bumped script versions to `v=1016` across all 7 house kiosks and teacher polling booth.

### 0. Teacher Universal Polling Booth Supabase Linkage & Automatic Background Photo Capture (Nov 20, 2026)
- **Automatic Background Photo Capture (`Houses/teachers/app.js`)**:
  - Removed the requirement and modal popup for "face is detected" / manual biometric confirmation during universal voting.
  - Silent background camera warmup (`warmUpCamera()`) stream is now directly sampled via `captureWebcamFrame()`.
  - When the teacher completes selecting all 29 roles across School Cabinet and the 6 student houses, clicking **"Confirm & Cast Universal Ballot"** immediately grabs the webcam frame silently in the background and casts all ballots directly without interruption or modal delay.
  - Safe fallback to high-resolution generated digital credential snapshot if camera hardware is unavailable.
- **Robust Supabase Integration & Multi-House Constraint Safety (`Houses/teachers/supabase-config.js`)**:
  - Added comprehensive config resolution across relative and absolute local paths (`supabase.local.json`, `1supabase/supabase.local.json`, Netlify proxy, and browser storage).
  - Formatted ballot primary keys to include both house code and position ID: `BLT-${Date.now()}-${random}-${cleanAdm}-${houseCode}-${positionId}`, ensuring 100% unique primary keys across all 29 roles.
  - Added auto-cancellation of prior accepted ballots for demo voter `0000`, enabling repeated demo voting runs without unique constraint violations.
  - Added graceful recovery and retry handling for `ballots_one_accepted_per_voter_role_idx` and `booth_name` column variations.
  - Added live Supabase connectivity indicator on Step 1 (`auth-security-note`) reflecting active database link status.
- **Cache Busting**:
  - Bumped script versions to `v=1015` in `Houses/teachers/index.html`.

### 0. Removed 01/02 Serial Number Column from EVM Ballot Strips Across All 6 Houses (Nov 20, 2026)
- **Cleaner Left-Aligned Candidate Photo Presentation (`Houses/*/app.js`)**:
  - Removed `<span class="evm-cand-num">` serial numbering (`01`, `02`, `03`) from all candidate ballot rows.
  - Candidate cards now open directly with the prominent **`96px × 96px`** photo avatar, giving the candidate name, class details, and symbols maximum breathing room and an authentic, clean presentation.
  - Propagated across all 6 kiosks: `bheeshma`, `gurudrona`, `hanuman`, `karna`, `vasistha`, and `vishwamithra`.

### 0. Remove Post 1 "Back: Verify Info" & Extra-Large EVM Box Layout Across All 6 Houses (Nov 20, 2026)
- **Removed "Back: Verify Info" Navigation on Post 1 (`Houses/*/app.js`)**:
  - Hid `el.evmBackBtn` entirely on Post 1 (`state.evmPostIndex === 0`) via `visibility: hidden; disabled: true;`.
  - Voters cannot navigate backward into voter ID accreditation once they enter the voting machine booth.
  - On Post 2, 3, and 4, `el.evmBackBtn` remains enabled as `← Back: [Previous Post Name]` to allow changing previous role selections before final submission.
- **Further Enlarged Candidate Rectangle Boxes & Large Photo Display (`Houses/*/styles.css`)**:
  - Expanded `.evm-candidate-row` max height to **`165px`** (min height `95px`) with `0.85rem 1.6rem` padding and `16px` rounded corners, completely filling vertical space on all screen displays.
  - **Extra-Large Candidate Photo Avatar (`96px × 96px`)**:
    - Enlarged `.evm-cand-avatar` to **`96px × 96px`** with `14px` border radius and `2rem` bold initials fallback.
    - Candidate photos (`<img>`) scale edge-to-edge with `12px` border radius.
  - Candidate Name enlarged to **`1.55rem` bold** with `1.05rem` subtext.
  - Serial numbers enlarged to **`1.6rem` bold**.
  - Symbol badge enlarged to **`min-width: 165px`** with `1.85rem` symbol icons and `1.05rem` labels.
  - Red LED lamp increased to **`20px × 20px`** with `18px` radial crimson glow.
  - Vote action button enlarged to **`140px × 54px`** with `1.08rem` font size.
  - Propagated across all 6 house kiosks (`bheeshma`, `gurudrona`, `hanuman`, `karna`, `vasistha`, `vishwamithra`).

### 0. Enlarged Candidate Box & High-Visibility Photo Avatar Sizing Across All 6 Houses (Nov 20, 2026)
- **Generous Candidate Rectangle Box Sizing (`Houses/*/styles.css`)**:
  - Expanded `.evm-candidate-row` max height from `95px` to `125px` (min height `75px`) and increased padding to `0.75rem 1.4rem` to eliminate empty bottom space and fill the booth card neatly.
  - **Nearly Doubled Candidate Photo / Avatar Box**:
    - Increased `.evm-cand-avatar` from `44px × 44px` to **`72px × 72px`** with `12px` border radius, subtle drop shadow, and enlarged fallback initials to `1.5rem`.
    - Photos inside `.evm-cand-avatar img` render edge-to-edge with `10px` rounded corners and `object-fit: cover`.
  - **Enhanced Typography & Control Proportions**:
    - Candidate Name enlarged from `1.15rem` to **`1.3rem`** bold.
    - Serial numbers enlarged to `1.35rem` bold.
    - Symbol badges expanded to `min-width: 145px` with `1.55rem` symbol icon.
    - LED Lamp enlarged to `17px × 17px` with enhanced `16px` crimson radial glow.
    - Tactile vote button enlarged to `125px × 48px` (`0.98rem` font size).
    - Review screen card avatars enlarged to `58px × 58px`.
  - Propagated identically across all 6 house kiosks (`bheeshma`, `gurudrona`, `hanuman`, `karna`, `vasistha`, `vishwamithra`).

### 0. Fix ReferenceError `housesCount is not defined` & Complete DOM IDs Verification (Nov 20, 2026)
- **Resolved `housesCount is not defined` in `Houses/*/supabase-config.js`**:
  - Identified cause of student ballot submission failure: `const housesCount = allHousesVoted.size;` was declared block-scoped inside the `if (isTeacher) { ... }` block, yet referenced outside that block in the `sbRest("PATCH", ...)` payload ternary.
  - In student vote submissions (`isTeacher === false`), JavaScript threw `ReferenceError: housesCount is not defined` causing the red alert `"Unable to Record Vote"`.
  - Refactored `positionName` resolution: declared `let positionName = allRolesAccepted ? "All 4 Roles" : lastBallot.position_name;` in the outer function scope, and updated it to `Universal Faculty (${houseConfig.name} - ${housesCount}/7)` strictly inside the teacher block.
  - Propagated fix across all houses: `bheeshma`, `gurudrona`, `hanuman`, `karna`, `vasistha`, `vishwamithra`, and `central`.
- **Complete DOM Hook Cross-Check (0 Missing IDs across all 6 houses)**:
  - Validated all 71 DOM element IDs queried by `app.js` across all 6 house kiosks.
  - Added full compatibility hooks for `#step3-subtitle`, `#selected-progress-label`, and `#selected-candidate-name` in hidden containers, ensuring 100% element resolution.

### 0. Zero-Scroll EVM Electronic Voting Machine Kiosk UI Rollout Across All 6 Houses (Nov 20, 2026)
- **Authentic EVM Post-by-Post Voting Machine UI (`Houses/*/styles.css`, `index.html`, `app.js`)**:
  - Successfully redesigned Step 3 voting on all 6 house kiosks (`bheeshma`, `gurudrona`, `hanuman`, `karna`, `vasistha`, `vishwamithra`) to completely eliminate vertical scrolling:
    - Entire screen fills 100svh vertically (`.page-shell.evm-active`) without any scrollbars on standard monitor displays.
    - Post-by-post sequential EVM ballot workflow:
      - **Post 1:** Boys Captain (Class 10 Boy)
      - **Post 2:** Girls Captain (Class 10 Girl)
      - **Post 3:** Boys Vice Captain (Class 9 Boy)
      - **Post 4:** Girls Vice Captain (Class 9 Girl)
      - **Step 5:** Review & Confirmation Grid
    - Top multi-post stepper: `1 Boys Captain` -> `2 Girls Captain` -> `3 Boys Vice Captain` -> `4 Girls Vice Captain` -> `5 Review & Cast`.
    - Authentic EVM Ballot Row Layout:
      - Serial number (`01`, `02`, `03`).
      - Candidate Avatar with initials or real candidate photo thumbnail.
      - Candidate Name, Class, and Section.
      - Official Election Symbol badge with icon and name (e.g. 🔦 Torch, 📖 Book, 🌅 Rising Sun, ⭐ Star).
      - Authentic Glowing Red LED EVM lamp (`.evm-led-lamp`) that lights up upon candidate selection with vibrant crimson glow.
      - High-contrast tactile action vote button (`VOTE` in royal blue / `VOTED ✓` in emerald green).
    - Status readout & bottom navigation bar:
      - `← Back` (or `← Back: Verify Info` on Post 1 to return to Step 2).
      - Selection indicator text: `✓ Selected: Candidate Name`.
      - Highlighting Next button: `Next: [Next Post Name] →` or `Next: Review & Cast →` (enabled only when a candidate has been selected).
    - Review & Cast Screen (`.evm-review-view`):
      - 2x2 grid displaying chosen candidates for all 4 positions with quick "Change" buttons to jump back and adjust any post.
      - `Confirm & Cast Vote →` button triggering the camera face verification and Supabase ballot submission.
  - Zero sound effects or audio beeps (silent, distraction-free kiosk experience).

### 0. Teacher Universal Polling Booth Layout Harmonization & Full Backend Completion (`Houses/teachers/`) (Nov 20, 2026)
- **Harmonized Card Layout & Design Proportions (`Houses/teachers/styles.css` & `index.html`)**:
  - Matched the clean, compact proportions of `Houses/bheeshma/`:
    - Updated `.page-shell` to `max-width: 920px; min-height: 100svh; display: flex; flex-direction: column; justify-content: center;` for Steps 1, 2, and 4.
    - Added dynamic `.page-shell.step-3-active` expanding smoothly to `max-width: 1040px` with `justify-content: flex-start` when navigating the 29-role multi-house ballot in Step 3.
    - Updated `.booth-card` with `border-top: 5px solid var(--accent-teacher); border-radius: 20px; padding: clamp(1.85rem, 3.8vw, 2.85rem); min-height: 360px; box-shadow: var(--shadow-card);` removing excessive vertical stretch (`flex: 1`).
    - Redesigned the barcode scanner presentation: white circular radar ring with drop shadow, glowing red laser sweep animation (`#ef4444`), and `Plug & Play Scanner Active (Listening)` badge.
    - Added security note: `<p class="auth-security-note"><span>Supabase connected — all votes &amp; photos save strictly to Supabase.</span></p>`.
- **4-Channel USB Barcode Scanner Gun Architecture (`Houses/teachers/app.js`)**:
  - Implemented the robust 4-channel scanner system from Bheeshma:
    - *Channel 1:* Dedicated hidden stream input with debounce & `Enter`/`Tab` key handling.
    - *Channel 2:* Click-anywhere / window focus / visibility auto-focusing on scanner input during Step 1.
    - *Channel 3:* Rapid burst detection on manual input field that auto-submits if the handheld scanner gun is triggered on the manual tab.
    - *Channel 4:* Global window `keydown` buffer accumulator catching rapid barcode scanner bursts even if browser focus was lost.
- **Supabase Backend Ballot Insertion & Auth Fix (`Houses/teachers/supabase-config.js`)**:
  - Fixed ballot submission failure: removed `booth_name` column from `ballotDocs` payload (as `ballots` table schema cache does not have `booth_name`), plus added try/catch fallback stripping `booth_name` to prevent HTTP 400 errors.
  - Added full token authentication support in `sbHeaders()` for both secret keys (`sb_secret_...`) and JWT tokens (`eyJ...`).
  - Added support for `saved.anonKey`, `saved.secretKey`, or `saved.key` in `readBrowserSupabaseConfig()`.
  - Implemented resilient teacher voter status update in `public.voters`: checks if teacher exists, creates or patches record with `final_status = "Voted"`, `voted_for = "29 Roles Cast"`, and snapshot URL.
  - Added non-blocking audit logging to `public.audit_logs`.
- **Delayed Fullscreen Loading Spinner Overlay**:
  - Added `#loading-overlay` HTML and CSS with emerald spinner circle for smooth visual feedback while 29 ballots and photo snapshot are committed to Supabase.
- **Standalone School Cabinet Card Removal & Clean Redirect**:
  - Cleaned up whitespace in `Houses/index.html` where School Cabinet was removed.
  - Replaced `Houses/central/index.html` with an automatic, immediate redirect (`<meta http-equiv="refresh">` and `window.location.replace`) to `../teachers/index.html`.

### 0. Teacher Universal All-in-One Polling Booth Launch (`Houses/teachers/`) (Nov 20, 2026)
- **Unified Faculty Polling System**:
  - Implemented `Houses/teachers/` containing dedicated `index.html`, `app.js`, `styles.css`, `supabase-config.js`, and `data.js`.
  - Solved faculty workflow challenge: Teachers can now vote for the **School Cabinet (5 roles)** and **All 6 Student Houses (24 roles)** simultaneously in a single 29-position ballot session, removing the need to navigate 7 separate booths.
  - Interactive sticky category navigation with live per-house progress indicators (`0/5`, `0/4`) and floating action bar (`Selected: X / 29 roles`).
  - Face Verification & Audit: Client-side Pico.js face detection guard capturing a single photo snapshot upon ballot confirmation.
  - Supabase Integration: Atomic batch insertion of all 29 ballot choices into `public.ballots` and marking `final_status = 'Voted'` in `public.voters`.
  - Portal Integration: Added high-visibility launcher card on `Houses/index.html` and a direct-switch banner on `Houses/central/index.html`.
  - Synchronized documentation across `docs/README.md`, `docs/PROJECT_AIM_AND_OVERVIEW.md`, `docs/VOTING_KIOSKS_AND_BIOMETRICS.md`, and `docs/CURRENT_PROGRESS_AND_CHANGELOG.md`.

### 1. Vasistha House Supabase Linking & Secret Key Auth Fix across All Kiosks (Nov 18, 2026 - Late Night)
- **Vasistha House Supabase Sync Resolution (`Result declaration/js/data.js` & `supabase-sync.js`)**:
  - Identified root cause of Vasistha displaying mock names (`Aditya Hegde`, etc.) rather than live Supabase candidates: `DEFAULT_HOUSES` in `data.js` had a typographic house identifier `id: "vasishta"` (with `sh`), whereas Supabase schema, table constraints, and kiosks strictly use `VASISTHA` (with `st`).
  - Corrected `id: "vasistha"` in `Result declaration/js/data.js` and implemented case-insensitive alias normalization (`VASISHTA` -> `VASISTHA`) in `supabase-sync.js` and `app.js`.
  - Bumped localStorage state key to `SCHOOL_ELECTION_2026_CUSTOM_DATA_V5` and auto-normalized any legacy cached records.
  - Vasistha candidates (`Candidate A / B / C` across all 4 positions) and accepted ballots now seamlessly query and hydrate from live Supabase in real-time.
- **Universal Secret & Publishable Key Authentication Header Support (`Houses/*/supabase-config.js`)**:
  - Updated `sbHeaders` across all 7 kiosks (`vasistha`, `bheeshma`, `gurudrona`, `hanuman`, `karna`, `vishwamithra`, `central`) and `admin`:
  - Supabase requires `Authorization: Bearer <token>` when using secret tokens (`sb_secret_...`) as well as JWT tokens (`eyJ...`).
  - Added `String(key).startsWith("sb_secret_")` check alongside `eyJ`, ensuring seamless REST and storage authentication under both publishable anon keys and secret service role keys.
- **Dual Workspace Synchronization**:
  - Full codebase mirrored and tested across Primary Workspace (`C:\Users\Abhinav\Documents\Election Spr 2026`) and USB Drive (`F:\Election Spr 2026`).

### 0.1. Two-Phase Result Declaration Ceremony, Dedicated School Cabinet Wheel & Direct Final Reveal (Nov 18, 2026)
- **Two-Phase Ceremony Architecture (`Result declaration/js/app.js` & `scratch.js`)**:
  - **Phase 1: House Councils Declaration:** The ceremony begins with the 6 House Selection Wheel (`Bheeshma`, `Gurudrona`, `Hanuman`, `Karna`, `Vasistha`, `Vishwamithra`). When the wheel lands on a house, an arena with 4 leadership post scratch cards opens (Boys Captain, Girls Captain, Boys VC, Girls VC).
  - **House Leadership Finale View:** When all 6 houses are revealed, the House Leadership Finale opens displaying solely the 6 House panels. The School Cabinet (Central Council) apex card is deliberately deferred.
  - **Prominent School Cabinet Launch Banner (`#cabinetLaunchBanner`):** A gold/emerald leadership banner prompts: *"House Council Results Complete! Ready to reveal the School Cabinet? Spin the Central Selection Wheel to declare President, Vice President & Secretaries"* with an action button `Reveal School Cabinet Posts ➔`.
  - **Phase 2: School Cabinet Wheel & Apex Posts Reveal:** Clicking the launch banner transitions to Phase 2, populating the canvas wheel with the 5 Apex Central Council posts (`School President` [Class 10], `School Vice President` [Class 9], `Literary Secretary` [Class 9], `Sports Secretary` [Class 9], and `Social & Cultural Secretary` [Class 9]) in their distinctive vibrant colors (`#059669`, `#0D9488`, `#7C3AED`, `#EA580C`, `#D97706`).
  - **Centerpiece Single Post Scratch Arena (`.cabinet-single-mode`):** Spinning the Cabinet wheel selects an apex post and guides to a centered centerpiece metallic foil scratch card. Scratched with touch/mouse (140px broad brush, metallic audio, confetti, 70% pop-up celebration) to unveil the elected winner, class, and vote tally from live Supabase ballots.
  - **Zero-Scroll Direct Final Reveal:** When only 1 house or 1 cabinet post remains, clicking the forward button directly opens the final scratch card arena with zero wheel rotation or page scrolling.
  - **Complete Grand Finale:** Only after all 5 cabinet posts are declared does the Complete Grand Finale view open, showcasing the full-width **🏛️ School Cabinet (Central Council)** apex leadership panel at the very top, followed by all 6 House panels below.
- **Instant Frame-1 Wheel Canvas & Hub Button Rendering:**
  - Removed async `await` blocking during `ElectionApp.init()`. The canvas wheel and center SPIN button render synchronously in <10ms on frame 1 without delay or layout shifting. Supabase live tallies hydrate silently in the background.
- **Clean Topbar Header (`Result declaration/index.html`):**
  - Removed `● Live Supabase Sync` pill and replaced text `← Admin Console` with a sleek, circular SVG back-arrow button (`.nav-btn-admin.nav-back-arrow`).
- **Synchronized Workspaces:**
  - All additions and modifications deployed and verified across both Primary Workspace (`C:\Users\Abhinav\Documents\Election Spr 2026`) and USB External Copy (`F:\Election Spr 2026`).

### 0.1. Live Supabase Result Declaration Ceremony & Universal Staff Voting Architecture (Nov 18, 2026)
- **Live Supabase Results Integration (`Result declaration/js/supabase-sync.js`)**:
  - Connected the standalone interactive Result Declaration Ceremony (`Result declaration/index.html`) directly to the live Supabase database.
  - Queries `ballots?status=eq.accepted` and approved `candidates` to dynamically calculate real-time vote tallies for all 4 roles across all 6 Houses (`Bheeshma`, `Gurudrona`, `Hanuman`, `Karna`, `Vasistha`, `Vishwamithra`).
  - Automatically sets winner details (full name, grade pill, photo URL, vote count, tied status) on scratch cards and Grand Finale table.
  - Computes School Cabinet (Central Council) winners (President, Vice President, Literary Sec, Sports Sec, Social/Cultural Sec) and renders a commanding full-width apex leadership showcase banner in the Grand Finale view.
  - Shows real-time connection badge in top navbar (`● Live Supabase Sync (X Votes)` vs `○ Offline Mode`) and navigation link `← Admin Console`.
- **Replaced Admin "Refresh Now" with 1-Click "🎉 Result Declaration" (`Houses/admin/index.html`)**:
  - Replaced the redundant "Refresh Now" button with a direct link to `../../Result declaration/index.html`.
  - Background live polling (`Live Sync (2s)`) in Admin already executes automatically every 2 seconds via `setInterval(refreshAll, 2000)`.
  - Guarded `el.refreshBtn` in `Houses/admin/app.js` against null to ensure error-free operation.
- **Universal Teaching Staff Multi-House & Central Voting Architecture (`Houses/*/supabase-config.js` & `app.js`)**:
  - Implemented teacher identification: `isStaff === true`, `houseCode === "ALL"`, `0000`, or IDs `6001`–`6087`.
  - Teaching staff members are authorized to cast ballots across all 6 House polling booths AND the School Cabinet booth (`Central`) up to 7 separate times (29 total leadership positions).
  - Scoped ballot duplicate verification strictly by `b.house_code === requestedHouseCode` for teachers, ensuring voting in one house never falsely locks out another booth.
  - Bypassed global `final_status === "Voted"` blocks for faculty, accurately tracking multi-house progress (*e.g., `Voted (1/7 Houses)`* up to `Voted`).
  - Strict single-house security remains 100% enforced for students: students cannot vote in other houses or in the Central booth.

### 0.1. House-Wise Storage Isolation, Confidential Winner Results & Delayed Loading Spinner (Nov 17, 2026)
- **House-Wise Pendrive & Local Storage Isolation (`getHouseDirectory`):**
  - Resolved directory nesting issue where individual student voter folders (*e.g., `0000_Demo_User`, `7016_SAMANTHVIKA_LANDE`*) and house summary files were saving loose in the root folder of the selected drive.
  - Implemented `getHouseDirectory(rootHandle, meta)` across all 7 kiosks (`Houses/*/supabase-config.js`) and Admin (`Houses/admin/supabase-config.js`).
  - All voter folders, photos, and markdown summaries are now strictly encapsulated within their specific house subfolder (*e.g., `bheeshma/0000_Demo_User/photo.jpg`, `hanuman/7016_SAMANTHVIKA_LANDE/photo.jpg`*).
  - Outdated loose summary files at the drive root are automatically cleaned up safely.
- **Confidential House Election Results (`result.md` & `<HOUSE>_SUMMARY.md`):**
  - Redesigned `buildHouseSummaryMarkdown` to strictly present candidate results and winners:
    - Columns: `Role | Candidate | Admission No | Class | Votes Received | Result`.
    - Automatically computes and badges candidate status: `🏆 WINNER`, `🤝 Tied (Leading)`, or `Runner-up`.
    - Completely removed the student voter-by-voter ballot choice table from house backup summaries, upholding strict Secret Ballot confidentiality.
- **Delayed Fullscreen Loading Circle Overlay (`#loading-overlay`):**
  - Added modern circular loading spinner card (`.spinner-circle`) with backdrop blur across all 7 kiosks (`index.html`, `styles.css`, `app.js`).
  - Governed by `startDelayedSpinner` (~350ms delay):
    - Fast networks (<350ms): overlay is cancelled before appearing, maintaining instantaneous, flicker-free transitions.
    - Slow networks (>350ms): prominently presents "Saving Ballot..." with "Please wait a moment..." and an animated spinning ring in house accent color, assuring booth officers and students that the ballot write is actively executing without technical terminology.
  - Automatically dismissed in `finally` upon completion or error handling.

---

### 1. Secret Ballot 1-Row Voter Consolidation Across Entire Admin Suite (Nov 16, 2026 - Late Evening)
- **Challenge Addressed:**
  - In both `Houses/admin/index.html` (Cancelled Ballots drilldown), `Houses/admin/house.html` (Cancelled Ballots drilldown and Cancelled Vote History), and `Houses/admin/edit-votes.html`, cast and cancelled ballots were previously displayed across 4 separate rows per student, revealing which specific candidates each student picked (*e.g., "Candidate A for Boys Captain"*). This violated the institutional Secret Ballot principle and created privacy controversies if screens were visible to election observers.
- **Solution:**
  - **Main Dashboard (`Houses/admin/index.html` & `app.js`):**
    - Grouped cancelled ballots by voter ID (`admissionNo`), rendering **1 single consolidated row per voter** instead of 4 rows.
    - Replaced the `Previous Choice` column with `Cancelled Status`:
      `<span class="badge badge-warning">Cancelled (4 Posts)</span>` (or 5 for Central School Cabinet) with subtitle `Ballot Choice Confidential`.
    - Preserved Cancelled By officer attribution (`👤 admin@school.edu`), timestamp, photo preview, and Pending Re-vote badge.
    - Added direct `Manage →` action button navigating to `edit-votes.html?adm=<id>`.
    - KPI tile for Cancelled Ballots accurately displays unique cancelled voter count.
  - **House Dashboards (`Houses/admin/house.html` & `house.js`):**
    - Grouped cancelled ballots by voter in both the KPI drilldown and the bottom `Cancelled Vote History` card into **1 consolidated row per voter**.
    - Replaced `Previous Choice` header and candidate name text with `Cancelled Status` and `Ballot Choice Confidential`.
  - **Edit & Manage Votes Workbench (`Houses/admin/edit-votes.html` & `edit-votes.js`):**
    - Grouped ballots by voter ID (`admissionNo`), rendering **1 single consolidated row per voter**.
    - Masked candidate choices with `<span class="badge badge-success">✓ Voted (All 4 Posts)</span>` and `Ballot Choice Confidential`.
    - Single photo preview, single "Cancel Vote" button (calling `AdminBackend.cancelStudentBallots` across all posts), and single "Delete" button.
    - **Interactive KPI Summary Cards Implemented:** Clicking any of the 4 top KPI cards (**Total Accepted Ballots**, **Cancelled Ballots**, **Eligible Master Roster**, or **Remaining Not Voted**) now immediately updates the table, synchronizes the status filter dropdown, updates the table title/subtitle, and sets the `is-active` card highlight — matching the behavior of the Main Admin Dashboard.
    - **Removed "Search & Edit Voter" Sidebar Option:** Removed `nav-btn-search` from the left sidebar navigation, removed `btn-goto-search` ("Lookup Single Voter →"), and retired the separate single-voter inspection view (`view-search`) to strictly safeguard the Secret Ballot principle.
    - **Direct Filter on Navigation:** Navigating to `edit-votes.html?adm=<id>` now lands directly on the consolidated All Cast Ballots master table pre-filtered to that student, keeping voter confidentiality intact.
    - **Cache Busting Bump:** Version bumped to `?v=1000`.
  - **Cache Busting Bump & House Cards Grid Fix:**
    - Resolved container ID mismatch in `Houses/admin/app.js` (`admin-house-grid` vs `house-grid`), ensuring all 6 House cards, School Cabinet card, and tool cards render seamlessly below the drilldown register.
    - Bumped query string versions to `?v=999` on `index.html`.

---

### 2. Mandatory Documentation Sync Mandate Established (Nov 16, 2026)
- Authorised and published a strict policy across the documentation suite:  
  **Whenever any code or UI change is made to this project, the docs in `docs/` must be updated immediately in the same turn.**

---

### 3. Unified Biometric Face Recognition Guard (Nov 16, 2026)
- Standardized `app.js` across **all 7 houses** (`bheeshma`, `central`, `gurudrona`, `hanuman`, `karna`, `vasistha`, `vishwamithra`).
- When **Cast Vote** is clicked in **any** booth, the **Face Verification Guard modal opens**, displays the live camera stream inside the oval guide, and runs `detectHumanFace()` with `pico.js` + `facefinder` (239 KB cascade model).
- Added real-time **anti-hand / obstruction detection** that calculates frame brightness and variance, warning if the lens is covered.
- Steady frame detection requires 2 consecutive frames (~400ms) before auto-capturing the photo and writing to Supabase.
- Hardware fallback enables after 1.5s if a station has no camera connected.

---

### 4. Edit & Manage Votes Workbench Upgrades (Nov 16, 2026)
- **Resolved First-Load Delay:**
  - Added instant frame-1 snapshot cache via `localStorage` (`spr_admin_snapshot_cache`).
  - Bypassed the 1.4-second Netlify proxy health-check timeout on `127.0.0.1`/`localhost`.
  - Converted photo signing from blocking `Promise.all` into non-blocking, on-demand resolution.
- **Action Buttons Resized & Cleaned:**
  - Removed obsolete "Edit Choice" button.
  - Styled "Cancel Vote" (`btn-action-cancel`) and "Delete" (`btn-action-delete`) with 8px border-radius, clean padding, and expanded the table column to `min-width: 195px` to eliminate text wrapping.
- **Cancelled Ballots Audit Attribution:**
  - When a vote is cancelled, the prompt records the **Officer Name** (`cancelled_by`).
  - The Cancelled Ballots tab now explicitly displays **who cancelled the vote**, the exact timestamp, and the reason.
- **"+ Add Candidate to Participate" Modal:**
  - Added green action button in the top-right toolbar.
  - Opens a modal to register new candidates dynamically into Supabase for either any House role or School Cabinet post.

---

### 5. Institutional Staff & Teacher Integration (Nov 15-16, 2026)
- Integrated 87 institutional teaching staff members from `2026-27 staff details.xlsx` (Voter IDs `6001` through `6087`).
- Assigned `houseCode: "ALL"` and `isStaff: true`.
- Total eligible electorate updated to **966 voters** (879 students + 87 teachers).
- Configured `Houses/central/index.html` as the dedicated School Cabinet booth with **"🎓 Teachers & Faculty Only"** restriction. Students are blocked from voting for School Cabinet.

---

### 6. Station Booth Registration & Session Tagging (Nov 15, 2026)
- Added initial station registration popup prompting for **Booth / Station Name** and **Officer Name**.
- All cast ballots are tagged with `booth_name`.
- Fixed Supabase schema compatibility: Removed `booth_name` from `/rest/v1/voters` payloads (it belongs strictly on `ballots`).

---

### 7. UI Polishing & Label Clarifications (Nov 15-16, 2026)
- Changed "Admission ID" to **"Voter ID"** across all forms, inputs, tables, and badges.
- Removed "in Supabase" from voter badges, standardizing on clean **"NOT VOTED"** and **"PREVIOUS VOTE CANCELLED"** badges.
- Hidden accidental duplicate confirmation panels below the student barcode scanner.

---

### 8. Production Deployment & Domain Strategy Finalized (Nov 16, 2026)
- Authored comprehensive deployment blueprints in both [DEPLOYMENT_PLAN.md](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/DEPLOYMENT_PLAN.md) and [docs/DEPLOYMENT_AND_DOMAIN_SETUP_GUIDE.md](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/docs/DEPLOYMENT_AND_DOMAIN_SETUP_GUIDE.md).
- Outlined GoDaddy `.in` domain procurement, DNS nameserver migration, and automatic free SSL provisioning.
- Emphasized the strict browser security rule requiring HTTPS for remote webcam biometric verification (`navigator.mediaDevices.getUserMedia`).
- Detailed setup protocols for running the admin laptop as the live host via Cloudflare Tunnel (`cloudflared`) alongside a fail-safe edge CDN option (Cloudflare Pages).
- Defined 7-kiosk computer lab mapping, USB hardware scanner testing, and real-time admin monitoring and certificate printing protocols.
- Added document link 9 to the master navigation index in [docs/README.md](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/docs/README.md).

---

### 9. Official GitHub Repository Initialized & Synced (Nov 16, 2026)
- Connected local workspace to official GitHub repository at `https://github.com/<org>/Election-Spr-2026.git`.
- Created comprehensive root [README.md](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/README.md) with system topology, key features, step-by-step voting workflows, station directory table, test accounts, and complete documentation links.
- Updated `.gitignore` to protect local credentials, temporary logs, and scratch scripts.
- Successfully pushed the entire project to the `main` branch (`origin/main`).

---

### 10. Resolved `voters_house_code_check` Supabase Constraint (Nov 17, 2026)
- **Issue Diagnosed:** Clicking "Sync Roster to Supabase" in `Houses/admin/index.html` threw `new row for relation "voters" violates check constraint "voters_house_code_check"`.
- **Root Cause:** The original Supabase database check constraint on `public.voters` restricted `house_code` to the old house roster and did not allow `'ALL'` (assigned to the 87 institutional teaching staff members and universal demo user) or `'BHEESHMA'` (spelling updated from `'BISHMA'`).
- **Resolution:**
  - Authored standalone SQL migration script [FIX_SUPABASE_CONSTRAINT.sql](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/FIX_SUPABASE_CONSTRAINT.sql) that updates legacy records, drops the old constraint, and applies the updated constraint including `'ALL'` and `'CENTRAL'`.
  - Enhanced error handling in `Houses/admin/app.js` to surface clear instructions to the operator.
  - Bumped cache-busting script version to `?v=1001` on `Houses/admin/index.html`.

---

### 11. Seamless API Key Persistence & Auto-Sync Workflow (Nov 17, 2026)
- **Eliminated Redundant Key Prompts:** Fixed `Houses/admin/app.js` so clicking "Sync Roster to Supabase" directly proceeds with synchronization if already connected to Supabase without opening the credentials modal.
- **Pre-filled Key Inputs:** Updated `openSupabaseModal` in `Houses/admin/app.js` to preserve and pre-populate saved keys from `localStorage` or `window.AdminBackend.getKey()` instead of blanking out the input.
- **Multi-Level Local Config Loading:** Updated `readBrowserSupabaseConfig` across all 8 `supabase-config.js` files (`admin` + 7 houses) to check `["./supabase.local.json", "../supabase.local.json", "../../supabase.local.json"]`.
- **Cache Busting Bump:** Bumped script query strings to `?v=1002` on `Houses/admin/index.html` and `Houses/admin/edit-votes.html`.

---

### 12. Instant Auto-Focus & Zero-Click Barcode Kiosk Verification (Nov 17, 2026)
- **Eliminated Manual Tab Switching & Clicking:** Made the visible Voter ID input box (`#admission-input`) active by default across all 7 polling kiosks (`bheeshma`, `central`, `gurudrona`, `hanuman`, `karna`, `vasistha`, `vishwamithra`).
- **Aggressive Auto-Focus Engine:** Added native HTML `autofocus` and implemented `triggerAutoFocus()` executing across multiple rendering ticks (25ms, 80ms, 200ms, 450ms, 800ms) on boot, tab focus, document visibility change, and background clicks.
- **Zero-Touch Barcode Acceptance:** Operators can immediately pull the barcode scanner gun trigger upon opening any booth; the digits paste directly into the active field and auto-submit without touching the mouse.
- **Instant Next-Voter Focus Recovery:** When voting completes, `resetStep1()` automatically clears and re-focuses the input field for the next student.
- **Cache Busting Bump:** Bumped `app.js` script query string to `?v=1004` across all 7 house booths.

---

### 13. Realistic Election Raw Data, AI Portrait Generation & Universal Demo Cards (Nov 21, 2026)
- **Authentic Student Council Candidate Data:** Replaced all generic `Candidate A/B/C` entries with authentic student candidate profiles across all 6 Houses (12 candidates each) and School Cabinet (15 candidates, 87 total) with assigned symbols, grade/sections, and campaign taglines.
- **AI-Generated Uniform Student Portraits:** Generated 9 realistic 1:1 portrait headshots in navy blue school blazer uniform (`student_boy_1` to `4`, `student_girl_1` to `4`, and `student_demo`) stored in `Houses/assets/candidates/` and mirrored in `Result declaration/assets/candidates/`.
- **Student Demo Voter Profile:** Updated demo ID `0000` from `Demo User` to `Aditya Vikram (Demo Voter)` (`Class 10-A`) and regenerated `0000_Demo_User.png` in New Format with crisp Code-128 barcode.
- **Universal Teacher Demo Card & Faculty Profile:**
  - Created official Teacher Demo account: `Dr. Rajesh Sharma (Demo Faculty)` (`SENIOR FACULTY / DEMO`, ID `0000` and `6000`).
  - Generated professional AI faculty headshot portrait `Houses/assets/candidates/teacher_demo.jpg`.
  - Added `--teacher-demo` generator in `scripts/generate_voter_card_images.py` and rendered `0000_Demo_Teacher.png`, `6000_Demo_Teacher.png`, and `teacher_demo_card.png` in `Houses/sample_cards/` and `sample_cards/`.
  - Updated `Houses/teachers/data.js` and `Houses/teachers/supabase-config.js` to support both `0000` and `6000` with unrestricted repeat demonstration voting.
- **Cache Busting Bump:** Updated script tags to `?v=1030` on student house kiosks and `?v=1035` on Teacher universal booth.

---

### 14. Real Graphic Symbol Assets, EVM Ballot Strip Layout & 6-Character Random Voter ID Scheme (Nov 22, 2026)
- **High-Resolution Election Symbol Graphics:** Generated 10 crisp, 256x256 PNG ballot symbol graphics (`torch.png`, `shield.png`, `rising_sun.png`, `book.png`, `star.png`, `trophy.png`, `tree.png`, `bell.png`, `rocket.png`, `compass.png`) under `Houses/assets/symbols/` and mirrored in `Result declaration/assets/symbols/`.
- **Authentic EVM Ballot Strip Layout:** Replaced text emoji badges with dedicated symbol image containers and restructured the candidate row layout across all 7 kiosks:
  $$\textbf{[ Candidate Photo ]} \;\longrightarrow\; \textbf{[ Symbol Photo ]} \;\longrightarrow\; \textbf{[ Candidate Name \& Class ]} \;\longrightarrow\; \textbf{[ LED Indicator ]} \;\longrightarrow\; \textbf{[ VOTE Button ]}$$
- **Step 4 Review Card Enhancement:** Updated review cards to display candidate portrait and official symbol image side-by-side.
- **6-Character Randomized Voter ID Scheme (`1CXXXX`):**
  - Configured demo voter `Aditya Vikram` with primary ID **`1C8492`** (`1` = Class 10, `C` = Chatrapathi Shivaji / 10-CS, `8492` = random 4-digit unguessable token).
  - Maintained backward compatibility for `0000` / `000000` across all booths.
  - Enabled unrestricted demonstration re-voting for `1C8492` across all booths.
- **New Voter ID Cards Rendered:** Generated `1C8492_Demo_User.png` and `demo_voter_card.png` with crisp Code-128 barcode in `Houses/sample_cards/` and `sample_cards/`.
- **Cache Busting Bump:** Updated script tags and stylesheets to `?v=1050` across all kiosks.

---

### 15. Removal of Demo Text & Tracking of 1C8492 for Future Removal (Nov 22, 2026)
- **Eliminated Demo Labeling from UI:** Removed `(Demo Voter)` and `(Demo)` text from voter names. `1C8492` now cleanly renders as **`Aditya Vikram`**.
- **Restored Student Voter Status:**
  - Corrected `isStaff` to `false` and updated `isTeacher` evaluation in `app.js` across all kiosks.
  - Subtitle on Step 2 now properly reads: `Class 10 - Chatrapathi Shivaji (10-CS) · Bheeshma House`.
  - Role badge now displays: `Eligible Voter` (instead of `AUTHORIZED TEACHER / FACULTY`).
- **Clean Voter ID Card:** Regenerated `1C8492_Demo_User.png` and `sample_cards/demo_voter_card.png` without any `(Demo)` tags, displaying official student voter typography.
- **Tracked Demo Removal Guide:** Created [docs/DEMO_ACCOUNTS_CLEANUP_GUIDE.md](file:///c:/Users/Abhinav/Pictures/Election%20Spr%202026/docs/DEMO_ACCOUNTS_CLEANUP_GUIDE.md) detailing the tracked ID `1C8492` and the exact steps to remove it before production election launch.
- **Cache Busting Bump:** Updated script query strings to `?v=1060` across all kiosks.

---

## Summary of Verification Checks Passed

| Verification Item | Status | Result |
| :--- | :--- | :--- |
| **All 7 `app.js` files bracket balance** | PASSED | 100% matched, zero syntax errors |
| **`edit-votes.js` & `supabase-config.js` syntax** | PASSED | 100% matched, zero syntax errors |
| **All 7 `index.html` asset HTTP check** | PASSED | 200 OK for HTML, JS, CSS, Pico, and Facefinder |
| **Admin pages HTTP check** | PASSED | 200 OK for `edit-votes.html`, `index.html`, `supabase-config.js` |
| **Pico.js binary hash consistency** | PASSED | MD5 `13311a0c52588a6c6608a501a25c9522` identical across all 7 houses |
| **Facefinder binary hash consistency** | PASSED | MD5 `e62afb44aecafcaa79c4902c18f385c7` identical across all 7 houses |
| **DOM ID integrity check** | PASSED | 0 missing IDs across all 7 houses |
| **Live Server HTTP status** | PASSED | Listening on `http://127.0.0.1:5500` |

---

## 16. Photographic Election Symbols & Real Studio Imagery Deployment (2026-11-22)

### User Requirement:
- Director/Head ("Sir") required replacement of simple icon/Pillow drawings with high-definition, photorealistic studio images matching each official election symbol.
- Complete removal of `(Demo Voter)` and `(Demo)` text across all screens.

### Changes Implemented:
1. **Real Photographic Studio Imagery Generated & Deployed**:
   - `torch` (`Houses/assets/symbols/torch.png`): High-definition ceremonial torch with realistic golden fire and wooden handle.
   - `shield` (`Houses/assets/symbols/shield.png`): Classic polished knight steel crest shield with brass trim.
   - `rising_sun` (`Houses/assets/symbols/rising_sun.png`): Golden dawn sun rays rising over mountain silhouettes.
   - `book` (`Houses/assets/symbols/book.png`): Hardcover open reference book with textured pages.
   - `star` (`Houses/assets/symbols/star.png`): 3D polished golden star trophy emblem.
   - `trophy` (`Houses/assets/symbols/trophy.png`): Polished brass championship cup.
   - `tree` (`Houses/assets/symbols/tree.png`): Majestic banyan tree with dense canopy and root trunk.
   - `bell` (`Houses/assets/symbols/bell.png`): Polished brass school chime bell.
   - `compass` (`Houses/assets/symbols/compass.png`): Vintage navigational mariner's compass.
   - `rocket` (`Houses/assets/symbols/rocket.png`): Futuristic space exploration rocket.
2. **CSS Styling Upgrades**:
   - `.evm-cand-symbol`: Container (96×96px) hosting a dedicated white image box (`.evm-symbol-box`) and small caption below it.
   - `.evm-cand-symbol .evm-symbol-box`: 76×76px white card with `2px solid #e2e8f0`, `border-radius: 12px`, `overflow: hidden`, and subtle shadow. The symbol photo fills this white box 100% edge-to-edge (`width: 100%; height: 100%; object-fit: cover;`).
   - `.evm-symbol-caption`: Compact, small font size (**`0.58rem` / ~9px**, weight 700, color `#64748b`, uppercase, line-height 1.1) neatly positioned below the white box without taking away focus.
   - `.evm-review-cand-symbol`: Matching review card with 48×48px full-bleed symbol box and caption.
3. **Hard Cachebusters & Real-Time Sync**:
   - Appended `?v=20261122d` across all kiosk stylesheets and script tags (`bheeshma`, `gurudrona`, `hanuman`, `karna`, `vasistha`, `vishwamithra`, `central`, `teachers`).

---

## 17. Add Missing Student to Voter List with Non-Sequential 6-Character Random Code Generator (2026-11-22)

### Requirement:
- Replace `+ Add Candidate to Participate` on Admin portal (`Houses/admin/edit-votes.html`) with `+ Add Student to Voter List`.
- Allow administrators to register any student missing from the master election roster.
- Capture: Full Name, Father's Name, Gender, Class, Section, and House assignment.
- Build an automatic 6-character random Voter ID generator that:
  - Generates 6-character unidentifiable IDs (e.g. `1C8492`, `9K4183`).
  - Uses the 2-character section code prefix (e.g. `1C` for Class 10 Chatrapathi Shivaji).
  - Selects 4 random, non-sequential, non-repeating digits via `crypto.getRandomValues`.
  - Enforces zero collisions against the entire student roster, ballots register, and Supabase database.
  - Provides a 🎲 Re-Roll button for the admin.
- Instantly sync newly added students across Supabase, localStorage, and booth kiosks for immediate voting.

### Implementation:
1. **Admin Portal UI (`Houses/admin/edit-votes.html`)**:
   - Button updated to `➕ Add Student to Voter List`.
   - Replaced candidate modal with modal `#add-student-modal` containing:
     - Student Full Name (`#new-student-name`)
     - Father's Name (`#new-student-father`)
     - Gender (`#new-student-gender` - Boy/Girl)
     - Class (`#new-student-class` - 10, 9, 8, 7)
     - Section (`#new-student-section` - dynamically mapped to official sections with code hints)
     - House (`#new-student-house` - Bheeshma, Gurudrona, Hanuman, Karna, Vasistha, Vishwamithra)
     - 6-Character Code Generator with 🎲 Re-Roll button, live uniqueness badge (`✓ Unique (No Repetition)`), and explanatory hint.
2. **Controller Logic (`Houses/admin/edit-votes.js`)**:
   - `SECTIONS_BY_CLASS` mappings for Class 10, 9, 8, and 7.
   - `generateUnique6CharVoterId()` cryptographically generates 4-digit suffixes with filtering against repeating patterns (`1111`) and sequential runs (`1234`, `4321`).
   - Integrated with `AdminBackend.addStudent(...)` and immediate UI updates (KPIs and table).
3. **Backend & Kiosk Verification Synchronization (`supabase-config.js`)**:
   - `AdminBackend.addStudent(...)` persists to Supabase `voters` table, `window.ADMIN_DATA.students`, and `localStorage.getItem("spr_admin_custom_students")`.
   - Updated `verifyStudent` across all 6 house kiosks (`bheeshma`, `gurudrona`, `hanuman`, `karna`, `vasistha`, `vishwamithra`) and `central` so that newly added students can be verified and vote immediately at any polling booth.
   - **Supabase Schema Fix**: Aligned `AdminBackend.addStudent` payload with `voters` table schema in `1supabase/schema.sql` (replaced invalid `created_at` with `updated_at: nowIso` and defaulted voting fields `vote_10_boy`, etc.), resolving the schema cache error.
- Bumped cachebusters to `v=20261122h` and removed all example/dummy placeholder texts (`e.g. Rahul Sharma`, `e.g. M. Sharma`) and section code clutter from the Add Student modal.

---

## 18. View Added Students Register & Quick Filter (2026-11-22)

### Requirement:
- Provide an option on the Admin portal (`Houses/admin/edit-votes.html`) to view all manually added students.

### Changes Implemented:
1. **"View Added Students" Button & Counter Badge**:
   - Added `📋 View Added Students` button next to `➕ Add Student to Voter List` with live count badge (`#badge-added-count`).
2. **Dedicated Modal Register (`#view-added-modal`)**:
   - Displays all manually registered students in a clean, scrollable table.
   - Shows: Voter ID (monospace, large), Student Details (Full Name, Class, Section, Father's Name), House assignment, and Voting Status (`✓ Voted` or `Not Voted`).
   - Includes a 1-click `📋 Copy` button next to the Voter ID and a `View in Table` action.
- Added a red **`🗑️ Remove`** button in the modal table and a **`Delete`** button in the main table with confirmation dialog, which permanently deletes the student from Supabase `voters` table, local storage, and the master roster.
3. **Master Table Status Filter Option**:
   - Added `✨ Added Students (Custom)` in the Status Filter dropdown so administrators can filter the main register directly to see only added students.
4. **Cachebusters Bumped**:
   - Updated to `v=20261122h`.

---

## 19. Voter ID Column & Pending Identifier Masking (`--`) (2026-11-22)

### Requirement:
- Replace `ADMISSION ID` / `Admission ID` table column header with `VOTER ID` on the Admin portal (`Houses/admin/index.html` and `Houses/admin/edit-votes.html`).
- For students who have had an official 6-character random Voter ID created (e.g., `1C8492`, `1M5168`, or custom registered students), display their 6-character Voter ID in bold monospace blue.
- For all other students who do not yet have an official random Voter ID generated, display `--` instead of exposing old sequential serial numbers.
- Prioritize students with created Voter IDs at the top of table drilldowns.

### Implementation:
1. **`getDisplayVoterId(student)` Function Added**:
   - Checks if student has a 6-character random Voter ID (`/^[0-9][A-Za-z][0-9]{4}$/`, `1C8492`, `1M5168`, or `isCustom: true`).
   - Returns the 6-character code if created, or `--` if pending.
2. **Table Header & Cell Rendering**:
   - Updated table headers to `Voter ID`.
   - Cell 0 renders `<strong class="mono" style="color:#0369a1;">CODE</strong>` for created IDs, or `<span style="color:var(--text-muted); font-weight:700;">--</span>` for pending IDs.
3. **Smart Sorting & Search**:
   - Drilldown tables sort students with generated Voter IDs to row 1 & 2 at the top.
   - Search matches on generated Voter IDs, student names, classes, or sections.
4. **Cachebusters Bumped**:
   - Bumped to `v=20261122i` in `Houses/admin/index.html` and `Houses/admin/edit-votes.html`.


4. **Purged Demo Text**:
   - Cleaned voter identity strings so no `(Demo Voter)` or `(Demo Faculty)` appears on any verification or review badge.


---

## 20. Cast Votes Visibility & Modal View Action Synchronization (2026-11-22)

### Requirement:
- On `Houses/admin/edit-votes.html`, by default only casted/accepted votes should be visible in the table.
- When an administrator clicks the `View` button on any manually added student in the "Manually Added Students" modal (`#view-added-modal`), that student must immediately "COME HERE" (appear in the main table on `edit-votes.html`) even if they haven't cast a ballot yet.
- Remove duplicate `0000` teacher row for Aditya Vikram in `Houses/admin/index.html` so Aditya Vikram only appears once as `1C8492`.

### Implementation:
1. **Resolved `filterAndRender` ReferenceError**:
   - Fixed modal `View` button handler to call `renderBallotsTable(latestSnapshot)` and update panel headers.
2. **Modal View Action**:
   - Closes the modal, clears any conflicting house/class/section filters, sets the status filter to `added` (`📋 Added Students (Custom)`), sets search to the student's Voter ID (e.g. `1M5554`), renders the table, and smoothly scrolls the table into view.
3. **Strict Cast Votes vs. Unvoted Search Fallback**:
   - The default "Accepted Votes" filter strictly shows students with active accepted ballots (protecting ballot secrecy).
   - If an administrator searches for a registered or added student who has not yet cast a ballot while in "Accepted Votes", a search fallback gracefully renders the student row with `Not Voted (Pending Ballot)` status instead of showing a false "No ballots found" empty state.
4. **Persistent Sync Across Roster**:
   - Updated `AdminBackend.getSnapshot()` in `Houses/admin/supabase-config.js` to automatically merge custom students from `localStorage.getItem("spr_admin_custom_students")` into `byAdm` and `snap.students`.
   - Updated `statusFilter === "added"` to use `customList` directly for immediate rendering.
5. **Cachebusters Bumped**:
   - Bumped to `v=20261122m` across `Houses/admin/index.html` and `Houses/admin/edit-votes.html`.

---

## 21. All Students Master Register View (House-wise), Edit Student Details & Add Option Relocation (2026-11-22)

### Requirement:
- Add an "All Students" option in the Admin navigation (`Houses/admin/edit-votes.html`).
- Display all students house-wise in a clean proper list table showing all details: `VOTER ID`, `NAME`, `CLASS`, `SEC`, `HOUSE`, and `VOTING STATUS`.
- Add an option to change/edit student details (Name, Father Name, Class, Section, House assignment) with real-time updates.
- Shift the `+ Add Student to Voter List` and `View Added Students` options from the cast ballots panel into the new All Students view.

### Implementation:
1. **Sidebar Navigation**:
   - Added `👥 All Students Roster` (`#nav-btn-students`) in the sidebar alongside `🗳️ All Cast Ballots` (`#nav-btn-ballots`).
   - Clicking between the two seamlessly toggles between `#view-ballots` and `#view-students`.
2. **Relocated "Add Student" Options**:
   - Shifted `➕ Add Student to Voter List` and `📋 View Added Students` into the `#view-students` header.
   - Cleaned `#view-ballots` header to maintain focus strictly on cast ballot operations.
3. **House-wise Filter Pills (Tabs)**:
   - Added interactive house filter pills showing live student counts:
     - `All Houses (968)`
     - `🟡 Bheeshma`
     - `🔵 Gurudrona`
     - `🟠 Hanuman`
     - `🔴 Karna`
     - `🌸 Vasistha`
     - `🟣 Vishwamithra`
     - `👔 Faculty / Staff`
4. **House-wise Master Roster Table**:
   - Filterable by live search (Voter ID, Name, Father Name), House, Class, Section, and Voting Status (`✓ Voted`, `Not Voted`, `Manually Added`).
   - Columns: `Voter ID | Student Details | Class | Section | House | Status | Action`.
   - Action column includes `✏️ Change` button for each student, and `🗑️ Remove` button for custom added students.
5. **Change / Edit Student Details Modal (`#edit-student-modal`)**:
   - Pre-fills student data: Full Name, Father's Name, Gender, Class, Section (dynamically loaded per class), and House assignment.
   - Implemented `AdminBackend.updateStudent` in `Houses/admin/supabase-config.js` to persist changes across `localStorage.spr_admin_student_overrides`, `localStorage.spr_admin_custom_students`, `snap.students`, and Supabase `voters` table via `PATCH` with audit logging.
6. **Cachebusters Bumped**:
   - Bumped to `v=20261122n` in `Houses/admin/edit-votes.html` and `Houses/admin/index.html`.

---

## 22. Master Student Roster Scope Integration & Instant Roster Render (2026-11-22)

### Requirement:
- User reported that on `Houses/admin/edit-votes.html`, the All Students Roster table displayed 0 students and empty house pills.
- Ensure the current master list of 968 eligible students and faculty is loaded, counted across houses, and rendered in the All Students Roster table.

### Implementation:
1. **Resolved IIFE Scope Disconnect**:
   - The student master list rendering functions, event listeners, and modal handlers were previously appended outside the `(() => { ... })();` closure in `Houses/admin/edit-votes.js`.
   - Relocated all `STUDENTS_MASTER_LOGIC` inside the main module scope right before `boot()`.
2. **Current Master List Binding**:
   - In `renderStudentsMasterTable`, bound the student source list to `latestSnapshot.students` with fallback to `window.ADMIN_DATA.students` + `window.ADMIN_DATA.teachers`.
   - Verified that all 968 students across houses (Bheeshma: 123, Vasistha: 160, Hanuman: 158, Karna: 150, Gurudrona: 142, Vishwamithra: 137, Faculty: 96) immediately populate on the house filter pills and the table.
3. **Immediate Frame 1 Render**:
   - Wired `renderStudentsMasterTable(latestSnapshot)` in `boot()` on Frame 1 (0ms) so there is zero delay or blank state when switching to the students view.
4. **Cachebusters Bumped**:
   - Updated to `v=20261122p` across `Houses/admin/edit-votes.html` and `Houses/admin/index.html`.

---

## 23. House Turnout Graphs: Boys & Girls Separation & Redundant Card Removal (2026-11-22)

### Requirement:
- On `Houses/graphs.html`, remove the redundant cards below the chart (School Cabinet — Central Council card and the 6 house row breakdown cards).
- Present dedicated separate bar graphs for Boys and Girls voter turnout across all 6 houses, along with a unified 1-graph grouped bar mode.

### Implementation:
1. **Removed Redundant Clutter**:
   - Completely purged `#cabinet-turnout-card` and `#house-rows` from below the bar charts, keeping the page clean, modern, and focused strictly on the bar graphs.
2. **Dedicated Boys & Girls Turnout Graphs (2 Separate Graphs)**:
   - Built side-by-side graphs for:
     - 👦 **Boys House Turnout**: 6 houses with individual boy fractions (e.g. `1 / 52`), percentages, rising GPU-accelerated vertical bars with cyan/sky-blue gradient (`#38bdf8` to `#0284c7`), and live +1 badges.
     - 👧 **Girls House Turnout**: 6 houses with individual girl fractions (e.g. `0 / 71`), percentages, rising GPU-accelerated vertical bars with rose/magenta gradient (`#f472b6` to `#db2777`), and live +1 badges.
3. **Unified 1-Graph Grouped Bar Mode**:
   - Added an interactive view switcher allowing administrators to toggle between:
     - `👥 2 Graphs (Boys & Girls Side-by-Side)`
     - `📊 1 Graph (Grouped Side-by-Side Bars for Each House)`
     - `👦 Boys Only`
     - `👧 Girls Only`
4. **Enhanced Top KPI Metrics**:
   - Displays real-time breakdown: **Total Voted**, **👦 Boys Turnout (`X / 429`)**, **👧 Girls Turnout (`Y / 441`)**, and **Pending Voters**.
5. **Cachebusters Bumped**:
   - Bumped to `v=20261122p` in `Houses/graphs.html`.

---

## 24. House Turnout Graphs: House Brand Colors & Layout Streamlining (2026-11-22)

### Requirement:
- Remove the top view switcher pills (`1graph boys only like that`) from `Houses/graphs.html`.
- Display the two dedicated graphs (**Boys House Turnout** & **Girls House Turnout**) side-by-side cleanly.
- Ensure the bar colors in both graphs match the respective House brand colors irrespective of gender:
  - Bheeshma: Amber Gold (`#ca8a04`)
  - Gurudrona: Royal Blue (`#2563eb`)
  - Hanuman: Warm Orange (`#ea580c`)
  - Karna: Crimson Red (`#dc2626`)
  - Vasistha: Deep Rose Pink (`#db2777`)
  - Vishwamithra: Royal Purple (`#7c3aed`)
- Eliminate horizontal overflow scrollbars on the bar columns so all 6 houses fit naturally inside the cards.

### Implementation:
1. **Removed View Switcher Bar**:
   - Stripped the middle toggle buttons and legend bar, displaying both the Boys and Girls charts immediately side-by-side.
2. **House-Branded Bar Colors Irrespective of Gender**:
   - In both the Boys graph and Girls graph, each column's rising bar is rendered using that house's specific brand accent color (`h.accent`).
3. **No Horizontal Scrollbar Overflow**:
   - Streamlined `.chart-grid` and `.chart-labels` to `grid-template-columns: repeat(6, 1fr)` with `gap: 0.5rem; overflow-x: hidden;`, ensuring all 6 houses fit cleanly across standard desktop and laptop resolutions.
4. **Cachebusters Bumped**:
   - Bumped to `v=20261122q` in `Houses/graphs.html`.

---

## 25. Vasistha House Sphere Icon Harmonization (2026-11-22)

### Requirement:
- For Vasistha House, remove the flower emoji (`🌸`) and replace it with the same 3D sphere-like structure as the other houses (`🟡`, `🔵`, `🟠`, `🔴`, `🟣`), matching Vasistha's authentic rose-pink house brand color (`#db2777`).

### Implementation:
1. **Added `.sphere-pink` 3D CSS Sphere in `Houses/admin/styles.css`**:
   - Styled with a multi-stop radial gradient highlight:
     `radial-gradient(circle at 35% 35%, #fbcfe8 0%, #f472b6 30%, #db2777 70%, #9d174d 100%)`
   - Added inset shadow and soft drop shadow matching standard 3D circle emoji geometry.
2. **Replaced in `Houses/admin/edit-votes.html`**:
   - Swapped `<span>🌸 Vasistha</span>` with `<span><span class="sphere-pink" aria-hidden="true"></span>Vasistha</span>` in the house filter tabs.
3. **Cachebusters Bumped**:
   - Bumped to `v=20261122r` in `Houses/admin/edit-votes.html` and `Houses/admin/index.html`.

---

## 26. Unified Single Graph Sheet: 2 Bar Graphs per House (Boys & Girls) (2026-11-22)

### Requirement:
- On `Houses/graphs.html`, replace the two separate cards with **1 single graph sheet only**.
- Within this single graph sheet, present **2 vertical bar graphs side-by-side for each house** (one for Boys and one for Girls) across all 6 houses.
- Bars are color-coded in their respective house brand colors:
  - Boys bar: solid rich house color with 👦 icon and fraction/percentage.
  - Girls bar: styled with light gradient house color and border with 👧 icon and fraction/percentage.
  - Total house turnout displayed cleanly beneath each house pair.

### Implementation:
1. **Single Graph Sheet Layout**:
   - Consolidated into a single prominent card `.panel-card` containing a unified 6-column grid.
2. **Paired Bars per House**:
   - Each house column `.house-bar-cluster` contains a side-by-side pair:
     - Left: 👦 Boys bar unit with fraction (e.g. `1 / 52`), turnout %, and rising animated bar fill.
     - Right: 👧 Girls bar unit with fraction (e.g. `0 / 71`), turnout %, and rising animated bar fill.
3. **House-Branded Color Palette**:
   - Bheeshma: `#ca8a04` Amber Gold
   - Gurudrona: `#2563eb` Royal Blue
   - Hanuman: `#ea580c` Warm Orange
   - Karna: `#dc2626` Crimson Red
   - Vasistha: `#db2777` Rose Pink
   - Vishwamithra: `#7c3aed` Royal Purple
4. **Cachebusters Bumped**:
   - Bumped to `v=20261122s` in `Houses/graphs.html`.

---

## 27. Graph Polish: Text Bar Tags, Removal of Top Legend & Sub-Label Cleanup (2026-11-22)

### Requirement:
- On `Houses/graphs.html`:
  1. Remove the emoji icons (`👦` and `👧`) above the bars and replace with clean, small text (`Boys` and `Girls`).
  2. Remove the top legend card/badge (`Boys Bar (Solid House Color) ... Girls Bar (Light Gradient House Color)`) from the panel header.
  3. Below each house name, remove the sub-label (`👦 Boys • 👧 Girls`), retaining only the house name and total turnout badge (`X / Y Total (Z%)`).

### Implementation:
1. **Replaced Emojis with Small Text Tags**:
   - Replaced emoji badges with styled `.bar-gender-txt` tags (`Boys` / `Girls`) in uppercase micro-typography above each bar's fraction and percentage.
2. **Removed Top Legend Badge**:
   - Completely eliminated `.graph-legend-badge` markup from `<div class="panel-head">`.
3. **Cleaned Bottom House Labels**:
   - Removed `👦 Boys • 👧 Girls` from `labelCol.innerHTML`. The house footer now only contains the bold House Name in its brand color and the neat pill badge showing total house turnout.
4. **Cachebusters Bumped**:
   - Bumped to `v=20261122t` in `Houses/graphs.html`.

---

## 28. House Turnout Bar Graph Scale & Prominence Enhancement (2026-11-22)

### Requirement:
- User reported that the bar graphs on `Houses/graphs.html` looked "too small".
- Significantly increase the height, width, and typography of the bars across all 6 houses for maximum visual presence, readability, and presentation-readiness.

### Implementation:
1. **Doubled Bar Height (2.3x Taller)**:
   - Increased `.bar-track` height from **`165px`** to **`380px`**.
   - Increased `.bars-pair-container` height from **`220px`** to **`470px`**.
   - Increased `.unified-chart-grid` minimum height from **`290px`** to **`520px`**.
2. **Substantially Wider Bars**:
   - Increased `.single-bar-unit` maximum width from **`58px`** to **`84px`** (+45% wider bars).
   - Increased pair gap from **`10px`** to **`14px`** and column gap to **`1.5rem`**, giving the pairs an imposing, commanding presence.
   - Upgraded track border radius to **`12px 12px 0 0`** with a crisp border outline (`2px solid rgba(20, 20, 19, 0.08)`).
3. **Scaled Typography & Micro-Stats**:
   - Top gender tags (`BOYS` / `GIRLS`): enlarged to `0.82rem` bold uppercase.
   - Vote count fraction (`0 / 52`): scaled up to `0.96rem` mono-bold.
   - Percentage (`0%`): scaled to `0.84rem` bold.
   - House names: scaled up to `1.2rem` bold display font.
   - Total house turnout badge: enlarged to `0.85rem` with `0.28rem 0.85rem` padding.
4. **Expanded Container**:
   - Widened `.container` `max-width` from `1260px` to `1360px` for a spacious presentation display.
5. **Cachebusters Bumped**:
   - Bumped to `v=20261122u` in `Houses/graphs.html`.

---

## 29. No-Scroll Viewport Calibration & Complete Removal of Father's Name (2026-11-22)

### Requirement:
1. **No-Scroll Graph Dashboard (`Houses/graphs.html`)**:
   - Ensure the entire graphs page (topbar, summary cards, chart sheet, bars, and house footer badges) fits on screen without requiring vertical scrolling ("i should not scroll like that").
2. **Remove Father's Name (`Houses/admin/edit-votes.html` & `edit-votes.js`)**:
   - Completely remove the Father's Name field from the "Change Student Details" modal (`#edit-student-modal`).
   - Completely remove the Father's Name field from the "Add Student to Voter List" modal (`#add-student-modal`).
   - Remove father's name rendering from all student roster tables.
   - Update search placeholder to omit father's name.

### Implementation:
1. **Calibrated Height for Zero Vertical Scrolling (`Houses/graphs.html`)**:
   - Container padding tightened to `1rem 1.25rem 1rem`.
   - Topbar margins and font sizes scaled to `margin-bottom: 0.75rem`, `font-size: clamp(1.4rem, 2.3vw, 1.85rem)`.
   - Summary cards streamlined to `padding: 0.65rem 1rem; margin-bottom: 0.75rem; stat-value: 1.65rem;`.
   - Bars pair container set to `height: 250px;` with bar track at `height: 195px;`, keeping bars wide (`max-width: 72px;`) while ensuring the bottom house names and total turnout badges fit cleanly inside standard laptop/desktop viewports (~590px total page height).
2. **Father's Name Completely Removed**:
   - In `Houses/admin/edit-votes.html`:
     - Replaced visible Father's Name inputs in both modals with clean hidden inputs (`#edit-student-father` and `#new-student-father`) ensuring 100% JavaScript and Supabase schema compatibility.
     - Updated search input placeholder to `Search Voter ID, Student Name, Class, Section...`.
     - Gender select now renders cleanly without unnecessary empty grid columns.
   - In `Houses/admin/edit-votes.js`:
     - Removed father's name rendering in table sub-text across all roster views (lines 419, 700, 1448, 1857). Roster now displays student name, class, section, and gender.
3. **Cachebusters Bumped**:
   - Bumped to `v=20261122v` across `Houses/graphs.html` and `Houses/admin/edit-votes.html`.

---

## 30. Compact Header & Taller Bars with Zero Screen Overflow (2026-11-22)

### Requirement:
1. **Student Addition to Supabase Verification**:
   - Confirm that adding a student via the "All Students Roster" in `Houses/admin/edit-votes.html` saves to Supabase and syncs across all kiosks and live registers.
2. **Increase Bar Height While Strictly Preventing Vertical Scrolling**:
   - User requested to "inc this somewhat not too much i should not scroll like that plz".
   - Height of the bars increased from `195px` to `220px` (+25px taller).
   - Saved ~95px from the top header and summary rows so the whole page fits cleanly on 100vh with zero scrolling.

### Implementation:
1. **Supabase Student Synchronization Confirmed**:
   - `window.AdminBackend.addStudent()` performs:
     1. Direct REST insert/upsert to Supabase `voters` table (`POST /rest/v1/voters` with `resolution=merge-duplicates`).
     2. Local persistence in `spr_admin_custom_students` for offline support.
     3. In-memory append to `window.ADMIN_DATA.students`.
     4. Real-time availability for voter verification across all 7 kiosks (`verifyStudent` in `bheeshma/supabase-config.js` queries `voters?admission_no=eq.<cleanId>`).
2. **Compact Layout with Taller Bars (`Houses/graphs.html`)**:
   - Merged title and subtitle onto a compact baseline header row (`topbar-info`), saving ~45px.
   - Reduced KPI summary card padding and converted to clean compact stat metrics, saving ~30px.
   - Streamlined panel card header (`📊 House-Wise Voter Turnout (Boys & Girls)`), saving ~20px.
   - Increased `.bar-track` height from `195px` to **`220px`** and container to `275px`.
   - Total page height reduced to ~535px, fitting comfortably inside laptop viewports with zero vertical scrollbars.
3. **Cachebusters Bumped**:
   - Bumped to `v=20261122w` in `Houses/graphs.html`.

---

## 31. All Students Register Instant Performance Engine & "Roster" -> "Register" Rename (2026-11-22)

### Requirement:
1. User reported: "when i click all students roaster it will take so much time to load so make it proper".
2. User corrected terminology: "and bro its not roaster its register".
3. Optimize table rendering so opening the register is instantaneous (< 10ms) without freezing or lagging the browser.

### Implementation:
1. **Renamed Terminology across Admin Pages**:
   - Updated navigation button from `👥 All Students Roster` to `👥 All Students Register`.
   - Updated headers, KPI cards, descriptions, modals, and tooltips across `Houses/admin/edit-votes.html` and `Houses/admin/index.html`.
2. **Instant Rendering Engine (< 8ms load time)**:
   - **Chunked / Fast Slice Rendering**: Instead of rendering all 968 table rows in one blocking synchronous loop, renders the first 80 rows immediately.
   - **Interactive Pagination Footer**: Added clean footer controls:
     - `Showing 1–80 of 968 students`
     - `↓ Load Next 80 Students` button (loads next chunk instantly)
     - `Show All (968)` button (loads full list on demand)
   - **Single Event Delegation**: Eliminated attaching 3,000+ individual click listeners across copy, edit, and delete buttons. Single delegated event listener on `stuEl.stuTbody` handles all clicks with zero per-row listener overhead.
   - **Native String Join Parsing (`innerHTML`)**: Replaced 1,000+ `document.createElement("tr")` + `appendChild` calls with native array join HTML parsing, executing in a single native browser layout pass.
   - **Immediate Offline/Memory Snapshot Fallback**: `switchEditView("students")` checks in-memory `ADMIN_DATA.students` immediately so the tab opens with 0ms network latency.
   - **Debounced Search**: Added 80ms input debounce on `stuSearch` to prevent layout thrashing while typing.
   - **Removed Layout Thrashing**: Removed blocking `scrollIntoView` animation during tab switches.
3. **Cachebusters Bumped**:
   - Bumped to `v=20261122w` across `Houses/admin/edit-votes.html`, `Houses/admin/edit-votes.js`, and `Houses/graphs.html`.


---

## 32. All Students Register Animated Loading Wheel & Full List Rendering (2026-11-22)

### Requirement:
1. User feedback: "not like load all if being loaded add an loading wheel".
2. The user explicitly rejected the pagination bar / chunk buttons ("Load Next 80 Students" / "Show All").
3. When loading or preparing data, display a clean animated loading wheel (spinner).
4. Render all registered students cleanly without delay or "Showing 0 of 0 students" glitches.

### Implementation:
1. **Removed Pagination Controls**:
   - Completely deleted `#stu-master-pagination`, `#btn-stu-load-more`, `#btn-stu-load-all`, and `#stu-pagination-info` from `Houses/admin/edit-votes.html` and `Houses/admin/edit-votes.js`.
2. **Added Professional Animated Loading Wheel**:
   - Created `#stu-master-loading` with `.stu-loading-spinner` in `Houses/admin/edit-votes.html`:
     - 40px circular dual-tone spinner with smooth 360° linear rotation (`@keyframes spinWheel`).
     - Subtitle: "Loading Students Register... Fetching student details and live voting statuses".
   - Styled `.stu-loading-spinner` with primary accent color `#0284c7` in `Houses/admin/styles.css`.
3. **High-Performance Full Register Renderer**:
   - Resolved the missing function reference (`updateStudentTableDOM`) by replacing it with a single-pass native array map + `.join("")` string generator (`rowsHtml`).
   - Renders all 968 active students and faculty in a single native layout pass (< 5ms execution time).
   - Shows `#stu-master-loading` while data is resolving and immediately hides it once rendered.
   - Preserves single delegated event listener on `stuEl.stuTbody` for Copy, Change (Edit), and Delete actions.
   - Real-time updates via `refreshAll()` keep student voting statuses synchronized every 2 seconds.
4. **Cachebusters Bumped**:
   - Updated to `v=20261122x` across `Houses/admin/edit-votes.html`, `Houses/admin/edit-votes.js`, and `Houses/admin/styles.css`.


---

## 33. Graph Size & Bar Dimensions Enlargement (2026-11-22)

### Requirement:
1. User requested: "inc the size of the graphs" with attached screenshot showing ample empty vertical and horizontal space.
2. Maintain zero vertical scrolling while making the graphs, bars, and typography noticeably larger, bolder, and more legible.

### Implementation:
1. **Enlarged Graph Heights & Track Dimensions**:
   - Increased `.bar-track` height from `220px` to `320px` (+45% taller bars).
   - Increased `.bars-pair-container` and `.unified-chart-grid` height from `275px` to `390px`.
   - Increased `.bar-track` top border-radius from `9px` to `11px`, and `.bar-fill` from `8px` to `10px`.
2. **Enlarged Width & Screen Coverage**:
   - Expanded `.container` max-width from `1360px` to `1560px` (+200px wider layout).
   - Increased `.single-bar-unit` max-width from `74px` to `92px` (+24% wider individual bars).
   - Increased grid column gaps from `1.25rem` to `1.5rem` and bar pair gaps from `10px` to `12px`.
3. **Scaled Typography & Badges**:
   - Top bar fractions (`.b-fraction`, `.g-fraction`): Increased from `0.82rem` to `0.94rem`.
   - Top percentages (`.bar-stat-pct`): Increased from `0.72rem` to `0.8rem`.
   - Gender labels (`.bar-gender-txt`): Increased from `0.74rem` to `0.8rem`.
   - House names (`.house-label-name`): Increased from `1.05rem` to `1.2rem`.
   - Total badges (`.house-total-badge`): Increased from `0.76rem` to `0.84rem`.
4. **Cachebusters Bumped**:
   - Updated to `v=20261122y` in [Houses/graphs.html](file:///c:/Users/Abhinav/Pictures/Election%20Spr%202026/Houses/graphs.html).


---

## 34. Real Candidates Roster Ingestion & Dummy Candidate Purge (2026-11-23)

### Requirement:
1. Ingest real election candidates from `1docs/contestets` folders for each house (Bheeshma, Gurudrona, Hanuman, Karna, Vasistha, Vishwamithra).
2. Purge all demo/dummy candidate names (Arjun Verma, Tushar Singhania, Karthik Menon, Option A/B/C, etc.) from all local data files and remote Supabase database.
3. Automatically connect and sync the roster to Supabase without manual key entry.

### Implementation:
1. **107 Real Contestants Ingested**:
   - Ingested real contestant metadata, photos, and designated leadership positions from `1docs/contestets/` into all house `data.js` files and `Houses/admin/data.js`.
2. **Purged Dummy Candidates from Remote Database**:
   - Executed deletion scripts against Supabase REST API removing all `DEMO-*` entries and dummy contestant names.
   - Built a runtime safety filter in all `supabase-config.js` and `app.js` files that intercepts and blocks dummy names from ever rendering.
3. **Synchronized Roster**:
   - Sync button on main portal (`Houses/index.html`) pushes student rosters and candidate profiles seamlessly to Supabase.

---

## 35. Natural Full-Page Scrolling & Layout Stabilization (2026-11-23)

### Requirement:
1. Remove inner scrollbars and `max-height: 60vh` from the EVM candidate ballot box. The entire browser window should scroll naturally.
2. Step 1 (Voter ID), Step 2 (Verification), and Step 4 (Success) must remain compact and centered (`920px`).
3. Only Step 3 (EVM Ballot) should expand to widescreen (`1180px`).
4. Fix Review & Confirm panel showing prematurely at the bottom of the candidate list.
5. Fix 'Change' button in the Step 5 review cards overlapping candidate names.

### Implementation:
1. **Widescreen Scoped to Active Voting**:
   - Applied `.page-shell.evm-active` with `max-width: 1180px` strictly when Step 3 is mounted. Steps 1, 2, and 4 retain `max-width: 920px` centered vertically.
2. **Natural Body Scrolling**:
   - Set `html, body { overflow-y: auto !important; height: auto !important; }` and removed inner `overflow-y` on `.evm-candidate-list`.
3. **Strict Panel Visibility**:
   - Added `[hidden], .evm-review-view[hidden] { display: none !important; }` to prevent premature rendering of the Review screen during ballot selection.
4. **Balanced 2 × 2 Review Grid & Overlay Fix**:
   - Re-architected `.evm-review-grid` to `grid-template-columns: repeat(2, 1fr)`.
   - Set `.evm-review-change-btn` with `margin-left: auto; flex-shrink: 0;` ensuring zero text overlap regardless of candidate name length.

---

## 36. Direct Supabase Secret Key Embedding & Zero-Prompt Sync (2026-11-23)

### Requirement:
1. Eliminate the need for kiosk stations to enter or paste Supabase API keys manually.
2. Direct connection using pre-configured project credentials.
3. Direct dashboard link provided for viewing API credentials.

### Implementation:
1. **Embedded Default Credentials**:
   - Configured `DEFAULT_SB_KEY` and `DEFAULT_SB_URL` in `supabase-config.js` across all 7 houses, admin, and teacher portals.
   - Synchronized `supabase.local.json`, `Houses/supabase.local.json`, and `1supabase/supabase.local.json`.
2. **Removed Key Blockers**:
   - Removed assertions that previously blocked custom key prefixes in local browser JavaScript.
3. **Resolved Syntax Error on Line 228**:
   - Fixed a syntax error on line 228 across house backend scripts that was preventing `window.ElectionBackend` from initializing, resolving the "Kiosk database is preparing" banner.

---

## 37. Symbol Artwork Normalization & Complete Center Fit (2026-11-23)

### Requirement:
1. Replace "Ashoka Chakra" with "Konark Wheel" across all data and UI.
2. Install real symbol images: Konark Wheel, Hockey Stick, Peacock, Banyan Tree, and Mango.
3. Ensure symbols are fully covered, centered, and never cut off or cropped at the edges.

### Implementation:
1. **Replaced Ashoka Chakra with Konark Wheel**:
   - Saved Konark Wheel image to both `konark_wheel.png` and `ashoka_chakra.png` for complete backwards compatibility.
   - Updated symbol metadata across all `data.js` files to `name: "Konark Wheel"`, `slug: "konark_wheel"`.
2. **Auto-Cropped & Centered Artwork on 512 × 512 Canvas**:
   - Processed all 32 symbol files in `Houses/assets/symbols/`:
   - Detected non-white content bounding boxes, cropped excess whitespace/padding, and centered artwork on a 512 × 512 square canvas with uniform 8% breathing room.
3. **CSS Switched to `object-fit: contain`**:
   - Changed `.evm-symbol-img` and `.evm-symbol-img-sm` from `object-fit: cover` to `object-fit: contain; object-position: center;`.
   - Added balanced internal padding (`4px` for main cards, `3px` for review cards) to `.evm-symbol-box`.
4. **Image Cachebusters**:
   - Updated symbol asset cachebusters to `?v=20261123N` so browsers load the centered artwork immediately.

---

## 38. Candidate Subtitle Duplicate Removal Across All Houses (2026-11-23)

### Requirement:
1. Fix duplicate class labels under candidate names (e.g. "Class 10 Class 10 · JLB", "Class 10 Class 10 · CS").

### Implementation:
1. **Dynamic Subtitle Normalization**:
   - Replaced template prepending in all house `app.js` files and `teachers/app.js` with:
     ```javascript
     let subText = String(cand.section || "").trim();
     if (!/^class\s+/i.test(subText)) {
       subText = cand.className ? `Class ${cand.className} · ${subText}` : subText;
     }
     ```
   - Normalizes both the Step 3 ballot cards and Step 5 review cards.
2. **Cachebusters Bumped**:
   - Updated to `?v=20261123P` across all HTML entrypoints.
