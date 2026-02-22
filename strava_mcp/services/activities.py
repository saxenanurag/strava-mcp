"""Activity-related services for Strava MCP Server."""

import sys
import datetime
from typing import Optional
from stravalib.client import Client
from strava_mcp.models import ActivitySummary, ActivityDetails


def list_activities(client: Client, limit: int) -> list[ActivitySummary]:
    """List recent activities for the authenticated athlete."""
    activities = client.get_activities(limit=limit)

    result = []
    for activity in activities:
        # Handle moving_time safely
        moving_time = (
            getattr(activity.moving_time, "seconds", 0) if activity.moving_time else 0
        )

        summary = ActivitySummary(
            id=activity.id or 0,
            name=activity.name or "",
            type=str(activity.type),
            start_date=activity.start_date.isoformat() if activity.start_date else None,
            distance=float(activity.distance) if activity.distance else 0.0,
            moving_time=moving_time,
            total_elevation_gain=float(activity.total_elevation_gain)
            if activity.total_elevation_gain
            else 0.0,
        )
        result.append(summary)
    return result


def search_activities(
    client: Client,
    query: Optional[str] = None,
    activity_type: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    min_distance: Optional[float] = None,
    max_distance: Optional[float] = None,
    limit: int = 50,
) -> list[ActivitySummary]:
    """Search activities with optional filters."""
    # Parse date strings if provided
    after_date = None
    before_date = None

    if after:
        try:
            after_date = datetime.datetime.fromisoformat(after.replace("Z", "+00:00"))
        except ValueError:
            sys.stderr.write(f"Warning: Invalid 'after' date format: {after}\n")

    if before:
        try:
            before_date = datetime.datetime.fromisoformat(before.replace("Z", "+00:00"))
        except ValueError:
            sys.stderr.write(f"Warning: Invalid 'before' date format: {before}\n")

    # Fetch activities with date filters
    activities = client.get_activities(
        before=before_date, after=after_date, limit=limit
    )

    result = []
    query_lower = query.lower() if query else None
    type_lower = activity_type.lower() if activity_type else None

    for activity in activities:
        # Handle moving_time safely
        moving_time = (
            getattr(activity.moving_time, "seconds", 0) if activity.moving_time else 0
        )

        # Get activity details
        activity_name = activity.name or ""
        activity_type_str = str(activity.type)
        activity_distance = float(activity.distance) if activity.distance else 0.0

        # Apply filters
        if query_lower and query_lower not in activity_name.lower():
            continue

        if type_lower and type_lower not in activity_type_str.lower():
            continue

        if min_distance is not None and activity_distance < min_distance:
            continue

        if max_distance is not None and activity_distance > max_distance:
            continue

        summary = ActivitySummary(
            id=activity.id or 0,
            name=activity_name,
            type=activity_type_str,
            start_date=activity.start_date.isoformat() if activity.start_date else None,
            distance=activity_distance,
            moving_time=moving_time,
            total_elevation_gain=float(activity.total_elevation_gain)
            if activity.total_elevation_gain
            else 0.0,
        )
        result.append(summary)

    return result


def get_activity_details(client: Client, activity_id: int) -> ActivityDetails:
    """Get detailed information for a specific activity."""
    activity = client.get_activity(activity_id)

    moving_time = (
        getattr(activity.moving_time, "seconds", 0) if activity.moving_time else 0
    )
    elapsed_time = (
        getattr(activity.elapsed_time, "seconds", 0) if activity.elapsed_time else 0
    )

    return ActivityDetails(
        id=activity.id or 0,
        name=activity.name or "",
        description=activity.description,
        type=str(activity.type),
        distance=float(activity.distance) if activity.distance else 0.0,
        moving_time=moving_time,
        elapsed_time=elapsed_time,
        total_elevation_gain=float(activity.total_elevation_gain)
        if activity.total_elevation_gain
        else 0.0,
        average_speed=float(activity.average_speed) if activity.average_speed else 0.0,
        max_speed=float(activity.max_speed) if activity.max_speed else 0.0,
        calories=activity.calories,
        device_name=activity.device_name,
    )
