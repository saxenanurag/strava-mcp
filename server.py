"""Strava MCP Server - Main entry point.

A Model Context Protocol (MCP) server that connects to the Strava API.
"""

from typing import Literal, Optional
from fastmcp import FastMCP

from strava_mcp.auth import get_client
from strava_mcp.services.athlete import get_athlete_stats
from strava_mcp.services.activities import (
    list_activities,
    search_activities,
    get_activity_details,
)
from strava_mcp.services.streams import get_activity_laps, get_activity_streams

# Initialize FastMCP
mcp = FastMCP("strava-server")


@mcp.tool()
def get_athlete_stats_tool() -> str:
    """
    Get statistics for the authenticated athlete.
    Returns a formatted string with recent and all-time stats.
    """
    client = get_client()
    stats = get_athlete_stats(client)
    return stats.to_formatted_string()


@mcp.tool()
def list_activities_tool(limit: int = 5) -> list[dict]:
    """
    List recent activities for the authenticated athlete.

    Args:
        limit: Number of activities to return (default 5)
    """
    client = get_client()
    activities = list_activities(client, limit)
    return [activity.to_dict() for activity in activities]


@mcp.tool()
def search_activities_tool(
    query: Optional[str] = None,
    activity_type: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    min_distance: Optional[float] = None,
    max_distance: Optional[float] = None,
    limit: int = 50,
) -> list[dict]:
    """
    Search activities with optional filters.
    Note: Name/description search is client-side, so a reasonable limit is recommended.

    Args:
        query: Search term to match in activity name (case-insensitive, partial match)
        activity_type: Filter by activity type (e.g., "Run", "Ride", "Walk", "Hike")
        after: ISO 8601 date string (e.g., "2025-01-01") - activities after this date
        before: ISO 8601 date string (e.g., "2026-01-01") - activities before this date
        min_distance: Minimum distance in meters
        max_distance: Maximum distance in meters
        limit: Maximum number of activities to fetch from API (default 50)
    """
    client = get_client()
    activities = search_activities(
        client,
        query=query,
        activity_type=activity_type,
        after=after,
        before=before,
        min_distance=min_distance,
        max_distance=max_distance,
        limit=limit,
    )
    return [activity.to_dict() for activity in activities]


@mcp.tool()
def get_activity_details_tool(activity_id: int) -> dict:
    """
    Get detailed information for a specific activity.

    Args:
        activity_id: The ID of the activity to retrieve
    """
    client = get_client()
    details = get_activity_details(client, activity_id)
    return details.to_dict()


@mcp.tool()
def get_activity_laps_tool(activity_id: int) -> list[dict]:
    """
    Get lap breakdowns for a specific activity.

    Args:
        activity_id: The ID of the activity to retrieve laps for
    """
    client = get_client()
    laps = get_activity_laps(client, activity_id)
    return [lap.to_dict() for lap in laps]


@mcp.tool()
def get_activity_streams_tool(
    activity_id: int,
    types: Optional[list[str]] = None,
    resolution: Optional[Literal["low", "medium", "high"]] = None,
) -> dict:
    """
    Get raw stream data (GPS, HR, power, etc.) for a specific activity.

    Args:
        activity_id: The ID of the activity to retrieve streams for
        types: List of stream types to fetch. Options: time, latlng, distance, altitude,
               velocity_smooth, heartrate, cadence, watts, temp, moving, grade_smooth.
               If None, all available streams will be returned.
        resolution: Data point resolution - 'low' (100 points), 'medium' (1000 points),
                   'high' (10000 points), or None (all points)
    """
    client = get_client()
    streams = get_activity_streams(client, activity_id, types, resolution)
    return streams.to_dict()


if __name__ == "__main__":
    mcp.run()
