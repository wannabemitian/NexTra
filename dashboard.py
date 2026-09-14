import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Traffic AI Monitor",
    page_icon="🚦",
    layout="wide",
)


# ---------------------------------------------------------
# API helper
# ---------------------------------------------------------

def get_api_data(endpoint):
    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=3,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🚦 Traffic AI Monitor")
st.caption(
    "Two-camera traffic analysis and bottleneck "
    "decision-support system"
)

st.divider()


# ---------------------------------------------------------
# Get backend data
# ---------------------------------------------------------

status_data = get_api_data("/api/status")


if status_data is None:
    st.error(
        "Backend API is not running. "
        "Start the FastAPI server first."
    )
    st.stop()


cameras = status_data.get("cameras", [])
traffic = status_data.get("traffic", {})


# ---------------------------------------------------------
# Camera information
# ---------------------------------------------------------

st.subheader("Camera Network")

camera_a = next(
    (camera for camera in cameras if camera["camera"] == "Camera_A"),
    None,
)

camera_b = next(
    (camera for camera in cameras if camera["camera"] == "Camera_B"),
    None,
)

col1, col2 = st.columns(2)


with col1:
    st.markdown("### Camera A")

    if camera_a:
        st.metric(
            "Vehicles observed",
            camera_a["vehicles_observed"],
        )

        st.write(
            f"Status: **{camera_a['status']}**"
        )

        st.write(
            f"Tracking observations: "
            f"**{camera_a['observations']}**"
        )


with col2:
    st.markdown("### Camera B")

    if camera_b:
        st.metric(
            "Vehicles observed",
            camera_b["vehicles_observed"],
        )

        st.write(
            f"Status: **{camera_b['status']}**"
        )

        st.write(
            f"Tracking observations: "
            f"**{camera_b['observations']}**"
        )


st.divider()


# ---------------------------------------------------------
# Traffic status
# ---------------------------------------------------------

st.subheader("Traffic Assessment")

status = traffic.get(
    "status",
    "UNKNOWN",
)

reason = traffic.get(
    "reason",
    "No explanation available.",
)

if status == "WAITING FOR DATA":
    st.warning(f"⏳ {status}")

elif status == "MONITORING":
    st.info(f"🟢 {status}")

else:
    st.warning(f"⚠️ {status}")


st.write(reason)


# ---------------------------------------------------------
# Recommendation
# ---------------------------------------------------------

recommendation_data = get_api_data(
    "/api/recommendation"
)

st.subheader("Traffic Officer Recommendation")

if recommendation_data:
    st.info(
        recommendation_data.get(
            "recommendation",
            "No recommendation available.",
        )
    )


# ---------------------------------------------------------
# System architecture
# ---------------------------------------------------------

st.divider()

st.subheader("System Flow")

st.code(
    """
Camera A ──┐
           │
           ├──► Vehicle Detection & Tracking
           │
Camera B ──┘
                    │
                    ▼
             Trajectory Analysis
                    │
                    ▼
             Traffic Assessment
                    │
                    ▼
             Bottleneck Risk
                    │
                    ▼
          Officer Recommendation
    """,
    language="text",
)


# ---------------------------------------------------------
# API information
# ---------------------------------------------------------

with st.expander("API / System Information"):
    st.write(
        "Frontend: Streamlit"
    )
    st.write(
        "Backend: FastAPI"
    )
    st.write(
        "Analysis: Python + vehicle tracking data"
    )
    st.write(
        "API endpoint: http://127.0.0.1:8000"
    )