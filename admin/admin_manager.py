"""
DealMind Admin — Firestore Admin User Manager
Handles CRUD for admin user profiles stored in the 'admins' Firestore collection.

Roles (2 only):
  - admin  : Full access to all features + can manage other admins/viewers
  - viewer : Read-only access to pipeline and alerts
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from admin.firebase_config import get_firestore_client

ADMINS_COLLECTION = "admins"


# ── Role definitions (2 roles only) ──────────────────────────────────────────
ROLES = {
    "admin": {
        "label": "Admin",
        "permissions": [
            "view_pipeline",
            "brief_me",
            "log_call",
            "view_alerts",
            "view_playbook",
            "manage_admins",   # Admins can manage the full admin roster
        ],
        "color": "#1D4ED8",   # blue
    },
    "viewer": {
        "label": "Viewer",
        "permissions": ["view_pipeline", "view_alerts"],
        "color": "#065F46",   # green
    },
}


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLES.get(role, {}).get("permissions", [])


# ── Firestore helpers ─────────────────────────────────────────────────────────

def get_admin_by_uid(uid: str) -> Optional[dict]:
    """Fetch admin document from Firestore by Firebase UID."""
    db = get_firestore_client()
    doc = db.collection(ADMINS_COLLECTION).document(uid).get()
    if doc.exists:
        return {"uid": doc.id, **doc.to_dict()}
    return None


def get_admin_by_email(email: str) -> Optional[dict]:
    """Fetch admin document from Firestore by email."""
    db = get_firestore_client()
    docs = (
        db.collection(ADMINS_COLLECTION)
        .where("email", "==", email)
        .limit(1)
        .stream()
    )
    for doc in docs:
        return {"uid": doc.id, **doc.to_dict()}
    return None


def list_all_admins() -> list[dict]:
    """Return all admin documents, ordered by role then name."""
    db = get_firestore_client()
    docs = db.collection(ADMINS_COLLECTION).stream()
    admins = [{"uid": d.id, **d.to_dict()} for d in docs]
    role_order = {"admin": 0, "viewer": 1}
    return sorted(admins, key=lambda a: (role_order.get(a.get("role", "viewer"), 9),
                                         a.get("name", "")))


def update_last_login(uid: str):
    """Record the last login timestamp for an admin."""
    db = get_firestore_client()
    db.collection(ADMINS_COLLECTION).document(uid).update({
        "last_login": datetime.now(timezone.utc).isoformat(),
        "login_count": _firestore_increment(1),
    })


def create_admin(uid: str, email: str, name: str, role: str = "viewer") -> dict:
    """Create a new admin document in Firestore."""
    if role not in ROLES:
        raise ValueError(f"Invalid role '{role}'. Choose from: {list(ROLES)}")
    db = get_firestore_client()
    data = {
        "email": email,
        "name": name,
        "role": role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login": None,
        "login_count": 0,
    }
    db.collection(ADMINS_COLLECTION).document(uid).set(data)
    return {"uid": uid, **data}


def update_admin_role(uid: str, new_role: str):
    """Update an admin's role."""
    if new_role not in ROLES:
        raise ValueError(f"Invalid role '{new_role}'.")
    db = get_firestore_client()
    db.collection(ADMINS_COLLECTION).document(uid).update({"role": new_role})


def toggle_admin_active(uid: str, active: bool):
    """Enable or disable an admin account."""
    db = get_firestore_client()
    db.collection(ADMINS_COLLECTION).document(uid).update({"is_active": active})


def delete_admin(uid: str):
    """Remove an admin document from Firestore."""
    db = get_firestore_client()
    db.collection(ADMINS_COLLECTION).document(uid).delete()


# ── Firestore server-side increment helper ────────────────────────────────────
def _firestore_increment(n: int):
    from google.cloud.firestore_v1.transforms import Increment
    return Increment(n)
