from fastapi import FastAPI, Depends, Request
from utils.auth_utils import validate_password, validate_username, get_password_hash, verify_password, create_access_token, validate_token, validate_request
from fastapi.responses import JSONResponse
from db import engine, SessionLocal, Base, User, Task, TaskStatus
from sqlalchemy.orm import Session
from schemas import UserRequest, Token, TaskRequest, TaskResponse
from sqlalchemy import select, insert
from datetime import datetime
from utils.task_utils import validate_task
import json

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def hello_world():
  """Hello World Example First FastAPI"""
  return {"Hello": "World"}

@app.post("/signup")
async def signup(user: UserRequest, db: Session = Depends(get_db)):
  try:
    stmt = select(User).where(User.username == user.username)
    check_user = db.execute(stmt).scalar_one_or_none()
    if check_user:
        return JSONResponse(status_code=400, content={"error": "User already exists"})
    if validate_username(user.username) != True:
        return JSONResponse(status_code=400, content={"error": validate_username(user.username)})
    if validate_password(user.password) != True:
        return JSONResponse(status_code=400, content={"error": validate_password(user.password)})
    user = insert(User).values(username=user.username, password=get_password_hash(user.password))
    db.execute(user)
    db.commit()
    return JSONResponse(status_code=201, content={"message": "User created successfully"})
  except Exception as e:
    print(e)
    return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/token")
async def token(user: UserRequest, db: Session = Depends(get_db)) -> Token:
  try:
    check_user = db.execute(select(User).where(User.username == user.username)).scalar_one_or_none()
    if not check_user:
        return JSONResponse(status_code=400, content={"error": "User not found"})
    if not verify_password(user.password, check_user.password):
        return JSONResponse(status_code=400, content={"error": "Incorrect password"})
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")
  except Exception as e:
    return JSONResponse(status_code=500, content={"error": str(e)})
  
@app.post("/tasks")
async def create_task(task: TaskRequest, request: Request, db: Session = Depends(get_db)) -> TaskResponse:
  try:
    validation = validate_request(request, db)
    if validation.status_code != 200:
        return validation
    user_id = json.loads(validation.body)["user_id"]
    
    stmt = insert(Task).values(
        title=task.title,
        description=task.description,
        user_id=user_id,
        status=TaskStatus.pending,
        created_at=datetime.now()
    )
    result = db.execute(stmt)
    db.commit()
    task_id = result.inserted_primary_key[0]
    return TaskResponse(id=task_id, title=task.title, description=task.description, status=TaskStatus.pending.value)
  except Exception as e:
    print(e)
    return JSONResponse(status_code=500, content={"error": str(e)})    

@app.get("/tasks")
async def get_tasks(request: Request, db: Session = Depends(get_db)) -> list[TaskResponse]:
  try:
    validation = validate_request(request, db)
    if validation.status_code != 200:
        return validation
    user_id = json.loads(validation.body)["user_id"]
    stmt = select(Task).where(Task.user_id == user_id)
    tasks = db.execute(stmt).scalars().all()
    return [TaskResponse(id=task.id, title=task.title, description=task.description, status=task.status.value) for task in tasks]
  except Exception as e:
    print(e)
    return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/tasks/{task_id}")
async def get_task(task_id: int, request: Request, db: Session = Depends(get_db)) -> TaskResponse:
  try:
    task_validation = validate_task(task_id, request, db)
    if task_validation.status_code != 200:
        return task_validation
      
    task_data = json.loads(task_validation.body)["task"]

    return TaskResponse(
        id=task_data["id"],
        title=task_data["title"],
        description=task_data["description"],
        status=task_data["status"]
    )
  except Exception as e:
    print(e)
    return JSONResponse(status_code=500, content={"error": str(e)})

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskRequest, request: Request, db: Session = Depends(get_db)) -> TaskResponse:
  try:
    task_validation = validate_task(task_id, request, db)
    if task_validation.status_code != 200:
        return task_validation
    
    stmt = select(Task).where(Task.id == task_id)
    db_task = db.execute(stmt).scalar_one_or_none()
    
    if db_task.status == TaskStatus.completed:
        return JSONResponse(status_code=400, content={"error": "Task is already completed"})
    
    db_task.title = task.title
    db_task.description = task.description
    db_task.status = TaskStatus.completed
    db.add(db_task)
    db.commit()
    
    return TaskResponse(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        status=db_task.status.value
    )
  except Exception as e:
    print(e)
    return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, request: Request, db: Session = Depends(get_db)) -> JSONResponse:
  try:
    task_validation = validate_task(task_id, request, db)
    if task_validation.status_code != 200:
        return task_validation
    
    stmt = select(Task).where(Task.id == task_id)
    db_task = db.execute(stmt).scalar_one_or_none()
    
    db.delete(db_task)
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Task deleted successfully"})
  except Exception as e:
    print(e)
    return JSONResponse(status_code=500, content={"error": str(e)})