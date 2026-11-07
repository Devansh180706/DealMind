# DealMind — Roles & Access Control Guide

> Complete guide on what every role can do, who should get each role,
> and how to assign/change roles via Firebase or the app.

---

## 📌 Overview — The 2-Role System

DealMind uses **2 roles** stored in Firebase Firestore:

| Role | Badge Color | Who Controls It |
|---|---|---|
| **Admin** | 🔵 Blue | Any existing Admin can assign this |
| **Viewer** | 🟢 Green | Any existing Admin can assign this |

> **Platform Super Admin** = whoever owns the Firebase project (`venkatasaip52@gmail.com`).  
> They can do everything via the Firebase Console, regardless of app roles.

---

## 🔵 ADMIN ROLE — Full Access

### What an Admin can see and do

| Tab / Feature | What they can actually do |
|---|---|
| **📊 Deal Pipeline** | View all monitored B2B deals, deal sizes, stages (Open / Closed Won / Closed Lost), stakeholders, interaction count, memory bank IDs |
| **⚡ Brief Me** | Select any deal → generate an AI pre-call briefing → toggle Memory ON/OFF to compare generic vs grounded advice → see citation drawer with memory references |
| **📝 Log a Call** | Paste a meeting transcript/notes → AI extracts structured facts (budget, objections, stakeholders, commitments) → stores everything into Hindsight memory → detects duplicate transcripts via SHA-256 hash |
| **🚨 Active Alerts** | See all risk alerts across every deal — overdue commitments, silent stakeholders (14+ days no contact), legal review stalls — with severity (CRITICAL / HIGH) and recommended actions |
| **🧠 Playbook Insights** | View cross-deal AI-generated learnings → verify against ground truth → record deal closures (Won/Lost) to trigger the Hindsight `reflect()` learning loop |
| **👥 Admin Panel** | Add new users, change roles (admin ↔ viewer), enable/disable accounts, delete users, see login history |

### Admin-only actions that Viewers CANNOT do

```
✅ Generate pre-call briefings        ✅ Log meeting transcripts
✅ Extract facts into AI memory        ✅ Trigger cross-deal learning
✅ View playbook patterns              ✅ Record deal closures
✅ Access the Admin Panel              ✅ Add / remove / change users
✅ Enable or disable user accounts     ✅ Delete user accounts
```

---

## 🟢 VIEWER ROLE — Read-Only, Limited Access

### What a Viewer can see and do

| Tab / Feature | What they can actually do |
|---|---|
| **📊 Deal Pipeline** | View all deals, deal sizes, stages, stakeholders, memory bank IDs — **READ ONLY** |
| **🚨 Active Alerts** | See all risk alerts across deals with severity levels and recommended actions — **READ ONLY** |

### What Viewers CANNOT access

```
❌ Brief Me tab            (cannot generate AI briefings)
❌ Log a Call tab          (cannot add transcripts or memory)
❌ Playbook Insights tab   (cannot view or trigger cross-deal learning)
❌ Admin Panel             (cannot see or manage any users)
❌ No write access to anything — purely read-only visibility
```

---

## 🏢 Real-Life Examples — Who Gets Which Role?

### 🔵 Who should be an ADMIN?

> **Admins are people who actively work on deals and need to use AI features.**

| Person | Why they need Admin |
|---|---|
| **Sales Manager / Team Lead** | Needs to brief the team before calls, log debriefs, see alerts, manage who has app access |
| **Account Executive (AE)** | Directly handles deals — logs call notes, generates briefings before every customer call, tracks commitments |
| **Sales Operations Analyst** | Manages the pipeline data, runs playbook analysis, records deal closures to train the AI |
| **Revenue Operations (RevOps)** | Sets up and maintains the system, adds/removes users as team changes |
| **CRO / VP of Sales** | Needs full access to review all deals, alerts, and AI-generated playbooks |

**Example:**  
*Ravi is an Account Executive managing the Acme Corp deal. He logs every call transcript using "Log a Call", generates a briefing before each CFO meeting using "Brief Me", and monitors alerts for overdue commitments. He needs **Admin**.*

---

### 🟢 Who should be a VIEWER?

> **Viewers are people who need visibility into deals but should NOT touch the AI system or write anything.**

| Person | Why they only need Viewer |
|---|---|
| **CEO / Founder** | Wants to see which deals are active and what risks exist — doesn't need to operate the AI tools |
| **Finance / CFO** | Monitors deal pipeline values and revenue risks — doesn't need to log calls or generate briefings |
| **Legal Counsel** | Needs to track deals stuck in legal review from the Alerts tab — no need to operate the AI |
| **Investor / Board Member** | Wants a live read-only dashboard of the deal pipeline and risk status |
| **External Consultant (read-only)** | Brought in to review pipeline health but should not have write access |
| **Junior SDR (trainee)** | Can observe the pipeline and alerts for learning without touching memory or AI tools |

**Example:**  
*Priya is the CFO. She logs in every Monday to check the Deal Pipeline tab to see total revenue in play (\$1.2M across 8 deals) and the Active Alerts tab to flag any high-risk deals for finance planning. She never needs to generate briefings or log transcripts. She gets **Viewer**.*

---

## 🔧 How to Make a Person Admin or Viewer

There are **3 methods** — pick the one that fits your situation:

---

### Method 1 — Via the App's Admin Panel (Easiest, Recommended)

> **Requires:** You must already be logged in as an **Admin**

**Step 1: Create the user in Firebase Console first**
1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Click **Authentication** → **Users** tab
3. Click **Add user** → Enter their email and a temporary password → **Add user**
4. Copy the **UID** shown next to their email

**Step 2: Register them in the app**
1. Log into DealMind as Admin
2. Go to **👥 Admin Panel** tab
3. Scroll to **"➕ Add New User"** section
4. Paste their **Firebase UID**, enter their email, name, and choose role
5. Click **Register User** → Done ✅

**Step 3: Share credentials**
- Tell the new user their email + temporary password
- Ask them to log in and use the **Reset Password** tab to set their own password

---

### Method 2 — Via the Seed Script (Best for initial setup / bulk adding)

Edit [`scripts/seed_admins.py`](scripts/seed_admins.py) and add an entry:

```python
SEED_ADMINS = [
    # Existing entries...
    {
        "email":    "ravi@yourcompany.com",    # Their email
        "password": "Temp@Password123!",       # Temporary password (they will reset it)
        "name":     "Ravi Kumar",
        "role":     "admin",                   # "admin" or "viewer"
    },
    {
        "email":    "priya@yourcompany.com",
        "password": "Temp@Priya123!",
        "name":     "Priya Sharma",
        "role":     "viewer",
    },
]
```

Then run:
```bash
python scripts/seed_admins.py
```

The script creates Firebase Auth accounts + Firestore documents automatically.

---

### Method 3 — Directly in Firebase Console (No code needed)

**To create a new user:**
1. Firebase Console → **Authentication** → **Users** → **Add user**
2. Set email + password → note the UID

**To create their Firestore role document:**
1. Firebase Console → **Firestore Database** → **admins** collection
2. Click **+ Add document** → Document ID = the user's **UID**
3. Add these fields:

| Field | Type | Value |
|---|---|---|
| `email` | string | `ravi@yourcompany.com` |
| `name` | string | `Ravi Kumar` |
| `role` | string | `admin` or `viewer` |
| `is_active` | boolean | `true` |
| `created_at` | string | `2026-11-07T10:00:00+00:00` |
| `last_login` | null | _(leave null)_ |
| `login_count` | number | `0` |

---

### ✅ Full Walkthrough — Adding a User Directly via Firebase (Both Steps Required)

> **IMPORTANT:** Two separate steps are needed — one in Firebase Auth, one in Firestore.
> If you only do Step A (Auth), login will fail with "not registered as administrator".
> If you only do Step B (Firestore), login will fail because Firebase can't authenticate.

**STEP A — Create the user account in Firebase Authentication**

1. Go to [console.firebase.google.com](https://console.firebase.google.com) → select your project
2. Left sidebar → **Authentication** → **Users** tab
3. Click **"Add user"** button (top right)
4. Enter their **email address** + a **temporary password** → click **"Add user"**
5. The new user appears in the list — **copy their UID** (long string like `Xk7mN2qPabcdef123`)

**STEP B — Add their role document in Firestore Database**

1. Left sidebar → **Firestore Database** → find the **"admins"** collection
2. Click **"+ Add document"**
3. In the **Document ID** field → **paste the UID** from Step A (do NOT use Auto-ID)
4. Add all 7 fields by clicking **"+ Add field"** for each:

```
Field name   │ Type    │ Value to enter
─────────────┼─────────┼────────────────────────────────
email        │ string  │ ravi@yourcompany.com
name         │ string  │ Ravi Kumar
role         │ string  │ admin          ← or:  viewer
is_active    │ boolean │ true
created_at   │ string  │ 2026-11-07T10:00:00+00:00
last_login   │ null    │ (select null type, leave empty)
login_count  │ number  │ 0
```

5. Click **"Save"**

**STEP C — Share credentials with the new user**
- Tell them their **email** + **temporary password**
- Ask them to open the DealMind login page → **🔑 Reset Password** tab → enter their email → set a permanent password

---

### How to CHANGE an existing user's role

**Option A — Via Admin Panel (In-app)**
1. Log into DealMind as Admin → go to **👥 Admin Panel**
2. Find the user → expand their card
3. Use the **"Change Role"** dropdown → select new role → click **Update Role**

**Option B — Via Firebase Console**
1. Firestore Database → **admins** collection → find their document (by UID)
2. Click the `role` field → edit → change to `admin` or `viewer` → **Update**

**Option C — Via Python (one-off script)**
```python
import firebase_admin
from firebase_admin import credentials, firestore

firebase_admin.initialize_app(credentials.Certificate("firebase-service-account.json"))
db = firestore.client()

# Change role of a specific user by their UID
db.collection("admins").document("PASTE_UID_HERE").update({"role": "admin"})
print("Role updated!")
```

---

## 📊 Role Decision Flowchart

```
Does this person need to actively USE the AI tools?
(generate briefings, log transcripts, record learnings)
        │
        ├── YES → Do they also need to manage who has app access?
        │               │
        │               ├── YES or MAYBE → 🔵 ADMIN
        │               └── No specific need but won't hurt → 🔵 ADMIN
        │
        └── NO → Do they just need to monitor deals and alerts?
                        │
                        ├── YES (read-only monitoring) → 🟢 VIEWER
                        └── No access needed at all → Don't create an account
```

---

## 🔐 Security Best Practices

1. **Minimum privilege:** Default new users to **Viewer** unless they specifically need Admin
2. **Change default passwords:** Always use the Reset Password tab after seeding accounts
3. **Disable inactive accounts:** Use the Admin Panel to disable (not delete) accounts for people who leave — this preserves login history
4. **Never share accounts:** Each person gets their own Firebase Auth login
5. **Audit logins:** The Admin Panel shows each user's last login time and total login count

---

## 🗂️ Where Role Data Lives in Firebase

```
Firestore Database
└── admins (collection)
    ├── {UID of user 1} (document)
    │   ├── email:       "ravi@yourcompany.com"
    │   ├── name:        "Ravi Kumar"
    │   ├── role:        "admin"          ← This controls app access
    │   ├── is_active:   true
    │   ├── created_at:  "2026-11-07T..."
    │   ├── last_login:  "2026-11-07T..."
    │   └── login_count: 12
    │
    └── {UID of user 2} (document)
        ├── email:       "priya@yourcompany.com"
        ├── name:        "Priya Sharma"
        ├── role:        "viewer"         ← Read-only access
        ├── is_active:   true
        └── ...
```

The app reads this document on every login and shows/hides tabs based on the `role` field.
