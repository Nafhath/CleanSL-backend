from datetime import datetime, timezone
from typing import Any

from app.core.supabase_client import supabase


def _safe_execute(builder):
    try:
        return builder.execute().data or []
    except Exception:
        return []


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value

    if not value:
        return datetime.fromtimestamp(0, tz=timezone.utc)

    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return datetime.fromtimestamp(0, tz=timezone.utc)


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_lat_lng(row: dict[str, Any]) -> tuple[float | None, float | None]:
    lat = _parse_float(row.get("lat") or row.get("latitude") or row.get("truck_lat") or row.get("current_lat"))
    lng = _parse_float(row.get("lng") or row.get("longitude") or row.get("truck_lng") or row.get("current_lng"))
    return lat, lng


def _extract_updated_at(row: dict[str, Any]) -> datetime:
    return _parse_timestamp(row.get("updated_at") or row.get("timestamp") or row.get("created_at"))


def _extract_speed(row: dict[str, Any]) -> float | None:
    return _parse_float(row.get("speed") or row.get("speed_kmh") or row.get("speed_km_h"))


def _format_truck_code(driver_id: str, explicit_code: Any = None) -> str:
    if explicit_code:
        return str(explicit_code)

    token = "".join(ch for ch in driver_id if ch.isalnum()).upper()
    if not token:
        return "TRK-001"
    return f"TRK-{token[:4]}"


def _load_tracking_rows() -> list[dict[str, Any]]:
    for table_name, order_field in (("driver_locations", "updated_at"), ("driver_tracking", "timestamp")):
        rows = _safe_execute(
            supabase.table(table_name).select("*").order(order_field, desc=True).limit(500)
        )
        if rows:
            return rows
    return []


def list_truck_dashboard_data():
    driver_rows = _safe_execute(supabase.table("users").select("*").eq("role", "driver"))
    profile_rows = _safe_execute(supabase.table("driver_profiles").select("*"))
    tracking_rows = _load_tracking_rows()
    task_rows = _safe_execute(supabase.table("collection_tasks").select("id,driver_id,address_id,status"))
    address_rows = _safe_execute(supabase.table("addresses").select("id,street_address,zone_or_ward"))

    if not tracking_rows and not task_rows and not driver_rows:
        return {"activeTruck": None, "wards": []}

    drivers_by_id = {str(row.get("id")): row for row in driver_rows if row.get("id")}
    profiles_by_driver_id = {str(row.get("user_id")): row for row in profile_rows if row.get("user_id")}
    addresses_by_id = {str(row.get("id")): row for row in address_rows if row.get("id")}

    tracking_by_driver: dict[str, list[dict[str, Any]]] = {}
    for raw in tracking_rows:
        driver_id = raw.get("driver_id") or raw.get("user_id")
        if not driver_id:
            continue

        lat, lng = _extract_lat_lng(raw)
        if lat is None or lng is None:
            continue

        tracking_by_driver.setdefault(str(driver_id), []).append(raw)

    for driver_id in tracking_by_driver:
        tracking_by_driver[driver_id].sort(key=_extract_updated_at, reverse=True)

    ward_state: dict[str, dict[str, Any]] = {}
    for task in task_rows:
        address = addresses_by_id.get(str(task.get("address_id")))
        ward_name = (address or {}).get("zone_or_ward") or "Unassigned Ward"
        bucket = ward_state.setdefault(
            ward_name,
            {"name": ward_name, "total": 0, "completed": 0, "trucks": set()},
        )
        bucket["total"] += 1
        if task.get("status") == "completed":
            bucket["completed"] += 1

        driver_id = task.get("driver_id")
        if driver_id:
            profile = profiles_by_driver_id.get(str(driver_id), {})
            bucket["trucks"].add(_format_truck_code(str(driver_id), profile.get("assigned_truck_id")))

    if not ward_state:
        for driver_id in tracking_by_driver.keys():
            profile = profiles_by_driver_id.get(driver_id, {})
            driver = drivers_by_id.get(driver_id, {})
            ward_name = profile.get("assigned_ward") or driver.get("location") or "Live Operations"
            bucket = ward_state.setdefault(
                ward_name,
                {"name": ward_name, "total": 1, "completed": 0, "trucks": set()},
            )
            bucket["trucks"].add(_format_truck_code(driver_id, profile.get("assigned_truck_id")))

    wards = []
    for index, item in enumerate(ward_state.values(), start=1):
        total = item["total"] or 1
        completed = item["completed"]
        progress = int(round((completed / total) * 100))
        wards.append(
            {
                "id": index,
                "name": item["name"],
                "progress": progress,
                "status": "Completed" if progress >= 100 else "In Progress",
                "trucks": sorted(item["trucks"]) or [f"T-{index:02d}"],
            }
        )

    preferred_driver_id = None
    for driver_id, profile in profiles_by_driver_id.items():
        if profile.get("status") == "on_duty" and tracking_by_driver.get(driver_id):
            preferred_driver_id = driver_id
            break
    if preferred_driver_id is None and tracking_by_driver:
        preferred_driver_id = next(iter(tracking_by_driver))

    if preferred_driver_id is None:
        return {"activeTruck": None, "wards": wards}

    profile = profiles_by_driver_id.get(preferred_driver_id, {})
    driver = drivers_by_id.get(preferred_driver_id, {})
    history = tracking_by_driver.get(preferred_driver_id, [])
    latest = history[0]
    latest_lat, latest_lng = _extract_lat_lng(latest)
    speed = _extract_speed(latest)

    route = []
    for row in reversed(history[:20]):
        lat, lng = _extract_lat_lng(row)
        if lat is not None and lng is not None:
            route.append([lat, lng])

    if not route and latest_lat is not None and latest_lng is not None:
        route = [[latest_lat, latest_lng]]

    location_label = (
        latest.get("location_name")
        or latest.get("area_name")
        or latest.get("address")
        or driver.get("location")
        or f"{latest_lat:.5f}, {latest_lng:.5f}"
    )
    if speed is not None:
        location_label = f"{location_label} ({int(round(speed))} km/h)"

    return {
        "activeTruck": {
            "id": _format_truck_code(preferred_driver_id, profile.get("assigned_truck_id")),
            "driverId": preferred_driver_id,
            "driverName": driver.get("full_name") or driver.get("name") or "Driver",
            "location": location_label,
            "route": route,
        },
        "wards": wards,
    }


def create_truck_location_update(truck_id: str, payload: dict[str, Any]):
    lat = _parse_float(payload.get("latitude"))
    lng = _parse_float(payload.get("longitude"))
    if lat is None or lng is None:
        raise ValueError("latitude and longitude are required")

    record = {
        "driver_id": payload.get("driver_id") or truck_id,
        "lat": lat,
        "lng": lng,
        "speed": _parse_float(payload.get("speed")) or 0,
        "location_name": payload.get("location_name") or f"{lat:.5f}, {lng:.5f}",
        "updated_at": payload.get("updated_at") or datetime.now(timezone.utc).isoformat(),
    }

    return supabase.table("driver_locations").insert(record).execute().data[0]
