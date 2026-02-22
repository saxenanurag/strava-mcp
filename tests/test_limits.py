import pytest
from unittest.mock import patch, MagicMock
from server import list_activities_tool, search_activities_tool, MAX_LIMIT


@patch("server.get_client")
@patch("server.list_activities")
def test_list_activities_tool_limit_clamping(mock_list_activities, mock_get_client):
    # Setup
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_list_activities.return_value = []

    # Test with limit > MAX_LIMIT
    excessive_limit = MAX_LIMIT + 100
    list_activities_tool.fn(limit=excessive_limit)

    # Verify list_activities was called with MAX_LIMIT
    mock_list_activities.assert_called_once_with(mock_client, MAX_LIMIT)

    # Verify list_activities was called with MAX_LIMIT
    mock_list_activities.assert_called_once_with(mock_client, MAX_LIMIT)


@patch("server.get_client")
@patch("server.list_activities")
def test_list_activities_tool_normal_limit(mock_list_activities, mock_get_client):
    # Setup
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_list_activities.return_value = []

    # Test with normal limit
    normal_limit = 10
    list_activities_tool.fn(limit=normal_limit)

    # Verify list_activities was called with normal_limit
    mock_list_activities.assert_called_once_with(mock_client, normal_limit)


@patch("server.get_client")
@patch("server.search_activities")
def test_search_activities_tool_limit_clamping(mock_search_activities, mock_get_client):
    # Setup
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_search_activities.return_value = []

    # Test with limit > MAX_LIMIT
    excessive_limit = MAX_LIMIT + 100
    search_activities_tool.fn(limit=excessive_limit)

    # Verify search_activities was called with MAX_LIMIT (among other args)
    # Check that limit=MAX_LIMIT is in kwargs or args
    call_args = mock_search_activities.call_args
    assert call_args.kwargs["limit"] == MAX_LIMIT
