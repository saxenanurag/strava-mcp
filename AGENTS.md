# Strava MCP Server - Agent Guidelines

This document provides comprehensive instructions for AI agents working on this repository.
It covers build commands, code style, testing protocols, and architectural patterns.

## 1. Environment & Build Commands

This project uses **`uv`** for dependency management and **`pytest`** for testing.
Ensure you are using Python 3.10 or higher.

| Action | Command | Description |
| :--- | :--- | :--- |
| **Install Dependencies** | `uv sync` | Creates/updates `.venv` with all dependencies |
| **Run Server** | `uv run server.py` | Starts the MCP server |
| **Run All Tests** | `uv run pytest tests` | Executes all unit tests |
| **Run Single Test** | `uv run pytest tests/test_server.py::test_list_activities` | targeted test execution |
| **Run Test File** | `uv run pytest tests/test_server.py` | Run all tests in a file |
| **Run with Coverage** | `uv run pytest --cov=strava_mcp tests` | specific for coverage analysis |
| **Add Package** | `uv add <package>` | Adds a runtime dependency |
| **Add Dev Package** | `uv add --dev <package>` | Adds a development dependency |
| **Format Code** | `uv run ruff format .` | (If ruff is available) otherwise follow PEP 8 |

*Note: If `ruff` is not installed, adhere strictly to PEP 8 standards manually.*

## 2. Project Structure

The project follows a modular architecture separating the MCP server interface from core logic.

```
strava-mcp/
├── server.py              # Entry point. Defines MCP tools and handles requests.
├── strava_mcp/            # Core package
│   ├── auth.py            # Authentication logic (OAuth token management)
│   ├── config.py          # Configuration loading
│   ├── models.py          # Pydantic models & data structures
│   └── services/          # Business logic (API interaction)
│       ├── activities.py  # Activity fetching/searching
│       ├── athlete.py     # Athlete stats
│       └── streams.py     # Data streams (GPS, HR, etc.)
└── tests/                 # Pytest test suite
    └── test_server.py     # Unit tests for tools and services
```

### Architectural Principles
1.  **Separation of Concerns**: `server.py` should only contain `@mcp.tool` definitions and delegation. Actual logic resides in `strava_mcp/services/`.
2.  **Service Layer**: Services take a `stravalib.client.Client` instance as an argument, making them easy to test with mocks.
3.  **Data Models**: Use dataclasses or Pydantic models in `strava_mcp/models.py` to structure API responses before returning them to the MCP client.

## 3. Code Style & Conventions

### General
- **Python Version**: Target Python 3.10+.
- **Type Hints**: **Strictly required** for all function signatures.
    - Use `list[str]` instead of `List[str]` (modern syntax).
    - Use `Optional[T]` or `T | None`.
- **Docstrings**: Required for all public tools and service functions.
    - Use clear, descriptive docstrings.
    - For MCP tools, the docstring is the user-facing description.

### Imports
Group imports in this specific order:
1.  **Standard Library**: `sys`, `os`, `typing`, `datetime`
2.  **Third-Party**: `fastmcp`, `stravalib`, `dotenv`
3.  **Local Modules**: `strava_mcp.auth`, `strava_mcp.models`

```python
# Good Example
import sys
from typing import Optional

from fastmcp import FastMCP
from stravalib.model import Activity

from strava_mcp.services.activities import list_activities
```

### Naming Conventions
- **Variables/Functions**: `snake_case` (e.g., `get_activity_details`)
- **Classes**: `PascalCase` (e.g., `ActivityManager`)
- **Constants**: `UPPER_CASE` (e.g., `MAX_RETRIES`)
- **Private/Internal**: Prefix with `_` (e.g., `_fetch_raw_data`)

### MCP Server Specifics
- **Output Safety**: **NEVER** use `print()` for logging. It corrupts the JSON-RPC channel.
    - ✅ **Correct**: `sys.stderr.write(f"Processing activity {id}\n")`
    - ❌ **Incorrect**: `print(f"Processing activity {id}")`
- **Tool Decorators**: Always use `@mcp.tool()` for public capabilities.

## 4. Error Handling

- **Authentication**: Wrap Strava API calls in `try/except` blocks to handle token expiration or API errors.
- **Graceful Failure**: If a non-critical field is missing, log it and return a partial result rather than crashing.
- **Secret Safety**: **NEVER** expose raw exception stack traces that might contain API tokens.
    - Catch exceptions and raise a generic `RuntimeError` or return a user-friendly error message.

## 5. Testing Guidelines

Tests are located in `tests/` and use `pytest`.

### Mocking Strategy
- **Do not make real API calls.**
- Use `unittest.mock.MagicMock` to mock `stravalib.client.Client` and its methods.
- Mock the return values using the data structures defined in `strava_mcp/models.py` or simple dictionaries if appropriate.

### Creating a New Test
1.  Create a fixture for the client if one doesn't exist for your scope.
2.  Mock the expected Strava API response.
3.  Call the service function (not the MCP tool directly, unless testing integration).
4.  Assert the result structure and values.

```python
def test_new_feature(mock_client):
    # 1. Setup Mock
    mock_client.get_something.return_value = "expected_data"
    
    # 2. Call Service
    result = my_new_service_function(mock_client)
    
    # 3. Assert
    assert result == "formatted_data"
    mock_client.get_something.assert_called_once()
```

## 6. Workflow for Adding Features

1.  **Define Model**: Add necessary data classes in `strava_mcp/models.py`.
2.  **Implement Service**: Create the logic in `strava_mcp/services/`.
3.  **Add Tool**: Expose the service via a new tool in `server.py`.
4.  **Write Tests**: Add unit tests in `tests/` covering success and failure cases.
5.  **Verify**: Run `uv run pytest` to ensure no regressions.
