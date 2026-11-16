# 9. Production Deployment & Domain Setup Guide (GoDaddy .in + Master Laptop Operations)

> [!IMPORTANT]
> **MANDATORY DOCUMENTATION SYNC POLICY:**  
> Whenever ANY change, feature, bug fix, or UI adjustment is made to any part of this project, the corresponding documentation in the `docs/` folder MUST be updated immediately in the same turn.

---

## 1. Executive Summary & Architecture

The **School House Elections 2026** platform is designed with a **decoupled, pure static frontend and cloud database architecture**. This architecture eliminates the need to maintain, patch, or scale a custom backend server on election day.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ELECTION DAY TOPOLOGY                           │
└────────────────────────────────────────────────────────────────────────┘

 [ School Lab Station 1 ] ─── Bheeshma House Kiosk   (HTTPS)
 [ School Lab Station 2 ] ─── Gurudrona House Kiosk  (HTTPS) ──┐
 [ School Lab Station 3 ] ─── Hanuman House Kiosk    (HTTPS)   │
 [ School Lab Station 4 ] ─── Karna House Kiosk      (HTTPS)   ├──> [ GoDaddy .in Domain ]
 [ School Lab Station 5 ] ─── Vasistha House Kiosk   (HTTPS)   │     (e.g., schoolelection.in)
 [ School Lab Station 6 ] ─── Vishwamithra Kiosk     (HTTPS)   │
 [ School Lab Station 7 ] ─── School Cabinet Kiosk   (HTTPS) ──┘
           │                                                       ▲
           ▼ (USB Scanners & Webcams)                              │
 ┌────────────────────────────────────────────────────────┐        │
 │              CLIENT-SIDE EDGE EXECUTION                │        │
 │  • Pico.js Face Verification Guard                     │        │
 │  • Hardware Barcode Scanner (WebHID)                   │        │
 └─────────────────────────┬──────────────────────────────┘        │
                           │                                       │
                           ▼ (Direct REST & Realtime WSS)          │
 ┌────────────────────────────────────────────────────────┐        │
 │                SUPABASE CLOUD PLATFORM                 │        │
 │  • PostgreSQL (ballots, voters, candidates, audit_logs)│        │
 │  • Cloud Storage Bucket (voter-photos)                 │        │
 └─────────────────────────▲──────────────────────────────┘        │
                           │                                       │
                           │ (Live Admin Audit & Control)          │
                           │                                       │
 ┌─────────────────────────┴──────────────────────────────┐        │
 │           YOUR LAPTOP: MASTER ELECTION COMMAND         │────────┘
 │  • Live Turnout KPIs & Graph Monitoring                │
 │  • Secret Ballot Vote Cancellation & Attribution       │
 │  • Candidate Management on the Fly                     │
 │  • Official Certificate Printing & Excel Export        │
 └────────────────────────────────────────────────────────┘
```

---

## 2. The Mandatory HTTPS / Camera Security Rule

> [!CAUTION]
> **Why HTTPS is 100% Non-Negotiable:**  
> Modern web browsers (Google Chrome, Microsoft Edge, Mozilla Firefox, Safari) enforce a strict security policy: **Webcam access (`navigator.mediaDevices.getUserMedia`) is completely disabled over plain `http://` on any remote IP address or network domain**.
>
> Camera access is allowed **ONLY** under:
> 1. `http://localhost` or `http://127.0.0.1` (the local computer itself).
> 2. **`https://` with a valid SSL/TLS certificate** (any domain or subdomain).
>
> If polling kiosks in the school computer lab open the site over an unencrypted local IP (e.g. `http://192.168.1.50:5500`), the browser will **block the webcam**, causing the **Face Verification Guard to fail**.  
> **Using a custom domain with SSL/HTTPS ensures every lab kiosk has seamless, permanent camera access.**

---

## 3. Deployment Option Comparison

| Feature | Option 1: Cloudflare Pages / Vercel (Recommended) | Option 2: Laptop-Hosted via Cloudflare Tunnel |
| :--- | :--- | :--- |
| **How it Works** | Static files hosted on global CDN; domain points via CNAME. | Static files served from your laptop; tunnel pipes to domain. |
| **SSL/HTTPS Certificate** | **Automatic & Free** (active in 5 mins). | **Automatic & Free** via Cloudflare Tunnel. |
| **Laptop Dependence** | **Zero Kiosk Downtime Risk.** If laptop restarts, kiosks stay up. | **High Risk.** If laptop sleeps, closes, or drops Wi-Fi, all kiosks freeze. |
| **School Wi-Fi Load** | Kiosks download assets once and cache locally; very fast. | All kiosk traffic routes through your laptop's local Wi-Fi. |
| **Setup Complexity** | Very Simple (drag-and-drop or Git commit). | Requires installing and running `cloudflared` CLI. |
| **Recommendation** | ⭐ **Strongly Recommended for Production** | Good for local testing or restricted air-gapped simulations. |

---

## 4. Option 1 Walkthrough (Recommended): Cloudflare Pages + GoDaddy Domain

### Step 1: Buy the Domain on GoDaddy
1. Visit [GoDaddy](https://www.godaddy.com) and search for your preferred `.in` domain (e.g., `schoolelection2026.in` or `springdaleelections.in`).
2. Complete the purchase and navigate to **My Products** → **DNS Management**.

### Step 2: Deploy Static Files to Cloudflare Pages (Free Tier)
1. Create a free account at [Cloudflare](https://dash.cloudflare.com/).
2. In the sidebar, navigate to **Compute (Workers) & Pages** → **Create application** → **Pages**.
3. Choose **Upload assets** (Direct Upload without Git) or connect your GitHub repository.
4. Set the project name (e.g., `school-elections-2026`).
5. Upload the contents of the project folder:
   - Root files (`index.html`, etc.)
   - `Houses/` directory
   - `voter_cards/` directory
6. Click **Deploy Site**. In 30 seconds, Cloudflare provides a live URL (e.g., `school-elections-2026.pages.dev`).

### Step 3: Link Your GoDaddy Domain in Cloudflare Pages
1. In your Cloudflare Pages project, go to **Custom domains** → **Set up a custom domain**.
2. Type your domain (e.g., `schoolelection2026.in` or `vote.schoolelection2026.in`).
3. Cloudflare gives you the exact DNS records to add:
   - If using a subdomain (e.g., `vote.schoolelection2026.in`):
     - **Type:** `CNAME`
     - **Name:** `vote`
     - **Value:** `school-elections-2026.pages.dev`
   - If using root domain (`schoolelection2026.in`):
     - Change GoDaddy Nameservers to Cloudflare (recommended for 1-click SSL), OR add the CNAME/A records indicated.
4. In **GoDaddy DNS Management**:
   - Add the `CNAME` record.
5. Within 5 to 15 minutes, Cloudflare automatically provisions a free SSL certificate. Your election site is now live at `https://vote.schoolelection2026.in`!

---

## 5. Option 2 Walkthrough: Laptop-Hosted via Cloudflare Tunnel (`cloudflared`)

If you want your laptop to physically serve the website files directly:

### Step 1: Install Cloudflare Tunnel on Your Laptop
1. Download `cloudflared` for Windows from [Cloudflare Releases](https://github.com/cloudflare/cloudflared/releases).
2. Open PowerShell as Administrator and verify:
   ```powershell
   cloudflared --version
   ```

### Step 2: Start Local Server on Laptop
Run your local server on your laptop (e.g. Live Server on port 5500):
```powershell
# Verify Live Server or local server is active on 5500
Test-NetConnection -ComputerName 127.0.0.1 -Port 5500
```

### Step 3: Launch Secure Tunnel to Your GoDaddy Domain
Authenticate with Cloudflare and route your domain:
```powershell
cloudflared tunnel --url http://127.0.0.1:5500
```
This instantly generates a secure public HTTPS link that forwards all incoming traffic to port 5500 on your laptop, fully encrypted with SSL!

---

## 6. Supabase Cloud Configuration Verification

Your production database is Cloud Supabase. Before election morning, verify these settings:

1. **Verify Credentials in [Houses/admin/supabase-config.js](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/Houses/admin/supabase-config.js):**
   ```javascript
   const DEFAULT_SUPABASE_URL = "https://your-project-id.supabase.co";
   const DEFAULT_SUPABASE_KEY = "your-anon-publishable-key";
   ```
2. **Verify Database Tables in Supabase Dashboard:**
   - `ballots`: Holds all cast and cancelled role ballots with `booth_name`, timestamps, and photo URLs.
   - `voters`: Holds accreditation records (`status`, `cast_at`, `verified_by`).
   - `candidates`: Holds approved candidates across the 6 houses and Central School Cabinet.
   - `audit_logs`: Preserves immutable event audit trails (who cancelled a ballot, when, and reason).
3. **Storage Bucket:**
   - Bucket `voter-photos` must exist and be set to Public (or allow signed read access) so verification photos preview instantly in the admin audit modal.

---

## 7. Election Day Hardware & Computer Lab Setup

### Station Allocation (7 Kiosks Total)

| Station ID | Target House / Electorate | Kiosk URL to Open on Browser |
| :--- | :--- | :--- |
| **Kiosk 1** | Bheeshma House | `https://yourdomain.in/Houses/bheeshma/index.html` |
| **Kiosk 2** | Gurudrona House | `https://yourdomain.in/Houses/gurudrona/index.html` |
| **Kiosk 3** | Hanuman House | `https://yourdomain.in/Houses/hanuman/index.html` |
| **Kiosk 4** | Karna House | `https://yourdomain.in/Houses/karna/index.html` |
| **Kiosk 5** | Vasistha House | `https://yourdomain.in/Houses/vasistha/index.html` |
| **Kiosk 6** | Vishwamithra House | `https://yourdomain.in/Houses/vishwamithra/index.html` |
| **Kiosk 7** | School Cabinet (Faculty Only) | `https://yourdomain.in/Houses/central/index.html` |

### Hardware Verification on Each Kiosk
1. **Full-Screen Browser Mode:** Press `F11` in Chrome or Edge to enter kiosk full-screen mode.
2. **Camera Permission:** Click **Allow** on the initial camera prompt. Check that the oval face guide displays the video feed.
3. **USB Barcode Gun:** Scan a test student card. Confirm the barcode input registers cleanly and auto-advances to the voter identity confirmation screen.
4. **Station Registration:** When opening the booth for the first time, register the station name (e.g., "Computer Lab - Station 3") and the officer's name.

---

## 8. Laptop Master Command Center Protocol

Your laptop acts as the **Central Operations Desk**:

1. **Open Dashboard:**  
   Open `https://yourdomain.in/Houses/admin/index.html`.
2. **Monitor Live Turnout:**  
   - Real-time auto-sync refreshes every 2 seconds.
   - Observe live turnout percentages across all 6 houses + Central Cabinet.
3. **Biometric Audit & Cancelled Ballots:**  
   - If an officer or student reports an accidental scan or error:
     1. Open [Edit & Manage Votes](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/Houses/admin/edit-votes.html).
     2. Click **Cancelled Ballots** or filter by voter ID.
     3. Click **Cancel Vote** — voids all 4 (or 5) posts at once and stamps the cancelling officer's name (`cancelled_by`).
     4. The student is immediately accredited to cast a new vote.
     5. The Secret Ballot principle is fully preserved (`Ballot Choice Confidential`).
4. **Election Close & Official Results:**  
   - When polling ends, open [All Election Results](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/Houses/admin/results.html).
   - Click **Print Results** on [index.html](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/Houses/admin/index.html) to:
     - Generate the formal, high-resolution printable election certificate.
     - Export the complete audit spreadsheet to Excel via SheetJS (`vendor/xlsx.full.min.js`).

---

## 9. Disaster Recovery & Offline Contingency Protocols

- **Internet Glitch During Voting:**  
  If school Wi-Fi temporarily drops, kiosks queue ballots in `localStorage` (`spr_offline_ballots_queue`). Once connectivity resumes, ballots auto-sync to Supabase automatically.
- **Station Hardware Failure:**  
  If a kiosk PC crashes or loses power, simply open the house URL on any backup laptop, phone, or tablet. No votes are lost because state lives in Cloud Supabase.
- **Accidental Tab Closure:**  
  Kiosk URLs can be re-opened immediately without losing station registration (stored in `localStorage`).
