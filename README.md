# Strava MCP Server

A Model Context Protocol (MCP) server that connects to the Strava API, allowing AI agents to retrieve athlete stats, list activities, and get detailed activity information.

## Prerequisites

- Python 3.10+
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

Or run it directly with Python (if the main block calls `mcp.run()`):

```bash
python server.py
```

### Available Tools

-   `get_athlete_stats`: Get statistics for the authenticated athlete.
-   `list_activities`: List recent activities (default limit: 5).
-   `get_activity_details`: Get detailed information for a specific activity ID.

## Development

-   Modify `server.py` to add more tools using the `stravalib` client.
