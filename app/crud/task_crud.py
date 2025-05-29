from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from datetime import datetime

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]
task_collection = db.tasks

async def create_task(user_id, task_data):
    task = task_data.dict()
    task["user_id"] = user_id
    task["date"] = datetime.combine(task["start_time"].date(), datetime.min.time())
    result = await task_collection.insert_one(task)
    return {"inserted_id": str(result.inserted_id)}

async def get_tasks_by_user(user_id):
    return await task_collection.find({"user_id": user_id}).to_list(1000)

async def update_feedback(task_id, feedback_data):
    return await task_collection.update_one(
        {"_id": task_id},
        {"$set": feedback_data.dict()}
    )