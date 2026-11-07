"""
DealMind — Seed Script: Pre-populate Firebase with default admin accounts.

Usage:
    python scripts/seed_admins.py

Requirements:
    - firebase-admin pip package installed
    - FIREBASE_SERVICE_ACCOUNT_PATH set in .env (or firebase-service-account.json present)
    - FIREBASE_API_KEY set in .env

The script will:
1. Create each admin in Firebase Authentication (email/password)
2. Create the corresponding Firestore document in the 'admins' collection
"""

import sys
import os
from pathlib import Path

# Allow running from project root
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

# ── Pre-seeded admins ─────────────────────────────────────────────────────────
# Change these credentials before deploying to production!
SEED_ADMINS = [
    {
        "email":    "superadmin@dealmind.ai",
        "password": "DealMind@SuperAdmin2026!",
        "name":     "Super Administrator",
        "role":     "super_admin",
    },
    {
        "email":    "admin@dealmind.ai",
        "password": "DealMind@Admin2026!",
        "name":     "Deal Admin",
        "role":     "admin",
    },
    {
        "email":    "viewer@dealmind.ai",
        "password": "DealMind@Viewer2026!",
        "name":     "Deal Viewer",
        "role":     "viewer",
    },
]

# ── Seed loop ─────────────────────────────────────────────────────────────────
print("\n🌱 Seeding DealMind admin accounts into Firebase...\n")

for admin_data in SEED_ADMINS:
    email    = admin_data["email"]
    password = admin_data["password"]
    name     = admin_data["name"]
    role     = admin_data["role"]

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

print("\n✅ Seeding complete! Admin accounts ready.\n")
print("=" * 55)
print("  LOGIN CREDENTIALS (change these after first login!)")
print("=" * 55)
for a in SEED_ADMINS:
    print(f"  [{a['role'].upper():15}] {a['email']}")
    print(f"                   Password: {a['password']}")
    print()
