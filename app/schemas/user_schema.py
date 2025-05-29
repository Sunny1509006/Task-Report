# from pydantic import BaseModel

# class UserCreate(BaseModel):
#     username: str
#     password: str

# class UserLogin(BaseModel):
#     username: str
#     password: str

# app/schemas/user_schema.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    mobile: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

