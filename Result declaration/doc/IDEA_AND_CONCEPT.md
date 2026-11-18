# Project Concept & Idea: School Digital Election Result Declaration

## 1. Overview
The **Digital Election Result Declaration Module** is a high-energy, interactive stage and auditorium web application built to reveal school cabinet election results. Instead of static slides or verbal announcements, this module brings suspense, celebration, and engagement through two core gamified mechanics:
1. **The Dynamic Spin Wheel**: Selects houses at random to determine the order of announcement.
2. **Interactive Scratch Cards**: Unveils the winners for the 4 designated leadership posts per house with suspenseful foil-scratching, drumrolls, and confetti bursts.

---

## 2. Houses & Color Profiles
The election features 6 distinct houses, each with a designated brand color matching the official school portal:

| House Name | Primary Color | Accent Border | Text Style |
| :--- | :--- | :--- | :--- |
| **Bheeshma House** | Warm Yellow (`#EAB308`) | Amber (`#CA8A04`) | Charcoal (`#111827`) |
| **Gurudrona House** | Royal Blue (`#2563EB`) | Deep Azure (`#1D4ED8`) | White (`#FFFFFF`) |
| **Hanuman House** | Vibrant Orange (`#EA580C`) | Deep Tangerine (`#C2410C`) | White (`#FFFFFF`) |
| **Karna House** | Crimson Red (`#DC2626`) | Dark Red (`#B91C1C`) | White (`#FFFFFF`) |
| **Vasistha House** | Rose Pink (`#DB2777`) | Deep Rose (`#BE185D`) | White (`#FFFFFF`) |
| **Vishwamithra House** | Royal Purple (`#7C3AED`) | Deep Violet (`#6D28D9`) | White (`#FFFFFF`) |

---

## 3. Leadership Posts
For each of the 6 houses, 4 student leaders are declared (total 24 elected student council members):
1. **Boys Captain**
2. **Girls Captain**
3. **Boys Vice-Captain**
4. **Girls Vice-Captain**

---

## 4. End-to-End Ceremony Flow
1. **Welcome & Arena Screen**:
   - Title: School Cabinet Election Declaration.
   - Shows current status of all 6 houses (Pending vs Revealed).
   - "Enter Wheel Arena" button.
2. **Spin Wheel Phase**:
   - The wheel displays all remaining (unannounced) houses.
   - Host clicks **"SPIN WHEEL"** (or hits Spacebar).
   - Wheel accelerates, ticks with audio cues, and smoothly decelerates to land on a house.
   - Dramatic announcement banner: *"House [Name] is Selected!"*.
   - Button: *"Show Results for House [Name]"*.
3. **House Reveal Arena (Scratch Cards)**:
   - Fullscreen stage background dynamically styled in the house's signature color theme.
   - 4 foil-stamped scratch cards represent the 4 posts.
   - Tapping any card expands it into a Big-Screen Spotlight Focus Modal.
   - Scratching can be done with touch or stylus with high coverage.
   - Once ~70% scratched, foil auto-dissolves with celebratory pop-up animation and victory sound.
   - Tapping anywhere outside the card returns to the arena to select remaining posts.
4. **House Summary**:
   - Once all 4 cards in the house are scratched, the "Cabinet Formed" victory banner appears.
   - "Next House" button appears.
5. **Wheel Elimination & Full Dynamic Spin**:
   - Returning to the Wheel, previously declared houses are removed. Slices redistribute over $360^\circ$.
   - Every single house is selected through a fair, cryptographically secure dynamic spin on the wheel.
6. **Grand Finale Showcase**:
   - Once all 6 houses are scratched, the master Student Council Showcase presents all 24 elected student leaders in a spacious, perfectly aligned 3-column auditorium layout.
