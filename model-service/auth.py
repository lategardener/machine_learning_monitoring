import os
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from db_models.models import TokenBlacklist
from typing import Optional
from db_models.database import SessionLocal
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = os.getenv("KEY", "totally-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

class TokenData(BaseModel):
    username: Optional[str] = None
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exeption
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exeption
    return token_data