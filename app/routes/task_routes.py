# app/routes/task_routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.schemas.task_schema import TaskCreate, TaskFeedback
from app.crud import task_crud
from app.services import google_calendar
from app.dependencies import get_current_user
from fastapi import Query
from typing import Optional

from app.utils import reports

router = APIRouter()

from pydantic import BaseModel
from datetime import datetime

class ManualRolloverRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    timezone: str = "Asia/Dhaka"

@router.post("/tasks")
async def add_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    await google_calendar.add_event(task)
    return await task_crud.create_task(current_user["sub"], task)

@router.post("/feedback")
async def add_feedback(feedback: TaskFeedback):
    update_result = await task_crud.update_feedback(feedback.task_id, feedback)
    if update_result["matched_count"] == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return update_result

@router.get("/report", response_class=HTMLResponse)
async def get_report(current_user: dict = Depends(get_current_user)):
    return await reports.generate_weekly_report(current_user["sub"])

@router.post("/tasks/rollover")
async def rollover_tasks(current_user: dict = Depends(get_current_user)):
    await task_crud.rollover_incomplete_tasks(current_user["sub"])
    return {"detail": "Incomplete tasks rolled over to next day"}


# Get today's incomplete tasks
@router.get("/tasks/incomplete")
async def get_incomplete_tasks(timezone: Optional[str] = Query("Asia/Dhaka"), current_user: dict = Depends(get_current_user)):
    tasks = await task_crud.get_incomplete_tasks(current_user["sub"], tz_str=timezone)
    for task in tasks:
        task["_id"] = str(task["_id"])
    return tasks

# Rollover a specific task by ID
# @router.post("/tasks/rollover/{task_id}")
# async def rollover_task(task_id: str, timezone: Optional[str] = Query("Asia/Dhaka")):
#     result = await task_crud.rollover_task_by_id(task_id, tz_str=timezone)
#     if not result:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return result

@router.post("/tasks/rollover/{task_id}/manual")
async def manual_rollover(task_id: str, payload: ManualRolloverRequest, current_user: dict = Depends(get_current_user)):
    result = await task_crud.manual_rollover_task(
        task_id=task_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        tz_str=payload.timezone
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return result

@router.get("/task-list")
async def get_tasks(current_user: dict = Depends(get_current_user)):
    tasks = await task_crud.get_tasks_by_user(current_user["sub"])
    for task in tasks:
        task["_id"] = str(task["_id"])  # Convert ObjectId to string
    return tasks
