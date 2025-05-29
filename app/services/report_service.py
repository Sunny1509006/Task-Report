from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.crud import task_crud
import datetime

templates = Jinja2Templates(directory="templates")

async def generate_weekly_report(user_id):
    tasks = await task_crud.get_tasks_by_user(user_id)
    total_tasks = len(tasks)
    completed = [t for t in tasks if t.get("completed")]
    date_labels = [str(t.get("date")) for t in tasks]
    completion_data = [t.get("completion_percentage") for t in tasks]
    return templates.TemplateResponse("report.html", {
        "request": Request,
        "total_tasks": total_tasks,
        "completed_tasks": completed,
        "all_tasks": tasks,
        "date_labels": date_labels,
        "completion_data": completion_data
    })
