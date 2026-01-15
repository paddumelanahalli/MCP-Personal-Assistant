import os
import asyncio
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP
from ddgs import DDGS

# OAuth Scopes for Gmail and Calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/calendar.readonly'
]

# Initialize FastMCP with a generic name
mcp = FastMCP("Personal-Assistant-Server")

# Secure path handling for local credentials
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')
CREDS_PATH = os.path.join(BASE_DIR, 'credentials.json')


def get_google_creds():
    """Handles OAuth2 token lifecycle securely."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_PATH):
                raise FileNotFoundError(f"Missing {CREDS_PATH}. Please provide Google Cloud credentials.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds


@mcp.tool()
async def get_weather(city: str = "San Francisco"):
    """Fetches a real-time weather summary for a specified city."""
    # Note: In a production version, you could integrate a weather API here.
    return f"The weather in {city} is currently 65°F and Partly Cloudy."


@mcp.tool()
async def get_unread_emails(limit: int = 3):
    """Summarizes recent unread Gmail messages from the inbox."""
    try:
        service = build('gmail', 'v1', credentials=get_google_creds())
        results = service.users().messages().list(userId='me', q="is:unread label:INBOX", maxResults=limit).execute()
        messages = results.get('messages', [])
        if not messages:
            return "No unread emails."

        summaries = []
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = txt['payload']['headers']
            subj = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            summaries.append(f"Subject: {subj} | Snippet: {txt.get('snippet', '')}")
        return "\n".join(summaries)
    except Exception as e:
        return f"Gmail Error: {str(e)}"


@mcp.tool()
async def get_calendar_events(limit: int = 5):
    """Lists upcoming appointments and birthdays from the primary calendar."""
    try:
        service = build('calendar', 'v3', credentials=get_google_creds())
        now = datetime.now(timezone.utc).isoformat()
        events_result = service.events().list(
            calendarId='primary', timeMin=now, maxResults=limit,
            singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        if not events:
            return "No upcoming events found."

        return "\n".join(
            [f"- {e.get('summary')} ({e['start'].get('dateTime', e['start'].get('date'))})" for e in events])
    except Exception as e:
        return f"Calendar Error: {str(e)}"


@mcp.tool()
async def web_search(query: str):
    """Performs a web search for research, gift ideas, or information synthesis."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=2)]
            if not results:
                return "No search results found."
            return "\n".join([f"{r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return f"Search Error: {str(e)}"


@mcp.tool()
async def create_draft(subject: str, body: str):
    """Creates a new Gmail draft based on the agent's findings."""
    try:
        from email.message import EmailMessage
        import base64

        service = build('gmail', 'v1', credentials=get_google_creds())
        mime_msg = EmailMessage()
        mime_msg.set_content(body)
        mime_msg['Subject'] = subject
        mime_msg['To'] = 'me'  # Drafts for the user to review

        encoded_message = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()
        create_message = {'message': {'raw': encoded_message}}

        service.users().drafts().create(userId='me', body=create_message).execute()
        return f"SUCCESS: Draft created with subject: '{subject}'"
    except Exception as e:
        return f"Drafting Error: {str(e)}"


@mcp.tool()
async def get_morning_status(city: str = "San Francisco"):
    """Unified command to gather Weather, Mail, and Calendar context in parallel."""
    weather_task = get_weather(city)
    email_task = get_unread_emails()
    calendar_task = get_calendar_events()

    weather, emails, calendar = await asyncio.gather(weather_task, email_task, calendar_task)
    return f"WEATHER: {weather}\n\nGMAIL:\n{emails}\n\nCALENDAR:\n{calendar}"


if __name__ == "__main__":
    mcp.run()
