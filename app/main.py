from fastapi import FastAPI
from auth_utils import validate_password, validate_username, get_password_hash, verify_password, create_access_token
from fastapi import Depends
from fastapi.responses import JSONResponse
from db import engine, SessionLocal, Base, User
from sqlalchemy.orm import Session
from schemas import UserRequest, Token

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
    check_user = db.query(User).filter(User.username == user.username).first()
    if check_user:
        return JSONResponse(status_code=400, content={"error": "User already exists"})
    if validate_username(user.username) != True:
        return JSONResponse(status_code=400, content={"error": validate_username(user.username)})
    if validate_password(user.password) != True:
        return JSONResponse(status_code=400, content={"error": validate_password(user.password)})
    user = User(username=user.username, password=get_password_hash(user.password))
    db.add(user)
    db.commit()
    return JSONResponse(status_code=201, content={"message": "User created successfully"})
  except Exception as e:
    print(e)
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

@app.post("/token")
async def token(user: UserRequest, db: Session = Depends(get_db)) -> Token:
  try:
    check_user = db.query(User).filter(User.username == user.username).first()
    if not check_user:
        return JSONResponse(status_code=400, content={"error": "User not found"})
    if not verify_password(user.password, check_user.password):
        return JSONResponse(status_code=400, content={"error": "Incorrect password"})
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")
  except Exception as e:
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})