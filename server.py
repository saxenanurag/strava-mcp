import sys
import os
import time
from dataclasses import dataclass, asdict, field
from typing import Optional
from dotenv import load_dotenv
from fastmcp import FastMCP
from stravalib.client import Client

# Load environment variables from the directory containing this script
# This ensures .env is found even if the script is run from a different CWD
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))

# Configuration
# CLIENT_ID can be int or str in stravalib, but usually int.
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    sys.stderr.write(
        "Warning: STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, or STRAVA_REFRESH_TOKEN not set in environment.\n"
    )

# Initialize FastMCP
mcp = FastMCP("strava-server")

# Global state for token management
_client = Client()
_token_expires_at = 0


@dataclass
class ActivityTotals:
    """Represents activity totals (distance, time, etc.)."""

    distance: float = 0.0
    achievement_count: int = 0
    elevation_gain: float = 0.0


@dataclass
class AthleteStats:
    """Statistics for the authenticated athlete."""

    firstname: str = ""
    lastname: str = ""
    recent_run_totals: ActivityTotals = field(default_factory=ActivityTotals)
    all_run_totals: ActivityTotals = field(default_factory=ActivityTotals)
    recent_ride_totals: ActivityTotals = field(default_factory=ActivityTotals)

    def to_formatted_string(self) -> str:
        """Convert stats to formatted string for display."""
        return f"""
Athlete: {self.firstname} {self.lastname}
Recent Run Totals:
  Distance: {self.recent_run_totals.distance}
  Achievement Count: {self.recent_run_totals.achievement_count}
All-Time Run Totals:
  Distance: {self.all_run_totals.distance}
Recent Ride Totals:
  Distance: {self.recent_ride_totals.distance}
  Elevation Gain: {self.recent_ride_totals.elevation_gain}
"""


@dataclass
class ActivitySummary:
    """Summary of a Strava activity."""

    id: int
    name: str
    type: str
    start_date: Optional[str]
    distance: float
    moving_time: int
    total_elevation_gain: float

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class ActivityDetails:
    """Detailed information about a Strava activity."""

    id: int
    name: str
    description: Optional[str]
    type: str
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    average_speed: float
    max_speed: float
    calories: Optional[float]
    device_name: Optional[str]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


def get_client() -> Client:
    """
    Returns an authenticated Strava client, refreshing the access token if necessary.
    """
    global _client, _token_expires_at

    # Buffer time to refresh before actual expiration (e.g., 5 minutes)
    if time.time() > _token_expires_at - 300:
        try:
            sys.stderr.write("Refreshing Strava access token...\n")
            # Ensure CLIENT_ID is correctly typed if needed, though stravalib handles str often
            response = _client.refresh_access_token(
                client_id=int(CLIENT_ID)
                if CLIENT_ID and CLIENT_ID.isdigit()
                else CLIENT_ID,  # type: ignore
                client_secret=CLIENT_SECRET,  # type: ignore
                refresh_token=REFRESH_TOKEN,  # type: ignore
            )
            _client.access_token = response["access_token"]
            _client.refresh_token = response["refresh_token"]
            _token_expires_at = response["expires_at"]
            sys.stderr.write("Token refreshed successfully.\n")
        except Exception as e:
            # Log full error to stderr for debugging
            sys.stderr.write(f"Auth Error: {e}\n")
            # Return generic error to client to avoid leaking secrets
            raise RuntimeError("Failed to authenticate with Strava. Check server logs.")

    return _client


@mcp.tool()
def get_athlete_stats() -> str:
    """
    Get statistics for the authenticated athlete.
    Returns a formatted string with recent and all-time stats.
    """
    client = get_client()
    stats = _get_athlete_stats(client)
    return stats.to_formatted_string()


def _get_athlete_stats(client: Client) -> AthleteStats:
    athlete = client.get_athlete()
    stats = client.get_athlete_stats(athlete.id)

    def get_val(obj, attr, default=None):
        val = getattr(obj, attr, default) if obj else default
        if val is None:
            return default
        return val

    recent_run = stats.recent_run_totals
    all_run = stats.all_run_totals
    recent_ride = stats.recent_ride_totals

    return AthleteStats(
        firstname=getattr(athlete, "firstname", ""),
        lastname=getattr(athlete, "lastname", ""),
        recent_run_totals=ActivityTotals(
            distance=float(get_val(recent_run, "distance", 0.0)),
            achievement_count=int(get_val(recent_run, "achievement_count", 0)),
        ),
        all_run_totals=ActivityTotals(
            distance=float(get_val(all_run, "distance", 0.0)),
        ),
        recent_ride_totals=ActivityTotals(
            distance=float(get_val(recent_ride, "distance", 0.0)),
            elevation_gain=float(get_val(recent_ride, "elevation_gain", 0.0)),
        ),
    )


@mcp.tool()
def list_activities(limit: int = 5) -> list[dict]:
    """
    List recent activities for the authenticated athlete.

    Args:
        limit: Number of activities to return (default 5)
    """
    client = get_client()
    activities = _list_activities(client, limit)
    return [activity.to_dict() for activity in activities]


def _list_activities(client: Client, limit: int) -> list[ActivitySummary]:
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


@mcp.tool()
def get_activity_details(activity_id: int) -> dict:
    """
    Get detailed information for a specific activity.

    Args:
        activity_id: The ID of the activity to retrieve
    """
    client = get_client()
    details = _get_activity_details(client, activity_id)
    return details.to_dict()


def _get_activity_details(client: Client, activity_id: int) -> ActivityDetails:
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


if __name__ == "__main__":
    mcp.run()
