# School House Elections 2026 — Master Documentation

Welcome to the official technical documentation for the **School House Elections 2026** platform. This repository contains the complete, production-ready, client-side electronic voting kiosk and election administration system built for school elections.

> **Current System Status:**  
> **100% Operational & Production-Ready** (Verified November 16, 2026)  
> All 7 polling kiosks, face biometric verification, barcode scanning, Supabase live sync, admin analytics, and ballot management are fully functional and tested.

> [!IMPORTANT]
> **MANDATORY DOCUMENTATION SYNC POLICY:**  
> **Whenever ANY change, new feature, bug fix, schema modification, or UI adjustment is made to any part of this project, the corresponding documentation in the `docs/` folder MUST be updated immediately in the same turn.**  
> Future developers, maintainers, and AI assistants must keep code and documentation in 100% sync at all times. Never make code changes without recording them in `docs/`.

---

## Quick Navigation

| Document | Purpose & Contents |
| :--- | :--- |
| **[1. Project Aim & Overview](./PROJECT_AIM_AND_OVERVIEW.md)** | Purpose, electoral rules, houses, roles, voter electorate (879 students + 87 teachers = 966 voters), and security philosophy. |
| **[2. Architecture & Tech Stack](./ARCHITECTURE_AND_TECH_STACK.md)** | Pure static zero-build architecture, client-side AI biometrics (Pico.js), WebHID barcode guns, Supabase cloud sync, and offline resilience. |
| **[3. Directory & File Guide](./DIRECTORY_AND_FILE_GUIDE.md)** | Comprehensive breakdown of every directory, file, and asset in this repository with exact responsibilities. |
| **[4. Database & Storage Schema](./DATABASE_SCHEMA_AND_STORAGE.md)** | Supabase PostgreSQL tables (`ballots`, `voters`, `candidates`, `audit_logs`), Storage bucket (`voter-photos`), RLS, and column definitions. |
| **[5. Voting Kiosks & Biometrics Flow](./VOTING_KIOSKS_AND_BIOMETRICS.md)** | Step-by-step voting lifecycle: Barcode scan, identity verification, candidate selection, Face Verification Guard, and photo capture. |
| **[6. Admin Portal & Operations](./ADMIN_PORTAL_AND_OPERATIONS.md)** | Live dashboard KPIs, graphs, vote cancellation with officer attribution, photo inspection, and adding participating candidates. |
| **[7. Developer Rules: What to Edit & What NOT to Edit](./DEVELOPER_RULES_WHAT_TO_EDIT_AND_WHAT_NOT.md)** | **CRITICAL READ FOR ANY NEW DEVELOPER / AGENT:** Golden rules, invariants never to break, documentation sync mandate, and troubleshooting. |
| **[8. Current Progress & Changelog](./CURRENT_PROGRESS_AND_CHANGELOG.md)** | Exact progress log, milestones, Secret Ballot 1-row voter consolidation, and verification results as of Nov 16, 2026. |
| **[9. Production Deployment & Domain Setup Guide](./DEPLOYMENT_AND_DOMAIN_SETUP_GUIDE.md)** | GoDaddy .in domain purchase, mandatory HTTPS/camera requirements, Cloudflare Pages vs. Laptop Tunnel, and Master Laptop Command protocols. |

---

## Quick Start (How to Run Locally)

The entire voting platform is built as a **pure static web application with zero npm/build dependencies**. It runs instantly in any modern web browser.

1. **Start Local HTTP Server:**
   Open this repository in VS Code / Antigravity and start **Live Server** on port `5500`:
   ```text
   http://127.0.0.1:5500
   ```
2. **Access Polling Booths:**
   - **Central Portal (Booth Selector):** [`http://127.0.0.1:5500/Houses/index.html`](http://127.0.0.1:5500/Houses/index.html)
   - **Hanuman House Booth:** [`http://127.0.0.1:5500/Houses/hanuman/index.html`](http://127.0.0.1:5500/Houses/hanuman/index.html)
   - **Bheeshma House Booth:** [`http://127.0.0.1:5500/Houses/bheeshma/index.html`](http://127.0.0.1:5500/Houses/bheeshma/index.html)
   - **Gurudrona House Booth:** [`http://127.0.0.1:5500/Houses/gurudrona/index.html`](http://127.0.0.1:5500/Houses/gurudrona/index.html)
   - **Karna House Booth:** [`http://127.0.0.1:5500/Houses/karna/index.html`](http://127.0.0.1:5500/Houses/karna/index.html)
   - **Vasistha House Booth:** [`http://127.0.0.1:5500/Houses/vasistha/index.html`](http://127.0.0.1:5500/Houses/vasistha/index.html)
   - **Vishwamithra House Booth:** [`http://127.0.0.1:5500/Houses/vishwamithra/index.html`](http://127.0.0.1:5500/Houses/vishwamithra/index.html)
   - **School Cabinet (Teacher-Only Booth):** [`http://127.0.0.1:5500/Houses/central/index.html`](http://127.0.0.1:5500/Houses/central/index.html)
3. **Access Administration Portals:**
   - **Admin Live Dashboard:** [`http://127.0.0.1:5500/Houses/admin/index.html`](http://127.0.0.1:5500/Houses/admin/index.html)
   - **Edit & Manage Votes (Secret Ballot 1-Row Register):** [`http://127.0.0.1:5500/Houses/admin/edit-votes.html`](http://127.0.0.1:5500/Houses/admin/edit-votes.html)
   - **Candidate Vote Graphs:** [`http://127.0.0.1:5500/Houses/graphs.html`](http://127.0.0.1:5500/Houses/graphs.html)

---

## Test Accounts & Demo Credentials

| Role | Voter ID | Name | House / Access |
| :--- | :--- | :--- | :--- |
| **Demo Voter** | `0000` | Demo User | Universal testing account, eligible in all booths |
| **Teacher / Faculty** | `6001` - `6087` (e.g. `6082`) | Ravi Chandra, etc. | Eligible in all 6 house booths + Central School Cabinet |
| **Bheeshma Student** | `10001`, `10004`, etc. | Aaradhya Kammari, etc. | Eligible in Bheeshma House only |
| **Gurudrona Student**| `10003`, `10006`, etc. | Akshara Bandari, etc. | Eligible in Gurudrona House only |
| **Hanuman Student**  | `10005`, `10017`, etc. | Anvitha, etc. | Eligible in Hanuman House only |
| **Karna Student**    | `10011`, `10014`, etc. | Bhavya Sri, etc. | Eligible in Karna House only |
| **Vasistha Student**  | `10002`, `10008`, etc. | Adwitha Reddy, etc. | Eligible in Vasistha House only |
| **Vishwamithra Student** | `10009`, `10016`, etc. | Charan Teja, etc. | Eligible in Vishwamithra House only |

---

## Key Invariants Summary (Quick Overview)

1. **Mandatory Docs Sync:** Any code modification must be accompanied by an immediate update to the documentation in `docs/`.
2. **Zero External Server Dependency:** Do not introduce Node.js or Python backend servers for voter authentication or voting. All logic runs in the browser, securely communicating directly with Supabase via REST & Storage.
3. **Biometric Face Verification:** Must always execute before a ballot is submitted. The pre-trained cascade model `facefinder` (239 KB) and `pico.js` run completely offline in WebAssembly/JS on the client device.
4. **Secret Ballot 1-Row Register:** In `edit-votes.html`, individual voters are represented by exactly 1 row showing `✓ Voted (All 4 Posts)` (or 5 for Cabinet). Individual candidate selections are never displayed alongside student names.
5. **Teacher Eligibility:** All 87 teachers are assigned `houseCode: "ALL"`. They are permitted to vote in every house booth, and are the exclusive eligible voters for the Central School Cabinet booth.
6. **Booth Name Column:** The `booth_name` column exists on the `ballots` table. It does **not** exist on the `voters` table.
