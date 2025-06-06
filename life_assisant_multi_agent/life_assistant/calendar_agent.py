from utils.file_utils import read_json, write_json
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'
QUEUE_PATH = "messages/queue.json"

def get_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    return service

def create_event(payload: dict) -> str:
    service = get_service()
    event = {
        'summary': payload["data"]["summary"],
        'start': {'dateTime': payload["data"]["start"]},
        'end': {'dateTime': payload["data"]["end"]},
        'attendees': [{'email': e} for e in payload["data"].get("attendees", [])]
    }
    created = service.events().insert(calendarId='primary', body=event).execute()
    return created.get("id")

def detect_conflicts(payload: dict) -> bool:
    service = get_service()
    body = {
        "timeMin": payload["data"]["start"],
        "timeMax": payload["data"]["end"],
        "items": [{"id": 'primary'}]
    }
    events_result = service.freebusy().query(body=body).execute()
    busy = events_result["calendars"]['primary']["busy"]
    return len(busy) == 0

def handle(payload):
    if payload.get("action") == "create_event":
        if detect_conflicts(payload):
            create_event(payload)
        else:
            queue = read_json(QUEUE_PATH)
            queue.setdefault("messages", []).append({
                "type": "calendar_response",
                "target": "interface_agent",
                "payload": {"status": "conflict"},
                "status": "new"
            })
            write_json(QUEUE_PATH, queue)
