from sqlalchemy import Column, Integer, String, Boolean, JSON
from db_user.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)

class Outbox(Base):
    __tablename__ = "outbox"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    published = Column(Boolean, default=False)

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(String)