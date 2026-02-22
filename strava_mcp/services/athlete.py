"""Athlete-related services for Strava MCP Server."""

from stravalib.client import Client
from strava_mcp.models import AthleteStats, ActivityTotals


def get_athlete_stats(client: Client) -> AthleteStats:
    """Get statistics for the authenticated athlete."""
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
