import streamlit as st
import requests
import time
import json
import platform
from datetime import datetime
import geocoder  # optional

st.set_page_config(page_title="Pointiva Dashboard", layout="wide")

API_BASE = "https://pointiva.onrender.com"
API_URL = f"{API_BASE}/dashboard"
API_UPLOAD_URL = "https://pointiva.onrender.com/upload"
API_STATUS_URL = "https://pointiva.onrender.com/upload/"
API_LIST_URL = "https://pointiva.onrender.com/uploads"


# -----------------------------------------
# SESSION INITIALIZATION
# -----------------------------------------
if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

if "full_name" not in st.session_state:
    st.session_state.full_name = None


# -----------------------------------------
# BACKGROUND + SECTION HEADER HELPERS
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

def section_header(text):
    st.markdown(
        f"""
        <h3 style="margin-top:30px; color:#2E7D32; border-left:5px solid #66BB6A; padding-left:10px;">
            {text}
        </h3>
        """,
        unsafe_allow_html=True
    )

# -----------------------------------------
# LOGIN BLOCK
# -----------------------------------------
if st.session_state.access_token is None:

    # LOGIN BACKGROUND
    set_bg("#87CEEB")  # sky blue login background
   
    st.title("Pointiva: A moment in time...")
    st.subheader("Sign in to continue")

    username = st.text_input("Username", value="")
    password = st.text_input("Password", type="password", value="")

    if st.button("Sign in"):
        resp = requests.post(
            f"{API_BASE}/token",
            data={"username": username, "password": password},
        )
        if resp.status_code == 200:
            data = resp.json()

            st.session_state.access_token = data["access_token"]
            st.session_state.role = data["role"]
            st.session_state.username = data["username"]
            st.session_state.full_name = data["full_name"]

            st.success("Logged in successfully.")
            # Redirect admins immediately
            if st.session_state.role == "admin":
                st.switch_page("pages/admin_dashboard.py")
            st.rerun()
        else:
            st.error("Invalid credentials.")

    st.stop()

# -----------------------------------------
# AUTHENTICATED BACKGROUND
# -----------------------------------------
# Background colour based on role
if st.session_state.role == "admin":
    set_bg("#FFF3E0")  # soft orange for admin
else:
    set_bg("#E8F5E9")  # light green for creators

# -----------------------------------------
# ADMIN SIDEBAR LINK (only for admin users)
# -----------------------------------------
if st.session_state.get("role") == "admin":
    st.sidebar.page_link("pages/admin_dashboard.py", label="Admin Dashboard")

# -----------------------------------------
# GREETING
# -----------------------------------------
st.markdown(
    f"""
    <h2 style="color:#1B5E20; font-weight:600;">
        👋 Welcome back, {st.session_state.full_name}
    </h2>
    """,
    unsafe_allow_html=True
)


# -------------------------
# Logout button (sidebar)
# -------------------------
if st.sidebar.button("Logout"):
    for key in ["access_token", "role", "username", "full_name"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# -----------------------------
# AUTHENTICATED DASHBOARD FETCH
# -----------------------------
headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

response = requests.get(f"{API_BASE}/dashboard", headers=headers)

if response.status_code != 200:
    st.error("Failed to load dashboard. Check authentication.")
    st.stop()

dashboard = response.json()

user = dashboard["user"]
wallet = dashboard["wallet"]
uploads = dashboard["uploads"]
featured = dashboard["featured"]

# -----------------------------------------
# WALLET SUMMARY
# -----------------------------------------
section_header("Your Wallet")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div style="padding:20px; border-radius:10px; background:#ffffff; 
        box-shadow:0 2px 6px rgba(0,0,0,0.1);">
            <h3 style="color:#2E7D32;">💰 Available Points</h3>
            <h2 style="margin-top:-10px;">{wallet['available_points']}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="padding:20px; border-radius:10px; background:#ffffff; 
        box-shadow:0 2px 6px rgba(0,0,0,0.1);">
            <h3 style="color:#F9A825;">⏳ Pending Points</h3>
            <h2 style="margin-top:-10px;">{wallet['pending_points']}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="padding:20px; border-radius:10px; background:#ffffff; 
        box-shadow:0 2px 6px rgba(0,0,0,0.1);">
            <h3 style="color:#1565C0;">🌟 Lifetime Earnings</h3>
            <h2 style="margin-top:-10px;">{wallet['lifetime_earnings']}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------------------
# 3. UPLOAD NEW MOMENT
# -----------------------------------------
section_header("Upload New Moment")

uploaded_file = st.file_uploader(
    "Choose a photo or video",
    type=["jpg", "jpeg", "png", "mp4", "mov"]
)

if uploaded_file is not None:
    st.write("File selected:", uploaded_file.name)

    if st.button("Upload Now"):

        timestamp = datetime.now().isoformat()
        device_info = platform.platform()

        try:
            g = geocoder.ip('me')
            location = {"lat": g.latlng[0], "lng": g.latlng[1]}
        except:
            location = {"lat": None, "lng": None}

        metadata = {
            "timestamp": timestamp,
            "device": device_info,
            "location": location,
            "caption": "Demo upload",
            "tags": ["demo", "pointiva"]
        }

        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            data = {"metadata": json.dumps(metadata)}
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

            response = requests.post(
                API_UPLOAD_URL,
                files=files,
                data=data,
                headers=headers
            )

        if response.status_code == 200:
            data = response.json()
            st.success(f"Upload successful! ID: {data['id']} Status: {data['status']}")

            left, right = st.columns([2, 1])

            with left:
                st.subheader("Preview")
                if uploaded_file.type.startswith("image"):
                    st.image(uploaded_file, caption=uploaded_file.name, width=400)
                elif uploaded_file.type.startswith("video"):
                    st.video(uploaded_file)
                else:
                    st.info("Preview not available.")

            with right:
                st.subheader("Metadata")
                st.write(f"**Timestamp:** {metadata['timestamp']}")
                st.write(f"**Device:** {metadata['device']}")
                st.write(f"**Location:** {metadata['location']}")
                st.write(f"**Caption:** {metadata['caption']}")
                st.write(f"**Tags:** {', '.join(metadata['tags'])}")

            st.subheader("Moderation Pipeline")

            steps = [
                "Authenticity Scan",
                "Duplicate Check",
                "AI Review",
                "Human Review",
                "Approved"
            ]

            def render_stepper(current_step_index):
                for i, step in enumerate(steps):
                    if i < current_step_index:
                        st.markdown(f"✅ **{step}**")
                    elif i == current_step_index:
                        st.markdown(f"🔄 **{step} (in progress...)**")
                    else:
                        st.markdown(f"⬜ {step}")

            for i in range(5):
                render_stepper(i)
                time.sleep(0.8)

            st.success("Moderation complete!")

            upload_id = data["id"]
            st.write("Checking moderation status...")
            time.sleep(1)

            status_response = requests.get(API_STATUS_URL + str(upload_id)).json()
            st.info(
                f"Current status: {status_response['status']} "
                f"(submitted {status_response['submitted']})"
            )

        else:
            st.error("Upload failed. Check backend logs.")

# -----------------------------------------
# 4. LIST ALL UPLOADS
# -----------------------------------------
section_header("All Uploads (Live from Backend)")

if st.button("Refresh Upload List"):
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    uploads = requests.get(API_LIST_URL, headers=headers).json()

    if len(uploads) == 0:
        st.write("No uploads yet.")
    else:
        for u in uploads:
            st.write(
                f"• ID {u['id']} — {u['filename']} — {u['status']} "
                f"(submitted {u['submitted']})"
            )
