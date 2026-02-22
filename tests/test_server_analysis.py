from unittest.mock import patch, MagicMock
from server import analyze_data_tool


def test_analyze_data_tool_with_dict():
    """Test tool with direct dictionary input."""
    code = "data['x']"
    data = {"x": 1}

    # We mock the service to avoid actual execution overhead/dependency in this unit test
    # though Monty is fast, we want to test the tool wrapper logic (json parsing etc)
    with patch("server.analyze_data") as mock_analyze:
        mock_analyze.return_value = 1

        # Access the underlying function directly
        result = analyze_data_tool.fn(code, data)

        assert result == 1
        mock_analyze.assert_called_with(code, data)


def test_analyze_data_tool_with_json_string():
    """Test tool with JSON string input."""
    code = "data['x']"
    data_str = '{"x": 1}'

    with patch("server.analyze_data") as mock_analyze:
        mock_analyze.return_value = 1

        result = analyze_data_tool.fn(code, data_str)

        assert result == 1
        # Check that it parsed the JSON
        mock_analyze.assert_called_with(code, {"x": 1})


def test_analyze_data_tool_error_handling():
    """Test tool error handling."""
    code = "invalid"
    data = {}

    with patch("server.analyze_data") as mock_analyze:
        mock_analyze.side_effect = RuntimeError("Monty error")

        result = analyze_data_tool.fn(code, data)

        assert "Error executing code: Monty error" in result
