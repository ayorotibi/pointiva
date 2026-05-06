import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Admin Review Dashboard")

# -----------------------------------------
# ACCESS CONTROL
# -----------------------------------------
if "access_token" not in st.session_state:
    st.error("You must log in first.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

# -----------------------------------------
# ADMIN BACKGROUND
# -----------------------------------------
def set_bg(color):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg("#FFF3E0")  # soft orange admin background

# -----------------------------------------
# ADMIN MODE BANNER
# -----------------------------------------
st.markdown(
    """
    <div style="
        width:100%;
        padding:14px;
        background-color:#FB8C00;
        color:white;
        font-size:22px;
        font-weight:700;
        border-radius:6px;
        text-align:center;
        margin-bottom:25px;">
        ⚙️ ADMIN MODE — System Management Console
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------
# ADMIN NAVIGATION BAR
# -----------------------------------------
st.markdown(
    """
    <style>
    .admin-nav {
        display: flex;
        gap: 12px;
        margin-bottom: 25px;
    }
    .admin-nav button {
        background-color: #FFE0B2;
        border: 1px solid #FB8C00;
        padding: 10px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
    }
    .admin-nav button:hover {
        background-color: #FFCC80;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="admin-nav">
        <button>📁 View All Uploads</button>
        <button>🕒 Recent Uploads</button>
        <button>👤 Uploads by User</button>
        <button>❌ Rejected Uploads</button>
        <button>💼 View All Purse</button>
        <button>💳 Purse by User</button>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------
# EXISTING ADMIN DASHBOARD CONTENT
# -----------------------------------------
st.title("Admin Review Dashboard")

# Fetch all uploads
resp = requests.get(f"{API_BASE}/admin/uploads", headers=headers)

if resp.status_code != 200:
    st.error("You are not an admin or cannot load uploads.")
    st.stop()

uploads = resp.json()

# Filter by status
status_filter = st.selectbox("Filter by status", ["all", "submitted", "in_review", "approved", "rejected"])

if status_filter != "all":
    uploads = [u for u in uploads if u["status"] == status_filter]

# Display uploads
for u in uploads:
    with st.expander(f"Upload {u['id']} — {u['filename']} — {u['status']}"):
        st.write("Submitted:", u["submitted"])
        st.write("User:", u.get("user"))
        st.write("Metadata:", u.get("metadata"))

        # Media preview
        try:
            st.image(f"../storage/uploads/{u['filename']}")
        except:
            st.info("Preview not available.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Approve {u['id']}"):
                r = requests.post(f"{API_BASE}/admin/approve/{u['id']}", headers=headers)
                st.success("Approved")
                st.rerun()

        with col2:
            if st.button(f"Reject {u['id']}"):
                r = requests.post(f"{API_BASE}/admin/reject/{u['id']}", headers=headers)
                st.warning("Rejected")
                st.rerun()
