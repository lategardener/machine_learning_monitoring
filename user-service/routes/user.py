from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from auth import create_access_token, oauth2_scheme, decode_access_token
from db_user.database import SessionLocal, engine
from db_user.models import User, Outbox
from authModels import TokenData, get_current_user, hash_password, verify_password, Token
from db_user.models import TokenBlacklist

router = APIRouter(prefix="/users")


User.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/createUser")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        username=user.username,
        password=hash_password(user.password),
        role="client"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    outbox_entry = Outbox(
        event_type="user.created",
        payload={
            "id": db_user.id,
            "username": db_user.username,
            "role": db_user.role
        }
    )
    db.add(outbox_entry)
    db.commit()
    return {"detail: c'est good"}
    
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = create_access_token(data={"username": form_data.username})

    outbox_entry = Outbox(
        event_type="user.login",
        payload={
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    )
    db.add(outbox_entry)
    db.commit()
    return Token(access_token=access_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    payload = decode_access_token(token)
    if payload is None or "username" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    user = db.query(User).filter(User.username == payload['username']).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    new_token = create_access_token({"username": user.username})
    return Token(access_token=new_token)

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    blacklisted_token = TokenBlacklist(token=token)
    db.add(blacklisted_token)
    db.commit()

    outbox_entry = Outbox(
        event_type="user.logout",
        payload={
            "username": current_user.username,
            "token": blacklisted_token.token
        }
    )
    db.add(outbox_entry)
    db.commit()
    return {"detail: logout reussi"}
