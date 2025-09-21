# Voice-Controlled Virtual Assistant with Google Calendar Integration

This project is a voice-controlled virtual assistant that can **create, move, and delete events** on your Google Calendar using ElevenLabs for conversational AI.

---

## Features

- **Schedule events** by specifying time, AM/PM, today, tomorrow, or exact dates.  
- **Move events** to a new date/time.  
- **Delete events** with partial, case-insensitive name matching.  
- **Voice interaction** using ElevenLabs AI.  
- **Timezone-aware** scheduling (supports your local timezone).

---

## Getting Started

### 1. Clone the repository

git clone https://github.com/yourusername/virtual-assistant.git
cd virtual-assistant

###2. Create a virtual environment

python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

###3. Install dependencies

pip install -r requirements.txt

###4. Set up environment variables

Create a .env file with the following:
AGENT_ID=your_elevenlabs_agent_id
API_KEY=your_elevenlabs_api_key
Do not commit this file to GitHub.

###5. Set up Google Calendar API
Go to Google Cloud Console.

Enable the Google Calendar API.

Create OAuth credentials and download credentials.json.

Place credentials.json in the project folder.

On first run, the app will generate token.json after you authenticate with Google.

#Usage
Run the voice assistant:

python voice_assistant.py

##Example commands:

Add event Reading Time for September 22, 2025 at 12 p.m.

Move event Reading Time to September 23, 2025 at 3 p.m.

Delete event Reading Time

#Project Files
voice_assistant.py – Main assistant logic

google_calendar_service.py – Google Calendar helper functions

.env.example – Template for environment variables

requirements.txt – Python dependencies

#Dependencies
Python 3.10+

ElevenLabs SDK

google-api-python-client

python-dotenv

pytz

dateparser

Security
Do not commit .env or token.json.

Use .gitignore to prevent sensitive files from being tracked.
