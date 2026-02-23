"""Data models for Strava MCP Server."""

from dataclasses import dataclass, asdict, field
from typing import Optional


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
    average_speed: float = 0.0
    max_speed: float = 0.0

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


@dataclass
class LapSummary:
    """Summary of a lap in a Strava activity."""

    id: int
    activity_id: int
    lap_index: int
    name: str
    elapsed_time: int
    moving_time: int
    distance: float
    average_speed: float
    max_speed: float
    average_cadence: Optional[float]
    average_watts: Optional[float]
    average_heartrate: Optional[float]
    max_heartrate: Optional[float]
    total_elevation_gain: float

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class ActivityStreams:
    """Raw stream data for a Strava activity."""

    time: Optional[list[int]] = None
    latlng: Optional[list[list[float]]] = None
    distance: Optional[list[float]] = None
    altitude: Optional[list[float]] = None
    velocity_smooth: Optional[list[float]] = None
    heartrate: Optional[list[int]] = None
    cadence: Optional[list[int]] = None
    watts: Optional[list[int]] = None
    temp: Optional[list[int]] = None
    moving: Optional[list[bool]] = None
    grade_smooth: Optional[list[float]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}
