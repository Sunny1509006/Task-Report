# app/routes/task_routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.schemas.task_schema import TaskCreate, TaskFeedback
from app.crud import task_crud
from app.services import google_calendar, report_service
from app.dependencies import get_current_user

router = APIRouter()

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
    return await report_service.generate_weekly_report(current_user["sub"])
