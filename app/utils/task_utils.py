import json
from db import Task
from fastapi.responses import JSONResponse
from fastapi import Request
from utils.auth_utils import validate_request
from sqlalchemy import select
from sqlalchemy.orm import Session
from schemas import TaskResponse

def validate_task(task_id: int, request: Request, db: Session):
    try:
        validation = validate_request(request, db)
        if validation.status_code != 200:
            return validation
        user_id = json.loads(validation.body)["user_id"]
        stmt = select(Task).where(Task.user_id == user_id, Task.id == task_id)
        task = db.execute(stmt).scalar_one_or_none()
        if task is None:
            return JSONResponse(status_code=404, content={"error": "Task not found"})
        task_response = TaskResponse(id=task.id, title=task.title, description=task.description, status=task.status.value)
        return JSONResponse(status_code=200, content={"task": task_response.model_dump()})
    except Exception as e:
        print("Error: ", e)
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})