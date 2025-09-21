from __future__ import print_function
import datetime
import os
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Returns an authenticated Google Calendar service object."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def get_todays_events(service, timezone="America/New_York"):
    """Fetch today's events from Google Calendar."""
    tz = pytz.timezone(timezone)
    now = datetime.datetime.now(tz).isoformat()
    end_of_day = datetime.datetime.now(tz).replace(hour=23, minute=59, second=59).isoformat()

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=end_of_day,
        maxResults=50,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return events_result.get("items", [])

def add_event(service, summary, start, end, timezone="America/New_York"):
    """Add an event to Google Calendar."""
    event = {
        "summary": summary,
        "start": {"dateTime": start.isoformat(), "timeZone": timezone},
        "end": {"dateTime": end.isoformat(), "timeZone": timezone},
    }
    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return created_event

def move_event(service, event_id, new_start, new_end, timezone="America/New_York"):
    """Move an existing event to a new start and end time."""
    event = service.events().get(calendarId="primary", eventId=event_id).execute()
    event['start'] = {"dateTime": new_start.isoformat(), "timeZone": timezone}
    event['end'] = {"dateTime": new_end.isoformat(), "timeZone": timezone}

    updated_event = service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
    return updated_event

def delete_event(service, event_id):
    """Delete an existing event by ID."""
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return f"Event {event_id} deleted."
