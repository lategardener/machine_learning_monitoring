from fastapi import Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError
from config import KEY,ALGORITHM
from auth import oauth2_scheme
from db_user.models import TokenBlacklist
from db_user.database import SessionLocal, engine
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str):
    return hash_password(plain_password) == hashed_password

def hash_password(password: str):
    return "fakehashed_" + password

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exeption = HTTPException(
        status_code = 401,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"}
    )
    try:
        is_blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
        if is_blacklisted:
            raise HTTPException(status_code=401, detail="Token revoked. Please login again.")
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exeption
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exeption
    return token_data