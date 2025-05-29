from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    task_name: str
    start_time: datetime
    end_time: datetime

class TaskFeedback(BaseModel):
    task_id: str
    completion_percentage: int
    feedback: str
