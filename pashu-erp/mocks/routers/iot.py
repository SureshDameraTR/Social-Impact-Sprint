"""IoT Gateway mock router.

Provides device listing, detail, latest telemetry, and historical
time-series endpoints with deterministic pseudo-random generation.
"""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/iot", tags=["IoT"])

# ---------------------------------------------------------------------------
# Load sample devices once at import time
# ---------------------------------------------------------------------------
_DATA_DIR = Path(__file__).parent.parent / "data"
_DEVICES: list = json.loads((_DATA_DIR / "sample_devices.json").read_text())
_DEVICE_MAP: dict = {d["device_id"]: d for d in _DEVICES}

# IST offset
_IST = timezone(timedelta(hours=5, minutes=30))


# ---------------------------------------------------------------------------
# Deterministic helpers
# ---------------------------------------------------------------------------

def _seed_float(seed_str: str) -> float:
    """Return a deterministic float in [0, 1) from a string seed."""
    h = hashlib.sha256(seed_str.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _seeded_range(seed_str: str, lo: float, hi: float) -> float:
    """Return a deterministic float in [lo, hi) from a string seed."""
    return lo + _seed_float(seed_str) * (hi - lo)


def _generate_metrics(device: dict, ts_iso: str, seed_prefix: str) -> list:
    """Generate a full set of metrics for one timestamp."""
    seed = f"{seed_prefix}:{device['device_id']}:{ts_iso}"

    # Determine anomaly flags
    fever = _seed_float(f"fever:{seed}") < 0.05
    # Estrus: ~2% chance per slot for demo realism
    estrus = _seed_float(f"estrus:{seed}") < 0.02

    # Body temperature
    if fever:
        temp = round(_seeded_range(f"temp:{seed}", 39.5, 40.5), 1)
    else:
        temp = round(_seeded_range(f"temp:{seed}", 38.0, 39.0), 1)

    # Activity index
    if estrus:
        activity = round(_seeded_range(f"act:{seed}", 300, 400))
    else:
        activity = round(_seeded_range(f"act:{seed}", 80, 200))

    # Rumination — low when fever
    if fever:
        rumination = round(_seeded_range(f"rum:{seed}", 15, 25))
    else:
        rumination = round(_seeded_range(f"rum:{seed}", 40, 60))

    # GPS — small jitter around device's base location
    lat_jitter = _seeded_range(f"lat:{seed}", -0.002, 0.002)
    lng_jitter = _seeded_range(f"lng:{seed}", -0.002, 0.002)
    lat = round(device["lat"] + lat_jitter, 5)
    lng = round(device["lng"] + lng_jitter, 5)

    return [
        {"type": "body_temperature", "value": temp, "unit": "\u00b0C"},
        {"type": "activity_index", "value": activity, "unit": "steps/hr"},
        {"type": "rumination", "value": rumination, "unit": "min/hr"},
        {"type": "gps", "value": {"lat": lat, "lng": lng}, "unit": "coords"},
    ]


def _telemetry_point(device: dict, ts: datetime, seed_prefix: str = "telem") -> dict:
    """Build a single telemetry payload for a device at a given timestamp."""
    ts_iso = ts.isoformat()
    metrics = _generate_metrics(device, ts_iso, seed_prefix)
    battery_drain = _seeded_range(f"bat:{seed_prefix}:{device['device_id']}:{ts_iso}", 0, 3)
    battery = max(0, round(device["battery_pct"] - battery_drain))
    rssi = round(_seeded_range(f"rssi:{seed_prefix}:{device['device_id']}:{ts_iso}", -85, -55))

    return {
        "device_id": device["device_id"],
        "animal_id": device["animal_id"],
        "timestamp": ts_iso,
        "metrics": metrics,
        "battery_pct": battery,
        "rssi": rssi,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/devices")
async def list_devices(
    status: Optional[str] = Query(None, description="Filter by status: active | inactive"),
    type: Optional[str] = Query(None, description="Filter by device type"),
):
    """List all IoT devices with optional filters."""
    results = _DEVICES
    if status:
        results = [d for d in results if d["status"] == status]
    if type:
        results = [d for d in results if d["type"] == type]
    return {"data": results, "total": len(results)}


@router.get("/devices/{device_id}")
async def get_device(device_id: str):
    """Get a single device's details."""
    device = _DEVICE_MAP.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    now = datetime.now(_IST)
    # Deterministic last_seen: within the last 5 minutes for active devices
    if device["status"] == "active":
        offset_sec = round(_seeded_range(f"lastseen:{device_id}:{now.strftime('%Y%m%d%H')}", 30, 300))
        last_seen = (now - timedelta(seconds=offset_sec)).isoformat()
    else:
        # Inactive devices: last seen days ago
        offset_days = round(_seeded_range(f"lastseen:{device_id}", 2, 14))
        last_seen = (now - timedelta(days=offset_days)).isoformat()

    return {
        **device,
        "last_seen": last_seen,
        "firmware_version": device["firmware"],
        "assigned_animal_id": device["animal_id"],
    }


@router.get("/devices/{device_id}/latest")
async def latest_telemetry(device_id: str):
    """Get the latest telemetry reading for a device."""
    device = _DEVICE_MAP.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    now = datetime.now(_IST)
    # Snap to most recent 15-min boundary for determinism within the same quarter-hour
    snapped = now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0)
    return _telemetry_point(device, snapped, seed_prefix="latest")


@router.get("/telemetry")
async def historical_telemetry(
    device_id: str = Query(..., description="Device ID (required)"),
    metric: Optional[str] = Query(None, description="Filter to a single metric type"),
    from_ts: Optional[str] = Query(None, description="Start ISO datetime"),
    to_ts: Optional[str] = Query(None, description="End ISO datetime"),
    interval_minutes: int = Query(15, description="Interval between readings in minutes"),
):
    """Historical telemetry time-series for a device."""
    device = _DEVICE_MAP.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    now = datetime.now(_IST)

    # Parse time range — default to last 24 hours
    if from_ts:
        start = datetime.fromisoformat(from_ts)
        if start.tzinfo is None:
            start = start.replace(tzinfo=_IST)
    else:
        start = now - timedelta(hours=24)

    if to_ts:
        end = datetime.fromisoformat(to_ts)
        if end.tzinfo is None:
            end = end.replace(tzinfo=_IST)
    else:
        end = now

    # Cap to 7 days max to avoid huge payloads
    if (end - start).total_seconds() > 7 * 86400:
        start = end - timedelta(days=7)

    interval = timedelta(minutes=max(1, interval_minutes))
    data = []
    current = start
    while current <= end:
        point = _telemetry_point(device, current, seed_prefix="hist")

        # If metric filter is set, keep only matching metrics
        if metric:
            point["metrics"] = [m for m in point["metrics"] if m["type"] == metric]

        data.append(point)
        current += interval

    return {
        "data": data,
        "total": len(data),
        "device_id": device_id,
        "from": start.isoformat(),
        "to": end.isoformat(),
    }
