# Data Schema & Customization Guide

This document defines how candidate information, photos, houses, and posts are structured in the system.

---

## 1. Candidate Data Model

Each house contains 4 candidate profiles corresponding to the 4 posts:

```json
{
  "id": "bheeshma",
  "name": "Bheeshma",
  "fullName": "Bheeshma House",
  "color": "#EAB308",
  "accent": "#CA8A04",
  "textColor": "#111827",
  "motto": "Unwavering Resolve & Duty",
  "candidates": {
    "boys_captain": {
      "postTitle": "Boys Captain",
      "name": "Arjun Verma",
      "grade": "Grade 12-A",
      "photo": "",
      "quote": "Leadership is action, not position."
    },
    "girls_captain": {
      "postTitle": "Girls Captain",
      "name": "Ananya Iyer",
      "grade": "Grade 12-B",
      "photo": "",
      "quote": "Together we strive, together we thrive."
    },
    "boys_vc": {
      "postTitle": "Boys Vice-Captain",
      "name": "Rohan Nair",
      "grade": "Grade 11-A",
      "photo": "",
      "quote": "Service with humility and courage."
    },
    "girls_vc": {
      "postTitle": "Girls Vice-Captain",
      "name": "Sneha Reddy",
      "grade": "Grade 11-C",
      "photo": "",
      "quote": "Empowering every student voice."
    }
  }
}
```

---

## 2. Default Houses & Color Palette

1. **Bheeshma**:
   - `color`: `#FACC15` (Yellow)
   - `accent`: `#EAB308`
   - `textColor`: `#1E293B`
2. **Guru Drona**:
   - `color`: `#3B82F6` (Blue)
   - `accent`: `#2563EB`
   - `textColor`: `#FFFFFF`
3. **Vasishta**:
   - `color`: `#EC4899` (Pink)
   - `accent`: `#DB2777`
   - `textColor`: `#FFFFFF`
4. **Vishwamithra**:
   - `color`: `#A855F7` (Purple)
   - `accent`: `#9333EA`
   - `textColor`: `#FFFFFF`
5. **Hanuman**:
   - `color`: `#F97316` (Orange)
   - `accent`: `#EA580C`
   - `textColor`: `#FFFFFF`
6. **Karna**:
   - `color`: `#EF4444` (Red)
   - `accent`: `#DC2626`
   - `textColor`: `#FFFFFF`

---

## 3. How to Update Candidates

There are two easy methods to update student names, classes, or images:

### Method A: Via the Built-in Admin Panel
1. Click the **⚙️ Edit Data / Settings** button in the top navigation bar.
2. Select any House from the dropdown.
3. Edit the Name, Grade/Class, and Photo URL / File path for each post.
4. Click **Save Changes**. The data is immediately updated and persisted in browser storage.

### Method B: Directly in `js/data.js`
Open `js/data.js` in any text editor and replace the default names, classes, and photo paths with your actual school candidates.
