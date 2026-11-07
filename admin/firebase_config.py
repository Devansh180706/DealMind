"""
DealMind Admin — Firebase Configuration & Initialization
Handles both Firebase Admin SDK (server-side) and REST API (client-side auth).
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Firebase Client Config (from .env or hardcoded for demo) ─────────────────
FIREBASE_API_KEY        = os.getenv("FIREBASE_API_KEY", "")
FIREBASE_AUTH_DOMAIN    = os.getenv("FIREBASE_AUTH_DOMAIN", "")
FIREBASE_PROJECT_ID     = os.getenv("FIREBASE_PROJECT_ID", "")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "")
FIREBASE_MSG_SENDER_ID  = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "")
FIREBASE_APP_ID         = os.getenv("FIREBASE_APP_ID", "")

# ── Firebase Admin SDK (server-side) ─────────────────────────────────────────
_admin_initialized = False


def get_firestore_client():
    """Return an initialized Firestore client using Firebase Admin SDK."""
    global _admin_initialized
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not _admin_initialized:
            # Try service-account JSON file first, then env-var JSON string
            sa_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json")
            sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")

            if Path(sa_path).exists():
                cred = credentials.Certificate(sa_path)
            elif sa_json:
                cred = credentials.Certificate(json.loads(sa_json))
            else:
                raise FileNotFoundError(
                    "Firebase service account not found.\n"
                    "Set FIREBASE_SERVICE_ACCOUNT_PATH or FIREBASE_SERVICE_ACCOUNT_JSON in your .env"
                )

            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            _admin_initialized = True

        return firestore.client()

    except ImportError:
        raise ImportError("firebase-admin package not installed. Run: pip install firebase-admin")


# ── REST Auth helpers ─────────────────────────────────────────────────────────
AUTH_BASE = "https://identitytoolkit.googleapis.com/v1/accounts"


def sign_in_with_email_password(email: str, password: str) -> dict:
    """
    Authenticate a user via Firebase Auth REST API.
    Returns the Firebase ID token payload or raises ValueError on failure.
    """
    if not FIREBASE_API_KEY:
        raise ValueError("FIREBASE_API_KEY is not set in your .env file.")

    resp = requests.post(
        f"{AUTH_BASE}:signInWithPassword?key={FIREBASE_API_KEY}",
        json={"email": email, "password": password, "returnSecureToken": True},
        timeout=10,
    )
    data = resp.json()

    if "error" in data:
        msg = data["error"].get("message", "Authentication failed.")
        # Make Firebase messages user-friendly
        friendly = {
            "EMAIL_NOT_FOUND":    "No account found with that email.",
            "INVALID_PASSWORD":   "Incorrect password.",
            "INVALID_EMAIL":      "Invalid email address.",
            "USER_DISABLED":      "This account has been disabled.",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many failed attempts. Try again later.",
        }
        raise ValueError(friendly.get(msg, msg))

    return data   # keys: idToken, localId (uid), email, refreshToken, expiresIn


def send_password_reset(email: str) -> bool:
    """Send a password-reset email via Firebase Auth REST API."""
    if not FIREBASE_API_KEY:
        raise ValueError("FIREBASE_API_KEY is not set in your .env file.")

    resp = requests.post(
        f"{AUTH_BASE}:sendOobCode?key={FIREBASE_API_KEY}",
        json={"requestType": "PASSWORD_RESET", "email": email},
        timeout=10,
    )
    data = resp.json()
    if "error" in data:
        raise ValueError(data["error"].get("message", "Failed to send reset email."))
    return True
