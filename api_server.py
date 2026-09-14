from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

CAMERAS = {
    "Camera_A": "Camera_A_tracking.csv",
    "Camera_B": "Camera_B_tracking.csv",
}

app = FastAPI(
    title="Traffic AI Monitoring API",
    description="Backend API for the two-camera traffic analysis system.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Data loading
# ---------------------------------------------------------

def load_camera_data(camera_name):
    """Load tracking data for a camera if its CSV exists."""

    filename = CAMERAS.get(camera_name)

    if filename is None:
        return None

    file_path = BASE_DIR / filename

    if not file_path.exists():
        return None

    try:
        data = pd.read_csv(file_path)
    except Exception:
        return None

    return data


def get_camera_summary(camera_name):
    """Return useful summary information for one camera."""

    data = load_camera_data(camera_name)

    if data is None:
        return {
            "camera": camera_name,
            "status": "NO_DATA",
            "vehicles_observed": 0,
            "observations": 0,
        }

    if data.empty:
        return {
            "camera": camera_name,
            "status": "NO_DETECTIONS",
            "vehicles_observed": 0,
            "observations": 0,
        }

    vehicle_count = 0

    if "vehicle_id" in data.columns:
        vehicle_count = int(data["vehicle_id"].nunique())

    return {
        "camera": camera_name,
        "status": "ACTIVE",
        "vehicles_observed": vehicle_count,
        "observations": int(len(data)),
    }


# ---------------------------------------------------------
# Traffic analysis
# ---------------------------------------------------------

def calculate_traffic_status(camera_summaries):
    """
    Prototype traffic-risk assessment.

    This deliberately does not invent traffic measurements.
    It only evaluates information that actually exists.
    """

    active_cameras = [
        camera
        for camera in camera_summaries
        if camera["status"] == "ACTIVE"
    ]

    if not active_cameras:
        return {
            "status": "WAITING FOR DATA",
            "risk_score": None,
            "reason": "No camera tracking data is currently available.",
        }

    total_vehicles = sum(
        camera["vehicles_observed"]
        for camera in active_cameras
    )

    return {
        "status": "MONITORING",
        "risk_score": None,
        "reason": (
            f"{total_vehicles} unique vehicles observed "
            "across the available camera data."
        ),
    }


# ---------------------------------------------------------
# API routes
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "system": "Traffic AI Monitoring System",
        "status": "online",
    }


@app.get("/api/cameras")
def cameras():
    return {
        "cameras": [
            get_camera_summary("Camera_A"),
            get_camera_summary("Camera_B"),
        ]
    }


@app.get("/api/status")
def status():
    camera_summaries = [
        get_camera_summary("Camera_A"),
        get_camera_summary("Camera_B"),
    ]

    traffic = calculate_traffic_status(camera_summaries)

    return {
        "system": "Traffic AI Monitoring System",
        "traffic": traffic,
        "cameras": camera_summaries,
    }


@app.get("/api/traffic")
def traffic():
    camera_summaries = [
        get_camera_summary("Camera_A"),
        get_camera_summary("Camera_B"),
    ]

    return calculate_traffic_status(camera_summaries)


@app.get("/api/recommendation")
def recommendation():
    camera_summaries = [
        get_camera_summary("Camera_A"),
        get_camera_summary("Camera_B"),
    ]

    traffic = calculate_traffic_status(camera_summaries)

    if traffic["status"] == "WAITING FOR DATA":
        message = (
            "Continue monitoring. "
            "A recommendation will be generated when traffic data is available."
        )
    else:
        message = (
            "Continue monitoring vehicle movement. "
            "Potential bottleneck analysis will use trajectory and "
            "movement data from both cameras."
        )

    return {
        "status": traffic["status"],
        "recommendation": message,
    }