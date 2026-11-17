# 5. Voting Kiosks & Biometrics Flow

Every polling booth kiosk implements a standardized, high-speed, 4-step progressive disclosure voting lifecycle.

---

## The 4-Step Voting Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Identification (Barcode Gun or Manual Voter ID)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Identity Confirmation & Background Camera Warm-Up    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Candidate Selection Across All Open Leadership Roles│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ FACE GUARD: Real-Time Human Face Verification & Photo Capture│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Ballot Recorded & 3-Second Automatic Booth Reset    │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 1: Identification & Barcode Scanning

- **Default Mode — Barcode Scanner Station:**
  - Displays a clean scanner target graphic and an active green pulse.
  - An invisible `<input id="barcode-scanner-stream">` continuously captures keyboard strokes from any USB or Bluetooth barcode scanner gun.
  - When the officer points the gun at the student's physical card and pulls the trigger, the barcode digits are read, validated, and processed within 50ms without clicking any buttons.
- **Manual Mode — Enter Voter ID:**
  - Clickable tab for manual keyboard entry if a card's barcode is damaged.
- **Accreditation Checks:**
  1. **Inactive Check:** Rejects voters marked inactive.
  2. **House Match Check:** In student house booths, voters registered to a different house are rejected with a clear message (e.g. *"Student belongs to Karna House. Please direct them to the Karna Polling Station"*).
  3. **Double-Voting Check:** Queries Supabase to verify whether this voter ID has already cast an active ballot.
  4. **Central Booth Guard:** If accessed at `Houses/central/index.html`, students are rejected; only teachers (`houseCode: "ALL"`) may vote.

---

### Step 2: Confirm Voter Identity

- Renders the voter's avatar initials, full name, class, section, house tag, and verification status.
- Shows whether the voter is a student or teacher (*"Authorized Teacher / Faculty"*).
- **Background Camera Warm-Up:**  
  While the voter glances at their name on screen, `warmUpBackgroundCamera()` silently requests camera access, attaches the media stream to a hidden `<video id="camera-video">`, and displays:
  ```text
  Camera ready — verification photo will auto-capture when you press Cast Vote.
  ```
  *(If the camera takes a moment or permission is pending, it provides informative fallback text).*

---

### Step 3: Candidate Selection

- Dynamic grid rendering all open leadership roles for that house:
  - **House Booths:** Boys Captain, Girls Captain, Boys Vice Captain, Girls Vice Captain (4 roles).
  - **School Cabinet:** Head Boy, Head Girl, Vice Head Boy, Vice Head Girl, Sports Captain (5 roles).
- The voter clicks their chosen candidate card in each role section.
- **Cast Action Bar:**
  - Floats at the bottom of the screen.
  - Displays progress (e.g. `Selected Candidates: 3 / 4`).
  - The **Cast Vote** button remains disabled until exactly 1 candidate is chosen for every required role.

---

### The Face Verification Guard Modal (`#face-guard-modal`)

When the voter clicks **Cast Vote**, the kiosk activates the Face Verification Guard across **all 7 houses**:

1. **Visual Modal Overlay:**
   - Opens a focused, high-contrast modal with a live camera preview (`#face-live-video`) framed inside an animated oval guide (`#face-oval-guide`).
2. **Real-Time Facial Analysis Loop:**
   - Every 200 milliseconds, `detectHumanFace()` captures a frame to a hidden 320x240 canvas.
   - **Anti-Hand / Anti-Obstruction Filter:**  
     Computes frame mean brightness and standard deviation variance. If a voter tries to place their palm or finger over the lens, the oval border flashes red and warns:
     ```text
     Camera is blocked by hand or object. Please uncover the lens.
     ```
   - **Biometric Detection:**  
     Evaluates the frame with `pico.js` and the pre-loaded Haar cascade `facefinder`.
3. **Automatic Verification & Capture:**
   - Once an unobstructed human face is recognized for **2 consecutive steady frames (~400ms)**:
     - The oval flashes green: `✓ Face Detected! Hold still...`
     - The verification photo is captured as a JPEG.
     - The ballot is submitted to Supabase and pendrive backup.
4. **Delayed Fullscreen Loading Circle Overlay (`#loading-overlay`):**
   - If network or storage operations take longer than ~350ms (e.g. under low-bandwidth WiFi), a centered circular spinner overlay appears displaying:
     - Circular rotating spinner in the house accent color (`.spinner-circle`)
     - **"Saving Ballot..."**
     - **"Please wait a moment..."**
   - Fast connections (<350ms) cancel the timer before it displays, avoiding screen flicker.
   - Reassures voters and polling officers that the ballot is being securely processed, preventing duplicate submission attempts or fear of application freeze.
5. **Hardware Fallback:**
   - If a kiosk computer has no webcam connected or camera permission was blocked in Chrome, a friendly fallback activates after 1.5 seconds enabling the confirm button so polling stations are never blocked by hardware failure.

---

### Step 4: Ballot Recorded & Automatic Reset

- Displays a confirmation badge: **"Ballot Recorded — Vote Casted"**.
- Summarizes the voter's name, ID, and selected candidates.
- Starts a **3-second countdown progress bar**.
- When the timer expires (or when the officer presses **"Ready for Next Voter"**):
  - Clears all candidate selections.
  - Stops the camera media stream tracks.
  - Resets state and returns to **Step 1: Scan Barcode** for the next student in line.
