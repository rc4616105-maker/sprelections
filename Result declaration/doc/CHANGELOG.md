# Project Changelog

All notable changes and updates to the School Election Declaration Module are documented in this file.

---

## [1.9.0] - 2026-11-18
### True Random Wheel, Bottom Buttons Removal & Large Straight-Column Tables
* **Completely Random Wheel Selection (`crypto.getRandomValues`)**:
  * Upgraded wheel selection from predictable pseudo-random to high-entropy `window.crypto.getRandomValues`.
  * Added natural randomized slice landing offsets ($20\%$ to $80\%$ within the slice) and varied full rotations ($6$ to $9$) so the pointer lands naturally instead of dead-center.
  * Every house—including the 6th final house—is spun on the wheel fairly, removing artificial auto-skipping.
* **Removed Bottom Action Buttons**:
  * Removed the entire bottom action controls bar (`🏠 Go to Home`, `🖨️ Print Summary`, and `🔄 Restart Election`) from the Grand Finale view.
* **Large, Spacious & Neat Table Layout with Straight Name Alignment**:
  * Replaced cramped flex rows with an explicit 3-column CSS Grid: `grid-template-columns: 145px 1fr auto;`.
  * **Column 1 (Post Title):** Fixed width of $145\text{px}$, preventing long titles like "Boys Vice-Captain" from colliding with names.
  * **Column 2 (Winner Name):** Bold, prominent ($1.12\text{rem}$ / weight $800$), crisp black (`#111827`), left-aligned down a **100% straight vertical column**.
  * **Column 3 (Grade / Class):** Styled as a clean pill badge (`.finale-grade-badge`) aligned on the right.
  * Expanded container max-width to $1560\text{px}$ with generous card padding ($1.6\text{rem}$) and header styling for an auditorium-ready presentation.

---

## [1.8.0] - 2026-11-18
### Spotlight Card Enlargement & Backdrop Navigation Fix
* **Substantially Enlarged Spotlight Card**:
  * Increased card dimensions to `clamp(480px, 44vw, 560px)` width and `clamp(540px, 82vh, 650px)` height.
  * Enlarged candidate photo frame to $165\text{px}$, candidate name to $2.25\text{rem}$ (`900` weight), and post title to $1.45\text{rem}$ for a commanding auditorium stage presence.
  * Increased touch brush coverage to **$140\text{px}$** for broad, effortless swipes on the larger canvas.
* **Backdrop Tap Navigation Fix**:
  * Fixed an event routing issue where tapping to the side of the spotlight card on the backdrop inadvertently triggered a history popstate back to the wheel.
  * Tapping to the side now strictly closes the spotlight modal and reliably keeps the presenter in the Scratch Arena to select the next cards.

---

## [1.7.0] - 2026-11-18
### Fresh-on-Reload, Browser Back Button & Header Spacing
* Ceremony progress resets on reload so the module always starts cleanly with all 6 houses on the wheel.
* Full browser Back button support via HTML5 History API.
* Moved `"House Selection Wheel"` title and remaining badge higher up for breathing room above the wheel pointer.

---

## [1.6.0] - 2026-11-18
### Direct Final House Scratch, Clean Spotlight & "Go to Home" Completion Flow
* Removed `"✕ Back to Cards"` top button and bottom `"Tap outside to return to cards"` pill from spotlight card.
* Fixed duplicate fanfare trigger when the 4th card reveals.
* Automatically skips wheel spin when 1 house remains, guiding directly to its scratch arena.
* Added `"🏠 Go to Home"` button returning to the home screen showing "Results of All 6 Houses Declared Successfully".

---

## [1.5.0] - 2026-11-18
### Slogan Removal, Enlarged House Reveal & Wheel Optimization
* Removed all house slogans and mottos for a clean, minimal look.
* Increased selected house modal title size to `clamp(2.5rem, 5.5vw, 3.4rem)`.
* Optimized wheel diameter up to $660\text{px}$ with inline header to ensure zero scrolling.

---

## [1.4.0] - 2026-11-18
### Zero-Scroll Viewport Lock & Uniform High-Power Scratch Sizing
* Enforced `overflow: hidden` across the entire viewport.
* Unified scratch brush radius to a massive $65\text{px}$ ($130\text{px}$ diameter) for uniform clearing across point, tap, and drag.

---

## [1.3.0] - 2026-11-18
### Big-Screen Touch Spotlight Mode & 70% Pop-up Reveal
* Added spotlight card expansion when any of the 4 cards is tapped in the arena grid.
* Automated 70% threshold auto-reveal with pop-up animation and fanfare.

---

## [1.2.0] - 2026-11-18
### Wheel Expansion, Center Interactive Spin & Clean House Slogans
* Converted center hub into an interactive clickable `"SPIN"` button.
* Removed `"Sound"` and `"Edit Data"` buttons from top bar.

---

## [1.1.0] - 2026-11-18
### Portal Theme Alignment & UI Polish
* Shifted to clean warm ivory/white (`#FAF7F2`) with crisp white (`#FFFFFF`) card surfaces.
* Replaced dark-mode aesthetic with 6px colored top borders.
* Removed emojis/symbols from wheel slices and candidate cards.

---

## [1.0.0] - 2026-11-18
### Initial Architecture & Implementation
* Established complete documentation in `doc/`.
* 6 houses: Bheeshma, Gurudrona, Hanuman, Karna, Vasistha, Vishwamithra.
* 4 leadership posts: Boys Captain, Girls Captain, Boys Vice-Captain, Girls Vice-Captain.
* Spin wheel with slice elimination physics, scratch cards with auto-reveal threshold, and audio synthesis.
