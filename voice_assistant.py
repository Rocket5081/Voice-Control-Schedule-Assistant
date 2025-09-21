import os
import re
from datetime import datetime, timedelta
import pytz
import dateparser
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from elevenlabs.types import ConversationConfig
from google_calendar_service import get_calendar_service, get_todays_events, add_event, move_event, delete_event

# Load environment variables
load_dotenv()
AGENT_ID = os.getenv("AGENT_ID")
API_KEY = os.getenv("API_KEY")

user_name = "Chandler"
timezone = pytz.timezone("America/New_York")

# Google Calendar setup
service = get_calendar_service()
events = get_todays_events(service, timezone=str(timezone))

# Format today's schedule for context
if not events:
    schedule = "You have no events scheduled today."
else:
    schedule = "; ".join(
        f"{event['summary']} at {event['start'].get('dateTime', event['start'].get('date'))}"
        for event in events
    )

# Conversation context
prompt = (
    f"You are a helpful assistant. Your interlocutor has the following schedule: {schedule}. "
    "You can also add, move, and delete events in their Google Calendar when asked."
)
first_message = f"Hello {user_name}, how can I help you today?"

conversation_override = {
    "agent": {
        "prompt": {"prompt": prompt},
        "first_message": first_message,
    }
}

config = ConversationConfig(
    user_id=user_name,
    conversation_config_override=conversation_override,
    extra_body={},
    dynamic_variables={},
)

# ElevenLabs client
client = ElevenLabs(api_key=API_KEY)

# --- Callback functions ---
def print_agent_response(response):
    print(f"Agent: {response}")

def print_interrupted_response(original, corrected):
    print(f"Agent interrupted, truncated response: {corrected}")

def print_user_transcript(transcript):
    print(f"User: {transcript}")
    transcript_lower = transcript.lower()

    if "add event" in transcript_lower or "schedule a" in transcript_lower:
        handle_event_creation(transcript)
    elif "move event" in transcript_lower or "reschedule" in transcript_lower:
        handle_event_move(transcript)
    elif "delete event" in transcript_lower or "remove event" in transcript_lower:
        handle_event_delete(transcript)

# --- Event Handlers ---
def handle_event_creation(transcript):
    """Add an event based on user input, supporting full dates, 'today', 'tomorrow', and AM/PM."""
    # Extract event name (before "for" or "at")
    summary_match = re.search(r"(?:add event|schedule)\s+(.*?)\s+(?:for|at)", transcript, re.IGNORECASE)
    summary = summary_match.group(1) if summary_match else "New Event"

    # Parse date and time from the transcript
    dt = dateparser.parse(
        transcript,
        settings={"TIMEZONE": str(timezone), "RETURN_AS_TIMEZONE_AWARE": True}
    )

    if dt is None:
        dt = datetime.now(timezone) + timedelta(hours=1)
        dt = timezone.localize(dt.replace(second=0, microsecond=0))

    # Ensure timezone awareness
    if dt.tzinfo is None:
        dt = timezone.localize(dt)
    else:
        dt = dt.astimezone(timezone)

    start = dt.replace(second=0, microsecond=0)
    end = start + timedelta(hours=1)

    tz_string = "America/New_York"
    created = add_event(service, summary, start, end, tz_string)
    print(f"Event created: {created['summary']} at {created['start']['dateTime']}")


def handle_event_move(transcript):
    # Extract event name
    name_match = re.search(r"move event\s+(.*?)\s+to", transcript, re.IGNORECASE)
    event_name = name_match.group(1) if name_match else None

    if not event_name:
        print("Could not detect event name.")
        return

    # Partial, case-insensitive match
    events = get_todays_events(service, timezone=str(timezone))
    event_to_move = next((e for e in events if event_name.lower() in e['summary'].lower()), None)
    if not event_to_move:
        print(f"No event found matching '{event_name}'")
        return

    # Parse new datetime
    dt = dateparser.parse(
        transcript,
        settings={"TIMEZONE": str(timezone), "RETURN_AS_TIMEZONE_AWARE": True}
    )

    if dt is None:
        print("Could not detect new date/time for the event.")
        return

    # Ensure timezone awareness
    if dt.tzinfo is None:
        dt = timezone.localize(dt)
    else:
        dt = dt.astimezone(timezone)

    start = dt.replace(second=0, microsecond=0)
    end = start + timedelta(hours=1)

    tz_string = "America/New_York"
    updated = move_event(service, event_to_move['id'], start, end, tz_string)
    print(f"Event '{updated['summary']}' moved to {updated['start']['dateTime']}")


def handle_event_delete(transcript):
    name_match = re.search(r"(?:delete|remove) event\s+(.*)", transcript, re.IGNORECASE)
    if not name_match:
        print("Could not detect event name to delete.")
        return

    event_name = name_match.group(1).strip().lower()

    # Fetch today's events
    events = get_todays_events(service, timezone=str(timezone))

    # Find first event that contains the name (partial, case-insensitive)
    event_to_delete = next(
        (e for e in events if event_name in e['summary'].strip().lower()),
        None
    )

    if not event_to_delete:
        print(f"No event found matching '{event_name}'")
        return

    # Delete the event
    delete_event(service, event_to_delete['id'])
    print(f"Event '{event_to_delete['summary']}' deleted.")




# --- Start Conversation ---
conversation = Conversation(
    client,
    AGENT_ID,
    config=config,
    requires_auth=True,
    audio_interface=DefaultAudioInterface(),
    callback_agent_response=print_agent_response,
    callback_agent_response_correction=print_interrupted_response,
    callback_user_transcript=print_user_transcript,
)

conversation.start_session()
