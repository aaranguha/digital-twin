# Google Calendar Integration

import os
from datetime import datetime, timedelta
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")

# Scopes = what permissions we're asking for
#   - calendar.readonly: Read calendar events (for availability/mood)
#   - presentations.readonly: Read Google Slides content (for pitch decks, etc.)
#   - drive.readonly: List files in Drive (needed to find slides by name)
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/presentations.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

#Store OAuth token
TOKEN_PATH = Path(__file__).resolve().parents[2] / "token.json"

#OAuth Flow:
def get_oauth_flow() -> Flow:
    """
    Create an OAuth flow object for the Google login process.

    Flow = the object that handles the OAuth dance:
    1. Generate the Google login URL
    2. Exchange the callback code for tokens
    """
    # Client config contains our app's credentials
    # This is what we got from Google Cloud Console
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uris": [GOOGLE_REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    # Create the Flow object
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )

    return flow


def get_authorization_url() -> str:
    """
    Generate the URL where users go to log in with Google.

    Returns something like:
    https://accounts.google.com/o/oauth2/auth?client_id=...&scope=...
    """
    flow = get_oauth_flow()

    # Generate the authorization URL
    # access_type='offline' = we get a refresh_token (so we can refresh without re-login)
    # prompt='consent' = always show the consent screen (ensures we get refresh_token)
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )

    return auth_url


def exchange_code_for_tokens(code: str) -> dict:
    """
    After user logs in, Google redirects back with a 'code'.
    We exchange this code for actual tokens.

    Args:
        code: The authorization code from Google's callback

    Returns:
        dict with access_token, refresh_token, etc.
    """
    flow = get_oauth_flow()

    # Exchange the code for tokens
    flow.fetch_token(code=code)

    # Get the credentials object
    credentials = flow.credentials

    # Save tokens to file so we don't need to re-login every time
    token_data = {
        "token": credentials.token,                    # Access token (expires in ~1 hour)
        "refresh_token": credentials.refresh_token,    # Refresh token (long-lived)
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    # Write tokens to file
    import json
    with open(TOKEN_PATH, "w") as f:
        json.dump(token_data, f)

    return token_data


def get_credentials() -> Credentials | None:
    """
    Load saved credentials from token.json.

    Returns:
        Credentials object if tokens exist and are valid, None otherwise
    """
    if not TOKEN_PATH.exists():
        return None

    import json
    with open(TOKEN_PATH, "r") as f:
        token_data = json.load(f)

    # Create Credentials object from saved data
    credentials = Credentials(
        token=token_data["token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"],
    )

    return credentials


def is_authenticated() -> bool:
    """Check if we have valid Google credentials."""
    creds = get_credentials()
    return creds is not None


def get_todays_events() -> list[dict]:
    """
    Fetch all calendar events for today.

    Returns:
        List of events, each with: summary, start, end, is_now

    Example return:
        [
            {"summary": "Team Standup", "start": "09:00", "end": "09:30", "is_now": False},
            {"summary": "1:1 with Manager", "start": "14:00", "end": "15:00", "is_now": True},
        ]
    """
    credentials = get_credentials()

    if not credentials:
        return []  # Not authenticated yet

    # Build the Google Calendar API service
    # 'calendar' = the API name, 'v3' = API version
    service = build("calendar", "v3", credentials=credentials)

    # Get today's date range (midnight to midnight in LOCAL time)
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    # Format as RFC3339 with timezone offset
    # Google Calendar API needs timezone info to filter correctly
    import time
    offset = time.timezone if time.daylight == 0 else time.altzone
    offset_hours = -offset // 3600
    offset_str = f"{offset_hours:+03d}:00"

    time_min = start_of_day.isoformat() + offset_str
    time_max = end_of_day.isoformat() + offset_str

    # Call the Calendar API
    events_result = service.events().list(
        calendarId="primary",          # 'primary' = user's main calendar
        timeMin=time_min,              # Start of time range
        timeMax=time_max,              # End of time range
        singleEvents=True,             # Expand recurring events
        orderBy="startTime"            # Sort by start time
    ).execute()

    # Extract the events
    events = events_result.get("items", [])

    # Format events into a simpler structure
    formatted_events = []

    for event in events:
        # Get start/end times (could be date or dateTime depending on all-day vs timed)
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))

        # Parse the datetime strings
        try:
            # Handle datetime format (timed events)
            if "T" in start:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
                start_str = start_dt.strftime("%H:%M")
                end_str = end_dt.strftime("%H:%M")

                # Get current time in the SAME timezone as the event
                # This fixes the timezone mismatch bug
                current_time = datetime.now(tz=start_dt.tzinfo)

                # Check if event is happening right now
                is_now = start_dt <= current_time <= end_dt

                # Check if event has already ended
                is_past = current_time > end_dt
            else:
                # All-day event
                start_str = "All day"
                end_str = "All day"
                is_now = False
                is_past = False
        except Exception:
            start_str = start
            end_str = end
            is_now = False
            is_past = False

        formatted_events.append({
            "summary": event.get("summary", "No title"),
            "start": start_str,
            "end": end_str,
            "is_now": is_now,
            "is_past": is_past,
        })

    return formatted_events
