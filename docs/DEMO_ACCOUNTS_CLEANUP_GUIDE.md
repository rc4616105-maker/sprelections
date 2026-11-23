# Demo Accounts & Test Data Cleanup Guide

> [!IMPORTANT]
> **Tracked Demo Account for Removal**:
> - **Voter ID:** `1C8492`
> - **Student Name:** `Aditya Vikram`
> - **Class / Section:** `Class 10 — Chatrapathi Shivaji (10-CS)`
> - **Purpose:** Temporary demonstration and presentation testing across all kiosks and universal booths.
> - **Status:** Active in test mode; must be removed prior to the official live school election.

---

## 1. List of All Active Demo Accounts
| Admission / Voter ID | Account Holder | Role / Type | Primary Location |
| :--- | :--- | :--- | :--- |
| **`1C8492`** | Aditya Vikram | Student Voter (10-CS) | `DEMO_ACCOUNTS` in `supabase-config.js`, `parse_roster.py` |
| **`0000`** | Aditya Vikram | Universal Fallback Voter | `DEMO_ACCOUNTS` in `supabase-config.js`, `parse_roster.py` |
| **`6000`** | Dr. Rajesh Sharma | Faculty Demo Voter | `Houses/teachers/data.js`, `teachers.json` |
| **`0001` – `0006`** | House Demo Students | Kiosk Specific Demo Accounts | `DEMO_ACCOUNTS` in `supabase-config.js` |

---

## 2. How to Completely Remove `1C8492` Before Official Live Election

When you are ready to switch the system into live, production-only voting:

### Step 1: Remove from `scripts/parse_roster.py`
In `scripts/parse_roster.py`, remove the `demo_profiles` block inside `parse_xlsx()`:
```python
# Remove or comment out:
demo_profiles = [ ... ]
```

### Step 2: Clear from `DEMO_ACCOUNTS` in `Houses/*/supabase-config.js`
In each kiosk's `supabase-config.js`, remove `"1C8492"` and `"0000"` from the `DEMO_ACCOUNTS` dictionary.

### Step 3: Run the Roster Export
Run:
```bash
python scripts/parse_roster.py
python scripts/update_candidates_and_demo.py
```
This regenerates clean production `data.js` files containing strictly the official student roster from `ELECTIONS HOUSES (1).xlsx` with zero test entries.

### Step 4: Clear Test Ballots in Supabase
Open `Houses/admin/index.html` -> **Supabase Console** -> Run SQL / Clear Ballots to wipe any test votes cast under `1C8492` or `0000`.
