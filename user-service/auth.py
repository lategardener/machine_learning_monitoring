from typing import Optional
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import jwt

from config import KEY,ACCESS_TOKEN_EXPIRATION_TIME,ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def create_access_token(data: dict, expiration_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expiration_delta:
        expire = datetime.utcnow() + expiration_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRATION_TIME)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None