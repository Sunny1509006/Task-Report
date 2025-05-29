from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class TaskModel(BaseModel):
    user_id: str
    task_name: str
    start_time: datetime
    end_time: datetime
    date: datetime
    feedback: Optional[str] = None
    completion_percentage: Optional[int] = 0
    completed: bool = False