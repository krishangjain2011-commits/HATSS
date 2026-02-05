import streamlit as st
import random
import time

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="AI Security Console", layout="wide")

# -----------------------------------
# STYLE — CLEAN PROFESSIONAL DASHBOARD
# -----------------------------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: #e5e7eb;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #1f2933;
}

/* Panel container */
.panel {
    background: #0f172a;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #1e293b;
}

/* Metric text */
.metric {
    font-size: 30px;
    font-weight: bold;
}

/* Accent colors */
.blue {color:#38bdf8;}
.green {color:#22c55e;}
.red {color:#ef4444;}
.yellow {color:#f59e0b;}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# STATE
# -----------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "known" not in st.session_state:
    st.session_state.known = 18

if "unknown" not in st.session_state:
    st.session_state.unknown = 5

# -----------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------
st.sidebar.title("AI Security")

st.session_state.page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Alert Center", "Memory Logs", "Settings"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("System Status:")
st.sidebar.markdown("<span class='green'>● ACTIVE</span>",
                    unsafe_allow_html=True)

# =================================================
# DASHBOARD
# =================================================
if st.session_state.page == "Dashboard":

    st.title("Live Security Dashboard")

    left, right = st.columns([2,1])

    # Camera Panel
    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("Camera Monitor")
        st.info("Live camera stream will appear here")
        st.markdown("</div>", unsafe_allow_html=True)

    # Metrics Panel
    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.subheader("System Metrics")

        st.markdown(
            f"<div class='metric blue'>{st.session_state.known}</div> Authorized Profiles",
            unsafe_allow_html=True)

        st.markdown(
            f"<div class='metric red'>{st.session_state.unknown}</div> Intrusion Records",
            unsafe_allow_html=True)

        st.markdown(
            f"<div class='metric yellow'>{random.randint(1,5)} sec</div> Last Scan",
            unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Control Panel
    st.subheader("Control Panel")

    if st.button("Run Detection Scan"):
        if random.choice([True, False]):
            st.session_state.page = "Alert Center"
            st.rerun()
        else:
            st.success("Authorized person detected")

# =================================================
# ALERT CENTER
# =================================================
elif st.session_state.page == "Alert Center":

    st.title("Security Alert")

    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    st.error("Unrecognized individual detected")

    col1, col2 = st.columns(2)

    with col1:
        st.warning("Captured image preview")

    with col2:
        score = round(random.uniform(0.30,0.55),2)
        st.write(f"Similarity Score: **{score}**")
        st.write("Threat Status: Review Required")

        st.divider()

        if st.button("Authorize Person"):
            st.session_state.known += 1
            st.success("Profile stored")
            time.sleep(1)
            st.session_state.page = "Dashboard"
            st.rerun()

        if st.button("Flag Intrusion"):
            st.session_state.unknown += 1
            st.warning("Intrusion recorded")
            time.sleep(1)
            st.session_state.page = "Dashboard"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# MEMORY LOGS
# =================================================
elif st.session_state.page == "Memory Logs":

    st.title("Recognition Logs")

    st.subheader("Authorized Profiles")

    cols = st.columns(6)
    for i in range(12):
        with cols[i % 6]:
            st.success("Known")

    st.divider()

    st.subheader("Intrusion Records")

    cols = st.columns(6)
    for i in range(8):
        with cols[i % 6]:
            st.error("Unknown")

# =================================================
# SETTINGS
# =================================================
elif st.session_state.page == "Settings":

    st.title("System Settings")

    st.slider("Recognition Sensitivity", 1, 10, 6)

    st.checkbox("Real-time Alerts", True)
    st.checkbox("Alarm Notification", True)

    if st.button("Clear Intrusion Logs"):
        st.session_state.unknown = 0
        st.success("Intrusion records cleared")
