# from fastapi import APIRouter, HTTPException
# from app.schemas.user_schema import UserCreate, UserLogin
# from app.crud import user_crud

# router = APIRouter()

# @router.post("/register")
# async def register(user: UserCreate):
#     await user_crud.create_user(user)
#     return {"msg": "User registered successfully"}

# @router.post("/login")
# async def login(user: UserLogin):
#     result = await user_crud.authenticate_user(user.username, user.password)
#     if not result:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return {"msg": "Login successful"}


# app/routes/user_routes.py

from fastapi import APIRouter, HTTPException
from app.schemas.user_schema import UserCreate, UserLogin
from app.crud import user_crud
from app.services.auth import create_access_token

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    try:
        await user_crud.create_user(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"msg": "User registered successfully"}

@router.post("/login")
async def login(user: UserLogin):
    result = await user_crud.authenticate_user(user.username, user.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


