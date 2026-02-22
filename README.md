# Strava MCP Server

A Model Context Protocol (MCP) server that connects to the Strava API, allowing AI agents to retrieve athlete stats, list activities, and get detailed activity information.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (installed and available in your PATH)
- [Strava Account](https://www.strava.com/)
- Strava API Application (to get Client ID and Secret)

## Setup

### 1. Credentials

1.  Go to [Strava API Settings](https://www.strava.com/settings/api).
2.  Create an application if you haven't already.
3.  Note your `Client ID` and `Client Secret`.
4.  You need a **Refresh Token**.
    *   The easiest way to get one for your own account is to use the [Strava OAuth playground](https://developers.strava.com/playground/) or follow the [Strava authentication docs](https://developers.strava.com/docs/authentication/) to authorize your app and get the initial refresh token.
    *   Scope required: `activity:read_all,read_all` (adjust based on needs).

### 2. Installation

Clone this repository and enter the directory.

**Using `uv` (Recommended):**

```bash
uv sync
source .venv/bin/activate
```

**Using standard `pip`:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install .
```

### 3. Configuration

1.  Copy `.env.example` to `.env`.
2.  Fill in your credentials.

```bash
cp .env.example .env
# Edit .env with your favorite editor
```

## Usage

Run the server using `fastmcp`:

```bash
fastmcp run server.py
```

Or run it directly with `uv`:

```bash
uv run server.py
```

### Available Tools

-   `get_athlete_stats`: Get statistics for the authenticated athlete.
-   `list_activities`: List recent activities (default limit: 5).
-   `get_activity_details`: Get detailed information for a specific activity ID.
-   `get_activity_laps`: Get lap breakdowns for an activity (lap splits with metrics like pace, HR, power).
-   `get_activity_streams`: Get raw stream data (GPS, heart rate, power, cadence, etc.) for an activity.
-   `search_activities`: Search activities with filters (name query, type, date range, distance range).

### Experimental

-   `analyze_data`: Execute Python code to analyze Strava data safely using [Monty](https://github.com/pydantic/monty).
    -   **Note:** This tool allows the agent to write and execute Python code in a secure, sandboxed environment to perform complex calculations on your data (e.g., "calculate average pace for runs over 10km").

## Connect to Claude Desktop

To use this server with Claude Desktop securely (keeping your API keys in `.env` and not in the config file), add the following to your `claude_desktop_config.json`:

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

You can use `uv` directly to run the server:

```json
{
  "mcpServers": {
    "strava": {
      "command": "uv",
      "args": [
        "run",
        "server.py"
      ],
      "cwd": "/absolute/path/to/strava-mcp"
    }
  }
}
```

*Note: Replace `/absolute/path/to/strava-mcp` with the full absolute path to your project directory. If Claude Desktop fails to start the server, you may need to provide the absolute path to the `uv` executable (e.g., `/Users/yourname/.cargo/bin/uv`). Run `which uv` (macOS/Linux) or `where uv` (Windows) in your terminal to find it.*

## Development

### Running Tests

To run the test suite:

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest tests
```

- Modify `server.py` to add more tools using the `stravalib` client.
