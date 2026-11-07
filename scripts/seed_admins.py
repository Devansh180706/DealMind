"""
DealMind — Seed Script: Pre-populate Firebase with default admin accounts.

Usage:
    python scripts/seed_admins.py

Requirements:
    - firebase-admin pip package installed
    - FIREBASE_SERVICE_ACCOUNT_PATH set in .env (or firebase-service-account.json present)
    - FIREBASE_API_KEY set in .env

The script will:
1. Create each user in Firebase Authentication (email/password)
2. Create the corresponding Firestore document in the 'admins' collection

WHO IS THE SUPER ADMIN?
  The "super admin" of this system is whoever owns the Firebase project —
  i.e., the Google account (venkatasaip52@gmail.com) used to create the Firebase
  project. That account has full control via the Firebase Console and can:
    - Reset any user's password
    - Delete or disable any user
    - View all Firestore data
  Inside the app, all 'admin' role users share the same permissions.

ROLES:
  admin  — Full access to all tabs + can manage the admin/viewer roster
  viewer — Read-only: can only see Deal Pipeline and Active Alerts
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime, timezone

# ── Service account init ──────────────────────────────────────────────────────
SA_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json")
SA_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")

if Path(SA_PATH).exists():
    cred = credentials.Certificate(SA_PATH)
elif SA_JSON:
    import json
    cred = credentials.Certificate(json.loads(SA_JSON))
else:
    print("❌ Firebase service account not found.")
    print("   Set FIREBASE_SERVICE_ACCOUNT_PATH or FIREBASE_SERVICE_ACCOUNT_JSON in .env")
    sys.exit(1)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ── Pre-seeded users ──────────────────────────────────────────────────────────
# IMPORTANT: Change these passwords immediately after first login!
# Use the Firebase Console or the Reset Password tab on the login page.
SEED_ADMINS = [
    {
        "email":    "admin@dealmind.ai",
        "password": "DealMind@Admin2026!",
        "name":     "Deal Admin",
        "role":     "admin",          # Full access + manage users
    },
    {
        "email":    "admin2@dealmind.ai",
        "password": "DealMind@Admin2_2026!",
        "name":     "Deal Admin 2",
        "role":     "admin",          # Second admin — same permissions
    },
    {
        "email":    "viewer@dealmind.ai",
        "password": "DealMind@Viewer2026!",
        "name":     "Deal Viewer",
        "role":     "viewer",         # Read-only: pipeline + alerts only
    },
]

# ── Seed loop ─────────────────────────────────────────────────────────────────
print("\n🌱 Seeding DealMind admin accounts into Firebase...\n")

for user_data in SEED_ADMINS:
    email    = user_data["email"]
    password = user_data["password"]
    name     = user_data["name"]
    role     = user_data["role"]

    # 1. Create / get user in Firebase Auth
    try:
        user = auth.get_user_by_email(email)
        print(f"  ⚡ Auth user already exists: {email} (uid={user.uid})")
    except auth.UserNotFoundError:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name,
            email_verified=True,
        )
        print(f"  ✅ Created Auth user: {email} (uid={user.uid})")

    # 2. Create / update Firestore admin document
    doc_ref  = db.collection("admins").document(user.uid)
    existing = doc_ref.get()

    if existing.exists:
        print(f"     ↳ Firestore doc already exists for {email}, skipping.")
    else:
        doc_ref.set({
            "email":       email,
            "name":        name,
            "role":        role,
            "is_active":   True,
            "created_at":  datetime.now(timezone.utc).isoformat(),
            "last_login":  None,
            "login_count": 0,
        })
        print(f"     ↳ Firestore admin doc created — role: {role}")

print("\n✅ Seeding complete!\n")
print("=" * 60)
print("  LOGIN CREDENTIALS")
print("  !! Change these passwords after first login !!")
print("=" * 60)
for a in SEED_ADMINS:
    print(f"  [{a['role'].upper():7}] {a['email']}")
    print(f"           Password: {a['password']}")
    print()
print("  HOW TO CHANGE A PASSWORD:")
print("  Option A — Login page → Reset Password tab → enter email")
print("  Option B — Firebase Console → Authentication → Users → Reset password")
print("  Option C — Firebase Console → Authentication → Users → Edit → set new password")
print()
print("  WHO IS THE SUPER ADMIN?")
print("  The Firebase project owner (venkatasaip52@gmail.com) is the")
print("  platform-level super admin with full Firebase Console access.")
print("  Inside the app, all 'admin' role users have equal permissions.")
