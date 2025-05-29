from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.crud import task_crud
from datetime import datetime

scheduler = AsyncIOScheduler()

async def daily_feedback_reminder():
    # Logic to send daily feedback reminder (e.g., email or log)
    print("Reminder: Submit your task feedback for today!")

def start_scheduler():
    scheduler.add_job(daily_feedback_reminder, 'cron', hour=21, minute=0)
    scheduler.start()