"""Tests for Strava MCP Server."""

import pytest
from unittest.mock import MagicMock
import datetime
from strava_mcp.models import (
    AthleteStats,
    ActivitySummary,
    ActivityDetails,
    LapSummary,
    ActivityStreams,
)
from strava_mcp.services.athlete import get_athlete_stats
from strava_mcp.services.activities import (
    list_activities,
    search_activities,
    get_activity_details,
)
from strava_mcp.services.streams import get_activity_laps, get_activity_streams

# Mock objects to simulate Strava API responses


class MockAthlete:
    def __init__(self):
        self.id = 123
        self.firstname = "Test"
        self.lastname = "Athlete"


class MockStats:
    def __init__(self):
        self.recent_run_totals = MagicMock(distance=1000.0, achievement_count=5)
        self.all_run_totals = MagicMock(distance=50000.0)
        self.recent_ride_totals = MagicMock(distance=2000.0, elevation_gain=100.0)


class MockActivity:
    def __init__(self, id=1, name="Run", type="Run"):
        self.id = id
        self.name = name
        self.type = type
        self.start_date = datetime.datetime(2023, 1, 1, 12, 0, 0)
        self.distance = 5000.0
        self.moving_time = datetime.timedelta(seconds=1800)
        self.elapsed_time = datetime.timedelta(seconds=2000)
        self.total_elevation_gain = 50.0
        self.average_speed = 2.8
        self.max_speed = 3.5
        self.calories = 300
        self.device_name = "Garmin"
        self.description = "Nice run"


class MockLap:
    def __init__(self, id=1, name="Lap 1"):
        self.id = id
        self.activity_id = 123
        self.lap_index = id
        self.name = name
        self.elapsed_time = datetime.timedelta(seconds=600)
        self.moving_time = datetime.timedelta(seconds=580)
        self.distance = 1000.0
        self.average_speed = 2.5
        self.max_speed = 3.0
        self.average_cadence = 85.0
        self.average_watts = None
        self.average_heartrate = 145.0
        self.max_heartrate = 165.0
        self.total_elevation_gain = 50.0


class MockStream:
    def __init__(self, data):
        self.data = data


@pytest.fixture
def mock_client():
    return MagicMock()


def test_get_athlete_stats(mock_client):
    # Setup mocks
    mock_client.get_athlete.return_value = MockAthlete()
    mock_client.get_athlete_stats.return_value = MockStats()

    # Run service function
    result = get_athlete_stats(mock_client)

    # Verify - result is now an AthleteStats dataclass
    assert isinstance(result, AthleteStats)
    assert result.firstname == "Test"
    assert result.lastname == "Athlete"
    assert result.recent_run_totals.distance == 1000.0
    assert result.recent_run_totals.achievement_count == 5

    # Verify the formatted string output
    formatted = result.to_formatted_string()
    assert "Test Athlete" in formatted
    assert "Distance: 1000.0" in formatted
    assert "Achievement Count: 5" in formatted

    mock_client.get_athlete.assert_called_once()
    mock_client.get_athlete_stats.assert_called_once_with(123)


def test_list_activities(mock_client):
    # Setup mocks
    activities = [
        MockActivity(id=1, name="Run 1"),
        MockActivity(id=2, name="Ride 1", type="Ride"),
    ]
    mock_client.get_activities.return_value = activities

    # Run service function
    result = list_activities(mock_client, limit=2)

    # Verify - result is now a list of ActivitySummary dataclasses
    assert len(result) == 2
    assert isinstance(result[0], ActivitySummary)
    assert result[0].id == 1
    assert result[0].name == "Run 1"
    assert result[0].type == "Run"
    assert result[1].type == "Ride"
    assert result[0].moving_time == 1800

    # Verify to_dict method works
    dict_result = result[0].to_dict()
    assert dict_result["id"] == 1
    assert dict_result["name"] == "Run 1"

    mock_client.get_activities.assert_called_once_with(limit=2)


def test_list_activities_empty(mock_client):
    mock_client.get_activities.return_value = []
    result = list_activities(mock_client, limit=5)
    assert result == []


def test_get_activity_details(mock_client):
    # Setup mocks
    mock_client.get_activity.return_value = MockActivity(id=999, name="Big Race")

    # Run service function
    result = get_activity_details(mock_client, 999)

    # Verify - result is now an ActivityDetails dataclass
    assert isinstance(result, ActivityDetails)
    assert result.id == 999
    assert result.name == "Big Race"
    assert result.distance == 5000.0
    assert result.device_name == "Garmin"

    # Verify to_dict method works
    dict_result = result.to_dict()
    assert dict_result["id"] == 999
    assert dict_result["name"] == "Big Race"

    mock_client.get_activity.assert_called_once_with(999)


def test_get_activity_laps(mock_client):
    # Setup mocks
    laps = [
        MockLap(id=1, name="Lap 1"),
        MockLap(id=2, name="Lap 2"),
    ]
    mock_client.get_activity_laps.return_value = laps

    # Run service function
    result = get_activity_laps(mock_client, 123)

    # Verify - result is a list of LapSummary dataclasses
    assert len(result) == 2
    assert isinstance(result[0], LapSummary)
    assert result[0].id == 1
    assert result[0].name == "Lap 1"
    assert result[0].activity_id == 123
    assert result[0].lap_index == 1
    assert result[0].distance == 1000.0
    assert result[0].average_speed == 2.5
    assert result[0].elapsed_time == 600
    assert result[0].moving_time == 580
    assert result[0].average_cadence == 85.0
    assert result[0].average_watts is None
    assert result[0].average_heartrate == 145.0
    assert result[0].max_heartrate == 165.0

    # Verify to_dict method works
    dict_result = result[0].to_dict()
    assert dict_result["id"] == 1
    assert dict_result["name"] == "Lap 1"
    assert dict_result["lap_index"] == 1

    mock_client.get_activity_laps.assert_called_once_with(123)


def test_get_activity_laps_empty(mock_client):
    mock_client.get_activity_laps.return_value = []
    result = get_activity_laps(mock_client, 123)
    assert result == []


def test_get_activity_streams(mock_client):
    # Setup mocks with sample stream data
    mock_streams = {
        "time": MockStream([0, 1, 2, 3, 4]),
        "latlng": MockStream([[37.7, -122.4], [37.8, -122.5]]),
        "distance": MockStream([0.0, 10.0, 20.0, 30.0, 40.0]),
        "altitude": MockStream([100.0, 101.0, 102.0, 103.0, 104.0]),
        "heartrate": MockStream([120, 125, 130, 135, 140]),
    }
    mock_client.get_activity_streams.return_value = mock_streams

    # Run service function with specific types
    result = get_activity_streams(mock_client, 123, types=["time", "heartrate"])

    # Verify - result is an ActivityStreams dataclass
    assert isinstance(result, ActivityStreams)
    assert result.time == [0, 1, 2, 3, 4]
    assert result.heartrate == [120, 125, 130, 135, 140]
    assert result.latlng == [[37.7, -122.4], [37.8, -122.5]]
    assert result.distance == [0.0, 10.0, 20.0, 30.0, 40.0]
    assert result.altitude == [100.0, 101.0, 102.0, 103.0, 104.0]
    assert result.cadence is None  # Not in our mock data
    assert result.watts is None  # Not in our mock data

    # Verify to_dict method works and excludes None values
    dict_result = result.to_dict()
    assert "time" in dict_result
    assert "heartrate" in dict_result
    assert "cadence" not in dict_result  # None values should be excluded
    assert dict_result["time"] == [0, 1, 2, 3, 4]

    mock_client.get_activity_streams.assert_called_once_with(
        123, types=["time", "heartrate"], resolution=None
    )


def test_get_activity_streams_empty(mock_client):
    mock_client.get_activity_streams.return_value = {}
    result = get_activity_streams(mock_client, 123)
    assert isinstance(result, ActivityStreams)
    assert result.to_dict() == {}


def test_get_activity_streams_missing_fields(mock_client):
    # Setup mocks with partial stream data
    mock_streams = {
        "time": MockStream([0, 1, 2]),
    }
    mock_client.get_activity_streams.return_value = mock_streams

    result = get_activity_streams(mock_client, 123)

    assert isinstance(result, ActivityStreams)
    assert result.time == [0, 1, 2]
    assert result.heartrate is None
    assert result.latlng is None


def test_search_activities_by_name(mock_client):
    # Setup mocks
    activities = [
        MockActivity(id=1, name="Morning Run", type="Run"),
        MockActivity(id=2, name="Evening Ride", type="Ride"),
        MockActivity(id=3, name="Morning Walk", type="Walk"),
    ]
    mock_client.get_activities.return_value = activities

    # Search for "morning" activities
    result = search_activities(mock_client, query="morning", limit=10)

    assert len(result) == 2
    assert all(isinstance(r, ActivitySummary) for r in result)
    assert result[0].name == "Morning Run"
    assert result[1].name == "Morning Walk"

    mock_client.get_activities.assert_called_once()


def test_search_activities_by_type(mock_client):
    # Setup mocks
    activities = [
        MockActivity(id=1, name="Run 1", type="Run"),
        MockActivity(id=2, name="Ride 1", type="Ride"),
        MockActivity(id=3, name="Run 2", type="Run"),
    ]
    mock_client.get_activities.return_value = activities

    # Filter by type "run"
    result = search_activities(mock_client, activity_type="run", limit=10)

    assert len(result) == 2
    assert all(r.type == "Run" for r in result)


def test_search_activities_by_distance(mock_client):
    # Setup mocks with different distances
    act1 = MockActivity(id=1, name="Short Run", type="Run")
    act1.distance = 3000.0
    act2 = MockActivity(id=2, name="Long Run", type="Run")
    act2.distance = 10000.0
    act3 = MockActivity(id=3, name="Medium Run", type="Run")
    act3.distance = 5000.0

    activities = [act1, act2, act3]
    mock_client.get_activities.return_value = activities

    # Filter by distance range
    result = search_activities(
        mock_client, min_distance=4000.0, max_distance=6000.0, limit=10
    )

    assert len(result) == 1
    assert result[0].name == "Medium Run"
    assert result[0].distance == 5000.0


def test_search_activities_combined_filters(mock_client):
    # Setup mocks
    activities = [
        MockActivity(id=1, name="Morning Run", type="Run"),
        MockActivity(id=2, name="Morning Ride", type="Ride"),
        MockActivity(id=3, name="Evening Run", type="Run"),
        MockActivity(id=4, name="Evening Ride", type="Ride"),
    ]
    mock_client.get_activities.return_value = activities

    # Combined search: "morning" + "ride"
    result = search_activities(
        mock_client, query="morning", activity_type="ride", limit=10
    )

    assert len(result) == 1
    assert result[0].name == "Morning Ride"


def test_search_activities_no_matches(mock_client):
    # Setup mocks
    activities = [
        MockActivity(id=1, name="Morning Run", type="Run"),
        MockActivity(id=2, name="Evening Ride", type="Ride"),
    ]
    mock_client.get_activities.return_value = activities

    # Search for non-existent term
    result = search_activities(mock_client, query="swimming", limit=10)

    assert len(result) == 0
    assert result == []


def test_search_activities_empty_query_returns_all(mock_client):
    # Setup mocks
    activities = [
        MockActivity(id=1, name="Run 1", type="Run"),
        MockActivity(id=2, name="Run 2", type="Run"),
    ]
    mock_client.get_activities.return_value = activities

    # No filters - should return all
    result = search_activities(mock_client, limit=10)

    assert len(result) == 2
