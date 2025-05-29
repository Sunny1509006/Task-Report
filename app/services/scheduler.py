from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.crud import task_crud
from datetime import datetime
from app.database import db
from app.utils.reports import get_sunday_saturday_range, generate_weekly_report
from datetime import datetime, timedelta
import pytz

scheduler = AsyncIOScheduler()

async def daily_feedback_reminder():
    # Logic to send daily feedback reminder (e.g., email or log)
    print("Reminder: Submit your task feedback for today!")

def start_scheduler():
    scheduler.add_job(daily_feedback_reminder, 'cron', hour=21, minute=0)
    scheduler.start()


async def generate_reports_for_all_users():
    user_ids = await db.tasks.distinct("user_id")

    tz = pytz.timezone("Asia/Dhaka")
    now = datetime.now(tz)
    # Generate for last full week (previous Sunday to Saturday)
    sunday, saturday = get_sunday_saturday_range(now - timedelta(days=7))

    for user_id in user_ids:
        await generate_weekly_report(user_id, sunday, saturday)
        print(f"Generated weekly report for user {user_id}")

async def weekly_report_job():
    print("Starting weekly report job...")
    await generate_reports_for_all_users()
    print("Weekly report job completed.")

def start_scheduler():
    scheduler.add_job(
        weekly_report_job,
        'cron',
        day_of_week='sun',
        hour=0,
        minute=0,
        second=0,
        timezone='Asia/Dhaka',
        id="weekly_report"
    )
    scheduler.start()
    print("Scheduler started for weekly report.")
