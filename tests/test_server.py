import pytest
from unittest.mock import MagicMock
import datetime
from server import _get_athlete_stats, _list_activities, _get_activity_details

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


@pytest.fixture
def mock_client():
    return MagicMock()


def test_get_athlete_stats(mock_client):
    # Setup mocks
    mock_client.get_athlete.return_value = MockAthlete()
    mock_client.get_athlete_stats.return_value = MockStats()

    # Run internal function
    result = _get_athlete_stats(mock_client)

    # Verify
    assert "Test Athlete" in result
    assert "Distance: 1000.0" in result
    assert "Achievement Count: 5" in result
    mock_client.get_athlete.assert_called_once()
    mock_client.get_athlete_stats.assert_called_once_with(123)


def test_list_activities(mock_client):
    # Setup mocks
    activities = [
        MockActivity(id=1, name="Run 1"),
        MockActivity(id=2, name="Ride 1", type="Ride"),
    ]
    mock_client.get_activities.return_value = activities

    # Run internal function
    result = _list_activities(mock_client, limit=2)

    # Verify
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["name"] == "Run 1"
    assert result[0]["type"] == "Run"
    assert result[1]["type"] == "Ride"
    assert result[0]["moving_time_seconds"] == 1800
    mock_client.get_activities.assert_called_once_with(limit=2)


def test_list_activities_empty(mock_client):
    mock_client.get_activities.return_value = []
    result = _list_activities(mock_client, limit=5)
    assert result == []


def test_get_activity_details(mock_client):
    # Setup mocks
    mock_client.get_activity.return_value = MockActivity(id=999, name="Big Race")

    # Run internal function
    result = _get_activity_details(mock_client, 999)

    # Verify
    assert result["id"] == 999
    assert result["name"] == "Big Race"
    assert result["distance"] == 5000.0
    assert result["device_name"] == "Garmin"
    mock_client.get_activity.assert_called_once_with(999)
