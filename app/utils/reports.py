from datetime import datetime, timedelta
from app.database import db
import pytz

# Helper to get Sunday-Saturday week range from a reference date
def get_sunday_saturday_range(reference_date=None, tz_str="Asia/Dhaka"):
    tz = pytz.timezone(tz_str)
    if reference_date is None:
        reference_date = datetime.now(tz).date()
    else:
        reference_date = reference_date.astimezone(tz).date() if hasattr(reference_date, "astimezone") else reference_date

    weekday = reference_date.weekday()  # Monday=0 ... Sunday=6
    days_since_sunday = (weekday + 1) % 7
    sunday = reference_date - timedelta(days=days_since_sunday)
    saturday = sunday + timedelta(days=6)
    return sunday, saturday

def generate_report_html(tasks, sunday, saturday):
    html = f"""
    <html><head><title>Weekly Task Report: {sunday} to {saturday}</title></head><body>
    <h2>Weekly Task Report</h2>
    <p>Period: {sunday} (Sunday) to {saturday} (Saturday)</p>
    <p>Total tasks promised: {len(tasks)}</p>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Task Name</th>
            <th>Completion Percentage</th>
            <th>Feedback</th>
            <th>Date</th>
        </tr>
    """

    for task in tasks:
        task_name = task.get("task_name", "N/A")
        completion = task.get("completion_percentage", 0)
        feedback = task.get("feedback", "")
        date = task.get("date")
        date_str = date.strftime("%Y-%m-%d") if date else "N/A"

        html += f"""
        <tr>
            <td>{task_name}</td>
            <td>{completion}%</td>
            <td>{feedback}</td>
            <td>{date_str}</td>
        </tr>
        """

    html += "</table></body></html>"
    return html

async def generate_weekly_report(user_id, start_date, end_date):
    # Convert date to datetime with min and max times
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    # Query tasks within the datetime range
    tasks_cursor = db.tasks.find({
        "user_id": user_id,
        "date": {"$gte": start_datetime, "$lte": end_datetime}
    })

    tasks = await tasks_cursor.to_list(length=None)

    report_html = generate_report_html(tasks, start_date, end_date)

    # Convert start_date and end_date to datetime for MongoDB filtering and document fields
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.min.time())

    report_doc = {
        "user_id": user_id,
        "start_date": start_dt,   # store as datetime
        "end_date": end_dt,       # store as datetime
        "generated_at": datetime.utcnow(),
        "report_html": report_html,
    }

    await db.weekly_reports.update_one(
        {"user_id": user_id, "start_date": start_dt, "end_date": end_dt},
        {"$set": report_doc},
        upsert=True
    )
    return report_doc
