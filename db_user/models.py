from sqlalchemy import Column, Integer, String, Boolean, JSON
from database import Base

class User(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)
