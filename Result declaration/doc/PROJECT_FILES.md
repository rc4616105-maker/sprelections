# Project File Map & Architecture

This document catalogs every file and directory in the project, explaining its responsibility and integration.

```
Result declaration/
├── doc/
│   ├── README.md               # Documentation landing page
│   ├── IDEA_AND_CONCEPT.md     # Concept, houses, colors, posts, and flow
│   ├── MECHANISMS.md           # Mathematical models, wheel physics & scratch logic
│   ├── DATA_SCHEMA.md          # Candidate data structure & customization guide
│   ├── PROJECT_FILES.md        # File map (this file)
│   └── CHANGELOG.md            # Ongoing log of changes and feature updates
│
├── index.html                  # Main application entry point & view stages
├── css/
│   ├── main.css                # Base styling, typography, glassmorphism & themes
│   ├── wheel.css               # Spin wheel styling, pointer, ticker & lighting
│   ├── scratch.css             # Scratch card canvas, foil effect, badge & candidate cards
│   └── finale.css              # Grand finale cabinet presentation & print layout
│
├── js/
│   ├── data.js                 # 6 Houses, colors, posts, and candidate profiles
│   ├── audio.js                # Web Audio API engine (wheel clicks, scratch, drumroll, fanfare)
│   ├── confetti.js             # Canvas-based celebratory particle/confetti system
│   ├── wheel.js                # Canvas wheel renderer, spin animation & elimination logic
│   ├── scratch.js              # Canvas scratch card mechanics, auto-reveal & thresholds
│   ├── admin.js                # In-app Candidate & Settings editor modal
│   └── app.js                  # Master application orchestrator, navigation & state manager
│
└── assets/
    └── icons/                  # SVG icons, emblems and graphics
```

---

## Instructions for Making Changes
Whenever any change or enhancement is introduced to the codebase:
1. Update the corresponding technical code files in `css/`, `js/`, or `index.html`.
2. Record the summary of changes in `doc/CHANGELOG.md`.
3. If new mechanisms, posts, or houses are added, update `doc/MECHANISMS.md` and `doc/DATA_SCHEMA.md` accordingly.
