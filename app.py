import streamlit as st
import random
import time

# ---------------------------------------------------
# PAGE CONFIG + SECURITY THEME
# ---------------------------------------------------
st.set_page_config(
    page_title="Home Security System",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.main-title {
    font-size: 32px;
    font-weight: bold;
    color: #e5e7eb;
}
.card {
    background-color: #1f2933;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #334155;
}
.status-green {
    color: #22c55e;
    font-weight: bold;
}
.status-red {
    color: #ef4444;
    font-weight: bold;
}
.metric {
    font-size: 20px;
    font-weight: bold;
}
.alert-box {
    background-color: #3b0a0a;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ef4444;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "known" not in st.session_state:
    st.session_state.known = 18

if "unknown" not in st.session_state:
    st.session_state.unknown = 5

if "intrusion" not in st.session_state:
    st.session_state.intrusion = False

# ---------------------------------------------------
# SIDEBAR NAV
# ---------------------------------------------------
st.sidebar.title("🔐 Security Panel")

st.session_state.page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Alert Center", "Memory Logs", "System Settings"]
)

st.sidebar.markdown("---")
st.sidebar.write("System Status:")
st.sidebar.markdown('<span class="status-green">● ACTIVE</span>',
                    unsafe_allow_html=True)

# ===================================================
# DASHBOARD
# ===================================================
if st.session_state.page == "Dashboard":

    st.markdown('<div class="main-title">🏠 Live Security Dashboard</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    # Live feed card
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Live Camera Monitor")
        st.image(
            "https://via.placeholder.com/900x450?text=LIVE+FEED",
            use_column_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Metrics panel
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("System Metrics")

        st.metric("Known Profiles", st.session_state.known)
        st.metric("Unknown Records", st.session_state.unknown)
        st.metric("Last Scan", f"{random.randint(1,5)} sec")

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    if st.button("🔍 Simulate Detection Event"):
        st.session_state.intrusion = random.choice([True, False])

        if st.session_state.intrusion:
            st.session_state.page = "Alert Center"
            st.rerun()
        else:
            st.toast("Authorized individual detected", icon="✅")

# ===================================================
# ALERT CENTER
# ===================================================
elif st.session_state.page == "Alert Center":

    st.markdown('<div class="main-title">🚨 Intrusion Alert Center</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="alert-box">', unsafe_allow_html=True)

    st.error("UNAUTHORIZED PRESENCE DETECTED")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(
            "https://via.placeholder.com/400?text=Captured+Face",
            caption="Captured Snapshot"
        )

    with col2:
        similarity = round(random.uniform(0.32, 0.55), 2)

        st.write(f"**Similarity Score:** {similarity}")
        st.write("**Risk Level:** HIGH 🔴")
        st.write("**Timestamp:** Just now")

        st.divider()

        approve = st.button("✅ Approve Access")
        reject = st.button("❌ Mark as Intruder")

        if approve:
            st.session_state.known += 1
            st.success("Profile added to authorized memory")
            time.sleep(1)
            st.session_state.page = "Dashboard"
            st.rerun()

        if reject:
            st.session_state.unknown += 1
            st.warning("Intruder recorded")
            time.sleep(1)
            st.session_state.page = "Dashboard"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =============================================
