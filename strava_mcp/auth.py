"""Authentication and token management for Strava MCP Server."""

import sys
import time
from stravalib.client import Client
from strava_mcp.config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN

# Global state for token management
_client = Client()
_token_expires_at = 0


def get_client() -> Client:
    """
    Returns an authenticated Strava client, refreshing the access token if necessary.
    """
    global _client, _token_expires_at

    # Buffer time to refresh before actual expiration (e.g., 5 minutes)
    if time.time() > _token_expires_at - 300:
        try:
            sys.stderr.write("Refreshing Strava access token...\n")
            # Ensure CLIENT_ID is correctly typed if needed, though stravalib handles str often
            response = _client.refresh_access_token(
                client_id=int(CLIENT_ID)
                if CLIENT_ID and CLIENT_ID.isdigit()
                else CLIENT_ID,  # type: ignore
                client_secret=CLIENT_SECRET,  # type: ignore
                refresh_token=REFRESH_TOKEN,  # type: ignore
            )
            _client.access_token = response["access_token"]
            _client.refresh_token = response["refresh_token"]
            _token_expires_at = response["expires_at"]
            sys.stderr.write("Token refreshed successfully.\n")
        except Exception as e:
            # Log full error to stderr for debugging
            sys.stderr.write(f"Auth Error: {e}\n")
            # Return generic error to client to avoid leaking secrets
            raise RuntimeError("Failed to authenticate with Strava. Check server logs.")

    return _client
