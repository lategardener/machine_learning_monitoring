from sqlalchemy import Column, Integer, String, Boolean, JSON
from database import Base

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    content = Column(String, nullable=False)

