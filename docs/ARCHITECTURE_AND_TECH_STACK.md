# 2. Architecture & Tech Stack

## Architectural Philosophy: Pure Static & Zero-Build

The platform is designed under a **Zero-Build, Pure Static Web Architecture**.

- **No Node.js runtime needed in production.**
- **No Webpack, Vite, Babel, or compilation pipeline.**
- **No external server processes required for authentication or vote handling.**

Any standard web server (VS Code Live Server, Python `http.server`, Apache, Nginx, or Netlify static hosting) can serve the files directly as static HTML, CSS, and vanilla ES6+ JavaScript.

---

## Complete Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Foundation** | HTML5, CSS3 (Custom Properties), ES6+ JavaScript | High-speed, responsive, lightweight kiosk UI |
| **Typography** | Plus Jakarta Sans, JetBrains Mono, Fraunces | Clear editorial aesthetic for cards, badges, and readouts |
| **Client Biometrics** | `pico.js` + Pretrained Haar Cascade (`facefinder`) | Fully client-side real-time human face detection |
| **Hardware Input** | WebHID API + Dedicated Key-Stream Receiver | Instant handheld USB/Bluetooth barcode scanner gun detection |
| **Cloud Database** | Supabase (PostgreSQL 15 via PostgREST) | Authoritative storage for ballots, voters, candidates, audit logs |
| **Cloud Storage** | Supabase Storage (`voter-photos` bucket) | High-resolution voter verification JPEG photos |
| **Local Cache** | Web Storage (`localStorage` & `sessionStorage`) | 0ms instant dashboard loading and session state persistence |
| **IPC & Sync** | BroadcastChannel API (`election_spr_2026_sync`) | Real-time cross-tab state synchronization |
| **Card Generation** | Python 3 + Pillow + python-barcode | Automated batch generation of voter ID cards and printable A4 sheets |

---

## Client-Side AI Biometrics: How It Works

Each polling booth includes client-side biometric verification without transmitting video streams to an external server:

```
[Webcam Video Stream]
         │
         ▼
[Hidden Canvas (320x240)] ──► Grayscale conversion: 0.299*R + 0.587*G + 0.114*B
         │
         ├──► 1. Lens Obstruction Analysis:
         │       • Mean Brightness < 14  ──► "Lens completely covered or too dark"
         │       • StdDev Variance < 8.5 ──► "Camera blocked by hand / flat object"
         │
         ├──► 2. Hardware FaceDetector (if available in Chromium)
         │
         └──► 3. Pico.js Haar Cascade (Runs pre-trained 239KB binary 'facefinder')
                 • Evaluates multi-scale pixel intensity differences
                 • Clusters detections (threshold score > 36.0)
                 • Steady Frame Counter: Requires 2 consecutive verified frames
```

### Why this design?
1. **Zero Privacy Risk:** The live video stream never leaves the voter's local computer.
2. **Instant Response:** Evaluates frames in ~15 milliseconds.
3. **Works Fully Offline:** The 239 KB `facefinder` cascade binary is stored locally inside each house directory and loaded via `fetch("./facefinder")`.

---

## Hardware Barcode Scanner Integration

Physical polling stations utilize handheld USB or Bluetooth barcode scanner guns that operate as keyboard wedge devices.

The system supports two complementary integration channels:

1. **Dedicated Invisible Stream Receiver (`#barcode-scanner-stream`):**
   - A hidden, autofocus-managed `<input>` permanently listens on the barcode tab.
   - When the scanner pulls its trigger, it fires rapid keystrokes ending in `Enter`.
   - The handler automatically strips prefixes/suffixes, validates the voter ID, and triggers verification within 50ms.
2. **Direct WebHID Device Pairing:**
   - For stations using raw USB HID mode, an **"Identify / Pair USB Scanner"** button connects directly via the Chrome WebHID API, providing device vendor feedback and diagnostics.
3. **Manual Entry Fallback:**
   - If a student's card barcode is torn or smudged, the polling officer clicks **"Enter Voter ID"** to type the numeric ID with built-in on-screen keyboard support.

---

## Supabase REST & Storage Integration

All booths communicate directly with Supabase via standard HTTPS REST calls:

```
[Polling Booth JS] ──HTTPS REST──► [Supabase PostgREST: /rest/v1/ballots]
[Polling Booth JS] ──HTTPS REST──► [Supabase Storage: /storage/v1/object/voter-photos]
```

- **Authentication:** Direct Bearer authorization using the public anonymous publishable key (`anon`).
- **Binary Image Upload:** Converts captured canvas JPEG Data URLs (`data:image/jpeg;base64,...`) into typed `Uint8Array` binary blobs and uploads directly to `{house_slug}/{admission_no}/{timestamp}.jpg`.
- **Signed URL Resolution:** Verification photos are securely read via signed URLs (`/storage/v1/object/sign/...`) with an in-memory client cache (`exp: 3600s`) to avoid redundant API hits.
- **Proxy Fallback:** If deployed on Netlify, an optional serverless proxy (`/.netlify/functions/supabase`) is available for environments requiring strict IP whitelisting.

---

## Offline Resilience & Instant Local Caching

1. **Dashboard 0ms Snapshot Cache:**  
   The administration console ([Houses/admin/edit-votes.html](file:///c:/Users/Abhinav/Documents/Election%20Spr%202026/Houses/admin/edit-votes.html)) caches the entire ballot database in `localStorage` (`spr_admin_snapshot_cache`). When opened, the UI renders instantly on frame 1 while seamlessly refreshing in the background.
2. **Pendrive Storage Sync:**  
   `Houses/assets/booth-session.js` exposes `window.PendriveStorage`, allowing local USB flash drives or file system access to record encrypted local backups if the internet drops.
