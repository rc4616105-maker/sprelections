# Core Technical Mechanisms

This document details the algorithms, mathematical models, and implementation mechanisms powering the School Digital Election Result Declaration module.

---

## 1. Dynamic Wheel Mechanism

### Mathematical Model & Physics
* **Slice Angular Width**:
  $$\theta = \frac{2\pi}{N}$$
  Where $N$ is the number of remaining houses ($6 \ge N \ge 1$).
* **Cryptographic Random Selection & Target Angle**:
  When a random house index $k$ ($0 \le k < N$) is selected using `window.crypto.getRandomValues`:
  $$\text{targetAngle} = 2\pi \times M + \left( \frac{3\pi}{2} - (k \times \theta + \delta \times \theta) \right)$$
  Where $M$ is a randomized number of full rotations ($6$ to $9$ turns), $\frac{3\pi}{2}$ corresponds to the top pointer indicator, and $\delta \in [0.20, 0.80]$ provides a natural randomized landing offset within the winning slice.
* **Easing Function**:
  Deceleration follows a cubic ease-out curve:
  $$\text{easeOutCubic}(t) = 1 - (1 - t)^3$$
  Where $t \in [0, 1]$.
* **Ticker Audio Trigger**:
  As the wheel rotates, when the current angle crosses a slice boundary ($\text{angle} \pmod \theta$), a short click/tick sound is emitted by the audio engine. The click frequency decreases naturally as the wheel slows down.
* **Slice Elimination**:
  When a house is completed, its ID is removed from the active wheel array. Slices automatically redistribute over the full $360^\circ$ circle for the remaining houses.

---

## 2. Scratch Card Mechanism & Big-Screen Spotlight Focus

### Touch-Optimized Large Screen Architecture
* **Grid Selection & Spotlight Modal**:
  * In the arena, the 4 posts are presented as elegant cards.
  * Tapping any card expands it into a **Spotlight Focus Modal** (`#scratchSpotlightModal`) with a darkened backdrop.
  * The expanded card is rendered in large dimensions ($520\text{px} \times 620\text{px}$) with an enlarged canvas foil layer, making fingertip scratching natural and effortless on large smartboards or projectors.
* **Touch Sensitivity & Fast Clearing**:
  * Brush radius is calibrated to $70\text{px}$ (stroke line width $140\text{px}$). Both single-point touches and drag sweeps clear identical massive $140\text{px}$ swaths of foil, allowing rapid reveals on smartboards and touchscreens without fatigue.
* **Zero-Scroll Viewport Calibration**:
  * All views are constrained to $100\text{vh}$ with `overflow: hidden`, dynamically resizing the wheel canvas (`window.innerHeight - 175px`) to prevent any scrollbars from appearing on stage displays.
* **70% Threshold & Pop-Up Celebration**:
  ```javascript
  const ratio = clearedPixels / samples;
  if (ratio >= 0.70) {
    this.reveal();
  }
  ```
  * Once $70\%$ is cleared, the remaining foil automatically dissolves with a burst pop-up animation (`cardPopSuccess`: scaling up to $1.08\times$ with celebratory bounce), triggering confetti and victory fanfare.
* **Return to Grid (Space / Click Outside)**:
  * Tapping anywhere outside the card on the backdrop, clicking `"✕ Back to Cards"`, or pressing the `SPACE` / `ESC` key smoothly closes the spotlight modal and returns the presenter to the 4-card grid to pick the remaining posts.
  * In the grid, the completed card is updated to the revealed winner with the **ELECTED** badge.

---

## 3. Web Audio Synthesis Engine (Zero Dependencies)
To ensure the application runs reliably offline on any school computer without relying on external MP3 assets, sound effects are generated natively via the **Web Audio API**:
* **Tick Sound**: Micro white-noise burst filtered through a high-pass biquad filter ($1200\text{ Hz}$) with an exponential gain decay over $20\text{ ms}$.
* **Scratch Sound**: Filtered white noise with random modulation during pointer movement.
* **Drumroll**: Rapid filtered oscillations creating build-up tension.
* **Victory Fanfare / Chime**: Harmonic major chord progression (C5 -> E5 -> G5 -> C6) using sine/triangle oscillators with sustained decay.
* **Audio Mute/Unmute Toggle**: Easily accessible on the top navigation bar.

---

## 4. State Persistence & Resilience
* **Storage Provider**: `window.localStorage`
* **Storage Key**: `SCHOOL_ELECTION_2026_STATE`
* **Preserved State Structure**:
  ```json
  {
    "activeHouseId": "bheeshma",
    "revealedHouses": ["bheeshma"],
    "revealedCards": {
      "bheeshma": ["boys_captain", "girls_captain"]
    },
    "customData": { ... }
  }
  ```
* **Safety Benefit**: If the host accidentally hits refresh (`Ctrl+R` or `F5`), the browser resumes exactly at the current house and cards without losing progress.
* **Hard Reset**: Protected by a confirmation dialog in the Settings / Reset panel.
