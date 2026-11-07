"""
DealMind Admin — Streamlit Auth Session
Manages login state and session-level admin context.
"""

import streamlit as st
from admin.firebase_config import sign_in_with_email_password, send_password_reset
from admin.admin_manager import get_admin_by_uid, update_last_login, ROLES


SESSION_KEY = "dealmind_admin_session"

# JavaScript injected once to prevent browser password-manager popups
# (Chrome's "Use strong password" / Google Password Manager suggestion).
_DISABLE_AUTOCOMPLETE_JS = """
<script>
(function() {
    function patchInputs() {
        document.querySelectorAll('input[type="password"]').forEach(function(el) {
            el.setAttribute('autocomplete', 'off');
            el.setAttribute('data-lpignore', 'true');
            el.setAttribute('data-form-type', 'other');
        });
        document.querySelectorAll('input[type="email"], input[type="text"]').forEach(function(el) {
            el.setAttribute('autocomplete', 'off');
        });
    }
    // Patch immediately and watch for Streamlit re-renders
    patchInputs();
    var observer = new MutationObserver(patchInputs);
    observer.observe(document.body, { childList: true, subtree: true });
})();
</script>
"""


def is_logged_in() -> bool:
    return SESSION_KEY in st.session_state and st.session_state[SESSION_KEY] is not None


def get_current_admin() -> dict | None:
    """Return the currently logged-in admin dict, or None."""
    return st.session_state.get(SESSION_KEY)


def login(email: str, password: str) -> dict:
    """
    Authenticate via Firebase, verify admin status in Firestore,
    and store session. Returns the admin profile dict on success.
    Raises ValueError with a user-friendly message on failure.
    """
    # 1. Firebase Auth
    token_data = sign_in_with_email_password(email, password)
    uid = token_data["localId"]

    # 2. Firestore admin lookup
    admin = get_admin_by_uid(uid)
    if admin is None:
        raise ValueError("Your account is not registered as a DealMind administrator.")
    if not admin.get("is_active", True):
        raise ValueError("Your admin account has been disabled. Contact an Admin.")

    # 3. Record login & persist session
    update_last_login(uid)
    admin["id_token"] = token_data["idToken"]
    st.session_state[SESSION_KEY] = admin
    return admin


def logout():
    """Clear admin session."""
    st.session_state.pop(SESSION_KEY, None)
    st.rerun()


def require_login():
    """
    Guard: if no admin is logged in, show the login page and stop execution.
    Call this at the top of any protected page/tab.
    """
    if not is_logged_in():
        render_login_page()
        st.stop()


def require_permission(permission: str):
    """
    Guard: stop if the logged-in admin lacks the required permission.
    """
    admin = get_current_admin()
    if admin is None:
        st.error("You are not logged in.")
        st.stop()
    role = admin.get("role", "viewer")
    allowed = ROLES.get(role, {}).get("permissions", [])
    if permission not in allowed:
        st.error(f"⛔ Access Denied — your role **{ROLES[role]['label']}** cannot perform `{permission}`.")
        st.stop()


# ── Login UI ──────────────────────────────────────────────────────────────────

def render_login_page():
    """Render the full-page admin login form."""
    # Inject autocomplete-disabling script FIRST (before any form renders)
    st.markdown(_DISABLE_AUTOCOMPLETE_JS, unsafe_allow_html=True)

    st.markdown("""
    <style>
        /* hide default streamlit chrome while on the login page */
        #MainMenu { visibility: hidden; }
        footer    { visibility: hidden; }
        header    { visibility: hidden; }

        .login-box {
            max-width: 420px;
            margin: 60px auto 0 auto;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 40px 36px 32px 36px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        }
        .login-logo {
            text-align: center;
            font-size: 2.4rem;
            margin-bottom: 4px;
        }
        .login-title {
            text-align: center;
            font-size: 1.5rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 2px;
        }
        .login-sub {
            text-align: center;
            font-size: 0.9rem;
            color: #64748B;
            margin-bottom: 28px;
        }
        .reset-info {
            background: #F0F9FF;
            border: 1px solid #BAE6FD;
            border-radius: 8px;
            padding: 12px 14px;
            font-size: 0.85rem;
            color: #0369A1;
            margin-bottom: 12px;
        }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="login-logo">💼</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">DealMind Admin</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Deal Intelligence Platform · Restricted Access</div>', unsafe_allow_html=True)

        tab_login, tab_reset = st.tabs(["🔐 Sign In", "🔑 Reset Password"])

        with tab_login:
            with st.form("admin_login_form", clear_on_submit=False):
                email    = st.text_input("Email Address", placeholder="admin@dealmind.ai")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In →", type="primary", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    with st.spinner("Authenticating…"):
                        try:
                            admin = login(email, password)
                            st.success(f"Welcome back, **{admin['name']}**! Redirecting…")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"🚫 {e}")
                        except Exception as e:
                            st.error(f"⚠️ Unexpected error: {e}")

        with tab_reset:
            st.markdown("""
            <div class="reset-info">
            📧 <strong>How password reset works:</strong><br>
            Enter your registered email below and click <em>Send Reset Link</em>.
            Firebase will send a password-reset email directly to that address.
            Click the link in the email, set your new password, then return here to sign in.
            The link expires in <strong>1 hour</strong>.
            </div>
            """, unsafe_allow_html=True)

            with st.form("reset_form"):
                reset_email = st.text_input("Registered Email", placeholder="admin@dealmind.ai")
                reset_btn = st.form_submit_button("Send Reset Link", use_container_width=True)

            if reset_btn:
                if not reset_email:
                    st.warning("Please enter your email address.")
                else:
                    try:
                        send_password_reset(reset_email)
                        st.success(
                            f"✅ Reset email sent to **{reset_email}**.\n\n"
                            "Check your inbox (and spam folder). "
                            "Click the link in the email to set a new password. "
                            "The link is valid for **1 hour**."
                        )
                    except ValueError as e:
                        st.error(f"🚫 {e}")

        st.markdown('</div>', unsafe_allow_html=True)
