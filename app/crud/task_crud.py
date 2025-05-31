from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from datetime import datetime, timedelta, time
from bson import ObjectId
from app.services import google_calendar  # assuming you have this
from app.schemas.task_schema import TaskCreate
from pytz import timezone, utc


client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]
task_collection = db.tasks

tz = timezone("Asia/Dhaka")


async def create_task(user_id, task_data):
    task = task_data.dict()
    task["user_id"] = user_id

    # Localize start_time and convert to UTC
    start_time_local = task["start_time"]
    if start_time_local.tzinfo is None:
        start_time_local = tz.localize(start_time_local)
    else:
        start_time_local = start_time_local.astimezone(tz)

    task["start_time"] = start_time_local.astimezone(utc)

    # Similarly localize end_time if exists
    if "end_time" in task:
        end_time_local = task["end_time"]
        if end_time_local.tzinfo is None:
            end_time_local = tz.localize(end_time_local)
        else:
            end_time_local = end_time_local.astimezone(tz)
        task["end_time"] = end_time_local.astimezone(utc)

    # Set "date" as the start of day in local tz, converted to UTC
    local_midnight = datetime.combine(start_time_local.date(), time.min)
    local_midnight = tz.localize(local_midnight)
    task["date"] = local_midnight.astimezone(utc)

    # Add default feedback fields
    task["completion_percentage"] = 0.0
    task["feedback"] = ""

    result = await task_collection.insert_one(task)
    return {"inserted_id": str(result.inserted_id)}


async def get_tasks_by_user(user_id):
    return await task_collection.find({"user_id": user_id}).sort("_id", -1).to_list(1000)


async def update_feedback(task_id, feedback_data):
    obj_id = ObjectId(task_id)
    update_fields = {
        "completion_percentage": feedback_data.completion_percentage,
        "feedback": feedback_data.feedback
    }
    result = await task_collection.update_one(
        {"_id": obj_id},
        {"$set": update_fields}
    )
    return {
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "upserted_id": str(result.upserted_id) if result.upserted_id else None
    }


async def rollover_incomplete_tasks(user_id):
    now_local = datetime.now(tz)
    today_local = tz.localize(datetime.combine(now_local.date(), time.min))
    tomorrow_local = today_local + timedelta(days=1)

    today_utc = today_local.astimezone(utc)
    tomorrow_utc = tomorrow_local.astimezone(utc)

    # Find incomplete tasks for today in UTC
    incomplete_tasks = await task_collection.find({
        "user_id": user_id,
        "date": today_utc,
        "completion_percentage": {"$lt": 100}
    }).to_list(None)

    for task in incomplete_tasks:
        task_id = task["_id"]
        task_name = task.get("task_name")

        # New full day start and end times for tomorrow in local tz
        new_start_local = tomorrow_local
        new_end_local = tz.localize(datetime.combine(tomorrow_local.date(), time.max))

        # Convert to UTC
        new_start_utc = new_start_local.astimezone(utc)
        new_end_utc = new_end_local.astimezone(utc)

        # Update task in DB
        await task_collection.update_one(
            {"_id": task_id},
            {"$set": {
                "date": new_start_utc,
                "start_time": new_start_utc,
                "end_time": new_end_utc,
                "completion_percentage": 0.0,
                "feedback": ""
            }}
        )

        # Create full-day Google Calendar event for the task tomorrow
        full_day_task = {
            "task_name": task_name,
            "start_time": new_start_utc,
            "end_time": new_end_utc,
        }
        full_day_task_model = TaskCreate(**full_day_task)
        await google_calendar.add_event(full_day_task_model)


async def get_incomplete_tasks(user_id, tz_str="Asia/Dhaka"):
    tz = timezone(tz_str)
    now = datetime.now(tz)
    today = tz.localize(datetime.combine(now.date(), time.min))
    tomorrow = today + timedelta(days=1)

    today_utc = today.astimezone(utc)
    tomorrow_utc = tomorrow.astimezone(utc)

    return await task_collection.find({
        "user_id": user_id,
        "start_time": {"$gte": today_utc, "$lt": tomorrow_utc},
        "completion_percentage": {"$lt": 100}
    }).to_list(None)


async def manual_rollover_task(task_id: str, start_time: datetime, end_time: datetime, tz_str="Asia/Dhaka"):
    obj_id = ObjectId(task_id)
    task = await task_collection.find_one({"_id": obj_id})
    if not task:
        return None

    tz = timezone(tz_str)

    if start_time.tzinfo is None:
        localized_start = tz.localize(start_time)
    else:
        localized_start = start_time.astimezone(tz)

    if end_time.tzinfo is None:
        localized_end = tz.localize(end_time)
    else:
        localized_end = end_time.astimezone(tz)

    new_start_utc = localized_start.astimezone(utc)
    new_end_utc = localized_end.astimezone(utc)

    # date field is midnight of start_time in local tz, converted to UTC
    local_midnight = datetime.combine(localized_start.date(), time.min)
    local_midnight = tz.localize(local_midnight)
    date_utc = local_midnight.astimezone(utc)

    await task_collection.update_one(
        {"_id": obj_id},
        {"$set": {
            "start_time": new_start_utc,
            "end_time": new_end_utc,
            "date": date_utc,
            "completion_percentage": 0.0,
            "feedback": ""
        }}
    )

    from app.schemas.task_schema import TaskCreate
    from app.services import google_calendar

    updated_task = TaskCreate(
        task_name=task["task_name"],
        start_time=new_start_utc,
        end_time=new_end_utc
    )
    await google_calendar.add_event(updated_task)

    return {"detail": "Task manually rolled over", "start_time": new_start_utc.isoformat(), "end_time": new_end_utc.isoformat()}
