from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import dotenv
import jwt
import os
import re
from db import engine, SessionLocal, Base, User, Task, TaskStatus
from sqlalchemy.orm import Session
from schemas import UserRequest, Token, TaskRequest
from sqlalchemy import select, insert
from fastapi.responses import JSONResponse

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def validate_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        return None

def validate_password(password: str):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*()]", password):
        return "Password must contain at least one special character"
    return True

def validate_username(username: str):
    if len(username) < 3:
        return "Username must be at least 3 characters long"
    if not re.search(r"[A-Za-z0-9]", username):
        return "Username must contain at least one letter or number"
    return True

def validate_request(request: dict, db: Session):
    authorization = request.headers.get("Authorization")
    api_key = request.headers.get("X-API-Key")
    if authorization is None or api_key is None or authorization.split(" ")[0] != "Bearer":
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    token = authorization.split(" ")[1]
    payload = validate_token(token)
    if payload is None:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    if api_key != "123456":
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    user = db.execute(select(User).where(User.username == payload["sub"])).scalar_one_or_none()
    if user is None:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return JSONResponse(status_code=200, content={"message": "Authorized", "user_id": user.id})
