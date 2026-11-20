# Production Deployment & Operations Plan
## GoDaddy .in Domain + Master Admin Laptop Setup
### School House Elections 2026

---

> [!IMPORTANT]
> **MANDATORY DOCUMENTATION SYNC POLICY:**  
> Whenever ANY change, feature, bug fix, or UI adjustment is made to any part of this project, the corresponding documentation in the `docs/` folder MUST be updated immediately in the same turn.

---

## 1. System Architecture: How It Works & What Runs Where

In this project, the architecture is split into three high-performance, fault-tolerant tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ELECTION DAY TOPOLOGY                           │
└────────────────────────────────────────────────────────────────────────┘

 [ School Lab Kiosk 1 ] ─── Bheeshma House Kiosk   (HTTPS)
 [ School Lab Kiosk 2 ] ─── Gurudrona House Kiosk  (HTTPS) ──┐
 [ School Lab Kiosk 3 ] ─── Hanuman House Kiosk    (HTTPS)   │
 [ School Lab Kiosk 4 ] ─── Karna House Kiosk      (HTTPS)   ├──> [ GoDaddy .in Domain ]
 [ School Lab Kiosk 5 ] ─── Vasistha House Kiosk   (HTTPS)   │     (e.g., https://schoolelection.in)
 [ School Lab Kiosk 6 ] ─── Vishwamithra Kiosk     (HTTPS)   │
 [ School Lab Kiosk 7 ] ─── School Cabinet Kiosk   (HTTPS) ──┘
           │                                                       ▲
           ▼ (USB Scanners & Webcams)                              │
 ┌────────────────────────────────────────────────────────┐        │
 │              CLIENT-SIDE EDGE EXECUTION                │        │
 │  • Pico.js Face Verification Guard (Offline Wasm/JS)   │        │
 │  • Hardware Barcode Scanner (WebHID Keyboard Emulation)│        │
 └─────────────────────────┬──────────────────────────────┘        │
                           │                                       │
                           ▼ (Direct REST & Realtime WSS)          │
 ┌────────────────────────────────────────────────────────┐        │
 │                SUPABASE CLOUD PLATFORM                 │        │
 │  • PostgreSQL Database (ballots, voters, candidates)   │        │
 │  • Cloud Storage Bucket (voter-photos)                 │        │
 └─────────────────────────▲──────────────────────────────┘        │
                           │                                       │
                           │ (Live Admin Audit & Control)          │
                           │                                       │
 ┌─────────────────────────┴──────────────────────────────┐        │
 │           YOUR LAPTOP: MASTER ELECTION COMMAND         │────────┘
 │  • Web Server / Cloudflare Tunnel Host                 │
 │  • Live Turnout KPIs & Graph Monitoring                │
 │  • Secret Ballot Vote Cancellation & Attribution       │
 │  • Candidate Management on the Fly                     │
 │  • Official Certificate Printing & Excel Export        │
 └────────────────────────────────────────────────────────┘
```

### Breakdown of Roles:
1. **Your Laptop (Master Election Command & Host):**
   - **Role A (Server):** Hosts the web application and pipes it to the GoDaddy `.in` domain over a secure encrypted tunnel.
   - **Role B (Admin Command):** Runs the Master Admin Dashboard (`Houses/admin/index.html`) and Edit & Manage Votes Workbench (`Houses/admin/edit-votes.html`). You monitor turnout in real-time (2-second sync), inspect voter photos, cancel duplicate/erroneous votes with officer attribution, and print official certificates.
2. **Cloud Supabase (The Cloud Database Backend):**
   - Automatically stores all cast ballots, voter accreditation flags, candidates, and biometric audit photos.
   - Kiosks and your admin laptop communicate directly with Supabase via secure REST APIs and WebSocket real-time channels.
3. **GoDaddy `.in` Domain + Cloudflare (HTTPS Edge):**
   - Provides an official, easy-to-type web address for school lab computers (e.g., `https://schoolelection.in`).
   - Automatically issues a valid, trusted SSL/TLS certificate.

---

## 2. The Mandatory Camera / HTTPS Security Rule

> [!CAUTION]
> **Why HTTPS is 100% Non-Negotiable:**  
> Modern desktop web browsers (Chrome, Edge, Firefox, Brave) have a strict security rule:  
> **Webcam access (`navigator.mediaDevices.getUserMedia`) is completely blocked over plain `http://` on any remote local IP (e.g. `http://192.168.1.50:5500`)**.
> 
> Camera access is permitted **ONLY** on:
> 1. `http://localhost` (only on the laptop itself).
> 2. **`https://` with a valid SSL certificate** (any domain or subdomain).
> 
> If school lab computers connect over unencrypted HTTP, the browser will refuse to open the webcam, blocking the **Face Verification Guard**.  
> **Routing your GoDaddy `.in` domain through Cloudflare guarantees free, automatic HTTPS/SSL so all lab webcams work instantly.**

---

## 3. Two Deployment Options for Your Laptop

| Feature | Method 1: Laptop as Host via Cloudflare Tunnel (Your Desired Plan) | Method 2: Cloudflare Pages CDN + Laptop Admin (Recommended Fallback) |
| :--- | :--- | :--- |
| **Where files live** | Directly on your laptop (`c:\Users\Abhinav\Documents\Election Spr 2026`). | Uploaded to Cloudflare Pages edge CDN. |
| **How kiosks reach it** | Kiosks -> `schoolelection.in` -> Cloudflare Tunnel -> Your Laptop port 5500. | Kiosks -> `schoolelection.in` -> Cloudflare Global CDN. |
| **Domain Setup** | GoDaddy `.in` domain managed via Cloudflare Tunnel CNAME. | GoDaddy `.in` domain managed via Cloudflare Pages CNAME. |
| **SSL / HTTPS** | **Free & Automatic** (Issued by Cloudflare). | **Free & Automatic** (Issued by Cloudflare). |
| **Laptop Role** | Web Server + Master Admin Console. | Master Admin Console (Zero server load). |
| **If Laptop sleeps** | Kiosks temporarily lose connection to web files. | Kiosks continue voting without interruption! |

---

## 4. Step-by-Step Execution Plan

### Step 1: Purchasing the Domain on GoDaddy
1. Go to [GoDaddy](https://www.godaddy.com) and search for a `.in` domain:
   - Examples: `schoolelection2026.in`, `springdaleelections.in`, `sprevoting.in`.
2. Select the `.in` domain and complete checkout (typically ₹400 – ₹600 for the first year).
3. Do **NOT** buy expensive hosting, email, or SSL add-ons from GoDaddy — Cloudflare provides world-class enterprise SSL and tunneling completely free of charge.

---

### Step 2: Creating a Free Cloudflare Account
1. Visit [Cloudflare](https://dash.cloudflare.com/sign-up) and create a free account.
2. Click **Add a Domain** and type your newly purchased GoDaddy domain (e.g., `schoolelection2026.in`).
3. Select the **Free Plan** ($0/month).
4. Cloudflare will scan existing DNS records and provide two Cloudflare Nameservers (e.g., `aria.ns.cloudflare.com` and `theo.ns.cloudflare.com`).
5. Open your **GoDaddy Domain Dashboard**:
   - Go to **Manage DNS** -> **Nameservers** -> **Change Nameservers**.
   - Select **I'll use my own nameservers**.
   - Paste the two Cloudflare nameservers and click **Save**.
   *(Nameserver propagation usually takes between 5 to 15 minutes).*

---

### Step 3: Setting Up Your Laptop as the Master Host (Method 1)

This method lets your laptop run the web server and host the elections module live:

#### A. Install the Cloudflare Tunnel Utility (`cloudflared`) on Your Laptop:
1. Open PowerShell as Administrator on your laptop.
2. Download and install `cloudflared` using `winget` (built into Windows 11):
   ```powershell
   winget install Cloudflare.cloudflared
   ```
   *(Or download the 64-bit `.exe` directly from [Cloudflare Releases](https://github.com/cloudflare/cloudflared/releases)).*
3. Verify installation:
   ```powershell
   cloudflared --version
   ```

#### B. Start Your Local Web Server:
Start your local server on port 5500 (VS Code Live Server or Python HTTP Server):
```powershell
# In c:\Users\Abhinav\Documents\Election Spr 2026
python -m http.server 5500 --bind 127.0.0.1
```
*(Or keep VS Code Live Server running on port 5500).*

#### C. Run the Secure Tunnel to Your GoDaddy Domain:
To make your laptop instantly accessible to the world over HTTPS:
```powershell
# 1-click instant tunnel:
cloudflared tunnel --url http://127.0.0.1:5500
```
This prints a secure `https://<random-id>.trycloudflare.com` link.  
To bind it directly to your custom GoDaddy `.in` domain (e.g., `schoolelection2026.in`):
1. In Cloudflare Dashboard, go to **Zero Trust** -> **Networks** -> **Tunnels**.
2. Click **Create a Tunnel** (name it `election-laptop`).
3. Follow the 1-line command displayed to authenticate your laptop.
4. Set Public Hostname:
   - **Subdomain:** `vote` (or leave blank for root)
   - **Domain:** `schoolelection2026.in`
   - **Service:** `HTTP://127.0.0.1:5500`
5. Click **Save Tunnel**.

Now, typing `https://schoolelection2026.in` in any computer lab browser securely reaches your laptop over valid HTTPS!

---

### Step 4: Laptop Power & Network Invariants (Crucial!)

Because your laptop is acting as the host:
1. **Disable Sleep Mode:**
   - Go to Windows Settings -> **System** -> **Power & battery**.
   - Set **"When plugged in, put my device to sleep after"** to **Never**.
   - Set **"When I close the lid"** (under Control Panel -> Power Options) to **Do nothing**.
2. **Dedicated Power Charger:** Keep the laptop plugged into continuous AC power with a surge protector or UPS.
3. **Dedicated Stable Wi-Fi / LAN:** Connect the laptop to the school's primary wired Ethernet cable or high-speed Wi-Fi router.

---

### Step 5: Setting Up the 7 Computer Lab Polling Kiosks

On election morning, set up the 7 polling stations in the school computer lab:

| Station ID | Target House / Electorate | Exact Browser URL to Open |
| :--- | :--- | :--- |
| **Kiosk 1** | Bheeshma House | `https://schoolelection2026.in/Houses/bheeshma/index.html` |
| **Kiosk 2** | Gurudrona House | `https://schoolelection2026.in/Houses/gurudrona/index.html` |
| **Kiosk 3** | Hanuman House | `https://schoolelection2026.in/Houses/hanuman/index.html` |
| **Kiosk 4** | Karna House | `https://schoolelection2026.in/Houses/karna/index.html` |
| **Kiosk 5** | Vasistha House | `https://schoolelection2026.in/Houses/vasistha/index.html` |
| **Kiosk 6** | Vishwamithra House | `https://schoolelection2026.in/Houses/vishwamithra/index.html` |
| **Kiosk 7** | Central School Cabinet (Teachers Only) | `https://schoolelection2026.in/Houses/central/index.html` |

#### Station Hardware Setup Steps:
1. **Camera Permission:** Click **Allow** on the camera popup. Verify the oval face guide displays the video feed.
2. **Kiosk Fullscreen:** Press `F11` in Chrome or Edge to lock into full-screen polling mode.
3. **USB Barcode Gun:** Plug in the barcode scanner. Scan a test card to confirm instant voter accreditation.
4. **Station Registration:** Type the station booth name (e.g. `Station 3 - Hanuman Lab`) and Officer Name when the booth loads.

---

### Step 6: Master Laptop Administration Protocols During Polling

On your laptop, keep two primary tabs open:

1. **Live Turnout & Monitoring Dashboard:**
   - **URL:** `http://127.0.0.1:5500/Houses/admin/index.html`
   - Automatically polls Supabase every 2 seconds.
   - Shows live turnout percentages, house-by-house vote counts, and real-time graphs.
2. **Edit & Manage Votes Workbench:**
   - **URL:** `http://127.0.0.1:5500/Houses/admin/edit-votes.html`
   - **Secret Ballot Protected:** Displays **1 row per student** (`✓ Voted (All 4 Posts)`). Individual candidate choices are strictly confidential.
   - **Interactive KPI Filters:** Click **Total Accepted Ballots**, **Cancelled Ballots**, **Eligible Master Roster**, or **Remaining Not Voted** to view filtered tables instantly.
   - **Cancelling a Vote:** If a voter scanned by accident or had a dispute:
     1. Click **Cancel Vote**.
     2. Enter the cancelling officer's name / reason.
     3. The student's previous vote is voided, and they are immediately cleared to re-vote.
3. **Election Conclusion & Results Certification:**
   - Open `Houses/admin/results.html`.
   - Click **Print Results** on `Houses/admin/index.html` to generate official printable certificates with school headers and export full audit records to Excel (`.xlsx`).

---

## 5. Pre-Election Verification Checklist

- [ ] GoDaddy `.in` domain purchased.
- [ ] Cloudflare Nameservers updated in GoDaddy DNS.
- [ ] SSL certificate active (green padlock on `https://schoolelection2026.in`).
- [ ] `cloudflared` installed and running on admin laptop (or files deployed to Cloudflare Pages).
- [ ] Laptop sleep/hibernate completely disabled.
- [ ] Test vote submitted from a remote lab PC with barcode scan + Pico.js face capture.
- [ ] Test vote verified in Supabase `ballots` table with photo in `voter-photos` storage bucket.
- [ ] Test vote cancelled in `edit-votes.html` and verified that student is allowed to re-vote.
- [ ] Backup power bank / UPS connected to admin laptop.
