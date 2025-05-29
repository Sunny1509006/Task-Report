# from motor.motor_asyncio import AsyncIOMotorClient
# from app.config import settings

# client = AsyncIOMotorClient(settings.MONGODB_URL)
# db = client[settings.DATABASE_NAME]
# user_collection = db.users

# async def create_user(user_data):
#     return await user_collection.insert_one(user_data.dict())

# async def authenticate_user(username, password):
#     return await user_collection.find_one({"username": username, "password": password})



# app/crud/user_crud.py

from app.database import db
from app.models.user_model import USER_COLLECTION
from app.schemas.user_schema import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user: UserCreate):
    user_dict = user.dict()
    user_dict["password"] = pwd_context.hash(user.password)

    existing = await db[USER_COLLECTION].find_one({
        "$or": [{"username": user.username}, {"email": user.email}]
    })
    if existing:
        raise Exception("User already exists")

    await db[USER_COLLECTION].insert_one(user_dict)

async def authenticate_user(username: str, password: str):
    user = await db[USER_COLLECTION].find_one({"username": username})
    if not user or not pwd_context.verify(password, user["password"]):
        return None
    return user

