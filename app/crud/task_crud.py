from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from datetime import datetime
from bson import ObjectId

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]
task_collection = db.tasks

async def create_task(user_id, task_data):
    task = task_data.dict()
    task["user_id"] = user_id
    task["date"] = datetime.combine(task["start_time"].date(), datetime.min.time())
    # Add default feedback fields
    task["completion_percentage"] = 0.0
    task["feedback"] = ""
    result = await task_collection.insert_one(task)
    return {"inserted_id": str(result.inserted_id)}

async def get_tasks_by_user(user_id):
    return await task_collection.find({"user_id": user_id}).to_list(1000)

async def update_feedback(task_id, feedback_data):
    # Convert task_id string to ObjectId
    obj_id = ObjectId(task_id)

    # Only update these two fields (exclude task_id)
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
