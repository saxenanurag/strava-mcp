from fastmcp import FastMCP
from stravalib.client import Client
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print(
        "Warning: STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, or STRAVA_REFRESH_TOKEN not set in environment."
    )

# Initialize FastMCP
mcp = FastMCP("strava-server")

# Global state for token management
_client = Client()
_token_expires_at = 0


def get_client() -> Client:
    """
    Returns an authenticated Strava client, refreshing the access token if necessary.
    """
    global _client, _token_expires_at

    # Buffer time to refresh before actual expiration (e.g., 5 minutes)
    if time.time() > _token_expires_at - 300:
        try:
            print("Refreshing Strava access token...")
            response = _client.refresh_access_token(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                refresh_token=REFRESH_TOKEN,
            )
            _client.access_token = response["access_token"]
            _client.refresh_token = response["refresh_token"]
            _token_expires_at = response["expires_at"]
            print("Token refreshed successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with Strava: {str(e)}")

    return _client


@mcp.tool()
def get_athlete_stats() -> str:
    """
    Get statistics for the authenticated athlete.
    Returns a formatted string with recent and all-time stats.
    """
    client = get_client()
    athlete = client.get_athlete()
    stats = client.get_athlete_stats(athlete.id)

    return f"""
Athlete: {athlete.firstname} {athlete.lastname}
Recent Run Totals:
  Distance: {stats.recent_run_totals.distance}
  Achievement Count: {stats.recent_run_totals.achievement_count}
All-Time Run Totals:
  Distance: {stats.all_run_totals.distance}
Recent Ride Totals:
  Distance: {stats.recent_ride_totals.distance}
  Elevation Gain: {stats.recent_ride_totals.elevation_gain}
"""


@mcp.tool()
def list_activities(limit: int = 5) -> list[dict]:
    """
    List recent activities for the authenticated athlete.

    Args:
        limit: Number of activities to return (default 5)
    """
    client = get_client()
    activities = client.get_activities(limit=limit)

    result = []
    for activity in activities:
        result.append(
            {
                "id": activity.id,
                "name": activity.name,
                "type": activity.type,
                "start_date": activity.start_date.isoformat(),
                "distance_meters": float(activity.distance),
                "moving_time_seconds": activity.moving_time.seconds,
                "total_elevation_gain": float(activity.total_elevation_gain),
            }
        )
    return result


@mcp.tool()
def get_activity_details(activity_id: int) -> dict:
    """
    Get detailed information for a specific activity.

    Args:
        activity_id: The ID of the activity to retrieve
    """
    client = get_client()
    activity = client.get_activity(activity_id)

    return {
        "id": activity.id,
        "name": activity.name,
        "description": activity.description,
        "type": activity.type,
        "distance": float(activity.distance),
        "moving_time": activity.moving_time.seconds,
        "elapsed_time": activity.elapsed_time.seconds,
        "total_elevation_gain": float(activity.total_elevation_gain),
        "average_speed": float(activity.average_speed),
        "max_speed": float(activity.max_speed),
        "calories": activity.calories,
        "device_name": activity.device_name,
    }


if __name__ == "__main__":
    mcp.run()
