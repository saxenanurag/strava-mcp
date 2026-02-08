# Strava MCP Server - Agent Guidelines

This document provides instructions for AI agents working on this repository.

## 1. Build, Lint, and Test Commands

This project uses `uv` for dependency management and `pytest` for testing.

| Command | Description |
| :--- | :--- |
| **Install dependencies** | `uv sync` (creates/updates `.venv`) |
| **Run Server** | `uv run server.py` |
| **Run All Tests** | `uv run pytest tests` |
| **Run Single Test** | `uv run pytest tests/test_server.py::test_list_activities` |
| **Run specific file** | `uv run pytest tests/test_server.py` |
| **Add Dependency** | `uv add <package>` |
| **Add Dev Dependency** | `uv add --dev <package>` |

## 2. Code Style & Conventions

### General
- **Python Version**: 3.10+
- **Formatter**: Follow standard PEP 8.
- **Type Hints**: strict type hints are encouraged for all function signatures (e.g., `def func(x: int) -> str:`).

### Imports
Group imports in the following order:
1. Standard Library (`sys`, `os`, `time`, `datetime`)
2. Third-Party (`dotenv`, `fastmcp`, `stravalib`)
3. Local Modules (`server`)

### Naming Conventions
- **Variables/Functions**: `snake_case` (e.g., `get_athlete_stats`, `activity_id`).
- **Constants**: `UPPER_CASE` (e.g., `CLIENT_ID`, `REFRESH_TOKEN`).
- **Private/Internal**: Prefix with underscore (e.g., `_client`, `_get_athlete_stats`).

### MCP Server Specifics
- **Output Safety**: **NEVER** use `print()` for logging or debugging. Standard output is used for the MCP protocol JSON communication.
    - ✅ **Use**: `sys.stderr.write("Log message\n")`
    - ❌ **Avoid**: `print("Log message")`
- **Tool Definition**:
    - Decorate public tools with `@mcp.tool()`.
    - Delegate logic to internal functions (e.g., `_list_activities`) to make them testable without mocking the MCP server instance.
    - Docstrings must be clear as they are exposed to the AI client.

### Error Handling
- **Authentication**: Wrap Strava API calls in `try/except` blocks.
- **Leaking Secrets**: Do not return raw exception traces to the user if they might contain tokens. Log the full error to `stderr` and raise a generic `RuntimeError`.
- **Missing Data**: Handle `None` values gracefully (e.g., `activity.distance` might be None). Use helper functions or defaults (e.g., `getattr(obj, 'attr', default)`).

### Environment Variables
- Load secrets from a `.env` file.
- **Critical**: Load `.env` relative to the script directory to ensure it works regardless of the Current Working Directory (CWD).
  ```python
  script_dir = os.path.dirname(os.path.abspath(__file__))
  load_dotenv(os.path.join(script_dir, ".env"))
  ```

## 3. Testing Guidelines
- **Framework**: `pytest` with `unittest.mock`.
- **Mocking**:
    - Mock `stravalib.client.Client` and its response objects (`Athlete`, `Activity`, `Stats`).
    - Do not make real API calls in tests.
- **Coverage**: Ensure tests cover:
    - Successful data retrieval.
    - Formatting of response strings.
    - Handling of optional/missing fields (e.g., missing `moving_time`).
    - Empty states (e.g., no activities found).

## 4. Project Structure
- `server.py`: Main entry point. Contains MCP tools and auth logic.
- `tests/`: Contains unit tests.
- `pyproject.toml`: Dependency configuration (hatchling build backend).
- `.env`: (Ignored) Local secrets.
