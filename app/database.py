# app/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGO_URL = config("MONGO_URL", default="mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)

db = client["task_tracker"]  # your MongoDB database name
