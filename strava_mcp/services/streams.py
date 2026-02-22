"""Streams and laps services for Strava MCP Server."""

from typing import Literal, Optional
from stravalib.client import Client
from strava_mcp.models import LapSummary, ActivityStreams


def get_activity_laps(client: Client, activity_id: int) -> list[LapSummary]:
    """Get lap breakdowns for a specific activity."""
    laps = client.get_activity_laps(activity_id)

    result = []
    for lap in laps:
        moving_time = getattr(lap.moving_time, "seconds", 0) if lap.moving_time else 0
        elapsed_time = (
            getattr(lap.elapsed_time, "seconds", 0) if lap.elapsed_time else 0
        )

        summary = LapSummary(
            id=lap.id or 0,
            activity_id=getattr(lap, "activity_id", 0) or 0,
            lap_index=getattr(lap, "lap_index", 0),
            name=lap.name or "",
            elapsed_time=elapsed_time,
            moving_time=moving_time,
            distance=float(lap.distance) if lap.distance else 0.0,
            average_speed=float(lap.average_speed) if lap.average_speed else 0.0,
            max_speed=float(lap.max_speed) if lap.max_speed else 0.0,
            average_cadence=float(lap.average_cadence) if lap.average_cadence else None,
            average_watts=float(lap.average_watts) if lap.average_watts else None,
            average_heartrate=float(lap.average_heartrate)
            if lap.average_heartrate
            else None,
            max_heartrate=float(lap.max_heartrate) if lap.max_heartrate else None,
            total_elevation_gain=float(lap.total_elevation_gain)
            if lap.total_elevation_gain
            else 0.0,
        )
        result.append(summary)
    return result


def get_activity_streams(
    client: Client,
    activity_id: int,
    types: Optional[list[str]] = None,
    resolution: Optional[Literal["low", "medium", "high"]] = None,
) -> ActivityStreams:
    """Get raw stream data (GPS, HR, power, etc.) for a specific activity."""
    streams = client.get_activity_streams(
        activity_id, types=types, resolution=resolution
    )

    # Extract data from each stream type if available
    # Each stream is a Stream object with a .data attribute
    def get_stream_data(key: str) -> Optional[list]:
        if key in streams:
            stream = streams[key]
            return getattr(stream, "data", None)
        return None

    return ActivityStreams(
        time=get_stream_data("time"),
        latlng=get_stream_data("latlng"),
        distance=get_stream_data("distance"),
        altitude=get_stream_data("altitude"),
        velocity_smooth=get_stream_data("velocity_smooth"),
        heartrate=get_stream_data("heartrate"),
        cadence=get_stream_data("cadence"),
        watts=get_stream_data("watts"),
        temp=get_stream_data("temp"),
        moving=get_stream_data("moving"),
        grade_smooth=get_stream_data("grade_smooth"),
    )
