import pytest
from strava_mcp.services.analysis import analyze_data


def test_analyze_simple_math():
    """Test basic arithmetic in Monty."""
    code = "data['x'] + 1"
    data = {"x": 10}
    result = analyze_data(code, data)
    assert result == 11


def test_analyze_list_processing():
    """Test processing a list of items (like activities)."""
    code = "sum(item['distance'] for item in data)"
    data = [
        {"id": 1, "distance": 1000},
        {"id": 2, "distance": 2000},
        {"id": 3, "distance": 500},
    ]
    result = analyze_data(code, data)
    assert result == 3500


def test_analyze_with_invalid_code():
    """Test that invalid code raises an error."""
    code = "syntax error here"
    data = {}
    # We expect some kind of error, likely exposed as a runtime error or caught
    # depending on how we implement the service. For now, let's assume it raises.
    with pytest.raises(Exception):
        analyze_data(code, data)
