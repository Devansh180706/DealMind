"""
DealMind Admin — Admin Management Panel (Admin role only)
Rendered as a tab in app.py for Admins to manage the admin roster.
"""

import streamlit as st
from admin.auth import require_permission
from admin.admin_manager import (
    list_all_admins, update_admin_role, toggle_admin_active,
    delete_admin, ROLES
)


def render_admin_panel():
    """Full admin management UI — only Admins can reach this."""
    require_permission("manage_admins")

    st.markdown('<div class="main-header">👥 Admin User Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage admin accounts, roles, and access.</div>',
                unsafe_allow_html=True)

    # ── Summary metrics ───────────────────────────────────────────────────────
    try:
        all_admins = list_all_admins()
    except Exception as e:
        st.error(f"⚠️ Could not load admins from Firestore: {e}")
        return

    total  = len(all_admins)
    active = sum(1 for a in all_admins if a.get("is_active", True))
    admins_count  = sum(1 for a in all_admins if a.get("role") == "admin")
    viewers_count = sum(1 for a in all_admins if a.get("role") == "viewer")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Users",  total)
    m2.metric("Active",       active)
    m3.metric("Admins",       admins_count)
    m4.metric("Viewers",      viewers_count)

    st.markdown("---")

    # ── Admin roster ──────────────────────────────────────────────────────────
    st.markdown("### 📋 User Roster")

    for admin in all_admins:
        uid        = admin["uid"]
        name       = admin.get("name", "Unknown")
        email      = admin.get("email", "")
        role       = admin.get("role", "viewer")
        is_active  = admin.get("is_active", True)
        last_login = admin.get("last_login") or "Never"
        login_cnt  = admin.get("login_count", 0)
        role_meta  = ROLES.get(role, {"label": role, "color": "#64748B"})
        status_icon = "🟢" if is_active else "🔴"

        with st.expander(
            f"{status_icon} **{name}** — {email}  [{role_meta['label']}]",
            expanded=False,
        ):
            col_info, col_actions = st.columns([3, 2])

            with col_info:
                st.markdown(f"**UID:** `{uid}`")
                st.markdown(f"**Email:** {email}")
                st.markdown(
                    f"**Role:** <span style='background:{role_meta['color']};color:#fff;"
                    f"padding:2px 8px;border-radius:12px;font-size:0.8rem'>"
                    f"{role_meta['label']}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Status:** {'✅ Active' if is_active else '❌ Disabled'}")
                st.markdown(f"**Last Login:** {last_login[:19] if last_login != 'Never' else 'Never'}")
                st.markdown(f"**Total Logins:** {login_cnt}")

            with col_actions:
                st.markdown("**🔧 Actions**")

                # Role change (admin ↔ viewer only)
                new_role = st.selectbox(
                    "Change Role",
                    options=list(ROLES.keys()),
                    index=list(ROLES.keys()).index(role),
                    format_func=lambda r: ROLES[r]["label"],
                    key=f"role_{uid}",
                )
                if st.button("Update Role", key=f"update_role_{uid}"):
                    try:
                        update_admin_role(uid, new_role)
                        st.success(f"Role updated to **{ROLES[new_role]['label']}**")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

                # Toggle active/disabled
                toggle_label = "Disable Account" if is_active else "Enable Account"
                if st.button(toggle_label, key=f"toggle_{uid}"):
                    toggle_admin_active(uid, not is_active)
                    st.success(f"Account {'enabled' if not is_active else 'disabled'}.")
                    st.rerun()

                # Delete with confirmation
                if st.button("🗑️ Delete User", key=f"delete_{uid}", type="secondary"):
                    st.session_state[f"confirm_delete_{uid}"] = True

                if st.session_state.get(f"confirm_delete_{uid}"):
                    st.warning(f"Permanently delete **{email}**?")
                    c1, c2 = st.columns(2)
                    if c1.button("Yes, delete", key=f"confirm_yes_{uid}"):
                        delete_admin(uid)
                        st.session_state.pop(f"confirm_delete_{uid}", None)
                        st.success("User deleted.")
                        st.rerun()
                    if c2.button("Cancel", key=f"confirm_no_{uid}"):
                        st.session_state.pop(f"confirm_delete_{uid}", None)
                        st.rerun()

    st.markdown("---")

    # ── Add new user ──────────────────────────────────────────────────────────
    st.markdown("### ➕ Add New User")
    st.info(
        "⚠️ First create the user in **Firebase Console → Authentication → Add User** "
        "(set their email & password there). Then paste their **UID** below to register them here."
    )

    with st.form("add_admin_form"):
        new_uid   = st.text_input("Firebase UID",  placeholder="Paste the UID from Firebase Console")
        new_email = st.text_input("Email Address", placeholder="newuser@dealmind.ai")
        new_name  = st.text_input("Display Name",  placeholder="Jane Doe")
        new_role  = st.selectbox("Role", list(ROLES.keys()),
                                 format_func=lambda r: ROLES[r]["label"])
        add_btn   = st.form_submit_button("Register User", type="primary")

    if add_btn:
        if not all([new_uid, new_email, new_name]):
            st.error("All fields are required.")
        else:
            try:
                from admin.admin_manager import create_admin
                create_admin(uid=new_uid, email=new_email, name=new_name, role=new_role)
                st.success(f"✅ **{new_name}** registered as **{ROLES[new_role]['label']}**!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to add user: {e}")

    st.markdown("---")

    # ── How to change passwords ───────────────────────────────────────────────
    st.markdown("### 🔑 Changing Passwords")
    st.markdown("""
**You cannot change passwords from inside this app.**
Passwords are managed entirely by **Firebase Authentication** in two ways:

**Option 1 — User resets their own password (Recommended)**
1. Go to the login page → click **🔑 Reset Password** tab
2. Enter the user's registered email → click **Send Reset Link**
3. Firebase sends an email with a reset link (valid for 1 hour)
4. Click the link → enter a new password → done

**Option 2 — Admin changes a password via Firebase Console**
1. Go to [Firebase Console](https://console.firebase.google.com) → **Authentication** → **Users**
2. Find the user → click **⋮ (menu)** → **Reset password**
3. Firebase emails a reset link directly to the user

**Option 3 — Admin sets a password directly (Firebase Console)**
1. Firebase Console → **Authentication** → **Users**
2. Find the user → click their email → **Edit** (pencil icon)
3. Enter a new password → **Save**
""")
