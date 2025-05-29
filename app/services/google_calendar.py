from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.schemas.task_schema import TaskCreate
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)

async def add_event(task: TaskCreate):
    # event = {
    #     'summary': task.task_name,
    #     'start': {'dateTime': task.start_time.isoformat(), 'timeZone': 'UTC'},
    #     'end': {'dateTime': task.end_time.isoformat(), 'timeZone': 'UTC'},
    # }
    event = {
    'summary': task.task_name,
    'start': {
        'dateTime': task.start_time.isoformat(),
        'timeZone': 'Asia/Dhaka',
    },
    'end': {
        'dateTime': task.end_time.isoformat(),
        'timeZone': 'Asia/Dhaka',
    },
}

    service.events().insert(calendarId='sunny1509006@gmail.com', body=event).execute()