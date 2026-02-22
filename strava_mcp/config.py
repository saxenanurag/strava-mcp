"""Configuration for Strava MCP Server."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from the directory containing this script
# This ensures .env is found even if the script is run from a different CWD
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "..", ".env"))

# Configuration
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    sys.stderr.write(
        "Warning: STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, or STRAVA_REFRESH_TOKEN not set in environment.\n"
    )
