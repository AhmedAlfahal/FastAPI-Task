from fastapi import FastAPI
from pydantic import BaseModel
from auth_utils import validate_password, validate_username
from fastapi import Depends
from fastapi.responses import JSONResponse
# from passlib.context import CryptContext
from db import engine, SessionLocal, Base, User
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserRequest(BaseModel):
    username: str
    password: str

@app.get("/")
def hello_world():
  """Hello World Example First FastAPI"""
  return {"Hello": "World"}

@app.post("/signup")
async def signup(user: UserRequest, db: Session = Depends(get_db)):
  try:
    check_user = db.query(User).filter(User.username == user.username).first()
    if check_user:
        return JSONResponse(status_code=400, content={"error": "User already exists"})
    if validate_username(user.username) != True:
        return JSONResponse(status_code=400, content={"error": validate_username(user.username)})
    if validate_password(user.password) != True:
        return JSONResponse(status_code=400, content={"error": validate_password(user.password)})
    user = User(username=user.username, password=user.password)
    db.add(user)
    db.commit()
    return JSONResponse(status_code=201, content={"message": "User created successfully"})
  except Exception as e:
    print(e)
    return JSONResponse(status_code=500, content={"error": str(e)})